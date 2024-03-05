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
        print("Generating prompt with sentiment")

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
        print(f"Generated prompt")

        return prompt, sentiment, json_prompt

    def process_and_save_results(self, model, sentiment, categories_json, prompt, extracted_text, request_body, full_response, duration):
        print(f"Processing results for model: {model}")
        if isinstance(full_response, dict):
            response_for_storage = {k: v for k, v in full_response.items() if k != 'body'}
        else:
            response_for_storage = {"error": "Unexpected response format"}
        try:
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
        except Exception as e:
            print(f"Error saving item for {model}: {e}")

    def invoke_model_and_process(self, invoke_func, model_id, prompt, sentiment, categories_json):
        try:
            # invoke_func is either self.brt_client.invoke_model or generator.invoke_model
            extracted_text, request_body, full_response, duration = invoke_func(model_id=model_id, prompt=prompt)
            self.process_and_save_results(model_id, sentiment, categories_json, prompt, extracted_text, request_body, full_response, duration)
        except Exception as e:
            print(f"Error invoking model {model_id}: {e}")

    def invoke_models_and_save(self, prompt, sentiment, categories_json):
        print("Invoking models and preparing to save concurrently...")
        
        # Define a list to collect futures
        futures = []

        # Initialize ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            # Schedule built-in model tasks
            for model in ["ai21.j2-ultra-v1", "amazon.titan-text-express-v1", "meta.llama2-70b-chat-v1", "anthropic.claude-v2"]:
                # Note: We're passing a lambda or partial to submit to correctly bind the current loop variable's value
                futures.append(executor.submit(self.invoke_model_and_process, self.brt_client.invoke_model, model, prompt, sentiment, categories_json))

            # Schedule ContentGenerator model tasks
            for model_id, generator in self.content_generators.items():
                futures.append(executor.submit(self.invoke_model_and_process, generator.invoke_model, model_id, prompt, sentiment, categories_json))

            # Wait for all futures to complete
            for future in as_completed(futures):
                # This block can be used to process results or catch exceptions
                # For example, future.result() will re-raise any exception caught during execution
                try:
                    result = future.result()
                    # Process result (if needed)
                except Exception as e:
                    # Handle exception
                    print(f"Task raised an exception: {e}")