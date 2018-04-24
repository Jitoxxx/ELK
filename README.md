# ELK
# I'll post files in here, for how to setup your own ELK server used with rsyslog/syslogsystems
#Code by Joachim Hermans
#Code for installing ELK VERSION 6.X
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get -y update && sudo apt-get -y upgrade
sudo apt-get -y install oracle-java8-installer
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list

#Elasticsearch
sudo apt-get update && sudo apt-get install elasticsearch

#Kibana
sudo apt-get update && sudo apt-get install kibana

#Nginx
sudo apt-get -y install nginx
sudo -v

##### CHANGE KIBANAADMIN TO YOUR ADMIN NAME
echo "kibanaadmin:`openssl passwd -apr1`" | sudo tee -a /etc/nginx/htpasswd.users
#####
# /etc/nginx/sites-available/default THIS IS THE RIGHT DEFAULT FILE!
sudo nginx -t
sudo ufw allow 'Nginx full'

#Logstash
sudo apt-get update && sudo apt-get install logstash

#Generate ssl
sudo mkdir -p /etc/pki/tls/certs
sudo mkdir /etc/pki/tls/private
sudo vi /etc/ssl/openssl.conf
#add at the end
subjectAltName = IP: IPELKSERVER

#Change IP address in clean-elasticsearch.sh
#This will clean the last entry that passes 7 days everyday
sudo vi /etc/elasticsearch/clean-elasticsearch.sh
crontab -e
# go to the bottem and add: 59 23 * * * /etc/elasticsearch/clean-elasticsearh.sh

# START and Enable all services
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
sudo systemctl start kibana
sudo systemctl enable kibana
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl start logstash
sudo systemctl enable logstash

#Kibana Dashboards

cd ~
curl -L -O https://download.elastic.co/beats/dashboards/beats-dashboards-1.3.1.zip
sudo apt-get -y install unzip
unzip beats-dashboards-*.zip
cd beats-dashboards-*
./load.sh


########      after everything is done         ########
#go to the machines you want to log 
#give their syslog forwarder, the ip and port of the ELK Server
#Make sure you allow the ip's you given inside the proxy and firewall
#sudo ufw allow 514, 9200, given ip's...
