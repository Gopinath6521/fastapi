import boto3
import json
from app.config import MASTER_AWS_REGION
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket

def get_aws_credentials_from_master(secret_name: str, snow_url: str, snow_user: str, snow_pass: str, ticket_sys_id: str):
    """
    Fetch AWS access/secret key from the master AWS account's Secrets Manager.
    Secret must contain JSON with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
    """

    try:
        update_snow_ticket(snow_url, snow_user, snow_pass, ticket_sys_id, "Successfully fetched the target AWS account credentials.")
        client = boto3.client("secretsmanager", region_name=MASTER_AWS_REGION)
        response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response["SecretString"])
        return secret_data.get("AWS_ACCESS_KEY_ID"), secret_data.get("AWS_SECRET_ACCESS_KEY")
    
    except Exception as e:
        route_snow_ticket(snow_url, snow_user, snow_pass, ticket_sys_id, f"Failed to fetch the target AWS account", 2, "Windows")
        raise RuntimeError(f"Error fetching secret '{secret_name}': {e}")


# Only used for testing this file directly
# if __name__ == "__main__":
#     try:
#         creds = get_aws_credentials_from_master("AWSAccount2")
#         print(f"SCTASK sys_id: {creds}")
#     except Exception as e:
#         print(f"Error occurred: {e}")
