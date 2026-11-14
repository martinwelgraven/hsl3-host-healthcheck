import re

from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

if __package__:
	from .hsl3_14647_ping import ping, tcp_health_check, icmp_echo_request, wake_on_lan # type: ignore
else:
	from hsl3_14647_ping import ping, tcp_health_check, icmp_echo_request, wake_on_lan # type: ignore


HOSTNAME_REGEX = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r")(?:\."
    r"[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r")*$"
)


class _NoRedirect(HTTPRedirectHandler):
	def redirect_request(self, req, fp, code, msg, headers, newurl):
		return None


class LogicModule:

	def __init__(self, hsl3):
		self.fw = hsl3
		self.debug = self.fw.create_debug_section()

		self.initialized = False
		self.client = {
			'host': '',
			'port': 0,
			'path': '',
			'ssl': False,
			'benchmark': '',
			'mac_address': '',
			'healthcheck_frequency': 0,
			'trigger_wol': False
		}

		self.error = None

		# For local reuse of output values
		self.outputs = {			
			'IS_DETECTED': { 'value': 0, 'sbc': 's', 'index': 1 },
			'IS_ONLINE': { 'value': 0, 'sbc': 's', 'index': 2 },
			'ERROR_MESSAGE': { 'value': b'', 'sbc': 's', 'index': 3 }
		}


	def on_init(self, inputs, store):
		"""
		Initialize the module with input connections and store information
		Args:
			inputs: Hsl3Slots object containing input slot definitions
			store: Hsl3Slots object containing the storage object for maintaining state (for this node unused)
		"""

		self.client['host'] = self.text('IN01_HOSTNAME', inputs)
		self.client['port'] = inputs.value('IN02_HOST_PORT')
		self.client['ssl'] = inputs.value('IN03_HOST_SSL')
		self.client['path'] = self.text('IN04_HOST_PATH', inputs)
		self.client['benchmark'] = self.text('IN05_HEALTHCHECK_BENCHMARK', inputs)
		self.client['mac_address'] = self.text('IN06_MAC_ADDRESS', inputs)
		self.client['healthcheck_frequency'] = inputs.value('IN07_HEALTHCHECK_FREQUENCY')

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
		if inputs.changed('IN08_TRIGGER_WOL') and self.validate(True):
			# Trigger Wake-on-LAN
			broadcast = '255.255.255.255'
			host_parts = self.client['host'].split('.')
			if len(host_parts) == 4:
				if all(0 <= int(x) < 256 for x in host_parts):
					broadcast = '.'.join(host_parts[:3] + ['255'])

			wake_on_lan(self.client['mac_address'], broadcast=broadcast)
			return
		elif inputs.changed('IN07_HEALTHCHECK_FREQUENCY') and self.client['healthcheck_frequency'] != inputs.value('IN07_HEALTHCHECK_FREQUENCY'):
			self.client['healthcheck_frequency'] = inputs.value('IN07_HEALTHCHECK_FREQUENCY')
		else:
			if inputs.changed('IN01_HOSTNAME'):
				self.client['host'] = self.text('IN01_HOSTNAME', inputs)
			if inputs.changed('IN02_HOST_PORT'):
				self.client['port'] = inputs.value('IN02_HOST_PORT')
			if inputs.changed('IN03_HOST_SSL'):
				self.client['ssl'] = inputs.value('IN03_HOST_SSL')
			if inputs.changed('IN04_HOST_PATH'):
				self.client['path'] = self.text('IN04_HOST_PATH', inputs)
			if inputs.changed('IN05_HEALTHCHECK_BENCHMARK'):
				self.client['benchmark'] = self.text('IN05_HEALTHCHECK_BENCHMARK', inputs)
			if inputs.changed('IN06_MAC_ADDRESS'):
				self.client['mac_address'] = self.text('IN06_MAC_ADDRESS', inputs)

		if self.validate():
			self.do_healthchecks()
			if self.client['healthcheck_frequency'] > 0:
				self.fw.set_timer('HOST_CHECK_TIMER', self.client['healthcheck_frequency'])
		else:
			self.set_output("IS_DETECTED", 0)
			self.set_output("IS_ONLINE", 0)


	def on_timer(self, timer):
		"""Executes when the host check timer expires, runs the host check and restarts the timer"""
		
		if timer.changed('HOST_CHECK_TIMER'):
			self.fw.run_in_context(self.do_healthchecks, ())
			self.fw.set_timer('HOST_CHECK_TIMER', self.client['healthcheck_frequency'])


	def set_output(self, key, value):
		""" Sets an output value taking into account 'send by change' settings """

		if key in self.outputs.keys():
			if self.outputs[key]['value'] != value or self.outputs[key]['sbc'] == 's':
				self.outputs[key]['value'] = value
				self.fw.set_output(key, value)

	
	def set_error(self, message):
		"""Sets the error message and updates the output accordingly."""
		
		self.error = message
		self.debug.log(message)
		self.set_output('ERROR_MESSAGE', message.encode('iso-8859-15'))


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

	
	def check_port(self) -> bool:
		"""Validates the host port input and returns True if valid, False otherwise."""
		
		port = self.client['port']
		if not isinstance(port, int) or port <= 0 or port > 65535:
			self.set_error('Invalid port')
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

		return self.text('IN05_HEALTHCHECK_BENCHMARK', inputs).strip()
		
	
	def check_healthcheck_frequency(self) -> bool:
		"""Validates the healthcheck frequency input as an integer."""

		frequency = self.client['healthcheck_frequency']
		if not isinstance(frequency, int) or frequency < 0:
			self.set_error('Invalid healthcheck frequency')
			return False
		
		return True


	def validate(self, do_mac_address: bool = True):
		"""Validate the host and port inputs."""

		self.set_output('ERROR_MESSAGE', ''.encode('iso-8859-15'))
	
		if not self.check_hostname():
			return False
		if not self.check_port():
			return False
		if not self.check_healthcheck_frequency():
			return False
		if not self.check_ssl():
			return False
		if not self.check_path():
			return False
		if do_mac_address and not self.check_mac_address():
			return False
		
		return True


	def do_healthchecks(self):
		"""Check the host's network and HTTP health and set the appropriate outputs."""
		
		is_online = False
		is_detected = self.do_healthcheck_host_on_network()
		if is_detected:
			is_online = self.do_healthcheck_host_alive()
			
		self.set_output('IS_DETECTED', 0 if not is_detected else 1)
		self.set_output('IS_ONLINE', 0 if not is_online else 1)


	def do_healthcheck_host_on_network(self) -> bool:
		"""Check network reachability using TCP, ping, and ICMP."""

		ping_ok = ping(self.client['host'].strip('[]'))
		icmp_ok = icmp_echo_request(self.client['host'].strip('[]'))

		return (ping_ok == True or icmp_ok == True)


	def do_healthcheck_host_alive(self) -> bool:
		"""Check network reachability and HTTP health using the current inputs."""

		scheme = 'https' if self.client['ssl'] else 'http'
		url = '{}://{}:{}{}'.format(scheme, self.client['host'], self.client['port'], self.client['path'] or '/')

		online = False
		error = ''
		
		try:
			benchmark = self.client['benchmark']
			if not benchmark:
				tcp_check = tcp_health_check(self.client['host'].strip('[]'), self.client['port'])
				if type(tcp_check) is bool:
					online = tcp_check
			else:
				opener = build_opener(ProxyHandler({}), _NoRedirect())
				with opener.open(url, timeout=4) as response:
					if 200 <= response.status < 300:
						charset = response.headers.get_content_charset() or 'utf-8'
						body = response.read().decode(charset, errors='replace')
						online = self.client['benchmark'] in body
						if not online:
							error = 'HTTP health check benchmark was not found in the response'
					else:
						error = 'HTTP health check returned status {}'.format(response.status)
		
		except HTTPError as exc:
			self.debug.log('HTTPError occurred: {}'.format(exc))
			error = 'HTTP health check returned status {}'.format(exc.code)
			exc.close()
		except (URLError, OSError, HTTPException, ValueError, LookupError) as exc:
			error = 'HTTP health check failed: {}'.format(exc)
		except Exception as exc:
			error = 'Unexpected error occurred: {}'.format(exc)

		if error:
			self.set_error(error)

		return online
