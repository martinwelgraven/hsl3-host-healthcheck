#!/usr/bin/env python3
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src" / "hsl3_host_healthcheck"

load_dotenv(ROOT_DIR / ".env")
HOSTNAME = os.getenv("HOSTNAME")
if HOSTNAME:
	HOSTNAME = HOSTNAME.encode()
MAC_ADDRESS = os.getenv("MAC_ADDRESS")
if MAC_ADDRESS:
	MAC_ADDRESS = MAC_ADDRESS.encode()
UDP_PORT = os.getenv("UDP_PORT")
TCP_PORT = os.getenv("TCP_PORT")

if not HOSTNAME or not MAC_ADDRESS or not UDP_PORT or not TCP_PORT:
	raise RuntimeError("Set HOSTNAME, MAC_ADDRESS, UDP_PORT, and TCP_PORT in .env (see .env.example).")

for path in (ROOT_DIR, SRC_DIR):
	if str(path) not in sys.path:
		sys.path.insert(0, str(path))

from hsl3.hsl3 import Hsl3Framework
from hsl3.hsl3_wrapper import Hsl3WrapperModule
from hsl3_host_healthcheck.hsl3_14647_host_healthcheck import LogicModule


MODULE = "hsl3_host_healthcheck.hsl3_14647_host_healthcheck"


def create_test_module():
	"""Create an initialized framework and wrapper for a health check test."""
	framework = Hsl3Framework("14647_host_healthcheck")
	logic_module = LogicModule(framework)

	config_file = ''
	if os.path.exists(SRC_DIR / "config_host_healthcheck.json"):
		config_file = SRC_DIR / "config_host_healthcheck.json"
	elif os.path.exists(SRC_DIR / "config_host_healthcheck.yaml"):
			config_file = SRC_DIR / "config_host_healthcheck.yaml"
	else:
		raise RuntimeError("No configuration file found for host health check.")

	wrapper = Hsl3WrapperModule(str(config_file), cast(Any, logic_module))
	framework.config = wrapper.config
	return framework, wrapper


class HealthHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		"""Serve a healthy response, an error, or a redirect based on the path."""
		if self.path == "/error":
			self.send_response(503)
			body = b"unavailable"
		elif self.path == "/redirect":
			self.send_response(302)
			self.send_header("Location", "/healthy")
			body = b""
		else:
			self.send_response(200)
			body = b"service ready"
		self.end_headers()
		self.wfile.write(body)

	def log_message(self, format, *args):
		"""Suppress the test HTTP server's request logs."""
		pass


