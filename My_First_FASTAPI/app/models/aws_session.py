import boto3
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket

def create_boto3_session(access_key: str, secret_key: str):
    """
    Create a boto3 session for the requested AWS account using retrieved credentials.
    """
    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        # region_name=region_name
    )
