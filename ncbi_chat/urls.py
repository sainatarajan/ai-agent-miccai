from django.urls import path
from .views import ChatView, get_ollama_models
from .agent_views import AgentListView, AgentDetailView, AgentStatusView

app_name = 'ncbi_chat'

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
    path('agents/', AgentListView.as_view(), name='agent_list'),
    path('agents/<int:pk>/', AgentDetailView.as_view(), name='agent_detail'),
    path('api/agents/status/', AgentStatusView.as_view(), name='agent_status'),
    path('api/ollama-models/', get_ollama_models, name='ollama_models'),
]
