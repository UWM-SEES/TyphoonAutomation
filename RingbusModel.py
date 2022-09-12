from uwmsees.TyphoonAutomator import TyphoonAutomator

from uwmsees.SimRunner import SimRunner

from uwmsees.SimEvents.SimEventSetScadaInput import SimEventSetScadaInput

# TODO: Move this and other examples files into their own repo

# Ringbus generator
class RingbusGenset(object):
  GEN_CTRL_MODE = "DG_in.Gen_Control_Mode"    # Generator control mode
  GEN_ON = "DG_in.Gen_On"                     # Generator on/off
  GEN_OP_MODE = "DG_in.Gen_OP_mode"           # Generator operation mode
  GEN_PF_REF = "DG_in.pf_ref"                 # Generator pf reference
  GEN_PREF = "DG_in.Pref"                     # Generator active power reference
  GEN_VREF = "DG_in.Vref"                     # Generator voltage reference
  GEN_WREF = "DG_in.wref"                     # Generator speed reference
  
  GEN_CTRL_MODE_MAP = {
    "Vf": 0,
    "PV": 1,
    "P - pref": 2
  }
    
  GEN_ON_MAP = {
    "Off": 0,
    "On": 1
  }
  
  GEN_OP_MODE_MAP = {
    "Standby": 0,
    "Grid Following": 1,
    "Grid Forming": 2
  }
  
  GEN_PF_MODE_MAP = {
    "Lead": -1,
    "Lag": 1
  }
  
  SB = 8.619e3        # MVA
  FB = 60.0           # Hz
  PMS = 4             # Number of pole pairs
  WB = FB * 60.0/PMS  # RPM
  VTB = 13.8e3        # V
  
  def get_ctrl_mode_value(ctrl_mode):
    return RingbusGenset.GEN_CTRL_MODE_MAP[ctrl_mode]
  
  def get_on_value(gen_on):
    return RingbusGenset.GEN_ON_MAP[gen_on]
  
  def get_op_mode_value(op_mode):
    return RingbusGenset.GEN_OP_MODE_MAP[op_mode]
  
  def get_wref_value(wref):
    return float(wref / RingbusGenset.WB)
  
  def get_pref_value(pref):
    return float(pref / RingbusGenset.SB)
  
  def get_vref_value(vref):
    return float(vref / RingbusGenset.VTB)
  
  def get_pf_ref_value(pf_mode, pf_ref):
    mult = RingbusGenset.GEN_PF_MODE_MAP[pf_mode]
    return float(pf_ref * mult)
    
  def set_defaults(simulation: SimRunner):
    simulation.invoke_event(SimEventSetScadaInput(RingbusGenset.GEN_ON, RingbusGenset.get_on_value("Off")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusGenset.GEN_CTRL_MODE, RingbusGenset.get_ctrl_mode_value("Vf")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusGenset.GEN_PF_REF, RingbusGenset.get_pf_ref_value("Lag", 4.7)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusGenset.GEN_OP_MODE, RingbusGenset.get_op_mode_value("Standby")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusGenset.GEN_WREF, RingbusGenset.get_wref_value(900)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusGenset.GEN_PREF, RingbusGenset.get_pref_value(1)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusGenset.GEN_VREF, RingbusGenset.get_vref_value(13.8e3)))
    

# Ringbus PV plant
class RingbusPV(object):
  PV_CONNECT = "PV_in.Connect"            # PV connect
  PV_ENABLE = "PV_in.Enable"              # PV enable
  PV_IRRADIATION = "PV_in.Irradiation"    # PV irradiation
  PV_Q_MODE = "PV_in.Q_mode"              # PV Q mode
  PV_QREF = "PV_in.Q_ref"                 # PV Q reference
  PV_VREF = "PV_in.V_ref"                 # PV voltage reference
  
  PV_CONNECT_MAP = {
    "Disconnected": 0,
    "Connected": 1
  }
  
  PV_ENABLE_MAP = {
    "Disabled": 0,
    "Enabled": 1
  }
  
  PV_Q_MODE_MAP = {
    "Disabled": 0,
    "Enabled": 1
  }
  
  SB = 5.0e6    # VA
  VB = 480.0    # V
  FB = 60.0     # Hz
  VDC = 1000.0  # V
  
  def get_connect_value(connect):
    return RingbusPV.PV_CONNECT_MAP[connect]
  
  def get_enable_value(enable):
    return RingbusPV.PV_ENABLE_MAP[enable]
  
  def get_q_mode_value(q_mode):
    return RingbusPV.PV_Q_MODE_MAP[q_mode]
  
  def get_irradiation_value(irr):
    return float(irr)

  def get_vref_value(vref):
    return float(vref)

  def get_qref_value(qref):
    return float(qref)
  
  def set_defaults(simulation: SimRunner):
    simulation.invoke_event(SimEventSetScadaInput(RingbusPV.PV_CONNECT, RingbusPV.get_connect_value("Disconnected")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusPV.PV_ENABLE, RingbusPV.get_enable_value("Disabled")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusPV.PV_Q_MODE, RingbusPV.get_q_mode_value("Enabled")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusPV.PV_IRRADIATION, RingbusPV.get_irradiation_value(100)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusPV.PV_VREF, RingbusPV.get_vref_value(480)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusPV.PV_QREF, RingbusPV.get_qref_value(0)))
  

