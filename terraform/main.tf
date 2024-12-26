provider "aws" {
  region = "eu-west-1"
}

# Local build process for Lambda package
resource "null_resource" "build_lambda" {
  provisioner "local-exec" {
    command = <<EOT
      rm -f lambda.zip
      rm -rf package
      pip install -r ../requirements.txt --target ./package
      cd package
      zip -r ../lambda.zip .
      cd ..
      zip -g lambda.zip ../main.py
    EOT
  }

  triggers = {
    main_py_hash = "${filemd5("../main.py")}"
    requirements_hash = "${filemd5("../requirements.txt")}"
  }
}