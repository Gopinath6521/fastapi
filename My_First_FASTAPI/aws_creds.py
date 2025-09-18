# import boto3
# import json

# def get_aws_credentials(secret_name, region_name):
#     # Create a Secrets Manager client
#     session = boto3.session.Session()
#     client = session.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )

#     try:
#         # Retrieve the secret value
#         response = client.get_secret_value(SecretId=secret_name)

#         # Secrets Manager returns either SecretString or a binary
#         if 'SecretString' in response:
#             secret_data = response['SecretString']
#             credentials = json.loads(secret_data)
#         else:
#             # Decode binary secret
#             secret_data = response['SecretBinary'].decode('utf-8')
#             credentials = json.loads(secret_data)

#         # Extract Access and Secret Keys
#         aws_access_key_id = credentials.get("AWS_ACCESS_KEY_ID")
#         aws_secret_access_key = credentials.get("AWS_SECRET_ACCESS_KEY")

#         return aws_access_key_id, aws_secret_access_key

#     except Exception as e:
#         print(f"Error retrieving secret: {e}")
#         return None, None

# if __name__ == "__main__":
#     # Replace with your secret name and region
#     secret_name = "AWSAccount3"
#     region_name = "us-east-1"

#     access_key, secret_key = get_aws_credentials(secret_name, region_name)
#     if access_key and secret_key:
#         print(f"AWS Access Key: {access_key}")
#         print(f"AWS Secret Key: {secret_key}")
#     else:
#         print("Failed to retrieve AWS credentials.")


import json
import boto3
import requests
from requests.auth import HTTPBasicAuth
# from app.models.json_data import AWSWindowsEC2ProvisionRequest

def get_aws_credentials_from_master(secret_name: str):
    try:
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(SecretId=secret_name)
        
        print("=== RAW SECRET STRING ===")
        print(response["SecretString"])  # <-- See exactly what AWS returns
        
        secret_data = json.loads(response["SecretString"])
        
        return secret_data.get("ServiceNow-URL"), secret_data.get("SNOW-User"), secret_data.get("SNOW-Pass")
    
    except Exception as e:
        raise RuntimeError(f"Error fetching secret '{secret_name}': {e}")

# Test call
snow_url, snow_user, snow_pass = get_aws_credentials_from_master("SNOWcreds")

print(f"ServiceNow URL: {snow_url}")
print(f"ServiceNow User: {snow_user}")
print(f"ServiceNow Password: {snow_pass}")

# sctask_number = "SCTASK0010003"

def get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number):
    """
    Fetches the sys_id of a ServiceNow SCTASK given its number.
    """
    table = "sc_task"
    url = f"{snow_url}/api/now/table/{table}"
    
    print(f"{url}")

    query_params = {
        'sysparm_query': f'number={sctask_number}',
        'sysparm_fields': 'sys_id',
        'sysparm_limit': 1
    }

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=query_params, auth=HTTPBasicAuth(snow_user, snow_pass))

    if response.status_code != 200:
        raise Exception(f"Failed to fetch SCTASK sys_id. Status: {response.status_code}, Response: {response.text}")

    result = response.json()
    if result["result"]:
        return result["result"][0]["sys_id"]
    else:
        raise ValueError(f"No SCTASK found with number: {sctask_number}")

if __name__ == "__main__":
    try:
        sys_id = get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number)
        print(f"SCTASK sys_id: {sys_id}")
    except Exception as e:
        print(f"Error occurred: {e}")
