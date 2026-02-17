# Copyright (C) 2026 XiangQinxi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Author: XiangQinxi
# Contributors: XiangQinxi, rgzz666, littlewhitecloud

"""A modern GUI library."""

from .const import *

# from .drawing import *
from .event import Event, EventHandling, EventTask, WorkingThread
from .object import CharmyObject
from .pos import Pos
from .rect import Rect
from .size import Size
from .var import Var, IntVar, FloatVar, StringVar, BooleanVar
from .styles import *
from .widgets import *
