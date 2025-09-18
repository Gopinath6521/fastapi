import logging
from fastapi import APIRouter, HTTPException
from app.models.json_data import AWSWEC2Backup  # you can reuse the same model since inputs are identical
from app.models.aws_creds import get_aws_credentials_from_master
from app.models.aws_session import create_boto3_session
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
def aws_ec2_backup(request: AWSWEC2Backup):
    # Step 1: Get ServiceNow sys_id
    try:
        sctask_number = request.sctask_number
        sys_id = get_sctask_sys_id_aws_azure(
            snow_url, snow_user, snow_pass, sctask_number
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")
    
    # # Step 2: Validate inputs
    # try:
    #     instance_ids_raw = request.instance_id.strip()
    #     regions_raw = request.region.strip()

    #     # Case 1: multiple inputs
    #     if "," in instance_ids_raw and "," in regions_raw:
    #         ec2s = [v.strip() for v in instance_ids_raw.split(",") if v.strip()]
    #         regions = [r.strip() for r in regions_raw.split(",") if r.strip()]
    #         update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
    #                            f"Multiple inputs detected. EC2s={ec2s}, Regions={regions}")

    #         if len(ec2s) != len(regions):
    #             msg = f"Validation failed: {len(ec2s)} EC2(s) but {len(regions)} region(s)"
    #             update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
    #             raise HTTPException(status_code=400, detail=msg)

    #     # Case 2: single input
    #     elif "," not in instance_ids_raw and "," not in regions_raw:
    #         ec2s = [instance_ids_raw]
    #         regions = [regions_raw]
    #         update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
    #                            f"Single input detected. EC2={ec2s}, Region={regions}")

    #     # Case 3: inconsistent inputs
    #     else:
    #         msg = "Inconsistency detected: either both inputs must be comma-separated or both single values."
    #         update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
    #         raise HTTPException(status_code=400, detail=msg)

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to parse the inputs: {str(e)}")

    # Step 3: Fetch AWS credentials
    access_key, secret_key = get_aws_credentials_from_master(
        request.aws_account_name, snow_url, snow_user, snow_pass, sys_id
    )
    if not access_key or not secret_key:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                          f"AWS credentials not found for account: {request.aws_account_name}", 2, "Windows")
        raise HTTPException(status_code=400, detail="AWS credentials not found")

    update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                       f"Credentials fetched successfully for {request.aws_account_name}.")

    # Step 4: Create boto3 session
    try:
        session = create_boto3_session(access_key, secret_key)
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                           f"Connected to {request.aws_account_name} AWS account.")
    except Exception as e:
        logger.error(f"Failed to create boto3 session: {e}")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                          f"Unable to connect to {request.aws_account_name} account.", 2, "Windows")
        raise HTTPException(status_code=500, detail="Error creating AWS session")

    # Step 5: Validate connection
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
        logger.info(f"Connected to AWS Account: {account_id}")
    except Exception as e:
        logger.error(f"STS call failed: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to validate {request.aws_account_name} connection")
    
    # Step 6: Stop the EC2 isntance
    try:
        ec2_client = session.client("ec2", region_name=request.region)
        ec2_client.stop_instances(InstanceIds=[request.instance_id])
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Stop initiated for EC2 {request.instance_id} in region {request.region}")
    except Exception as e:
        logger.error(f"Failed to stop {request.instance_id} in {request.region}: {e}")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed to stop {request.instance_id} in {request.region}: {str(e)}")

    # Step 7: Backup EC2 instance volumes
    try:
        ec2_client = session.client("ec2", region_name=request.region)

        # 1. Get volumes attached to the instance
        reservations = ec2_client.describe_instances(InstanceIds=[request.instance_id])["Reservations"]
        volumes = []
        for reservation in reservations:
            for instance in reservation["Instances"]:
                for mapping in instance.get("BlockDeviceMappings", []):
                    volume_id = mapping["Ebs"]["VolumeId"]
                    volumes.append(volume_id)

        if not volumes:
            raise RuntimeError(f"No volumes found for EC2 {request.instance_id}")

        # 2. Create snapshots for each volume
        snapshot_ids = []
        success = []
        failed = []
        for vol_id in volumes:
            try:
                snapshot = ec2_client.create_snapshot(VolumeId=vol_id,Description=f"Backup snapshot of {request.instance_id} volume {vol_id}")
                snapshot_ids.append(snapshot["SnapshotId"])
                update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Snapshot {snapshot['SnapshotId']} created for Volume {vol_id} of EC2 {request.instance_id}")
                success.append({vol_id})
            except:
                logger.error(f"Failed to take snapshot of {vol_id} with error: {e}")
                failed.append({vol_id})

    except Exception as e:
        logger.error(f"Failed to backup EC2 {request.instance_id} in {request.region}: {e}")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed to backup EC2 {request.instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unable to initiate backup of {request.instance_id}.")

    # Step 8: Validate the success and failed
    if failed:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Failed to take snapshot of the volumes {failed} in {request.instance_id}", 2, "Windows")
        raise HTTPException(status_code=500, detail={"success": success, "failed": failed})
    else:
        close_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"All volume snapshot completed successfully",3)
        return {"status": "success", "stopped_instances": success}        
