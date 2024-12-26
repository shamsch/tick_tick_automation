## TickTick Automation

This is a simple automation I made for myself. I use (TickTick)[https://ticktick.com/webapp/] as my To-Do list of choice and I wanted to  sync events between my personal Google Calender, school Outlook calender, and TickTick. While you can acheive this without any code if you buy their premium subscription (which I recommend you do as it is a great app), I wanted to put my AWS free tier, Python scripting, and Infrastructure as Code (Terraform in this case) skills to the test. 

### How it works

The lambda function is triggered by a CloudWatch event every 15 minutes. It then gets the calender events from shareable ICS links from Google Calender and Outlook Calender. It then parses the ICal data, checks if the events were already sent to TickTick (for this, it uses DynamoDB), and if not, sends the event to TickTick. To send the event to TickTick, it uses TickTick's (email to task)[https://help.ticktick.com/articles/7055782422935240704] feature. It then uses SMTP server and a Gmail account for which you need the old (APP password)[https://support.google.com/accounts/answer/185833?hl=en] to send the email.

### If you want to use this

You will need to create a `terraform.tfvars` file in the `/terraform` directory with the following variables:

```hcl
gmail              = ""
gmail_app_password = ""
calender_link_1    = ""
calender_link_2    = ""
email              = ""
```

You then need to modify the `main.py` to your needs. Other than that, you can run `terraform apply` in the `/terraform` directory and you should be good to go as long you have the right credentials for Terraform to deploy the resources. 

