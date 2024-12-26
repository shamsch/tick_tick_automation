variable "gmail" {
  description = "Gmail user email"
  type        = string
}

variable "gmail_app_password" {
  description = "Gmail app password"
  type        = string
  sensitive = true
}

variable "calender_link_1" {
  description = "Google calendar link"
  type        = string
}

variable "calender_link_2" {
  description = "Outlook calendar link"
  type        = string
}

variable "email" {
  description = "ticktick email address"
  type        = string
}
