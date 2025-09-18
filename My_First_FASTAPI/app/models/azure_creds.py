# aws_secrets.py
import boto3
import json
from botocore.exceptions import ClientError

def get_azure_credentials_from_aws(secret_name: str, region_name: str = "us-east-1"):
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise Exception(f"Error fetching secret: {str(e)}")

    secret = response["SecretString"]
    creds = json.loads(secret)  # Expected JSON: {"tenant_id":"...","client_id":"...","client_secret":"..."}
    return creds
