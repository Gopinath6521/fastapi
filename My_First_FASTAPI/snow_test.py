import json

# Load raw state file

# with open("D:\Study Materials\Python\FASTAPI\My_First_FASTAPI\terraform\Azure\windows_vm\terraform.tfstate", "r") as f:
with open(r"D:\Study Materials\Python\FASTAPI\My_First_FASTAPI\terraform\Azure\windows_vm\terraform.tfstate", "r") as f:
    #  tf_state = json.load(f)


    tf_state = json.load(f)

# Get outputs block

tf_out = tf_state.get("outputs", {})


# Rest of the code same as above

# Desired outputs (your original list)

desired_outputs = [

    "hob_id", "serial_number", "hosting_model", "hosting_platform", "assignment_group",

    "environment", "ip_address", "is_virtual", "location", "manufacturer", "os_version",

    "operating_system", "*sys_class_name", "managing_responsibility_unit", "eam_id", "status",

    "u_environment_id", "fqdn", "u_backup_sla", "u_operating_model", "u_rto", "u_rpo",

    "u_service_stack", "u_storage_sla", "u_technical_service_level", "u_patching_group",

    "u_service_delivery_location", "cpu_core_count", "cpu_core_thread", "cpu_count",

    "cpu_manufacturer", "cpu_name", "cpu_speed", "cpu_type", "default_gateway", "disk_space",

    "model_id", "os_address_width", "os_domain", "os_service_pack", "ram",

    "u_owning_responsibility_unit", "u_billable", "u_patching_group_2", "*object_id", "u_role"

]

 

# Clean and compare

cleaned_outputs = [k.lstrip('*') for k in desired_outputs]

available_in_state = [k for k in cleaned_outputs if k in tf_out]

 

print("✅ Outputs available in Terraform state:")

for key in available_in_state:

    print(f"- {key}")

 

print("\n❌ Outputs missing from Terraform state:")

for key in cleaned_outputs:

    if key not in tf_out:

        print(f"- {key}")