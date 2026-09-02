output "public_ip"   { value = aws_eip.app.public_ip }
output "ssh_command" { value = "ssh ubuntu@${aws_eip.app.public_ip}" }
