from django.core.management.base import BaseCommand
from ncbi_chat.config_models import SystemConfiguration

class Command(BaseCommand):
    help = 'Initialize system configuration with default values'

    def handle(self, *args, **kwargs):
        default_configs = [
            # NCBI Configuration
            {
                'parameter_name': SystemConfiguration.NCBI_API_KEY,
                'parameter_value': '',
                'description': 'API key for NCBI E-utilities. Get one at: https://www.ncbi.nlm.nih.gov/account/settings/'
            },
            {
                'parameter_name': SystemConfiguration.RATE_LIMIT,
                'parameter_value': '3',
                'description': 'Maximum number of requests per second to NCBI E-utilities'
            },
            {
                'parameter_name': SystemConfiguration.MAX_CONCURRENT_QUERIES,
                'parameter_value': '5',
                'description': 'Maximum number of concurrent queries that can be processed'
            },
            {
                'parameter_name': SystemConfiguration.CACHE_DURATION,
                'parameter_value': '86400',
                'description': 'Duration in seconds to cache query results (default: 24 hours)'
            },
            # Ollama Configuration
            {
                'parameter_name': SystemConfiguration.OLLAMA_HOST,
                'parameter_value': 'http://localhost:11434',
                'description': 'Ollama API host address'
            },
            {
                'parameter_name': SystemConfiguration.OLLAMA_MODEL_GENERAL,
                'parameter_value': 'llama3.2',  # Without :latest, will be added by normalize function
                'description': 'General purpose language model for query understanding'
            },
            {
                'parameter_name': SystemConfiguration.OLLAMA_MODEL_BIOMEDICAL,
                'parameter_value': 'llama3.2',
                'description': 'Specialized model for biomedical queries'
            },
            {
                'parameter_name': SystemConfiguration.OLLAMA_MODEL_ANALYSIS,
                'parameter_value': 'llama3.2',
                'description': 'Model for analyzing research results'
            },
            {
                'parameter_name': SystemConfiguration.OLLAMA_TIMEOUT,
                'parameter_value': '30',
                'description': 'Timeout in seconds for Ollama API requests'
            },
        ]

        for config in default_configs:
            obj, created = SystemConfiguration.objects.get_or_create(
                parameter_name=config['parameter_name'],
                defaults={
                    'parameter_value': config['parameter_value'],
                    'description': config['description']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created {config['parameter_name']} configuration")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Configuration {config['parameter_name']} already exists")
                )
        
        self.stdout.write(
            self.style.SUCCESS("\nConfiguration initialized successfully!")
        )
        self.stdout.write(
            self.style.WARNING("\nNote: The default model is set to 'llama3.2'. ")
        )
        self.stdout.write(
            self.style.WARNING("If you don't have this model, install it with: ollama pull llama3.2")
        )
        self.stdout.write(
            self.style.WARNING("Or update the model configuration in the Django admin panel.")
        )