# Ringbus battery ESS
class RingbusESS(object):
  ESS_FREF = "Batt_in.f_ref"      # ESS frequency reference
  ESS_ON = "Batt_in.On"           # ESS on/off
  ESS_OP_MODE = "Batt_in.mode"    # ESS operation mode
  ESS_PREF = "Batt_in.Pref"       # ESS active power reference
  ESS_QREF = "Batt_in.Qref"       # ESS reactive power reference
  ESS_VREF = "Batt_in.Vref"       # ESS voltage reference
  
  ESS_ON_MAP = {
    "Off": 0,
    "On": 1
  }
  
  ESS_OP_MODE_MAP = {
    "Grid Forming": 0,
    "Grid Following": 1
  }
  
  VB = 480.0    # V
  FB = 60.0     # Hz
  SB = 1.6e6    # VA
  
  def get_on_value(ess_on):
    return RingbusESS.ESS_ON_MAP[ess_on]
  
  def get_op_mode_value(op_mode):
    return RingbusESS.ESS_OP_MODE_MAP[op_mode]
  
  def get_vref_value(vref):
    return float(vref)
  
  def get_fref_value(fref):
    return float(fref)
  
  def get_pref_value(pref):
    return float(pref * 1e3)
  
  def get_qref_value(qref):
    return float(qref * 1e3)
  
  def set_defaults(simulation: SimRunner):
    simulation.invoke_event(SimEventSetScadaInput(RingbusESS.ESS_ON, RingbusESS.get_on_value("Off")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusESS.ESS_OP_MODE, RingbusESS.get_op_mode_value("Grid Following")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusESS.ESS_VREF, RingbusESS.get_vref_value(480)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusESS.ESS_FREF, RingbusESS.get_fref_value(60)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusESS.ESS_PREF, RingbusESS.get_pref_value(0)))
    simulation.invoke_event(SimEventSetScadaInput(RingbusESS.ESS_QREF, RingbusESS.get_qref_value(0)))
  

