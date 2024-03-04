import boto3
import json
import time

class BedrockRuntimeClient:
    def __init__(self):
        self.brt_client = boto3.client(service_name='bedrock-runtime')
        self.default_parameters = {
            'ai21.j2-ultra-v1': {
                'maxTokens': 200,
                'temperature': 0.1,
                'topP': 1,
                'stopSequences': [],
                'countPenalty': {"scale": 0},
                'presencePenalty': {"scale": 0.8},
                'frequencyPenalty': {"scale": 0.1}
            },
            'amazon.titan-text-express-v1': {
                'maxTokenCount': 2048,
                'stopSequences': ["User:"],
                'temperature': 0.5,
                'topP': 0.9
            },
            'meta.llama2-70b-chat-v1': {
                'temperature': 0.5,
                'top_p': 0.9,
                'max_gen_len': 200
            },
            'anthropic.claude-v2': {
                'max_tokens_to_sample': 200,
                'temperature': 0.5,
                'stop_sequences': ["\n\nHuman:"]
            }
        }
        self.response_paths = {
            'ai21.j2-ultra-v1': ['completions', 0, 'data', 'text'],
            'amazon.titan-text-express-v1': ['results', 0, 'outputText'],
            'meta.llama2-70b-chat-v1': ['generation'],
            'anthropic.claude-v2': ['completion']
        }

    def call_model_api(self, body, model_id):
        start_time = time.time()
        response = self.brt_client.invoke_model(body=body, modelId=model_id, accept='application/json', contentType='application/json')
        end_time = time.time()
        duration = end_time - start_time
        return response, duration

    def extract_response_text(self, model_id, response):
        if model_id not in self.response_paths:
            print(f"Model ID {model_id} not supported.")
            return "Model ID not supported."

        try:
            # Decode the response here
            response_body = json.loads(response['body'].read().decode('utf-8'))

            text = response_body
            for key in self.response_paths[model_id]:
                if isinstance(key, int) or key in text:
                    text = text[key]
                else:
                    raise KeyError
            return text.strip()
        except (KeyError, TypeError, IndexError):
            error_message = f"Response structure unknown or changed for {model_id} model"
            print(error_message)
            return error_message
        
    def invoke_model(self, model_id, prompt, custom_parameters={}):
        parameters = self.default_parameters.get(model_id, {}).copy()
        parameters.update(custom_parameters)

        if model_id == 'amazon.titan-text-express-v1':
            parameters['inputText'] = prompt  # Specific case for Titan Text Express
            body = json.dumps({"inputText": parameters.pop('inputText'), "textGenerationConfig": parameters})
        else:
            parameters['prompt'] = prompt
            body = json.dumps(parameters)

        full_response, duration = self.call_model_api(body, model_id)
        return self.extract_response_text(model_id, full_response), body, full_response, duration