import boto3

# Your current AWS credentials must have permission to assume the target role
sts_client = boto3.client('sts')

# Replace 'arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME' with the actual role ARN you want to assume
role_arn = 'arn:aws:iam::022438919154:role/service-role/AmazonSageMaker-ExecutionRole-20240225T000555'

# Assume the role
assumed_role = sts_client.assume_role(
    RoleArn=role_arn,
    RoleSessionName="AssumedRoleSession"  # This can be any string that helps you identify the session
)

# Extract the temporary credentials
credentials = assumed_role['Credentials']

# Use the temporary credentials to create a boto3 session
session = boto3.Session(
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
)

# Now you can use this session to access AWS services with the permissions of the assumed role
# For example, to access an S3 resource
s3 = session.client('s3')

# Now you can use s3 or other service clients as needed, with the permissions of the assumed role
