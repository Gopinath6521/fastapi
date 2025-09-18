
import logging
from fastapi import APIRouter, HTTPException
from app.models.json_data import AWSWindowsEC2ProvisionRequest
from app.models.aws_creds import get_aws_credentials_from_master
from app.models.aws_session import create_boto3_session
from app.runners.windows_Ec2_runner import run_terraform_provision
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
def provision_aws_ec2(request: AWSWindowsEC2ProvisionRequest):
    try:
        sctask_number = request.sctask_number
        sys_id = get_sctask_sys_id_aws_azure(snow_url, snow_user, snow_pass, sctask_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")

    # Step 1: Get credentials from master account
   
    access_key, secret_key = get_aws_credentials_from_master(request.aws_account_name, snow_url, snow_user, snow_pass, sys_id)
    if not access_key or not secret_key:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"AWS credentials not found for account: {request.aws_account_name}", 2, "Windows")
        raise HTTPException(
            status_code=400,
            detail=f"AWS credentials not found for account: {request.aws_account_name}"
        )
    else:
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Target AWS account {request.aws_account_name} credentials fetched successfully.")

    # Step 2: Create boto3 session for target AWS account
    try:
        session = create_boto3_session(access_key, secret_key)#, snow_url, snow_user, snow_pass, sys_id)
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Successfully connected to the {request.aws_account_name} AWS account.")
    except Exception as e:
        logger.error(f"Failed to create boto3 session: {e}")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Unable to connect to the {request.aws_account_name} with the credentials fetched.", 2, "Windows")
        raise HTTPException(status_code=500, detail="Error creating AWS session")

    # Optional: Validate connection
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
        logger.info(f"Connected to AWS Account: {account_id}")
    except Exception as e:
        logger.error(f"STS call failed: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to validate {request.aws_account_name} connection")

    # Step 3: Map Terraform variables
    update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, "Setting up terraform variables.")
    terraform_vars = {
        "region": request.region,
        "instance_type": request.instance_type,
        "key_name": request.key_name,
        "volume_size": request.volume_size,
        "vm_name": request.vm_name
    }

    # Step 4: Run Terraform provisioning
    try:
        tf_output = run_terraform_provision(snow_url, snow_user, snow_pass, sys_id, terraform_vars, aws_access_key=access_key,aws_secret_key=secret_key, )
        
        instance_id = tf_output.get("instance_id", {}).get("value")
        # public_ip = tf_output.get("public_ip", {}).get("value")
        subnet_id = tf_output.get("subnet_id", {}).get("value")
        security_group_id = tf_output.get("security_group_id", {}).get("value")

        # Prepare ServiceNow update message
        ec2_details_msg = (
            f"EC2 Instance provisioned successfully:\n"
            f"- Instance ID: {instance_id}\n"
            # f"- Public IP: {public_ip}\n"
            f"- Subnet ID: {subnet_id}\n"
            f"- Security Group ID: {security_group_id}"
        )

        close_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"EC2 provisioned successfully. {ec2_details_msg}.", 3)
    except RuntimeError as e:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Terraform provisioning failed: {e}", 2, "Windows")
        logger.error(f"Terraform provisioning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Unexpected error in Terraform run: {e}", 2, "Windows")
        logger.error(f"Unexpected error in Terraform run: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during Terraform execution")

    return {
        "status": "success",
        "account_id": account_id,
        "terraform_output": tf_output
    }
