#!/usr/bin/env python3
import os
import sys
import threading
import types
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

load_dotenv(ROOT_DIR / ".env")
HOSTNAME = os.getenv("HOSTNAME")
MAC_ADDRESS = os.getenv("MAC_ADDRESS")
if not HOSTNAME or not MAC_ADDRESS:
	raise RuntimeError("Set HOSTNAME and MAC_ADDRESS in .env (see .env.example).")

for path in (ROOT_DIR, SRC_DIR):
	if str(path) not in sys.path:
		sys.path.insert(0, str(path))

from hsl3.hsl3 import Hsl3Framework
from hsl3.hsl3_wrapper import Hsl3WrapperModule
from hsl3_host_healthcheck import hsl3_14647_ping
from hsl3_host_healthcheck.hsl3_14647_host_healthcheck import LogicModule


MODULE = "hsl3_host_healthcheck.hsl3_14647_host_healthcheck"


def create_test_module():
	"""Create an initialized framework and wrapper for a health check test."""
	framework = Hsl3Framework("14647_host_healthcheck")
	logic_module = LogicModule(framework)
	config_path = SRC_DIR / "hsl3_host_healthcheck" / "config_host-healthcheck.json"
	wrapper = Hsl3WrapperModule(str(config_path), cast(Any, logic_module))
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
		
		return (self.wrapper.get_output_value("IS_DETECTED").value, self.wrapper.get_output_value("IS_ONLINE").value)

	def error(self):
		"""Return the value set on the error output of the host check logic node."""

		return self.wrapper.get_output_value("ERROR_MESSAGE").value
	
	def test_standalone_module_import_and_script_order(self):
		"""Verify script ordering"""
		
		self.assertEqual(
			[script.filename for script in self.wrapper.config.scripts],
			["hsl3_14647_host_healthcheck.py","hsl3_14647_ping.py"],
		)
		module = types.ModuleType("hsl3_14647_host_healthcheck")
		source = SRC_DIR / "hsl3_host_healthcheck" / "hsl3_14647_host_healthcheck.py"
		with patch.dict(sys.modules, {"hsl3_14647_ping": hsl3_14647_ping}):
			exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
		self.assertIs(module.ping, hsl3_14647_ping.ping)
		
	
	def test_http_health_no_benchmark(self):
		"""Check that the configured host is detected without an error."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME.encode()) 
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN03_HOST_SSL", 0)
		self.wrapper.set_input_value("IN05_HEALTHCHECK_BENCHMARK", b"")
				
		self.assertIn(self.outputs(), [(1, 0), (1, 1)])
		self.assertEqual(self.error(), b"")

	def test_https_health_no_benchmark(self):
		"""Check that the configured host is detected without an error."""

		assert HOSTNAME is not None
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME.encode())
		self.wrapper.set_input_value("IN02_HOST_PORT", 443)
		self.wrapper.set_input_value("IN03_HOST_SSL", 1)
		self.wrapper.set_input_value("IN07_HEALTHCHECK_FREQUENCY", 0)
				
		self.assertIn(self.outputs(), [(1, 0), (1, 1)])
		self.assertEqual(self.error(), b"")

	def test_output_host_empty(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", "")
		self.assertEqual(self.outputs(), (0, 0))
		self.assertEqual(self.error(), b"Invalid hostname")

	def test_output_port_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 67000)
		
		self.assertEqual(self.outputs(), (0, 0))
		self.assertEqual(self.error(), b"Invalid port")

	def test_output_ssl_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN03_HOST_SSL", 2)
		self.assertEqual(self.error(), b"Invalid SSL input")

	def test_output_path_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN04_HOST_PATH", "invalid")
		self.assertEqual(self.error(), b"Invalid HTTP path")

	def test_output_mac_address_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN06_MAC_ADDRESS", "invalid")
		self.assertEqual(self.error(), b"Invalid MAC address format")

	def test_output_frequency_incorrect(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN07_HEALTHCHECK_FREQUENCY", -1)
		self.assertEqual(self.error(), b"Invalid healthcheck frequency")
	
	def test_output_http_error(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN04_HOST_PATH", "/error")
		self.wrapper.set_input_value("IN05_HEALTHCHECK_BENCHMARK", "ready")

		self.assertEqual(self.outputs(), (1, 0))
		self.assertEqual(self.error(), b"HTTP health check returned status 404")

	def test_benchmark_check(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN03_HOST_SSL", 0)
		self.wrapper.set_input_value("IN04_HOST_PATH", b"")
		self.wrapper.set_input_value("IN05_HEALTHCHECK_BENCHMARK", b"FRITZ!Box")
		self.wrapper.set_input_value("IN07_HEALTHCHECK_FREQUENCY", 0)
		
		self.assertEqual(self.outputs(), (1, 1))
		self.assertEqual(self.error(), b"")

	def test_benchmark_check_fails(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN03_HOST_SSL", 0)
		self.wrapper.set_input_value("IN04_HOST_PATH", b"")
		self.wrapper.set_input_value("IN05_HEALTHCHECK_BENCHMARK", b"FRITZ!!Box")
		self.wrapper.set_input_value("IN07_HEALTHCHECK_FREQUENCY", 0)

		self.assertEqual(self.outputs(), (1, 0))
		self.assertEqual(self.error(), b"HTTP health check benchmark was not found in the response")

	def test_wol_request(self):
		self.wrapper.set_input_value("IN01_HOSTNAME", HOSTNAME)
		self.wrapper.set_input_value("IN02_HOST_PORT", 80)
		self.wrapper.set_input_value("IN06_MAC_ADDRESS", MAC_ADDRESS)
		self.wrapper.set_input_value("IN08_TRIGGER_WOL", "1")
		
		self.assertEqual(self.error(), b"")



if __name__ == "__main__":
	unittest.main(exit=False)
