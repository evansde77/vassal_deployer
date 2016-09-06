#!/usr/bin/env python
"""
test fixtures for integ tests
"""
import os
import inspect


def find_this():
    pass


def fixtures_dir():
    return os.path.dirname(inspect.getsourcefile(find_this))


def list_fixtures():
    dirname = fixtures_dir()
    result = [
        os.path.join(dirname, i)
        for i in os.listdir(dirname) if i.endswith('.ini')
    ]
    return result

def update_and_write_fixtures(target_dir, **kwargs):
    for fix in list_fixtures():

        with open(fix, 'r') as in_handle:
            content = in_handle.read()

        new_content = content.format(**kwargs)
        target = os.path.join(target_dir, os.path.basename(fix))
        with open(target, 'w') as out_handle:
            out_handle.write(new_content)

