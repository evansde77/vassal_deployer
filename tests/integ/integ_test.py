#!/usr/bin/env python
"""
_integ_test_

"""
import os
import tempfile
import unittest
from virtualenvapi.manage import VirtualEnvironment

from vassal_deployer.deploy import deploy
from tests.integ.fixtures import update_and_write_fixtures, list_fixtures


class VassalIntegTest(unittest.TestCase):
    """
    Integration test to run the vassal config processor
    and render the nginx config.

    Note that this will build virtualenvs and pip install libraries
    into them
    """
    def setUp(self):
        """set up test structure"""
        self.dir = tempfile.mkdtemp()
        self.home = os.path.join(self.dir, 'home')
        self.templates = os.path.join(self.dir, 'templates')
        self.vassals = os.path.join(self.dir, 'vassals')
        self.sites_enabled = os.path.join(self.dir, 'sites-enabled')
        self.sites_available = os.path.join(self.dir, 'sites-available')
        os.makedirs(self.home)
        os.makedirs(self.templates)
        os.makedirs(self.vassals)
        os.makedirs(self.sites_enabled)
        os.makedirs(self.sites_available)

        update_and_write_fixtures(
            self.templates,
            home=self.home
            )

    def tearDown(self):
        """clean up test dirs"""
        if os.path.exists(self.dir):
            os.system('rm -rf {}'.format(self.dir))

    def test_deploy(self):
        """
        test end to end deploy call to create configs for fixtures
        and set up virtual envs
        """
        deploy(
            self.templates,
            self.vassals,
            'integ-test',
            8088,
            sites_available=self.sites_available,
            sites_enabled=self.sites_enabled
        )

        self.failUnless('sample_app_1' in os.listdir(self.home))
        self.failUnless('sample_app_2' in os.listdir(self.home))

        v1 = VirtualEnvironment(os.path.join(self.home, 'sample_app_1', 'venv'))
        v2 = VirtualEnvironment(os.path.join(self.home, 'sample_app_2', 'venv'))
        self.failUnless(v1.is_installed('requests'))
        self.failUnless(v2.is_installed('requests'))

        self.failUnless('sample_app_1.ini' in os.listdir(self.vassals))
        self.failUnless('sample_app_2.ini' in os.listdir(self.vassals))
        self.failUnless('integ-test.conf' in os.listdir(self.sites_available))
        self.failUnless('integ-test.conf' in os.listdir(self.sites_available))

if __name__ == '__main__':
    unittest.main()
