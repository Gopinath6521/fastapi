import boto3
import json

def get_azure_credentials(subscription_id: str, region_name: str = "us-east-1"):
    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=subscription_id)
        print("🔍 Raw Secret Response:", response)  # Debug print

        secret_dict = json.loads(response["SecretString"])
        print("✅ Parsed Secret:", secret_dict)

        return {
            "tenant_id": secret_dict.get("tenant_id"),
            "client_id": secret_dict.get("client_id"),
            "client_secret": secret_dict.get("client_secret"),
            "subscription_id": subscription_id
        }
    except Exception as e:
        print("❌ Error retrieving secret:", str(e))
        return {}

# ✅ Run the function directly
if __name__ == "__main__":
    subscription_id = "6bc3cd1b-2dc4-45cf-ba4d-235f05368ea7"   # 🔹 replace with your actual secret name
    creds = get_azure_credentials(subscription_id)
    print("🔑 Retrieved Azure Credentials:")
    print(json.dumps(creds, indent=4))
