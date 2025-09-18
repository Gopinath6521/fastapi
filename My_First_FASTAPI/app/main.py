from fastapi import FastAPI
import requests
from requests.auth import HTTPBasicAuth
import json
from app.routes import ping, azure_windows_vm, get_keys, aws_windows_ec2, aws_windows_decommission, azure_windows_decommission, azure_stop_vm, azure_start_vm, aws_stop_ec2, aws_start_ec2, aws_ec2_backup, aws_resize, azure_resize, azure_vm_backup, s3bucket, ebs_provision

app = FastAPI()

# app.include_router(ping.router)
##### Azure Windows Provision/Decommission ####

app.include_router(azure_windows_vm.router, prefix="/Provision/Azure/windows-vm", tags=["Azure Windows Provision/Decommission"])
app.include_router(azure_windows_decommission.router, prefix="/Decommission/Azure/windows-vm", tags=["Azure Windows Provision/Decommission"])

##### AWS Windows Provision/Decommission ####

app.include_router(aws_windows_ec2.router, prefix="/Provision/AWS/windows-ec2", tags=["AWS Windows Provision/Decommission"])
app.include_router(aws_windows_decommission.router, prefix="/Decommission/AWS/windows-ec2", tags=["AWS Windows Provision/Decommission"])

#### Azure VM Operations ####

app.include_router(azure_stop_vm.router, prefix="/Stop/Azure", tags=["Azure VM Operations"])
app.include_router(azure_start_vm.router, prefix="/Start/Azure", tags=["Azure VM Operations"])
app.include_router(azure_vm_backup.router, prefix="/Backup/Azure", tags=["Azure VM Operations"])
app.include_router(azure_resize.router, prefix="/Resize/Azure", tags=["Azure VM Operations"])

#### AWS EC2 Operations ####

app.include_router(aws_stop_ec2.router, prefix="/Stop/AWS", tags=["AWS EC2 Operations"])
app.include_router(aws_start_ec2.router, prefix="/Start/AWS", tags=["AWS EC2 Operations"])
app.include_router(aws_ec2_backup.router, prefix="/Backup/AWS", tags=["AWS EC2 Operations"])
app.include_router(aws_resize.router, prefix="/Resize/AWS", tags=["AWS EC2 Operations"])

#### AWS Storage ####

app.include_router(s3bucket.router, prefix="/AWS/S3", tags=["AWS Storage"])
app.include_router(ebs_provision.router, prefix="/AWS/EBS", tags=["AWS Storage"])


# app.include_router(get_keys.router, prefix="/get-keys", tags=["get keys"])