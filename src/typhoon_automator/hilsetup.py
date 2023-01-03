import typhoon.api.device_manager as device_manager
import logging


class HilSetupManager(object):
    """ HIL setup managemer
    
    A management object for configuring and interacting with Typhoon HIL devices
    """

    def __init__(
            self,
            automator):
        from .automator import TyphoonAutomator

        if automator is None:
            raise ValueError("Automator cannot be none")
            
        self._automator: TyphoonAutomator = automator

        # Typhoon API for HIL device management
        self._device_manager = device_manager.DeviceManagerAPI()

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
        self._automator.log("Getting available devices")

        available = self._device_manager.get_available_devices()

        # Filter available devices by Ethernet interface
        ethernet_devs = list(
            filter(lambda dev: "interface" in dev and dev["interface"] == "Ethernet", available))

        # Filter avilable devices by serial numbers (if requested)
        if (not serial_numbers) or (len(serial_numbers) < 1):
            devices = ethernet_devs
        else:
            devices = list(
                filter(lambda dev: "serial_number" in dev and dev["serial_number"] in serial_numbers, ethernet_devs))

        return devices

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
        if (not devices) or (len(devices) < 1):
            raise ValueError("Device list cannot be empty")

        try:
            # Disconnect any currently connected setup
            if self.is_connected():
                self._automator.log(
                    "Already connected, disconnecting", logging.WARNING)
                self.disconnect()

            # Try to connect devices
            self._automator.log(f"Checking {len(devices)} devices")

            setup_devices = []
            for device in devices:
                try:
                    name = device["device_name"]
                    serial = device["serial_number"]
                    interface = device["interface"]

                    if interface != "Ethernet":
                        self._automator.log(
                            f"Skipping device {name}, serial number {serial}: interface is not Ethernet")
                        continue

                    self._automator.log(f"Device name {name}, serial number {serial}")
                    setup_devices.append((name, serial))

                # Catch missing device keys, log the error and skip the device
                except KeyError as ex:
                    self._automator.log_exception(ex)
                    continue

            # No usable devices found, return empty list
            if len(setup_devices) < 1:
                self._automator.log("No usable devices found", logging.WARNING)
                return []

            # Add devices to setup
            serial_numbers = list(
                map(lambda e: e[1], setup_devices))

            if not self._device_manager.add_devices_to_setup(serial_numbers):
                raise RuntimeError("Failed to add devices to setup")

            # Connect setup
            if not self._device_manager.connect_setup():
                raise RuntimeError("Failed to connect setup")

            # Return list of connected devices
            return setup_devices

        except:
            self._automator.log("Unhandled exception in connect_devices, disconnecting", logging.ERROR)
            if self.is_connected():
                self.disconnect()
            raise

    def disconnect(self):
        """ Disconnect the HIL setup """
        if self.is_connected():
            self._automator.log("Disconnecting setup")
            if not self._device_manager.disconnect_setup():
                self._automator.log("Failed to disconnect setup", logging.ERROR)
        else:
            self._automator.log("Disconnect called but setup was not connected", logging.WARNING)

    def is_connected(self) -> bool:
        """ Check if the HIL setup is currently connected
        
        :returns True if the HIL setup is connected, false otherwise
        :rtype bool
        """
        return self._device_manager.is_setup_connected()
