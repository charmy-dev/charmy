"""
Basic object class.
"""
from __future__ import annotations as _

import typing

import weakref

from .const import ID


# class InstanceCounterMeta(type):
#     """
#     InstanceCounterMeta
#     """

#     def __init__(cls, name, bases, attrs):
#         super().__init__(name, bases, attrs)
#         cls._instances = weakref.WeakSet()

#     def __call__(cls, *args, **kwargs):
#         instance = super().__call__(*args, **kwargs)

#         if type(instance) is cls:
#             cls._instances.add(instance)

#         return instance


class CharmyInstanceDestroyedError(Exception): ...


# region _InstancesList

_InstanceType = typing.TypeVar("_InstanceType", bound="CharmyObject")

class _InstancesList(typing.Generic[_InstanceType]):
    """Instances list of each CharmyObject subclass, with customized abilities."""

    def __init__(self):
        """To create a list that stores instances of CharmyObject or its subclasses.

        This is mainly for internal use, but you are welcomed to find any other usage of this. 
        Remember to tell me your idea via GitHub discussions of this project (if available).
        """
        super().__init_subclass__()
        self.instances: weakref.WeakSet[_InstanceType] = weakref.WeakSet()
        self.instances_by_id: weakref.WeakValueDictionary[str, _InstanceType] = \
            weakref.WeakValueDictionary()

    def append(self, item: _InstanceType) -> typing.Self:
        """Add an object to this list.

        :param item: The object to add
        """
        self.instances.add(item)
        self.instances_by_id[item.id] = item
        return self

    def __getitem__(self, id_: str) -> _InstanceType:
        """Get or find an object from this list.

        :param item: Either the index or the ID of the target object
        """
        instance: _InstanceType | None = self.instances_by_id[id_]
        if instance is None:
            raise CharmyInstanceDestroyedError("Trying to access a destroyed or inexisting object.")
        else:
            return instance

    def __iter__(self):
        """Iterate this list."""
        return iter(self.instances)

    def __contains__(self, item: str| CharmyObject) -> bool:
        """Check if a specific object available.

        :param item: Either the object itself or its ID
        """
        if isinstance(item, CharmyObject):
            return weakref.ref(item) in self.instances
        else:
            return item in self.instances_by_id.keys()

    def __len__(self) -> int:
        """Get the length of this list."""
        return len(self.instances)

# endregion

# region CharmyObject

class CharmyObject:
    """CharmyObject is this project's basic class.

    CharmyObject provides abilities of cumulating ID and set attributes.
    """

    # Find by class {Button: _InstancesList(), Rect: _InstancesList(), ...}
    objects_sorted: typing.ClassVar[typing.Dict[type[CharmyObject], _InstancesList]] = {}

    # Instances list
    instances: typing.ClassVar[_InstancesList[typing.Self]]

    def __init__(self, id_: typing.Optional[str] = None):
        """CharmyObject is this project's basic class.

        CharmyObject provides abilities of cumulating ID and set attributes.

        Args:
            id_ (str): Optional, ID for the object

        """

        if id_ is None:
            id_prefix = self.class_name
            id_ = id_prefix + str(self.instance_count)
        # if  any(id_ in cls_instances for cls_instances in CharmyObject.objects_sorted.values()):
        #     raise KeyError(id_)

        self.id: typing.Final[str] = id_  # Do not change after initialization

        # if self.class_name not in self.objects_sorted:
        #     self.objects_sorted[self.class_name] = {self.id: self}
        # else:
        #     self.objects_sorted[self.class_name][self.id] = self

        self.__class__.instances.append(self)

    def __init_subclass__(cls):
        """To initialize a CharmyObject subclass."""
        super().__init_subclass__()
        cls.instances = _InstancesList()
        cls.objects_sorted[cls] = cls.instances

    # region: Properties

    @property
    def class_name(self) -> str:
        """Returns class name."""
        return self.__class__.__name__

    @property
    def instance_count(self) -> int:
        """Returns the class instance count."""
        return len(self.__class__.instances)

    # endregion

    # region: Object search

    def get_obj(self, target_id: str, default=None) -> typing.Any | None:
        """Get registered object by id. (If not found, return default)"""
        for cls_instances in CharmyObject.objects_sorted.values():
            if target_id in cls_instances:
                return cls_instances[target_id]
        else:
            return default

    find = get_obj

    def set(self, name: str, value: typing.Any):
        """Set attributes in CharmyObject.

        Args:
            name: Name of the attribute to set
            value: Value to set
        """
        setattr(self, name, value)

    def get(self, name: str, default: typing.Any = None) -> typing.Any:
        """Get attributes in CharmyObject.

        Args:
            name: Name of the attribute to get
            default: Default value to return if attribute not found

        Returns:
            Value of the attribute

        """
        if name in self.__dict__:
            return self.__dict__[name]
        return default

    def config(self, **kwargs):
        """Batch set values of multiple attributes in CharmyObject by giving params.

        Args:
             **kwargs: Any configs to add
        """
        for name in kwargs.keys():
            setattr(self, name, kwargs[name])

    # region: __str__

    def __str__(self) -> str:
        """Happens when someone boring puts a Charmy stuff into str() or print()."""
        return str(f"CharmyObject[{self.id}]")

    # endregion
