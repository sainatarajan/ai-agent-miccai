#!/usr/bin/env python
"""
Simple fix script that handles different Ollama response formats
"""

import os
import sys
import subprocess
import json
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ncbi_agent.settings")
django.setup()

from ncbi_chat.config_models import SystemConfiguration

def get_models_via_cli():
    """Get models using ollama CLI as fallback"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header
                models = []
                for line in lines[1:]:
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        models.append(model_name)
                return models
    except Exception as e:
        print(f"CLI approach failed: {e}")
    return []

def get_models_via_api():
    """Get models using API"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            data = response.json()
            if 'models' in data:
                return [m.get('name', m) if isinstance(m, dict) else str(m) for m in data['models']]
    except Exception as e:
        print(f"API approach failed: {e}")
    return []

def main():
    print("OLLAMA Simple Fix Tool")
    print("=" * 40)
    
    # Try multiple approaches to get models
    models = []
    
    # First try API
    print("\n1. Trying API approach...")
    models = get_models_via_api()
    
    # If that fails, try CLI
    if not models:
        print("\n2. API failed, trying CLI approach...")
        models = get_models_via_cli()
    
    if not models:
        print("\n❌ Could not find any Ollama models!")
        print("\nPlease ensure:")
        print("1. Ollama is running (ollama serve)")
        print("2. You have at least one model installed")
        print("\nInstall a model with:")
        print("  ollama pull llama2")
        print("  ollama pull mistral")
        print("  ollama pull llama3.2")
        return
    
    print(f"\n✅ Found {len(models)} model(s):")
    for i, model in enumerate(models):
        print(f"  {i+1}. {model}")
    
    # Use the first available model
    default_model = models[0]
    # Remove version tags for configuration
    model_base = default_model.split(':')[0]
    
    print(f"\n3. Setting all models to use: {model_base}")
    
    # Update configuration
    configs = [
        (SystemConfiguration.OLLAMA_MODEL_GENERAL, 'General Purpose Model'),
        (SystemConfiguration.OLLAMA_MODEL_BIOMEDICAL, 'Biomedical Model'),
        (SystemConfiguration.OLLAMA_MODEL_ANALYSIS, 'Analysis Model'),
    ]
    
    for param_name, description in configs:
        try:
            obj, created = SystemConfiguration.objects.update_or_create(
                parameter_name=param_name,
                defaults={
                    'parameter_value': model_base,
                    'description': f'{description} (auto-configured)'
                }
            )
            print(f"  ✅ Updated {param_name}")
        except Exception as e:
            print(f"  ❌ Failed to update {param_name}: {e}")
    
    print("\n✅ Configuration complete!")
    print(f"All models set to: {model_base}")
    
    # Test model
    print(f"\n4. Testing model {default_model}...")
    try:
        result = subprocess.run(
            ['ollama', 'run', default_model, 'Say "Hello, I am working!"'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Model test successful!")
        else:
            print("❌ Model test failed")
    except subprocess.TimeoutExpired:
        print("⚠️  Model test timed out (this might be normal for first run)")
    except Exception as e:
        print(f"❌ Model test error: {e}")
    
    print("\n" + "=" * 40)
    print("NEXT STEPS:")
    print("1. Replace ncbi_chat/services/ollama_service.py with the fixed version")
    print("2. Replace ncbi_chat/templates/ncbi_chat/chat.html with the updated version")
    print("3. Restart your Django server: ./restart_server.sh")
    print("4. Try chatting again!")

if __name__ == "__main__":
    main()