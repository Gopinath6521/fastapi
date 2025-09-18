
import os
import shutil
import json
import subprocess
from datetime import datetime
from app.models.snow_update import update_snow_ticket, close_snow_ticket, route_snow_ticket

def run_terraform(vars: dict):  # , snow_url, snow_user, snow_pass, sys_id
    # terraform_dir = r"D:\Study Materials\Python\FASTAPI\My_First_FASTAPI\terraform\Azure\windows_vm"
    # tfvars_path = os.path.join(terraform_dir, "terraform.tfvars.json")
    terraform_dir = os.environ.get("TERRAFORM_DIR", os.path.join(os.getcwd(), "terraform", "Azure", "windows_vm"))
    tfvars_path = os.path.join(terraform_dir, "terraform.tfvars.json")

    STATE_ARCHIVE_DIR = os.path.join(terraform_dir, "state_archieve")

    # ✅ Write tfvars file
    with open(tfvars_path, "w") as f:
        json.dump(vars, f, indent=2)

    # ✅ Initialize Terraform
    subprocess.run(["terraform", "init", "-upgrade"], cwd=terraform_dir, check=True)

    # ✅ Apply Terraform
    subprocess.run(
        ["terraform", "apply", "-auto-approve", f"-var-file={tfvars_path}"],
        cwd=terraform_dir,
        check=True
    )

    # ✅ Capture Terraform outputs in JSON format
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=terraform_dir,
        check=True,
        capture_output=True,
        text=True
    )
    
    try:
        outputs = json.loads(result.stdout)
        # return outputs
    
    except Exception as e:
        raise RuntimeError(f"Failed to parse Terraform outputs: {str(e)}")

    tfstate_path = os.path.join(terraform_dir, "terraform.tfstate")
    backup_path = os.path.join(terraform_dir, "terraform.tfstate.backup")

    # Use instance_name if available, else timestamp
    instance_id = vars.get("instance_name", datetime.now().strftime("%Y%m%d%H%M%S"))

    new_tfstate_path = os.path.join(STATE_ARCHIVE_DIR, f"terraform_{instance_id}.tfstate")
    new_backup_path = os.path.join(STATE_ARCHIVE_DIR, f"terraform_backup_{instance_id}.tfstate.backup")

    if os.path.exists(tfstate_path):
        shutil.move(tfstate_path, new_tfstate_path)
    if os.path.exists(backup_path):
        shutil.move(backup_path, new_backup_path)

    print(f"Terraform state files moved to: {STATE_ARCHIVE_DIR}")
    return outputs