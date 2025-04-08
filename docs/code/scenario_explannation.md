# Creating A Scenario

There is an example of a scenario [here](./../../demo_scenario.py). 

There are two required functions to be in a scenario class, set_up_scenario and tear_down_scenario.

These two methods can only have two parameters, self (the scenario class instance) and simulation which needs to be of type
typhoon_automator.Simulation.

The set_up_scenario function will be called when the automator runs the scenarios. This will run once before any events 
occur. This is also where any events you want to occur must be added. 

The tear_down_scenario function will be called after all events and captures in a scenario are completed. This allows you
do whatever needs to be done to safely shut down your current scenario.

The events that are created need to be created with a time at which they occur and a typhoon_automator.Utility.create_callback_event
which needs a message and a callback.  The callback should be a function within the scenario class that takes only a 
typhoon_automator.Simulation object into the function and returns nothing. 

These callback functions use the simulation.set_scada_value function to change the scada input to a set value. For example
closing a switch or changing a generator voltage. 

In your set_up_scenario you can also set initial parameters for you various generators, batteries, etc. These will ensure
that all your devices in the model have correct initial parameters. 

Additionally, during set_up_scenario you define the signals you want record throughout the scenario through the data
logger. You also define the signals that will be recorded during the capture. You can define both analog and digital signals
to record during the capture. 

You also schedule the capture during setup with a defined start time and a duration time. 

Finally, you must set the simulation duration in the set_up_scenario. If this is not set then the simulation will not run any
of the events at times after 0 seconds. 