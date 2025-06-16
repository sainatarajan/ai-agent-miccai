from django.conf import settings
from ..config_models import SystemConfiguration

def get_ollama_settings():
    """Get Ollama settings from SystemConfiguration"""
    
    # Get model names or use defaults
    general_model = SystemConfiguration.get_value(
        SystemConfiguration.OLLAMA_MODEL_GENERAL, 
        'llama3.2'  # Will be appended with :latest by _normalize_model_name
    )
    biomedical_model = SystemConfiguration.get_value(
        SystemConfiguration.OLLAMA_MODEL_BIOMEDICAL, 
        'llama3.2'
    )
    analysis_model = SystemConfiguration.get_value(
        SystemConfiguration.OLLAMA_MODEL_ANALYSIS, 
        'llama3.2'
    )
    
    return {
        'host': SystemConfiguration.get_value(
            SystemConfiguration.OLLAMA_HOST, 
            'http://localhost:11434'
        ),
        'models': {
            'general': general_model,
            'biomedical': biomedical_model,
            'analysis': analysis_model,
        },
        'timeout': int(SystemConfiguration.get_value(
            SystemConfiguration.OLLAMA_TIMEOUT, 
            30
        )),
        'max_retries': 3
    }
