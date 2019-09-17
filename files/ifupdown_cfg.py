#!/usr/bin/python3

"""This script generates ansible custom fact for network config files.

Support ifupdown network subsystem
(Ubuntu up to Xenial and Debian distros).
"""

import os
import json


def iterate_configs(location='/etc/network'):
    for f_entry in os.scandir(location):
        if f_entry.is_dir():
            yield from iterate_configs(os.path.join(location, f_entry.name))
        if f_entry.is_file():
            yield os.path.join(location, f_entry.name)


def lines(text):
    accumulator = []
    for line in text:
        sline = line.strip()
        if sline.startswith('#'):
            continue
        if sline.endswith('\\'):
            accumulator.append(sline[:-1].strip())
            continue
        if sline == '':
            continue
        accumulator.append(sline)
        yield ' '.join(accumulator)
        accumulator = []


def enumerate_ifaces(text, proto):
    for line in lines(text):
        if line.startswith('iface'):
            chunks = line.split()
            if len(chunks) < 3:
                continue
            # iface eth0 inet static
            # iface ens3 inet dhcp
            if chunks[2] == 'inet':
                yield chunks[1]


def ifaces_from_file(filename, proto):
    with open(filename, 'r') as f:
        yield from enumerate_ifaces(f.readlines(), proto)


def all_iface_configs(location):
    iface_config_rel = {}
    for config in iterate_configs(location):
        for iface in ifaces_from_file(config, 'inet'):
            iface_config_rel[iface] = config
    return iface_config_rel


def gen_json(data):
    return json.dumps(data, indent=2)

if __name__ == '__main__':
    print(gen_json(all_iface_configs('/etc/network')))

### TESTS BELOW


def test_lines_normal():
    text = ['one', 'two']
    assert list(lines(text)) == text


def test_lines_stirp():
    text = [' one ', '', ' ' 'two']
    assert list(lines(text)) == ['one', 'two']


def test_lines_comments():
    text = [' one ', '#comment', ' #comment ', 'two']
    assert list(lines(text)) == ['one', 'two']


def test_lines_multiline():
    text = ['one\\', 'two', 'one \\', '   two']
    assert list(lines(text)) == ['one two', 'one two']


def test_enumerate_ifaces_normal():
    text = """
       auto eth0
       allow-hotplug eth1

       iface eth0 inet dhcp

       iface eth1 inet6 auto

       iface eth2 inet static
            address 192.168.1.2/24
            gateway 192.168.1.1

       iface eth3 inet6 static
            address fec0:0:0:1::2/64
            gateway fec0:0:0:1::1
    """.split('\n')
    assert list(enumerate_ifaces(text, 'inet')) == ['eth0', 'eth2' ]
