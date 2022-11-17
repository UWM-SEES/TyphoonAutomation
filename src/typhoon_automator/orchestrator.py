from typing import Any

from .simulation import Simulation


# TODO: Class diagram documentation for this is incomplete
class Orchestrator(object):
    """ Simulation orchestrator
    
    Organizes and runs simulation scenarios
    """

    def __init__(
            self,
            automator):
        from .automator import TyphoonAutomator

        if automator is None:
            raise ValueError("Automator cannot be none")
            
        self._automator: TyphoonAutomator = automator

        # TODO: Consider creating a factory function to address this Simulation dependency
        self._model = self._automator._simulation

        self._scenarios: list[Any] = []

    def add_scenario(
            self,
            scenario: Any):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()
