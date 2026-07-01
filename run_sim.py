import logging
import time
LOG_LEVEL = logging.DEBUG
LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
from colorlog import ColoredFormatter
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)

from src import typhoon_automator
from sim_scenario import SimScenario as SimScenario

# Create logger
HIL_LOGGER_NAME = "HIL_LOGGER"  # Logger name
HIL_LOG_FILENAME = "./log.txt"  # Logging filename
HIL_LOG_LEVEL = logging.DEBUG  # Lowest severity level to log

logger = logging.getLogger(HIL_LOGGER_NAME)

# Add console handler
logger_console = logging.StreamHandler()
logger_console.setFormatter(formatter)
logger.addHandler(logger_console)

# Set log level
logger.setLevel(HIL_LOG_LEVEL)

Gen_1_2_SCHEMATIC = "./tsefiles/FaultsG12Testing.tse"
Gen_1_3_SCHEMATIC = "./tsefiles/FaultsG13Testing.tse"
Bus_SCHEMATIC = "./tsefiles/FaultsBTesting.tse"

CAPTURE_PATH = "./output/capture/"
DATA_LOG_PATH = "./output/data/"

SIM_RUNS = 100
time_sim = 17
offset = 100
start_time = time.perf_counter()

try:
    automator = typhoon_automator.TyphoonAutomator()
    automator.set_automation_logger(logger)

    # Find available HIL devices
    hil_devices = automator.get_available_devices()
    use_vhil = False

    x = 0
    popitem = -1
    top = {}
    for dev in hil_devices: # Only connects to one HIL devices leaving the others available so use
        if dev['device_name'] == '604_Bottom_0':
            popitem = x
        x += 1
    if popitem != -1:
        top = hil_devices.pop(popitem)
    hil_devices = [top]
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

        # Initialize the automator with the schematic
    automator.initialize(Gen_1_2_SCHEMATIC, conditional_compile=True)

    #TODO: Uncomment this
    # range(0, 12)
    # for fault in range(0, 5):
    #     for x in range(1, SIM_RUNS + 1):
    #         automator.add_scenario(name=f"Load 1 Scenario {x+offset} Fault {fault}", scenario=SimScenario(time_sim))

    for fault in range(1, 5):
        for x in range(1, SIM_RUNS + 1):
            automator.add_scenario(name=f"Load 2 Scenario {x+offset} Fault {fault}", scenario=SimScenario(time_sim))

    for fault in range(1, 5):
        for x in range(1, SIM_RUNS + 1):
            automator.add_scenario(name=f"Generator Scenario {x+offset} Fault {fault}", scenario=SimScenario(time_sim))

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

        # Initialize the automator with the schematic
    automator.initialize(Gen_1_3_SCHEMATIC, conditional_compile=True)

    for fault in range(1, 5):
        for x in range(1, SIM_RUNS + 1):
            automator.add_scenario(name=f"Load 3 Scenario {x+offset} Fault {fault}", scenario=SimScenario(time_sim))

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

        # Initialize the automator with the schematic
    automator.initialize(Bus_SCHEMATIC, conditional_compile=True)

    for fault in range(1, 5):
        for x in range(1, SIM_RUNS + 1):
            automator.add_scenario(name=f"Bus Scenario {x+offset} Fault {fault}", scenario=SimScenario(time_sim))

    # Run all the scenarios
    automator.run(use_vhil=use_vhil)
    automator.shutdown()

except BaseException as ex:
    logger.critical("Exiting due to exception")
    logger.exception(ex)
finally:
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    logger.info(f"Program runtime: {elapsed_time:.2f} seconds")
    logger.info(f"Program runtime: {elapsed_time / 60:.2f} minutes")