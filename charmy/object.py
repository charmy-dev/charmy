import typing
import weakref

from .const import ID


class CInstanceCounterMeta(type):
    """
    CInstanceCounterMeta
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._instances = weakref.WeakSet()

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)

        if type(instance) is cls:
            cls._instances.add(instance)

        return instance


class CObject(metaclass=CInstanceCounterMeta):
    """
    CObject is this project's basic class, can set and get attribute
    """

    objects: typing.Dict[str, typing.Any] = {}  # find by ID {1: OBJ1, 2: OBJ2}
    objects_sorted: typing.Dict[str, typing.Any] = (
        {}
    )  # find by class name {OBJ1: {1: OBJECT1, 2: OBJECT2}}

    def __init__(self, _id: ID | str = ID.AUTO):
        self._attributes = {}

        if _id == ID.AUTO:
            _prefix = self.class_name
            _id = _prefix + str(self.instance_count)
        if _id in self.objects:
            raise KeyError(_id)
        if _id != ID.NONE:
            self.objects[_id] = self
            self.new("id", _id)

            if self.class_name not in self.objects_sorted:
                self.objects_sorted[self.class_name] = {self.get("id"): self}
            else:
                self.objects_sorted[self.class_name][self.get("id")] = self

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
        set_func: typing.Callable = None,
        get_func: typing.Callable = None,
    ) -> typing.Self:
        """New attribute
        【推荐如果值为布尔值，则键名前加`is_`】

        Example
        -------
        .. code-block:: python
            from charmy import *

            obj = CObject()
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

        # self._attributes[key] -> ["@custom", value, set_func, get_func] | value

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

    def get_obj(self, _id: str) -> object | None:
        """Get registered object by id"""
        try:
            return self.objects[_id]
        except KeyError:
            return None

    find = get_obj

    def configure(self, **kwargs):
        """High level set attributes by keyword arguments"""
        for key, value in kwargs.items():
            self.set(key, value)

    config = configure

    def cget(self, key: str) -> typing.Any:
        """Low level get attribute by key"""
        return self.get(key)

    def __setitem__(self, key: str, value: typing.Any):
        """You can set attribute by key: obj["key"] = value"""
        self.set(key, value)

    def __getitem__(self, key: str) -> typing.Any:
        """You can get attribute by key: obj["key"]"""
        return self.get(key)

    @property
    def attributes(self) -> typing.Dict[str, typing.Any]:
        """Return all attributes"""
        return self._attributes

    def __str__(self) -> str:
        """Return all attributes in string"""
        return str(self._attributes)
