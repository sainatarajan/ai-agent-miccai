from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from .models import Agent, MCPTool

class AgentListView(LoginRequiredMixin, ListView):
    model = Agent
    template_name = 'ncbi_chat/agent_list.html'
    context_object_name = 'agents'

class AgentDetailView(LoginRequiredMixin, DetailView):
    model = Agent
    template_name = 'ncbi_chat/agent_detail.html'
    context_object_name = 'agent'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tools'] = MCPTool.objects.filter(agent=self.object)
        return context

class AgentStatusView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        agents = Agent.objects.all()
        data = []
        
        for agent in agents:
            agent_data = {
                'id': agent.id,
                'name': agent.name,
                'type': agent.agent_type,
                'status': agent.status,
                'last_heartbeat': agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
                'active_tools': [
                    {
                        'name': tool.name,
                        'status': tool.status
                    }
                    for tool in agent.get_active_tools()
                ]
            }
            data.append(agent_data)
        
        return JsonResponse({'agents': data})
