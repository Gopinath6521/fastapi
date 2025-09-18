import requests
from requests.auth import HTTPBasicAuth
from app.models.json_data import AzureWindowsVMProvisionRequest
from app.models.json_data import AWSWindowsEC2ProvisionRequest
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

key_vault_url = "https://fastapikv.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)

snow_url = client.get_secret("ServiceNow-URL").value
snow_user = client.get_secret("SNOW-User").value
snow_pass = client.get_secret("SNOW-Pass").value

# print("From Azure")
# print(f"ServiceNow URL: {snow_url}")
# print(f"ServiceNow User: {snow_user}")
# print(f"ServiceNow Password: {snow_pass}")

def get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number):
    """
    Fetches the sys_id of a ServiceNow SCTASK given its number.
    """
    table = "sc_task"
    url = f"{snow_url}/api/now/table/{table}"

    query_params = {
        'sysparm_query': f'number={sctask_number}',
        'sysparm_fields': 'sys_id',
        'sysparm_limit': 1
    }

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=query_params,
        auth=HTTPBasicAuth(snow_user, snow_pass)
    )

    if response.status_code != 200:
        raise Exception(f"Failed to fetch SCTASK sys_id. Status: {response.status_code}, Response: {response.text}")

    result = response.json()
    if result["result"]:
        return result["result"][0]["sys_id"]
    else:
        raise ValueError(f"No SCTASK found with number: {sctask_number}")


# # Only used for testing this file directly
# if __name__ == "__main__":
#     # sctask_number = "TASK0000001"  # <-- Define it only here
#     print(snow_url, snow_user, snow_pass, sctask_number)
#     try:
#         sys_id = get_sctask_sys_id(snow_url, snow_user, snow_pass, sctask_number)
#         print(f"SCTASK sys_id: {sys_id}")
#     except Exception as e:
#         print(f"Error occurred: {e}")
