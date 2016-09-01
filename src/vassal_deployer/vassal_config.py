#!/usr/bin/env python
"""
vassal_config

Object that represents a uwsgi vassal configuration with some
extra fields that can be used to control setup for the application
including creation of a virtualenv and pip installing requirements

vassal configs containing an extra section called [vassaldeployer]
as well as the initial [uwsgi] config get processed and included
in a generated nginx config file that contains the site definition
for the multiple uwsgi vassal apps

Eg:

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

This script will create the virtualenv in the location specified,
install the requirements via pip and add a section to
the master nginx conf mapping /some_package to the uwsgi app
listening on the specified socket

"""
import os
import subprocess


try:
    import ConfigParser as configparser
except ImportError:
    import configparser


class VassalConfig(dict):
    """
    Representation of a uwsgi vassal config, taking a
    templated uwsgi vassal config with additional directives controlled
    by a vassaldeployer section
    """
    SECTION = 'vassaldeployer'

    def __init__(self, conf_file):
        self.config_file = conf_file
        self.basename = os.path.basename(self.config_file)

    def load(self):
        """
        read the ini file
        """
        self.parser = configparser.RawConfigParser()
        self.parser.read(self.config_file)
        for section in self.parser.sections():
            self.setdefault(section, {})
            for option in self.parser.options(section):
                self[section].setdefault(
                    option,
                    self.parser.get(section, option)
                )

    def uwsgi_config(self, **settings):
        """
        write the cleaned uwsgi config including
        additional settings
        """
        content = "[uwsgi]\n"
        values = dict(self['uwsgi'])
        values.update(settings)
        content += '\n'.join("{}={}".format(k, v) for k, v in values.iteritems())
        return content

    def nginx_config(self):
        """
        make the location section of the nginx conf

        routing the apps based off a subdomain of the nginx
        server requires the two extra params:
          SCRIPT_NAME tells nginx to strip the url
          uwsgi_modifier1 30 is the magic that makes it work
          see: http://blog.codepainters.com/2012/08/05/wsgi-deployment-under-a-subpath-using-uwsgi-and-nginx/
          for more details.

        """
        conf = "location {}".format(self.app_url)
        conf += "{\n"
        conf += "    include uwsgi_params;\n"
        conf += "    uwsgi_pass 127.0.0.1:{};\n".format(self.uwsgi_port)
        conf += "    uwsgi_param SCRIPT_NAME {};\n".format(self.app_url)
        conf += "    uwsgi_modifier1 30;\n"
        conf += "}\n"
        return conf

    @property
    def uwsgi_socket(self):
        """uwsgi socket location, linked to nginx"""
        return self['uwsgi']['socket']

    @property
    def uwsgi_home(self):
        """uwsgi home param"""
        return self['uwsgi']['home']

    @property
    def uwsgi_virtualenv(self):
        """virtualenv location"""
        if not self['uwsgi'].get('virtualenv'):
            venv = os.path.join(self.uwsgi_home, 'venv')
            self['uwsgi']['virtualenv'] = venv
        return self['uwsgi']['virtualenv']

    @property
    def uwsgi_port(self):
        """uwsgi port, linked to nginx"""
        return self.uwsgi_socket.split(':', 1)[1]

    @property
    def section(self):
        """get the template section"""
        return self[self.SECTION]

    @property
    def app_url(self):
        """app url setting"""
        return self.section.get('app_url')

    @property
    def app_python(self):
        """app python interpreter"""
        return self.section.get('python')

    @property
    def app_requirements(self):
        """app requirements to install"""
        return self.section.get('requirements')

    @property
    def pip_options(self):
        """extra options to pass to pip install"""
        return self.section.get('pip_options', '')

    def make_virtualenv(self):
        """
        execute the virtualenv command using the appropriate python
        """
        cmd = [
            "virtualenv", "-p",
            "{}".format(self.app_python),
            self.uwsgi_virtualenv
        ]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    def pip_install(self):
        """
        pip install the requirements list
        """
        reqs = ' '.join([
            x.strip()
            for x in self.app_requirements.split(',') if x.strip
            ]
        )
        if not reqs:
            # no reqs specified
            return
        cmd = (
            " . {}/bin/activate && "
            "pip install {} {}"
        ).format(self.uwsgi_virtualenv, self.pip_options, reqs)
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

    def write(self, dirname):
        """write config for vassal into the vassals dir"""
        f = os.path.join(dirname, self.basename)
        with open(f, 'w') as handle:
            handle.write(self.uwsgi_config())
