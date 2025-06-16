#!/usr/bin/env python
"""
Patch views.py to fix the async issue
"""

import os
import shutil

# The fixed content for the get_ollama_models function
FIXED_FUNCTION = '''@csrf_exempt
@require_http_methods(["GET"])
def get_ollama_models(request):
    """Get available Ollama models - synchronous version"""
    try:
        # Convert async function to sync
        models = async_to_sync(ollama_service.get_available_models)()
        
        # Ensure models are JSON serializable
        serializable_models = []
        for model in models:
            if isinstance(model, dict):
                # Extract only the fields we need
                serializable_models.append({
                    'name': model.get('name', 'unknown'),
                    'size': model.get('size', 0),
                    'modified': str(model.get('modified', ''))
                })
            else:
                # If it's just a string, wrap it
                serializable_models.append({
                    'name': str(model),
                    'size': 0,
                    'modified': ''
                })
        
        return JsonResponse({
            'models': serializable_models,
            'success': True
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'models': [],
            'success': False
        }, status=500)'''

# Read the current views.py
views_path = 'ncbi_chat/views.py'

if not os.path.exists(views_path):
    print(f"❌ Could not find {views_path}")
    exit(1)

# Backup the original
shutil.copy(views_path, views_path + '.backup')
print(f"✅ Created backup: {views_path}.backup")

# Read the file
with open(views_path, 'r') as f:
    content = f.read()

# Check if we need to add the import
if 'from asgiref.sync import async_to_sync' not in content:
    # Add the import after the other imports
    import_line = 'from asgiref.sync import async_to_sync\n'
    
    # Find where to insert (after the last import)
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i
    
    lines.insert(last_import_idx + 1, import_line)
    content = '\n'.join(lines)
    print("✅ Added missing import: async_to_sync")

# Find the async get_ollama_models function
import re

# Pattern to find the function
pattern = r'@csrf_exempt\s*\n@require_http_methods\(\["GET"\]\)\s*\nasync def get_ollama_models\(request\):.*?(?=\n(?:def|class|\Z))'

# Replace the function
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, FIXED_FUNCTION, content, flags=re.DOTALL)
    print("✅ Replaced get_ollama_models function")
else:
    print("❌ Could not find the async get_ollama_models function")
    print("   You may need to manually update the function")

# Write the updated content
with open(views_path, 'w') as f:
    f.write(content)

print(f"\n✅ Updated {views_path}")
print("\nNow restart your server with: ./restart_server.sh")