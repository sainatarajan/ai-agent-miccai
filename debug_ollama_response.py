#!/usr/bin/env python
"""
Debug script to see the exact Ollama API response structure
"""

import ollama
import asyncio
import json

async def debug_ollama():
    print("OLLAMA DEBUG TOOL")
    print("=" * 60)
    
    try:
        # Create client
        client = ollama.AsyncClient()
        print("1. Testing connection to Ollama...")
        
        # Get raw response
        response = await client.list()
        
        print("\n2. Raw response from Ollama:")
        print(json.dumps(response, indent=2))
        
        print("\n3. Response type:", type(response))
        
        if isinstance(response, dict):
            print("\n4. Response keys:", list(response.keys()))
            
            # Check different possible structures
            if 'models' in response:
                print("\n5. Models field type:", type(response['models']))
                if response['models']:
                    print("\n6. First model structure:")
                    first_model = response['models'][0]
                    print("   Type:", type(first_model))
                    if isinstance(first_model, dict):
                        print("   Keys:", list(first_model.keys()))
                        print("   Full content:", json.dumps(first_model, indent=2))
        
        # Try alternative: direct list() call
        print("\n7. Trying alternative list approach...")
        try:
            # Some versions might return a generator or list directly
            models = await client.list()
            if hasattr(models, '__iter__') and not isinstance(models, (dict, str)):
                print("   Response is iterable, converting to list...")
                models_list = list(models)
                print(f"   Found {len(models_list)} models")
                if models_list:
                    print("   First item:", models_list[0])
        except Exception as e:
            print(f"   Alternative approach failed: {e}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ollama())