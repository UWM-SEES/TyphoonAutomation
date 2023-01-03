:::mermaid
sequenceDiagram
  actor User
  participant Automator as TyphoonAutomator
  participant HIL as HilSetupManager
  participant Model as ModelManager
  participant Orchestrator as Orchestrator
  participant Simulation as Simulation
  participant Scenario as Scenario
  participant Schedule as EventSchedule

  User->>+Automator: get_available_devices
    Automator->>+HIL: get_available_devices
    HIL->>-Automator: Device serial numbers
  Automator->>-User: Device serial numbers


  User->>+Automator: connect_devices
    Automator->>+HIL: connect_devices
    HIL->>-Automator: Device serial numbers/names
  Automator->>-User: Device serial numbers/names

  User->>+Automator: initialize
    Automator->>+Model: load_schematic
    Model->>-Automator: {done}
    Automator->>+Model: compile
    Model->>-Automator: {done}
  Automator->>-User: {done}

  User->>+Automator: set_data_logger_filename
  Automator->>-User: {done}

  User->>+Automator: add_data_logger_signals
    Automator->>+Model: check_signal_names
    Model->>-Automator: OK/Not OK
  Automator->>-User: {done}

  User->>+Automator: set_capture_filename
  Automator->>-User: {done}

  User->>+Automator: add_analog_capture_signals
    Automator->>+Model: check_signal_names
    Model->>-Automator: OK/Not OK
  Automator->>-User: {done}

  User->>+Automator: add_digital_capture_signals
    Automator->>+Model: check_signal_names
    Model->>-Automator: OK/Not OK
  Automator->>-User: {done}

  loop Repeat for each scenario
    User->>+Automator: add_scenario
      Automator->>+Orchestrator: add_scenario
      Orchestrator->>-Automator: {done}
    Automator->>-User: {done}
  end
:::