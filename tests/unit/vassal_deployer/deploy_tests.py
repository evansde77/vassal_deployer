#!/usr/bin/env python
"""
deploy module tests

"""
import os
import mock
import tempfile
import unittest

from vassal_deployer.deploy import (
    deploy, list_vassals_configs, make_vassals
)


class DeployTests(unittest.TestCase):
    """tests for deploy module functions"""
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        for i in range(1, 4):
            with open(os.path.join(self.dir, 'vassal{0}.ini'.format(i)), 'w') as handle:
                handle.write('womp')


    def tearDown(self):
        """clean up tempdir and stop patchers"""
        if os.path.exists(self.dir):
            os.system('rm -rf {}'.format(self.dir))


    def test_list_vassals_configs(self):
        """test listing vassal configs"""
        confs = list_vassals_configs(self.dir)
        self.assertEqual(len(confs), 3)
        for c in confs:
            self.failUnless(c.endswith('.ini'))

    def test_make_vassals(self):
        """test make_vassals instances"""
        vassals = make_vassals(self.dir)
        self.assertEqual(len(vassals), 3)

    @mock.patch('vassal_deployer.deploy.VassalConfig')
    @mock.patch('vassal_deployer.deploy.NginxSite')
    def test_deploy(self, mock_site_cls, mock_vassal_cls):
        """test deploy function"""
        mock_site = mock.Mock()
        mock_site.add_vassal = mock.Mock()
        mock_site.write_available = mock.Mock()
        mock_site.link_enabled = mock.Mock()
        mock_site_cls.return_value = mock_site

        mock_vassal = mock.Mock()
        mock_vassal.load = mock.Mock()
        mock_vassal.make_virtualenv = mock.Mock()
        mock_vassal.pip_install = mock.Mock()
        mock_vassal.write = mock.Mock()
        mock_vassal_cls.return_value = mock_vassal

        deploy(
            self.dir,
            self.dir,
            'site-name',
            8080
        )
        self.assertEqual(mock_vassal.load.call_count, 3)
        self.assertEqual(mock_vassal.make_virtualenv.call_count, 3)
        self.assertEqual(mock_vassal.pip_install.call_count, 3)
        self.assertEqual(mock_vassal.write.call_count, 3)
        self.assertEqual(mock_site.add_vassal.call_count, 3)
        self.failUnless(mock_site.write_available.called)
        self.failUnless(mock_site.link_enabled.called)


if __name__ == '__main__':
    unittest.main()
