import logging

from numpy.f2py.auxfuncs import throw_error

from src import typhoon_automator
import random

# Create an example scenario
class SimScenario(object):

    def __init__(self, duration: float):
        self._duration = duration


    def beginning_values(simulation: typhoon_automator.Simulation):
        # Battery initial values
        simulation.set_scada_value("Batt_in.Pref", -200000.0)
        # Battery starts off
        simulation.set_scada_value("Batt_in.On", 0.0)
        simulation.set_scada_value("Batt_in.Qref", 0.0)
        simulation.set_scada_value("Batt_in.Vref", 480.0)
        simulation.set_scada_value("Batt_in.f_ref", 60.0)
        simulation.set_scada_value("Batt_in.mode", 1.0)
        # Generator initial values
        simulation.set_scada_value("DG_in1.Gen_On", 1.0)
        simulation.set_scada_value("DG_in1.Gen_OP_mode", 2.0)
        simulation.set_scada_value("DG_in1.Gen_Control_Mode", 0.0)
        simulation.set_scada_value("DG_in1.Load_share", 0.0)
        simulation.set_scada_value("DG_in1.Load_share_on", 0.0)
        simulation.set_scada_value("DG_in1.Pref", 0.0000096)
        simulation.set_scada_value("DG_in1.pf_ref", 1.0)
        simulation.set_scada_value("DG_in1.wref", 1.0)
        simulation.set_scada_value("DG_in1.Vref", 1.0)
        # PV initial values
        simulation.set_scada_value("PV_in.Connect", 0.0)
        simulation.set_scada_value("PV_in.Enable", 0.0)
        simulation.set_scada_value("PV_in.Irradiation", 200.0)
        simulation.set_scada_value("PV_in.Q_mode", 1.0)
        simulation.set_scada_value("PV_in.Q_ref", 0.0)
        simulation.set_scada_value("PV_in.V_ref", 480.0)
        # Initialize fault events as no event
        simulation.set_scada_value("Load1 Fault", 0.0)
        simulation.set_scada_value("Load2 Fault", 0.0)
        simulation.set_scada_value("Load3 Fault", 0.0)
        simulation.set_scada_value("Generator Fault", 0.0)
        simulation.set_scada_value("Bus Fault", 0.0)
        simulation.log(f"Simulation initial values set", logging.DEBUG)

    def close_switch(simulation: typhoon_automator.Simulation):
        file_name = simulation.get_capture_name()
        simulation.log(f"Testing {file_name}", logging.DEBUG)
        extension = file_name.split(" Scenario")[0].split("_")[1]
        simulation.log(f"Testing 1 {extension}", logging.DEBUG)
        fault = int(file_name.split("Fault ")[1].split(".")[0])
        simulation.log(f"Closing {fault} Fault for {extension}", logging.DEBUG)
        match extension:
            case "Load 1":
                simulation.set_scada_value("Load1 Fault", fault)
            case "Load 2":
                simulation.set_scada_value("Load2 Fault", fault)
            case "Load 3":
                simulation.set_scada_value("Load3 Fault", fault)
            case "Generator":
                simulation.set_scada_value("Generator Fault", fault)
            case "Bus":
                simulation.set_scada_value("Bus Fault", fault)
            case _:
                raise ValueError("Provided fault case that no exist")

    def open_switch(simulation: typhoon_automator.Simulation):
        file_name = simulation.get_capture_name()
        simulation.log(f"Testing {file_name}", logging.DEBUG)
        extension = file_name.split(" Scenario")[0].split("_")[1]
        simulation.log(f"Closing closing fault switch for {extension}", logging.DEBUG)
        match extension:
            case "Load 1":
                simulation.set_scada_value("Load1 Fault", 0.0)
            case "Load 2":
                simulation.set_scada_value("Load2 Fault", 0.0)
            case "Load 3":
                simulation.set_scada_value("Load3 Fault", 0.0)
            case "Generator":
                simulation.set_scada_value("Generator Fault", 0.0)
            case "Bus":
                simulation.set_scada_value("Bus Fault", 0.0)
            case _:
                raise ValueError("Provided fault case that no exist")

    def enable_batt(simulation: typhoon_automator.Simulation):
        simulation.set_scada_value(name="Batt_in.On", value=1.0)
        simulation.log(f"Enabled batt", logging.DEBUG)

    def disable_batt(simulation: typhoon_automator.Simulation):
        simulation.set_scada_value(name="Batt_in.On", value=0.0)
        simulation.log(f"Disabled batt", logging.DEBUG)

    def set_up_scenario(
            self,
            simulation: typhoon_automator.Simulation):
        """ Set up the load1 scenaro
            First all necessary values are set up
        """
        SimScenario.beginning_values(simulation)
        asignals = [
            "Battery inverter.Grid meas.Va",
            "Battery inverter.Grid meas.Vb",
            "Battery inverter.Grid meas.Vc",
            "Battery inverter.Ia",
            "Battery inverter.Ib",
            "Battery inverter.Ic",
            "Battery inverter.Converter meas.Va",
            "Battery inverter.Converter meas.Vb",
            "Battery inverter.Converter meas.Vc",
            "Battery inverter.Ia_out",
            "Battery inverter.Ib_out",
            "Battery inverter.Ic_out",

        ]

        # simulation.set_data_logging_signals(signals)

        simulation.set_capture_signals(
            analog_signals = asignals,
            digital_signals = ["FaultTriggered"])

        CAPTURE_DURATION = 1.0/60.0
        simulation.log(f"Simulation initial values are signals set", logging.DEBUG)
        # Create and schedule switch close and open events
        close_event = typhoon_automator.Utility.create_callback_event(
            message = f"Fault Event",
            callback = SimScenario.close_switch)
        close_time = random.uniform(13, 14)
        simulation.log(f"Closing switch at {close_time}", logging.DEBUG)

        open_event = typhoon_automator.Utility.create_callback_event(
            message = "Opening switch",
            callback = SimScenario.open_switch)
        open_time = 14.5

        enable_event = typhoon_automator.Utility.create_callback_event(
            message="Turning Battery On",
            callback=SimScenario.enable_batt)
        enable_time = 1

        disable_event = typhoon_automator.Utility.create_callback_event(
            message="Turning Battery Off",
            callback=SimScenario.disable_batt)
        disable_time = open_time + 0.01

        simulation.schedule_event(close_time, close_event)
        simulation.schedule_event(open_time, open_event)
        # Turns the battery on
        simulation.schedule_event(enable_time, enable_event)
        # Turns the battery off
        simulation.schedule_event(disable_time, disable_event)

        simulation.schedule_capture(
            start_time = close_time - (0.75 * CAPTURE_DURATION),
            duration = CAPTURE_DURATION,
            decimation = 34)

        # Set scenario duration
        simulation.set_scenario_duration(self._duration)


    def tear_down_scenario(
            self,
            simulation: typhoon_automator.Simulation):
        pass
