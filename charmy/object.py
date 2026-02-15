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
    """CharmyObject is this project's basic class, with features to set and get attribute."""

    objects: typing.Dict[str, typing.Any] = {}  # find by ID {1: OBJ1, 2: OBJ2}
    objects_sorted: typing.Dict[str, typing.Any] = (
        {}
    )  # find by class name {OBJ1: {1: OBJECT1, 2: OBJECT2}}

    def __init__(self, id_: ID | str = ID.AUTO):
        self._attributes: dict[
            str, typing.Any | list[str, typing.Any, typing.Callable | None, typing.Callable | None]
        ] = {}  # NOQA: Expected to be user-modifiable.
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
        """Return the lowered class name"""
        return self.__class__.__name__.lower()

    @property
    def instances(self):
        """Return all the class instances"""
        return self.objects_sorted[self.class_name]

    @property
    def instance_count(self):
        """Return the class instance count"""
        return len(self._instances)

    def new(
        self,
        key: str,
        default=None,
        *,
        set_func: typing.Callable | None = None,
        get_func: typing.Callable | None = None,
    ) -> typing.Self:
        """New attribute
        [Suggested: add `is_`~ as prefix if value is in type bool]

        Example
        -------
        .. code-block:: python

            from charmy import *

            obj = CharmyObject()
            obj.new("name", "obj1")
            print(obj.get("name"))  # OUTPUT: obj1
            obj.set("name", "obj2")
            print(obj.get("name"))  # OUTPUT: obj2


            def set_func(value):
                print("User set value:", value)
                return "Hello, " + value


            def get_func():
                return f"User get value: {obj.get('title', skip=True)}"


            obj.new("title", "default title", set_func=set_func, get_func=get_func)
            print(obj.get("title"))  # OUTPUT: default title
            obj.set("title", "A")  # OUTPUT: User set value: A
            print(obj.get("title"))  # User get value: Hello, A


        Args:
            key (str): attribute name
            default (typing.Any): default value
            set_func (typing.Callable): function to set
            get_func (typing.Callable): function to get

        Return:
            Self
        """
        if set_func or get_func:
            self._attributes[key] = ["@custom", default, set_func, get_func]
        else:
            self._attributes[key] = default
        return self

    def set(self, key: str, value, *, skip: bool = False) -> typing.Self:
        """Set attribute

        Args:
            key (str): attribute name
            value (typing.Any): attribute value
            skip (bool): skip custom set_func function

        Return:
            self
        """
        if key not in self._attributes:
            raise KeyError(key)
        if isinstance(self._attributes[key], list):
            if self._attributes[key][0] == "@custom":
                if self._attributes[key][2]:
                    if not skip:
                        _return = self._attributes[key][2](value)
                    else:
                        _return = None
                    if _return:
                        self._attributes[key][1] = _return
                    else:
                        self._attributes[key][1] = value
                else:
                    self._attributes[key][1] = value
                return self
        self._attributes[key] = value
        return self

    def get(self, key: str, *, skip: bool = False) -> typing.Any:
        """Get attribute by key

        Args:
            key (str): attribute name
            skip (bool): skip custom get_func function

        Return:
            the value corresponding to the key
        """

        # check is an available key
        if key not in self._attributes:
            raise KeyError(key)

        # check is a custom attribute
        if isinstance(self._attributes[key], list) and len(self._attributes[key]) > 0:
            if self._attributes[key][0] == "@custom":
                if self._attributes[key][3]:
                    if not skip:
                        _return = self._attributes[key][3]()
                    else:
                        _return = None

                    if _return:
                        return _return
                    else:
                        return self._attributes[key][1]
                else:
                    return self._attributes[key][1]
        return self._attributes[key]

    def get_obj(self, _id: str) -> typing.Any | None:
        """Get registered object by id. (If not found, return None)"""
        try:
            return self.objects[_id]
        except KeyError:
            return None

    find = get_obj

    def configure(self, **kwargs):
        """High level set attributes by keyword arguments."""
        for key, value in kwargs.items():
            self.set(key, value)

    config = configure

    def cget(self, key: str) -> typing.Any:
        """Low level get attribute by key"""
        return self.get(key)

    # region Item configuration

    def __setitem__(self, key: str, value: typing.Any):
        """Set attribute by key: obj["key"] = value"""
        self.set(key, value)

    def __getitem__(self, key: str) -> typing.Any:
        """Get attribute by key: obj["key"]"""
        return self.get(key)

    def __delitem__(self, key: str):
        """Delete attribute by key: obj["key"]"""
        del self._attributes[key]

    def __contains__(self, item: str) -> bool:
        return item in self._attributes

    # endregion

    @property
    def attributes(self) -> typing.Dict[str, typing.Any]:
        """Return all attributes"""
        return self._attributes

    def __str__(self) -> str:
        """Return all attributes in string"""
        return str(self._attributes)
