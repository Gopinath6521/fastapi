from pydantic import BaseModel

class AzureWindowsVMProvisionRequest(BaseModel):
    subscription_id: str
    vm_name: str
    resource_group: str  #= "testingDKRG"
    location: str
    admin_username: str
    admin_password: str
    vm_size: str #= "Standard_B1ms#"
    sctask_number: str

class AWSWindowsEC2ProvisionRequest(BaseModel):
    aws_account_name: str
    instance_type: str
    vm_name: str
    key_name: str
    region: str
    volume_size: int = 30
    sctask_number: str

class AWSWindowsEC2Decommission(BaseModel):
    aws_account_name: str
    region: str
    instance_id: str
    sctask_number: str

class AzureWindowsVMDecommission(BaseModel):
    subscription_id: str
    vm_name: str
    resource_group: str 
    sctask_number: str

class AzureStopVM(BaseModel):
    subscription_id: str
    vm_name: str
    resource_group: str  
    sctask_number: str

class AzureStartVM(BaseModel):
    subscription_id: str
    vm_name: str
    resource_group: str  
    sctask_number: str

class AWSWStopEC2(BaseModel):
    aws_account_name: str
    region: str
    instance_id: str
    sctask_number: str

class AWSWStartEC2(BaseModel):
    aws_account_name: str
    region: str
    instance_id: str
    sctask_number: str

class AWSWEC2Backup(BaseModel):
    aws_account_name: str
    region: str
    instance_id: str
    sctask_number: str
class AzureBackupVM(BaseModel):
    subscription_id: str
    vm_name: str
    resource_group: str  
    sctask_number: str
class AWSWEC2Resize(BaseModel):
    aws_account_name: str
    region: str
    instance_id: str
    sctask_number: str
    new_instance_type: str
class AzureVMResize(BaseModel):
    subscription_id: str
    vm_name: str
    resource_group: str  
    sctask_number: str
    new_size: str

class AWSS3Bucket(BaseModel):
    aws_account_name: str
    region: str
    bucket_name: str
    sctask_number: str
class AWSEBSProvision(BaseModel):
    aws_account_name: str
    region: str
    instance_id: str
    volume_size_in_gb: str
    sctask_number: str
    