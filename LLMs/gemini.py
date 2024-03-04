import requests
import json
import time

class ContentGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models/'
        self.default_parameters = {
            "safetySettings": [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}],
            "generationConfig": {"stopSequences": ["Title"], "temperature": 1.0, "maxOutputTokens": 800, "topP": 0.8, "topK": 10}
        }
        self.response_paths = {
            'text': ['candidates', 0, 'content', 'parts', 0, 'text']  # Assuming a generic path for simplicity
        }

    def call_model_api(self, model_id, body):
        # Correctly format the URL to include the model_id and API key
        url = f'{self.base_url}{model_id}:generateContent?key={self.api_key}'
        headers = {'Content-Type': 'application/json'}

        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(body))
        duration = time.time() - start_time
        return response.json(), duration

    def count_tokens(self, text):
        url = f'{self.base_url}countTokens?key={self.api_key}'
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": text}]}]}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['totalTokens']
        else:
            print(f"Error in count_tokens: {response.status_code}, {response.text}")
            return None

    def extract_response_text(self, response):
        path = self.response_paths['text']
        text = response
        for key in path:
            if isinstance(text, dict) and key in text:
                text = text[key]
            elif isinstance(text, list) and isinstance(key, int) and len(text) > key:
                text = text[key]
            else:
                return "Path extraction error."
        token_count = self.count_tokens(text)
        return text, token_count

    def invoke_model(self, model_id, prompt, custom_parameters=None):
        parameters = self.default_parameters.copy()
        if custom_parameters:
            parameters['generationConfig'].update(custom_parameters)
        parameters['contents'] = [{"parts": [{"text": prompt}]}]
        
        full_response, duration = self.call_model_api(model_id, parameters)
        extracted_response, token_count = self.extract_response_text(full_response)
        
        # Enhance response with token counts
        full_response['tokenCount'] = token_count
        return extracted_response, parameters, full_response, duration

# Example usage
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
model_id = "gemini-pro"  # Replace with actual model ID
prompt = "Write a story about a magical forest."

generator = ContentGenerator(api_key)
extracted_response, request_body, full_response, duration = generator.invoke_model(model_id, prompt)
print("Extracted Response:", extracted_response)
print("Duration:", duration, "seconds")