from src import typhoon_automator
import random

# Create an example scenario
class Load3Scenario(object):
    AtoB = "AB - Load3"
    BtoC = "BC - Load3"
    AtoC = "AC - Load3"
    AtoGnd = "AGND - Load3"
    BtoGnd = "BGND - Load3"
    CtoGnd = "CGND - Load3"

    def __init__(
            self,
            duration: float):
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
        simulation.set_scada_value("PV_in.V_ref", 480.0) \
        # Initialize switches as open
        simulation.set_contactor(Load3Scenario.AtoB, True, False)
        simulation.set_contactor(Load3Scenario.BtoC, True, False)
        simulation.set_contactor(Load3Scenario.AtoC, True, False)
        simulation.set_contactor(Load3Scenario.AtoGnd, True, False)
        simulation.set_contactor(Load3Scenario.BtoGnd, True, False)
        simulation.set_contactor(Load3Scenario.CtoGnd, True, False)

    def flip_switch(simulation: typhoon_automator.Simulation, swControl: bool, swState: bool):
        match int(simulation._fault):
            case 0: # No event
                pass
            case 1:  # Line to Line (A to B)
                simulation.set_contactor(Load3Scenario.AtoB, swControl, swState)
            case 2:  # Line to Line (B to C)
                simulation.set_contactor(Load3Scenario.BtoC, swControl, swState)
            case 3:  # Line to Line (A to C)
                simulation.set_contactor(Load3Scenario.AtoC, swControl, swState)
            case 4:  # Line to Ground (A to Gnd)
                simulation.set_contactor(Load3Scenario.AtoGnd, swControl, swState)
            case 5:  # Line to Ground (B to Gnd)
                simulation.set_contactor(Load3Scenario.BtoGnd, swControl, swState)
            case 6:  # Line to Ground (C to Gnd)
                simulation.set_contactor(Load3Scenario.CtoGnd, swControl, swState)
            case 7:  # Line to Line to Ground (A to B to Gnd)
                simulation.set_contactor(Load3Scenario.AtoB, swControl, swState)
                simulation.set_contactor(Load3Scenario.AtoGnd, swControl, swState)
            case 8:  # Line to Line to Ground (B to C to Gnd)
                simulation.set_contactor(Load3Scenario.BtoC, swControl, swState)
                simulation.set_contactor(Load3Scenario.BtoGnd, swControl, swState)
            case 9:  # Line to Line to Ground (A to C to Gnd)
                simulation.set_contactor(Load3Scenario.AtoC, swControl, swState)
                simulation.set_contactor(Load3Scenario.AtoGnd, swControl, swState)
            case 10:  # Three Line (A to B to C)
                simulation.set_contactor(Load3Scenario.AtoB, swControl, swState)
                simulation.set_contactor(Load3Scenario.BtoC, swControl, swState)
            case 11:  # Three Line to Ground (A to B to C to Gnd)
                simulation.set_contactor(Load3Scenario.AtoB, swControl, swState)
                simulation.set_contactor(Load3Scenario.BtoC, swControl, swState)
                simulation.set_contactor(Load3Scenario.CtoGnd, swControl, swState)

    def close_switch(simulation: typhoon_automator.Simulation):
        Load3Scenario.flip_switch(simulation,True,True)

    def open_switch(simulation: typhoon_automator.Simulation):
        Load3Scenario.flip_switch(simulation, True, False)

    def enable_batt(simulation: typhoon_automator.Simulation):
        simulation.set_scada_value(name="Batt_in.On", value=1.0)

    def disable_batt(simulation: typhoon_automator.Simulation):
        simulation.set_scada_value(name="Batt_in.On", value=0.0)

    def set_up_scenario(
            self,
            simulation: typhoon_automator.Simulation):
        """ Set up the Load3 scenaro
            First all necessary values are set up
        """
        Load3Scenario.beginning_values(simulation)
        signals = [
            "Battery inverter.Va",
            "Battery inverter.Vb",
            "Battery inverter.Vc",
            "Battery inverter.I_a",
            "Battery inverter.I_b",
            "Battery inverter.I_c"
        ]

        #simulation.set_data_logging_signals(signals)

        simulation.set_capture_signals(
            analog_signals = signals,
            digital_signals = [])

        CAPTURE_DURATION = 1.0/60.0

        # Create and schedule switch close and open events
        close_event = typhoon_automator.Utility.create_callback_event(
            message = f"Closing switches case {simulation._fault}",
            callback = Load3Scenario.close_switch)
        close_time = random.uniform(11, 14)

        open_event = typhoon_automator.Utility.create_callback_event(
            message = "Opening switch",
            callback = Load3Scenario.open_switch)
        #open_time = random.uniform(close_time+0.003, CAPTURE_DURATION+close_time)
        open_time = 15

        enable_event = typhoon_automator.Utility.create_callback_event(
            message="Turning Battery On",
            callback=Load3Scenario.enable_batt)
        enable_time = 3

        disable_event = typhoon_automator.Utility.create_callback_event(
            message="Turning Battery Off",
            callback=Load3Scenario.disable_batt)
        disable_time = 15

        simulation.schedule_event(close_time, close_event)
        simulation.schedule_event(open_time, open_event)
        # Turns the battery on
        simulation.schedule_event(enable_time, enable_event)
        # Turns the battery off
        simulation.schedule_event(disable_time, disable_event)

        simulation.schedule_capture(
            start_time = close_time - (CAPTURE_DURATION / 2),
            duration = CAPTURE_DURATION,
            decimation = 50)

        # Set scenario duration
        simulation.set_scenario_duration(self._duration)


    def tear_down_scenario(
            self,
            simulation: typhoon_automator.Simulation):
        pass
