#! /usr/bin/env python3
import argparse
import collections
import itertools
import multiprocessing
import operator
import socket

PURPOSE = 'Scan for open ports on a computer.'
PORTS = range(1 << 16)
POOL_SIZE = 1 << 8
TIMEOUT = 0.01


def main():
    """Get computer to scan, connect with process pool, and show open ports."""
    parser = argparse.ArgumentParser(description=PURPOSE)
    parser.add_argument('host', type=str, help='computer you want to scan')
    host = parser.parse_args().host
    with multiprocessing.Pool(POOL_SIZE, socket.setdefaulttimeout, [TIMEOUT]) \
            as pool:
        results = pool.imap_unordered(test, ((host, port) for port in PORTS))
        servers = filter(operator.itemgetter(0), results)
        numbers = map(operator.itemgetter(1), servers)
        ordered = sorted(numbers)
    print(f'Ports open on {host}:', *format_ports(ordered), sep='\n    ')


field_names = 'family', 'socket_type', 'protocol', 'canon_name', 'address'
AddressInfo = collections.namedtuple('AddressInfo', field_names)
del field_names


def test(address):
    """Try connecting to the server and return whether or not it succeeded."""
    host, port = address
    for info in itertools.starmap(AddressInfo, socket.getaddrinfo(host, port)):
        try:
            probe = socket.socket(info.family, info.socket_type, info.protocol)
        except OSError:
            pass
        else:
            try:
                probe.connect(info.address)
            except OSError:
                pass
            else:
                probe.shutdown(socket.SHUT_RDWR)
                return True, port
            finally:
                probe.close()
    return False, port


def format_ports(ports):
    """Convert port numbers into strings and show all associated services."""
    if ports:
        for port in ports:
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = '?'
            yield f'{port:<5} = {service}'
    else:
        yield 'None'


if __name__ == '__main__':
    main()