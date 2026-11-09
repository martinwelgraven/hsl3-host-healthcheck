# Auto-generated Python file

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT_DIR not in sys.path:
	sys.path.insert(0, ROOT_DIR)
if os.path.join(ROOT_DIR, "src") not in sys.path:
	sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from hsl3.hsl3 import Hsl3Framework
from hsl3.hsl3_wrapper import Hsl3WrapperModule
from src.hsl3_14647_host_healthcheck import LogicModule

json_file = "config_host-healthcheck.json"

def main():

	if sys.platform == "win32":
		os.system('cls')
	else:
		os.system('clear')

	print(" === Starting test for 14647 - Host Healthcheck === ")
	print("")

	hsl3 = Hsl3Framework("14647_host_healthcheck")
	logic_module = LogicModule(hsl3)
	wrapper_node = Hsl3WrapperModule(os.path.join(ROOT_DIR, 'src', json_file), logic_module)  # type: ignore
	if (wrapper_node.config is not None):
		hsl3.config = wrapper_node.config

	wrapper_node.set_input_value("IN01_HOST_NAME", "192.168.3.1")
	wrapper_node.set_input_value("IN02_HOST_PORT", 80)
	wrapper_node.set_input_value("IN03_HOST_SSL", 1)
	wrapper_node.set_input_value("IN04_HOST_PATH", "")
	wrapper_node.set_input_value("IN05_HEALTHCHECK_BENCHMARK", "")
	wrapper_node.set_input_value("IN06_MAC_ADDRESS", "")
	wrapper_node.set_input_value("IN07_HEALTHCHECK_FREQUENCY", 1)
	wrapper_node.set_input_value("IN08_TRIGGER_WOL", 1)

	print("")

	print(" === DEBUG LOG ===")
	print("")

	logic_module.debug.print_log()


if __name__ == "__main__":
	main()
