import json
import time

import requests
import logging
import re

if __package__:
	from .hsl3_14647_ping import  udp_packet_ping, tcp_health_check,  wake_on_lan # type: ignore
else:
	from hsl3_14647_ping import  udp_packet_ping, tcp_health_check, wake_on_lan # type: ignore


HOSTNAME_REGEX = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r")(?:\."
    r"[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r")*$"
)


class LogicModule:

	def __init__(self, hsl3):
		self.fw = hsl3
		self.debug = self.fw.create_debug_section()
		self.logger = self.fw.get_logger(level=logging.ERROR)	

		self.initialized = False
		self.client = {
			'host': '',
			'port': 0,
			'udp_port': 7,
			'path': '',
			'params': '',
			'ssl': False,
			'benchmark': '',
			'mac_address': '',
			'healthcheck_frequency': 0,
			'trigger_wol': False
		}

		self.do_log = False
		self.error = None

		# For local reuse of output values
		self.outputs = {			
			'OUT1_IS_ONLINE': { 'value': 0, 'sbc': 's', 'index': 2 },
			'OUT2_RESPONSE_TIME': { 'value': 0.0, 'sbc': 's', 'index': 2 },
			'OUT4_ERROR_MESSAGE': { 'value': b'', 'sbc': 's', 'index': 3 }
		}


	def on_init(self, inputs, store):
		"""
		Initialize the module with input connections and store information
		Args:
			inputs: Hsl3Slots object containing input slot definitions
			store: Hsl3Slots object containing the storage object for maintaining state (for this node unused)
		"""

		self.client['host'] = self.text('IN01_HOSTNAME', inputs)
		self.client['udp_port'] = inputs.value('IN02_UDP_PORT')
		self.client['port'] = inputs.value('IN03_TCP_PORT')
		self.client['ssl'] = inputs.value('IN04_SSL')
		self.client['path'] = self.text('IN05_HOST_PATH', inputs)
		self.client['params'] = self.text('IN06_PARAMS', inputs)
		self.client['benchmark'] = self.text('IN07_BENCHMARK', inputs)
		self.client['mac_address'] = self.text('IN08_MAC_ADDRESS', inputs)
		self.client['healthcheck_frequency'] = inputs.value('IN09_HEALTHCHECK_FREQUENCY')
		
		# Configure logger based on input
		self.do_log = True if inputs.value('IN11_ENABLE_LOGGING') == 1 else False
		self.set_logger(self.do_log)
			

		self.initialized = True
		self.on_calc(inputs)


	def on_calc(self, inputs):
		"""
		Calculate called if any new input is received by the logic node.

		Args:
			inputs:  Hsl3Slots object containing input slot definition
		"""

		if not self.initialized:
			return

		# Reset the timer
		self.fw.set_timer('HOST_CHECK_TIMER', None)
		self.error = None

		# Handle logging enable/disable input
		if inputs.changed('IN10_TRIGGER_WOL') and self.validate(True):
			# Trigger Wake-on-LAN
			self.logger.info("Wake-on-LAN trigger received")
			wake_on_lan(self.client['mac_address'], self.client['host'], self.logger)
			return
		
		elif inputs.changed('IN09_HEALTHCHECK_FREQUENCY') and \
			self.client['healthcheck_frequency'] != inputs.value('IN09_HEALTHCHECK_FREQUENCY'):
			
			self.client['healthcheck_frequency'] = inputs.value('IN09_HEALTHCHECK_FREQUENCY')
			self.log(f"Healthcheck frequency: {self.client['healthcheck_frequency']}", logging.DEBUG)
			
		elif inputs.changed("IN11_ENABLE_LOGGING"):
			self.do_log = True if inputs.value("IN11_ENABLE_LOGGING") == 1 else False
			self.set_logger(self.do_log)

		else:
			if inputs.changed('IN01_HOSTNAME'):
				self.client['host'] = self.text('IN01_HOSTNAME', inputs)
				
			if inputs.changed('IN02_UDP_PORT'):
				self.client['udp_port'] = inputs.value('IN02_UDP_PORT')

			if inputs.changed('IN03_TCP_PORT'):
				self.client['port'] = inputs.value('IN03_TCP_PORT')
		
			if inputs.changed('IN04_SSL'):
				self.client['ssl'] = inputs.value('IN04_SSL')

			if inputs.changed('IN05_HOST_PATH'):
				self.client['path'] = self.text('IN05_HOST_PATH', inputs)

			if inputs.changed('IN06_PARAMS'):
				self.client['params'] = self.text('IN06_PARAMS', inputs)

			if inputs.changed('IN07_BENCHMARK'):
				self.client['benchmark'] = self.text('IN07_BENCHMARK', inputs)

			if inputs.changed('IN08_MAC_ADDRESS'):
				self.client['mac_address'] = self.text('IN08_MAC_ADDRESS', inputs)

		if self.validate():
			self.log("Validation passed, executing healthchecks", logging.DEBUG)
			self.do_healthchecks()
			if self.client['healthcheck_frequency'] > 0:
				self.log(f"Setting timer for next healthcheck in {self.client['healthcheck_frequency']}s", logging.INFO)
				self.fw.set_timer('HOST_CHECK_TIMER', self.client['healthcheck_frequency'])
			
			for index_or_key in inputs.keys():
				if inputs.changed(index_or_key):
					self.debug.set(index_or_key, inputs.value(index_or_key))
		
		else:
			self.log("Validation failed, clearing outputs", logging.DEBUG)
			self.set_output("OUT1_IS_ONLINE", 0)

	def set_logger(self, do_log = False):
		"""Enables or disables logging."""
		if do_log:
			self.logger.setLevel(logging.DEBUG)
		else:
			self.logger.setLevel(logging.ERROR)

		self.do_log = bool(do_log)
		self.log(f"Logging {'enabled' if self.do_log else 'disabled'}")

	def log(self, message, level=logging.INFO):
		"""Logs a message at the specified level if logging is enabled."""

		if level==logging.DEBUG:
			if self.do_log:
				self.debug.log(message)
		elif level==logging.INFO:
			self.logger.info(message)
		elif level==logging.WARNING:
			self.logger.warning(message)
		elif level==logging.ERROR:
			self.logger.error(message)
		elif level==logging.CRITICAL:
			self.logger.critical(message)

	def on_timer(self, timer):
		"""Executes when the host check timer expires, runs the host check and restarts the timer"""
		
		if timer.changed('HOST_CHECK_TIMER'):
			self.logger.debug("Host check timer triggered")
			self.fw.run_in_context(self.do_healthchecks, ())
			self.fw.set_timer('HOST_CHECK_TIMER', self.client['healthcheck_frequency'])


	def set_output(self, key, value):
		""" Sets an output value taking into account 'send by change' settings """

		if key in self.outputs.keys():
			if not isinstance(value, (int, float, bytes, str)):
				self.logger.error(f"Invalid value type for output '{key}': {type(value)}".encode('iso-8859-15'))
				return
			elif isinstance(value, str):
				value = value.encode('iso-8859-15')

			if self.outputs[key]['value'] != value or self.outputs[key]['sbc'] == 's':
				self.outputs[key]['value'] = value
				self.fw.set_output(key, value)
				if self.do_log:
					self.debug.set(key, value.decode('iso-8859-15') if isinstance(value, bytes) else value)

	def set_error(self, message):
		"""Sets the error message and updates the output accordingly."""

		self.error = message

		self.logger.warning(message)
		self.set_output('OUT4_ERROR_MESSAGE', message)


	def text(self, key, inputs):
		"""Returns the text value of the given input key, decoding it if necessary."""

		value = inputs.get(key).value
		return value.decode('iso-8859-15') if isinstance(value, bytes) else value

	
	def check_hostname(self) -> bool:
		"""Validates the host name input and returns True if valid, False otherwise."""

		host = self.client['host']
		if not host or not re.match(HOSTNAME_REGEX, host):
			self.set_error('Invalid hostname')
			return False
		
		return True

	
	def check_port(self, port: int, type: str) -> bool:
		"""Validates the host port input and returns True if valid, False otherwise."""
		
		if not isinstance(port, int) or port < 0 or port > 65535:
			self.set_error(F"Invalid {type.upper()} port")
			return False
		
		return True
		
	
	def check_ssl(self) -> bool:
		"""Validates the SSL input and returns True if valid, False otherwise."""
		
		ssl = self.client['ssl']
		if ssl not in (0, 1):
			self.set_error('Invalid SSL input')
			return False

		return True

	
	def check_path(self) -> bool:
		"""Validates the HTTP path input, ensuring it starts with '/' if provided."""
	
		path = self.client['path']
		if path and not path.startswith('/'):
			self.set_error('Invalid HTTP path')
			return False

		return True


	def check_params(self) -> bool:
		"""Validates the HTTP request parameters input as a JSON string."""
	
		params = self.client['params']
		try:
			json.loads(params)
		except json.JSONDecodeError as esc:
			if params.find('\'') != -1:
				self.set_error(f"Invalid HTTP request parameters: use double quotes")
			else:
				self.set_error(f"Invalid HTTP request parameters")
			return False

		return True

	
	def check_mac_address(self) -> bool:
		"""Validates the MAC address input as a string, validating its format."""
	
		mac_address = self.client['mac_address']
		if mac_address and not re.match(r'([0-9A-F]{2}[:]){5}[0-9A-F]{2}|([0-9A-F]{2}[-]){5}[0-9A-F]{2}',
                            string=mac_address, flags=re.IGNORECASE):
			self.set_error('Invalid MAC address format')
			return False

		return True

	
	def get_benchmark(self, inputs) -> str:
		"""Returns the healthcheck benchmark input as a string."""

		return self.text('IN06_HEALTHCHECK_BENCHMARK', inputs).strip()
		
	
	def check_healthcheck_frequency(self) -> bool:
		"""Validates the healthcheck frequency input as an integer."""

		frequency = self.client['healthcheck_frequency']
		if not isinstance(frequency, int) or frequency < 0:
			self.set_error('Invalid healthcheck frequency')
			return False
		
		return True


	def validate(self, do_mac_address: bool = True):
		"""Validate the host and port inputs."""

		self.set_output('OUT4_ERROR_MESSAGE', '')
		
		if not self.check_hostname():
			return False
		if not self.check_port(self.client['udp_port'], "udp"):
					return False
		if not self.check_port(self.client['port'], "tcp"):
			return False
		if not self.check_healthcheck_frequency():
			return False
		if not self.check_ssl():
			return False
		if not self.check_path():
			return False
		if not self.check_params():
			return False
		if do_mac_address and not self.check_mac_address():
			return False
		
		return True


	def do_healthchecks(self):
		"""Check the host's network and HTTP health and set the appropriate outputs."""
		
		self.logger.info(f"Starting healthcheck for {self.client['host']}")

		response_text = None
		is_online = False
		response_ms = 0.0

		if not self.client['path']:
			if self.client['udp_port'] and self.client['udp_port'] != 0:
				is_online, response_ms = self.do_udp_healthcheck()
				
			
			if not is_online and self.client['port'] and self.client['port'] != 0:
				is_online, response_ms = self.do_tcp_healthcheck()
			
		elif self.client['path']:
			is_online, response_ms, response_text = self.do_http_healthcheck()
		
		self.set_output('OUT1_IS_ONLINE', 0 if not is_online else 1)
		self.set_output('OUT2_RESPONSE_TIME', response_ms)
		self.set_output('OUT3_RESPONSE_TEXT', response_text if response_text is not None else '')


	def do_udp_healthcheck(self) -> tuple[bool, float]:
		"""Perform a UDP health check and set the appropriate outputs."""

		is_online = False
		response_ms = 0.0
		udp_results  = udp_packet_ping(self.client['host'].strip('[]'), logger=self.logger, port=self.client['udp_port'])
		if udp_results and 'available' in udp_results.keys() and 'response_ms' in udp_results.keys():
			self.logger.info(f"UDP probe returned {udp_results['available']}: {udp_results['response_ms']}")
			is_online = udp_results['available'] is True
			response_ms = udp_results['response_ms']

		return is_online, response_ms



	def do_tcp_healthcheck(self) -> tuple[bool, float]:
		"""Perform a TCP health check and set the appropriate outputs."""

		is_online = False
		response_ms = 0.0
		tcp_results = tcp_health_check(self.client['host'].strip('[]'), self.client['port'], logger=self.logger)
		if tcp_results and 'available' in tcp_results.keys() and 'response_ms' in tcp_results.keys():
			self.logger.info(f"TCP health check returned {tcp_results['available']}: {tcp_results['response_ms']}")
			is_online = tcp_results['available'] is True
			response_ms = tcp_results['response_ms']

		return is_online, response_ms


	def do_http_healthcheck(self) -> tuple[bool, float, str]:
		scheme = 'https' if self.client['ssl'] else 'http'
		url = '{}://{}:{}{}'.format(scheme, self.client['host'], self.client['port'], self.client['path'] or '/')

		response_text = ""
		response_ms = 0.0
	
		self.logger.info(f"Checking HTTP health at {url}")
		params = self.client['params']

		response: requests.Response
		start = time.monotonic()
		try:
			response = requests.get(url, params=params, verify=False)
			response_ms = (time.monotonic() - start) * 1000
			response_text = response.text
			if response.status_code == 200:
				self.logger.info("HTTP health check passed")
				is_online = False
				if self.client['benchmark']:
					if self.client['benchmark'] in response_text:
						self.logger.info("Benchmark found in response body")
						is_online = True
					else:
						self.set_error("Benchmark not found in response body")
				else:
					is_online = True

				return is_online, response_ms, response_text
			
			else:
				self.set_error(f"HTTP health check failed with status {response.status_code}")
				return False, response_ms, response_text
		except requests.RequestException as e:
			self.logger.error(f"HTTP request failed: {e}")
			self.set_error(f"HTTP request failed: {e}")
			return False, 0.0, ""
		