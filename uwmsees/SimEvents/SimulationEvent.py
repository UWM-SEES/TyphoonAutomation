from abc import ABC, abstractmethod

class SimulationEvent(ABC):
  """
  Base simulation event constructor
  
  :param float simulation_time: Simulation time at which to schedule the event
  :param str message: Message to output when the event is invoked
  """
  def __init__(
      self,
      message: str):
    
    self.message = message
    
  
  """
  Invoke the event
  
  :param SimRunner invoker: SimRunner invoking the event
  """  
  @abstractmethod
  def invoke(self, invoker) -> None:
    pass