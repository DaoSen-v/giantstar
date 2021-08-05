"""
Gives information about the current operating system.
"""
import sys
import socket


def is_windows():
    return sys.platform in ('win32', 'cygwin')


def is_mac():
    return sys.platform == 'darwin'


def is_linux():
    return sys.platform.startswith('linux')


def get_canonical_os_name():
    if is_windows():
        return 'windows'
    elif is_mac():
        return 'mac'
    elif is_linux():
        return 'linux'


def acquire_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip


def acquire_port():
    sock = socket.socket()
    sock.bind(('', 0))
    ip, port = sock.getsockname()
    sock.close()
    return port
