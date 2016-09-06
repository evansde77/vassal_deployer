#!/usr/bin/env python
"""
deploy

"""
import os
from .vassal_config import VassalConfig
from .nginx_config import NginxSite
from . import logger


def list_vassals_configs(directory):
    """
    find all *.ini files in the given directory path

    :param directory: file system path containing *.ini files

    :returns: list of abs path ini files found
    """
    result = []
    for f in os.listdir(directory):
        if f.endswith('.ini'):
            result.append(
                os.path.join(directory, f)
            )
    return result


def make_vassals(directory):
    """
    Find the *.ini files in the given directory and wrap each
    one in a VassalConfig object

    :param directory: file system path containing *.ini files
    :returns: list of VassalConfig instances, one per found file

    """
    vassals = []
    for vc in list_vassals_configs(directory):
        logger.info('found vassal config: {}'.format(vc))
        vassals.append(VassalConfig(vc))
    return vassals


def deploy(
        templates_dir,
        vassals_dir,
        site_name,
        site_port,
        sites_available=None,
        sites_enabled=None):
    """
    _deploy_

    Main call to consume a directory containing the vassal templates,
    write the rendered vassal configs to the vassals_dir,
    set up the virtualenvs as needed and build the nginx site config

    :param templates_dir: file system path containing uwsgi *.ini files
    :param vassals_dir: file system path to write the vassal configs
        to for deployment
    :param site_name: nginx site name
    :param site_port: nginx port number
    :param sites_available: Path to nginx sites available dir
        (defaults to /etc/nginx/sites-available)
    :param sites_enabled: Path to nginx sites enabled dir
        (defaults to /etc/nginx/sites-enabled)

    """
    vassals = make_vassals(templates_dir)
    site = NginxSite(site_name, site_port, sites_available, sites_enabled)

    for vassal in vassals:
        vassal.load()
        vassal.make_virtualenv()
        vassal.pip_install()
        vassal.write(vassals_dir)
        site.add_vassal(vassal)

    site.write_available()
    site.link_enabled()
