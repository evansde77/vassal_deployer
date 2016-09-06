#!/usr/bin/env python
"""
nginx_config

Wrapper to build an nginx site config from a set of
uwsgi vassal configurations

"""
import os
from . import logger


class NginxSite(object):

    """
    Helper to build the nginx config file for the
    uwsgi site containing the vassals.

    Instantiate with the site name and port and optional locations of
    the nginx sites available and sites enabled dirs.

    """

    def __init__(
            self,
            site_name,
            site_port,
            sites_available=None,
            sites_enabled=None):
        self.site_name = site_name
        self.site_port = site_port
        self.sites_available = sites_available or '/etc/nginx/sites-available'
        self.sites_enabled = sites_enabled or '/etc/nginx/sites-enabled'
        self._vassals = []
        self._conf_file = "{}.conf".format(site_name)

    @property
    def conf_header(self):
        """nginx config header with uwsgi params"""
        nginx_conf = (
            "server {{\n"
            "    listen {};\n"
            "    server_tokens off;\n"
            "    server_name {};\n\n"
        ).format(self.site_port, self.site_name)
        return nginx_conf

    @property
    def conf_footer(self):
        """config footer"""
        return "\n}\n"

    def add_vassal(self, vassal_conf):
        """
        add a uwsgi vassal to this config via a VassalConfig instance

        :param vassal_conf: Instance of VassalConfig to be included in the
           nginx config
        """
        self._vassals.append(vassal_conf)

    def configuration(self):
        """
        build the nginx configuration string
        """
        conf = "{}".format(self.conf_header)
        conf += "\n".join(v.nginx_config() for v in self._vassals)
        conf += self.conf_footer
        return conf

    def write_available(self):
        """
        write the nginx config to the sites available directory
        """
        avail_file = os.path.join(self.sites_available, self._conf_file)
        logger.info("writing sites available: {}".format(avail_file))
        with open(avail_file, 'w') as handle:
            handle.write(self.configuration())

    def link_enabled(self):
        """
        link the config file for the site from sites-available to sites-enabled
        """
        avail_file = os.path.join(self.sites_available, self._conf_file)
        enabled_file = os.path.join(self.sites_enabled, self._conf_file)
        logger.info("linking {} to {}".format(avail_file, enabled_file))
        os.system("ln -sf {} {}".format(avail_file, enabled_file))
