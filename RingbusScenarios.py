import random

from uwmsees.SimScenario import SimScenario
from uwmsees.SimRunner import SimRunner

from uwmsees.SimEvents.SimEventSetScadaInput import SimEventSetScadaInput

from RingbusModel import RingbusGenset
from RingbusModel import RingbusESS
from RingbusModel import RingbusPV
from RingbusModel import RingbusModel

# TODO: Move this and other examples files into their own repo

def get_time_uniform_delay(
    start_time,
    max_delay):
  return start_time + random.uniform(a = 0.0, b = max_delay)

def get_time_normal_dist(
    time_mu,
    time_stddev):
  return random.normalvariate(mu = time_mu, sigma = time_stddev)


"""
Normal scenario:  Genset, PV, and ESS with random load connects/disconnects
"""
class RingbusScenarioNormalGensetPVESS(SimScenario):
  SCENARIO_DURATION = 20.0
  
  def __init__(self):
    super().__init__(RingbusScenarioNormalGensetPVESS.SCENARIO_DURATION)
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Generator on at start, switch to grid forming shortly thereafter
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusGenset.GEN_ON, RingbusGenset.get_on_value("On")))
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusGenset.GEN_OP_MODE, RingbusGenset.get_op_mode_value("Grid Forming")))
    
    # PV connect and enable
    simulation.schedule_event(get_time_uniform_delay(7.5, 0.16),
                             SimEventSetScadaInput(RingbusPV.PV_CONNECT, RingbusPV.get_connect_value("Connected")))
    simulation.schedule_event(get_time_uniform_delay(7.5, 0.16),
                             SimEventSetScadaInput(RingbusPV.PV_ENABLE, RingbusPV.get_enable_value("Enabled")))
    
    # ESS on
    simulation.schedule_event(get_time_uniform_delay(8.0, 0.16),
                             SimEventSetScadaInput(RingbusESS.ESS_ON, RingbusESS.get_on_value("On")))
    
    # Schedule random load steps
    load_switches = {
      RingbusModel.SW_F3L1_CTRL: 0,
      RingbusModel.SW_F3L2_CTRL: 0,
      RingbusModel.SW_F4L1_CTRL: 0,
      RingbusModel.SW_F4L2_CTRL: 0
    }    
    get_toggle_value = lambda sw: 1 if (sw == 0) else 0
    
    switch_time = 8.5
    
    LOAD_STEP_COUNT = 10
    for __ in range(0, LOAD_STEP_COUNT):
      # Pick a random switch and toggle its value
      switch = random.choice(list(load_switches))
      switch_value = get_toggle_value(load_switches[switch])
      
      switch_time = switch_time + random.uniform(0.0, 1.0)
      simulation.schedule_event(switch_time, SimEventSetScadaInput(switch, switch_value))
      
      load_switches[switch] = switch_value


  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass


"""
Normal scenario:  PV and ESS with random load connects/disconnects
"""
class RingbusScenarioNormalPVESS(SimScenario):
  SCENARIO_DURATION = 20.0
  
  def __init__(self):
    super().__init__(RingbusScenarioNormalPVESS.SCENARIO_DURATION)
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Set ESS to grid forming and lower PV irradiance
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusESS.ESS_OP_MODE, RingbusESS.get_op_mode_value("Grid Forming")))
    
    # ESS on
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusESS.ESS_ON, RingbusESS.get_on_value("On")))
    
    # PV connect and enable
    simulation.schedule_event(get_time_uniform_delay(7.5, 0.16),
                             SimEventSetScadaInput(RingbusPV.PV_CONNECT, RingbusPV.get_connect_value("Connected")))
    simulation.schedule_event(get_time_uniform_delay(7.5, 0.16),
                             SimEventSetScadaInput(RingbusPV.PV_ENABLE, RingbusPV.get_enable_value("Enabled")))
    
    # Schedule random load steps
    load_switches = {
      RingbusModel.SW_F3L1_CTRL: 0,
      RingbusModel.SW_F3L2_CTRL: 0,
      RingbusModel.SW_F4L1_CTRL: 0,
      RingbusModel.SW_F4L2_CTRL: 0
    }    
    get_toggle_value = lambda sw: 1 if (sw == 0) else 0
    
    switch_time = 8.5
    
    LOAD_STEP_COUNT = 10
    for __ in range(0, LOAD_STEP_COUNT):
      # Pick a random switch and toggle its value
      switch = random.choice(list(load_switches))
      switch_value = get_toggle_value(load_switches[switch])
      
      switch_time = switch_time + random.uniform(0.0, 1.0)
      simulation.schedule_event(switch_time, SimEventSetScadaInput(switch, switch_value))
      
      load_switches[switch] = switch_value


  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass
  
  
