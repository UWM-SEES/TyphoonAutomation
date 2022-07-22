import sys
import logging

from datetime import datetime

from uwmsees.HilSetupManager import HilSetupManager
from uwmsees.ModelManager import ModelManager
from uwmsees.SimConfiguration import SimConfiguration
from uwmsees.SimRunner import SimRunner
from uwmsees.SimSchedule import SimSchedule
from uwmsees.SimOrchestrator import SimOrchestrator

import simulation_scenarios
from simulation_scenarios import ExampleFaultScenario


# Set to True to bypass device discovery and force use of Virtual HIL
FORCE_VHIL = False

# Filter available devices by serial number (set to None if not used)
SERIAL_NUMBER_FILTER = [
  "00604-00-00188"]               # HIL-604-Top is 00604-00-00188

SCENARIO_REPETITION_COUNT = 20    # Number of times to run each scenario

CAPTURE_STOP_TIMEOUT = 10.0       # Wall time in seconds to wait for capture data transfer to stop
PERIODIC_UPDATE_INTERVAL = 20.0   # Wall time inverval in seconds between periodic updates

HIL_LOGGER_NAME = "HIL_LOGGER"          # Logger name
LOGGER_FILENAME = "./output/log.txt"    # Logger file name


# TODO list:
# Read the simulation timestep from the model
# Set the sample frequency elsewhere (perhaps the model manager)
# Set the analog/digital capture channels elsewhere (perhaps the model manager)
# Consider using a builder pattern to instantiate the model manager
# Allow the user to set the capture file path (perhaps in the simulation configuration)
# Allow the user to adjust the number of scenario repetitions (perhaps in the simulation configuration)
# Add a way to stream captured data out of the simulation run (e.g. for prototyping digital twins)
# And eventually... separate the simulation code into its own Python package

SIMULATION_TIMESTEP = 2e-6        # Model timestep in seconds
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

  
# Configure logging
logger = logging.getLogger(HIL_LOGGER_NAME)
logger_formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s")

logger_console = logging.StreamHandler()
logger_console.setFormatter(logger_formatter)
logger.addHandler(logger_console)

logger_file = logging.FileHandler(filename = LOGGER_FILENAME, mode = "w")
logger_file.setFormatter(logger_formatter)
logger.addHandler(logger_file)

logger.setLevel(level = logging.DEBUG)

  
### Main try block ###
try:
  startup_time = datetime.now()
  logger.info(f"*** Startup at {startup_time.strftime('%H:%M:%S, %m/%d/%Y')} ***")
  
  # Set up HIL
  hil_setup = HilSetupManager(logger = logger)
  
  if FORCE_VHIL:
    # If requested, skip device setup and force use of VHIL
    using_vhil = True
    devices = []
    
  else:
    # Find available devices and include them in the setup
    devices = hil_setup.get_available_devices(SERIAL_NUMBER_FILTER)
    
    if len(devices) < 1:
      # Default to VHIL if no devices are found
      logger.warning("No available devices found, using VHIL")
      using_vhil = True
      
    else:
      logger.info(f"Found {len(devices)} devices")
      hil_setup.connect_available_devices(devices)
      using_vhil = False

  # Load model
  model_manager = ModelManager(logger = logger)
  
  # TODO: Make path naming more graceful
  model_name = "ringbus-f01"
  model_filename = f"./local/models/ringbus/{model_name} Target files/{model_name}.cpd"
  
  model_manager.load_model(model_filename, use_vhil = using_vhil)
  
  # Configuration simulation
  sim_config = SimConfiguration()
  sim_config.set_model_timestep(SIMULATION_TIMESTEP)
  sim_config.set_sample_frequency(SAMPLE_FREQUENCY)
  sim_config.set_capture_stop_timeout(CAPTURE_STOP_TIMEOUT)
  sim_config.add_analog_capture(ANALOG_CAPTURE_CHANNELS)
  sim_config.add_digital_capture(DIGITAL_CAPTURE_CHANNELS)
  # Don't forget to set the capture filename and capture start/stop times before running the simulation
  
  # Create simulation schedule
  sim_schedule = SimSchedule()
  
  # Initialize simulation runner
  sim_runner = SimRunner(
    config = sim_config,
    model_manager = model_manager,
    schedule = sim_schedule,
    update_interval = PERIODIC_UPDATE_INTERVAL,
    logger = logger)
  
  sim_orchestrator = SimOrchestrator(
    sim_runner = sim_runner,
    logger = logger)
  
  # Add a scenario for each fault type
  for fault_name in simulation_scenarios.FAULT_MAP.keys():
    sim_orchestrator.add_scenario(
      name = str(f"Fault-{fault_name}"),
      scenario = ExampleFaultScenario(fault_type = fault_name))
  
  # Run all scenarios
  start_time = datetime.now()
  logger.info(f"Starting scenario simulations at {start_time.strftime('%H:%M:%S, %m/%d/%Y')}")
  
  sim_orchestrator.run_all_scenarios(repetitions = SCENARIO_REPETITION_COUNT)
  
  stop_time = datetime.now()
  logger.info(f"Ended scenario simulations at {stop_time.strftime('%H:%M:%S, %m/%d/%Y')}")
  
  # Disconnect
  if hil_setup.is_connected():
    hil_setup.disconnect()
    
  shutdown_time = datetime.now()
  logger.info(f"*** Shutdown at {shutdown_time.strftime('%H:%M:%S, %m/%d/%Y')} ***")
  
  
# Catch-all exception block    
except BaseException as ex:
  logger.exception(ex)
  

# Clean up and shut down
finally:
  sys.stderr.flush()
  sys.stdout.flush()
  logger_file.flush()
  logger_console.flush()
  # TODO: Flush anything else, free resources, etc.
