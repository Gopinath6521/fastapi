from fastapi import APIRouter, HTTPException
from app.models.aws_creds import get_aws_credentials_from_master
from app.models.aws_session import create_boto3_session
from app.models.json_data import AWSWEC2Resize
from app.models.snow_update import update_snow_ticket, route_snow_ticket, close_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/resize")
def resize_aws_ec2(request: AWSWEC2Resize):
    try:
        # Get SNOW sys_id
        sys_id = get_sctask_sys_id_aws_azure(
            snow_url, snow_user, snow_pass, request.sctask_number
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")

    try:
        # Step 1: Get credentials
        access_key, secret_key = get_aws_credentials_from_master(
            request.aws_account_name, snow_url, snow_user, snow_pass, sys_id
        )
        if not access_key or not secret_key:
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"AWS credentials not found for account: {request.aws_account_name}", 2, "Windows")
            raise HTTPException(status_code=400, detail="AWS credentials not found")

        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Credentials fetched successfully for {request.aws_account_name}.")
        
        # Step 2: Create boto3 session
        try:
            session = create_boto3_session(access_key, secret_key)
            ec2_client = session.client("ec2", region_name=request.region)
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Successfully connected to {request.aws_account_name}.")
        except:
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Failed to connect to {request.aws_account_name}", 2, "Windows")
            raise HTTPException(status_code=400, detail="Failed to connect.")
        
        # Step 3: Check current state
        response = ec2_client.describe_instances(InstanceIds=[request.instance_id])
        current_state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        was_running = current_state == "running"
        current_type = response["Reservations"][0]["Instances"][0]["InstanceType"]

        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Current state of EC2 {request.instance_id}: {current_state}")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Current EC2 Instance type is {current_type}")

        # Step 4: Stop the instance if running
        if was_running:
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Stopping EC2 {request.instance_id} before resize.")
            ec2_client.stop_instances(InstanceIds=[request.instance_id])
            waiter = ec2_client.get_waiter("instance_stopped")
            waiter.wait(InstanceIds=[request.instance_id])

        # Step 5: Modify instance type
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Resizing EC2 {request.instance_id} to {request.new_instance_type}.")
        ec2_client.modify_instance_attribute(
            InstanceId=request.instance_id,
            InstanceType={"Value": request.new_instance_type}
        )

        # Step 6: Restart only if VM was running before
        if was_running:
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                               f"Starting EC2 {request.instance_id} after resize.")
            ec2_client.start_instances(InstanceIds=[request.instance_id])
            waiter = ec2_client.get_waiter("instance_running")
            waiter.wait(InstanceIds=[request.instance_id])
            close_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"EC2 {request.instance_id} resized to {request.new_instance_type} and started again.",3)
            return {"status": "success","message": f"EC2 {request.instance_id} resized to {request.new_instance_type} and started again."}
        else:
            close_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"EC2 {request.instance_id} resized to {request.new_instance_type}. It remains stopped (was stopped before resize).",3)
            return {"status": "success","message": f"EC2 {request.instance_id} resized to {request.new_instance_type}. It remains stopped (was stopped before resize)."}

    except Exception as e:
        logger.error(f"Failed to resize EC2 {request.instance_id}: {e}")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Failed to resize EC2 {request.instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resize EC2 {request.instance_id}. Error: {str(e)}")
