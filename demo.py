import logging

from src import typhoon_automator

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

# Set up and run automator
automator = None
try:
  automator = typhoon_automator.TyphoonAutomator()
  automator.set_automation_logger(logger)

  automator.initialize("./examples/rlc.tse")
  
  automator.set_data_logger_filename("./output/signals.csv")
  automator.add_data_logger_signals([
    "I_ind",
    "V_cap"])
  
  automator.set_capture_filename("./output/capture.csv")
  automator.add_analog_capture_signals([
    "I_ind",
    "V_cap"])

  # TODO: Expand this example
  
except BaseException as ex:
  if automator:
    automator.log_exception(ex)
