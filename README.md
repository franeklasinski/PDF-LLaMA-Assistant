# PDF LLaMA Assistant

Inteligentny asystent do analizy dokumentów PDF z wykorzystaniem modelu LLaMA.

## Funkcje

- **Odczytywanie PDF-ów** - Automatyczna ekstrakcja tekstu z dokumentów PDF
- **Pytania i odpowiedzi** - Zadawaj pytania o zawartość dokumentu
- **Wyciąganie konkretnych informacji**:
  - Daty
  - Liczby
  - Nazwy firm
  - Adresy email
  - Numery telefonu
- **Interfejs webowy** - Łatwy w użyciu interfejs Streamlit
- **Export danych** - Pobierz wyniki jako CSV

## Wymagania

- Python 3.8+
- Ollama (dla lokalnego LLaMA)
- Biblioteki Python (requirements.txt)

## Instalacja i uruchomienie

### Opcja 1: Automatyczne uruchomienie
```bash
./run_app.sh
```

### Opcja 2: Manualne uruchomienie

1. **Zainstaluj Ollama:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

2. **Pobierz model LLaMA:**
```bash
ollama pull llama2
```

3. **Uruchom serwis Ollama:**
```bash
ollama serve
```

4. **Uruchom aplikację:**
```bash
streamlit run untitled:Untitled-1
```

## Jak używać

1. **Załaduj model** - Wybierz "local" dla Ollama lub "huggingface" dla online
2. **Upload PDF** - Przeciągnij i upuść plik PDF
3. **Zadawaj pytania** - Wpisz pytanie o dokument i otrzymaj odpowiedź
4. **Wyciągaj informacje** - Wybierz typ informacji do automatycznego wyciągnięcia

## Wygląd intefejsu

<img width="1470" height="956" alt="Zrzut ekranu 2025-07-21 o 13 45 10" src="https://github.com/user-attachments/assets/6e5e6ed2-333c-491e-9641-92c4786773e2" />

## Przykłady użycia

### Pytania do dokumentu:
- "O czym jest ten dokument?"
- "Jakie są główne punkty tego raportu?"
- "Kto jest autorem tego dokumentu?"
- "Jakie są kluczowe daty w tym dokumencie?"

### Automatyczne wyciąganie:
- **Daty**: Znajduje wszystkie daty w różnych formatach
- **Liczby**: Wyciąga liczby, kwoty, procenty
- **Firmy**: Identyfikuje nazwy firm i organizacji
- **Kontakt**: E-maile i numery telefonu

## Rozwiązywanie problemów

**Problem**: "Nie można połączyć się z Ollama"
**Rozwiązanie**: Upewnij się, że Ollama jest uruchomiona (`ollama serve`)

**Problem**: "Model nie został załadowany"
**Rozwiązanie**: Sprawdź czy model llama2 jest pobrany (`ollama list`)

**Problem**: "Błąd przy odczytywaniu PDF"
**Rozwiązanie**: Sprawdź czy PDF nie jest zaszyfrowany lub uszkodzony

## Autor
Franciszek Łasiński 

--------
