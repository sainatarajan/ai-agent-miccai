#!/bin/zsh
export DJANGO_SETTINGS_MODULE=ncbi_agent.settings
export PYTHONPATH=/Users/sainatarajan/ddrive/github/ai-agent-miccai
daphne -b 0.0.0.0 -p 8000 ncbi_agent.asgi:application
