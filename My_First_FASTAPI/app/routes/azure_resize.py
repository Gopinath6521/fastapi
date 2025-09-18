from fastapi import APIRouter, HTTPException
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from app.models.azure_creds import get_azure_credentials_from_aws
from app.models.azure_session import test_azure_connection
from app.models.json_data import AzureVMResize
from app.models.snow_update import update_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/resize")
def resize_vm(request: AzureVMResize):
    try:
        # Get SNOW sys_id
        sys_id = get_sctask_sys_id_aws_azure(
            snow_url, snow_user, snow_pass, request.sctask_number
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")

    try:
        # Step 1: Fetch creds
        creds = get_azure_credentials_from_aws(request.subscription_id)

        # Step 2: Test connection
        test_azure_connection(
            tenant_id=creds["tenant_id"],
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            subscription_id=request.subscription_id
        )

        # Step 3: Authenticate
        credential = ClientSecretCredential(
            tenant_id=creds["tenant_id"],
            client_id=creds["client_id"],
            client_secret=creds["client_secret"]
        )
        compute_client = ComputeManagementClient(credential, request.subscription_id)

        # Step 4: Get VM state
        vm_instance = compute_client.virtual_machines.get(
            request.resource_group, request.vm_name, expand="instanceView"
        )
        power_state = next(
            (s.code for s in vm_instance.instance_view.statuses if s.code.startswith("PowerState")), None
        )
        was_running = power_state == "PowerState/running"

        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                           f"Current state of VM {request.vm_name}: {power_state}")

        # Step 5: If running, deallocate
        if was_running:
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                               f"Deallocating VM {request.vm_name} before resize.")
            async_deallocate = compute_client.virtual_machines.begin_deallocate(
                request.resource_group, request.vm_name
            )
            async_deallocate.wait()

        # Step 6: Resize VM
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                           f"Resizing VM {request.vm_name} to {request.new_size}.")
        async_resize = compute_client.virtual_machines.begin_update(
            request.resource_group,
            request.vm_name,
            {"hardware_profile": {"vm_size": request.new_size}}
        )
        async_resize.wait()

        # Step 7: If VM was running before, start again
        if was_running:
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                               f"Starting VM {request.vm_name} after resize.")
            async_start = compute_client.virtual_machines.begin_start(
                request.resource_group, request.vm_name
            )
            async_start.wait()
            return {"status": "success",
                    "message": f"VM {request.vm_name} resized to {request.new_size} and started again."}
        else:
            return {"status": "success",
                    "message": f"VM {request.vm_name} resized to {request.new_size}. It remains stopped (was stopped before resize)."}

    except Exception as e:
        logger.error(f"Failed to resize VM {request.vm_name}: {e}")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                           f"Failed to resize VM {request.vm_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resize VM {request.vm_name}. Error: {str(e)}")
