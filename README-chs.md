<div style="display: flex; justify-items: center;">
  <img src="./artworks/icon.png" alt="Project main icon" style="width: 8rem; height: 8rem;">
  <div>
    <h1>Charmy GUI</h1>
    <p>适用于Python的，轻量但全能的GUI库</p>
  </div>
</div>

曾用名`Suzaku`。

Charmy是一个针对Python程序的GUI库，允许再多个后端之间切换，并因此提供一个在跨平台的同时保持轻量的GUI方案。

Charmy仍然在开发中，您可以透过点亮一个star来激励我们并加速开发进程。

十分感谢[稲凪 咲](https://inagi-saki.work)提供的图标和吉祥物设计。

本README是一个早期开发阶段的临时版本，未来可能会有较大修改

## 更多资讯

Charmy仍在开发中，它的许多细节可能还没设计好，或者可能会在将来面临大改。

如果您对此项目感兴趣，则可以加入我们的讨论并查看最新进度。参阅[最新动态](#最新动态)章节。

## 目前成果

首先，简要介绍Charmy的基本架构设计。Charmy被设计为三层：后端层、绘图层、控件层，由底到顶。

截至目前，我们已经完成了后端层和绘图层的基本功能，其效果可透过运行`/tests/graphics.py`来查看。

## 最新动态

我们（Charmy开发组）像大部分中国开发团队一样，在QQ群内沟通开发进度。我们欢迎任何感兴趣或希望贡献的人加入我们的群组。群号为：`887102507`。

请不要在Issues中发布除反馈或建议以外的其他内容。对于这些离题内容，发在Discussions（如果可用）中，或直接联系我们

Please DO NOT create issues irrelevant to software bugs or suggestions etc. in this repository, use GitHub Discussions (if available) or contact us directly in that case.

### 对于海外用户或不希望使用QQ的用户

~~讲真，老哥，你为什么会在阅读中文README？~~

很遗憾，我们尚未在任何海外平台上提供交流群，因为在第一个可用版本出现之前，收集反馈似乎意义不大。您可以[联系rgzz666](mailto:tt1224@hotmail.com)，用中文或英文沟通。

## Genesis后端

Genesis后端时目前使用的唯一后端，它会在早期开发阶段临时使用。Genesis后端主要用于可行性验证，同时方便我们调试更上层的机制是否可用。

Genesis后端分别使用SDL2和Cairo进行窗口操作和绘制。

## 授权

注：此部分以英文原文为准，中文翻译仅供参考

Charmy是一个遵循`AGPLv3`开源协议的项目，对于完整的开源协议文本，参阅`LICENSE.txt`。

我们也计划在未来提供付费授权。购买付费授权的实体将可以不受`AGPL`的约束而使用或修改本项目（但仍需遵循一定的规定和条款）。请注意：这些描述只是对我们未来规划的简要介绍，而不对当前的开源条款构成任何补全、覆盖、解释或描述作用。有关更多相关规划，请关注后续通知，或带价咨询。
