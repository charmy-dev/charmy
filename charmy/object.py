"""Basic object class."""

import typing
import weakref

from .const import ID


class InstanceCounterMeta(type):
    """
    InstanceCounterMeta
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._instances = weakref.WeakSet()

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)

        if type(instance) is cls:
            cls._instances.add(instance)

        return instance


class CharmyObject(metaclass=InstanceCounterMeta):
    """CharmyObject is this project's basic class.

    CharmyObject provides abilities of cummulating ID and set attributes.
    """

    objects: typing.Dict[str, typing.Any] = {}  # find by ID {1: OBJ1, 2: OBJ2}
    objects_sorted: typing.Dict[str, typing.Any] = (
        {}
    )  # find by class name {OBJ1: {1: OBJECT1, 2: OBJECT2}}

    def __init__(self, id_: ID | str = ID.AUTO):
        """CharmyObject is this project's basic class.

        CharmyObject provides abilities of cummulating ID and set attributes.

        Args:
            param (ID | str): Optional, ID for the object
        """

        self._attributes: dict[str, typing.Any | list] = {}  # NOQA: Expected to be user-modifiable.
        # self._attributes -> {key: value, key2: ["@custom", value, set_func, get_func]}
        # self._attributes[key] -> ["@custom", value, set_func, get_func] | value

        if id_ == ID.AUTO:
            _prefix = self.class_name
            id_ = _prefix + str(self.instance_count)
        if id_ in self.objects:
            raise KeyError(id_)
        if id_ != ID.NONE:
            self.objects[id_] = self
            self.id = id_

            if self.class_name not in self.objects_sorted:
                self.objects_sorted[self.class_name] = {self.id: self}
            else:
                self.objects_sorted[self.class_name][self.id] = self

    @property
    def class_name(self) -> str:
        """Returns the class name."""
        return self.__class__.__name__

    @property
    def instances(self):
        """Returns all the class instances."""
        return self.__class__.objects_sorted[self.class_name]

    @property
    def instance_count(self):
        """Returns the class instance count."""
        return len(self._instances)
    
    # region: Attributes set / unset
    
    def set(self, name: str, value: typing.Any):
        """Set the value of a specific attribute with giver name.
        
        :param name: Name of the attribute to set
        :param value: Value to set
        """
        self.__setattr__(name, value)
    
    def get(self, name: str):
        """Get the value of a specific attribute with given name.
        
        :param name: Name of the attribute to get
        """
        return self.__getattribute__(name)
    
    def config(self, **kwargs):
        """Batch set values of multiple attributes by giving params.
        
        :param **kwargs: Any configs to add
        """
        param_list: dict[str, typing.Any] = {**kwargs}
        for name in param_list.keys():
            self.set(name, param_list[name])
    
    def __setitem__(self, name: str, value: typing.Any):
        """Compatibility with set and get item.
        
        **To Charmy developers:** Rewrite all relating code to new set / get attr method **ASAP!!!**

        :param name: Name of attr to set
        :param value: Value to set
        """
        self.set(name, value)
    
    def __getitem__(self, name: str):
        """Compatibility with set and get item.
        
        **To Charmy developers:** Rewrite all relating code to new set / get attr method **ASAP!!!**

        :param name: Name of attr to get
        """
        return self.get(name)
    
    new = set # Compatibility for old interface

    # endregion

    # region: __str__

    def __str__(self) -> str:
        """Happens when someone boring puts a Charmy stuff into str() or print()."""
        return str(f"CharmyObject[{self.id}]")
