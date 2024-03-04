import requests
import json

class ContentGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:'

    def count_tokens(self, text):
        url = f'{self.base_url}countTokens?key={self.api_key}'
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": text}]
            }]
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['totalTokens']
        else:
            print(f"Error in count_tokens: {response.status_code}, {response.text}")
            return None

    def generate_content(self, prompt):
        url = f'{self.base_url}generateContent?key={self.api_key}'
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}],
            "generationConfig": {"stopSequences": ["Title"], "temperature": 1.0, "maxOutputTokens": 800, "topP": 0.8, "topK": 10}
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error in generate_content: {response.status_code}, {response.text}")
            return None

    def process_response(self, response_json, prompt):
        # Extract the generated text
        generated_text = response_json['candidates'][0]['content']['parts'][0]['text']
        print("Generated Text:\n", generated_text)

        # Calculate token counts
        input_token_count = self.count_tokens(prompt)
        output_token_count = self.count_tokens(generated_text)

        # Append token counts to the response JSON
        token_counts = {
            "input": {"totalTokens": input_token_count},
            "output": {"totalTokens": output_token_count}
        }
        response_json['tokenCount'] = token_counts

        # Print the modified response JSON
        print("\nResponse JSON with Token Counts:")
        print(json.dumps(response_json, indent=2))

# Example usage
API_KEY = "AIzaSyAULZfLGV0ha8Ue-fESIEnHosoAR2eyU54"
generator = ContentGenerator(API_KEY)

prompt = "Write a story about a magic backpack."
response_json = generator.generate_content(prompt)
if response_json:
    generator.process_response(response_json, prompt)
