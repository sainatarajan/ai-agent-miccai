#!/usr/bin/env python
"""
Complete fix for Ollama integration issues
Run this to fix all Ollama-related problems
"""

import os
import sys
import subprocess
import time
import shutil

print("COMPLETE OLLAMA FIX")
print("=" * 60)

# Step 1: Check if Ollama is installed
print("\n1. Checking Ollama installation...")
try:
    result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Ollama is installed")
    else:
        print("   ❌ Ollama not found. Please install from https://ollama.ai")
        exit(1)
except:
    print("   ❌ Ollama not found. Please install from https://ollama.ai")
    exit(1)

# Step 2: Check if Ollama is running
print("\n2. Checking if Ollama service is running...")
import requests
try:
    response = requests.get('http://localhost:11434/', timeout=5)
    print("   ✅ Ollama service is running")
except:
    print("   ⚠️  Ollama service not running. Starting it...")
    # Start Ollama in background
    subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    # Check again
    try:
        response = requests.get('http://localhost:11434/', timeout=5)
        print("   ✅ Ollama service started successfully")
    except:
        print("   ❌ Failed to start Ollama service")
        print("   Please run 'ollama serve' manually in another terminal")
        exit(1)

# Step 3: Check available models
print("\n3. Checking available models...")
result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
if result.returncode == 0:
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        models = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if parts:
                models.append(parts[0])
        
        if models:
            print(f"   ✅ Found {len(models)} model(s):")
            for model in models:
                print(f"      - {model}")
            first_model = models[0].split(':')[0]  # Get base name without tag
        else:
            print("   ❌ No models found")
            print("   Installing llama2...")
            subprocess.run(['ollama', 'pull', 'llama2'])
            first_model = 'llama2'
    else:
        print("   ❌ No models found")
        print("   Installing llama2...")
        subprocess.run(['ollama', 'pull', 'llama2'])
        first_model = 'llama2'
else:
    print("   ❌ Could not list models")
    first_model = 'llama2'

# Step 4: Fix views.py
print("\n4. Fixing views.py...")
views_path = 'ncbi_chat/views.py'

if os.path.exists(views_path):
    # Backup
    shutil.copy(views_path, views_path + '.backup')
    print(f"   ✅ Created backup: {views_path}.backup")
    
    # Read current content
    with open(views_path, 'r') as f:
        content = f.read()
    
    # Add async_to_sync import if missing
    if 'from asgiref.sync import async_to_sync' not in content:
        # Find the last import line
        lines = content.split('\n')
        last_import = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import = i
        
        lines.insert(last_import + 1, 'from asgiref.sync import async_to_sync')
        content = '\n'.join(lines)
    
    # Replace the async function
    import re
    
    # Find and replace the async get_ollama_models function
    pattern = r'(@csrf_exempt\s*\n@require_http_methods\(\["GET"\]\)\s*\n)async def get_ollama_models'
    replacement = r'\1def get_ollama_models'
    content = re.sub(pattern, replacement, content)
    
    # Find the function body and fix it
    pattern = r'(def get_ollama_models\(request\):.*?)(models = await ollama_service\.get_available_models\(\))'
    replacement = r'\1models = async_to_sync(ollama_service.get_available_models)()'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Add serialization logic if not present
    if 'serializable_models = []' not in content:
        # Find the JsonResponse in get_ollama_models and update it
        pattern = r'(def get_ollama_models.*?)(return JsonResponse\({\'models\': models}\))'
        replacement = r'''\1# Ensure models are JSON serializable
        serializable_models = []
        for model in models:
            if isinstance(model, dict):
                serializable_models.append({
                    'name': model.get('name', 'unknown'),
                    'size': model.get('size', 0),
                    'modified': str(model.get('modified', ''))
                })
            else:
                serializable_models.append({
                    'name': str(model),
                    'size': 0,
                    'modified': ''
                })
        
        return JsonResponse({
            'models': serializable_models,
            'success': True
        })'''
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write updated content
    with open(views_path, 'w') as f:
        f.write(content)
    
    print("   ✅ Fixed views.py")
else:
    print(f"   ❌ Could not find {views_path}")

# Step 5: Update Django configuration
print(f"\n5. Updating Django configuration to use {first_model}...")

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ncbi_agent.settings")

try:
    import django
    django.setup()
    
    from ncbi_chat.config_models import SystemConfiguration
    
    configs = [
        (SystemConfiguration.OLLAMA_MODEL_GENERAL, 'General Purpose Model'),
        (SystemConfiguration.OLLAMA_MODEL_BIOMEDICAL, 'Biomedical Model'),
        (SystemConfiguration.OLLAMA_MODEL_ANALYSIS, 'Analysis Model'),
    ]
    
    for param_name, description in configs:
        obj, created = SystemConfiguration.objects.update_or_create(
            parameter_name=param_name,
            defaults={
                'parameter_value': first_model,
                'description': f'{description} (auto-configured)'
            }
        )
        print(f"   ✅ Updated {param_name} to {first_model}")
    
except Exception as e:
    print(f"   ❌ Could not update configuration: {e}")
    print("   You may need to update it manually in Django admin")

# Step 6: Test generation
print(f"\n6. Testing model {first_model}...")
try:
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': first_model,
            'prompt': 'Say "Hello from Ollama!"',
            'stream': False
        },
        timeout=30
    )
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Model test successful!")
        print(f"   Response: {result.get('response', '')[:100]}...")
    else:
        print(f"   ❌ Model test failed with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Model test error: {e}")

print("\n" + "=" * 60)
print("COMPLETE! Next steps:")
print("1. Restart your Django server: ./restart_server.sh")
print("2. Open http://localhost:8000 in your browser")
print("3. Login and try the chat interface")
print("\nIf you still have issues, run: python manage.py test_ollama")