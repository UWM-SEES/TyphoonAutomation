
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
  User->>+Automator: run
    Automator->>+Model: load_to_setup
    Model->>-Automator: {done}

    Automator->>+Orchestrator: run
    loop For each scenario
      Orchestrator->>+Simulation: initialize
        Simulation->>+Scenario: set_up_scenario
        Scenario->>-Simulation: {done}
      Simulation->>-Orchestrator: {done}
        
      Orchestrator->>+Simulation: run
        loop Until stop signal or no events
          Simulation->>Simulation: get_stop_signal

          Simulation->>+Schedule: has_next_event
          Schedule->>-Simulation: Yes/No

          loop Until event is ready
            Simulation->>Simulation: get_simulation_time
            Simulation->>+Schedule: get_next_event_time
            Schedule->>-Simulation: Event time
          end

          Simulation->>+Schedule: get_next_event
          Schedule->>-Simulation: Event

          opt
            Simulation->>Model: set_scada_value
          end
          opt
            Simulation->>Model: set_model_variable
          end
          opt
            Simulation->>Simulation: set_stop_signal
          end
        end

        Simulation->>+Scenario: tear_down_scenario
        Scenario->>-Simulation: {done}
      Simulation->>-Orchestrator: {done}
    end
    Orchestrator->>-Automator: {done}

  Automator->>-User: {done}

  User->>+Automator: shutdown
    Automator->>+HIL: disconnect
    HIL->>-Automator: {done}
  Automator->>-User: {done}
:::