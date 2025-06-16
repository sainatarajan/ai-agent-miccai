#!/usr/bin/env python
"""
Quick fix script to automatically configure Django to use available Ollama models
Run this from your project root: python quick_fix_ollama.py
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

async def quick_fix():
    print("OLLAMA Quick Fix Tool")
    print("=" * 40)
    
    try:
        # Check available models
        client = ollama.AsyncClient()
        response = await client.list()
        
        if not response or 'models' not in response or not response['models']:
            print("❌ No Ollama models found!")
            print("\nPlease install at least one model:")
            print("  ollama pull llama3.2")
            print("  ollama pull llama2")
            print("  ollama pull mistral")
            return
        
        available_models = response['models']
        print(f"Found {len(available_models)} available model(s):")
        for i, model in enumerate(available_models):
            print(f"  {i+1}. {model['name']}")
        
        # Use the first available model as default
        default_model = available_models[0]['name']
        
        print(f"\n✅ Setting all models to use: {default_model}")
        
        # Update configuration
        configs_to_update = [
            (SystemConfiguration.OLLAMA_MODEL_GENERAL, 'General Purpose Model'),
            (SystemConfiguration.OLLAMA_MODEL_BIOMEDICAL, 'Biomedical Model'),
            (SystemConfiguration.OLLAMA_MODEL_ANALYSIS, 'Analysis Model'),
        ]
        
        for param_name, description in configs_to_update:
            obj, created = SystemConfiguration.objects.update_or_create(
                parameter_name=param_name,
                defaults={
                    'parameter_value': default_model.replace(':latest', ''),  # Remove :latest suffix
                    'description': f'{description} (auto-configured)'
                }
            )
            print(f"  ✅ Updated {param_name}")
        
        print("\n✅ Configuration updated successfully!")
        print(f"All models now set to use: {default_model}")
        print("\nYou can now restart your Django server and try chatting again.")
        
        # Optional: Install recommended models
        print("\n" + "=" * 40)
        print("RECOMMENDATIONS:")
        print("For better performance, consider installing these models:")
        print("  ollama pull llama3.2       # Fast, good general purpose")
        print("  ollama pull mistral        # Good for analysis")
        print("  ollama pull llama2         # Reliable alternative")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nMake sure Ollama is running:")
        print("  - On macOS/Linux: ollama serve")
        print("  - On Windows: Start Ollama from the system tray")

if __name__ == "__main__":
    asyncio.run(quick_fix())