import logging

from datetime import datetime
from typing import Any

from .hilsetup import HilSetupManager
from .model import ModelManager
from .orchestrator import Orchestrator
from .simulation import Simulation


class TyphoonAutomator(object):
    """ Typhoon HIL automator

    Interface for automating Typhoon HIL simulations
    """

    def __init__(self):
        self._logger: logging.Logger = None              # Logger for automation log output

        self._hil_setup: HilSetupManager = None          # HIL setup manager
        self._model: ModelManager = None                 # Model manager
        self._orchestrator: Orchestrator = None          # Simulation orchestrator
        self._simulation: Simulation = None              # Simulation interface

        self._schematic_filename: str = None             # Filename of schematic
        self._compiled_filename: str = None              # Filename of compiled model

        self._data_logger_path: str = None               # Path for data logging
        self._capture_path: str = None                   # Path for signal capture

        self._hil_setup = self._create_hilsetup()
        self._model = self._create_modelmanager()
        self._simulation = self._create_simulation()
        self._orchestrator = self._create_orchestrator()

    def set_automation_logger(
            self,
            logger: logging.Logger):
        """ Set the logging object to use for automation logging
        
        :param logging.Logger logger: Logging object to use for log output
        """
        self._logger = logger

    def log(
            self,
            message: str,
            level: int = logging.INFO):
        """ Write a message to the automation log

        :param str message: Message to log
        :param int level: Logging level of the message
        """
        if self._logger:
            self._logger.log(level, message)

    def log_exception(
            self,
            ex: BaseException):
        """ Write an exception to the automation log

        :param BaseException ex: Exception to log
        """
        if self._logger:
            self._logger.exception(ex)

    def initialize(
            self,
            schematic: str,
            conditional_compile: bool = False):
        """ Initialize the automator

        :param str schematic: Path to Typhoon schematic to use
        """
        if not schematic:
            raise ValueError("Schematic path cannot be empty")

        self.log("Initializing automator")

        # Load schematic
        self._compiled_filename = None
        self._schematic_filename = schematic
        self._model.load_schematic(self._schematic_filename)
        
        # Compile schematic
        self._model.compile(conditional_compile)

        self.log("Automator initialized")

    def get_available_devices(
            self,
            serial_numbers: list[str] = None) -> list[str]:
        """ Get a list of the available Typhoon devices
        
        Devices must be available via Ethernet.  If serial_numbers is provided, any devices with serial
        numbers not in the list will not be included.
        
        :param list serial_numbers: List of device serial numbers
        :return List of available Typhoon devices
        :rtype list[str]
        """
        return self._hil_setup.get_available_devices(serial_numbers=serial_numbers)

    def connect_devices(
            self,
            devices: list[str]) -> list[(str, str)]:
        """ Connect the specified HIL devices
        
        The returned list contains tuples of device names and serial numbers which were connected.  Not all
        devices in the argument list may actually have been connected.
        
        :param list[str] devices: List of descriptors for devices to connect
        :returns List of connected
        :rtype list[(str, str)]
        """
        return self._hil_setup.connect_devices(devices=devices)

    def disconnect(self):
        """ Disconnect the HIL setup """
        return self._hil_setup.disconnect()

    def is_connected(self) -> bool:
        """ Check if the HIL setup is currently connected
        
        :returns True if the HIL setup is connected, false otherwise
        :rtype bool
        """
        return self._hil_setup.is_connected()

    def set_data_logger_path(
            self,
            path: str):
        """ Set the directory for data logging
        
        :param str path: Path to directory for data logging output
        """
        if not path:
            raise ValueError('Data logging path cannot be empty')
        self._data_logger_path = path

    def set_capture_path(
            self,
            path: str):
        """ Set the directory for capture output
        
        :param str path: Path to directory for capture output
        """
        if not path:
            raise ValueError('Capture path cannot be empty')  
        self._capture_path = path

    def add_scenario(
            self,
            name: str,
            scenario):
        """ Add a scenario to be simulated
  
        :param str name: Scenario name
        :param SimScenario scenario: Scenario to be simulated
        """
        if self._orchestrator is None:
          raise RuntimeError("Automation is not initialized")
    
        self._orchestrator.add_scenario(
          name = name,
          scenario = scenario)

    def clear_scenarios(self):
        raise NotImplementedError()

    def load_scenarios(
            self,
            filename: str):
        raise NotImplementedError()

    def save_scenarios(
            self,
            filename: str):
        raise NotImplementedError()

    def run(
            self,
            use_vhil: bool = False):
        """ Run all scenarios in the automation

        :param bool use_vhil:
        """
        if (self._orchestrator is None) or (self._model is None):
            raise RuntimeError("Automation is not initialized")
        
        if use_vhil:
            self.log("Using Virtual HIL", level = logging.WARNING)

        if self._data_logger_path:
            self._orchestrator.set_data_logging_path(self._data_logger_path)
        if self._capture_path:
            self._orchestrator.set_capture_path(self._capture_path)

        self._model.load_to_setup(use_vhil = use_vhil)
    
        start_time = datetime.now()
        self.log(f"Starting scenario simulations at {start_time.strftime('%H:%M:%S, %m/%d/%Y')}")
    
        self._orchestrator.run_all()
    
        stop_time = datetime.now()
        self.log(f"Ended scenario simulations at {stop_time.strftime('%H:%M:%S, %m/%d/%Y')}")
 

    def shutdown(self):
        """ Shut down and clean up
        """
        
        self.log(f"Shutting down automation")
  
        # Stop simulation if needed
        try:
            if (self._simulation is not None) and (self._simulation.is_simulation_running()):
                self._simulation.stop_simulation()
        except:
            self.log("Failed to stop simulation", level = logging.CRITICAL)
            raise
  
        # Disconnect HIL
        try:
          if (self._hil_setup is not None) and (self._hil_setup.is_connected()):
            self._hil_setup.disconnect()
        except:
          self.log("Failed to disconnect HIL setup", level = logging.CRITICAL)
          raise
    
        # Log shutdown  
        shutdown_time = datetime.now()
        self.log(f"*** Shutdown at {shutdown_time.strftime('%H:%M:%S, %m/%d/%Y')} ***")

    def _create_hilsetup(self) -> HilSetupManager:
        return HilSetupManager(
            automator = self)

    def _create_modelmanager(self) -> ModelManager:
         return ModelManager(
            automator = self)

    def _create_orchestrator(self) -> Orchestrator:
        if self._simulation is None:
            raise RuntimeError("Automator simulation is not initialized")

        return Orchestrator(
            automator = self,
            simulation = self._simulation)

    def _create_simulation(self) -> Simulation:
        if self._model is None:
            raise RuntimeError("Automator model manager is not initialized")

        return Simulation(
            automator = self,
            model = self._model)


class Utility(object):
    """ Utility class
    
    Contains helpful methods
    """

    def create_callback_event(
            message: str,
            callback) -> Any:
        """ Create a generic callback event

        The function to be called should take a Simulation object as the only argument

        :param str message: The message to be logged when the event is invoked
        :param callback: Function to call when invoked
        :return An object with a 'message' string and an 'invoke(Simulation)' method
        :rtype Any
        """
        class _CallbackEvent(object):
            pass
        
        event = _CallbackEvent()
        setattr(event, "message", message)
        setattr(event, "invoke", callback)
        return event
