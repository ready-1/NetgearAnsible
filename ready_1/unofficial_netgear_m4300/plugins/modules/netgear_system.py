#!/usr/bin/env python3
# Copyright (c) 2025, Unofficial Netgear M4300 Collection Maintainers
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

DOCUMENTATION = """
---
module: netgear_system
short_description: Configure Netgear M4300 switch system settings
description:
  - Configure system-level settings on Netgear M4300 series switches
  - Supports management IP configuration, SSH setup, user management, SNTP, SNMP
author: Unofficial Netgear M4300 Collection Maintainers
version_added: "1.0.0"
options:
  management_ip:
    description:
      - Configure the out-of-band management interface IP address
      - Format: ip_address/subnet_mask (e.g., "192.168.1.1/24")
    type: str
  management_gateway:
    description:
      - Default gateway for management interface
    type: str
  hostname:
    description:
      - Set the system hostname
    type: str
  enable_ssh:
    description:
      - Enable SSH service on the switch
    type: bool
    default: false
  ssh_port:
    description:
      - SSH service port (default 22)
    type: int
    default: 22
  generate_ssh_keys:
    description:
      - Generate new SSH host keys
    type: bool
    default: false
  users:
    description:
      - Configure local users
      - List of user dictionaries with 'name', 'password', 'privilege' keys
    type: list
    elements: dict
    suboptions:
      name:
        description: Username
        type: str
        required: true
      password:
        description: User password
        type: str
        required: true
      privilege:
        description: User privilege level (1-15)
        type: int
        default: 1
  sntp_server:
    description:
      - Configure SNTP server for time synchronization
    type: str
  snmp_community:
    description:
      - Configure SNMP community string for read-only access
    type: str
  snmp_location:
    description:
      - Set SNMP location string
    type: str
  snmp_contact:
    description:
      - Set SNMP contact information
    type: str
  state:
    description:
      - Whether the configuration should be present or absent
    type: str
    choices: [present, absent]
    default: present
requirements:
  - netmiko
"""

EXAMPLES = """
# Configure management IP
- name: Set management IP address
  ready_1.unofficial_netgear_m4300.netgear_system:
    management_ip: "192.168.1.10/24"
    management_gateway: "192.168.1.1"
    hostname: "switch01"

# Enable SSH with key generation
- name: Enable SSH service
  ready_1.unofficial_netgear_m4300.netgear_system:
    enable_ssh: true
    generate_ssh_keys: true

# Configure users
- name: Add local users
  ready_1.unofficial_netgear_m4300.netgear_system:
    users:
      - name: admin
        password: "securepass123"
        privilege: 15
      - name: operator
        password: "oppass456"
        privilege: 5

# Configure SNTP and SNMP
- name: Configure time and monitoring
  ready_1.unofficial_netgear_m4300.netgear_system:
    sntp_server: "192.168.1.100"
    snmp_community: "public"
    snmp_location: "Data Center Rack 1"
    snmp_contact: "admin@company.com"
"""

RETURN = """
commands:
  description: List of commands executed on the switch
  returned: always
  type: list
  sample: ["interface mgmt", "ip address 192.168.1.10/24", "exit"]
changed:
  description: Whether any changes were made
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ready_1.unofficial_netgear_m4300.plugins.module_utils.netgear import (
    run_commands,
    get_config,
    netgear_argument_spec
)


def configure_management_interface(module, commands):
    """Configure management interface IP"""
    mgmt_ip = module.params['management_ip']
    mgmt_gw = module.params['management_gateway']

    if mgmt_ip:
        commands.extend([
            "interface mgmt",
            f"ip address {mgmt_ip}",
        ])
        if mgmt_gw:
            commands.append(f"ip default-gateway {mgmt_gw}")
        commands.append("exit")


def configure_hostname(module, commands):
    """Configure system hostname"""
    hostname = module.params['hostname']
    if hostname:
        commands.append(f"hostname {hostname}")


def configure_ssh(module, commands):
    """Configure SSH service"""
    enable_ssh = module.params['enable_ssh']
    ssh_port = module.params['ssh_port']
    generate_keys = module.params['generate_ssh_keys']

    if enable_ssh:
        commands.extend([
            "ip ssh server enable",
            f"ip ssh port {ssh_port}"
        ])

        if generate_keys:
            commands.extend([
                "crypto key generate rsa",
                "crypto key generate dsa"
            ])


def configure_users(module, commands):
    """Configure local users"""
    users = module.params['users']
    if users:
        for user in users:
            name = user['name']
            password = user['password']
            privilege = user.get('privilege', 1)

            commands.extend([
                f"username {name} password {password}",
                f"username {name} privilege {privilege}"
            ])


def configure_sntp(module, commands):
    """Configure SNTP server"""
    sntp_server = module.params['sntp_server']
    if sntp_server:
        commands.extend([
            f"sntp server {sntp_server}",
            "sntp enable"
        ])


def configure_snmp(module, commands):
    """Configure SNMP settings"""
    community = module.params['snmp_community']
    location = module.params['snmp_location']
    contact = module.params['snmp_contact']

    if community:
        commands.append(f"snmp-server community {community} ro")

    if location:
        commands.append(f"snmp-server location \"{location}\"")

    if contact:
        commands.append(f"snmp-server contact \"{contact}\"")


def main():
    """Main module function"""
    argument_spec = netgear_argument_spec()
    argument_spec.update(
        management_ip=dict(type='str'),
        management_gateway=dict(type='str'),
        hostname=dict(type='str'),
        enable_ssh=dict(type='bool', default=False),
        ssh_port=dict(type='int', default=22),
        generate_ssh_keys=dict(type='bool', default=False),
        users=dict(type='list', elements='dict', options=dict(
            name=dict(type='str', required=True),
            password=dict(type='str', required=True),
            privilege=dict(type='int', default=1)
        )),
        sntp_server=dict(type='str'),
        snmp_community=dict(type='str'),
        snmp_location=dict(type='str'),
        snmp_contact=dict(type='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present')
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    # Build list of commands to execute
    commands = ["configure"]

    # Configure each feature
    configure_management_interface(module, commands)
    configure_hostname(module, commands)
    configure_ssh(module, commands)
    configure_users(module, commands)
    configure_sntp(module, commands)
    configure_snmp(module, commands)

    commands.append("end")
    commands.append("save config")

    # Remove the configure command if no other commands were added
    if len(commands) == 3:  # Just configure, end, save config
        commands = []

    # Execute commands
    if commands and not module.check_mode:
        try:
            run_commands(module, commands)
            changed = True
        except Exception as e:
            module.fail_json(msg=f"Failed to configure system: {e}")
    else:
        changed = False

    module.exit_json(
        changed=changed,
        commands=commands
    )


if __name__ == '__main__':
    main()