class TestHostHealthcheck(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Start a local HTTP server shared by the test class."""

		cls.server = HTTPServer(("127.0.0.1", 0), HealthHandler)
		cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
		cls.thread.start()

	@classmethod
	def tearDownClass(cls):
		"""Stop the shared HTTP server and release its resources."""
		
		cls.server.shutdown()
		cls.thread.join()
		cls.server.server_close()

	def setUp(self):
		"""Create a fresh health check module and inputs for each test."""
		
		self.framework, self.wrapper = create_test_module()
		self.inputs = self.framework.inputs
		
	def outputs(self):
		"""Return the values set on the output of the host check logic node."""
		
		return (self.wrapper.get_output_value("OUT1_IS_ONLINE").value)

	def error(self):
		"""Return the value set on the error output of the host check logic node."""

		return self.wrapper.get_output_value("OUT4_ERROR_MESSAGE").value


	def test_udp_call_success(self):
		"""Test that a UDP call succeeds."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 7)
			
		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")

	def test_tcp_call_success(self):
		"""Test that a TCP call succeeds."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 0)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)

		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")

	def test_tcp_ssl_call_success(self):
		"""Test that a TCP call with SSL succeeds."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 0)
		self.wrapper.set_input_value("IN03_TCP_PORT", 443)
		self.wrapper.set_input_value("IN04_SSL", 1)

		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")

	def test_http_call_success(self):
		"""Test that an HTTP call succeeds."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 7)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN04_SSL", 0)
		self.wrapper.set_input_value("IN05_HOST_PATH", "/")
						
		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")
	
	def test_https_call_success(self):
		"""Test that an HTTPS call succeeds."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 7)
		self.wrapper.set_input_value("IN03_TCP_PORT", 443)
		self.wrapper.set_input_value("IN04_SSL", 1)
		self.wrapper.set_input_value("IN05_HOST_PATH", "/")
						
		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")

	def test_http_benchmark_call_success(self):
		"""Test that an HTTP call succeeds."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 7)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN04_SSL", 0)
		self.wrapper.set_input_value("IN05_HOST_PATH", "/")
		self.wrapper.set_input_value("IN07_BENCHMARK", 'FRITZ!Box')
						
		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")
	
	def test_https_benchmark_call_success(self):
		"""Test that an HTTPS call succeeds."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 7)
		self.wrapper.set_input_value("IN03_TCP_PORT", 443)
		self.wrapper.set_input_value("IN04_SSL", 1)
		self.wrapper.set_input_value("IN05_HOST_PATH", "/")
		self.wrapper.set_input_value("IN07_BENCHMARK", 'FRITZ!Box')
						
		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")


	def test_hostname_incorrect(self):
		"""Test that an incorrect hostname is detected."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN01_HOSTNAME", "".encode())
		self.wrapper.set_input_value("IN02_UDP_PORT", 7)
		self.wrapper.set_input_value("IN03_TCP_PORT", 443)
		self.wrapper.set_input_value("IN04_SSL", 0)

		self.assertEqual(self.outputs(), (0))
		self.assertEqual(self.error(), b"Invalid hostname")
	
	def test_udp_port_incorrect(self):
		"""Test that an incorrect UDP port is detected."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_UDP_PORT", 70000)

		self.assertEqual(self.outputs(), (0))
		self.assertEqual(self.error(), b"Invalid UDP port")

	def test_tcp_port_incorrect(self):
		"""Test that an incorrect TCP port is detected."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 70000)

		self.assertEqual(self.outputs(), (0))
		self.assertEqual(self.error(), b"Invalid TCP port")


	def test_ssl_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN04_SSL", 2)
		self.assertEqual(self.error(), b"Invalid SSL input")

	def test_path_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN05_HOST_PATH", "invalid")
		self.assertEqual(self.error(), b"Invalid HTTP path")

	def test_params_valid_json(self):
		with patch(f"{MODULE}.tcp_health_check", return_value={"available": True, "response_ms": 1}) as tcp:
			self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
			self.wrapper.set_input_value("IN01_HOSTNAME", "example.test")
			tcp.reset_mock()
			self.wrapper.set_input_value("IN06_PARAMS", '{"key1": 10, "key2": "value2"}')

			self.assertEqual(self.error(), b"")
			self.assertEqual(self.outputs(), 1)
			tcp.assert_called_once()

	def test_params_invalid_json(self):
		with patch(f"{MODULE}.tcp_health_check", return_value={"available": True, "response_ms": 1}) as tcp:
			self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)
			self.wrapper.set_input_value("IN01_HOSTNAME", "example.test")
			tcp.reset_mock()
			self.wrapper.set_input_value("IN06_PARAMS", '{"key1": }')

			self.assertEqual(self.error(), b"Invalid HTTP request parameters")
			self.assertEqual(self.outputs(), 0)
			tcp.assert_not_called()

	def test_mac_address_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN08_MAC_ADDRESS", "invalid")
		self.assertEqual(self.error(), b"Invalid MAC address format")

	def test_frequency_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", -1)
		self.assertEqual(self.error(), b"Invalid healthcheck frequency")
	
	def test_http_error(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN05_HOST_PATH", "/error")
		self.wrapper.set_input_value("IN07_BENCHMARK", "ready")

		self.assertEqual(self.outputs(), (0))
		self.assertEqual(self.error(), b"HTTP health check failed with status 404")


	def test_url_with_params_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN04_SSL", 0)
		self.wrapper.set_input_value("IN05_HOST_PATH", b"/")
		self.wrapper.set_input_value("IN06_PARAMS", b"")
		self.wrapper.set_input_value("IN07_BENCHMARK", b"FRITZ!!Box")
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)

		self.assertEqual(self.outputs(), (0))
		self.assertEqual(self.error(), b"Invalid HTTP request parameters")

	def test_url_with_params_single_quotes(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN04_SSL", 0)
		self.wrapper.set_input_value("IN05_HOST_PATH", b"/login_sid.lua")
		self.wrapper.set_input_value("IN06_PARAMS", b"{'username':'test'}")
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)

		self.assertEqual(self.outputs(), (0))
		self.assertEqual(self.error(), b"Invalid HTTP request parameters: use double quotes")

	def test_url_with_params_success(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN04_SSL", 0)
		self.wrapper.set_input_value("IN05_HOST_PATH", b"/login_sid.lua")
		self.wrapper.set_input_value("IN06_PARAMS", b'{"username":"test"}')
		self.wrapper.set_input_value("IN09_HEALTHCHECK_FREQUENCY", 0)

		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"")

	def test_wol_request(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN03_TCP_PORT", 80)
		self.wrapper.set_input_value("IN08_MAC_ADDRESS", MAC_ADDRESS)
		self.wrapper.set_input_value("IN10_TRIGGER_WOL", "1")
		
		self.assertEqual(self.outputs(), (1))
		self.assertEqual(self.error(), b"") 


if __name__ == "__main__":
	unittest.main(exit=False)
