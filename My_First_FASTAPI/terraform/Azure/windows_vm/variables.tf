# # variable "vm_name" {}
# # variable "resource_group" {}
# # variable "location" {}
# # variable "admin_username" {}
# # variable "admin_password" {}
# # variable "vm_size" {
# #   # default = "Standard_DS1_v2"
# # }
# # variable "subscription_id" {}



# variable "subscription_id" { type = string }
# variable "vm_name" { type = string }
# variable "resource_group" { type = string }
# variable "location" { type = string }
# variable "admin_username" { type = string }
# variable "admin_password" { type = string }
# variable "vm_size" { type = string }
# variable "sctask_number" { type = string }


# variable "vm_name" {
#   description = "Name of the VM"
#   type        = string
# }

# variable "region" {
#   description = "Azure region for deployment"
#   type        = string
# }

# variable "vm_size" {
#   description = "Size of the VM"
#   type        = string
# }

# variable "admin_username" {
#   description = "Admin username for VM login"
#   type        = string
# }

# variable "admin_password" {
#   description = "Admin password for VM login"
#   type        = string
# }

# Azure subscription details (these will be set via environment vars in FastAPI, 
# so they do not need defaults unless you want to test manually)

# variable "subscription_id" {
#   description = "Azure subscription ID"
#   type        = string
# }

# variable "tenant_id" {
#   description = "Azure tenant ID"
#   type        = string
# }

# variable "client_id" {
#   description = "Azure client ID (Service Principal)"
#   type        = string
# }

# variable "client_secret" {
#   description = "Azure client secret (Service Principal)"
#   type        = string
#   sensitive   = true
# }

# # VM-specific configuration
# variable "vm_name" {
#   description = "Name of the Windows VM"
#   type        = string
# }

# variable "location" {
#   description = "Azure region to deploy the VM"
#   type        = string
# }

# variable "vm_size" {
#   description = "Size of the VM (e.g., Standard_B2ms)"
#   type        = string
# }

# variable "admin_username" {
#   description = "Admin username for the Windows VM"
#   type        = string
# }

# variable "admin_password" {
#   description = "Admin password for the Windows VM"
#   type        = string
#   sensitive   = true
# }


variable "subscription_id" {
  type = string
}
variable "tenant_id" { type = string }
variable "client_id" { type = string }
variable "client_secret" { type = string }

variable "location" {
  type = string
}

variable "vm_name" {
  type = string
}

variable "vm_size" {
  type = string
}

variable "admin_username" {
  type = string
}

variable "admin_password" {
  type = string
}
