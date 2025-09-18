import boto3
import json
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient

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

def test_azure_credentials(subscription_id: str):
    # Step 1: Get credentials from AWS Secrets Manager
    creds = get_azure_credentials(subscription_id)

    if not creds:
        print("❌ No credentials found for subscription:", subscription_id)
        return

    try:
        # Step 2: Build Azure credential object
        credential = ClientSecretCredential(
            tenant_id=creds["tenant_id"],
            client_id=creds["client_id"],
            client_secret=creds["client_secret"]
        )

        # Step 3: Try listing subscriptions using Azure SDK
        subscription_client = SubscriptionClient(credential)
        subs = list(subscription_client.subscriptions.list())

        print("✅ Successfully authenticated to Azure!")
        for sub in subs:
            print(f"   - Subscription ID: {sub.subscription_id}, Name: {sub.display_name}")

    except Exception as e:
        print("❌ Authentication failed:", str(e))

# ✅ Run the function directly
if __name__ == "__main__":
    subscription_id = "6bc3cd1b-2dc4-45cf-ba4d-235f05368ea7"   # 🔹 replace with your actual secret name
    creds = get_azure_credentials(subscription_id)
    print("🔑 Retrieved Azure Credentials:")
    print(json.dumps(creds, indent=4))

# Run test
if __name__ == "__main__":
    test_azure_credentials("6bc3cd1b-2dc4-45cf-ba4d-235f05368ea7")  # replace with your subscription_id/secret name
