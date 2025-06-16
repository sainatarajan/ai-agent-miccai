from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .config_models import SystemConfiguration

class Agent(models.Model):
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('busy', 'Busy'),
        ('error', 'Error'),
        ('offline', 'Offline'),
    ]
    
    name = models.CharField(max_length=100)
    agent_type = models.CharField(max_length=50)  # 'utility' or 'domain'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    last_heartbeat = models.DateTimeField(auto_now=True)
    capabilities = models.JSONField(default=dict)
    performance_metrics = models.JSONField(default=dict)

    def get_active_tools(self):
        return MCPTool.objects.filter(agent=self, status='active')

    def __str__(self):
        return f"{self.name} ({self.agent_type}) - {self.status}"

class Query(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField()
    query_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    assigned_agents = models.ManyToManyField(Agent)
    execution_time = models.FloatField(null=True)
    result_count = models.IntegerField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    def __str__(self):
        return f"Query {self.id} by {self.user.username} - {self.status}"

class QueryResult(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    source_database = models.CharField(max_length=50)
    result_data = models.JSONField()
    relevance_score = models.FloatField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-relevance_score']
    
    def __str__(self):
        return f"Result for Query {self.query.id} from {self.source_database}"

class MCPTool(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=100)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_execution = models.DateTimeField(null=True)
    execution_count = models.IntegerField(default=0)
    average_execution_time = models.FloatField(default=0.0)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.agent.name})"
