import random

from uwmsees.SimRunner import SimRunner
from uwmsees.SimScenario import SimScenario

from uwmsees.SimEvents.SimEventSetScadaInput import SimEventSetScadaInput

# Map of fault names to fault control values
FAULT_MAP = {
  "None": 0,
  "A-B": 1,
  "A-C": 2,
  "A-B-C": 3,
  "A-Gnd": 4,
  "A-B-Gnd": 5,
  "A-C-Gnd": 6,
  "A-B-C-Gnd": 7
}

SCADA_FAULT_CTRL = "Fault_Ctrl"           # Fault control
SCADA_GEN_OP_MODE = "DG_in.Gen_OP_mode"   # Generator operation mode
SCADA_GEN_ON = "DG_in.Gen_On"             # Generator on/off


class ExampleFaultScenario(SimScenario):
  
  SCENARIO_DURATION = 10.0    # Scenario duration
      
  FAULT_START_MU = 5.0        # Mean time of fault start
  FAULT_START_STDEV = 0.25    # Standard deviation of fault start

  FAULT_STOP_MU = 7.0         # Mean time of fault stop
  FAULT_STOP_STDEV = 0.25     # Standard deviation of fault stop
  
  """
  :param str fault_type: Type of fault to induce
  """  
  def __init__(
      self,
      fault_type: str):
    super().__init__(ExampleFaultScenario.SCENARIO_DURATION)
    
    self.fault_type = fault_type
    
    
  # Add fault start and stop events
  def setup(
      self,
      simulation: SimRunner):
    
    # Get randomized start and stop times
    # TODO: Get rid of this probably-not-infinite loop
    while True:
      fault_start = random.normalvariate(
        mu = ExampleFaultScenario.FAULT_START_MU, 
        sigma = ExampleFaultScenario.FAULT_START_STDEV)
      
      fault_stop = random.normalvariate(
        mu = ExampleFaultScenario.FAULT_STOP_MU,
        sigma = ExampleFaultScenario.FAULT_STOP_STDEV)
      
      # Ensure start time occurs before stop time
      if fault_start < fault_stop:    
        break
    
    # Set initial scenario values
    simulation.invoke_event(SimEventSetScadaInput(SCADA_GEN_ON, 1.0))
    simulation.invoke_event(SimEventSetScadaInput(SCADA_GEN_OP_MODE, 2.0))
    simulation.invoke_event(SimEventSetScadaInput(SCADA_FAULT_CTRL, FAULT_MAP["None"]))

    # Schedule fault events
    simulation.schedule_event(fault_start, SimEventSetScadaInput(SCADA_FAULT_CTRL, FAULT_MAP[self.fault_type]))
    simulation.schedule_event(fault_stop, SimEventSetScadaInput(SCADA_FAULT_CTRL, FAULT_MAP["None"]))
  
  
  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass
