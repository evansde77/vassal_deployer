# vassal_deployer

[![Build Status](https://travis-ci.org/evansde77/vassal_deployer.svg?branch=develop)](https://travis-ci.org/evansde77/vassal_deployer)

Util to deploy uwsgi vassals from templated configuration files and build an nginx config from them. Aimed at simplifying deployment of apps on docker containers

Given a set of uwsgi vassal ini files, you can add a set of extra controls in a [vassaldeployer] section that are interpreted and used to build virtual environments for each vassal, install requirements and build an nginx configuration file mapping each vassal to a URL stub. Primarily this is intended to be used as part of a container, so that you can, for example start up the container mounting a volume containing the vassal configuration templates and the startup script will pick them up, create the necessary environments and then link the nginx conf into the server running on the container. 


## Configuration Options 

In the vassaldeployer section you can specify the following fields:

* app_url - URL stub of the application on the nginx web server
* python - The python interpreter to use
* requirements - comma separated list of packages to install into the vassal's virtualenv 
* pip_options - extra verbatim options to pass to pip install (eg extra index etc) 

## Example

```ini
[uwsgi]
home=/opt/app
socket=127.0.0.1:3030
module=some_package.some_module:APP
master=1
enable-threads=true
workers=2
die-on-term=1
virtualenv=/opt/app/venv

[vassaldeployer]
app_url=/some_package
python=python2.7
requirements=some_package=0.1.2.some_dep==1.2.3
pip_options= --extra-index=mypypi:8080
```

In the above option, a uwsgi vassal is defined listening on 3030 with a basic python application handler and virtualenv. When vassal_deployer processes this config file, it will perform the following actions:

1. Build the virtualenv if not created 
2. Install the requirements via pip 
3. Render the vassal configuration (without the extra vassaldeployer section) 
4. Build an nginx site configuration that maps the uwsgi socket to an nginx site, with the URL /some_package on the nginx server proxying requests to the uwsgi vassal on the backend. 


## CLI Usage 

The tool comes with a CLI called vassal_deployer: 

```bash
vassal_deployer -h
usage: vassal_deployer [-h] --vassals VASSALS_OUT --input-vassals VASSALS_IN
                       [--sites-enabled SITES_ENABLED]
                       [--sites-available SITES_AVAILABLE]
                       [--nginx-port NGINX_PORT] [--nginx-site NGINX_SITE]

uwsgi vassal config processor that builds nginx confs

optional arguments:
  -h, --help            show this help message and exit
  --vassals VASSALS_OUT
                        directory to write vassals configs
  --input-vassals VASSALS_IN, -i VASSALS_IN
                        directory containing vassals configs with extra
                        deployer conf section
  --sites-enabled SITES_ENABLED
                        nginx sites-enabled directory location
  --sites-available SITES_AVAILABLE
                        nginx sites-available directory location
  --nginx-port NGINX_PORT
                        nginx server port number
  --nginx-site NGINX_SITE
                        nginx site name
```
