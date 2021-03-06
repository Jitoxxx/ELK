# Installation Guide on ELK and Exabgp
all the files that have been adjusted can also be found in this project.
 If you make changes to a file or if this guide tells you to, the changes are pointing towards the files in this project
 by Joachim Hermans

# Code for installing ELK VERSION 6.X
(adding repositories, updates, installing java8, adding GPG key, transport-https and sourcelist)
```

sudo add-apt-repository -y ppa:webupd8team/java

sudo apt-get -y update && sudo apt-get -y upgrade

sudo apt-get -y install oracle-java8-installer

wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

sudo apt-get install apt-transport-https

echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list
```

# Elasticsearch install
```
sudo apt-get update && sudo apt-get install elasticsearch
```
Change IPADDRESS in the following file
```
sudo vi /etc/elasticsearch/elasticsearch.yml
```
# Kibana install
```
sudo apt-get update && sudo apt-get install kibana
```
Change IPADDRESS in the following file
```
sudo vi /etc/kibana/kibana.yml
```
# Nginx install
```
sudo apt-get -y install nginx
sudo -v
```
# CHANGE KIBANAADMIN TO YOUR ADMIN NAME
```
echo "kibanaadmin:`openssl passwd -apr1`" | sudo tee -a /etc/nginx/htpasswd.users
```
change the IPADDRESS in the following file
/etc/nginx/sites-available/default
```
sudo nginx -t

sudo ufw allow 'Nginx full'
```

# Logstash install
```
sudo apt-get update && sudo apt-get install logstash
```
Change IPADDRESS in the following file
```
sudo vi /etc/logstash/conf.d/output.conf
```

change the disered ports in the following file
```
sudo vi /etc/logstash/conf.d/input.conf
```
# Generate ssl
```
sudo mkdir -p /etc/pki/tls/certs

sudo mkdir /etc/pki/tls/private

sudo vi /etc/ssl/openssl.conf
```

add at the end
```
subjectAltName = IP: IPELKSERVER
```
# Auto Clean
Change IP address in clean-elasticsearch.sh
This will clean the last entry that passes 7 days everyday (it) possible to change the "7")
```
sudo vi /etc/elasticsearch/clean-elasticsearch.sh
```
crontab -e
go to the bottem and add: 
```
59 23 * * * /etc/elasticsearch/clean-elasticsearh.sh
```
# START and Enable all services
```
sudo systemctl start elasticsearch

sudo systemctl enable elasticsearch

sudo systemctl start kibana

sudo systemctl enable kibana

sudo systemctl start nginx

sudo systemctl enable nginx

sudo systemctl start logstash

sudo systemctl enable logstash
```
# Kibana Dashboards
```
cd ~

curl -L -O https://download.elastic.co/beats/dashboards/beats-dashboards-1.3.1.zip

sudo apt-get -y install unzip

unzip beats-dashboards-*.zip

cd beats-dashboards-*

./load.sh
```
# Exabgp:

check python VERSION
```
python -V
```
if it displays 2.7.12 we are good
else install it
```
sudo apt-get install -y python-pip
```
# Install Exabgp
```
pip install exabgp
exabgp --help
python -m exabgp healthcheck --help
```
output should be :"healthchecker for exabgp."...

configuration are in this project and under the right directories.
For this to work you need to set the Ips, AS's and Router Reflectors into collector.cfg
```
vi /etc/exabgp/conf.d/collector.cfg
```
if you have issues with starting it up there can be execute permissions issues, make sure you have execution rights.
if the systemd file is set up ( from the files in this project )

```
sudo systemctl daemon-reload
sudo systemctl start exabgprun.service
sudo systemctl status exabgprun.service
```
output should be active

#Finishing touch

go to the machines you want to log 
give their syslog forwarder, the ip and port of the ELK Server
Make sure you allow the ports you given inside the proxy and firewall
sudo ufw allow "ports"...
