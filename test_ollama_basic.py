#!/usr/bin/env python
"""
Basic test to check Ollama connectivity and models
"""

import subprocess
import requests
import json

print("OLLAMA BASIC TEST")
print("=" * 50)

# Test 1: Check if Ollama is running
print("\n1. Checking if Ollama service is running...")
try:
    response = requests.get('http://localhost:11434/', timeout=5)
    print(f"   ✅ Ollama is running (status: {response.status_code})")
except Exception as e:
    print(f"   ❌ Ollama is not running: {e}")
    print("\n   Please start Ollama with: ollama serve")
    exit(1)

# Test 2: Check models via CLI
print("\n2. Checking models via CLI...")
try:
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    if result.returncode == 0:
        print("   CLI output:")
        print("   " + "\n   ".join(result.stdout.strip().split('\n')))
    else:
        print(f"   ❌ CLI command failed: {result.stderr}")
except Exception as e:
    print(f"   ❌ Could not run ollama CLI: {e}")

# Test 3: Check API endpoint
print("\n3. Checking API endpoint...")
try:
    response = requests.get('http://localhost:11434/api/tags')
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API responded successfully")
        print(f"   Response keys: {list(data.keys())}")
        if 'models' in data:
            print(f"   Number of models: {len(data['models'])}")
            if data['models']:
                print("   First model structure:")
                first_model = data['models'][0]
                print(f"   Type: {type(first_model)}")
                if isinstance(first_model, dict):
                    print(f"   Keys: {list(first_model.keys())}")
                    print(f"   Name: {first_model.get('name', 'N/A')}")
    else:
        print(f"   ❌ API returned status: {response.status_code}")
except Exception as e:
    print(f"   ❌ API request failed: {e}")

# Test 4: Simple generation test
print("\n4. Testing simple generation...")
model_to_test = None

# Get first available model
try:
    response = requests.get('http://localhost:11434/api/tags')
    if response.status_code == 200:
        data = response.json()
        if 'models' in data and data['models']:
            model_to_test = data['models'][0].get('name', data['models'][0])
except:
    pass

if model_to_test:
    print(f"   Testing with model: {model_to_test}")
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model_to_test,
                'prompt': 'Say hello',
                'stream': False
            },
            timeout=30
        )
        if response.status_code == 200:
            print("   ✅ Generation successful!")
        else:
            print(f"   ❌ Generation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
else:
    print("   ❌ No model available to test")

print("\n" + "=" * 50)
print("SUMMARY:")
print("If all tests pass, Ollama is working correctly.")
print("If not, please address the issues shown above.")