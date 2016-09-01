#!/usr/bin/env python
"""
cli entry point for vassal deployer

"""
import argparse
from .deploy import deploy


def build_parser():
    """
    build command line parser

    """
    parser = argparse.ArgumentParser(
        description='uwsgi vassal config processor that builds nginx confs'
    )
    parser.add_argument(
        '--vassals',
        help='directory to write vassals configs',
        required=True,
        dest='vassals_out'
    )
    parser.add_argument(
        '--input-vassals', '-i',
        help='directory containing vassals configs with extra deployer conf section',
        required=True,
        dest='vassals_in'
    )
    parser.add_argument(
        '--sites-enabled',
        help='nginx sites-enabled directory location',
        default='/etc/nginx/sites-enabled',
        dest='sites_enabled'
    )
    parser.add_argument(
        '--sites-available',
        help='nginx sites-available directory location',
        default='/etc/nginx/sites-available',
        dest='sites_available'
    )
    parser.add_argument(
        '--nginx-port',
        help='nginx server port number',
        default=8080,
        dest='nginx_port'
        )
    parser.add_argument(
        '--nginx-site',
        help='nginx site name',
        default='uwsgi_vassals',
        dest='nginx_site'
        )

    opts = parser.parse_args()
    return opts


def main():
    """
    parse cli args and run deploy
    """
    opts = build_parser()
    deploy(
        opts.vassals_in,
        opts.vassals_out,
        opts.nginx_site,
        opts.nginx_port,
        opts.sites_available,
        opts.sites_enabled
        )

if __name__ == '__main__':  # pragma: no cover
    main()

