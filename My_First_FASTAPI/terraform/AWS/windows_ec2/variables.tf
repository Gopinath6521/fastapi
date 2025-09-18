# variable "region" {
#   description = "AWS region where EC2 will be created"
#   type        = string
# }


variable "region" {
  description = "AWS region where EC2 will be created"
  type        = string
}

variable "instance_type" {
  description = "Type of EC2 instance"
  type        = string
}

variable "key_name" {
  description = "Name of the existing EC2 Key Pair"
  type        = string
}

# variable "subnet_id" {
#   description = "Subnet ID for the instance"
#   type        = string
# }

# variable "security_group_ids" {
#   description = "List of Security Group IDs"
#   type        = list(string)
# }

variable "volume_size" {
  description = "Size of root volume in GB"
  type        = number
  default     = 30
}

variable "vm_name" {
  description = "Name tag for the EC2 instance"
}

# variable "aws_access_key" {}
# variable "aws_secret_key" {}

# provider "aws" {
#   region     = var.region
#   access_key = var.aws_access_key
#   secret_key = var.aws_secret_key
# }


# variable "tags" {
#   description = "Tags to apply to the instance"
#   type        = map(string)
#   default     = {}
# }
