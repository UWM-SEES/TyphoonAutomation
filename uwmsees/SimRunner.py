import typhoon.api.hil as hil
import logging
import math
import time

from datetime import datetime
from datetime import timedelta

from . import ModelManager
from . import SimConfiguration
from . import SimSchedule
from . import SimScenario
from .SimEvents.SimulationEvent import SimulationEvent
from .SimEvents.SimEventCallable import SimEventCallable

# TODO: Run the simulation loop in its own thread, add thread safety as needed, etc.

class SimRunner(object):
  """
  :param SimConfiguration config: Simulation configuration to use
  :param ModelManager model_manager: Manager for the simulated model
  :param SimSchedule schedule: Schedule of invokable simulation events
  :param float update_interval: Wall time interval in seconds to output simulation time
  :param Logger logger: Logger to be used for simulation logging
  """
  def __init__(
      self,
      config: SimConfiguration,
      model_manager: ModelManager,
      schedule: SimSchedule,
      update_interval: float,
      logger: logging.Logger = None):
    # TODO: Check parameters
    
    self.config = config
    self.model_manager = model_manager
    self.schedule = schedule
    
    self.stop_signal = False
    self.wall_start_time: datetime = None
    self.wall_stop_time: datetime = None
    
    self.update_interval = update_interval
    self.last_update_time = datetime.now()

    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
      
      
  def __del__(self):
    try:
      if self.is_simulation_running():
        self.logger.warning("Stopping simulation in SimRunner destructor")
        self.stop_simulation()
    except:
      self.logger.critical("Exception thrown in SimRunner destructor")
      
    
  """
  Run the simulation once for the specified simulation time duration. If the savestate_filename
  parameter is provided, the simulation state will be saved to the file after the simulation run
  
  :param float duration: Simulation time in seconds to run the simulation
  :param str savestate_filename: Filename to save the simulation after the simulation run
  """
  def run_simulation(
      self,
      duration: float,
      savestate_filename: str = None):
    # Check parameters
    if duration <= 0.0:
      raise ValueError(f"Invalid simulation duration ({duration})")
    
    # Start simulation
    sim_start_time = self.get_simulation_time()
    self.logger.info(f"Stopping at sim time {sim_start_time + duration}")

    self.clear_stop_signal()    
    self.start_simulation()
    self.last_update_time = datetime.now()
    
    # Main simulation loop
    while self.is_simulation_running() and not self.get_stop_signal():
      # TODO: Check simulation health, etc.
      # See utils.py in the Typhoon examples (probably {Typhoon install dir}/examples/tests/utilities_lib)
      
      # Get current simulation time
      simulation_time = self.get_simulation_time()
            
      # Invoke all events scheduled up to and including the current simulation time
      while (self.schedule.get_event_count() > 0):
        if self.schedule.next_event_time() > simulation_time:
          # Next event is scheduled for the future, no more events to invoke
          break

        # Pop next event from schedule and invoke the event
        event = self.schedule.pop_next_event()
        self.invoke_event(event)
      
      # Set stop signal if the simulation duration has been reached
      if (not self.get_stop_signal()) and ((simulation_time - sim_start_time) >= duration):
        self.invoke_event(SimEventCallable("Stopping simulation", lambda sim:
          sim.set_stop_signal()))
          
      # Output simulation time at requested intervals
      if (datetime.now() - self.last_update_time) >= timedelta(seconds = self.update_interval):
        self.last_update_time = datetime.now()
        self.logger.info(f"Sim time {self.get_simulation_time()}")
       
    # Stop simulation
    self.stop_simulation(savestate_filename)
    
    elapsed_wall_time = self.wall_stop_time - self.wall_start_time
    self.logger.info(f"Elapsed wall time: {elapsed_wall_time.total_seconds()} seconds")
    
  
  """
  Invoke an event
  
  :param SimulationEvent: Event to be invoked
  """
  def invoke_event(self, event: SimulationEvent):
    try:
      self.logger.info(f"Event at {self.get_simulation_time()}: {event.message}")
      event.invoke(self)
      
    except AttributeError:
      if not hasattr(event, "invoke"):
        self.logger.error("Event object does not have an invoke method")
      elif not hasattr(event, "message"):
        self.logger.error("Event object does not have a message")
        
    except BaseException as ex:
      self.logger.error("Event invocation failed")
      self.logger.exception(ex)
      raise

  
  """
  Start the simulation
  """
  def start_simulation(self):
    self.logger.info("Starting simulation")
    if self.is_simulation_running():
      raise RuntimeError("Simulation is already running")
    
    self.wall_start_time = datetime.now()
    
    # Start capture and simulation
    self.start_capture()
    hil.start_simulation()
  
  
  """
  Stop the simulation
  
  :param str savestate_filename: Filename to save the simulation after the simulation run
  """
  def stop_simulation(
      self,
      savestate_filename: str = None):
    # Stop capture
    if self.capture_in_progress():
      self.stop_capture(timeout = self.config.capture_stop_timeout)
    else:
      self.logger.info("Capture already stopped")
      
    # Save model state if savestate_filename is provided
    if savestate_filename:
      self.logger.info(f"Saving model state to {savestate_filename}")
      #self.model_manager.save_model_state(savestate_filename)
      self.logger.error(f"Not saving model state due to Typhoon bug, see support ticket #003498")
    else:
      self.logger.info("No model state file specified, not saving model state")
    
    # Stop simulation
    if self.is_simulation_running():
      self.logger.info("Stopping simulation")
      hil.stop_simulation()
    else:
      self.logger.warning("Stop simulation called but simulation was not running")
    
    self.wall_stop_time = datetime.now()
  
  
  """
  Check if the simulation is running
  
  :return True if simulation is running, false otherwise
  :rtype bool
  """
  def is_simulation_running(self) -> bool:
    return hil.is_simulation_running()


  """
  Get the current simulation time
  
  :return Simulation time
  :rtype float
  """
  def get_simulation_time(self) -> float:
    return hil.get_sim_time()
  
  
  """
  Get the current simulation step
  
  :return Simulation step
  :rtype int
  """
  def get_simulation_step(self) -> int:
    return hil.get_sim_step()
  
  
  """
  Start the data capture

  :raises ValueError: A configuration value is invalid
  """
  def start_capture(self):
    # Ensure configured values are acceptable
    if self.config.model_timestep <= 0.0:
      raise ValueError(f"Invalid timestep ({self.config.model_timestep})")
    if self.config.sample_frequency <= 0.0:
      raise ValueError(f"Invalid sample frequency ({self.config.sample_frequency})")
    if self.config.capture_start_time < 0.0:
      raise ValueError(f"Invalid capture start time ({self.config.capture_start_time})")
    if self.config.capture_duration < 0.0:
      raise ValueError(f"Invalid capture duration ({self.config.capture_duration})")
    if not self.config.capture_filename:
      raise ValueError(f"Invalid capture filename ({self.config.capture_filename})")
    # TODO: Capture doesn't seem to stop successfully if capture start time is after simulation stop time
    
    # Initialize capture values
    num_analog_channels = len(self.config.analog_capture_signals)
    num_samples = int(self.config.sample_frequency * self.config.capture_duration)
    decimation = int(1.0 / (self.config.model_timestep * self.config.sample_frequency))
    
    capture_digital = len(self.config.digital_capture_signals) > 0
    
    capture_buffer = []
    
    # Start capture
    self.logger.info(f"Capturing {num_samples} samples starting at sim time {self.config.capture_start_time} to {self.config.capture_filename}")
    
    # TODO: Clean up capture parameters, e.g. trigger and execute-at time
    if not hil.start_capture(
        cpSettings = [
          decimation,
          num_analog_channels,
          num_samples,
          capture_digital],
        trSettings = ["Forced"],
        chSettings = [
          self.config.analog_capture_signals,
          self.config.digital_capture_signals],
        dataBuffer = capture_buffer,
        fileName = self.config.capture_filename,
        executeAt = self.config.capture_start_time):  # TODO: executeAt doesn't work as expected (perhaps this isn't its correct use)
      raise RuntimeError("Failed to start capture")
    
        
  """
  Stop the data capture
  
  :param float timeout: Time to wait for data capture in progress to stop
  """
  def stop_capture(self, timeout: float = 0.0):
    if timeout > 0.0:
      start_time = datetime.now()
      elapsed_time = timedelta(seconds = 0.0)
      self.logger.info(f"Waiting for capture to stop, timeout {timeout}")
      
      # Wait for capture to stop, timing out if necessary
      while elapsed_time.total_seconds() < timeout:
        if not self.capture_in_progress():
          self.logger.info("Capture stopped")
          return
        time.sleep(0)   # TODO: Is there a better way to yield without the threading library?
        elapsed_time = datetime.now() - start_time

    if self.capture_in_progress():
      self.logger.info("Stopping capture")
      if not hil.stop_capture():
        self.logger.error("Failed to stop capture")
    else:
      self.logger.warn("Stop capture called but capture was not in progress")
      
      
  """
  Check if capture is in progress

  :return True if capture is in progress, false otherwise
  :rtype bool
  """
  def capture_in_progress(self) -> bool:
    return hil.capture_in_progress()
  
  
  """
  Set the simulation stop signal
  """
  def set_stop_signal(self):
    self.logger.info("Setting stop signal")
    self.stop_signal = True
    
    
  """
  Clear the simulation stop signal
  """
  def clear_stop_signal(self):
    self.stop_signal = False
    
    
  """
  Get the state of the simulation stop signal
  
  :return State of the stop signal (True for stop, False otherwise)
  """
  def get_stop_signal(self):
    return self.stop_signal
  
  
  """
  Schedule an event to be invoked at a given simulation time
  
  :param float simulation_time: Simulation time at which to schedule the event
  :param SimulationEvent event: Simulation event to be invoked at the given time
  """
  def schedule_event(
      self,
      simulation_time: float,
      event):
    return self.schedule.add_event(simulation_time, event)
  
  
  """
  Set up a simulation scenario
  
  :param SimScenario scenario: The simulation scenario to set up
  """
  def set_up_scenario(
      self,
      scenario: SimScenario):
    self.logger.info(f"Setting up scenario")
    try:
      scenario.setup(self)      
    except AttributeError:
      if not hasattr(scenario, "setup"):
        self.logger.error("Scenario object does not have a setup method")
      raise
  
  
  """
  Tear down a simulation scenario
  
  :param SimScenario scenario: The simulation scenario to tear down
  """
  def tear_down_scenario(
      self,
      scenario: SimScenario):
    self.logger.info(f"Tearing down scenario")
    try:
      scenario.teardown(self)      
    except AttributeError:
      if not hasattr(scenario, "teardown"):
        self.logger.error("Scenario object does not have a teardown method")
      raise
