import sys
import logging

from uwmsees.TyphoonAutomator import TyphoonAutomator

import simulation_scenarios
from simulation_scenarios import ExampleFaultScenario


# Filter available devices by serial number (set to None if not used)
SERIAL_NUMBER_FILTER = [
  "00604-00-00188"]               # HIL-604-Top is 00604-00-00188

SCENARIO_REPETITION_COUNT = 20    # Number of times to run each scenario

HIL_LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # Log message format
HIL_LOGGER_NAME = "HIL_LOGGER"    # Logger name
HIL_LOG_FILENAME = "./log.txt"    # Logging filename
HIL_LOG_LEVEL = logging.DEBUG     # Lowest severity level to log

# TODO list:
# Set the sample frequency elsewhere (perhaps the model manager)
# Set the analog/digital capture channels elsewhere (perhaps the model manager)
# Allow the user to set the capture file path (perhaps in the simulation configuration)
# Allow the user to adjust the number of scenario repetitions (perhaps in the simulation configuration)
# Add a way to load/save simulation configuration files
# Add a way to stream captured data out of the simulation run (e.g. for prototyping digital twins)
# And eventually... separate the simulation code into its own Python package

SAMPLE_FREQUENCY = 3.84e3         # Capture sampling frequency in Hz

# Names of analog signals to capture
ANALOG_CAPTURE_CHANNELS = [
  "Data_F3L1.Ia_inst",
  "Data_F3L1.Ib_inst",
  "Data_F3L1.Ic_inst",
  "Data_F3L1.Va_inst",
  "Data_F3L1.Vb_inst",
  "Data_F3L1.Vc_inst",
  "Data_F3L1.Ia_rms",
  "Data_F3L1.Ib_rms",
  "Data_F3L1.Ic_rms",
  "Data_F3L1.Va_rms",
  "Data_F3L1.Vb_rms",
  "Data_F3L1.Vc_rms",
  "Data_F3L1.Sp",
  "Data_F3L1.Sn",
  "Data_F3L1.Sz",
  "Data_F3L1.f",
  "Data_F3L1.S"]

# Names of digital signals to capture
DIGITAL_CAPTURE_CHANNELS = []


# Create logger
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
  
  # Initialize the automator
  automator.set_sample_frequency(SAMPLE_FREQUENCY)
  automator.add_analog_capture_channels(ANALOG_CAPTURE_CHANNELS)
  automator.add_digital_capture_channels(DIGITAL_CAPTURE_CHANNELS)
  automator.initialize()
  
  # Add a scenario for each fault type
  for fault_name in simulation_scenarios.FAULT_MAP.keys():
    automator.add_scenario(
      name = str(f"Fault-{fault_name}"),
      scenario = ExampleFaultScenario(fault_type = fault_name))
  
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
