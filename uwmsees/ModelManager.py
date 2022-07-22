import typhoon.api.hil as hil
import logging

from pathlib import Path

class ModelManager(object):
  def __init__(
      self,
      logger: logging.Logger = None):
    
    if logger is None:
      self.logger = logging.getLogger()
    else:
      self.logger = logger
      
      
  """
  Load a model into the current setup
  
  :param str filename: Full path to the compiled model file
  :param bool use_vhil: True if virtual HIL should be used, false otherwise
  :raises FileNotFoundError: The specified file does not exist
  """
  def load_model(
      self,
      filename: str,
      use_vhil = False):
    self.logger.info(f"Loading model from {filename}")
    
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
