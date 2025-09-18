import requests
from requests.auth import HTTPBasicAuth
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json

key_vault_url = "https://fastapikv.vault.azure.net/"

# Authenticate using DefaultAzureCredential (supports Managed Identity, ENV vars, etc.)
credential = DefaultAzureCredential()

# Create Secret Client
client = SecretClient(vault_url=key_vault_url, credential=credential)

snow_url = client.get_secret("ServiceNow-URL").value
snow_user =  client.get_secret("SNOW-User").value
snow_pass = client.get_secret("SNOW-Pass").value
sctask_number = "TASK0000001"
table = "sc_task"
print (snow_url, snow_user, snow_pass, sctask_number)

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
