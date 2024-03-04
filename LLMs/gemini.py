import requests
import json
import time

class ContentGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        # Mapping model IDs to their base URLs
        self.base_url = {
            "gemini-pro": 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=',
            "gpt-4": 'https://api.openai.com/v1/chat/completions'
        }
        self.default_parameters = { 
            "gemini-pro": {
                "safetySettings": [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}],
                "generationConfig": {"stopSequences": ["Title"], "temperature": 1.0, "maxOutputTokens": 800, "topP": 0.8, "topK": 10}
            },
            "gpt-4": {
                "temperature": 0.7,
                "max_tokens": 512,
                "top_p": 0.95,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            }
        }
        self.response_paths = {
            'gemini-pro': ['candidates', 0, 'content', 'parts', 0, 'text'],
            'gpt-4': ['choices', 0, 'message', 'content']
        }

    def call_model_api(self, model_id, prompt, custom_parameters=None):
        base_url = self.base_url.get(model_id, '')
        if not base_url:
            print(f"Base URL for model {model_id} not found.")
            return {}, 0

        headers = {'Content-Type': 'application/json'}
        if model_id == "gpt-4":
            headers['Authorization'] = f'Bearer {self.api_key}'
            url = base_url
            body = {
                "model": "gpt-4-1106-preview",
                "messages": [{"role": "system", "content": "You are an assistant"}, {"role": "user", "content": prompt}]
            }
            if custom_parameters:
                body.update(custom_parameters)
        else:  # Handling for Gemini
            url = f'{base_url}{self.api_key}'
            body = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if custom_parameters:
                # Directly apply the known correct structure for Gemini custom parameters
                body.update(custom_parameters)

        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(body))
        duration = time.time() - start_time

        if response.status_code != 200:
            print(f"Error calling {model_id} API. HTTP Status: {response.status_code}, Response Body: {response.text}")
            return {"error": "API call failed", "details": response.text, "status_code": response.status_code}, duration

        return body, response.json(), duration

    def count_tokens(self, text):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:countTokens?key={gemini_api_key}'
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": text}]}]}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['totalTokens']
        else:
            print(f"Error in count_tokens: {response.status_code}, {response.text}")
            return None

    def extract_response_text(self, model_id, response):
        # Check if the model ID is supported and has a defined response path
        if model_id not in self.response_paths:
            print(f"Model ID {model_id} not supported.")
            return "Model ID not supported.", 0  # Adjusted to return 0 as token count in case of error
    
        path = self.response_paths[model_id]
        text = response  # Assuming 'response' is already a Python dictionary (decoded JSON)

        # Navigate through the response using the path to extract the text
        for key in path:
            if isinstance(text, dict) and key in text:
                text = text[key]
            elif isinstance(text, list) and isinstance(key, int) and len(text) > key:
                text = text[key]
            else:
                return "Path extraction error.", 0  # Adjusted to return 0 as token count in case of error
    
        # Calculate the token count for the extracted text
        token_count = self.count_tokens(text)
        return text, token_count

    def invoke_model(self, model_id, prompt, custom_parameters=None):
        # Pass custom_parameters to call_model_api
        body, full_response, duration = self.call_model_api(model_id, prompt, custom_parameters)

        # Extract the response and count tokens based on the full response
        extracted_response, output_token_count = self.extract_response_text(model_id, full_response)

        # Count input tokens
        input_token_count = self.count_tokens(prompt)

        # Include token count in the response
        if 'tokenCount' not in full_response:
            full_response['tokenCount'] = {}
        full_response['tokenCount']['input'] = input_token_count
        full_response['tokenCount']['output'] = output_token_count

        return body, extracted_response, full_response, duration

# # Example usage
# from dotenv import load_dotenv
# import os

# # Initialize environment and load API key
# load_dotenv()
# prompt = "Write a story about a magical forest in a sentence."

# # ========== Gemini ==========
# api_key = os.getenv("GEMINI_API_KEY")  # Use OPENAI_API_KEY for GPT-4
# generator = ContentGenerator(api_key)
# custom_params_gemini = {
#     "generationConfig": {
#         "temperature": 0.8,
#         "maxOutputTokens": 500
#     }
# }
# body, extracted_response_gemini, full_response_gemini, duration_gemini = generator.invoke_model(
#     model_id="gemini-pro",
#     prompt=prompt,
#     custom_parameters=custom_params_gemini
# )
# print("Gemini Model Response:", extracted_response_gemini)
# print("Duration:", duration_gemini, "seconds")

# # ========== GPT-4 ==========
# api_key = os.getenv("OPENAI_API_KEY")  # Use OPENAI_API_KEY for GPT-4
# generator = ContentGenerator(api_key)
# custom_params_gpt4 = {
#     "temperature": 0.6,
#     "max_tokens": 256,
#     "top_p": 1
# }
# body, extracted_response_gpt, full_response_gpt, duration_gpt = generator.invoke_model(
#     model_id="gpt-4",
#     prompt=prompt,
#     custom_parameters=custom_params_gpt4
# )
# print("GPT-4 Model Response:", extracted_response_gpt)
# print("Duration:", duration_gpt, "seconds")