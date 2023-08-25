terraform {
  backend "s3" {
      bucket         = "backend-terraform-master"
      key            = "statefile.tfstate"
      region         = "eu-west-1"
  }

  required_providers {
    aws = {
      version = "= 4.19"
    }
    null = {
      source  = "hashicorp/null"
      version = "3.1.1"
    }

  }
}

provider "aws" {
  region = "eu-west-1"
}