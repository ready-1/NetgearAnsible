#!/usr/bin/env python3
# Copyright (c) 2025, Unofficial Netgear M4300 Collection Maintainers
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

DOCUMENTATION = """
    name: netgear_telnet
    short_description: Connect to Netgear M4300 switches via Telnet
    description:
        - Connect to Netgear M4300 series switches using Telnet protocol
        - Uses netmiko library for device communication
    author: Unofficial Netgear M4300 Collection Maintainers
    version_added: "1.0.0"
    options:
      host:
        description:
          - Hostname or IP address of the Netgear switch
        required: true
        vars:
          - name: ansible_host
      port:
        description:
          - Telnet port to connect to
        default: 23
        vars:
          - name: ansible_port
      username:
        description:
          - Username for switch authentication
        vars:
          - name: ansible_user
      password:
        description:
          - Password for switch authentication
        vars:
          - name: ansible_password
      timeout:
        description:
          - Connection timeout in seconds
        default: 30
      persistent_connect_timeout:
        description:
          - Maximum time to wait for connection to be established
        default: 30
      persistent_command_timeout:
        description:
          - Maximum time to wait for command execution
        default: 30
"""

EXAMPLES = """
# Connect to a Netgear M4300 switch via Telnet
- name: Connect to switch
  connection: netgear_telnet
  hosts: switches
  vars:
    ansible_host: 192.168.1.1
    ansible_user: admin
    ansible_password: mypassword
"""

RETURN = """
# No return values
"""

import os
import time
import traceback

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.connection import ConnectionBase
from ansible.utils.display import Display

display = Display()

# Import netmiko at module level to avoid import issues
try:
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
    HAS_NETMIKO = True
except ImportError:
    ConnectHandler = None
    NetMikoTimeoutException = None
    NetMikoAuthenticationException = None
    HAS_NETMIKO = False


class Connection(ConnectionBase):
    """Netgear Telnet connection plugin"""

    transport = 'netgear_telnet'
    has_pipelining = False

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)
        self._connected = False
        self._connection = None

    def _connect(self):
        """Establish connection to the Netgear switch"""
        if self._connected:
            return

        if not HAS_NETMIKO:
            raise AnsibleConnectionFailure("netmiko is required for netgear_telnet connection plugin")

        host = self.get_option('host')
        port = self.get_option('port') or 23
        username = self.get_option('username')
        password = self.get_option('password')
        timeout = self.get_option('timeout') or 30

        display.vvv(f"Connecting to {host}:{port} via Telnet")

        try:
            # Netmiko device parameters for Netgear M4300
            device_params = {
                'device_type': 'cisco_ios_telnet',  # Netgear uses similar CLI to Cisco IOS
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'timeout': timeout,
                'session_timeout': timeout,
                'global_delay_factor': 1,
                'secret': password,  # Enable password if needed
            }

            self._connection = ConnectHandler(**device_params)
            self._connected = True
            display.vvv(f"Successfully connected to {host}")

        except NetMikoTimeoutException as e:
            raise AnsibleConnectionFailure(f"Connection timeout to {host}:{port}: {e}")
        except NetMikoAuthenticationException as e:
            raise AnsibleConnectionFailure(f"Authentication failed for {host}: {e}")
        except Exception as e:
            raise AnsibleConnectionFailure(f"Failed to connect to {host}: {e}")

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """Execute command on the switch"""
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        if in_data:
            raise AnsibleConnectionFailure("Internal error: exec_command with in_data not supported")

        self._connect()

        display.vvv(f"Executing command: {cmd}")

        try:
            # Send command and get output
            output = self._connection.send_command(cmd)

            # Convert to bytes as expected by Ansible
            return 0, to_bytes(output), b''

        except Exception as e:
            raise AnsibleConnectionFailure(f"Command execution failed: {e}")

    def put_file(self, in_path, out_path):
        """Transfer file to switch (not supported for Telnet)"""
        raise AnsibleConnectionFailure("File transfer not supported over Telnet connection")

    def fetch_file(self, in_path, out_path):
        """Fetch file from switch (not supported for Telnet)"""
        raise AnsibleConnectionFailure("File transfer not supported over Telnet connection")

    def close(self):
        """Close the connection"""
        if self._connection and self._connected:
            display.vvv("Closing Telnet connection")
            self._connection.disconnect()
            self._connected = False
            self._connection = None
