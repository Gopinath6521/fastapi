
import os
import shutil
import json
import subprocess
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket

def run_terraform_provision(snow_url, snow_user, snow_pass, sys_id, terraform_vars, aws_access_key, aws_secret_key):
    # TERRAFORM_DIR = r"D:\Study Materials\Python\FASTAPI\My_First_FASTAPI\terraform\AWS\windows_ec2"

    # TERRAFORM_DIR_AWS = os.environ.get("TERRAFORM_DIR_AWS", os.path.join(os.getcwd(), "terraform", "AWS", "windows_ec2"))
    # TERRAFORM_DIR_AWS = os.environ["TERRAFORM_DIR_AWS"]

    TERRAFORM_DIR_AWS = os.environ.get("TERRAFORM_DIR_AWS",os.path.join(os.getcwd(), "terraform", "AWS", "windows_ec2"))
    STATE_ARCHIVE_DIR = os.path.join(TERRAFORM_DIR_AWS, "state_archieve")

    # STATE_ARCHIVE_DIR = os.path.join(TERRAFORM_DIR_AWS, "state_archieve")
    # tfvars_path = os.path.join(terraform_dir, "terraform.tfvars.json")
    os.makedirs(STATE_ARCHIVE_DIR, exist_ok=True)

    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = aws_access_key
    env["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
    env["TF_VAR_region"] = terraform_vars.get("region")

    for key, value in terraform_vars.items():
        env[f"TF_VAR_{key}"] = str(value)
    
    update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, "Initiating Terraform.")

    # Terraform INIT
    init_process = subprocess.run(
        ["terraform", "init", "-upgrade"],
        cwd=TERRAFORM_DIR_AWS,
        env=env,
        capture_output=True,
        text=True
    )
    if init_process.returncode != 0:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed to initiate terraform. Error: {init_process.stderr}", 2, "Windows")
        raise RuntimeError(f"Terraform init failed: {init_process.stderr}")
    else:
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, "Terraform initiated Successfully.")

    # Terraform APPLY
    apply_process = subprocess.run(
        ["terraform", "apply", "-auto-approve"],
        cwd=TERRAFORM_DIR_AWS,
        env=env,
        capture_output=True,
        text=True
    )
    if apply_process.returncode != 0:
        route_snow_ticket(snow_url, snow_user, snow_pass, sys_id, f"Failed to apply terraform configurations. Error: {apply_process.stderr}", 2, "Windows")
        raise RuntimeError(f"Terraform apply failed: {apply_process.stderr}")
    else:
        update_snow_ticket(snow_url, snow_user, snow_pass, sys_id, "Terraform configurations applied Successfully.")

    # Get Terraform outputs in JSON
    output_process = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=TERRAFORM_DIR_AWS,
        env=env,
        capture_output=True,
        text=True
    )
    outputs = json.loads(output_process.stdout)

    instance_id = outputs.get("instance_id", {}).get("value")
    if not instance_id:
        raise ValueError("Instance ID not found in Terraform outputs")

    # Rename and move tfstate files
    tfstate_path = os.path.join(TERRAFORM_DIR_AWS, "terraform.tfstate")
    backup_path = os.path.join(TERRAFORM_DIR_AWS, "terraform.tfstate.backup")

    new_tfstate_path = os.path.join(STATE_ARCHIVE_DIR, f"terraform_{instance_id}.tfstate")
    new_backup_path = os.path.join(STATE_ARCHIVE_DIR, f"terraform_backup_{instance_id}.tfstate.backup")

    shutil.move(tfstate_path, new_tfstate_path)
    # shutil.move(backup_path, new_backup_path)

    print(f"Terraform state files moved to: {STATE_ARCHIVE_DIR}")
    return outputs
