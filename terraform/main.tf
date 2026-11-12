# Создаем свою VPC вместо поиска дефолтной
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "smart-home-vpc" }
}

# Создаем подсеть
resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-central-1a"
  tags = { Name = "smart-home-subnet" }
}

# Security Group
resource "aws_security_group" "server" {
  name        = "smart-home-server"
  description = "Smart Home EC2 access"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM Роль
resource "aws_iam_role" "server" {
  name = "smart-home-ec2"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# IAM Профиль
resource "aws_iam_instance_profile" "server" {
  name = "smart-home-ec2"
  role = aws_iam_role.server.name
}

# Сам EC2 инстанс (используем жестко заданный AMI)
resource "aws_instance" "server" {
  ami                         = "ami-0c55b159cbfafe1f0" 
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.main.id
  vpc_security_group_ids      = [aws_security_group.server.id]
  iam_instance_profile        = aws_iam_instance_profile.server.name

  tags = { Name = "SmartHome-Server" }
}