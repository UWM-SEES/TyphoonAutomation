import logging
import argparse

from datetime import datetime

from .HilSetupManager import HilSetupManager
from .ModelManager import ModelManager
from .SimConfiguration import SimConfiguration
from .SimSchedule import SimSchedule
from .SimRunner import SimRunner
from .SimOrchestrator import SimOrchestrator
from .SimScenario import SimScenario

class TyphoonAutomator(object):
  # Compile argument types
  COMPILE_NO = "No"
  COMPILE_YES = "Yes"
  COMPILE_CONDITIONAL = "Conditional"
  
  # Default parameters
  DEFAULT_UPDATE_INTERVAL = 30.0
  DEFAULT_CAPTURE_STOP_TIMEOUT = 10.0
  
  
  def __init__(
      self,
      logger: logging.Logger = None):
    # Builder options
    self.model_name: str = None
    self.schematic_filename: str = None
    self.compiled_model_filename: str = None
    self.conditional_compile: str = TyphoonAutomator.COMPILE_CONDITIONAL
    self.force_vhil = False
    self.serial_number_filter = None
    
    # Simulation automation parts
    self.hil_setup: HilSetupManager = None
    self.model_manager: ModelManager = None
    self.sim_config = SimConfiguration()
    self.sim_schedule = SimSchedule()
    self.sim_runner: SimRunner = None
    self.sim_orchestrator: SimOrchestrator = None
    
    self.using_vhil = True
    
    self.sim_config.capture_stop_timeout = TyphoonAutomator.DEFAULT_CAPTURE_STOP_TIMEOUT
    
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
    
    
  def __del__(self):
    try:
      if self.sim_runner:
        del self.sim_runner

      if self.hil_setup:
        del self.hil_setup
        
    except:
      if self.logger is not None:
        self.logger.critical("Exception thrown in TyphoonAutomator destructor")

  
  """
  Set the name of the model to be automated
  
  :param str name: Name of model
  """
  def set_model_name(
      self,
      name: str):
    self.model_name = name

    
  """
  Set the schematic filename
  
  :param str filename: Schematic filename to use for the model
  """
  def set_schematic_filename(
      self,
      filename: str):
    self.schematic_filename = filename
    
    
  """
  Set the compiled model filename
  
  :param str filename: Compiled model filename to use
  """
  def set_compiled_model_filename(
      self,
      filename: str):
    self.compiled_model_filename = filename
    
    
  """
  Set the model compile condition:
  TyphoonAutomator.COMPILE_NO to skip compiling
  TyphoonAutomator.COMPILE_YES to always compile model
  TyphoonAutomator.COMPILE_CONDITIONAL to skip compiling if related files are up-to-date
  """
  def set_conditional_compile(
      self,
      compile):
    valid_compile_args = [
      TyphoonAutomator.COMPILE_NO,
      TyphoonAutomator.COMPILE_YES,
      TyphoonAutomator.COMPILE_CONDITIONAL]
    if not compile in valid_compile_args:
      raise ValueError(f"Invalid compile argument ({compile})")
    
    self.conditional_compile = compile
    
    
  """
  Set the flag to force use of Virtual HIL
  
  :param bool force_vhil: True to force use of VHIL, False to attempt device discovery
  """
  def set_force_vhil(
      self,
      force_vhil: bool):
    self.force_vhil = force_vhil
    
    
  """
  Set the serial numbers to be used in the HIL setup
  
  :param list serial_number: List of serial numbers to be used, or None for to use all discovered devices
  """
  def set_serial_number_filter(
      self,
      serial_numbers: list):
    self.serial_number_filter = serial_numbers
    
  
  """
  Set the sample frequency for captured data
  
  :param float frequency: Capture sample frequency
  """  
  def set_sample_frequency(
      self,
      frequency: float):
    self.sim_config.set_sample_frequency(frequency)
    
    
  """
  Add analog channels to be captured
  
  :param list channels: List of analog channel names
  """
  def add_analog_capture_channels(
      self,
      channels: list):
    self.sim_config.add_analog_capture(channels)


  """
  Add digital channels to be captured
  
  :param list channels: List of digital channel names
  """
  def add_digital_capture_channels(
      self,
      channels: list):
    self.sim_config.add_digital_capture(channels)
  
  
  """
  Add a list of streaming signals to be logged
  
  :param list signals: List of names of streaming signals to be logged
  """
  def add_streaming_signals(
      self,
      signals: list):
    self.sim_config.add_streaming_signals(signals)
  
  
  """
  BUild the command line argument parser
  
  :returns An argument parser to handle Typhoon Automator command line arguments
  :rtype argparse.ArgumentParser
  """
  def build_command_line_parser(self) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
      description = "Typhoon Automation - Automate Typhoon HIL simulations",
      allow_abbrev = False)
    
    parser.add_argument(    # Model name is the only non-switch argument
      "model_name",
      help = "Name of model, used for default filenames",
      type = str)

    parser.add_argument(    # Ex: --schematic_filename "./models/example.tse"
      "--schematic_filename",
      help = "Path to Typhoon schematic filename, overrides default if provided",
      type = str)

    parser.add_argument(    # Ex: --compiled_filename "./models/example.cpd"
      "--compiled_filename",
      help = "Path to Typhoon compiled model filename, overrides default if provided",
      type = str)

    parser.add_argument(    # Ex: --conditional_compile Conditional
      "--conditional_compile",
      help = "Compile schematic after loading",
      type = str,
      choices = [
        TyphoonAutomator.COMPILE_NO,
        TyphoonAutomator.COMPILE_YES,
        TyphoonAutomator.COMPILE_CONDITIONAL],
      default = TyphoonAutomator.COMPILE_CONDITIONAL)
    
    parser.add_argument(
      "--force_vhil",
      help = "Skip device discovery and force the use of Virtual HIL",
      action = "store_true")
    
    return parser
    
    
  """
  Set configuration values from parsed command line arguments
  
  :param args: Arguments parsed by the TyphoonAutomator argument parser
  """
  def configure_from_arguments(
      self,
      args):
    try:
      # Check model name
      if not args.model_name:
        raise RuntimeError(f"Invalid model name ({args.model_name})")
      self.set_model_name(args.model_name)
      
      # Set remaining parameters  
      self.set_schematic_filename(filename = args.schematic_filename)
      self.set_compiled_model_filename(filename = args.compiled_filename)
      self.set_conditional_compile(compile = args.conditional_compile)
      self.set_force_vhil(force_vhil = args.force_vhil)
    
    except AttributeError:
      self.logger.error("Attribute error while configuring from arguments")
      raise

    except BaseException:
      self.logger.error("Failed to configure from arguments")
      raise

  
  """
  Initialize the automation
  
  :raises ValueError: A parameter is invalid
  """  
  def initialize(self):
    # Check parameters
    if not self.model_name:
      raise ValueError("Invalid model name")
   
    # Log start
    startup_time = datetime.now()
    self.logger.info(f"*** Initialization at {startup_time.strftime('%H:%M:%S, %m/%d/%Y')} ***")
    
    # Create HIL setup manager
    self.hil_setup = HilSetupManager(self.logger)
    
    # Set up HIL, skip device setup and force use of VHIL if requested
    if self.force_vhil:
      self.logger.info("Forcing use of VHIL")
      self.using_vhil = True
      devices = []  
    else:
      # Find available devices and include them in the setup
      available = self.hil_setup.get_available_devices(self.serial_number_filter)
      devices = self.hil_setup.connect_available_devices(available)
      
      if len(devices) < 1:
        # Default to VHIL if no devices are found
        self.logger.warning("No available devices found, using VHIL")
        self.using_vhil = True
      else:
        self.logger.info(f"Using {len(devices)} devices")
        self.using_vhil = False

    # Create model manager
    self.model_manager = ModelManager(
      model_name = self.model_name,
      logger = self.logger)
            
    # Load schematic
    self.logger.info(f"Using model name {self.model_name}")

    if self.schematic_filename is not None:
      self.model_manager.load_schematic(filename = self.schematic_filename)
    else:
      self.model_manager.load_schematic()
    
    # Compile model if needed
    if self.compiled_model_filename is None:
      if self.conditional_compile == "No":
        self.logger.info("Not compiling schematic")
      else:
        compile_flag = self.conditional_compile == "Conditional"
        self.model_manager.compile_schematic(conditional_compile = compile_flag)
    else:
      self.logger.info(f"Skipping compile, using compiled model file {self.compiled_model_filename}")
    
    # Load compiled model
    if self.compiled_model_filename is None:
      self.compiled_model_filename = self.model_manager.get_compiled_model_filename()
      
    self.model_manager.load_model(
      use_vhil = self.using_vhil,
      filename = self.compiled_model_filename)
    
    # Update configuration
    self.sim_config.set_model_timestep(self.model_manager.get_model_timestep())
     
    # Initialize simulation runner
    self.sim_runner = SimRunner(
      config = self.sim_config,
      model_manager = self.model_manager,
      schedule = self.sim_schedule,
      update_interval = TyphoonAutomator.DEFAULT_UPDATE_INTERVAL,
      logger = self.logger)
    
    self.sim_orchestrator = SimOrchestrator(
      sim_runner = self.sim_runner,
      logger = self.logger)
  
  
  """
  Run all scenarios in the automation
  
  :param int repetions: Number of times to repeat scenario simulation
  """
  def run(
      self,
      repetitions: int = 1):
    
    if self.sim_orchestrator is None:
      raise RuntimeError("Automation is not initialized")
    
    start_time = datetime.now()
    self.logger.info(f"Starting scenario simulations at {start_time.strftime('%H:%M:%S, %m/%d/%Y')}")
    
    self.sim_orchestrator.run_all_scenarios(repetitions = repetitions)
    
    stop_time = datetime.now()
    self.logger.info(f"Ended scenario simulations at {stop_time.strftime('%H:%M:%S, %m/%d/%Y')}")
  
  
  """
  Shut down and clean up
  """
  def shutdown(self):
    self.logger.info(f"Shutting down automation")
  
    # Stop simulation if needed
    try:
      if (self.sim_runner is not None) and (self.sim_runner.is_simulation_running()):
        self.sim_runner.stop_simulation()
    except:
      self.logger.critical("Failed to stop simulation")
      raise
  
    # Disconnect HIL
    try:
      if (self.hil_setup is not None) and (self.hil_setup.is_connected()):
        self.hil_setup.disconnect()
    except:
      self.logger.critical("Failed to disconnect HIL setup")
      raise
    
    # Log shutdown  
    shutdown_time = datetime.now()
    self.logger.info(f"*** Shutdown at {shutdown_time.strftime('%H:%M:%S, %m/%d/%Y')} ***")
  
  
  """
  Add a scenario to be simulated
  
  :param str name: Scenario name
  :param SimScenario scenario: Scenario to be simulated
  """
  def add_scenario(
      self,
      name: str,
      scenario: SimScenario):
    if self.sim_orchestrator is None:
      raise RuntimeError("Automation is not initialized")
    
    self.sim_orchestrator.add_scenario(
      name = name,
      scenario = scenario)
