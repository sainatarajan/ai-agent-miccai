#!/usr/bin/env python
"""
Diagnostic script to check Ollama setup and configuration
Run this from your project root: python diagnose_ollama.py
"""

import os
import sys
import ollama
import asyncio
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ncbi_agent.settings")
django.setup()

from ncbi_chat.config_models import SystemConfiguration
from ncbi_chat.services.ollama_service import ollama_service

async def diagnose_ollama():
    print("=" * 60)
    print("OLLAMA DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # 1. Check Ollama connection
    print("\n1. Checking Ollama connection...")
    try:
        client = ollama.AsyncClient()
        response = await client.list()
        print("✅ Successfully connected to Ollama")
        
        # List available models
        print("\n2. Available models:")
        if 'models' in response and response['models']:
            for model in response['models']:
                size_gb = model.get('size', 0) / (1024**3)
                print(f"   - {model['name']} ({size_gb:.1f} GB)")
        else:
            print("   ❌ No models found!")
            print("   Run: ollama pull llama3.2")
            
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {str(e)}")
        print("\nMake sure Ollama is running:")
        print("   - On macOS/Linux: ollama serve")
        print("   - On Windows: Start Ollama from the system tray")
        return
    
    # 2. Check Django configuration
    print("\n3. Django configuration:")
    try:
        models_config = {
            'General': SystemConfiguration.get_value(SystemConfiguration.OLLAMA_MODEL_GENERAL, 'Not set'),
            'Biomedical': SystemConfiguration.get_value(SystemConfiguration.OLLAMA_MODEL_BIOMEDICAL, 'Not set'),
            'Analysis': SystemConfiguration.get_value(SystemConfiguration.OLLAMA_MODEL_ANALYSIS, 'Not set'),
        }
        
        for name, model in models_config.items():
            print(f"   - {name} model: {model}")
            
        # Check if configured models are available
        print("\n4. Checking if configured models are available:")
        available_model_names = [m['name'] for m in response.get('models', [])]
        
        for name, model in models_config.items():
            # Normalize model name
            if model and ':' not in model:
                model = f"{model}:latest"
                
            if model in available_model_names:
                print(f"   ✅ {name} model ({model}) is available")
            else:
                print(f"   ❌ {name} model ({model}) is NOT available")
                print(f"      Suggestion: ollama pull {model.split(':')[0]}")
                
    except Exception as e:
        print(f"❌ Error checking configuration: {str(e)}")
    
    # 3. Test the service
    print("\n5. Testing ollama_service...")
    try:
        connected = await ollama_service.check_ollama_connection()
        if connected:
            print("   ✅ ollama_service connected successfully")
            
            # Try to generate a response
            print("\n6. Testing response generation...")
            response = await ollama_service.generate_response(
                prompt="Hello, this is a test",
                model_type='general'
            )
            
            if response['success']:
                print("   ✅ Successfully generated response")
                print(f"   Model used: {response['model']}")
            else:
                print(f"   ❌ Failed to generate response: {response['error']}")
        else:
            print("   ❌ ollama_service failed to connect")
            
    except Exception as e:
        print(f"   ❌ Error testing service: {str(e)}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    
    if not available_model_names:
        print("1. No models installed. Install a model first:")
        print("   ollama pull llama3.2")
        print("   ollama pull mistral")
        print("   ollama pull llama2")
    else:
        print(f"1. You have {len(available_model_names)} model(s) installed")
        print("2. Update your Django admin configuration to use one of these models")
        print("3. Or install the configured models using ollama pull")

if __name__ == "__main__":
    asyncio.run(diagnose_ollama())