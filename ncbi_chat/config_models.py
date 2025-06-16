from django.db import models
from django.core.cache import cache

class SystemConfiguration(models.Model):
    """Singleton model for system-wide configuration parameters"""
    # NCBI Configuration
    NCBI_API_KEY = 'ncbi_api_key'
    RATE_LIMIT = 'rate_limit'
    MAX_CONCURRENT_QUERIES = 'max_concurrent_queries'
    CACHE_DURATION = 'cache_duration'
    
    # Ollama Configuration
    OLLAMA_HOST = 'ollama_host'
    OLLAMA_MODEL_GENERAL = 'ollama_model_general'
    OLLAMA_MODEL_BIOMEDICAL = 'ollama_model_biomedical'
    OLLAMA_MODEL_ANALYSIS = 'ollama_model_analysis'
    OLLAMA_TIMEOUT = 'ollama_timeout'
    
    PARAMETER_CHOICES = [
        # NCBI Parameters
        (NCBI_API_KEY, 'NCBI API Key'),
        (RATE_LIMIT, 'API Rate Limit (requests per second)'),
        (MAX_CONCURRENT_QUERIES, 'Maximum Concurrent Queries'),
        (CACHE_DURATION, 'Cache Duration (seconds)'),
        # Ollama Parameters
        (OLLAMA_HOST, 'Ollama API Host'),
        (OLLAMA_MODEL_GENERAL, 'General Purpose Model'),
        (OLLAMA_MODEL_BIOMEDICAL, 'Biomedical Model'),
        (OLLAMA_MODEL_ANALYSIS, 'Analysis Model'),
        (OLLAMA_TIMEOUT, 'Ollama Request Timeout (seconds)'),
    ]
    
    parameter_name = models.CharField(max_length=50, choices=PARAMETER_CHOICES, unique=True)
    parameter_value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # First save to database
        super().save(*args, **kwargs)
        try:
            # Then update cache
            cache.set(f'config_{self.parameter_name}', self.parameter_value, timeout=None)
        except Exception:
            # If cache fails, continue anyway as we have the DB backup
            pass
    
    @classmethod
    def get_value(cls, parameter_name, default=None):
        try:
            # Try to get from cache first
            cached_value = cache.get(f'config_{parameter_name}')
            if cached_value is not None:
                return cached_value
        except Exception:
            pass
            
        # If not in cache or cache fails, get from database
        try:
            config = cls.objects.get(parameter_name=parameter_name)
            value = config.parameter_value
            try:
                # Try to update cache
                cache.set(f'config_{parameter_name}', value, timeout=None)
            except Exception:
                pass
            return value
        except cls.DoesNotExist:
            return default
    
    def __str__(self):
        return f"{self.get_parameter_name_display()}: {self.parameter_value}"
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"
