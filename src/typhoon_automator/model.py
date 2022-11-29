import typhoon.api.hil as hil
import typhoon.api.schematic_editor as schematic_editor
import logging

from pathlib import Path
from typing import Any

import math


class ModelManager(object):
    """ Model manager
    
    Management object for working with Typhoon schematics and compiled models
    """

    MAX_TIMESTEP: float = 20e-6     # Maximum acceptable timestep

    def __init__(
            self,
            automator):
        from .automator import TyphoonAutomator

        if automator is None:
            raise ValueError("Automator cannot be none")
            
        self._automator: TyphoonAutomator = automator

        self._schematic = schematic_editor.SchematicAPI()   # Schematic editor API

        self._schematic_filename: str = None    # Filename of schematic
        self._compiled_filename: str = None     # Filename of compiled model

        self._model_timestep: float = 0.0       # Simulation timestep

    def load_schematic(
            self,
            filename: str,
            debug: bool = False):
        if not filename:
            raise ValueError("Schematic filename cannot be empty")

        # Ensure schematic file exists
        filepath = Path(filename)
        if not filepath.exists():
            raise FileNotFoundError(f"Schematic file not found: {filename}")

        # Load schematic
        self._automator.log(f"Loading schematic from file {filename}")
        if not self._schematic.load(
                filename=filename,
                debug=debug):
            raise RuntimeError(f"Failed to load schematic ({filename})")

        # Get model timestep
        timestep = 0.0
        try:
            timestep = float(self._schematic.get_model_property_value("simulation_time_step"))
        except:
            self._automator.log(
                "Failed to read model timestep from schematic",
                logging.ERROR)
            raise

        if (timestep <= 0.0) or (timestep > ModelManager.MAX_TIMESTEP):
            raise ValueError(f"Invalid model timestep ({timestep})")

        self._automator.log(f"Model timestep is {timestep}")

        self._schematic_filename = filename
        self._model_timestep = float(timestep)

    def compile(
            self,
            conditional: bool = True):
        """ Compile the schematic
        
        :param bool conditional: True if compile should occur conditionally, false if
        compile should always occur
        """
        if not self._schematic_filename:
            raise RuntimeError("No schematic specified, cannot compile")

        # Compile schematic
        self._automator.log(f"Compiling, conditional compile is {conditional}")
        if not self._schematic.compile(conditional):
            raise RuntimeError("Failed to compile")

        # Get compiled model filename
        filename = self._schematic.get_compiled_model_file(self._schematic_filename)
        if not filename:
            raise RuntimeError("Failed to get compiled model filename")

        self._compiled_filename = filename
        self._automator.log(f"Compiled model filename is {self._compiled_filename}")

    def load_to_setup(
            self,
            use_vhil: bool = False):
        """ Load the compiled model to the HIL setup
        
        :param bool use_vhil: True if Virtual HIL should be used, false otherwise
        """
        if not self._compiled_filename:
            raise RuntimeError("No compiled model filename, cannot load")

        # Ensure compiled model file exists
        filepath = Path(self._compiled_filename)
        if not filepath.exists():
            raise FileNotFoundError(f"Compiled model file not found: {self._compiled_filename}")

        # Load model to HIL setup
        if not hil.load_model(
                file=self._compiled_filename,
                offlineMode=False,
                vhil_device=use_vhil):
            raise RuntimeError(f"Failed to load compiled model to setup ({self._compiled_filename})")

    def simtime_to_simstep(
            self,
            time: float) -> int:
        """ Convert a simulation time value to a simulation step value
        
        :param float time: Simulation time to convert
        :returns Simulation step corresponding to the given time
        :rtype int
        :raises ValueError: A configuration value is invalid
        """
        if math.isclose(self._model_timestep, 0.0) or self._model_timestep > ModelManager.MAX_TIMESTEP:
          raise ValueError(f"Invalid model timestep ({self.model_timestep})") #this is handled in load_schematic-- should I also check it here?
        
        return int(time / self._model_timestep)

    def simstep_to_simtime(
            self,
            step: int) -> float:
        """ Convert a simulation step value into a simulation time value
        
        :param int step: Simulation step to convert
        :returns Simulation time corresponding to the given step
        :rtype int
        :raises ValueError: A configuration value is invalid
        """
        if math.isclose(self._model_timestep, 0.0) or self._model_timestep > ModelManager.MAX_TIMESTEP::
          raise ValueError(f"Invalid model timestep ({self.model_timestep})")
    
        return float(step * self._model_timestep)

    def save_model_state(
            self,
            filename: str):
        """ Save the current state of the model
        
        :param str filename: Name of file to save file state
        """
        if not filename:
            raise ValueError("File name cannot be empty")

        # Save model state
        self._automator.log(f"Saving model state to {filename}")
        if not hil.save_model_state(filename):
            raise RuntimeError("Failed to save model state")

    def load_model_state(
            self,
            filename: str):
        """ Load the model from a previously saved state
        
        :param str filename: Name of file containing saved model state
        """
        if not filename:
            raise ValueError("File name cannot be empty")

        # Ensure file exists
        filepath = Path(filename)
        if not filepath.exists():
            raise FileNotFoundError(f"Saved model file does not exist ({filename})")

        # Load model state
        self._automator.log(f"Loading model state from {filename}")
        if not hil.load_model_state(filename):
            raise RuntimeError("Failed to load model state")

    def set_scada_value(
            self,
            name: str,
            value: Any):
        raise NotImplementedError()

    def set_model_variable(
            self,
            name: str,
            value: Any):
        raise NotImplementedError()

    def get_scada_value(
            self,
            name: str) -> Any:
        # TODO: Add this to documentation
        raise NotImplementedError()

    def get_model_variable(
            self,
            name: str) -> Any:
        # TODO: Add this to documentation
        raise NotImplementedError()
