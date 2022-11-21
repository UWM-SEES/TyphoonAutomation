import logging

from .hilsetup import HilSetupManager
from .model import ModelManager
from .orchestrator import Orchestrator
from .simulation import Simulation


class TyphoonAutomator(object):
    """ Typhoon HIL automator

    Interface for automating Typhoon HIL simulations
    """

    _logger: logging.Logger = None              # Logger for automation log output

    _hil_setup: HilSetupManager = None          # HIL setup manager
    _model: ModelManager = None                 # Model manager
    _orchestrator: Orchestrator = None          # Simulation orchestrator
    _simulation: Simulation = None              # Simulation interface

    _schematic_filename: str = None             # Filename of schematic
    _compiled_filename: str = None              # Filename of compiled model

    _data_log_signals: list[str] = []           # List of signals to log
    _data_log_filename: str = None              # Filename for signal log

    _analog_capture_signals: list[str] = []     # Analog capture signal names
    _digital_capture_signals: list[str] = []    # Digital capture signal names
    _capture_filename: str = None               # Filename for signal capture

    def __init__(self):
        self._hil_setup = HilSetupManager(self)
        self._model = ModelManager(self)

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

        # Reset data logging and capture
        self.clear_data_logger_signals()
        self._data_log_filename = None

        self.clear_capture_signals()
        self._capture_filename = None

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

    def set_data_logger_filename(
            self,
            filename: str):
        """ Set the file name for data logging
        
        :param str filename: Path to file for data logging output
        """
        raise NotImplementedError()

    def add_data_logger_signals(
            self,
            signals: list[str]):
        """ Add streaming signals to be logged
        
        :param list[str] signals: Names of streaming signals to be logged
        :raises ValueError: The loaded schematic does not contain one or more of the signal names
        """
        raise NotImplementedError()

    def clear_data_logger_signals(self):
        """ Clear the list of data logging signal names """
        self._data_log_signals = []

    def set_capture_filename(
            self,
            filename: str):
        """ Set the file name for capture signals
        
        :param str filename: Path to file for capture output
        """
        raise NotImplementedError()

    def add_analog_capture_signals(
            self,
            signals: list[str]):
        """ Add analog signals to be captured
        
        :param list[str] signals: Names of analog signals to be captured
        :raises ValueError: The loaded schematic does not contain one or more of the signal names
        """
        raise NotImplementedError()

    def add_digital_capture_signals(
            self,
            signals: list[str]):
        """ Add digital signals to be captured
        
        :param list[str] signals: Names of digital signals to be captured
        :raises ValueError: The loaded schematic does not contain one or more of the signal names
        """
        raise NotImplementedError()

    def clear_capture_signals(self):
        """ Clear the list of capture signal names """
        self._analog_capture_signals = []
        self._digital_capture_signals = []

    def add_scenario(
            self,
            name: str,
            scenario):
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
        self._model.load_to_setup(use_vhil=use_vhil)
        raise NotImplementedError()

    def shutdown(self):
        self._logger.info(f"Shutting down automation")
  
        # Stop simulation if needed
        try:
            if (self._simulation is not None) and (self._simulation.is_simulation_running()):
                self._simulation.stop_simulation()
        except:
            self._logger.critical("Failed to stop simulation")
            raise
  
        # Disconnect HIL
        try:
          if (self._hil_setup is not None) and (self._hil_setup.is_connected()):
            self._hil_setup.disconnect()
        except:
          self._logger.critical("Failed to disconnect HIL setup")
          raise
    
    # Log shutdown  
    shutdown_time = datetime.now()
    self._logger.info(f"*** Shutdown at {shutdown_time.strftime('%H:%M:%S, %m/%d/%Y')} ***")
  
