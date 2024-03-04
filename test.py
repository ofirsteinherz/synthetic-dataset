import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def generate_message(promot):
    """Generate a commit message using GPT-4 and format the response as JSON."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}'
    }

    data = {
        "model": "gpt-4-1106-preview",
        "messages": [
            {"role": "system", "content": "You are an assistant, and you only reply with JSON."},
            {"role": "user", "content": promot}
        ],
        "response_format": {
            "type": "json_object"
        }
    }

    print(headers)

    print()

    print(json.dumps(data))

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        data=json.dumps(data)
    )

    response_json = response.json()
    print(response)
    response_text = response_json['choices'][0]['message']['content']

    try:
        # Assuming the response_text is a string in JSON format
        formatted_response = json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback in case the response isn't in the expected JSON format
        formatted_response = {"message": "Failed to parse response", "bullets": []}
    return formatted_response

print(generate_message("hello!"))