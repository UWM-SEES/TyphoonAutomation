import sys
import logging

from uwmsees.TyphoonAutomator import TyphoonAutomator

from RingbusModel import RingbusModel

from RingbusScenarios import RingbusScenarioFaultGensetPVESS
from RingbusScenarios import RingbusScenarioFaultPVESS
from RingbusScenarios import RingbusScenarioFaultESS
from RingbusScenarios import RingbusScenarioFaultGenset
from RingbusScenarios import RingbusScenarioNormalGensetPVESS
from RingbusScenarios import RingbusScenarioNormalPVESS
from RingbusScenarios import RingbusScenarioNormalESS
from RingbusScenarios import RingbusScenarioNormalGenset


# Filter available devices by serial number (set to None if not used)
SERIAL_NUMBER_FILTER = [
  "00604-00-00188"]               # HIL-604-Top is 00604-00-00188

SCENARIO_REPETITION_COUNT = 4    # Number of times to run each scenario

# Create logger
HIL_LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # Log message format
HIL_LOGGER_NAME = "HIL_LOGGER"    # Logger name
HIL_LOG_FILENAME = "./log.txt"    # Logging filename
HIL_LOG_LEVEL = logging.DEBUG     # Lowest severity level to log

logger = logging.getLogger(HIL_LOGGER_NAME)
logger_formatter = logging.Formatter(HIL_LOGGING_FORMAT)

# Add console handler
logger_console = logging.StreamHandler()
logger_console.setFormatter(logger_formatter)
logger.addHandler(logger_console)

# Add log file handler
logger_file = logging.FileHandler(filename = HIL_LOG_FILENAME, mode = "w")
logger_file.setFormatter(logger_formatter)
logger.addHandler(logger_file)

# Set log level  
logger.setLevel(HIL_LOG_LEVEL)


# Automator object
automator = None

### Main try block ###
exit_code = -1
try:
  # Create automator
  automator = TyphoonAutomator(logger = logger)
  
  # Handle command line arguments
  parser = automator.build_command_line_parser()
  (args, unknown_args) = parser.parse_known_args()
  automator.configure_from_arguments(args = args)
  
  # Configure and initialize the automation
  RingbusModel.configure_automator(automator)
  automator.set_serial_number_filter(SERIAL_NUMBER_FILTER)
  
  automator.initialize()
  
  # Add scenarios with each fault type
  for fault_name in RingbusModel.FAULT_CTRL_MAP.keys():
    automator.add_scenario(
      name = str(f"FaultGensetPVESS-{fault_name}"),
      scenario = RingbusScenarioFaultGensetPVESS(fault_type = fault_name))
    
    automator.add_scenario(
      name = str(f"FaultPVESS-{fault_name}"),
      scenario = RingbusScenarioFaultPVESS(fault_type = fault_name))
    
    automator.add_scenario(
      name = str(f"FaultESS-{fault_name}"),
      scenario = RingbusScenarioFaultESS(fault_type = fault_name))
    
    automator.add_scenario(
      name = str(f"FaultGenset-{fault_name}"),
      scenario = RingbusScenarioFaultGenset(fault_type = fault_name))
    
  # Add normal scenarios
  NORMAL_SCENARIO_MULTIPLIER = 1
  for __ in range(0, NORMAL_SCENARIO_MULTIPLIER):
    automator.add_scenario(
      name = str(f"NormalGensetPVESS"),
      scenario = RingbusScenarioNormalGensetPVESS())
    
    automator.add_scenario(
      name = str(f"NormalPVESS"),
      scenario = RingbusScenarioNormalPVESS())
    
    automator.add_scenario(
      name = str(f"NormalESS"),
      scenario = RingbusScenarioNormalESS())
    
    automator.add_scenario(
      name = str(f"NormalGenset"),
      scenario = RingbusScenarioNormalGenset())

  
  # Run the automator
  automator.run(SCENARIO_REPETITION_COUNT)
  
  # Shut down
  automator.shutdown()

  # Done
  exit_code = 0
  

# Catch keyboard interrupt
except KeyboardInterrupt:
  logger.warning("*** Keyboard interrupt ***")
  if automator is not None:
    automator.shutdown()
  
  exit_code = -1

# Catch all other exceptions  
except BaseException as ex:
  logger.exception(ex)
  exit_code = -1
  
  
# Clean up and shut down
finally:
  del automator
  
  for handler in logger.handlers:
    handler.close()
    handler.flush()

  sys.stderr.flush()
  sys.stdout.flush()
  sys.exit(exit_code)
