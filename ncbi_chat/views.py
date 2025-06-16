from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import Agent
from django.http import JsonResponse
from .services import ollama_service
import asyncio
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json

@method_decorator(login_required, name='dispatch')
class ChatView(TemplateView):
    template_name = 'ncbi_chat/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agents'] = Agent.objects.all()
        return context

@csrf_exempt
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
        }, status=500)