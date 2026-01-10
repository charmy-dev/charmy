import typing
import weakref

from .const import ID


class AqInstanceCounterMeta(type):
    """
    AqInstanceCounterMeta
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._instances = weakref.WeakSet()

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)

        if type(instance) is cls:
            cls._instances.add(instance)

        return instance


class AqObject(metaclass=AqInstanceCounterMeta):
    """
    AqObject is this project`s basic class, can set and get attribute
    """

    objects: typing.Dict[str, typing.Any] = {}
    objects_sorted: typing.Dict[str, typing.Any] = {}

    def __init__(self, _id: ID = ID.AUTO):
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
            obj.new("name", "obj1")
            print(obj.get("name"))  # OUTPUT: obj1
            obj.set("name", "obj2")
            print(obj.get("name"))  # OUTPUT: obj2


            def set_func(value):
                print("User set value:", value)
                return "Hi" + value


            def get_func():
                print("User get value")


            obj.new("title", "", set_func=set_func, get_func=get_func)
            obj.set("title", "A")
            print(obj.get("title"))

        Parameters:
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

    def set(self, key: str, value) -> typing.Self:
        """Set attribute

        Parameters:
            key (str): attribute name
            value (typing.Any): attribute value

        Return:
            self
        """
        if key not in self._attributes:
            raise KeyError(key)
        if isinstance(self._attributes[key], list):
            if self._attributes[key][0] == "@custom":
                if self._attributes[key][2]:
                    _return = self._attributes[key][2](value)
                    if _return:
                        self._attributes[key][1] = _return
                    else:
                        self._attributes[key][1] = value
                else:
                    self._attributes[key][1] = value
                return self
        self._attributes[key] = value
        return self

    def get(self, key: str) -> typing.Any:
        """Get attribute by key

        Parameters:
            key (str): attribute name

        Return:
            the value corresponding to the key
        """
        if isinstance(self._attributes[key], list) and len(self._attributes[key]) > 0:
            if self._attributes[key][0] == "@custom":
                if self._attributes[key][3]:
                    _return = self._attributes[key][3]()
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

    def configure(self, **kwargs):
        for key, value in kwargs.items():
            self.set(key, value)

    config = configure

    def __setitem__(self, key: str, value: typing.Any):
        self.set(key, value)

    def __getitem__(self, key: str) -> typing.Any:
        return self.get(key)

    @property
    def attributes(self) -> typing.Dict[str, typing.Any]:
        """Return all attributes"""
        return self._attributes
