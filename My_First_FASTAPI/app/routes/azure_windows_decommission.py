
from fastapi import APIRouter, HTTPException
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from app.models.azure_creds import get_azure_credentials_from_aws
from app.models.azure_session import test_azure_connection
from app.models.json_data import AzureWindowsVMDecommission
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.delete("/")  # Decommission/Azure/Windows-VM
def decommission_vm(request: AzureWindowsVMDecommission):
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
        network_client = NetworkManagementClient(credential, request.subscription_id)

        # Step 4: Get VM details
        vm = compute_client.virtual_machines.get(request.resource_group, request.vm_name)

        nic_ids = [nic.id for nic in vm.network_profile.network_interfaces]
        os_disk = vm.storage_profile.os_disk.managed_disk.id if vm.storage_profile.os_disk else None
        data_disks = [d.managed_disk.id for d in vm.storage_profile.data_disks] if vm.storage_profile.data_disks else []

        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Decommissioning VM {request.vm_name} and related resources.")

        # Step 5: Delete VM
        poller = compute_client.virtual_machines.begin_delete(request.resource_group, request.vm_name)
        poller.wait()

        # Step 6: Delete NICs and Public IPs
        for nic_id in nic_ids:
            rg = nic_id.split("/")[4]
            nic_name = nic_id.split("/")[-1]

            nic = network_client.network_interfaces.get(rg, nic_name)
            # Delete attached Public IPs
            for ip_cfg in nic.ip_configurations:
                if ip_cfg.public_ip_address:
                    pip_id = ip_cfg.public_ip_address.id
                    pip_rg = pip_id.split("/")[4]
                    pip_name = pip_id.split("/")[-1]
                    poller = network_client.public_ip_addresses.begin_delete(pip_rg, pip_name)
                    poller.wait()
                    update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Deleted Public IP {pip_name}")

            poller = network_client.network_interfaces.begin_delete(rg, nic_name)
            poller.wait()
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Deleted NIC {nic_name}")

        # Step 7: Delete Disks (OS + Data)
        if os_disk:
            disk_rg = os_disk.split("/")[4]
            disk_name = os_disk.split("/")[-1]
            poller = compute_client.disks.begin_delete(disk_rg, disk_name)
            poller.wait()
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Deleted OS Disk {disk_name}")

        for d in data_disks:
            disk_rg = d.split("/")[4]
            disk_name = d.split("/")[-1]
            poller = compute_client.disks.begin_delete(disk_rg, disk_name)
            poller.wait()
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Deleted Data Disk {disk_name}")

        # Step 8: Close SNOW ticket
        close_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"VM {request.vm_name} and all related resources successfully decommissioned.",
            3
        )

        return {
            "status": "success",
            "subscription_id": request.subscription_id,
            "vm_name": request.vm_name,
            "resource_group": request.resource_group,
            "message": "VM and related resources successfully decommissioned"
        }

    except Exception as e:
        logger.error(f"Error decommissioning Azure VM: {e}")
        route_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Failed to decommission VM {request.vm_name}: {str(e)}", 2, "Windows"
        )
        raise HTTPException(status_code=500, detail=f"Error decommissioning Azure VM: {str(e)}")
