# # # Get the latest Windows Server AMI from AWS SSM
# # data "aws_ssm_parameter" "latest_windows" {
# #   name = "/aws/service/ami-windows-latest/Windows_Server-2019-English-Full-Base"
# # }

# # resource "tls_private_key" "example" {
# #   algorithm = "RSA"
# #   rsa_bits  = 4096
# # }

# # resource "aws_key_pair" "example" {
# #   key_name   = var.key_name
# #   public_key = tls_private_key.example.public_key_openssh
# # }

# # output "private_key_pem" {
# #   value     = tls_private_key.example.private_key_pem
# #   sensitive = true
# # }

# # # Get the default VPC
# # data "aws_vpc" "default" {
# #   default = true
# # }

# # # Get all existing subnets in the default VPC
# # data "aws_subnets" "default_vpc_subnets" {
# #   filter {
# #     name   = "vpc-id"
# #     values = [data.aws_vpc.default.id]
# #   }
# # }

# # # Create a subnet inside default VPC using cidrsubnet()
# # # This example picks the 100th subnet slice in the /16 range (unlikely to conflict)
# # resource "aws_subnet" "new_subnet" {
# #   vpc_id            = data.aws_vpc.default.id
# #   cidr_block        = cidrsubnet(data.aws_vpc.default.cidr_block, 8, 100)
# #   availability_zone = "us-east-1a"

# #   tags = {
# #     Name = "my-new-subnet"
# #   }
# # }

# # output "default_vpc_cidr" {
# #   value = data.aws_vpc.default.cidr_block
# # }

# # # Create a new security group
# # resource "aws_security_group" "new_sg" {
# #   name        = "custom-sg"
# #   description = "Allow RDP inbound and all outbound"
# #   vpc_id      = data.aws_vpc.default.id

# #   ingress {
# #     description = "RDP"
# #     from_port   = 3389
# #     to_port     = 3389
# #     protocol    = "tcp"
# #     cidr_blocks = ["0.0.0.0/0"]
# #   }

# #   egress {
# #     from_port   = 0
# #     to_port     = 0
# #     protocol    = "-1"
# #     cidr_blocks = ["0.0.0.0/0"]
# #   }

# #   tags = {
# #     Name = "custom-sg"
# #   }
# # }

# # # Create EC2 instance
# # resource "aws_instance" "windows_ec2" {
# #   ami                    = data.aws_ssm_parameter.latest_windows.value
# #   instance_type          = var.instance_type
# #   key_name               = var.key_name
# #   subnet_id              = aws_subnet.new_subnet.id
# #   vpc_security_group_ids = [aws_security_group.new_sg.id]

# #   root_block_device {
# #     volume_size = var.volume_size
# #     volume_type = "gp3"
# #   }

# #     tags = {
# #     Name = var.vm_name
# #   }

# #   # tags = merge(
# #   #   {
# #   #     Name = "windows-ec2"
# #   #   },
# #   #   var.tags
# #   # )
# # }

# # # # Outputs
# # # output "instance_id" {
# # #   value = aws_instance.windows_ec2.id
# # # }

# # # output "public_ip" {
# # #   value = aws_instance.windows_ec2.public_ip
# # # }

# # # output "subnet_id" {
# # #   value = aws_subnet.new_subnet.id
# # # }

# # # output "security_group_id" {
# # #   value = aws_security_group.new_sg.id
# # # }



# # Get the latest Windows Server AMI from AWS SSM
# data "aws_ssm_parameter" "latest_windows" {
#   name = "/aws/service/ami-windows-latest/Windows_Server-2019-English-Full-Base"
# }

# resource "tls_private_key" "example" {
#   algorithm = "RSA"
#   rsa_bits  = 4096
# }

# resource "aws_key_pair" "example" {
#   key_name   = var.key_name
#   public_key = tls_private_key.example.public_key_openssh
# }

# output "private_key_pem" {
#   value     = tls_private_key.example.private_key_pem
#   sensitive = true
# }

# # Get the default VPC
# data "aws_vpc" "default" {
#   default = true
# }

# # Get all existing subnets in the default VPC
# data "aws_subnets" "default_vpc_subnets" {
#   filter {
#     name   = "vpc-id"
#     values = [data.aws_vpc.default.id]
#   }
# }

# # Fetch the default security group of the default VPC
# data "aws_security_group" "default" {
#   filter {
#     name   = "group-name"
#     values = ["default"]
#   }

#   vpc_id = data.aws_vpc.default.id
# }

# # Create a subnet inside default VPC using cidrsubnet()
# resource "aws_subnet" "new_subnet" {
#   vpc_id            = data.aws_vpc.default.id
#   cidr_block        = cidrsubnet(data.aws_vpc.default.cidr_block, 8, 100)
#   availability_zone = "us-east-1a"

#   tags = {
#     Name = "my-new-subnet"
#   }
# }

# output "default_vpc_cidr" {
#   value = data.aws_vpc.default.cidr_block
# }

# # Create EC2 instance using default security group
# resource "aws_instance" "windows_ec2" {
#   ami                    = data.aws_ssm_parameter.latest_windows.value
#   instance_type          = var.instance_type
#   key_name               = var.key_name
#   subnet_id              = aws_subnet.new_subnet.id
#   vpc_security_group_ids = [data.aws_security_group.default.id]

