# Ansible Collection - ready_1.unofficial_netgear_m4300

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Unofficial Ansible collection for managing Netgear M4300 series managed switches.

## Description

This collection provides Ansible modules and connection plugins for automating configuration and management of Netgear M4300 series switches. It supports Telnet connectivity initially, with planned expansion to SSH and REST API connections.

## Features

- **Telnet Connection Plugin**: Connect to switches via Telnet protocol
- **System Configuration Module**: Configure management IP, SSH, users, SNTP, SNMP
- **VLAN Management Module**: Create and manage VLANs with IGMP configuration (planned)
- **Interface Configuration Module**: Configure ports and interfaces (planned)
- **Routing Configuration Module**: Set up static and dynamic routing (planned)

## Requirements

- Python 3.6+
- `netmiko` library
- Ansible 2.9+

## Installation

### Install from GitHub

```bash
ansible-galaxy collection install git+https://github.com/ready-1/NetgearAnsible.git#/ready_1/unofficial_netgear_m4300
```

### Install locally for development

```bash
cd ready_1/unofficial_netgear_m4300
ansible-galaxy collection install .
```

## Usage

### Basic Connection

```yaml
---
- name: Configure Netgear M4300 switch
  hosts: switches
  connection: ready_1.unofficial_netgear_m4300.netgear_telnet
  vars:
    ansible_host: 192.168.1.10
    ansible_user: admin
    ansible_password: mypassword

  tasks:
    - name: Set management IP
      ready_1.unofficial_netgear_m4300.netgear_system:
        management_ip: "192.168.1.10/24"
        management_gateway: "192.168.1.1"
        hostname: "switch01"
```

### System Configuration

```yaml
- name: Configure system settings
  ready_1.unofficial_netgear_m4300.netgear_system:
    hostname: "core-switch"
    enable_ssh: true
    generate_ssh_keys: true
    users:
      - name: admin
        password: "securepass123"
        privilege: 15
      - name: operator
        password: "oppass456"
        privilege: 5
    sntp_server: "192.168.1.100"
    snmp_community: "public"
    snmp_location: "Data Center Rack 1"
```

## Modules

### Connection Plugins

- `netgear_telnet`: Connect via Telnet (default port 23)

### Modules

- `netgear_system`: System-level configuration (management IP, SSH, users, SNTP, SNMP)

## Development

### Setting up Development Environment

1. Clone the repository
2. Create/activate Python virtual environment
3. Install dependencies:

```bash
pip install ansible-core netmiko pytest ansible-lint
```

4. Install collection in development mode:

```bash
ansible-galaxy collection install -p ./ ~/.ansible/collections/
```

### Running Tests

```bash
# Run Ansible lint
ansible-lint

# Run unit tests
pytest tests/unit/
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- `artifacts_TCO.md`: Table of contents for documentation artifacts
- `command_ref.jsonl`: JSON Lines format command reference
- `M4300_CLI_EN_chunks.jsonl`: CLI manual in chunks
- `M4300_CLI_EN.txt`: Full CLI manual text
- `M4300_Switch_CLI_Exercise.md`: CLI exercise learnings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

GPL-3.0-or-later

## Disclaimer

This is an unofficial collection and is not affiliated with or supported by Netgear. Use at your own risk.
