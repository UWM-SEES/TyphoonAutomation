from typing import Any

class EventSchedule(object):
  """ Simulation event schedule
  
  Maintains a list of simulation events ordered by their schedule time
  """
  
  def __init__(self):
    self._event_list = []         # List of (time, event) tuples
    
  def add_event(
      self,
      sim_time: float,
      event: Any):
    """ Add an event to the simulation schedule
    
    Event objects must have an 'invoke' method and a 'message' attribute
    
    :param float sim_time: Simulation time at which to invoke the event
    :param event: Event to be invoked
    """
    if event is None:
      raise ValueError("Event cannot be None")
    
    # Check event attributes
    if not hasattr(event, "invoke"):
      raise ValueError("Event does not have an invoke method")
      
    if not callable(event.invoke):
      raise ValueError("Event invoke attribute is not callable")
      
    if not hasattr(event, "message"):
      raise ValueError("Event does not have a log message")
    
    # Add (time, event) tuple to list and keep list sorted by time
    self._event_list.append((sim_time, event))
    self._event_list.sort(key = lambda e: e[0])
    
  def clear_schedule(self):
    """ Clear the event schedule """
    self._event_list = []
    
  def get_event_count(self) -> int:
    """ Get the number of scheduled events
    
    :return Number of scheduled events
    :rtype int
    """
    return len(self._event_list)
  
  def has_next_event(self) -> bool:
    """ Check if there is a next event
    
    :return True if there is a next event, false if schedule is empty
    :rtype bool
    """
    return (len(self._event_list) > 0)
  
  def get_next_event_time(self) -> float:
    """ Get the time of the next scheduled event
    
    :return Simulation time of next scheduled event
    :rtype float
    :raises IndexError: There is no next event
    """
    if not self.has_next_event():
      raise IndexError("Event list is empty")
    
    # Return time of first tuple in list
    event = self._event_list[0]
    return event[0]
  
  def pop_next_event(self) -> Any:
    """ Get the next scheduled event
    
    The event will be removed from the schedule
    
    :return Next scheduled event
    :raises IndexError: There is no next event
    """
    if not self.has_next_event():
      raise IndexError("Event list is empty")
    
    # Pop first tuple from list and return event
    event = self._event_list.pop(0)
    return event[1]
