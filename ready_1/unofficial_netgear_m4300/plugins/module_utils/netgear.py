#!/usr/bin/env python3
# Copyright (c) 2025, Unofficial Netgear M4300 Collection Maintainers
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Shared utilities for Netgear M4300 Ansible modules
"""

import re
from ansible.module_utils.basic import env_fallback


def netgear_argument_spec():
    """Return common argument spec for Netgear modules"""
    return dict(
        host=dict(type='str',
                  fallback=(env_fallback, ['ANSIBLE_NET_HOST']),
                  required=True),
        port=dict(type='int', default=23),
        username=dict(type='str',
                      fallback=(env_fallback, ['ANSIBLE_NET_USERNAME']),
                      required=True),
        password=dict(type='str', no_log=True,
                      fallback=(env_fallback, ['ANSIBLE_NET_PASSWORD']),
                      required=True),
        timeout=dict(type='int', default=30),
        provider=dict(type='dict', options=dict(
            host=dict(type='str'),
            port=dict(type='int', default=23),
            username=dict(type='str'),
            password=dict(type='str', no_log=True),
            timeout=dict(type='int', default=30),
        )),
    )


def run_commands(module, commands, check_rc=True):
    """Run commands on Netgear switch using netmiko"""
    if not commands:
        return []

    try:
        from netmiko import ConnectHandler
        from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
    except ImportError as e:
        module.fail_json(msg=f"netmiko is required: {e}")

    # Get connection parameters
    host = module.params.get('host')
    port = module.params.get('port', 23)
    username = module.params.get('username')
    password = module.params.get('password')
    timeout = module.params.get('timeout', 30)

    # Support provider dict for backward compatibility
    provider = module.params.get('provider')
    if provider:
        host = provider.get('host', host)
        port = provider.get('port', port)
        username = provider.get('username', username)
        password = provider.get('password', password)
        timeout = provider.get('timeout', timeout)

    # Establish connection
    device_params = {
        'device_type': 'cisco_ios_telnet',  # Netgear uses similar CLI
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'timeout': timeout,
        'session_timeout': timeout,
        'global_delay_factor': 1,
        'secret': password,  # Enable password if needed
    }

    try:
        connection = ConnectHandler(**device_params)

        results = []
        for cmd in commands:
            if cmd.strip():  # Skip empty commands
                module.debug(f"Executing command: {cmd}")
                output = connection.send_command(cmd)
                results.append({
                    'command': cmd,
                    'output': output
                })

        connection.disconnect()
        return results

    except NetMikoTimeoutException as e:
        module.fail_json(msg=f"Connection timeout to {host}:{port}: {e}")
    except NetMikoAuthenticationException as e:
        module.fail_json(msg=f"Authentication failed for {host}: {e}")
    except Exception as e:
        module.fail_json(msg=f"Failed to execute commands on {host}: {e}")


def get_config(module, config_type='running'):
    """Get configuration from Netgear switch"""
    commands = [f"show {config_type} config"]
    results = run_commands(module, commands)
    if results:
        return results[0]['output']
    return ""


def load_config(module, config):
    """Load configuration to Netgear switch"""
    commands = [
        "configure",
        config,
        "end",
        "save config"
    ]
    return run_commands(module, commands)


def parse_vlan_config(config_output):
    """Parse VLAN configuration from show vlan output"""
    vlans = {}
    vlan_pattern = r'(\d+)\s+(\w+)\s+(.+)'

    for line in config_output.split('\n'):
        match = re.search(vlan_pattern, line)
        if match:
            vlan_id, name, ports = match.groups()
            vlans[vlan_id] = {
                'name': name.strip(),
                'ports': [p.strip() for p in ports.split(',') if p.strip()]
            }

    return vlans


def parse_interface_config(config_output):
    """Parse interface configuration from show interface output"""
    interfaces = {}
    current_interface = None
    interface_pattern = r'^interface\s+(.+)$'

    for line in config_output.split('\n'):
        line = line.strip()
        if not line:
            continue

        interface_match = re.match(interface_pattern, line)
        if interface_match:
            current_interface = interface_match.group(1)
            interfaces[current_interface] = {}
        elif current_interface:
            # Parse interface configuration lines
            if line.startswith('description'):
                interfaces[current_interface]['description'] = line.split(' ', 1)[1]
            elif line.startswith('switchport mode'):
                interfaces[current_interface]['mode'] = line.split(' ', 2)[2]
            elif line.startswith('switchport access vlan'):
                interfaces[current_interface]['access_vlan'] = line.split(' ', 3)[3]
            elif line.startswith('switchport trunk allowed vlan'):
                vlans = line.split(' ', 4)[4]
                interfaces[current_interface]['trunk_vlans'] = vlans

    return interfaces


def parse_system_info(output):
    """Parse system information from show system output"""
    info = {}
    patterns = {
        'hostname': r'hostname\s+(.+)',
        'version': r'software version\s+(.+)',
        'serial': r'serial number\s+(.+)',
        'uptime': r'uptime\s+(.+)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            info[key] = match.group(1).strip()

    return info
