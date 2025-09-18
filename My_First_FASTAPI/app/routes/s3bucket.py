from fastapi import APIRouter, HTTPException
from app.models.aws_creds import get_aws_credentials_from_master
from app.models.aws_session import create_boto3_session
from app.models.json_data import AWSS3Bucket
from app.models.snow_update import update_snow_ticket, route_snow_ticket, close_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import logging
import boto3

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
def AWS_S3(request: AWSS3Bucket):
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
            s3_client = session.client("s3", region_name=request.region)
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                        f"Successfully connected to {request.aws_account_name}.")
        except:
            route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                            f"Failed to connect to {request.aws_account_name}", 2, "Windows")
            raise HTTPException(status_code=400, detail="Failed to connect.")
        
        # Step 3: Checking if it is us-east-1 region
        if request.region == "us-east-1":
            response = s3_client.create_bucket(Bucket=request.bucket_name)
        else:
            response = s3_client.create_bucket(Bucket=request.bucket_name,CreateBucketConfiguration={"LocationConstraint": request.region})

        close_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                          f"S3 uckBucket created successfully. Bucket Name: {request.bucket_name} under the region {request.region}.",3)
        logger.info(f"S3 bucket {request.bucket_name} created successfully.")
        return {
            "status": "success",
            "bucket_name": request.bucket_name,
            "region": request.region,
            "response": response
        }
    
    except Exception as e:
        logger.error(f"Failed to create bucket {request.bucket_name}: {e}")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed to create bucket {request.bucket_name}: {e}", 2, "Windows")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
