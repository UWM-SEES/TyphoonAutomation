import typhoon.api.device_manager as device_manager
import logging

class HilSetupManager(object):
  def __init__(
      self,
      logger: logging.Logger = None):

    self.device_manager_api = device_manager.DeviceManagerAPI()
    
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
  
  def __del__(self):
    try:
      if self.is_connected():
        self.logger.warning("Disconnecting setup from HilSetupManager destructor")
        self.disconnect()
    except:
      self.logger.critical("Exception thrown in HilSetupManager destructor")
  
  
  """
  Get a list of the available Typhoon devices
  
  :param list serial_number_filter: Filter devices by serial number
  :return List of available Typhoon devices
  :rtype list
  """
  def get_available_devices(
      self,
      serial_number_filter: list = None) -> list:
    self.logger.info("Getting available devices")
    available = self.device_manager_api.get_available_devices()
    
    # Filter available devices by interface and (if requested) serial numbers
    ethernet_devs = list(filter(lambda dev: "interface" in dev and dev["interface"] == "Ethernet", available))
    if (not serial_number_filter) or (len(serial_number_filter) < 1):
      devices = ethernet_devs
    else:
      devices = list(filter(lambda dev: "serial_number" in dev and dev["serial_number"] in serial_number_filter, ethernet_devs))
      
    return devices
  
  
  """
  Connect to a setup using all available HIL devices or the HIL devices
  specified in the argument. The returned list of devices may be different
  than the argument list (if provided)
  
  :param list devices: List of devices to use in setup
  :return List of devices used in the setup
  :rtype list
  """
  def connect_available_devices(self, devices = None) -> list:
    try:
      # Disconnect any currently connected setup
      if self.is_connected():
        self.disconnect()
      
      # Get info for all available devices if no device list was specified
      if devices is None:
        devices = self.get_available_devices()
      
      self.logger.info(f"Checking {len(devices)} devices")
      
      # Get all devices which can be used in the setup
      setup_devices = []
      for device in devices:
        try:
          name = device["device_name"]
          serial = device["serial_number"]
          interface = device["interface"]
          
          # Only use devices connected via Ethernet
          if interface != "Ethernet":
            self.logger.warning(f"Skipping device {name}, serial number {serial}: interface is not Ethernet")
            continue

          self.logger.info(f"Device name {name}, serial number {serial}")
          
          setup_devices.append((name, serial))
        
        # Catch missing device keys, log the error and skip the device 
        except KeyError as ex:
          self.logger.exception(ex)
          continue
        
      # Add devices and connect setup
      if len(setup_devices) < 1:
        self.logger.warning("No usable serial numbers found")
        return []

      self.logger.info("Adding devices to setup")
      serial_numbers = list(map(lambda e: e[1], setup_devices))
      if not self.device_manager_api.add_devices_to_setup(serial_numbers):
        raise RuntimeError("Failed to add devices to setup")

      self.logger.info("Connecting setup")
      if not self.device_manager_api.connect_setup():
        raise RuntimeError("Failed to connect setup")
      
      # Verify that setup is connected
      if not self.is_connected():
        raise RuntimeError("Setup is not connected after connect_setup()")
        
    except:
      self.logger.error("Exception in HilSetupManager.connect_available_devices(), disconnecting")
      if self.is_connected():
        self.disconnect()
      raise
    
    # Return info on which devices are used in the setup
    return setup_devices
  

  """
  Disconnect from the setup
  """
  def disconnect(self):
    if self.is_connected():
      self.logger.info("Disconnecting setup")
      if not self.device_manager_api.disconnect_setup():
        self.logger.error("Failed to disconnect setup")
    else:
      self.logger.warning("Disconnect called, but setup was not connected")


  """
  Check if a setup is currently connected
  
  :return True if a setup is connected, false otherwise
  :rtype bool
  """     
  def is_connected(self) -> bool:
    return self.device_manager_api.is_setup_connected()
