resource "aws_lambda_function" "calendar_lambda" {
  filename         = "lambda.zip"
  function_name    = "calendar_events_processor"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120
  source_code_hash = filebase64sha256("../main.py")

  environment {
    variables = {
      DYNAMO_TABLE_NAME = aws_dynamodb_table.calendar_events.name
      GMAIL_USER        = var.gmail
      GMAIL_PASSWORD    = var.gmail_app_password
      CALENDAR_LINK_1   = var.calender_link_1
      CALENDAR_LINK_2   = var.calender_link_2
      EMAIL_ADDRESS     = var.email
    }
  }

  depends_on = [
    null_resource.build_lambda,
  ]
}
