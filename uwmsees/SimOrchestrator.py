import logging

from datetime import datetime

from . import SimRunner
from . import SimScenario

class SimOrchestrator(object):
  """
  :param SimRunner sim_runner: SimRunner to use for the simulation
  """
  def __init__(
      self,
      sim_runner: SimRunner,
      logger: logging.Logger = None):
    if sim_runner is None:
      raise ValueError("SimRunner cannot be None")
    
    self.sim_runner: SimRunner = sim_runner
    self.scenario_map = {}
    
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
      
      
  """
  Run all scenarios
  
  :param int repetions: Number of times to repeat scenario simulation
  """
  def run_all_scenarios(
    self,
    repetitions: int = 1):
    if repetitions < 1:
      raise ValueError(f"Invalid number of repetitions ({repetitions})")
    
    # Run each scenario for the given number of repetitions
    scenario_names = self.get_scenario_names()
    for name in scenario_names:
      self.run_scenario(name, repetitions)


  """
  Run a scenario for its specified number of repetitions
  
  :param str name: Name of scenario to run
  :raises ValueError: A parameter is invalid
  """
  def run_scenario(
      self,
      name: str,
      repetitions: int = 1):
    if not name or not name in self.scenario_map.keys():
      raise ValueError(f"Invalid scenario name ({name})")
    if repetitions < 1:
      raise ValueError(f"Invalid number of repetitions ({repetitions})")
    
    # Lambda for creating timestamped filenames
    generate_capture_filename = lambda name: str(
      f"./output/{name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv")
    
    # Get scenario
    scenario = self.scenario_map[name]
    duration = scenario.duration
    
    # Run the scenario simulation for the given number of repetitions
    for rep in range(repetitions):
      self.logger.info(f"--- Scenario {name}, repetition {rep} ---")
      
      # Set capture filaname for this iteration
      capture_filename = generate_capture_filename(name)
      self.sim_runner.config.set_capture_filename(capture_filename)
      streaming_filename = generate_capture_filename(name)
      self.sim_runner.config.set_streaming_filename(streaming_filename)
      
      # Set capture times to full length of simulation
      # TODO: Consider adding capture start/stop times to the scenario
      self.sim_runner.config.set_capture_start_time(0.0)
      self.sim_runner.config.set_capture_duration(duration)
    
      # Clear any leftover events
      self.sim_runner.schedule.clear_schedule()

      # Set up scenario
      try:
        self.sim_runner.set_up_scenario(scenario)
      except:
        self.logger.error("Failed to set up scenario")
        raise
      
      # Run simulation
      try:
        self.sim_runner.run_simulation(duration = scenario.duration)
      except:
        self.logger.error("Failed to run scenario simulation")
        raise
      
      # Tear down simulation
      try:
        self.sim_runner.tear_down_scenario(scenario)
      except:
        self.logger.error("Failed to tear down scenario")
        raise
      
    self.logger.info(f"--- End scenario {name}, {repetitions} repetitions ---")
    
  
  """
  Get a list of the existing scenario names
  
  :return List of scenario names
  :rtype list
  """
  def get_scenario_names(self) -> list:
    return list(self.scenario_map.keys())
    
  
  """
  Add a scenario to be simulated
  
  :param str name: Scenario name
  :param SimScenario scenario: Scenario to be simulated
  :raises ValueError: A parameter is invalid
  """
  def add_scenario(
      self,
      name: str,
      scenario: SimScenario):
    if not name:
      raise ValueError(f"Invalid scenario name ({name})")
    if scenario is None:
      raise ValueError("Scenario cannot be None")
    # TODO: Ensure name is filename friendly (e.g. for capture filename)
    
    if name in self.scenario_map.keys():
      raise ValueError(f"Scenario name {name} already exists")
    
    self.scenario_map[name] = scenario
    
  
  """
  Remove a scenario
  
  :param str name: Scenario name
  :raises ValueError: A parameter is invalid
  """
  def remove_scenario(
      self,
      name: str):
    try:
      del self.scenario_map[name]
    except:
      self.logger.error(f"Failed to remove scenario ({name})")
      raise
