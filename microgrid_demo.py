import sys
import logging
import argparse

from datetime import datetime

from uwmsees.HilSetupManager import HilSetupManager
from uwmsees.ModelManager import ModelManager
from uwmsees.SimConfiguration import SimConfiguration
from uwmsees.SimRunner import SimRunner
from uwmsees.SimSchedule import SimSchedule
from uwmsees.SimOrchestrator import SimOrchestrator

import simulation_scenarios
from simulation_scenarios import ExampleFaultScenario


# Filter available devices by serial number (set to None if not used)
SERIAL_NUMBER_FILTER = [
  "00604-00-00188"]               # HIL-604-Top is 00604-00-00188

SCENARIO_REPETITION_COUNT = 20    # Number of times to run each scenario

CAPTURE_STOP_TIMEOUT = 10.0       # Wall time in seconds to wait for capture data transfer to stop
PERIODIC_UPDATE_INTERVAL = 20.0   # Wall time inverval in seconds between periodic updates

HIL_LOGGER_NAME = "HIL_LOGGER"    # Logger name
HIL_LOGGING_FORMAT = "%(levelname)s - %(asctime)s - %(message)s"    # Log message format


# TODO list:
# Read the simulation timestep from the model
# Set the sample frequency elsewhere (perhaps the model manager)
# Set the analog/digital capture channels elsewhere (perhaps the model manager)
# Consider using a builder pattern to instantiate the model manager
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


# Configure logger and log format
logger = logging.getLogger(HIL_LOGGER_NAME)
logger_formatter = logging.Formatter(HIL_LOGGING_FORMAT)

# Configure console logger
logger_console = logging.StreamHandler()
logger_console.setFormatter(logger_formatter)
logger.addHandler(logger_console)


# Parse command line arguments
model_name = None
log_filename = None
schematic_filename = None
compiled_model_filename = None
compile_model_argument = None
force_vhil = False

try:
  parser = argparse.ArgumentParser(
    description = "Typhoon Automation - Automate Typhoon HIL simulations")
  
  parser.add_argument(    # Model name is the only non-switch argument
    "model_name",
    help = "Name of model, used for default filenames",
    type = str)
  
  parser.add_argument(    # Ex: --log_filename "log.txt"
    "--log_filename",
    help = "Filename for logging, defaults to './log.txt' if not provided",
    type = str,
    default = "./log.txt")

  parser.add_argument(    # Ex: --schematic_filename "./models/example.tse"
    "--schematic_filename",
    help = "Path to Typhoon schematic filename, overrides default if provided",
    type = str)

  parser.add_argument(    # Ex: --compiled_filename "./models/example.cpd"
    "--compiled_filename",
    help = "Path to Typhoon compiled model filename, overrides default if provided",
    type = str)

  parser.add_argument(    # Ex: --compile Conditional
    "--compile",
    help = "Compile schematic after loading",
    type = str,
    choices = ["Yes", "No", "Conditional"],
    default = "Conditional")
  
  parser.add_argument(
    "--force_vhil",
    help = "Skip device discovery and force the use of Virtual HIL",
    action = "store_true")
  
  # Parse and check arguments
  args = parser.parse_args()

  model_name = args.model_name
  if not args.model_name:
    raise RuntimeError(f"Invalid model name ({args.model_name})")
  
  log_filename = args.log_filename
  if not args.model_name:
    raise RuntimeError(f"Invalid log file name ({args.log_filename})")
  
  schematic_filename = args.schematic_filename
  compiled_model_filename = args.compiled_filename
  compile_model_argument = args.compile
  force_vhil = args.force_vhil
  
except BaseException as ex:
  logger.critical("Failed to parse command line arguments")
  logger.exception(ex)
  sys.exit(-1)
  
# Configure file logger
try:
  logger_file = logging.FileHandler(filename = log_filename, mode = "w")
  logger_file.setFormatter(logger_formatter)
  logger.addHandler(logger_file)
except BaseException as ex:
  logger.critical("Failed configure log file")
  logger.exception(ex)
  sys.exit(-1)
  
# Set log level  
logger.setLevel(level = logging.DEBUG)

# Program exit code
exit_code = -1

# Objects which need special handling (e.g. resource cleanup)
hil_setup: HilSetupManager = None
sim_runner: SimRunner = None


### Main try block ###
try:
  startup_time = datetime.now()
  logger.info(f"*** Startup at {startup_time.strftime('%H:%M:%S, %m/%d/%Y')} ***")
  
  # Set up HIL
  hil_setup = HilSetupManager(logger = logger)
  
  # If requested, skip device setup and force use of VHIL
  if force_vhil:
    logger.info("Forcing use of VHIL")
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

  # Load schematic
  logger.info(f"Using model name {model_name}")
  model_manager = ModelManager(
    model_name = model_name,
    logger = logger)
  
  if schematic_filename is not None:
    model_manager.load_schematic(filename = schematic_filename)
  else:
    model_manager.load_schematic()
  
  # Compile model if needed
  if compiled_model_filename is None:
    if compile_model_argument == "No":
      logger.info("Not compiling schematic")
    else:
      compile_schematic = compile_model_argument == "Conditional"
      model_manager.compile_schematic(conditional_compile = compile_schematic)
  else:
    logger.info(f"Skipping compile, using compiled model file {compiled_model_filename}")
  
  
  # Load compiled model
  if compiled_model_filename is None:
    compiled_model_filename = model_manager.get_compiled_model_filename()
    
  model_manager.load_model(
    use_vhil = using_vhil,
    filename = compiled_model_filename)
  
  # Configuration simulation
  sim_config = SimConfiguration()
  sim_config.set_model_timestep(model_manager.get_model_timestep())
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
  
  # Done
  exit_code = 0
  

# Catch keyboard interrupt
except KeyboardInterrupt:
  logger.warning("*** Keyboard interrupt ***")
  
  # Try to stop simulation
  try:
    if (sim_runner is not None) and (sim_runner.is_simulation_running()):
      sim_runner.stop_simulation()
  except BaseException as ex:
    logger.critical("Failed to stop simulation")
    logger.exception(ex)
  
  # Try to disconnect HIL
  try:
    if (hil_setup is not None) and (hil_setup.is_connected()):
      hil_setup.disconnect()
  except BaseException as ex:
    logger.critical("Failed to disconnect HIL setup")
    logger.exception(ex)
  
  exit_code = -1
    
# Catch-all exception block    
except BaseException as ex:
  logger.exception(ex)
  exit_code = -1

# Clean up and shut down
finally:
  del sim_runner
  del hil_setup

  logger_file.close()  
  logger_console.close()
  
  logger_file.flush()
  logger_console.flush()
  
  sys.stderr.flush()
  sys.stdout.flush()
  sys.exit(exit_code)
