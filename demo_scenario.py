from src import typhoon_automator
import random

# Create an example scenario
class DemoScenario(object):
    SCADA_SWITCH_NAME = "Sw_ctrl"

    def __init__(
            self,
            duration: float):
        self._duration = duration

    def close_switch(simulation: typhoon_automator.Simulation):
        simulation.set_scada_value(name = DemoScenario.SCADA_SWITCH_NAME, value = 1)

    def open_switch(simulation: typhoon_automator.Simulation):
        simulation.set_scada_value(name = DemoScenario.SCADA_SWITCH_NAME, value = 0)

    def set_up_scenario(
            self,
            simulation: typhoon_automator.Simulation):
        """ Set up the demo scenaro
        """
        simulation.set_data_logging_signals([
            "I_ind",
            "V_cap"])

        simulation.set_capture_signals(
            analog_signals = [
                "I_ind",
                "V_cap"],
            digital_signals = [])

        # Create and schedule switch close and open events
        close_event = typhoon_automator.Utility.create_callback_event(
            message = "Closing switch",
            callback = DemoScenario.close_switch)
        close_time = random.uniform(0.0, self._duration / 2)

        open_event = typhoon_automator.Utility.create_callback_event(
            message = "Opening switch",
            callback = DemoScenario.open_switch)
        open_time = random.uniform(self._duration / 2, self._duration)

        simulation.schedule_event(close_time, close_event)
        simulation.schedule_event(open_time, open_event)

        # Schedule a 100 millisecond capture starting 50 milliseconds before the switch close
        simulation.schedule_capture(start_time = close_time - 0.05, duration = 0.1)

        # Set scenario duration
        simulation.set_scenario_duration(self._duration)

        # Initialize switch as open
        DemoScenario.open_switch(simulation)


    def tear_down_scenario(
            self,
            simulation: typhoon_automator.Simulation):
        pass
