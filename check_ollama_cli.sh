#!/bin/bash

echo "OLLAMA CLI CHECK"
echo "================"

echo -e "\n1. Checking if Ollama is running:"
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not running or not accessible"
    echo "   Please start it with: ollama serve"
    exit 1
fi

echo -e "\n2. Checking installed models using CLI:"
ollama list

echo -e "\n3. Checking API response:"
curl -s http://localhost:11434/api/tags | python3 -m json.tool

echo -e "\n4. Testing model generation:"
echo "Testing with a simple prompt..."
ollama run llama2 "Say hello" 2>&1 | head -n 5

echo -e "\nDone!"