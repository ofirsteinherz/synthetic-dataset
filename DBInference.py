import boto3
from boto3.dynamodb.conditions import Key, Attr
import pytz
from datetime import datetime
from decimal import Decimal
from faker import Faker
import random
import json

class DBInference:
    def __init__(self, table_name='ModelExecutionMetadata'):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Adjust the region as necessary
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
        self.faker = Faker()

    def create_table(self):
        try:
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'model', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'timestamp', 'KeyType': 'RANGE'},  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'model', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                ],
                BillingMode='PAY_PER_REQUEST'  # On-Demand mode
            )
            self.table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            print(f"Table {self.table_name} created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")

    def write_item(self, model, sentiment, categories, prompt, run_time, response, request_body, full_response):
        timestamp = datetime.now(pytz.timezone('Asia/Jerusalem')).isoformat()

        item = {
            'model': model,
            'timestamp': timestamp,
            'sentiment': sentiment,
            'categories': categories,
            'prompt': prompt,
            'run_time': Decimal(str(run_time)),
            'response': response,
            'request_body': json.dumps(request_body),
            'full_response': json.dumps(full_response)
        }
        try:
            # Each item can store approximately 68,267 words (400 KB)
            self.table.put_item(Item=item)
            print(f"Item saved successfully: {model}")
        except Exception as e:
            print(f"Error saving item for {model}: {e}")

    def get_items(self, **kwargs):
        try:
            filter_expression = None
            for key, value in kwargs.items():
                if filter_expression:
                    filter_expression = filter_expression & Attr(key).eq(value)
                else:
                    filter_expression = Attr(key).eq(value)
            
            items = []
            last_evaluated_key = None

            # Continue scanning until all pages have been retrieved
            while True:
                if filter_expression:
                    if last_evaluated_key:
                        response = self.table.scan(
                            FilterExpression=filter_expression,
                            ExclusiveStartKey=last_evaluated_key
                        )
                    else:
                        response = self.table.scan(
                            FilterExpression=filter_expression
                        )
                else:
                    if last_evaluated_key:
                        response = self.table.scan(
                            ExclusiveStartKey=last_evaluated_key
                        )
                    else:
                        response = self.table.scan()
                
                items.extend(response['Items'])

                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

            return items
        except Exception as e:
            print(f"Error retrieving items: {e}")
            return []
        
#     def _generate_fake_item(self):
#         categories = {
#             "Intensity Modifiers": self.faker.sentence(),
#             "Temporal Aspects": self.faker.sentence(),
#             "Cultural or Idiomatic Expressions": self.faker.sentence()
#         }
#         return {
#             'model': 'Model' + str(random.randint(1, 5)),
#             'timestamp': datetime.now(pytz.timezone('Asia/Jerusalem')).isoformat(),
#             'sentiment': random.choice(['Positive', 'Neutral', 'Negative']),
#             'categories': categories,
#             'prompt': self.faker.sentence(),
#             'run_time': Decimal(str(round(random.uniform(0.1, 1.5), 2))),
#             'response': self.faker.sentence()
#         }

#     def write_items_batch(self, n):
#         with self.table.batch_writer() as batch:
#             for _ in range(n):
#                 item = self._generate_fake_item()
#                 batch.put_item(Item=item)
#         print(f"Batch write of {n} items completed.")