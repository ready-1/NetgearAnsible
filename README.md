# NetgearAnsible

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Ansible collection for managing Netgear M4300 series managed switches.

## Overview

This project provides an unofficial Ansible collection (`ready_1.unofficial_netgear_m4300`) for automating the configuration and management of Netgear M4300 series switches. The collection supports Telnet connectivity initially, with planned expansion to SSH and REST API connections.

## Project Structure

```
├── ready_1/                          # Ansible collection namespace
│   └── unofficial_netgear_m4300/     # Collection name
│       ├── galaxy.yml               # Collection metadata
│       ├── plugins/
│       │   ├── connection/          # Connection plugins
│       │   │   └── netgear_telnet.py # Telnet connection
│       │   ├── modules/             # Ansible modules
│       │   │   └── netgear_system.py # System configuration
│       │   └── module_utils/        # Shared utilities
│       │       └── netgear.py       # Common functions
│       ├── docs/                   # Documentation
│       │   ├── artifacts_TCO.md    # Table of contents
│       │   ├── command_ref.jsonl   # Command reference
│       │   └── ...                 # CLI documentation
│       ├── roles/                  # Ansible roles
│       ├── playbooks/              # Example playbooks
│       ├── tests/                  # Unit/integration tests
│       └── README.md               # Collection documentation
├── python/                          # Python virtual environment
├── doc_processing/                  # Documentation processing scripts
└── README.md                        # This file
```

## Features

### Current Features

- **Telnet Connection Plugin**: Connect to switches via Telnet protocol using netmiko
- **System Configuration Module**: Configure management IP, SSH, users, SNTP, SNMP
- **Documentation**: Processed CLI command reference and manual

### Planned Features

- **SSH Connection Plugin**: Secure shell connectivity
- **REST API Connection Plugin**: Modern API-based management
- **VLAN Management Module**: Create and manage VLANs with IGMP configuration
- **Interface Configuration Module**: Configure ports and interfaces
- **Routing Configuration Module**: Set up static and dynamic routing
- **Roles and Playbooks**: Reusable roles for common switch configurations

## Quick Start

### Prerequisites

- Python 3.6+
- Ansible 2.9+

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ready-1/NetgearAnsible.git
   cd NetgearAnsible
   ```

2. **Activate virtual environment**:
   ```bash
   source python/bin/activate
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install ansible-core netmiko pytest ansible-lint
   ```

4. **Install the collection**:
   ```bash
   cd ready_1/unofficial_netgear_m4300
   ansible-galaxy collection install .
   ```

### Basic Usage

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
    - name: Configure management interface
      ready_1.unofficial_netgear_m4300.netgear_system:
        management_ip: "192.168.1.10/24"
        management_gateway: "192.168.1.1"
        hostname: "switch01"

    - name: Enable SSH and create users
      ready_1.unofficial_netgear_m4300.netgear_system:
        enable_ssh: true
        generate_ssh_keys: true
        users:
          - name: admin
            password: "securepass123"
            privilege: 15
```

## Development

### Setting up Development Environment

The virtual environment in `python/` contains all necessary dependencies. Simply activate it:

```bash
source python/bin/activate
```

### Running Tests

```bash
# Run Ansible linting
ansible-lint ready_1/unofficial_netgear_m4300/

# Run unit tests (when implemented)
pytest ready_1/unofficial_netgear_m4300/tests/
```

### Building Documentation

The `doc_processing/` directory contains scripts for processing Netgear CLI documentation:

```bash
cd doc_processing
python3 clean_commands.py    # Clean command data
python3 convert_to_jsonl.py  # Convert to JSONL format
```

## Documentation

- **Collection Documentation**: See `ready_1/unofficial_netgear_m4300/README.md`
- **CLI Reference**: Processed command documentation in `ready_1/unofficial_netgear_m4300/docs/`
- **API Documentation**: Generated from module docstrings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-module`)
3. Make your changes
4. Add tests for new functionality
5. Run linting: `ansible-lint`
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-module`)
8. Create a Pull Request

### Development Guidelines

- Follow Ansible collection best practices
- Include comprehensive documentation for all modules
- Add unit tests for new functionality
- Use `ansible-lint` for code quality checks
- Update documentation for any changes

## License

This project is licensed under the GPL-3.0-or-later License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an **unofficial** collection and is not affiliated with or supported by Netgear. It is provided as-is for educational and operational purposes. Use at your own risk and always test in a development environment before deploying to production.

## Roadmap

- [x] Project structure setup
- [x] Telnet connection plugin
- [x] System configuration module
- [ ] SSH connection plugin
- [ ] REST API connection plugin
- [ ] VLAN management module
- [ ] Interface configuration module
- [ ] Routing configuration module
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Published to Ansible Galaxy
