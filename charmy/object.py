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
        self.instances: list[weakref.ReferenceType[_InstanceType]] = []
        self.instances_by_id: weakref.WeakValueDictionary[str, _InstanceType] = \
            weakref.WeakValueDictionary()

    def append(self, item: _InstanceType) -> typing.Self:
        """Add an object to this list.

        :param item: The object to add
        """
        self.instances.append(weakref.ref(item))
        self.instances_by_id[item.id] = item
        return self

    def __getitem__(self, item: int | str) -> _InstanceType:
        """Get or find an object from this list.

        :param item: Either the index or the ID of the target object
        """
        instance: _InstanceType | None = None
        if isinstance(item, int):
            # int expressing an index
            if item < len(self.instances):
                ref: weakref.ReferenceType = self.instances[item]
                instance: _InstanceType | None = ref()
        else:
            # str expressing an ID
            if item in self.instances_by_id:
                instance: _InstanceType | None = None
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

    # objects: typing.Dict[str, CharmyObject] = {}  # find by ID {1: OBJ1, 2: OBJ2}
    objects_sorted: typing.ClassVar[typing.Dict[str, dict[str, CharmyObject]]] = (
        {}
    )  # find by class name {OBJ1: {1: OBJECT1, 2: OBJECT2}}

    instances: typing.ClassVar[_InstancesList[typing.Self]]

    def __init__(self, id_: ID | str = ID.AUTO):
        """CharmyObject is this project's basic class.

        CharmyObject provides abilities of cumulating ID and set attributes.

        Args:
            id_ (ID | str): Optional, ID for the object

        """

        # self._attributes -> {key: value, key2: ["@custom", value, set_func, get_func]}
        # self._attributes[key] -> ["@custom", value, set_func, get_func] | value

        self._custom: typing.Dict[str, typing.Any] = {}  # Private custom attributes

        if id_ == ID.AUTO:
            id_prefix = self.class_name
            id_ = id_prefix + str(self.instance_count)
        if  any(id_ in cls_instances for cls_instances in CharmyObject.objects_sorted.values()):
            raise KeyError(id_)
        if id_ != ID.NONE:
            self.id: typing.Final[str] = id_  # Do not change after initialization

            if self.class_name not in self.objects_sorted:
                self.objects_sorted[self.class_name] = {self.id: self}
            else:
                self.objects_sorted[self.class_name][self.id] = self

            self.__class__.instances.append(self)

    def __init_subclass__(cls):
        """To initialize a CharmyObject subclass."""
        cls.instances = _InstancesList()

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
            if target_id in cls_instances.keys():
                return cls_instances[target_id]
        else:
            return default

    find = get_obj


    # endregion

    # ? @XiangQinxi I told u to forget these fucking mechanisms?
    #
    # # region: Shared attributes set / get

    # def cset(self, name: str, value: typing.Any):
    #     """Set shared attributes in CharmyObject.

    #     Args:
    #         name: Name of the attribute to set
    #         value: Value to set
    #     """
    #     self.attributes[name] = value

    # def cget(self, name: str, default: typing.Any = None) -> typing.Any:
    #     """Get shared attributes in CharmyObject.

    #     Args:
    #         name: Name of the attribute to get
    #         default: Default value to return if attribute not found

    #     Returns:
    #         Value of the attribute

    #     """
    #     if name in self.attributes:
    #         return self.attributes[name]
    #     return default

    # def cconfig(self, **kwargs):
    #     """Batch set values of multiple shared attributes in CharmyObject by giving params.

    #     Args:
    #          **kwargs: Any configs to add
    #     """
    #     for name in kwargs.keys():
    #         self.cset(name, kwargs[name])

    # # endregion

    def set(self, name: str, value: typing.Any):
        """Set attributes in CharmyObject.

        Args:
            name: Name of the attribute to set
            value: Value to set
        """
        self.__dict__[name] = value

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
            self.set(name, kwargs[name])

    # region: __str__

    def __str__(self) -> str:
        """Happens when someone boring puts a Charmy stuff into str() or print()."""
        return str(f"CharmyObject[{self.id}]")

    # endregion
