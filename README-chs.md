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

Currently, we almost completed the basic functions of backend and graphics layer, and the effect can be seen by running `/tests/graphics.py`.

## 最新动态

We (The development team members) discuss our latest progress and the next steps in a QQ group chat, which many other Chinese developers also do. Anyone who is interested in (or even better, willing to contribute to) this project will be welcomed to join. The group chat number is: `887102507` .

Please DO NOT create issues irrelevant to software bugs or suggestions etc. in this repository, use GitHub Discussions (if available) or contact us directly in that case.

### For anyone outside China

Unfortunately, currently there is no other discussion group chat available on any other platforms that you may be easier to access. We will create one when we publish our first usable version, because there is no reason to do so before that since users cannot provide any feedback without a working version.

**However,** the good news is, totowang-hhh (aka. rgzz666, one of the devs) can communicate well in English (and that's why he was the one who wrote this README), so feel free to reach him via any possible method. For instance, you may [email him](mailto:tt1224@hotmail.com) for further discussion.

~~thx, now I'm getting annoyed with 26-key touchscreen keyboards 😅~~

## The Genesis Backend

The Genesis backend is current used backend. It will be temporarily used during the development of the higher level GUI APIs exposed to users.

The Genesis backend uses Cairo and SDL2 for rendering and window operations respectively.

## License

This is an open-source project licensed under `AGPLv3`, for full license text, please refer to `LICENSE.txt`.

We also plan to provide paid license in the future, anyone who buys paid license will be able to freely (to some extents, terms and conditions apply) use Charmy without the limitations of `AGPL`. Please note that this paragraph is a brief description of one of our future plans, and does not describe, explain, or complete the licensing policies (currently AGPL only) of this project. For more information of the price and terms of paid license, please wait for further notice or contact us.
