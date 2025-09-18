terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.9"  # match the version of state, e.g., 6.x
      # region = var.region
    }
  }
  required_version = ">= 1.3.0"
}



# variable "aws_access_key" {
#   description = "AWS Access Key"
#   type        = string
# }

# variable "aws_secret_key" {
#   description = "AWS Secret Key"
#   type        = string
# }

# provider "aws" {
#   access_key = var.aws_access_key
#   secret_key = var.aws_secret_key
# }
