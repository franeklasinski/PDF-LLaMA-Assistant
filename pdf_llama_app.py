import streamlit as st
import PyPDF2
import pdfplumber
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import io
import requests
import json
from typing import List, Dict, Any
import re
import pandas as pd

class PDFLlamaAssistant:
    def __init__(self):
        self.pdf_text = ""
        self.pdf_name = ""
        self.model = None
        self.tokenizer = None
        self.qa_pipeline = None
        self.use_ollama = False 
        
    def load_model(self, model_choice: str = "local"):
        """Ładowanie modelu LLaMA"""
        try:
            if model_choice == "local":
                # Próba użycia lokalnego modelu przez Ollama
                self.use_ollama = True
                st.info("Używam lokalnego modelu Ollama (llama3.2)")
            else:
                # Użycie modelu przez Hugging Face
                st.info("Ładuję model z Hugging Face...")
                self.qa_pipeline = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    tokenizer="microsoft/DialoGPT-medium",
                    device=0 if torch.cuda.is_available() else -1
                )
                self.use_ollama = False
                
        except Exception as e:
            st.error(f"Błąd przy ładowaniu modelu: {e}")
            return False
        return True
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Ekstrakcja tekstu z pliku PDF"""
        text = ""
        try:
            # Użycie pdfplumber (lepsze dla tabel i formatowania)
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
            # Jeśli pdfplumber nie zadziałał, daje PyPDF2
            if not text.strip():
                pdf_file.seek(0)  # Reset pozycji pliku
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                    
        except Exception as e:
            st.error(f"Błąd przy odczytywaniu PDF: {e}")
            return ""
            
        return text.strip()
    
    def query_ollama(self, prompt: str) -> str:
        """Zapytanie do lokalnego modelu Ollama"""
        try:
            url = "http://localhost:11434/api/generate"
            data = {
                "model": "llama3.2", 
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "Brak odpowiedzi")
            else:
                return f"Błąd API: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Nie można połączyć się z Ollama. Upewnij się, że Ollama jest uruchomiona."
        except Exception as e:
            return f"Błąd: {e}"
    
    def answer_question(self, question: str, context: str) -> str:
        """Odpowiadanie na pytanie na podstawie kontekstu PDF"""
        if self.use_ollama:
            prompt = f"""
            Na podstawie następującego tekstu odpowiedz na pytanie użytkownika.
            
            TEKST:
            {context[:3000]}  # Ograniczenie długości kontekstu
            
            PYTANIE: {question}
            
            ODPOWIEDŹ:
            """
            return self.query_ollama(prompt)
        else:
            # Fallback do prostszego modelu
            prompt = f"Kontekst: {context[:1000]}\nPytanie: {question}\nOdpowiedź:"
            if self.qa_pipeline:
                result = self.qa_pipeline(prompt, max_length=200, num_return_sequences=1)
                return result[0]["generated_text"].split("Odpowiedź:")[-1].strip()
            else:
                return "Model nie został załadowany poprawnie."
    
    def extract_specific_info(self, info_type: str) -> List[str]:
        """Wyciągnięcie konkretnych informacji z tekstu"""
        results = []
        text = self.pdf_text.lower()
        
        if info_type == "daty":
            # Wzorce dla dat
            date_patterns = [
                r'\d{1,2}[./\-]\d{1,2}[./\-]\d{4}',  # 12/01/2023
                r'\d{4}[./\-]\d{1,2}[./\-]\d{1,2}',  # 2023-01-12
                r'\d{1,2}\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+\d{4}'
            ]
            for pattern in date_patterns:
                matches = re.findall(pattern, self.pdf_text, re.IGNORECASE)
                results.extend(matches)
                
        elif info_type == "liczby":
            # Wzorce dla liczb
            number_patterns = [
                r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b',  # Liczby z przecinkami
                r'\b\d+\.\d+\b',  # Liczby dziesiętne
                r'\b\d+\b'  # Liczby całkowite
            ]
            for pattern in number_patterns:
                matches = re.findall(pattern, self.pdf_text)
                results.extend(matches)
                
        elif info_type == "nazwy_firm":
            # Proste wzorce dla nazw firm
            company_patterns = [
                r'\b[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]*\s+(?:Sp\.|Ltd\.|Inc\.|LLC|S\.A\.|Sp\. z o\.o\.)',
                r'\b[A-Z][a-z]*\s+[A-Z][a-z]*\s+(?:Company|Corporation|Corp\.)'
            ]
            for pattern in company_patterns:
                matches = re.findall(pattern, self.pdf_text)
                results.extend(matches)
                
        elif info_type == "adresy_email":
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            results = re.findall(email_pattern, self.pdf_text)
            
        elif info_type == "numery_telefonu":
            phone_patterns = [
                r'\+\d{1,3}\s*\d{3}\s*\d{3}\s*\d{3}',  # +48 123 456 789
                r'\d{3}[-.\s]?\d{3}[-.\s]?\d{3}',  # 123-456-789
                r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'  # (123) 456-7890
            ]
            for pattern in phone_patterns:
                matches = re.findall(pattern, self.pdf_text)
                results.extend(matches)
        
        return list(set(results))

def main():
    st.set_page_config(
        page_title="PDF LLaMA Assistant", 
        page_icon="",
        layout="wide"
    )
    
    st.title("PDF LLaMA Assistant")
    st.markdown("**Inteligentny asystent do analizy dokumentów PDF z wykorzystaniem LLaMA**")
    
    # Inicjalizacja asystenta
    if 'assistant' not in st.session_state:
        st.session_state.assistant = PDFLlamaAssistant()
    
    assistant = st.session_state.assistant
    
    # Sidebar z opcjami
    st.sidebar.header("Konfiguracja")
    
    # Wybór modelu
    model_choice = st.sidebar.selectbox(
        "Wybierz model:",
        ["local", "huggingface"],
        help="local = Ollama (szybszy), huggingface = online (wolniejszy)"
    )
    
    if st.sidebar.button("Załaduj model"):
        with st.spinner("Ładowanie modelu..."):
            if assistant.load_model(model_choice):
                st.success("Model załadowany pomyślnie!")
            else:
                st.error("Nie udało się załadować modelu")
    
    # Upload pliku PDF
    st.header("Upload pliku PDF")
    uploaded_file = st.file_uploader(
        "Wybierz plik PDF", 
        type="pdf",
        help="Przeciągnij i upuść plik PDF lub kliknij, aby wybrać"
    )
    
    if uploaded_file is not None:
        assistant.pdf_name = uploaded_file.name
        
        with st.spinner("Przetwarzanie PDF..."):
            assistant.pdf_text = assistant.extract_text_from_pdf(uploaded_file)
            
        if assistant.pdf_text:
            st.success(f" PDF '{uploaded_file.name}' został przetworzony pomyślnie!")
            
            # Podgląd tekstu
            with st.expander("Podgląd tekstu z PDF"):
                st.text_area(
                    "Wyciągnięty tekst:", 
                    assistant.pdf_text[:1000] + "..." if len(assistant.pdf_text) > 1000 else assistant.pdf_text,
                    height=200,
                    disabled=True
                )
            
            # Główne funkcje
            col1, col2 = st.columns(2)
            
            with col1:
                st.header(" Zadaj pytanie")
                question = st.text_area(
                    "Twoje pytanie o dokument:",
                    placeholder="np. Jaka jest główna tematyka tego dokumentu?"
                )
                
                if st.button("Znajdź odpowiedź") and question:
                    with st.spinner("Szukam odpowiedzi..."):
                        answer = assistant.answer_question(question, assistant.pdf_text)
                        st.markdown("**Odpowiedź:**")
                        st.write(answer)
            
            with col2:
                st.header("Wyciągnij konkretne informacje")
                info_type = st.selectbox(
                    "Wybierz typ informacji:",
                    ["daty", "liczby", "nazwy_firm", "adresy_email", "numery_telefonu"]
                )
                
                if st.button("Wyciągnij informacje"):
                    with st.spinner("Przetwarzanie..."):
                        results = assistant.extract_specific_info(info_type)
                        
                        if results:
                            st.markdown(f"**Znalezione {info_type}:**")
                            df = pd.DataFrame(results, columns=[info_type.replace('_', ' ').title()])
                            st.dataframe(df, use_container_width=True)
                            
                            # Opcja pobrania wyników
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Pobierz jako CSV",
                                data=csv,
                                file_name=f"{info_type}_{assistant.pdf_name}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning(f"Nie znaleziono żadnych {info_type} w dokumencie.")
        else:
            st.error("Nie udało się wyciągnąć tekstu z PDF. Sprawdź czy plik nie jest zaszyfrowany.")
    
    # Instrukcje w sidebar
    st.sidebar.markdown("---")
    st.sidebar.header(" Instrukcje")
    st.sidebar.markdown("""
    **Krok 1:** Załaduj model (Ollama lub HuggingFace)
    
    **Krok 2:** Upload plik PDF
    
    **Krok 3:** Zadawaj pytania lub wybieraj konkretne informacje
    
    **Dla Ollama:**
    ```bash
    # Zainstaluj Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Pobierz model
    ollama pull llama3.2
    
    # Uruchom serwis
    ollama serve
    ```
    """)

if __name__ == "__main__":
    main()
