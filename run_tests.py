import logging
import pathlib as PATH

from plotting_data import plot_data
from src import typhoon_automator

from load1_scenario import Load1Scenario as Load1Scenario
from load2_scenario import Load2Scenario as Load2Scenario
from load3_scenario import Load3Scenario as Load3Scenario
from bus_scenario import BusScenario as BusScenario
from gen_scenario import GenScenario as GenScenario

# Create logger
HIL_LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # Log message format
HIL_LOGGING_DATETIMEFORMAT = '%m/%d/%Y %I:%M:%S %p'  # Formats datetime data to be Month/Day/Year Hour:Minute:Seconds AM/PM
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

LOAD1_SCHEMATIC = "./fault_files/load1_faults.tse"
LOAD2_SCHEMATIC = "./fault_files/load2_faults.tse"
LOAD3_SCHEMATIC = "./fault_files/load3_faults.tse"
BUS_SCHEMATIC = "./fault_files/bus_faults.tse"
GEN_SCHEMATIC = "./fault_files/gen_faults.tse"
DATA_LOG_PATH = "./output/data/"
CAPTURE_PATH = "./output/capture/"

RUNS = 1000
capture_time = 1.0 / 60.0


# Set up and run automator
try:
    automator = typhoon_automator.TyphoonAutomator()
    automator.set_automation_logger(logger)

    # Find available HIL devices
    hil_devices = automator.get_available_devices()
    use_vhil = False

    #x = 0
    #popitem = -1
    #for dev in hil_devices:
    #    if dev['device_name'] == 'HiL-604-Bottom':
    #        popitem = x
    #    x += 1
    #if popitem != -1: hil_devices.pop(popitem)

    # Add data logging and capture paths
    automator.set_data_logger_path(DATA_LOG_PATH)
    automator.set_capture_path(CAPTURE_PATH)

    # Connect to HIL devices, or specify use of Virtual HIL
    if len(hil_devices) > 0:
        devices = automator.connect_devices(hil_devices)

        logger.info(f"Connected to {len(devices)} HIL devices:")
        for serial_num in devices:
            logger.info(f"  {serial_num}")

    else:
        use_vhil = True
        logger.info("Using Virtual HIL")

    # Runs Load 1 Fault Scenarios and No Event

    # Initialize the automator with the schematic
    automator.initialize(LOAD1_SCHEMATIC, conditional_compile=True)

    # range(0, 12)
    for fault in range(0, 12):
        for x in range(1, RUNS + 1):
            time = 16
            automator.add_scenario(name=f"Load 1 Scenario {x} Fault {fault}", scenario=Load1Scenario(time))

    # Run all the scenarios
    automator.run(use_vhil=use_vhil)
    automator.shutdown()

    # Connect to HIL devices, or specify use of Virtual HIL
    if len(hil_devices) > 0:
        devices = automator.connect_devices(hil_devices)

        logger.info(f"Connected to {len(devices)} HIL devices:")
        for serial_num in devices:
            logger.info(f"  {serial_num}")

    else:
        use_vhil = True
        logger.info("Using Virtual HIL")

    # Runs Load 2 Fault Scenarios

    # Initialize the automator with the schematic
    automator.initialize(LOAD2_SCHEMATIC, conditional_compile=True)

    #range(1,12)
    for fault in range(1,12):
        for x in range(1, RUNS + 1):
            time = 16
            automator.add_scenario(name=f"Load 2 Scenario {x} Fault {fault}", scenario=Load2Scenario(time))

    # Run all the scenarios
    automator.run(use_vhil=use_vhil)
    automator.shutdown()

    # Connect to HIL devices, or specify use of Virtual HIL
    if len(hil_devices) > 0:
        devices = automator.connect_devices(hil_devices)

        logger.info(f"Connected to {len(devices)} HIL devices:")
        for serial_num in devices:
            logger.info(f"  {serial_num}")

    else:
        use_vhil = True
        logger.info("Using Virtual HIL")

    # Runs Load 3 Fault Scenarios

    # Initialize the automator with the schematic
    automator.initialize(LOAD3_SCHEMATIC, conditional_compile=True)

    for fault in range(1,12):
        for x in range(1, RUNS + 1):
            time = 16
            automator.add_scenario(name=f"Load 3 Scenario {x} Fault {fault}", scenario=Load3Scenario(time))

    # Run all the scenarios
    automator.run(use_vhil=use_vhil)
    automator.shutdown()

    # Connect to HIL devices, or specify use of Virtual HIL
    if len(hil_devices) > 0:
        devices = automator.connect_devices(hil_devices)

        logger.info(f"Connected to {len(devices)} HIL devices:")
        for serial_num in devices:
            logger.info(f"  {serial_num}")

    else:
        use_vhil = True
        logger.info("Using Virtual HIL")

    # Runs Generator Fault Scenarios

    # Initialize the automator with the schematic
    automator.initialize(GEN_SCHEMATIC, conditional_compile=True)

    for fault in range(1,12):
        for x in range(1, RUNS + 1):
            time = 16
            automator.add_scenario(name=f"Generator Scenario {x} Fault {fault}", scenario=GenScenario(time))

    # Run all the scenarios
    automator.run(use_vhil=use_vhil)
    automator.shutdown()

    # Connect to HIL devices, or specify use of Virtual HIL
    if len(hil_devices) > 0:
        devices = automator.connect_devices(hil_devices)

        logger.info(f"Connected to {len(devices)} HIL devices:")
        for serial_num in devices:
            logger.info(f"  {serial_num}")

    else:
        use_vhil = True
        logger.info("Using Virtual HIL")

    # Runs Bus Fault Scenarios

    # Initialize the automator with the schematic
    automator.initialize(BUS_SCHEMATIC, conditional_compile=True)

    for fault in range(1,12):
        for x in range(1, RUNS + 1):
            time = 16
            automator.add_scenario(name=f"Bus Scenario {x} Fault {fault}", scenario=BusScenario(time))

    # Run all the scenarios
    automator.run(use_vhil=use_vhil)
    automator.shutdown()

    plot_data(PATH.Path.cwd() / 'output' / 'capture')

except BaseException as ex:
    logger.critical("Exiting due to exception")
    logger.exception(ex)