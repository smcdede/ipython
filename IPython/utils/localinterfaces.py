"""Simple utility for building a list of local IPs using the socket module.
This module defines two constants:

LOCALHOST : The loopback interface, or the first interface that points to this
            machine.  It will *almost* always be '127.0.0.1'

LOCAL_IPS : A list of IP addresses, loopback first, that point to this machine.

PUBLIC_IPS : A list of public IP addresses that point to this machine.
             Use these to tell remote clients where to find you.
"""
#-----------------------------------------------------------------------------
#  Copyright (C) 2010-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import socket

from .data import uniq_stable

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------

LOCAL_IPS = []
PUBLIC_IPS = []

LOCALHOST = '127.0.0.1'

def _only_once(f):
    """decorator to only run a function once"""
    f.called = False
    def wrapped():
        if f.called:
            return
        ret = f()
        f.called = True
        return ret
    return wrapped

def _requires_ips(f):
    """decorator to ensure load_ips has been run before f"""
    def ips_loaded(*args, **kwargs):
        _load_ips()
        return f(*args, **kwargs)
    return ips_loaded

@_only_once
def _load_ips():
    """load the IPs that point to this machine
    
    This function will only ever be called once.
    """
    global LOCALHOST
    try:
        LOCAL_IPS[:] = socket.gethostbyname_ex('localhost')[2]
    except socket.error:
        pass
    
    try:
        hostname = socket.gethostname()
        PUBLIC_IPS[:] = socket.gethostbyname_ex(hostname)[2]
        # try hostname.local, in case hostname has been short-circuited to loopback
        if not hostname.endswith('.local') and all(ip.startswith('127') for ip in PUBLIC_IPS):
            PUBLIC_IPS[:] = socket.gethostbyname_ex(socket.gethostname() + '.local')[2]
    except socket.error:
        pass
    finally:
        PUBLIC_IPS[:] = uniq_stable(PUBLIC_IPS)
        LOCAL_IPS.extend(PUBLIC_IPS)

    # include all-interface aliases: 0.0.0.0 and ''
    LOCAL_IPS.extend(['0.0.0.0', ''])

    LOCAL_IPS[:] = uniq_stable(LOCAL_IPS)

    LOCALHOST = LOCAL_IPS[0]

@_requires_ips
def local_ips():
    """return the IP addresses that point to this machine"""
    return LOCAL_IPS

@_requires_ips
def public_ips():
    """return the IP addresses for this machine that are visible to other machines"""
    return PUBLIC_IPS

@_requires_ips
def localhost():
    """return ip for localhost (almost always 127.0.0.1)"""
    return LOCALHOST

@_requires_ips
def is_local_ip(ip):
    """does `ip` point to this machine?"""
    return ip in LOCAL_IPS

@_requires_ips
def is_public_ip(ip):
    """is `ip` a publicly visible address?"""
    return ip in PUBLIC_IPS
