#!/bin/bash

echo "OLLAMA FIX-ALL SCRIPT"
echo "===================="

# Step 1: Check if Ollama is running
echo -e "\n1. Checking Ollama status..."
if ! curl -s http://localhost:11434/ >/dev/null 2>&1; then
    echo "❌ Ollama is not running!"
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Step 2: Check available models
echo -e "\n2. Checking available models..."
MODELS=$(ollama list | tail -n +2 | awk '{print $1}')

if [ -z "$MODELS" ]; then
    echo "No models found. Installing llama2..."
    ollama pull llama2
    MODELS="llama2:latest"
else
    echo "Found models:"
    echo "$MODELS"
fi

# Get first model
FIRST_MODEL=$(echo "$MODELS" | head -n 1)
echo -e "\nUsing model: $FIRST_MODEL"

# Step 3: Update Django configuration
echo -e "\n3. Updating Django configuration..."
cat << EOF > update_config.py
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ncbi_agent.settings")
django.setup()

from ncbi_chat.config_models import SystemConfiguration

model = "${FIRST_MODEL}".split(':')[0]
print(f"Setting all models to: {model}")

configs = [
    SystemConfiguration.OLLAMA_MODEL_GENERAL,
    SystemConfiguration.OLLAMA_MODEL_BIOMEDICAL,
    SystemConfiguration.OLLAMA_MODEL_ANALYSIS,
]

for param in configs:
    SystemConfiguration.objects.update_or_create(
        parameter_name=param,
        defaults={'parameter_value': model}
    )
    print(f"  ✅ Updated {param}")

print("\nConfiguration updated!")
EOF

python update_config.py
rm update_config.py

# Step 4: Create the test_ollama management command directory if it doesn't exist
echo -e "\n4. Setting up test command..."
mkdir -p ncbi_chat/management/commands
touch ncbi_chat/management/__init__.py
touch ncbi_chat/management/commands/__init__.py

# Step 5: Final instructions
echo -e "\n===================="
echo "NEXT STEPS:"
echo "1. Replace ncbi_chat/views.py with the fixed version"
echo "2. Restart your server: ./restart_server.sh"
echo "3. The chat interface should now work!"
echo ""
echo "To test: python manage.py test_ollama"