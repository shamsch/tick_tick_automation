## EXECUTION ROLE FOR LAMBDA

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

## These are the permissions that the Lambda function will have.

## POLICY DOCUMENTS

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
      "cloudwatch:PutMetricData",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

data "aws_iam_policy_document" "allowing_lambda_to_access_dynamodb" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:*"]
    resources = [aws_dynamodb_table.calendar_events.arn]
  }
}


## POLICIES 

resource "aws_iam_policy" "lambda_logging" {
  name   = "lambda_logging"
  policy = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_policy" "allowing_lambda_to_access_dynamodb" {
  name   = "allowing_lambda_to_access_dynamodb"
  policy = data.aws_iam_policy_document.allowing_lambda_to_access_dynamodb.json
}


## ATTACHING POLICIES TO THE ROLE

resource "aws_iam_role_policy_attachment" "attach_log" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "allowing_lambda_to_access_dynamodb" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.allowing_lambda_to_access_dynamodb.arn
}

