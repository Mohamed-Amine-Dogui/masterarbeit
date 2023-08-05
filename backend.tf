terraform {
  backend "s3" {
    bucket         = "backend-terraform-master"
    key            = "statefile.tfstate"
    region         = "eu-west-1"
  }
}