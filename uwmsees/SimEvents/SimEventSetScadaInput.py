import typhoon.api.hil as hil

from . import SimulationEvent

class SimEventSetScadaInput(SimulationEvent.SimulationEvent):
  def __init__(
      self,
      input_name: str,
      scada_value):
    super().__init__(f"Changing SCADA input {input_name} to {scada_value}")
    
    self.input_name = input_name
    self.scada_value = scada_value


  """
  Modify the specified SCADA value
  
  :param SimRunner invoker: SimRunner invoking the event
  """ 
  def invoke(self, invoker):
    if not hil.set_scada_input_value(self.input_name, self.scada_value):
      raise RuntimeError(f"Failed to set SCADA input {self.input_name}")