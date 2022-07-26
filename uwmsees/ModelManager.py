import typhoon.api.hil as hil
import typhoon.api.schematic_editor as schematic_editor
import logging

from pathlib import Path

class ModelManager(object):
  """
  ModelManager constructor
  
  The default schematic filename will be './{self.model_name}.tse'
  
  :param str model_name: Name of model
  """
  def __init__(
      self,
      model_name: str,
      logger: logging.Logger = None):
    
    if not model_name:
      raise ValueError("Invalid model name")
    
    self.model_name = model_name
    
    self.schematic_filename = str(f"./{self.model_name}.tse")
    
    self.schematic = schematic_editor.SchematicAPI()
    self.schematic_loaded = False
    
    self.model_timestep = None
    self.MAX_TIMESTEP = 20e-6
    
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
      
      
  def __del__(self):
    try:
      self.schematic.close_model()
    except:
      self.logger.critical("Exception thrown in ModelManager destructor")
      
      
  """
  Load the schematic
  
  :param str filename: Full path to the schematic file
  :param bool debug: Load the schematic for debug
  """
  def load_schematic(
      self,
      filename: str = None,
      debug: bool = False):
    
    if not filename:
      filename = self.get_schematic_filename()
    else:
      self.schematic_filename = filename
      
    self.logger.info(f"Loading schematic from file {filename}")
    
    # Ensure schematic file exists
    filepath = Path(filename)
    if not filepath.exists():
      raise FileNotFoundError(f"Schematic file does not exist: {filename}")
    
    # Load schematic
    self.schematic_loaded = False
    self.model_timestep = None
    if not self.schematic.load(
        filename = filename,
        debug = debug):
      raise RuntimeError(f"Failed to load schematic file ({filename}")
    
    # Get model timestep
    try:
      timestep = self.schematic.get_model_property_value("simulation_time_step")
      self.model_timestep = float(timestep)
    except:
      self.logger.error("Failed to read model timestep from schematic")
      raise

    # Check model timestep
    if (self.model_timestep <= 0.0) or (self.model_timestep > self.MAX_TIMESTEP):
      raise ValueError("Invalid model timestep")
    
    self.logger.info(f"Model timestep is {self.model_timestep}")
    self.schematic_loaded = True
      
  
  """
  Compile the schematic
  
  The schematic must have been loaded before calling this method
  
  Setting conditional_compile to False will always cause the model to compile
  Setting conditional_compile to True will cause the compilation to be skipped if the "model together with
  it's dependencies is unchanged" (per the Typhoon Schematic API documentation)
  
  :raises RuntimeError: A schematic has not been loaded
  :param bool conditional_compile: True if compile should occur conditionally, false if compile should always occur
  """    
  def compile_schematic(
      self,
      conditional_compile: bool = False):
    if not self.schematic_loaded:
      raise RuntimeError("Cannot compile, schematic has not been loaded")
    
    self.logger.info(f"Compiling schematic, conditional compile is {conditional_compile}")
    
    if not self.schematic.compile(conditional_compile = conditional_compile):
      raise RuntimeError("Failed to compile schematic")
    
    filename = self.get_compiled_model_filename()
    if not filename:
      raise RuntimeError("Falied to get compiled model filename")
    
    self.logger.info(f"Compiled model file is {filename}")
    
    
  """
  Get the schematic filename
  
  :returns Schematic filename
  :rtype str
  """
  def get_schematic_filename(self) -> str:
    return self.schematic_filename
  
  
  """
  Get the compiled model filename
  
  :raises RuntimeError: No schematic filename has been provided
  :returns Compiled model filename corresponding to the schematic filename
  :rtype str
  """
  def get_compiled_model_filename(self) -> str:
    if not self.schematic_filename:
      raise RuntimeError("No schematic filename provided, cannot get compiled model filename")
    
    return self.schematic.get_compiled_model_file(self.schematic_filename)
  
  
  """
  Get the model timestep
  
  :raises ValueError: Model timestep has not been propertly initialized
  :returns Model timestep
  :rtype float
  """
  def get_model_timestep(self) -> float:
    if self.model_timestep is None:
      raise ValueError("Invalid model timestep")
    
    return float(self.model_timestep)
  
  
  """
  Load a model into the current setup
  
  If a compiled model filename is not provided, the default filename will be used
  
  :param bool use_vhil: True if virtual HIL should be used, false otherwise
  :param str filename: Full path to the compiled model file
  :raises FileNotFoundError: The specified file does not exist
  """
  def load_model(
      self,
      use_vhil = False,
      filename: str = None):
    
    # Use own compiled filename if no overriding filename exists
    if not filename:
      filename = self.get_compiled_model_filename()

    # Check filename
    if not filename:
      raise RuntimeError("No compiled model filename")

    self.logger.info(f"Loading compiled model from {filename}")

    # Ensure compiled model file exists
    filepath = Path(filename)
    if not filepath.exists():
      raise FileNotFoundError(f"Compiled model file does not exist: {filename}")
    
    # Load model
    if not hil.load_model(
        file = filename,
        offlineMode = False,
        vhil_device = use_vhil):
      raise RuntimeError(f"Failed to load model from {filename}")
    
  
  """
  Save the current state of the model
  
  :param str filename: Name of file to save file state
  :raises ValueError: The filename is invalid
  """  
  def save_model_state(
      self,
      filename: str):
    if not str:
      raise ValueError("Filename is invalid")
    
    self.logger.info(f"Saving model state to {filename}")
    
    # Save model state
    if not hil.save_model_state(filename):
      raise RuntimeError("Failed to save model state")
  
  
  """
  Load the model from a previously saved state
  
  :param str filename: Name of file containing saved model state
  :raises ValueError: The filename is invalid
  :raises FileNotFoundError: The specified file could not be found
  """
  def load_model_from_savestate(
      self,
      filename: str):
    if not filename:
      raise ValueError("Filename is invalid")
    
    self.logger.info(f"Loading model state from {filename}")
    
    # Ensure saved model exists
    filepath = Path(filename)
    if not filepath.exists():
      raise FileNotFoundError(f"Savestate model file does not exist: {filename}")
    
    # Load model state
    if not hil.load_model_state(filename):
      raise RuntimeError(f"Failed to load model state")
