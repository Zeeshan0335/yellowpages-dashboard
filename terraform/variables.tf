variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "yellowpages-dashboard"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "key_name" {
  type = string
}

variable "ssh_allowed_cidr" {
  type = string
}
