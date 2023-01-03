import logging

from src import typhoon_automator

from demo_scenario import DemoScenario as DemoScenario

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

# Set log level  
logger.setLevel(HIL_LOG_LEVEL)

# Set example information
DEMO_SCHEMATIC = "./examples/rlc.tse"
DEMO_DATA_LOG_PATH = "./output/data/"
DEMO_CAPTURE_PATH = "./output/capture/"


# Set up and run automator
try:
  automator = typhoon_automator.TyphoonAutomator()
  automator.set_automation_logger(logger)

  # Find available HIL devices
  hil_devices = automator.get_available_devices()
  use_vhil = False

  # Connect to HIL devices, or specify use of Virtual HIL
  if len(hil_devices) > 0:
    devices = automator.connect_devices(hil_devices)

    logger.info(f"Connected to {len(devices)} HIL devices:")
    for serial_num in devices:
      logger.info(f"  {serial_num}")

  else:
    use_vhil = True
    logger.info("Using Virtual HIL")

  # Initialize the automator with the schematic
  automator.initialize(DEMO_SCHEMATIC, conditional_compile = True)
  
  # Add data logging and capture paths
  automator.set_data_logger_path(DEMO_DATA_LOG_PATH)
  automator.set_capture_path(DEMO_CAPTURE_PATH)

  # Add some demo scenarios
  automator.add_scenario(name = "Demo Scenario 1", scenario = DemoScenario(1.0))
  automator.add_scenario(name = "Demo Scenario 2", scenario = DemoScenario(2.0))
  automator.add_scenario(name = "Demo Scenario 3", scenario = DemoScenario(3.0))
  
  # Run all the scenarios
  automator.run(use_vhil = use_vhil)
  
except BaseException as ex:
  logger.critical("Exiting due to exception")
  logger.exception(ex)
