# 14647 Host Healthcheck

A logic node for the GIRA HomeServer that checks a configured hosts for its health status. Depending on the configuration it can check via ping, tcp or http(s) connections. If the host has WakeOnLan enabled, you can trigger a wake command via an input. 

> **EARLY STAGES OF DEVELOPMENT**<br/>
> This software is in the early stages of development. Please use accordingly and provide feedback if you experience issues.

> **Independent Development & Non-Affiliation Disclaimer**<br/>
> This software is an independently developed integration. It is not affiliated with, endorsed by, or supported by Gira Giersiepen GmbH & Co. KG or Connectix or any of their affiliated companies. All referenced product and company names are trademarks of their respective owners and are used for identification purposes only.

## Features



## Table of Contents

## Installation

### Requirements

- Python 3.9.x (as installed on the HomeServer/FacilityServer itself)
- Package `requests`: `pip install requests`

### Setup


## Quick Start

### Basic Example

This is a basic example for building testcase 

```python
from hsl3.hsl3 import Hsl3Framework
from hsl3.hsl3_wrapper import Hsl3WrapperModule
from src.hsl3_14647_host_healthcheck import LogicModule

# Create HSL3 instance
hsl3fw = Hsl3Framework("14648_connectix_watermeter_gateway")
logic_module = LogicModule(hsl3fw)

# Create wrapper with configuration
wrapper_node = Hsl3WrapperModule("src/config_host-healthcheck.json", logic_module)

# Set input values
wrapper_node.set_input_value("IN01_HOST", "127.0.0.1")
wrapper_node.set_input_value("IN02_PORT", 453)
wrapper_node.set_input_value("IN03_BASEPATH", "")
wrapper_node.set_input_value("IN04_CHECK_INTERVAL", 60)
```

### Running the Example

```bash
python tests/test_14647_host_healthcheck.py
```

This loads the logic node and performs a call to the 

## Project Structure

```
hsl3/                               # Core HSL3 framework
src/                                # Logic node files
├── config_host-healthcheck.json    # Module configuration
├── hsl3_14647_host_healthcheck.py  # Generated logic module
├── 14647_host_healthcheck.hsl      # HSL3 source file
└── log14647.html                   # HTML information file
tests/                              # Test suite
└── test_14647_host_healthcheck.py  # Test and demo
README.md
LICENSE
```

## Configuration

The module is configured through `src/config_connectix-watermeter-gateway.json`.

### Inputs

| Identifier | Type | Default | Description |
|------------|------|---------|-------------|

### Outputs

| Identifier | Type | Description |
|------------|------|-------------|

## Testing


## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure:

- Code follows the existing structure and naming conventions
- JSON configurations are properly formatted and validated
- Tests pass before submitting pull requests
- New features include corresponding documentation

## Additional Resources

- [Gira HomeServer Documentation](https://www.gira.de/) (official Gira resources)
- [GiraHS HSL3 Development Framework](https://github.com/martinwelgraven/girahs-hsl3)

## Support

For issues or questions:

1. Check existing issues on the repository
2. Review configuration examples in `src/`
3. Run tests to isolate problems
4. Enable debug output using HSL3 debug sections