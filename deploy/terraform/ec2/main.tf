terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of the existing SSH key pair"
  type        = string
}

variable "allowed_cidr" {
  description = "CIDR block allowed to access HTTP/SSH (e.g. your office IP)"
  type        = string
  default     = "0.0.0.0/0"
}

resource "aws_security_group" "offsec_sg" {
  name        = "offsec-program-sg"
  description = "Security group for OffSec Program MVP"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "offsec_ec2" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.offsec_sg.id]

  tags = {
    Name = "offsec-program-mvp"
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y python3 python3-venv python3-pip git nginx
              cd /opt
              git clone https://github.com/your-org/offsec_program_mvp.git
              cd offsec_program_mvp
              python3 -m venv venv
              source venv/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt
              cp deploy/nginx/offsec-program.conf /etc/nginx/sites-available/offsec-program
              ln -s /etc/nginx/sites-available/offsec-program /etc/nginx/sites-enabled/offsec-program
              rm /etc/nginx/sites-enabled/default
              systemctl restart nginx
              cp deploy/systemd/offsec-program.service /etc/systemd/system/offsec-program.service
              systemctl daemon-reload
              systemctl enable offsec-program
              systemctl start offsec-program
              EOF
}

output "public_ip" {
  description = "Public IP of the OffSec Program MVP instance"
  value       = aws_instance.offsec_ec2.public_ip
}
