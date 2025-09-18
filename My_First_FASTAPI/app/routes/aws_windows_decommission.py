
import logging
from fastapi import APIRouter, HTTPException
from app.models.json_data import AWSWindowsEC2Decommission  # new model for inputs
from app.models.aws_creds import get_aws_credentials_from_master
from app.models.aws_session import create_boto3_session
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass

router = APIRouter()
logger = logging.getLogger(__name__)

@router.delete("/")
def decommission_aws_ec2(request: AWSWindowsEC2Decommission):
    try:
        # Step 1: Get SCTASK sys_id
        sctask_number = request.sctask_number
        sys_id = get_sctask_sys_id_aws_azure(snow_url, snow_user, snow_pass, sctask_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")

    # Step 2: Get credentials from master account
    access_key, secret_key = get_aws_credentials_from_master(
        request.aws_account_name, snow_url, snow_user, snow_pass, sys_id
    )
    if not access_key or not secret_key:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                          f"AWS credentials not found for account: {request.aws_account_name}", 2, "Windows")
        raise HTTPException(status_code=400, detail="AWS credentials not found")

    update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                       f"Credentials fetched successfully for decommissioning in {request.aws_account_name}.")

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

    # Step 4: Terminate the EC2 instance
    try:
        ec2_client = session.client("ec2", region_name=request.region)

        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                           f"Initiating termination of EC2 instance {request.instance_id}.")

        response = ec2_client.terminate_instances(InstanceIds=[request.instance_id])
        current_state = response["TerminatingInstances"][0]["CurrentState"]["Name"]

        # Optional: wait for termination to complete
        waiter = ec2_client.get_waiter("instance_terminated")
        waiter.wait(InstanceIds=[request.instance_id])

        close_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"EC2 instance {request.instance_id} successfully decommissioned in {request.region} "
            f"(Final state: {current_state}).", 3
        )

        return {
            "status": "success",
            "instance_id": request.instance_id,
            "region": request.region,
            "final_state": current_state
        }

    except Exception as e:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                          f"Failed to decommission EC2 instance {request.instance_id}: {str(e)}", 2, "Windows")
        logger.error(f"Failed to terminate EC2 instance: {e}")
        raise HTTPException(status_code=500, detail=f"Error terminating EC2 instance: {str(e)}")
