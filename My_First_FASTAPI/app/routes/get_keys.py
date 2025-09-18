from fastapi import APIRouter, Query
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

router = APIRouter()

# key_vault_url = settings.key_vault_url 

@router.get("/")
def get_keys(key_vault_name: str = Query(..., description="Name of the Key Vault"),
             key_vault_value: str = Query(..., description="Name of the secret in Key Vault")):
    key_vault_url = f"https://{key_vault_name}.vault.azure.net"
    # return {"message": "keyvault value"}
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    try:
        secret_value = client.get_secret(key_vault_value).value
        return {"secret_value": secret_value}
    except Exception as e:
        return {"error": str(e)}
    