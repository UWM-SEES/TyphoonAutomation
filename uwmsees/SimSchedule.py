from .SimEvents.SimulationEvent import SimulationEvent

# TODO: Thread safety if SimRunner uses threading

class SimSchedule(object):
  def __init__(self):
    self.event_list = []
  
  
  """
  Add an event to the schedule
  
  :param float simulation_time: Simulation time at which to schedule the event
  :param SimulationEvent event: Simulation event to be invoked at the given time
  """  
  def add_event(
      self,
      simulation_time: float,
      event):
    if event is None:
      raise ValueError("Event cannot be None")
    
    # Add event and keep list sorted by ascending time
    self.event_list.append((simulation_time, event))
    self.event_list.sort(key = lambda e: e[0])
    
    
  """
  Remove all events from the event list
  """
  def clear_schedule(self):
    self.event_list = []
    
    
  """
  Get the number of scheduled events
  
  :return Number of scheduled events
  :rtype int
  """
  def get_event_count(self) -> int:
    return len(self.event_list)
  
  
  """
  Get the time of the next upcoming scheduled event
  
  :return Simulation time of next upcoming scheduled event
  :rtype float
  :raises IndexError: There is no next event
  """
  def next_event_time(self) -> float:
    if self.get_event_count() < 1:
      raise IndexError("Event list is empty")
    
    event = self.event_list[0]
    return event[0]
  
  
  """
  Get the next event in the event list. The event will be removed from the list
  
  :return The next event
  :rtype SimulationEvent
  :raises TypeError: The next object in the event list is invalid
  """
  def pop_next_event(self) -> SimulationEvent:
    if self.get_event_count() < 1:
      raise IndexError("Event list is empty")
    
    event = self.event_list.pop(0)
    if not issubclass(type(event[1]), SimulationEvent):
      raise TypeError(f"Invalid event type {type(event)}")
    
    return event[1]
