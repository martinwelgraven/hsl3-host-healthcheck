# 14647 Host Healthcheck

A GIRA HomeServer logic node for checking whether a configured host is reachable
or its HTTP endpoint is healthy. It supports UDP and TCP probes, HTTP(S) checks,
periodic checks, and Wake-on-LAN.

> **Early stages of development**
>
> This software is in the early stages of development. Use it accordingly and
> provide feedback if you experience issues.

> **Independent development and non-affiliation disclaimer**
>
> This software is an independently developed integration. It is not affiliated
> with, endorsed by, or supported by Gira Giersiepen GmbH & Co. KG, Connectix,
> or their affiliated companies. Referenced product and company names are
> trademarks of their respective owners and are used for identification only.

## Features

- Check host reachability with a UDP probe followed by a TCP connection attempt.
- Check an HTTP(S) endpoint, optionally looking for a benchmark string in the
  response body.
- Run checks periodically using a configurable interval.
- Send a Wake-on-LAN packet when triggered.

## Table of Contents

- [Requirements and setup](#requirements-and-setup)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Health-check behavior and limitations](#health-check-behavior-and-limitations)
- [Testing](#testing)
- [Project structure](#project-structure)
- [License](#license)
- [Contributing](#contributing)
- [Additional resources](#additional-resources)
- [Support](#support)

## Requirements and setup

If you plan to work with this project, ensure you have the following prerequisites installed:
- Python 3.9 (the project metadata requires `>=3.9,<3.10`).
- The `requests` package for the logic module.
- The `pyyaml` package for parsing YAML configuration files.
- The `pytest` package for running tests.
- The `hsl3` Git submodule for local framework development.

Initialize the framework submodule with:

```bash
git submodule update --init --recursive
```

The current module configuration is
[`src/hsl3_host_healthcheck/config_host_healthcheck.yaml`](src/hsl3_host_healthcheck/config_host_healthcheck.yaml).
The repository also includes
[`src/hsl3_host_healthcheck/config_host_healthcheck.json.example`](src/hsl3_host_healthcheck/config_host_healthcheck.json.example)
as a JSON configuration example.

The generated HSL module is
[`src/hsl3_host_healthcheck/14647_host_healthcheck.hsl`](src/hsl3_host_healthcheck/14647_host_healthcheck.hsl).
The project's `pyproject.toml` does not define the previously documented
`uv run build-hsl` command; consult the HSL3 framework's build instructions
before regenerating module artifacts.

## Quick start

The following shows how the module is wired to the local HSL3 test wrapper. Set
`IN01_HOSTNAME` to a non-empty path to use an HTTP(S) check;

```python
from hsl3.hsl3 import Hsl3Framework
from hsl3.hsl3_wrapper import Hsl3WrapperModule
from hsl3_host_healthcheck.hsl3_14647_host_healthcheck import LogicModule

hsl3fw = Hsl3Framework("14647_host_healthcheck")
logic_module = LogicModule(hsl3fw)
wrapper_node = Hsl3WrapperModule(
    "src/hsl3_host_healthcheck/config_host_healthcheck.yaml",
    logic_module,
)
hsl3fw.config = wrapper_node.config

wrapper_node.set_input_value("IN01_HOSTNAME", "127.0.0.1")
wrapper_node.set_input_value("IN02_UDP_PORT", 7)
wrapper_node.set_input_value("IN03_TCP_PORT", 80)
wrapper_node.set_input_value("IN05_HOST_PATH", "/health")
wrapper_node.set_input_value("IN07_BENCHMARK", "ready")
```

## Configuration

The YAML file is the current module configuration. Inputs and defaults:

| Identifier | Type | Default | Description |
|---|---|---:|---|
| `IN01_HOSTNAME` | String | Empty | Hostname or IP address to check. |
| `IN02_UDP_PORT` | Number | `7` | UDP port to probe; `0` disables the UDP probe. |
| `IN03_TCP_PORT` | Number | `80` | TCP port to connect to; `0` disables the TCP probe. |
| `IN04_SSL` | Number | `0` | Use HTTPS instead of HTTP (`1` = yes, `0` = no). |
| `IN05_HOST_PATH` | String | Empty | HTTP(S) path. When empty, use UDP/TCP probes instead. |
| `IN06_PARAMS` | String | `{}` | HTTP request parameters, supplied as a JSON string. |
| `IN07_BENCHMARK` | String | Empty | Text that must appear in the HTTP response body. |
| `IN08_MAC_ADDRESS` | String | Empty | Target MAC address for Wake-on-LAN. |
| `IN09_HEALTHCHECK_FREQUENCY` | Number | `60` | Periodic check interval in seconds; `0` disables periodic checks. |
| `IN10_TRIGGER_WOL` | Number | `0` | A change to this input triggers Wake-on-LAN. |
| `IN11_ENABLE_LOGGING` | Number | `0` | Enable debug logging (`1` = yes, `0` = no). |

Outputs declared by the module configuration:

| Identifier | Type | Description |
|---|---|---|
| `OUT1_IS_ONLINE` | Number | `1` when the selected health check succeeds; otherwise `0`. |
| `OUT2_RESPONSE_TIME` | Number | Probe or HTTP response time in milliseconds. |
| `OUT3_HTTP_RESPONSE` | String | Intended to contain the HTTP response. The current logic code does not publish it: it uses a different identifier, which is also absent from its output map. |
| `OUT4_ERROR_MESSAGE` | String | Error for the most recent validation or HTTP check; empty when cleared. |

## Health-check behavior and limitations

- With an empty path, the module tries the configured UDP port first and then
  the configured TCP port if UDP does not succeed. A successful connection
  indicates reachability, not that an application is healthy.
- With a non-empty path, the module performs an HTTP GET. Only status `200` is
  considered successful. If a benchmark is configured, it must occur in the
  response body; otherwise any `200` response passes.
- The module uses the configured SSL input to choose HTTP or HTTPS. TLS
  certificate verification is disabled in the current implementation, and
  redirects are followed by the HTTP client.
- Checks run in the logic node. UDP and TCP probes have socket timeouts, but
  the HTTP request currently has no timeout configured and may block longer
  than expected.
- A failed HTTP check does not fall back to UDP or TCP. The frequency input
  schedules repeated checks when greater than zero.
- Wake-on-LAN requires a valid MAC address and a network that permits the
  broadcast packet to reach the target.

## Testing

Create a local environment file from the template:

```bash
cp .env.example .env
```

Set `HOSTNAME` to the hostname or IP address of the test host, `MAC_ADDRESS` to
its Wake-on-LAN MAC address, and provide `UDP_PORT` and `TCP_PORT` values. The
test module requires all four variables to be present in `.env`; individual
test cases configure their own probe ports. The local `.env` file is ignored
by Git; do not commit device-specific values.

Install the development dependencies and run the test suite with:

```bash
uv sync --extra dev
uv run --extra dev pytest tests/
```

The tests include network-dependent checks against the configured host as well
as a local HTTP test server. Ensure the configured host and network are
available before running them.

## Project structure

```text
hsl3/                                        # HSL3 framework Git submodule
src/hsl3_host_healthcheck/
├── 14647_host_healthcheck.hsl               # HSL module artifact
├── config_host_healthcheck.yaml             # Current module configuration
├── config_host_healthcheck.json.example     # JSON configuration example
├── hsl3_14647_host_healthcheck.py           # Logic module
├── hsl3_14647_ping.py                       # UDP, TCP, and Wake-on-LAN helpers
└── log14647.html                            # Module information page
tests/
└── test_14647_host_healthcheck.py
```

## License

This project is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0). See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome. Please ensure:

- Code follows the existing structure and naming conventions.
- JSON and YAML configurations are properly formatted and validated.
- Tests pass before submitting pull requests.
- New features include corresponding documentation.

## Additional resources

- [Gira HomeServer resources](https://www.gira.de/)
- [GiraHS HSL3 Development Framework](https://github.com/martinwelgraven/girahs-hsl3)

## Support

For issues or questions:

1. Check existing issues on the repository.
2. Review configuration examples in `src/`.
3. Run tests to isolate problems.
4. Enable debug output using the HSL3 debug sections.
