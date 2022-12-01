::: mermaid
classDiagram
  class TyphoonAutomator {
    -Logger logger

    -HilSetupManager hil_setup
    -ModelManager model
    -Orchestrator orchestrator
    -Simulation simulation

    -str schematic_filename
    -str compiled_filename

    -list[str] data_log_signals
    -str data_log_filename

    -list[str] analog_capture_signals
    -list[str] digital_capture_signals
    -str capture_filename

    +initialize(str schematic, bool conditional_compile)

    +set_automation_logger(Logger logger)
    +log(str message, int level)
    +log_exception(BaseException ex)

    +get_available_devices(list~str~ serial_numbers) list~str~
    +connect_devices(list~str~ devices) list~tuple~
    +disconnect()
    +is_connected() bool

    +set_data_logger_filename(str filename)
    +add_data_logger_signals(list~str~ signals)
    +clear_data_logger_signals()

    +set_capture_filename(str filename)
    +add_analog_capture_signals(list~str~ signals)
    +add_digital_capture_signals(list~str~ signals)
    +clear_capture_signals()

    +add_scenario(str name, Scenario scenario)
    +clear_scenarios()
    +load_scenarios(str filename)
    +save_scenarios(str filename)

    +run(bool use_vhil)
    +shutdown()
  }

  TyphoonAutomator *-- HilSetupManager
  TyphoonAutomator *-- ModelManager
  TyphoonAutomator *-- Orchestrator
  TyphoonAutomator *-- Simulation

  class HilSetupManager {
    -TyphoonAutomator automator

    +get_available_devices(list~str~ serial_numbers) list~str~
    +connect_devices(list~str~ devices) list~tuple~
    +disconnect()
    +is_connected() bool
  }

  class ModelManager {
    -TyphoonAutomator automator

    +load_schematic(str filename, bool debug)
    +compile(bool conditional)
    +load_to_setup(bool use_vhil)

    +simtime_to_simstep(float time) int
    +simstep_to_simtime(int step) float

    +save_model_state(str filename)
    +load_model_state(str filename)

    +set_scada_value(str name, Any value)
    +set_model_variable(str name, Any value)
  }

  ModelManager -- Simulation

  class Orchestrator {
    -TyphoonAutomator automator
    -Simulation simulation

    +add_scenario(Scenario scenario)
    +run()
  }

  Orchestrator -- Simulation
  Orchestrator o-- "1..*" Scenario

  class Simulation {
    -TyphoonAutomator automator
    -ModelManager model
    -EventSchedule schedule

    +initialize(Scenario scenario)

    +schedule_event(float sim_time, SimEvent event)
    +invoke_event(SimEvent event)

    +start_simulation()
    +stop_simulation()
    +is_simulation_running() bool

    +get_simulation_time() float
    +get_simulation_step() int

    +start_capture()
    +stop_capture()
    +is_capture_in_progress() bool

    +start_data_logger()
    +stop_data_logger()

    +set_stop_signal()
    +clear_stop_signal()
    +get_stop_signal() bool
  }

  Simulation *-- EventSchedule
  Simulation -- SimEvent
  Simulation -- Scenario

  class EventSchedule {
    -list[SimEvent] event_list

    +add_event(float sim_time, SimEvent event)
    +clear_schedule()

    +get_event_count() int
    +has_next_event() bool
    +get_next_event_time() float
    
    +pop_next_event() SimEvent
  }

  EventSchedule o-- "0..*" SimEvent

  class SimEvent {
    <<interface>>
    +message
    +invoke()
  }

  class Scenario {
    <<interface>>
    +set_up_scenario(Simulation simulation)
    +tear_down_scenario(Simulation simulation)
  }
:::
