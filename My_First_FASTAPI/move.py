import os
import shutil

TERRAFORM_DIR = r"D:\Study Materials\Python\FASTAPI\My_First_FASTAPI\terraform\AWS\windows_ec2"  # Path where your Terraform config is
STATE_ARCHIVE_DIR = r"D:\Study Materials\Python\FASTAPI\My_First_FASTAPI\terraform\AWS\windows_ec2\state_archieve"  # Path to store renamed tfstate files

instance_id = "i-037aa7f7131f238b8"#outputs.get("instance_id", {}).get("value")

if not instance_id:
    raise ValueError("Instance ID not found in Terraform outputs")

    # Rename and move the tfstate file
tfstate_path = os.path.join(TERRAFORM_DIR, "terraform.tfstate")
backup_path = os.path.join(TERRAFORM_DIR, "terraform.tfstate.backup")
new_tfstate_name = f"terraform_{instance_id}.tfstate"
new_backup_path = f"terraform_backup_{instance_id}.tfstate.backup"
new_tfstate_path = os.path.join(STATE_ARCHIVE_DIR, new_tfstate_name)
new_backup_path = os.path.join(STATE_ARCHIVE_DIR, new_backup_path)

shutil.move(tfstate_path, new_tfstate_path)
shutil.move(backup_path, new_backup_path)
print(f"Terraform state file moved to: {new_tfstate_path}")