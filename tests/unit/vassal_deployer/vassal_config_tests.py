#!/usr/bin/env python
"""
tests for vassal_config module
"""
import os
import unittest
import tempfile
import mock

from vassal_deployer.vassal_config import VassalConfig


FIXTURE1 = \
"""
[uwsgi]
home={home}/app1
socket=127.0.0.1:3030
module=some_package.some_module:APP
master=1
enable-threads=true
workers=2
die-on-term=1
virtualenv={home}/app1/venv

[vassaldeployer]
app_url=/app1
python=python2.7

"""

FIXTURE2 = \
"""
[uwsgi]
home={home}/app2
socket=127.0.0.1:3030
module=some_package.some_module:APP
master=1
enable-threads=true
workers=2
die-on-term=1
virtualenv={home}/app2/venv

[vassaldeployer]
app_url=/app2
python=python2.7
requirements=some_package=0.1.2.some_dep==1.2.3
pip_options= --extra-index=mypypi:8080
"""

FIXTURE3 = \
"""
[uwsgi]
home={home}/app3
socket=127.0.0.1:3030
module=some_package.some_module:APP
master=1
enable-threads=true
workers=2
die-on-term=1

[vassaldeployer]
app_url=/app3
requirements= pkg1==0.1.2,pkg2==1.2.3, pkg3==3.4.5

"""

class VassalConfigTests(unittest.TestCase):
    """tests for VassalConfig class"""
    def setUp(self):
        """set up fixtures"""
        self.dir = tempfile.mkdtemp()
        self.inputs = os.path.join(self.dir, 'in')
        self.outputs = os.path.join(self.dir, 'out')
        os.makedirs(self.inputs)
        os.makedirs(self.outputs)
        self.file1 = os.path.join(self.inputs, 'file1.ini')
        self.file2 = os.path.join(self.inputs, 'file2.ini')
        self.file3 = os.path.join(self.inputs, 'file3.ini')
        with open(self.file1, 'w') as handle:
            handle.write(FIXTURE1.format(home=self.outputs))
        with open(self.file2, 'w') as handle:
            handle.write(FIXTURE2.format(home=self.outputs))
        with open(self.file3, 'w') as handle:
            handle.write(FIXTURE3.format(home=self.outputs))

        self.patch_subp = mock.patch('vassal_deployer.vassal_config.subprocess.check_output')
        self.mock_subp = self.patch_subp.start()

    def tearDown(self):
        """clean up tempdir and stop patchers"""
        self.patch_subp.stop()
        if os.path.exists(self.dir):
            os.system('rm -rf {}'.format(self.dir))

    def test_fixture1(self):
        """test processing fixture 1"""
        vc = VassalConfig(self.file1)
        vc.load()
        vc.make_virtualenv()
        vc.pip_install()
        vc.write(self.outputs)

        self.assertEqual(vc.uwsgi_socket, '127.0.0.1:3030')
        self.assertEqual(vc.uwsgi_port, 3030)
        self.assertEqual(vc.uwsgi_home, os.path.join(self.outputs, 'app1'))
        self.assertEqual(vc.app_url, '/app1')
        nginx_conf = vc.nginx_config()
        self.failUnless(vc.app_url in nginx_conf)
        self.failUnless(vc.uwsgi_socket in nginx_conf)

        self.failUnless(self.mock_subp.called)
        self.assertEqual(self.mock_subp.call_count, 1)

        expected_venv = os.path.join(self.outputs, 'app1', 'venv')
        self.mock_subp.assert_has_calls([
            mock.call(['virtualenv', '-p', 'python2.7', expected_venv], stderr=-2)
        ])
        self.failUnless('file1.ini' in os.listdir(self.outputs))

    def test_fixture2(self):
        """test processing fixture2"""
        vc = VassalConfig(self.file2)
        vc.load()
        vc.make_virtualenv()
        vc.pip_install()
        vc.write(self.outputs)

        expected_venv = os.path.join(self.outputs, 'app2', 'venv')
        expected_activate = os.path.join(expected_venv, 'bin', 'activate')
        self.failUnless(self.mock_subp.called)
        self.assertEqual(self.mock_subp.call_count, 2)
        self.mock_subp.assert_any_call(
            ['virtualenv', '-p', 'python2.7', expected_venv], stderr=-2
            )
        cmd = self.mock_subp.call_args[0][0]
        self.failUnless(expected_activate in cmd)
        self.failUnless('pip install --extra-index=mypypi:8080' in cmd)
        self.failUnless('some_package=0.1.2.some_dep==1.2.3' in cmd)
        self.failUnless('file2.ini' in os.listdir(self.outputs))

    def test_fixture3(self):
        """test processing fixture3"""
        vc = VassalConfig(self.file3)
        vc.load()
        vc.make_virtualenv()
        vc.pip_install()
        vc.write(self.outputs)
        expected_venv = os.path.join(self.outputs, 'app3', 'venv')
        self.failUnless(self.mock_subp.called)
        self.assertEqual(self.mock_subp.call_count, 2)
        self.mock_subp.assert_any_call(
            ['virtualenv', '-p', 'python', expected_venv], stderr=-2
            )
        cmd = self.mock_subp.call_args[0][0]
        self.failUnless('pkg1==0.1.2' in cmd)
        self.failUnless('pkg2==1.2.3' in cmd)
        self.failUnless('pkg3==3.4.5' in cmd)


if __name__ == '__main__':
    unittest.main()
