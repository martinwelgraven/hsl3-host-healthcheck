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
from hsl3_host_healthcheck.hsl3_14647_host_healthcheck import LogicModule

# Create HSL3 instance
hsl3fw = Hsl3Framework("14647_host_healthcheck")
logic_module = LogicModule(hsl3fw)

# Create wrapper with configuration
wrapper_node = Hsl3WrapperModule(
    "src/hsl3_host_healthcheck/config_host-healthcheck.json",
    logic_module,
)

# Set input values
wrapper_node.set_input_value("IN01_HOST_NAME", "127.0.0.1")
wrapper_node.set_input_value("IN02_HOST_PORT", 80)
wrapper_node.set_input_value("IN03_HOST_SSL", 1)
wrapper_node.set_input_value("IN04_HOST_PATH", "/")
```

## Project Structure

```
hsl3/                               # Core HSL3 framework
src/hsl3_host_healthcheck/              # Logic node package
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

The module is configured through `src/hsl3_host_healthcheck/config_host-healthcheck.json`.

### Inputs

| Identifier | Type | Default | Description |
|------------|------|---------|-------------|
| `IN01_HOST_NAME` | String | Empty | Hostname or IP address to check. |
| `IN02_HOST_PORT` | Number | `80` | Port number to check. |
| `IN03_HOST_SSL` | Number | `1` | Whether to use SSL for the health check (`1` = yes, `0` = no). |
| `IN04_HOST_PATH` | String | Empty | HTTP(S) path to request when checking whether the host is reachable. |
| `IN05_HEALTHCHECK_BENCHMARK` | String | Empty | Benchmark value for the HTTP(S) health check. |
| `IN06_MAC_ADDRESS` | String | Empty | MAC address of the host, used for Wake-on-LAN. |
| `IN07_HEALTHCHECK_FREQUENCY` | Number | `1` | Health-check frequency in seconds. |
| `IN08_TRIGGER_WOL` | Number | `1` | Whether to trigger Wake-on-LAN (`1` = yes, `0` = no). |

### Health-check behavior

Changing the host, port, SSL setting, path, or benchmark runs a check. The
module first requests the configured HTTP(S) path (or `/` when empty). A 2xx
response is online if the response body contains the benchmark text; an empty
benchmark accepts any 2xx response. HTTPS certificates are verified, redirects
are not followed, and HTTP proxies are not used.

Any HTTP response detects the host, even if its status or body fails the health
check. If there is no HTTP response, the module tries the configured TCP port,
system ping, and raw ICMP echo, in that order, stopping at the first successful
probe. Raw ICMP may require elevated privileges. If all probes fail, the host
is reported as not detected and offline; this does not prove it is powered off,
because firewalls or network errors can also block probes.

The frequency and Wake-on-LAN inputs are not yet implemented; checks are
currently triggered only by changes to the health-check inputs above.
Checks run synchronously in the logic node and can take several seconds when
probes time out.

### Outputs

| Identifier | Type | Default | Description |
|------------|------|---------|-------------|
| `IS_DETECTED` | Number | `0` | Whether the host is detected on the network (`1` = yes, `0` = no). |
| `IS_ONLINE` | Number | `0` | Whether the HTTP(S) health check succeeds (`1` = yes, `0` = no). |
| `ERROR_MESSAGE` | String | Empty | Reason the HTTP(S) health check failed, or empty after a successful check. |

`ERROR_MESSAGE` also reports an empty hostname or invalid configuration. A
successful fallback network probe does not clear an HTTP error: it indicates
reachability, not HTTP health. Non-ASCII characters in error messages are
escaped for compatibility with the HomeServer string output. An empty hostname
skips the check and leaves the previous detection and online outputs unchanged.

## Testing

Create a local environment file from the template and set the host and MAC
address used by the tests:

```bash
cp .env.example .env
```

Set `HOST_NAME` to the hostname or IP address of the test host and `MAC_ADDRESS`
to its Wake-on-LAN MAC address in `.env`. The local `.env` file is ignored by
Git; do not commit your device-specific values.

Run the full test suite with:

```bash
uv run --extra dev pytest tests/
```

Pytest discovers all test files in `tests/` that follow its naming conventions
(`test_*.py` or `*_test.py`). Run the command above after adding a test file so
the entire suite is executed. The current test can also be run on its own with:

```bash
./tests/test_14647_host_healthcheck.py
```

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