"""
Normal scenario:  ESS with random load connects/disconnects
"""
class RingbusScenarioNormalESS(SimScenario):
  SCENARIO_DURATION = 20.0
  
  def __init__(self):
    super().__init__(RingbusScenarioNormalESS.SCENARIO_DURATION)
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Set ESS to grid forming
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusESS.ESS_OP_MODE, RingbusESS.get_op_mode_value("Grid Forming")))
    
    # ESS on
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusESS.ESS_ON, RingbusESS.get_on_value("On")))
    
    # Schedule random load steps
    load_switches = {
      RingbusModel.SW_F3L1_CTRL: 0,
      RingbusModel.SW_F3L2_CTRL: 0,
      RingbusModel.SW_F4L1_CTRL: 0,
      RingbusModel.SW_F4L2_CTRL: 0
    }    
    get_toggle_value = lambda sw: 1 if (sw == 0) else 0
    
    switch_time = 8.5
    
    LOAD_STEP_COUNT = 10
    for __ in range(0, LOAD_STEP_COUNT):
      # Pick a random switch and toggle its value
      switch = random.choice(list(load_switches))
      switch_value = get_toggle_value(load_switches[switch])
      
      switch_time = switch_time + random.uniform(0.0, 1.0)
      simulation.schedule_event(switch_time, SimEventSetScadaInput(switch, switch_value))
      
      load_switches[switch] = switch_value


  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass
  
  
"""
Normal scenario:  Genset with random load connects/disconnects
"""
class RingbusScenarioNormalGenset(SimScenario):
  SCENARIO_DURATION = 20.0
  
  def __init__(self):
    super().__init__(RingbusScenarioNormalGenset.SCENARIO_DURATION)
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Generator on at start, switch to grid forming shortly thereafter
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusGenset.GEN_ON, RingbusGenset.get_on_value("On")))
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusGenset.GEN_OP_MODE, RingbusGenset.get_op_mode_value("Grid Forming")))
    
    # Schedule random load steps
    load_switches = {
      RingbusModel.SW_F3L1_CTRL: 0,
      RingbusModel.SW_F3L2_CTRL: 0,
      RingbusModel.SW_F4L1_CTRL: 0,
      RingbusModel.SW_F4L2_CTRL: 0
    }    
    get_toggle_value = lambda sw: 1 if (sw == 0) else 0
    
    switch_time = 8.5
    
    LOAD_STEP_COUNT = 10
    for __ in range(0, LOAD_STEP_COUNT):
      # Pick a random switch and toggle its value
      switch = random.choice(list(load_switches))
      switch_value = get_toggle_value(load_switches[switch])
      
      switch_time = switch_time + random.uniform(0.0, 1.0)
      simulation.schedule_event(switch_time, SimEventSetScadaInput(switch, switch_value))
      
      load_switches[switch] = switch_value


  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass
  

"""
Fault scenario: Generator grid forming, PV enabled, ESS grid forming
  - Start genset
  - Switch genset to grid forming
  - Connect each load (one after another)
  - Connect and enable PV
  - Connect ESS (grid following)
  - Add fault
"""
class RingbusScenarioFaultGensetPVESS(SimScenario):
  SCENARIO_DURATION = 20.0
  
  """
  :param str fault_type: Type of fault to induce
  """
  def __init__(
      self,
      fault_type: str):
    super().__init__(RingbusScenarioFaultGensetPVESS.SCENARIO_DURATION)
    
    self.fault_type = fault_type
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Generator on at start, switch to grid forming shortly thereafter
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusGenset.GEN_ON, RingbusGenset.get_on_value("On")))
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusGenset.GEN_OP_MODE, RingbusGenset.get_op_mode_value("Grid Forming")))
    
    # Load steps (feeder 3 load 1, feeder 4 load 2, feeder 3 load 2, feeder 4 load 1)
    simulation.schedule_event(get_time_uniform_delay(start_time = 8.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 8.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    
    # PV connect and enable
    simulation.schedule_event(get_time_uniform_delay(7.0, 0.16),
                             SimEventSetScadaInput(RingbusPV.PV_CONNECT, RingbusPV.get_connect_value("Connected")))
    simulation.schedule_event(get_time_uniform_delay(7.5, 0.16),
                             SimEventSetScadaInput(RingbusPV.PV_ENABLE, RingbusPV.get_enable_value("Enabled")))
    
    # ESS on
    simulation.schedule_event(get_time_uniform_delay(8.0, 0.16),
                             SimEventSetScadaInput(RingbusESS.ESS_ON, RingbusESS.get_on_value("On")))

    # Fault start
    simulation.schedule_event(get_time_uniform_delay(12.0, 0.16),
                              SimEventSetScadaInput(RingbusModel.FAULT_CTRL, RingbusModel.get_fault_value(self.fault_type)))
    

  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass

  
"""
Fault scenario: PV enabled, ESS grid forming
  - Switch ESS to grid forming
  - Connect and enable ESS
  - Connect and enable PV
  - Connect each load (one after another)
  - Add fault
"""
class RingbusScenarioFaultPVESS(SimScenario):
  SCENARIO_DURATION = 20.0
  
  """
  :param str fault_type: Type of fault to induce
  """
  def __init__(
      self,
      fault_type: str):
    super().__init__(RingbusScenarioFaultPVESS.SCENARIO_DURATION)
    
    self.fault_type = fault_type
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Set ESS to grid forming
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusESS.ESS_OP_MODE, RingbusESS.get_op_mode_value("Grid Forming")))
    
    # Turn on ESS and PV
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusESS.ESS_ON, RingbusESS.get_on_value("On")))
    simulation.schedule_event(7.5, SimEventSetScadaInput(RingbusPV.PV_ENABLE, RingbusPV.get_enable_value("Enabled")))
    simulation.schedule_event(7.5, SimEventSetScadaInput(RingbusPV.PV_ENABLE, RingbusPV.get_connect_value("Connected")))

    
    # Load steps (feeder 3 load 1, feeder 4 load 2, feeder 3 load 2, feeder 4 load 1)
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 10.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 10.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    
    # Fault start
    simulation.schedule_event(get_time_uniform_delay(12.0, 0.16),
                              SimEventSetScadaInput(RingbusModel.FAULT_CTRL, RingbusModel.get_fault_value(self.fault_type)))
    

  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass

  
