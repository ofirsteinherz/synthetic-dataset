from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import json

class ModelPromptProcessor:
    def __init__(self, categories, brt_client, db_instance, content_generators):
        self.categories = categories
        self.brt_client = brt_client
        self.db = db_instance
        self.content_generators = content_generators  # Dictionary of ContentGenerator instances
        print("ModelPromptProcessor initialized.")  # Confirm initialization

    def generate_prompt_with_sentiment(self):
        print("Generating prompt with sentiment...")

        sentiment = random.choice(["positive", "negative"])
        categories_list = self.categories['data']
        selected_categories = random.sample(categories_list, 3)
        
        category_topic_pairs = {}
        for category in selected_categories:
            topic = random.choice(category["topics"])
            category_topic_pairs[category['category']] = topic
        
        json_prompt = json.dumps(category_topic_pairs, ensure_ascii=False)
        topics_list = "\n".join(f"- {cat['category']}: {random.choice(cat['topics'])}" for cat in selected_categories)
        
        prompt = f"""Human:
You are tasked with creating a single sentence that encapsulates a specific sentiment, given topics from specified categories. 
The sentiment is {sentiment}, with the topics:
{topics_list}
The output should be concise and limited to this sentence alone, with no additional explanations, comments, or queries following it. 
The response must reflect a positive outlook or outcome despite the context of tiredness.

Here's a sentence that fits the criteria you've described:
Assistant:
"""        
        print(f"Generated prompt: {prompt}, Sentiment: {sentiment}, Categories JSON: {json_prompt}")

        return prompt, sentiment, json_prompt

    def invoke_models_and_save(self, prompt, sentiment, categories_json):
        print("Invoking models and preparing to save...")

        model_names = ["ai21.j2-ultra-v1", "amazon.titan-text-express-v1", "meta.llama2-70b-chat-v1", "anthropic.claude-v2"]

        # Process built-in models one by one
        for model in model_names:
            print(f"Invoking model: {model}")
            try:
                extracted_text, request_body, full_response, duration = self.brt_client.invoke_model(model_id=model, prompt=prompt)
                self.process_and_save_results(model, sentiment, categories_json, prompt, extracted_text, request_body, full_response, duration)
            except Exception as e:
                print(f"Error invoking built-in model {model}: {e}")

        # Invoke ContentGenerator models one by one
        for model_id, generator in self.content_generators.items():
            print(f"Invoking ContentGenerator model: {model_id}")
            try:
                extracted_text, request_body, full_response, duration = generator.invoke_model(model_id=model_id, prompt=prompt)
                self.process_and_save_results(model_id, sentiment, categories_json, prompt, extracted_text, request_body, full_response, duration)
            except Exception as e:
                print(f"Error invoking ContentGenerator model {model_id}: {e}")

    def process_and_save_results(self, model, sentiment, categories_json, prompt, extracted_text, request_body, full_response, duration):
        if isinstance(full_response, dict):
            response_for_storage = {k: v for k, v in full_response.items() if k != 'body'}
        else:
            response_for_storage = {"error": "Unexpected response format"}

        self.db.write_item(
            model=model, 
            sentiment=sentiment, 
            categories=categories_json, 
            prompt=prompt, 
            run_time=duration, 
            response=extracted_text, 
            request_body=request_body,
            full_response=response_for_storage
        )

        print(f"Data saved for model: {model}")