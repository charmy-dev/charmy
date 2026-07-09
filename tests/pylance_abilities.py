from charmy import CharmyObject, EventHandling
import reactive_caching

class Widget(CharmyObject, EventHandling, reactive_caching.CachedClass):
    pass