# azure_session.py
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient

def test_azure_connection(tenant_id, client_id, client_secret, subscription_id):
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    subscription_client = SubscriptionClient(credential)
    subs = [sub.subscription_id for sub in subscription_client.subscriptions.list()]

    if subscription_id not in subs:
        raise Exception(f"Subscription {subscription_id} not accessible.")
    return True
