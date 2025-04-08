import logging
import random

from src import typhoon_automator

from gen_scenario import GenScenario as GenScenario

runs = 10

# Create logger
HIL_LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # Log message format
HIL_LOGGING_DATETIMEFORMAT = '%m/%d/%Y %I:%M:%S %p' #Formats datetime data to be Month/Day/Year Hour:Minute:Seconds AM/PM
HIL_LOGGER_NAME = "HIL_LOGGER"  # Logger name
HIL_LOG_FILENAME = "./log.txt"  # Logging filename
HIL_LOG_LEVEL = logging.DEBUG  # Lowest severity level to log

logger = logging.getLogger(HIL_LOGGER_NAME)
logger_formatter = logging.Formatter(fmt=HIL_LOGGING_FORMAT, datefmt=HIL_LOGGING_DATETIMEFORMAT)

# Add console handler
logger_console = logging.StreamHandler()
logger_console.setFormatter(logger_formatter)
logger.addHandler(logger_console)

# Set log level
logger.setLevel(HIL_LOG_LEVEL)

# Set example information
Gen_SCHEMATIC = "./fault_files/gen_faults.tse"
Gen_DATA_LOG_PATH = "./output/data/"
Gen_CAPTURE_PATH = "./output/capture/"

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
    automator.initialize(Gen_SCHEMATIC, conditional_compile=True)

    capture_time = 1.0/60.0

    # Add data logging and capture paths
    automator.set_data_logger_path(Gen_DATA_LOG_PATH)
    automator.set_capture_path(Gen_CAPTURE_PATH)

    for fault in range(1, 12):
        for x in range(1, runs + 1):
            time = 16
            automator.add_scenario(name=f"Generator Scenario {x} Fault {fault}", scenario=GenScenario(time))


    # Run all the scenarios
    automator.run(use_vhil=use_vhil)

except BaseException as ex:
    logger.critical("Exiting due to exception")
    logger.exception(ex)
