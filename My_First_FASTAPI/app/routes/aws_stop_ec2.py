
# import logging
# from fastapi import APIRouter, HTTPException
# from app.models.json_data import AWSWStopEC2  # new model for inputs
# from app.models.aws_creds import get_aws_credentials_from_master
# from app.models.aws_session import create_boto3_session
# from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
# from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass

# router = APIRouter()
# logger = logging.getLogger(__name__)

# @router.delete("/")
# def decommission_aws_ec2(request: AWSWStopEC2):
#     try:
#         # Get SNOW sys_id
#         sctask_number = request.sctask_number
#         sys_id = get_sctask_sys_id_aws_azure(snow_url, snow_user, snow_pass, sctask_number)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")
    
#     # Validate the swagger UI inputs
#     try:
#         instance_ids = request.instance_id.strip()
#         regions = request.region.strip()

#         ec2s, regions = [], []  # initialize

#         # Case 1: Both inputs contain commas → multiple inputs
#         if "," in instance_ids and "," in regions:
#             ec2s = [v.strip() for v in instance_ids.split(",") if v.strip()]
#             regions = [r.strip() for r in regions.split(",") if r.strip()]
#             print("Multiple inputs detected")
#             update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, "Multiple inputs detected")

#             if len(ec2s) == len(regions):
#                 print("No of VM is equal to no of RG")
#                 update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
#                                 f"No of EC2 is equal to no of regions. VM->{ec2s} RG->{regions}")
#             else:
#                 msg = f"Validation failed: {len(ec2s)} VM(s) but {len(regions)} RG(s)"
#                 print(msg)
#                 update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
#                 raise HTTPException(status_code=400, detail=msg)

#         # Case 2: Both inputs do NOT contain commas → single input
#         elif "," not in ec2s and "," not in regions:
#             ec2s = [ec2s]
#             regions = [regions]
#             print("Single input detected")
#             update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
#                             f"Single input detected. VM->{ec2s} RG->{regions}")

#         # Case 3: Inconsistent → one has a comma, the other doesn’t
#         else:
#             msg = "Inconsistency detected: either both inputs must be comma-separated or both single values."
#             print(msg)
#             update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
#             raise HTTPException(status_code=400, detail=msg)

#         # Final parsed lists
#         print(f"Parsed EC2s: {ec2s}")
#         print(f"Parsed Regions: {regions}")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to parse the inputs: {str(e)}")

#     # Step 2: Get credentials from master account
#     access_key, secret_key = get_aws_credentials_from_master(
#         request.aws_account_name, snow_url, snow_user, snow_pass, sys_id
#     )
#     if not access_key or not secret_key:
#         route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
#                           f"AWS credentials not found for account: {request.aws_account_name}", 2, "Windows")
#         raise HTTPException(status_code=400, detail="AWS credentials not found")

#     update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
#                        f"Credentials fetched successfully for decommissioning in {request.aws_account_name}.")

#     # Step 2: Create boto3 session for target AWS account
#     try:
#         session = create_boto3_session(access_key, secret_key)#, snow_url, snow_user, snow_pass, sys_id)
#         update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Successfully connected to the {request.aws_account_name} AWS account.")
#     except Exception as e:
#         logger.error(f"Failed to create boto3 session: {e}")
#         route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Unable to connect to the {request.aws_account_name} with the credentials fetched.", 2, "Windows")
#         raise HTTPException(status_code=500, detail="Error creating AWS session")

#     # Optional: Validate connection
#     try:
#         sts_client = session.client("sts")
#         account_id = sts_client.get_caller_identity()["Account"]
#         logger.info(f"Connected to AWS Account: {account_id}")
#     except Exception as e:
#         logger.error(f"STS call failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Unable to validate {request.aws_account_name} connection")

#     success_ec2 = []
#     failed_ec2 = []
#     for ec2, region in zip(ec2s, regions):
#         print(f"VM: {ec2} -> Resource Group: {region}")  


import logging
from fastapi import APIRouter, HTTPException
from app.models.json_data import AWSWStopEC2
from app.models.aws_creds import get_aws_credentials_from_master
from app.models.aws_session import create_boto3_session
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
def stop_aws_ec2(request: AWSWStopEC2):
    # Step 1: Get ServiceNow sys_id
    try:
        sctask_number = request.sctask_number
        sys_id = get_sctask_sys_id_aws_azure(
            snow_url, snow_user, snow_pass, sctask_number
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")
    
    # Step 2: Validate inputs
    try:
        instance_ids_raw = request.instance_id.strip()
        regions_raw = request.region.strip()

        # Case 1: multiple inputs
        if "," in instance_ids_raw and "," in regions_raw:
            ec2s = [v.strip() for v in instance_ids_raw.split(",") if v.strip()]
            regions = [r.strip() for r in regions_raw.split(",") if r.strip()]
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                               f"Multiple inputs detected. EC2s={ec2s}, Regions={regions}")

            if len(ec2s) != len(regions):
                msg = f"Validation failed: {len(ec2s)} EC2(s) but {len(regions)} region(s)"
                update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
                raise HTTPException(status_code=400, detail=msg)

        # Case 2: single input
        elif "," not in instance_ids_raw and "," not in regions_raw:
            ec2s = [instance_ids_raw]
            regions = [regions_raw]
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                               f"Single input detected. EC2={ec2s}, Region={regions}")

        # Case 3: inconsistent inputs
        else:
            msg = "Inconsistency detected: either both inputs must be comma-separated or both single values."
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
            raise HTTPException(status_code=400, detail=msg)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse the inputs: {str(e)}")

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

    # Step 6: Stop EC2 instances
    success_ec2, failed_ec2 = [], []
    for ec2, region in zip(ec2s, regions):
        try:
            ec2_client = session.client("ec2", region_name=region)
            ec2_client.stop_instances(InstanceIds=[ec2])
            success_ec2.append({"ec2": ec2, "region": region})
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                               f"Stop initiated for EC2 {ec2} in region {region}")
        except Exception as e:
            logger.error(f"Failed to stop {ec2} in {region}: {e}")
            failed_ec2.append({"ec2": ec2, "region": region, "error": str(e)})
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                               f"Failed to stop {ec2} in {region}: {str(e)}")

    # Step 7: Final SNOW update
    if failed_ec2:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                          f"Some instances failed to stop: {failed_ec2}", 2, "Windows")
        raise HTTPException(status_code=500, detail={"success": success_ec2, "failed": failed_ec2})
    else:
        close_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                          f"All EC2 instances stopped successfully: {success_ec2}",3)
        return {"status": "success", "stopped_instances": success_ec2}
