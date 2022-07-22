from abc import ABC, abstractmethod

from . import SimRunner

class SimScenario(ABC):
  def __init__(
      self,
      duration: float):
    if duration < 0.0:
      raise ValueError(f"Invalid scenario duration ({duration})")
    
    self.duration = duration

  """
  Set up the simulation.  Called before the simulation starts
  
  :param SimRunner simulSimRunnernRunner which will run this scenario
  """
  @abstractmethod
  def setup(
      self,
      simulation: SimRunner) -> None:
    pass
  
  
  """
  Tear down the simulation.  Called after the simulation stops
  
  :param SimRunner simulation: SimRunner which ran this scenario
  """
  @abstractmethod
  def teardown(
      self,
      simulation: SimRunner) -> None:
    pass
