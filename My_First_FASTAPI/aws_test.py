import requests
from requests.auth import HTTPBasicAuth
import boto3
import json

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


# import boto3
# import json
# # from app.config import MASTER_AWS_REGION
# # from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket

# def get_aws_credentials_from_master(secret_name: str):#, snow_url: str, snow_user: str, snow_pass: str, ticket_sys_id: str):
#     """
#     Fetch AWS access/secret key from the master AWS account's Secrets Manager.
#     Secret must contain JSON with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
#     """
    
#     #update_snow_ticket(snow_url, snow_user, snow_pass, ticket_sys_id, "Initiating the Server Provisioning Process.")

#     try:
#         client = boto3.client("SNOWcreds", region_name="us-east-1")
#         response = client.get_secret_value(SecretId=secret_name)
#         secret_data = json.loads(response["SecretString"])
#         return secret_data.get("ServiceNow-URL"), secret_data.get("SNOW-User"), secret_data.get("SNOW-Pass")
    
#     except Exception as e:
#         raise RuntimeError(f"Error fetching secret '{secret_name}': {e}")



# import boto3
# import json

# def get_aws_credentials_from_master(secret_name: str):
#     """
#     Fetch AWS credentials and ServiceNow info from the master AWS account's Secrets Manager.
#     Secret must contain JSON with AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optionally SNOW info.
#     """
#     try:
#         client = boto3.client("secretsmanager", region_name="us-east-1")
#         response = client.get_secret_value(SecretId=secret_name)
#         secret_data = json.loads(response["SecretString"])
        
#         snow_url = secret_data.get("ServiceNow-URL")
#         snow_user = secret_data.get("SNOW-User")
#         snow_pass = secret_data.get("SNOW-Pass")
        
#         # Return as a dictionary (easier to handle)
#         return {
#             "snow_url": snow_url,
#             "snow_user": snow_user,
#             "snow_pass": snow_pass
#         }
    
#     except Exception as e:
#         raise RuntimeError(f"Error fetching secret '{secret_name}': {e}")

# snow_url, snow_user, snow_pass = get_aws_credentials_from_master("SNOWcreds")

# print(f"ServiceNow URL: {snow_url}")
# print(f"ServiceNow User: {snow_user}")
# print(f"ServiceNow Password: {snow_pass}")

# if __name__ == "__main__":
#     try:
#         snow_url, snow_user, snow_pass = get_aws_credentials_from_master("SNOWcreds")
#         print(f"ServiceNow URL: {snow_url}")
#         print(f"ServiceNow User: {snow_user}")
#         print(f"ServiceNow Password: {snow_pass}")
#     except Exception as e:
#         print(f"Error occurred: {e}")

# def get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number):
#     """
#     Fetches the sys_id of a ServiceNow SCTASK given its number.
#     """
#     table = "sc_task"
#     url = f"{snow_url}/api/now/table/{table}"
    
#     print(f"{url}")

#     query_params = {
#         'sysparm_query': f'number={sctask_number}',
#         'sysparm_fields': 'sys_id',
#         'sysparm_limit': 1
#     }

#     headers = {
#         "Accept": "application/json"
#     }

#     response = requests.get(url, headers=headers, params=query_params, auth=HTTPBasicAuth(snow_user, snow_pass))

#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch SCTASK sys_id. Status: {response.status_code}, Response: {response.text}")

#     result = response.json()
#     if result["result"]:
#         return result["result"][0]["sys_id"]
#     else:
#         raise ValueError(f"No SCTASK found with number: {sctask_number}")

# if __name__ == "__main__":
#     try:
#         sys_id = get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number)
#         print(f"SCTASK sys_id: {sys_id}")
#     except Exception as e:
#         print(f"Error occurred: {e}")










# def get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number):
#     """
#     Fetches the sys_id of a ServiceNow SCTASK given its number.
#     """
#     table = "sc_task"
#     url = f"{snow_url}/api/now/table/{table}"

#     query_params = {
#         'sysparm_query': f'number={sctask_number}',
#         'sysparm_fields': 'sys_id',
#         'sysparm_limit': 1
#     }

#     headers = {
#         "Accept": "application/json"
#     }

#     response = requests.get(
#         url,
#         headers=headers,
#         params=query_params,
#         auth=HTTPBasicAuth(snow_user, snow_pass)
#     )

#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch SCTASK sys_id. Status: {response.status_code}, Response: {response.text}")

#     result = response.json()
#     if result["result"]:
#         return result["result"][0]["sys_id"]
#     else:
#         raise ValueError(f"No SCTASK found with number: {sctask_number}")


# # # Only used for testing this file directly
# # if __name__ == "__main__":
# #     # sctask_number = "TASK0000001"  # <-- Define it only here
# #     print(snow_url, snow_user, snow_pass, sctask_number)
# #     try:
# #         sys_id = get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number)
# #         print(f"SCTASK sys_id: {sys_id}")
# #     except Exception as e:
# #         print(f"Error occurred: {e}")
