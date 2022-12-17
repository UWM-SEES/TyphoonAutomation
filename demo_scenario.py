from src import typhoon_automator
import random

# Create an example scenario
class DemoScenario(object):
  def __init__(
      self,
      duration: float):
    self._duration = duration

  def print_message(simulation: typhoon_automator.Simulation):
    print(f"Example message at simulation step {simulation.get_simulation_step()}")

  def set_up_scenario(
      self,
      simulation: typhoon_automator.Simulation):
    """ Set up the demo scenaro
    """

    # Create and schedule a simple print event
    log_event = typhoon_automator.Utility.create_callback_event(
      message = "Print demo event",
      callback = DemoScenario.print_message)
    event_time = random.uniform(0.0, self._duration)

    simulation.schedule_event(event_time, log_event)

    simulation.set_scenario_duration(self._duration)

  def tear_down_scenario(
      self,
      simulation: typhoon_automator.Simulation):
    pass
