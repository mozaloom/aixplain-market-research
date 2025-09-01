import json
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mangum import Mangum
import asyncio

# Import your FastAPI app
try:
    from api import app
except ImportError:
    # Fallback if direct import fails
    import importlib.util
    spec = importlib.util.spec_from_file_location("api", os.path.join(os.path.dirname(__file__), "api.py"))
    api_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api_module)
    app = api_module.app

# Create the Lambda handler
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    try:
        # Use Mangum to handle the Lambda event
        return handler(event, context)
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
