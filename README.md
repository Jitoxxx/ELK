# Centralized-Logging by Joachim Hermans

This project involved Exabgp and ELK, It is used to collect logs (mainly syslog and bgp) to a centralized logging server and monitor it on one location. This project is tested on a Linux Ubuntu 16.04.4 LTS, with ELK being version 6.x and Exabgp Version 4.x

What is ELK and Exabgp?
ELK:
Elasticsearch the database. 
Logstash the logcollector and filter.
Kibana GUI to display logs.

Exabgp:
There is information about exabgp on the github: https://github.com/Exa-Networks/exabgp.
In this project Exabgp is used to collect bgp data from the Router Reflectors and send it to ELK.

The file structure:
the directories represent those of the ubuntu, example: "ELKExabgp/etc" goes into etc folder on your ubuntu. 

Installation instructions:
there is a file called "Installation Guide", this will give you a guide on how to install the whole project.

Issues:
There is an issue with the VPN-RR's that is not yet resolved.

Hope it works and you can contact me with issues if you find any.