from fastapi import APIRouter, HTTPException
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from app.models.azure_creds import get_azure_credentials_from_aws
from app.models.azure_session import test_azure_connection
from app.models.json_data import AzureBackupVM
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import logging
import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")  
def backup_vm(request: AzureBackupVM):
    try:
        # Get SNOW sys_id
        sctask_number = request.sctask_number
        sys_id = get_sctask_sys_id_aws_azure(snow_url, snow_user, snow_pass, sctask_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")

    try:
        # Step 1: Fetch creds
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Testing connectivity with {request.subscription_id}.")
        creds = get_azure_credentials_from_aws(request.subscription_id)

        # Step 2: Test Azure connection
        test_azure_connection(
            tenant_id=creds["tenant_id"],
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            subscription_id=request.subscription_id
        )

        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Successfully connected to {request.subscription_id}.")

        # Step 3: Authenticate with Azure
        credential = ClientSecretCredential(
            tenant_id=creds["tenant_id"],
            client_id=creds["client_id"],
            client_secret=creds["client_secret"]
        )
        compute_client = ComputeManagementClient(credential, request.subscription_id)

        # Step 4: Get VM details
        vm = compute_client.virtual_machines.get(request.resource_group, request.vm_name)

        # Step 5: Prepare timestamp for unique snapshot names
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

        # Step 6: Backup OS disk
        os_disk = vm.storage_profile.os_disk
        os_snapshot_name = f"{request.vm_name}-osdisk-snap-{timestamp}"
        os_snapshot_params = {
            "location": vm.location,
            "creation_data": {
                "create_option": "Copy",
                "source_resource_id": os_disk.managed_disk.id
            }
        }
        compute_client.snapshots.begin_create_or_update(
            request.resource_group, os_snapshot_name, os_snapshot_params
        )
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Snapshot {os_snapshot_name} initiated for OS disk of VM {request.vm_name}")

        # Step 7: Backup data disks (if any)
        if vm.storage_profile.data_disks:
            for i, disk in enumerate(vm.storage_profile.data_disks):
                data_snap_name = f"{request.vm_name}-datadisk{i}-snap-{timestamp}"
                data_snap_params = {
                    "location": vm.location,
                    "creation_data": {
                        "create_option": "Copy",
                        "source_resource_id": disk.managed_disk.id
                    }
                }
                compute_client.snapshots.begin_create_or_update(
                    request.resource_group, data_snap_name, data_snap_params
                )
                close_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Snapshot {data_snap_name} completed for Data disk {i} of VM {request.vm_name}",3)

        return {"status": "success", "message": f"Backup snapshots completed for VM {request.vm_name}"}

    except Exception as e:
        logger.error(f"Failed to backup VM {request.vm_name}: {e}")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id,f"Failed to backup VM {request.vm_name}: {str(e)}", 2, "Windows")
        raise HTTPException(status_code=500, detail=f"Failed to backup VM {request.vm_name}. Error: {str(e)}")
