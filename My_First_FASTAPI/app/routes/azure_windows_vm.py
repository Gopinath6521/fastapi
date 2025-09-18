from fastapi import APIRouter, HTTPException
from app.models.azure_creds import get_azure_credentials_from_aws
from app.models.azure_session import test_azure_connection
from app.runners.azure_new_runner import run_terraform
from app.models.json_data import AzureWindowsVMProvisionRequest
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket
from app.models.get_sys_id import get_sctask_sys_id_aws_azure, snow_url, snow_user, snow_pass
import json

# ✅ Define the router object
router = APIRouter()

@router.post("/")
def provision_vm(request: AzureWindowsVMProvisionRequest):
    try:
        # Step 1: Get ServiceNow sys_id
        sctask_number = request.sctask_number
        sys_id = get_sctask_sys_id_aws_azure(
            snow_url, snow_user, snow_pass, sctask_number
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get SCTASK sys_id: {str(e)}"
        )

    try:
        # Step 2: Fetch Azure credentials
        update_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Testing connectivity with Azure subscription {request.subscription_id}."
        )
        creds = get_azure_credentials_from_aws(request.subscription_id)

        # Step 3: Test Azure connection
        test_azure_connection(
            tenant_id=creds["tenant_id"],
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            subscription_id=request.subscription_id
        )

        update_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Successfully connected to Azure subscription {request.subscription_id}."
        )
        update_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Setting up Terraform variables."
        )

        # Step 4: Build Terraform vars (✅ Added resource_group_name)
        terraform_vars = {
            "subscription_id": request.subscription_id,
            "tenant_id": creds["tenant_id"],
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "vm_name": request.vm_name,
            "location": request.location,
            "vm_size": request.vm_size,
            "admin_username": request.admin_username,
            "admin_password": request.admin_password,
            "resource_group_name": request.resource_group,  # 👈 Pass from Swagger UI
        }

        update_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Terraform variables set up successfully."
        )
        update_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Initiating Terraform run."
        )

        # Step 5: Run Terraform
        tf_output = run_terraform(terraform_vars)

        # Step 6: Extract Azure VM details
        vm_name = tf_output.get("vm_hostname", {}).get("value")
        private_ip = tf_output.get("vm_private_ip", {}).get("value")
        nic_id = tf_output.get("nic_id", {}).get("value")
        resource_group = tf_output.get("resource_group", {}).get("value")

        # Prepare ServiceNow message
        azure_vm_details_msg = (
            f"Azure Windows VM provisioned successfully:\n"
            f"- VM Name: {vm_name}\n"
            f"- Private IP: {private_ip}\n"
            f"- NIC ID: {nic_id}\n"
            f"- Resource Group: {resource_group}"
        )

        close_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Azure VM provisioned successfully. {azure_vm_details_msg}", 3
        )

        return {
            "status": "success",
            "message": f"Azure VM {request.vm_name} provisioned successfully",
            "details": {
                "vm_name": vm_name,
                "private_ip": private_ip,
                "nic_id": nic_id,
                "resource_group": resource_group,
            },
        }

    except Exception as e:
        route_snow_ticket(
            snow_url, snow_user, snow_pass, sys_id,
            f"Azure provisioning failed for subscription {request.subscription_id}: {str(e)}",
            2,
            "Windows",
        )
        raise HTTPException(status_code=500, detail=str(e))