# Ringbus model  
class RingbusModel(object):
  # Capture sampling frequency in Hz
  SAMPLE_FREQUENCY = 3.84e3  
  
  # Load switch SCADA inputs
  SW_F3L1_CTRL = "SW_F3L1_Ctrl"   # Feeder 3, load 1
  SW_F3L1_GEN_CTRL = "SW_F3L1_Gen_Ctrl"
  SW_F3L1_ESS_CTRL = "SW_F3L1_ESS_Ctrl"
  
  SW_F3L2_CTRL = "SW_F3L2_Ctrl"   # Feeder 3, load 2
  SW_F3L2_GEN_CTRL = "SW_F3L2_Gen_Ctrl"
  SW_F3L2_ESS_CTRL = "SW_F3L2_ESS_Ctrl"
  
  SW_F4L1_CTRL = "SW_F4L1_Ctrl"   # Feeder 4, load 1
  SW_F4L1_GEN_CTRL = "SW_F4L1_Gen_Ctrl"
  SW_F4L1_ESS_CTRL = "SW_F4L1_ESS_Ctrl"
  
  SW_F4L2_CTRL = "SW_F4L2_Ctrl"   # Feeder 4, load 2
  SW_F4L2_GEN_CTRL = "SW_F4L2_Gen_Ctrl"
  SW_F4L2_ESS_CTRL = "SW_F4L2_ESS_Ctrl"
  
  # Bus switch SCADA inputs
  SW_F3_GEN_CTRL = "SW_F3_Gen_Ctrl"
  SW_F4_GEN_CTRL = "SW_F4_Gen_Ctrl"
  SW_F3_ESS_CTRL = "SW_F3_ESS_Ctrl"
  SW_F4_ESS_CTRL = "SW_F4_ESS_Ctrl"
  
  
  SW_CTRL_MAP = {
    "Off": 0,
    "On": 1
  }
  
  # Fault control SCADA inputs
  FAULT_CTRL = "Fault_Ctrl"
  
  FAULT_CTRL_MAP = {
    "None": 0,
    "A-B": 1,
    "A-C": 2,
    "A-B-C": 3
  }
  
  # Fault indicator output
  FAULT_INDICATOR = "Fault_Indicator"     # Fault active indicator
  FAULT_CTRL_VALUE = "Fault_Ctrl_Value"   # Fault control value
  
  # Data block names
  DATA_BLOCK_NAMES = [
    "Data_F3_Gen",
    "Data_F3L1_Gen",
    "Data_F3L1_ESS",
    "Data_F3_ESS",
    "Data_F4_Gen",
    "Data_F4L2_Gen",
    "Data_F4L2_ESS",
    "Data_F4_ESS"
  ]
    
  
  # Signals in a data block
  DATA_BLOCK_SIGNALS = [
    "Va_inst",
    "Vb_inst",
    "Vc_inst",
    "Ia_inst",
    "Ib_inst",
    "Ic_inst",
    "Sp",
    "Sn",
    "Sz",
    "f",
    "wt"
  ]
  
  def get_fault_value(fault):
    return RingbusModel.FAULT_CTRL_MAP[fault]
  
  def get_sw_ctrl_value(sw_ctrl):
    return RingbusModel.SW_CTRL_MAP[sw_ctrl]
  
  
  """
  Configure a TyphoonAutomator
  
  :param TyphoonAutomator automator: The automation to configure
  """  
  def configure_automator(automator: TyphoonAutomator):
    if automator is None:
      raise ValueError("Invalid automator")
    
    # Utility for creating a list of measurement block signal names
    get_data_block_signal_list = lambda prefix: list(map(lambda signal: prefix + "." + signal, RingbusModel.DATA_BLOCK_SIGNALS))
    
    # Set capture sample frequency
    automator.set_sample_frequency(RingbusModel.SAMPLE_FREQUENCY)
    # TODO: Sample frequency only affects capture rate. Streaming data rate is set in the model
    # TODO: Allow the streaming data rate to be modified
    
    # Add fault signals
    automator.add_streaming_signals([
      RingbusModel.FAULT_INDICATOR,
      RingbusModel.FAULT_CTRL_VALUE
    ])
    
    # Add signals from data blocks
    for data_block in RingbusModel.DATA_BLOCK_NAMES:
      signals = get_data_block_signal_list(data_block)
      automator.add_streaming_signals(signals)    
  
  
  """
  Default setup for all scenarios
  """
  def set_defaults(simulation: SimRunner):
    if simulation is None:
      raise ValueError("Invalid simulation")

    RingbusGenset.set_defaults(simulation)
    RingbusPV.set_defaults(simulation)
    RingbusESS.set_defaults(simulation)
    
    # Set fault type to no fault
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.FAULT_CTRL, RingbusModel.get_fault_value("None")))
    
    # Disconnect all loads
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3L1_CTRL, RingbusModel.get_sw_ctrl_value("Off")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3L2_CTRL, RingbusModel.get_sw_ctrl_value("Off")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4L1_CTRL, RingbusModel.get_sw_ctrl_value("Off")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4L2_CTRL, RingbusModel.get_sw_ctrl_value("Off")))
    
    # Close switches along feeders
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3L1_GEN_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3L1_ESS_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3L2_GEN_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3L2_ESS_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4L1_GEN_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4L1_ESS_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4L2_GEN_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4L2_ESS_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    
    # Close switches at ringbus corners
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3_GEN_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4_GEN_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F3_ESS_CTRL, RingbusModel.get_sw_ctrl_value("On")))
    simulation.invoke_event(SimEventSetScadaInput(RingbusModel.SW_F4_ESS_CTRL, RingbusModel.get_sw_ctrl_value("On")))
