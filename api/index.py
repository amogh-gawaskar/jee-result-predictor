import sys
import os

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app

# Vercel serverless function handler
def handler(request, response):
    return app(request, response)

# For Vercel
app = app
