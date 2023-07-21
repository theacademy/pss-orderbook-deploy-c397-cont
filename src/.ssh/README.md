The password for the provided SSH key is `wiley123`

Make your own key pair with `ssh-keygen -t ed25519 -C "your_email@example.com"`
Place the keys in this directory, and they will allow you to SSH into the container

To connect, simply use `ssh wiley@<EXTERNAL_IP> -i /path/to/id_ed25519`

where `<EXTERNAL_IP>` can be found in k8s dashboard under services for your namespace
