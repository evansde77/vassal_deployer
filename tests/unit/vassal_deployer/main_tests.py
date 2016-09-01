#!/usr/bin/env python
"""
tests for main module cli
"""
import sys
import unittest
import mock

from vassal_deployer.__main__ import build_parser, main


class MainTests(unittest.TestCase):
    """tests for main module and command line client"""

    def test_parser(self):
        with mock.patch.object(
            sys, 'argv', [
                'vassal_deployer',
                '--vassals', 'OUT',
                '--input-vassals', 'IN'
                ]):
            opts = build_parser()
            self.assertEqual(opts.vassals_in, 'IN')
            self.assertEqual(opts.vassals_out, 'OUT')

    @mock.patch('vassal_deployer.__main__.deploy')
    def test_main(self, mock_dep):
        """test coverage for main call"""
        with mock.patch.object(
            sys, 'argv', [
                'vassal_deployer',
                '--vassals', 'OUT',
                '--input-vassals', 'IN'
                ]):

            main()
            mock_dep.assert_has_calls([
                mock.call(
                    'IN',
                    'OUT',
                    'uwsgi_vassals',
                    8080,
                    '/etc/nginx/sites-available',
                    '/etc/nginx/sites-enabled'
                )
            ])


if __name__ == '__main__':
    unittest.main()
