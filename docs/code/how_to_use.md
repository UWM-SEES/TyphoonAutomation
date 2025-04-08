# Using The Typhoon Automator

This is a tool to run scenarios in Typhoon without having to use much of the Typhoon HIL API. The process attempts to be
as straightforward as possible.

The [demo.py](./../../demo.py) file is a nice basic overview of how to set up the automator, but I will also explain here.

First setup some kind of logging to set what the is happening within your code. If you want to use the logger from anything
during runtime from with your scenario use 
```
simulation.log(message:Str, level:int = logging.DEBUG)
```

Once your logging is setup you need to establish paths to where your .tse file is, where you want to store the capture,
and where you want to store the output of the data logger.

The capture is set by you to capture signals during a specific period of time during the simulation.

The data logger records all signals that you set from Typhoon during the entire scenario. These signals in Typhoon need to
connected to a streaming probe in order to be recorded properly.

Once all of this is set up follow the example in [demo.py](./../../demo.py) you need to set up automator, set the logger,
connect to the typhoon devices on your network which can be found by calling 
```
hil_devices = automator.get_available_devices()
```

Then you need to initialize the .tse file you want to run scenarios on. This takes the path to the .tse file and a second
argument, conditional compile. This will only compile the .tse file if it has changed since the last compiled version of the
.tse file was made. This can help speed up run time especially on larger models or older computers where compiling takes 
a significant amount of time.

After this you need to provide the automator with the data logging path and the capture path which will place .csv files once
the simulation is complete.

Once all of this is complete you are good to add scenarios to the automator. These can be very simple of quite complicated
depending on your needs. See [scenario explanner](./scenario_explannation.md) for information on how to create scenarios.

Each scenario added needs to have a different name and should be calling a class which acts as the scenario for the model.

Once all of your scenarios are added you are good to run the automator. It will go through all the scenarios provided and
once completed safely shutdown the model. You can load a different model into the automator or end the program. 