# pyOpenPortsChecker4Prometheus
## Use
The aim of this repo is to observe the open/closed status of your own router's ports. 
In my case, looks like that:

![image](https://user-images.githubusercontent.com/73612508/174436103-15c8042d-383e-45f5-8e05-3520fd0b3684.png)

Indeed, this is aimed to be consumed from a metrics application. I used <strong>Prometheus client</strong> in the code for later retrieve this output from Grafana.

## Structure  
The structure of this project is intended to have an easy Docker packaging. 

However, it can be used as standalone python script, but in this case you'll need to move the config folder to the same path of the script.

## Config
In the config file you'll can set:

- service_port: the port where the metrics will be exposed. For example [IP]:9116 (and also [IP]:9116/metrics)
- scrape_frequency: interval to scrap from canyouseeme, in seconds
- host_to_check: I only tested using DynamincDNS domain, idk if can work with your public IP or your "direct" domain
- ports_tocheck: list of the ports you're interested to observe

## How
It's using webscraping to canyouseeme.org, so please be consious of this must be used with common sense, specially with a long scrape interval (for example I've setted it to <strong>1h</strong>)  

That's all folks :)
