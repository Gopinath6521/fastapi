from fastapi import APIRouter, HTTPException
from app.models.aws_creds import get_aws_credentials_from_master
from app.models.aws_session import create_boto3_session
from app.models.json_data import AWSEBSProvision
from app.models.snow_update import update_snow_ticket, route_snow_ticket, close_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import logging
import boto3

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
def AWS_EBS(request: AWSEBSProvision):
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
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                            f"AWS credentials not found for account: {request.aws_account_name}", 2, "Windows")
            raise HTTPException(status_code=400, detail="AWS credentials not found")

        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                        f"Credentials fetched successfully for {request.aws_account_name}.")
        
        # Step 2: Create boto3 session
        try:
            session = create_boto3_session(access_key, secret_key)
            ec2_client = session.client("ec2", region_name=request.region)
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                        f"Successfully connected to {request.aws_account_name}.")
        except:
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                            f"Failed to connect to {request.aws_account_name}", 2, "Windows")
            raise HTTPException(status_code=400, detail="Failed to connect.")

        # Get the AZ of the EC2 Instance
        try:
            response = ec2_client.describe_instances(InstanceIds=[request.instance_id])
            instance = response["Reservations"][0]["Instances"][0]
            # Availability zone
            availability_zone = instance["Placement"]["AvailabilityZone"]

            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"EC2 instance is in {availability_zone}")

        except:
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Failed to fetch EC2 details.", 2, "Windows")
            raise HTTPException(status_code=400, detail="Failed to fetch EC2 details.")

         # Collect currently attached devices
        used_devices = [bdm["DeviceName"] for bdm in instance.get("BlockDeviceMappings", [])]
        print(f"Currently attached devices: {used_devices}")

        # Define a list of candidate device names (Linux style, AWS remaps them internally)
        candidate_devices = [f"/dev/sd{chr(letter)}" for letter in range(ord("f"), ord("z")+1)]

        # Find the first unused device
        device_name = None
        for candidate in candidate_devices:
            if candidate not in used_devices:
                device_name = candidate
                break

        if not device_name:
            raise RuntimeError("No available device names found!")

        print(f"Next available device name: {device_name}")


        # Provision the EBS Volume
        try:
            create_volume = response.create_volume(
            AvailabilityZone=availability_zone,  # Must match the instance AZ
            Size=request.volume_size_in_gb,  # in GiB
            VolumeType="gp3",  # gp3 is default now (you can choose gp2/io1/io2/sc1/st1)
            TagSpecifications=[
                {
                    "ResourceType": "volume",
                    "Tags": [{"Key": "Name", "Value": f"{request.instance_id}-extra-volume"}]
                }
                ]
            )
            volume_id = response["VolumeId"] 
            print(f"Created volume {volume_id} in {availability_zone}")
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Created volume {volume_id} in {availability_zone}")
        except:
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Failed to create volume.", 2, "Windows")
            raise HTTPException(status_code=400, detail="Failed to create volume.")

        # Step 2: Wait until the volume is available
        waiter = response.get_waiter("volume_available")
        waiter.wait(VolumeIds=[volume_id])
        print(f"Volume {volume_id} is now available")

        try:
            attach_response = response.attach_volume(
                InstanceId=request.instance_id,
                VolumeId=volume_id,
                Device=device_name
            )

            print(f"Attached volume {volume_id} to instance {request.instance_id} as {device_name}")
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Attached volume {volume_id} to instance {request.instance_id} as {device_name}")
            return attach_response
        
        except:
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed to attach the newly created EBS Volume to {request.instance_id}: {e}", 2, "Windows")
            raise HTTPException(status_code=500, detail=f"Failed to attach the newly created EBS Volume to {request.instance_id}: {e}")

    except Exception as e:
        logger.error(f"Failed to create EBS Volume for {request.instance_id}: {e}")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed to create EBS Volume for {request.instance_id}: {e}", 2, "Windows")
        raise HTTPException(status_code=500, detail=f"Failed to create EBS Volume for {request.instance_id}: {str(e)}")
