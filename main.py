import boto3
import json
from dotenv import load_dotenv
import os

from LLMs.BedrockRuntimeClient import BedrockRuntimeClient
from LLMs.ApiRuntimeClient import ContentGenerator
from ModelPromotProcessor import ModelPromptProcessor
from DBInference import DBInference

# Load environment variables from .env file
load_dotenv()

prompt = "Write a story about a magical forest in a sentence."

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
    prompt=prompt,
    custom_parameters={'temperature': 0.5, 'topP': 0.9}
)
print("AI21 J2 Model Response:", extracted_response)
print("Duration:", duration, "seconds\n")

# Initialize environment and load API key
# ========== Gemini ==========
api_key = os.getenv("GEMINI_API_KEY")  # Use OPENAI_API_KEY for GPT-4
generator = ContentGenerator(api_key)
custom_params_gemini = {
    "generationConfig": {
        "temperature": 0.8,
        "maxOutputTokens": 500
    }
}
extracted_response_gemini, body, full_response_gemini, duration_gemini = generator.invoke_model(
    model_id="gemini-pro",
    prompt=prompt,
    custom_parameters=custom_params_gemini
)
print("Gemini Model Response:", extracted_response_gemini)
print("Duration:", duration_gemini, "seconds\n")

# ========== GPT-4 ==========
api_key = os.getenv("OPENAI_API_KEY")  # Use OPENAI_API_KEY for GPT-4
generator = ContentGenerator(api_key)
custom_params_gpt4 = {
    "temperature": 0.6,
    "max_tokens": 256,
    "top_p": 1
}
extracted_response_gpt, body, full_response_gpt, duration_gpt = generator.invoke_model(
    model_id="gpt-4",
    prompt=prompt,
    custom_parameters=custom_params_gpt4
)
print("GPT-4 Model Response:", extracted_response_gpt)
print("Duration:", duration_gpt, "seconds")

# categories_data = ""
# with open('topics.json', 'r', encoding='utf-8') as file:
#     categories_data = json.load(file)
    
# # Initialize the necessary components
# brt_client = BedrockRuntimeClient()  # Make sure this client has the updated invoke methods
# db_instance =  DBInference()  # Your database instance for saving items

# # Create the processor instance with your data and components
# processor = ModelPromptProcessor(categories_data, brt_client, db_instance)

# # Generate a prompt and invoke the models to generate responses and save them
# prompt, sentiment, categories_json = processor.generate_prompt_with_sentiment()

# processor.invoke_models_and_save(prompt, sentiment, categories_json)