
from fastapi import APIRouter, HTTPException
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from app.models.azure_creds import get_azure_credentials_from_aws
from app.models.azure_session import test_azure_connection
from app.models.json_data import AzureStopVM
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import logging
import sys

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
def azure_start_vm(request: AzureStopVM):
    # Get SCTASK Details from ServiceNow
    try:
        # Get SNOW sys_id
        sctask_number = request.sctask_number
        sys_id = get_sctask_sys_id_aws_azure(snow_url, snow_user, snow_pass, sctask_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}")
    
    # Validate the swagger UI inputs
    try:
        VM_names = request.vm_name.strip()
        rg_groups = request.resource_group.strip()

        vms, rgs = [], []  # initialize

        # Case 1: Both inputs contain commas → multiple inputs
        if "," in VM_names and "," in rg_groups:
            vms = [v.strip() for v in VM_names.split(",") if v.strip()]
            rgs = [r.strip() for r in rg_groups.split(",") if r.strip()]
            print("Multiple inputs detected")
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, "Multiple inputs detected")

            if len(vms) == len(rgs):
                print("No of VM is equal to no of RG")
                update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                                f"No of VM is equal to no of RG. VM->{vms} RG->{rgs}")
            else:
                msg = f"Validation failed: {len(vms)} VM(s) but {len(rgs)} RG(s)"
                print(msg)
                update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
                raise HTTPException(status_code=400, detail=msg)

        # Case 2: Both inputs do NOT contain commas → single input
        elif "," not in VM_names and "," not in rg_groups:
            vms = [VM_names]
            rgs = [rg_groups]
            print("Single input detected")
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id,
                            f"Single input detected. VM->{vms} RG->{rgs}")

        # Case 3: Inconsistent → one has a comma, the other doesn’t
        else:
            msg = "Inconsistency detected: either both inputs must be comma-separated or both single values."
            print(msg)
            update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, msg)
            raise HTTPException(status_code=400, detail=msg)

        # Final parsed lists
        print(f"Parsed VMs: {vms}")
        print(f"Parsed RGs: {rgs}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse the inputs: {str(e)}")

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
    except:
        raise HTTPException(status_code=500, detail=f"Failed to establish connection with the target subscription:{request.subscription_id} with the error message {str(e)}")
    
    success_vms = []
    failed_vms = []
    for vm, rg in zip(vms, rgs):
        print(f"VM: {vm} -> Resource Group: {rg}")  
    
    try:
        print(f"Starting VM: {vm} in {rg}...")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Starting VM: {vm} in {rg}...")
        async_start = compute_client.virtual_machines.begin_start(
            resource_group_name=rg,
            vm_name=vm
        )
        async_start.result()
        print(f"✅ {vm} started successfully!")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"✅ {vm} started successfully!")
        success_vms.append({"vm": vm, "resource_group": rg})
    except Exception as e:
        print(f"❌ Error starting {vm} in {rg}: {e}")
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"❌ Error starting {vm} in {rg}: {e}")
        failed_vms.append({"vm": vm, "resource_group": rg, "error": str(e)})

    if len(success_vms) == len(vms):
        print("All the requested servers are started successfully")
        close_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"All the requested servers are started successfully. VM->{vms}", 3)
    elif len(failed_vms) == len(vms):
        print("All the requested vms failed to start")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"All the requested vms failed to start. Failed VM's->{failed_vms}", 2, "Windows")
    elif len(success_vms) != 0 and len(failed_vms) != 0:
        print(f"Some of the VM's are started successfully {success_vms}")
        print(f"Some of the VM's failed to start {failed_vms}")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed VM's->{failed_vms} Success VM's->{success_vms}", 2, "Windows")
    else:
        print("Some issue occured to start VM")
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Some issue occured to start VM", 2, "Windows")
