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
            id_ (ID | str): Optional, ID for the object

        """

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

    # region: Properties

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
    
    # endregion

    # region: Object search

    def get_obj(self, id_: str, default=None) -> typing.Any | None:
        """Get registered object by id. (If not found, return default)"""
        if id_ in self.objects:
            return self.objects[id_]
        return default

    find = get_obj

    # endregion

    # region: __str__

    def __str__(self) -> str:
        """Happens when someone boring puts a Charmy stuff into str() or print()."""
        return self.id

    # endregion