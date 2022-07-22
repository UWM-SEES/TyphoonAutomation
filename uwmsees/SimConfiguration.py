import math

# TODO: Add a way to load/save configuration files

class SimConfiguration(object):
  def __init__(self):
    
    self.model_timestep = 0.0
    self.sample_frequency = 0.0
    
    self.analog_capture_signals = []
    self.digital_capture_signals = []
    self.capture_start_time = 0.0
    self.capture_duration = 0.0
    self.capture_filename = ""
    self.capture_stop_timeout = 0.0
      
      
  """
  Convert a simulation time to the corresponding simulation step number
  
  :param float simulation_time: Simulation time in seconds
  :returns Step number corresponding to the given simulation time
  :rtype int
  :raises ValueError: A configuration value is invalid
  """
  def simtime_to_simstep(
      self,
      simulation_time: float):
    if math.isclose(self.model_timestep, 0.0):
      raise ValueError(f"Invalid model timestep ({self.model_timestep})")
    
    return int(simulation_time / self.model_timestep)
  
  
  """
  Convert a simulation step number to the corresponding simulation time
  
  :param float simulation_step: Simulation step number
  :returns Simulation time in seconds corresponding to the given step number
  :rtype float
  :raises ValueError: A configuration value is invalid
  """
  def simstep_to_simtime(
      self,
      simulation_step: float):
    if math.isclose(self.model_timestep, 0.0):
      raise ValueError(f"Invalid model timestep ({self.model_timestep})")
    
    return float(simulation_step * self.model_timestep)
  
  
  """
  Add a list of analog signals to be captured
  
  :param list signals: List of names of analog signals to be captured
  """
  def add_analog_capture(
      self,
      signals: list):
    if signals is not None:
      self.analog_capture_signals.extend(signals)
      
  """
  Clear the analog signal capture list
  """
  def clear_analog_capture(self):
    self.analog_capture_signals = []
      
      
  """
  Add a list of digital signals to be captured
  
  :param list signals: List of names of digital signals to be captured
  """
  def add_digital_capture(
      self,
      signals: list):
    if signals is not None:
      self.digital_capture_signals.extend(signals)
      
      
  """
  Clear the digital signal capture list
  """
  def clear_digital_capture(self):
    self.digital_capture_signals = []
      
      
  """
  Set the model timestep
  
  :param float timestep: Model timestep
  :raises ValueError: The given timestep is invalid
  """
  def set_model_timestep(
      self,
      timestep: float):
    if (timestep < 0.0) or (math.isclose(timestep, 0.0)):
      raise ValueError(f"Invalid timestep ({timestep})")
    
    self.model_timestep = timestep
    
    
  """
  Set the sample frequency

  :param float frequency: Sample frequency
  :raises ValueError: The given sample frequency is invalid
  """
  def set_sample_frequency(
      self,
      frequency: float):
    if (frequency < 0.0) or (math.isclose(frequency, 0.0)):
      raise ValueError(f"Invalid sample frequency ({frequency})")
    
    self.sample_frequency = frequency
    
    
  """
  Set the capture start time

  :param float start_time: Capture start time
  :raises ValueError: The given capture duration is invalid
  """
  def set_capture_start_time(
      self,
      start_time: float):
    if start_time < 0.0:
      raise ValueError(f"Invalid capture start time ({start_time})")
    
    self.capture_start_time = start_time
    
    
  """
  Set the capture duration

  :param float duration: Capture duration
  :raises ValueError: The given capture duration is invalid
  """
  def set_capture_duration(
      self,
      duration: float):
    if (duration < 0.0) or (math.isclose(duration, 0.0)):
      raise ValueError(f"Invalid capture duration ({duration})")
    
    self.capture_duration = duration


  """
  Set the capture output file name

  :param str filename: Full path to capture output file
  :raises ValueError: The file name is invalid
  """
  def set_capture_filename(
      self,
      filename: str):
    if not filename:
      raise ValueError(f"Invalid capture filename ({filename})")
    
    self.capture_filename = filename
    
    
  """
  Set the capture output stop timeout

  :param float timeout: Capture stop timeout in seconds
  :raises ValueError: The timeout is invalid
  """
  def set_capture_stop_timeout(
      self,
      timeout: float):
    if timeout < 0.0:
      raise ValueError(f"Invalid capture stop timeout ({timeout})")
    
    self.capture_stop_timeout = timeout
