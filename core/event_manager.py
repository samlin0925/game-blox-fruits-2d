from collections import defaultdict

class EventManager:
    def __init__(self):
        self._listeners = defaultdict(list)

    def subscribe(self, event_type: str, callback):
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback):
        if callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)

    def emit(self, event_type: str, **kwargs):
        for cb in list(self._listeners[event_type]):
            cb(**kwargs)

event_manager = EventManager()
