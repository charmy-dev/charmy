"""This module contains all ability of a container to manage layouts."""

from __future__ import annotations as _

import typing

from abc import abstractmethod
import reactive_caching

from ..utils import layout_profiles # Expose them as (...).container.layout_profiles
from ..utils import type_checking, var
from ..styles import shape, texture
from .. import cm_object

if typing.TYPE_CHECKING:
    from . import widget

__all__ = ["Container", "layout_profiles"]


class Container(reactive_caching.CachedClass):
    """Container represents a widget's ability to contain and arrange other widgets inside.

    The `Container` class contains the ability of managing widgets within the container, and should 
    be inherited by all types of containers including windows, frames, etc., but not supposed to be 
    instantiated directly.
    """

    _with_stack: typing.ClassVar[list[Container]] = [] # Used to store embedding stack in with as

    def __init__(self, 
            managed_layout_type: type[layout_profiles.ManagedLayout] | str = \
                layout_profiles.LinearLayout, 
            flex_direction: typing.Literal[0, 1] = 1, 
            *args, **kwargs):
        """Initialize a container base class.

        The container base class is not supposed to be instantiated directly, make sure you are 
        executing this method during subclassing.
        """
        super().__init__(*args, **kwargs)

        if type(managed_layout_type) is str:
            # Search for subclasses of managed layout base class to convert string param to class
            for subclass in layout_profiles.ManagedLayout.__subclasses__():
                if subclass.type == managed_layout_type:
                    managed_layout_type = subclass
                    break
            else:
                raise ValueError(
                    "Specified invalid managed layout type name "
                    f"'{managed_layout_type}' for container"
                    )
        managed_layout_type = typing.cast(type[layout_profiles.ManagedLayout], managed_layout_type)

        self.children: list[widget.Widget] = []
        self._flex_dist: dict[widget.Widget, int] = {}

        self.background: texture.Texture | texture.TextureLike
        # TODO: Change this⬆️ to let it only be specified with profiles, in specific widgets
        self.managed_layout_type: type[layout_profiles.ManagedLayout] = managed_layout_type
        self.flex_direction: typing.Literal[0, 1] = flex_direction

    @reactive_caching.cached_property(["children", "background"])
    def layers(self) -> \
        tuple[texture.Texture | texture.TextureLike, list[widget.Widget], list[widget.Widget]]:
        place_list = []
        managed_list = []
        for child in self.children:
            if isinstance(child.layout_profile, layout_profiles.ManagedLayout):
                managed_list.append(child)
            else:
                place_list.append(child)
        return (self.background, managed_list, place_list)

    @property
    @abstractmethod
    def pos(self) -> shape.Point: ...

    @property
    @abstractmethod
    def abs_pos(self) -> shape.Point: ...

    @property
    @abstractmethod
    def size(self) -> shape.Size: ...

    # region Context

    def __enter__(self) -> typing.Self:
        """Enter the context."""
        Container._with_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> typing.Literal[False]:
        """Exit the context."""
        Container._with_stack.pop()
        return False # Does not handle exceptions

    # endregion

    def add_child(self, child: widget.Widget) -> typing.Self:
        """Add a child object.

        Note
        ----
        The child list is **rebound** rather than mutated in place on purpose. The `layers` 
        cached property is only invalidated through `__setattr__`, so an in-place `append()` would 
        leave the cache stale and the newly added child would never be drawn.
        """
        if child not in self.children:
            self.children = [*self.children, child]
        return self

    def remove_child(self, child: widget.Widget) -> typing.Self:
        """Remove a child object, so that it is no longer drawn or hit-tested.

        This seem like a vibed function, and I cannot ensure its source.  —— rgzz666
        """
        if child in self.children:
            # Identity comparison: never drop a merely "equal" sibling object
            self.children = [sibling for sibling in self.children if sibling is not child]
        return self

    def update_layout(self):
        """Update layout results."""

        def get_widget_sizes(the_widget: widget.Widget) -> tuple[shape.Size, shape.Size, shape.Size]:
            full_profile = the_widget.migrate_full_curr_profile()
            wanted_size = \
                var.unpack_var(typing.cast(var.VarOrVal[shape.Size], full_profile.size), (0, 0))
            min_size = var.unpack_var(
                typing.cast(var.VarOrVal[shape.Size], full_profile.min_size), wanted_size)
            max_size = var.unpack_var(
                typing.cast(var.VarOrVal[shape.Size], full_profile.max_size), wanted_size)
            if min_size == (-1, -1):
                min_size = wanted_size
            if max_size == (-1. -1):
                max_size = wanted_size
            return min_size, wanted_size, max_size

        match self.managed_layout_type:
            case layout_profiles.LinearLayout:
                # Flex layout logic
                d = self.flex_direction # d for direction or dimension
                total_length = self.size[d]
                remain_length = total_length
                max_priority = 0
                priority_levels: dict[int, list[widget.Widget]] = {}
                # Warning: below comments all in Chinese as things are getting a bit complicated
                #          and Chinese is a language with higher efficiency.   —— rgzz666
                for child in self.children:
                    if isinstance(child.layout_profile, layout_profiles.LinearLayout):
                        # 对于每一个采用线性布局的控件
                        # 如尚未记录，则先将其记录到flex_dist列表中
                        if child not in self._flex_dist:
                            self._flex_dist[child] = get_widget_sizes(child)[1][d]
                        # 初步处理，将其长度从总长减去，全部处理完后即为余长
                        remain_length -= child.size[d]
                        # 如果当前child的优先级还不在优先级列表里，则初始化相应的列表项
                        if child.layout_profile.expand_priority not in priority_levels.keys():
                            priority_levels[child.layout_profile.expand_priority] = []
                            # 只有新增了优先级，才判断它是不是新的最大优先级
                            if child.layout_profile.expand_priority > max_priority:
                                max_priority = child.layout_profile.expand_priority
                        # 完成后，把child加入相应的优先级层级列表
                        priority_levels[child.layout_profile.expand_priority].append(child)
                if remain_length == 0:
                    # 此处处理一个特殊情况：如果第一轮正好分完长度，也就是余长恰好=0，则什么也不做直接返回
                    # 这样按照当前的结果，所有控件都会取其profile中指定的默认值
                    return
                first_go_remain_length = remain_length # >0为伸展控件，<0为压缩控件
                # 生成一个列表，内容是所有存在的优先级，按照尝试顺序排序
                # 即：如果初步的余长>0则优先级由大而小，余长<0则由小而大
                priority_level_nums = sorted(priority_levels.keys(), reverse=remain_length > 0)
                for priority_level_num in priority_level_nums:
                    # 对于每一个优先级层级
                    assumed_remain_length = remain_length # 用于存储本层级初步处理后，假设的剩余长度
                    for the_widget in priority_levels[priority_level_num]:
                        sizes = get_widget_sizes(the_widget)
                        if first_go_remain_length > 0:
                            assumed_remain_length -= sizes[2][d] - sizes[1][d]
                    if assumed_remain_length == 0: # 对于正好没有剩余长度的情况
                        return # 停止分配，就这样了
                    else: # 如本轮分配后不是正好结束
                        ratio_sum = sum([
                            the_widget.layout_profile.stretch_share_ratio for the_widget in \
                            priority_levels[priority_level_num] \
                            if isinstance(the_widget.layout_profile, layout_profiles.LinearLayout)
                            ]) # 将所有比例求和作为下一步除数
                            #（虽然已经确定priority_levels只会有线性布局的控件，但还是保留判断来修复类型提示）
                        for the_widget in priority_levels[priority_level_num]:
                            if not isinstance(the_widget.layout_profile, 
                                              layout_profiles.LinearLayout):
                                # 此处同理，虽然已经确定priority_levels只会有线性布局的控件，但还是保留判断来
                                # 修复类型提示
                                continue
                            ## 根据比例计算每个控件最终分得的长度
                            self._flex_dist[the_widget] = round(
                                abs(self.size[d]) / ratio_sum * \
                                the_widget.layout_profile.stretch_share_ratio)
                            ## 此处核验每个控件分配的长度，记录需要再分配的长度，然后调整这些超出的长度
                            len_to_redist = 0 # 需要再分配的总长
                            # 可以伸展或收缩的控件列表
                            expandable: list[widget.Widget] = list(self._flex_dist.keys())
                            compressable: list[widget.Widget] = list(self._flex_dist.keys())
                            for the_widget, dist_len in self._flex_dist.items():
                                widget_sizes = get_widget_sizes(the_widget)
                                if dist_len > widget_sizes[2][d]:
                                    # 超出最大容许长度
                                    len_to_redist += widget_sizes[2][d] - dist_len
                                    self._flex_dist[the_widget] = widget_sizes[2][d]
                                    expandable.remove(the_widget)
                                elif dist_len <  widget_sizes[0][d]:
                                    # 不足最小容许长度
                                    len_to_redist += dist_len - widget_sizes[0][d]
                                    self._flex_dist[the_widget] = widget_sizes[0][d]
                                    compressable.remove(the_widget)
            case _:
                self_id = self.id if isinstance(self, cm_object.CharmyObject) else "without ID"
                raise ValueError(f"Managed layout type chosen for container {self_id} is invalid.")

    def draw_children(self) -> typing.Self:
        """Draw the container and its children."""
        _, managed_layer, place_layer = self.layers
        if typing.TYPE_CHECKING:
            managed_layer = typing.cast(list[widget.Widget], managed_layer)
            place_layer = typing.cast(list[widget.Widget], place_layer)
        for layer in place_layer, managed_layer:
            for child in layer:
                child._check_change()
        return self

    def _clear_children(self):
        """Destroy every child, then drop them from the child list."""
        # 👇 Iterate a copy: destroy() removes each child from `self.children` as it goes
        for child in list(self.children):
            child.destroy()
        self.children = []

    def __contains__(self, target: widget.Widget) -> bool:
        return target in self.children
    
    def get_mouse_hover(self, abs_pos: shape.Point) -> typing.List[Container | widget.Widget]:
        layers: \
            tuple[texture.Texture | texture.TextureLike, 
                  list[widget.Widget], list[widget.Widget]] = self.layers
        pos = (abs_pos[0] - self.abs_pos[0], abs_pos[1] - self.abs_pos[1])
        placed_children = layers[2]
        managed_children = layers[1]
        for layer in (reversed(placed_children), reversed(managed_children)): # For each layer
            for child in layer: # For each child
                result: typing.List[Container | widget.Widget] = []# TODO: Sure???
                if pos in child:
                    if isinstance(child, Container):
                        result = child.get_mouse_hover(pos)
                        if len(result) == 0:
                            # Not hovering on anything, not even background
                            continue # Check if hovering of widgets below
                    else:
                        result = [child]
                    result.insert(0, self)
                    return result
        else:
            if isinstance(texture.ensure_texture(self.background), texture.Transparent) and \
                not isinstance(self, type_checking.WindowLike):
                # Self is not a window and self has transparent back
                return []
            else:
                return [self]