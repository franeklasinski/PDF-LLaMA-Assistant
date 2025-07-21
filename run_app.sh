#!/bin/bash

echo "PDF LLaMA Assistant - Uruchamianie aplikacji..."

# Sprawdza czy Ollama jest zainstalowana
if ! command -v ollama &> /dev/null; then
    echo "Ollama nie jest zainstalowana. Instaluję przez Homebrew..."
    brew install ollama
fi

# sprawdza czy Ollama jest uruchomiona
echo "Uruchamiam Ollama (jeśli nie jest już uruchomiona)..."
if ! pgrep -x "ollama" > /dev/null; then
    brew services start ollama
fi
sleep 3

# Sprawdza czy model llama3.2 jest pobrany
if ! ollama list | grep -q llama3.2; then
    echo "Pobieram model llama3.2 (może potrwać kilka minut)..."
    ollama pull llama3.2
fi

# Uruchamia aplikację Streamlit
echo "Uruchamiam aplikację webową..."
echo "Aplikacja będzie dostępna pod adresem: http://localhost:8501"
echo "Aby zatrzymać aplikację, naciśnij Ctrl+C"

/usr/bin/python3 -m streamlit run pdf_llama_app.py --server.headless true