from .hsl3_14647_ping import ping, tcp_health_check, icmp_echo_request, wake_on_lan

class LogicModule:

	def __init__(self, hsl3):
		self.fw = hsl3
		self.debug = self.fw.create_debug_section()

		# For local reuse of output values
		self.outputs = {			
			'IS_DETECTED': { 'value': 0, 'sbc': 's', 'index': 1 } 
		}

	def on_init(self, inputs, store):
		"""
		Initialize the module with input connections and store information
		Args:
			inputs: Hsl3Slots object containing input slot definitions
			store: Hsl3Slots object containing the storage object for maintaining state (for this node unused)
		"""

		for key in inputs.keys():
			# .keys() returns both indexes and keynames
			if key in ['IN01_HOST_NAME', 'IN02_HOST_PORT', 'IN03_HOST_SSL', 'IN04_HOST_PATH', 'IN05_HEALTHCHECK_BENCHMARK', 'IN06_MAC_ADDRESS', 'IN07_HEALTHCHECK_FREQUENCY', 'IN08_TRIGGER_WOL']:
				pass

	def on_calc(self, inputs):
		"""
		Calculate called if any new input is received by the logic node.

		Args:
			inputs:  Hsl3Slots object containing input slot definition
		"""
		# TODO: Implement the health check logic here, using the input values to perform the necessary checks and set the output accordingly.
		if inputs.changed('IN01_HOST_NAME') or inputs.changed('IN02_HOST_PORT') or inputs.changed('IN03_HOST_SSL') or inputs.changed('IN04_HOST_PATH') or inputs.changed('IN05_HEALTHCHECK_BENCHMARK') or inputs.changed('IN06_MAC_ADDRESS') or inputs.changed('IN07_HEALTHCHECK_FREQUENCY'):  
			pass

		if inputs.changed('IN08_TRIGGER_WOL'):
			pass

	def on_timer(self, timer):
		""" Timers """
		pass

	def set_output(self, key, value):
		""" Set output value taking into account 'send by change' settings """

		if key in self.outputs.keys():
			if self.outputs[key]['value'] != value or self.outputs[key]['sbc'] == 's':
				self.outputs[key]['value'] = value
				self.fw.set_output(key, value)

