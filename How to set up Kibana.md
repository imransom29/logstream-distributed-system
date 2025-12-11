# Kibana Installation and Configuration Guide

This guide provides step-by-step instructions for installing and configuring Kibana on your system.

---

## Prerequisites
- Ensure you have `wget` and `apt-transport-https` installed on your system.
- Root or sudo permissions are required to execute these commands.

---

## Installation Steps

### 1. Add Kibana GPG Key
To ensure the authenticity of the Kibana packages, add the official GPG key:
```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
```

### 2. Install Prereqs
Ensure you have the required apt-transport-https package:
```bash
sudo apt-get install apt-transport-https
```

### 3. Add Kibana Repository
Add the official Kibana APT repository to your sources list:
```bash
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
```

### 4. Install Kibana
Update your system's package list and install Kibana:
```bash
sudo apt-get update && sudo apt-get install kibana
```

### 5. Enable Kibana as a Service
Reload the system daemon and enable Kibana to start on boot:
```bash
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable kibana.service
```

### 6. Start Kibana
Start Kibana:
```bash
sudo systemctl start kibana.service
```
Stop Kibana:
```bash
sudo systemctl stop kibana.service
``` 

### 7. Access Kibana Dashboard
To confirm Kibana is running successfully, visit the following URL in your browser:

[http://localhost:5601](http://localhost:5601)

The Kibana dashboard will be accessible if the service is running correctly.