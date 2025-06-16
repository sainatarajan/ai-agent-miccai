# Save this as: ncbi_chat/management/commands/test_ollama.py

from django.core.management.base import BaseCommand
from ncbi_chat.services import ollama_service
from ncbi_chat.config_models import SystemConfiguration
import asyncio

class Command(BaseCommand):
    help = 'Test Ollama connectivity and configuration'

    def handle(self, *args, **kwargs):
        self.stdout.write("Testing Ollama Integration...")
        self.stdout.write("=" * 50)
        
        # Run async tests
        asyncio.run(self.run_tests())
    
    async def run_tests(self):
        # Test 1: Check connection
        self.stdout.write("\n1. Testing Ollama connection...")
        connected = await ollama_service.check_ollama_connection()
        if connected:
            self.stdout.write(self.style.SUCCESS("   ✅ Connected to Ollama"))
        else:
            self.stdout.write(self.style.ERROR("   ❌ Failed to connect to Ollama"))
            return
        
        # Test 2: Get available models
        self.stdout.write("\n2. Getting available models...")
        models = await ollama_service.get_available_models()
        if models:
            self.stdout.write(self.style.SUCCESS(f"   ✅ Found {len(models)} model(s):"))
            for model in models:
                name = model.get('name', model) if isinstance(model, dict) else str(model)
                self.stdout.write(f"      - {name}")
        else:
            self.stdout.write(self.style.ERROR("   ❌ No models found"))
            self.stdout.write("\n   Install a model with:")
            self.stdout.write("     ollama pull llama2")
            self.stdout.write("     ollama pull llama3.2")
            self.stdout.write("     ollama pull mistral")
            return
        
        # Test 3: Check configuration
        self.stdout.write("\n3. Checking Django configuration...")
        general_model = SystemConfiguration.get_value(
            SystemConfiguration.OLLAMA_MODEL_GENERAL, 
            'Not configured'
        )
        self.stdout.write(f"   General model: {general_model}")
        
        # Test 4: Try to generate a response
        self.stdout.write("\n4. Testing response generation...")
        try:
            response = await ollama_service.generate_response(
                prompt="Say 'Hello, Django!'",
                model_type='general'
            )
            
            if response['success']:
                self.stdout.write(self.style.SUCCESS("   ✅ Generation successful!"))
                self.stdout.write(f"   Model used: {response['model']}")
                self.stdout.write(f"   Response: {response['response'][:100]}...")
            else:
                self.stdout.write(self.style.ERROR(f"   ❌ Generation failed: {response['error']}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error: {str(e)}"))