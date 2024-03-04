import boto3
from dotenv import load_dotenv
import os

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

sts_client = boto3.client('sts')

# Call the get_caller_identity method
caller_identity = sts_client.get_caller_identity()

# The ARN of the user or role
arn = caller_identity['Arn']

print("ARN:", arn)


# # Now you can use this session to access AWS services
# # For example, creating an S3 client
# s3 = session.client('s3')


# # Try to list S3 buckets
# try:
#     response = s3.list_buckets()
#     # If the call succeeds, we can assume we're connected. Print the bucket names.
#     print("Connected to AWS. S3 Buckets:")
#     for bucket in response['Buckets']:
#         print(f"- {bucket['Name']}")
# except Exception as e:
#     print(f"Failed to connect to AWS: {e}")
    