import boto3
from dotenv import load_dotenv
import os

from LLMs.BedrockRuntimeClient import BedrockRuntimeClient

# Load environment variables from .env file
load_dotenv()

# Use the loaded environment variables to configure boto3
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_default_region = os.getenv('AWS_DEFAULT_REGION')

# Initialize a boto3 session
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_default_region
)



brt_client = BedrockRuntimeClient()

# Invoke a model with some custom parameters
extracted_response, body, full_response, duration = brt_client.invoke_model(
    model_id='ai21.j2-ultra-v1',
    prompt="Discuss the ethical considerations of AI.",
    custom_parameters={'temperature': 0.5, 'topP': 0.9}
)

# extracted_response, body, full_response, duration

print(extracted_response)