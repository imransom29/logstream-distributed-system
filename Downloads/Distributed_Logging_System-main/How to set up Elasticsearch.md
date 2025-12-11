# Elasticsearch Installation and Configuration Guide

Follow these steps to install and configure Elasticsearch on your system.

---

## **1. Add Elasticsearch GPG Key**
To ensure the authenticity of the Elasticsearch packages, add the GPG key:
```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
```

## **2. Install Prereqs**
Ensure you have the required apt-transport-https package:
```bash
sudo apt-get install apt-transport-https
```

## **3. Add Elasticsearch Repository**
Add the official Elasticsearch APT repository to your sources list:
```bash
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
```

## **4. Install Elasticsearch**
Update your system's package list and install Elasticsearch:
```bash
sudo apt-get update && sudo apt-get install elasticsearch
``` 
## **5. Enable Elasticsearch as a Service**
Reload the system daemon and enable Elasticsearch to start on boot:
```bash
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable elasticsearch.service
```

## **6. Start Elasticsearch**
Start Elasticsearch:
```bash
sudo systemctl start elasticsearch.service
```
Stop Elasticsearch:
```bash
sudo systemctl stop elasticsearch.service
```

## **7.Modify Elasticsearch Configuration**
o allow modifications to the elasticsearch.yml file, update its permissions:
```bash
cd /etc
sudo chmod 777 elasticsearch/
cd elasticsearch
sudo chmod 777 elasticsearch.yml
```

## **8. Open and edit the elasticsearch.yml file using a text editor (e.g., gedit):**
```bash
gedit elasticsearch.yml
```
Set the required property from true to false as needed.

## **9. Restart Elasticsearch**
Restart the Elasticsearch service:
```bash
sudo systemctl restart elasticsearch.service
```

## **10. Verify Elasticsearch Status**
Check if Elasticsearch is running successfully by accessing the following URL in your browser:

[http://localhost:9200](http://localhost:9200)

You should see a JSON response confirming that Elasticsearch is up and running.

## This completes the Elasticsearch setup and configuration process.