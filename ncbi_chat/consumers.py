import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Query, Agent
from .services import ollama_service

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
            
        self.user = self.scope["user"]
        self.room_group_name = f"chat_{self.user.id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            query_text = data.get('message')
            model = data.get('model', 'llama3.2:latest')  # Default to latest model
            
            if not query_text:
                return
                
            # Create query in database
            query = await self.create_query(query_text)
            
            # Send acknowledgment
            await self.send(text_data=json.dumps({
                'type': 'query_received',
                'query_id': query.id,
                'message': query_text
            }))
            
            # Generate response with conversation history
            response = await ollama_service.generate_response(
                prompt=query_text,
                model_type=model,
                system_prompt="You are a helpful biomedical research assistant. Maintain context from the conversation history when answering.",
                user_id=str(self.user.id)  # Pass user ID for context
            )
            
            # Send response
            await self.send(text_data=json.dumps({
                'type': 'processing_update',
                'message': response['response'] if response['success'] else response['error'],
                'model_used': model,
                'success': response['success']
            }))
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def query_update(self, event):
        # Send update to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def create_query(self, query_text):
        return Query.objects.create(
            user=self.user,
            query_text=query_text,
            query_type='natural_language',
            status='processing'
        )
    
    @database_sync_to_async
    def update_query(self, query_id, search_strategy):
        query = Query.objects.get(id=query_id)
        query.status = 'ready'
        query.save()
        return query