#   root_block_device {
#     volume_size = var.volume_size
#     volume_type = "gp3"
#   }

#   tags = {
#     Name = var.vm_name
#   }
# }

# # Outputs
# output "instance_id" {
#   value = aws_instance.windows_ec2.id
# }

# output "public_ip" {
#   value = aws_instance.windows_ec2.public_ip
# }

# output "subnet_id" {
#   value = aws_subnet.new_subnet.id
# }

# output "security_group_id" {
#   value = data.aws_security_group.default.id
# }


# Variables
# variable "key_name" {
#   description = "Name of the existing AWS key pair"
#   type        = string
# }

# variable "instance_type" {
#   description = "EC2 instance type"
#   type        = string
# }

# variable "volume_size" {
#   description = "Root volume size in GB"
#   type        = number
# }

# variable "vm_name" {
#   description = "Name of the VM"
#   type        = string
# }

# Get the latest Windows Server AMI from AWS SSM
# data "aws_ssm_parameter" "latest_windows" {
#   name = "/aws/service/ami-windows-latest/Windows_Server-2019-English-Full-Base"
# }

# # Get the default VPC
# data "aws_vpc" "default" {
#   default = true
# }

# # Get all existing subnets in the default VPC
# data "aws_subnets" "default_vpc_subnets" {
#   filter {
#     name   = "vpc-id"
#     values = [data.aws_vpc.default.id]
#   }
# }

# # Fetch the default security group of the default VPC
# data "aws_security_group" "default" {
#   filter {
#     name   = "group-name"
#     values = ["default"]
#   }
#   vpc_id = data.aws_vpc.default.id
# }

# # Create a new subnet inside default VPC (avoid conflicts by using random 3rd octet)
# resource "aws_subnet" "new_subnet" {
#   vpc_id            = data.aws_vpc.default.id
#   cidr_block        = cidrsubnet(data.aws_vpc.default.cidr_block, 8, 201)
#   availability_zone = "us-east-1a"

#   tags = {
#     Name = "my-new-subnet"
#   }
# }

# output "default_vpc_cidr" {
#   value = data.aws_vpc.default.cidr_block
# }

# # Create EC2 instance using existing key pair
# resource "aws_instance" "windows_ec2" {
#   ami                    = data.aws_ssm_parameter.latest_windows.value
#   instance_type          = var.instance_type
#   key_name               = var.key_name # Pass from FastAPI JSON
#   subnet_id              = aws_subnet.new_subnet.id
#   vpc_security_group_ids = [data.aws_security_group.default.id]

#   root_block_device {
#     volume_size = var.volume_size
#     volume_type = "gp3"
#   }

#   tags = {
#     Name = var.vm_name
#   }
# }

# # Outputs
# output "instance_id" {
#   value = aws_instance.windows_ec2.id
# }

# output "public_ip" {
#   value = aws_instance.windows_ec2.public_ip
# }

# output "subnet_id" {
#   value = aws_subnet.new_subnet.id
# }

# output "security_group_id" {
#   value = data.aws_security_group.default.id
# }

# variable "key_name" {
#   description = "Name of the existing AWS key pair"
#   type        = string
# }

# variable "instance_type" {
#   description = "EC2 instance type"
#   type        = string
# }

# variable "volume_size" {
#   description = "Root volume size in GB"
#   type        = number
# }

# variable "vm_name" {
#   description = "Name of the VM"
#   type        = string
# }

# Get latest Windows AMI
data "aws_ssm_parameter" "latest_windows" {
  name = "/aws/service/ami-windows-latest/Windows_Server-2019-English-Full-Base"
}

# Get the default VPC
data "aws_vpc" "default" {
  default = true
}

# Get an existing subnet in the default VPC
data "aws_subnets" "default_vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Fetch the default security group of the default VPC
data "aws_security_group" "default" {
  filter {
    name   = "group-name"
    values = ["default"]
  }
  vpc_id = data.aws_vpc.default.id
}

provider "aws" {
  region = var.region
}

resource "aws_iam_instance_profile" "ssm_profile" {
  name = "ec2-ssm-profile"
  role = "EC2-SSM-Role"
}

# Create EC2 instance in an existing subnet (NO public IP)
resource "aws_instance" "windows_ec2" {
  ami                    = data.aws_ssm_parameter.latest_windows.value
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = tolist(data.aws_subnets.default_vpc_subnets.ids)[0] # pick first existing subnet
  vpc_security_group_ids = [data.aws_security_group.default.id]

  associate_public_ip_address = false  # 🚫 prevent auto-assignment of public IP

  root_block_device {
    volume_size = var.volume_size
    volume_type = "gp3"
  }

  user_data = <<-EOF
    <powershell>
    $Username = "gopiuser"
    $Password = "MySecurePass@123" | ConvertTo-SecureString -AsPlainText -Force
    New-LocalUser -Name $Username -Password $Password -FullName "Gopi User" -Description "Custom login user"
    Add-LocalGroupMember -Group "Administrators" -Member $Username
    </powershell>
  EOF

  tags = {
    Name = var.vm_name
  }
}

# Outputs
output "instance_id" {
  value = aws_instance.windows_ec2.id
}

output "subnet_id" {
  value = aws_instance.windows_ec2.subnet_id
}

output "security_group_id" {
  value = data.aws_security_group.default.id
}