"""
Fault scenario: ESS grid forming
  - Switch ESS to grid forming
  - Connect and enable ESS
  - Connect each load (one after another)
  - Add fault
"""
class RingbusScenarioFaultESS(SimScenario):
  SCENARIO_DURATION = 20.0
  
  """
  :param str fault_type: Type of fault to induce
  """
  def __init__(
      self,
      fault_type: str):
    super().__init__(RingbusScenarioFaultESS.SCENARIO_DURATION)
    
    self.fault_type = fault_type
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Set ESS to grid forming
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusESS.ESS_OP_MODE, RingbusESS.get_op_mode_value("Grid Forming")))
    
    # Turn on ESS
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusESS.ESS_ON, RingbusESS.get_on_value("On")))

    
    # Load steps (feeder 3 load 1, feeder 4 load 2, feeder 3 load 2, feeder 4 load 1)
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 10.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 10.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    
    # Fault start
    simulation.schedule_event(get_time_uniform_delay(12.0, 0.16),
                              SimEventSetScadaInput(RingbusModel.FAULT_CTRL, RingbusModel.get_fault_value(self.fault_type)))
    

  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass
  
  
"""
Fault scenario: Generator grid forming
  - Start genset
  - Switch genset to grid forming
  - Connect each load (one after another)
  - Add fault
"""
class RingbusScenarioFaultGenset(SimScenario):
  SCENARIO_DURATION = 20.0
  
  """
  :param str fault_type: Type of fault to induce
  """
  def __init__(
      self,
      fault_type: str):
    super().__init__(RingbusScenarioFaultGenset.SCENARIO_DURATION)
    
    self.fault_type = fault_type
    
  # Set up simulation and schedule events
  def setup(
      self,
      simulation: SimRunner):
    # Set default values
    RingbusModel.set_defaults(simulation)
    
    # Generator on at start, switch to grid forming shortly thereafter
    simulation.schedule_event(0.0, SimEventSetScadaInput(RingbusGenset.GEN_ON, RingbusGenset.get_on_value("On")))
    simulation.schedule_event(7.0, SimEventSetScadaInput(RingbusGenset.GEN_OP_MODE, RingbusGenset.get_op_mode_value("Grid Forming")))
    
    # Load steps (feeder 3 load 1, feeder 4 load 2, feeder 3 load 2, feeder 4 load 1)
    simulation.schedule_event(get_time_uniform_delay(start_time = 8.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 8.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.0, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F3L2_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.schedule_event(get_time_uniform_delay(start_time = 9.5, max_delay = 0.16),
                              SimEventSetScadaInput(RingbusModel.SW_F4L1_CTRL, RingbusModel.get_sw_ctrl_value("On")))

    # Fault start
    simulation.schedule_event(get_time_uniform_delay(12.0, 0.16),
                              SimEventSetScadaInput(RingbusModel.FAULT_CTRL, RingbusModel.get_fault_value(self.fault_type)))
    

  # Nothing to do here
  def teardown(
      self,
      simulation: SimRunner):
    pass
