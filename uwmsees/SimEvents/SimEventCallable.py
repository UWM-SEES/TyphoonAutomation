from . import SimulationEvent

class SimEventCallable(SimulationEvent.SimulationEvent):
  """
  :param float simulation_time: Simulation time at which to schedule the event
  :param str message: Message to output when the event is invoked
  :param callable callback: A callable to be called when the event is invoked
  """
  def __init__(
      self,
      message: str,
      callback):
    super().__init__(message)
    
    # If callback is not None, check if it's callable
    if (callback is not None) and (not callable(callback)):
      raise TypeError("Invalid callback")
    
    self.callback = callback
    
  
  """
  Call the provided callback
  
  :param SimRunner invoker: SimRunner invoking the event
  """   
  def invoke(self, invoker) -> None:
    if self.callback is not None:
      self.callback(invoker)
