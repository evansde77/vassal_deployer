#!/usr/bin/env python
"""
nginx_config module tests
"""
import os
import mock
import tempfile
import unittest

from vassal_deployer.nginx_config import NginxSite


class NginxSiteTests(unittest.TestCase):
    """tests for NginxSite class"""
    def setUp(self):
        """set up temp dir"""
        self.dir = tempfile.mkdtemp()
        self.available = os.path.join(self.dir, 'sites-available')
        self.enabled = os.path.join(self.dir, 'sites-enabled')
        os.makedirs(self.available)
        os.makedirs(self.enabled)

    def tearDown(self):
        """clean up tempdir"""
        if os.path.exists(self.dir):
            os.system('rm -rf {}'.format(self.dir))

    def test_nginx_site(self):
        """test NginxSite config building"""
        mock_vassal = mock.Mock()
        mock_vassal.nginx_config = mock.Mock(return_value="{VASSAL1}")
        conf = NginxSite("site", 8080, self.available, self.enabled)
        for i in range(1, 4):
            mock_vassal = mock.Mock()
            mock_vassal.nginx_config = mock.Mock(return_value="VASSAL{}".format(i))
            conf.add_vassal(mock_vassal)
        conf_str = conf.configuration()
        self.failUnless('server_name site;' in conf_str)
        for i in range(1, 4):
            self.failUnless("VASSAL{}".format(i) in conf_str)

        conf.write_available()
        conf.link_enabled()
        self.failUnless('site.conf' in os.listdir(self.available))
        self.failUnless('site.conf' in os.listdir(self.enabled))


if __name__ == '__main__':
    unittest.main()
