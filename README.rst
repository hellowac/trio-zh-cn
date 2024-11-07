.. image:: https://img.shields.io/badge/chat-join%20now-blue.svg
   :target: https://gitter.im/python-trio/general
   :alt: Join chatroom

.. image:: https://img.shields.io/badge/forum-join%20now-blue.svg
   :target: https://trio.discourse.group
   :alt: Join forum

.. image:: https://img.shields.io/badge/docs-read%20now-blue.svg
   :target: https://trio.readthedocs.io
   :alt: Documentation

.. image:: https://img.shields.io/pypi/v/trio.svg
   :target: https://pypi.org/project/trio
   :alt: Latest PyPi version

.. image:: https://img.shields.io/conda/vn/conda-forge/trio.svg
   :target: https://anaconda.org/conda-forge/trio
   :alt: Latest conda-forge version

.. image:: https://codecov.io/gh/python-trio/trio/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/python-trio/trio
   :alt: Test coverage

Trio – 用于异步并发和 I/O 的友好 Python 库
==============================================================

.. image:: https://raw.githubusercontent.com/python-trio/trio/9b0bec646a31e0d0f67b8b6ecc6939726faf3e17/logo/logo-with-background.svg
   :width: 200px
   :align: right

Trio 项目的目标是创建一个 **生产级** 、 **宽松许可** 的( `permissively licensed <https://github.com/python-trio/trio/blob/main/LICENSE>`__ )，原生支持 `async/await` 的 Python I/O 库。像所有异步库一样，它的主要目的是帮助您编写能够同时执行 **多个任务** 的程序，实现 **并行化 I/O** 。例如，一个需要并行抓取大量页面的网络爬虫、一个同时处理众多下载和 WebSocket 连接的 Web 服务器、一个监控多个子进程的进程管理器……等等。与其他库相比，Trio 力求通过专注于 **可用性** 和 **正确性** 来与众不同。并发编程很复杂，而我们试图使其 *简单易用* ，以帮助开发者 *正确地* 完成任务。

Trio 从头开始设计，以充分利用 `最新的 Python 特性 <https://www.python.org/dev/peps/pep-0492/>`__，并从 `多个来源 <https://github.com/python-trio/trio/wiki/Reading-list>`__ 汲取灵感，尤其是 Dave Beazley 的 `Curio <https://curio.readthedocs.io/>`__ 。最终的设计比传统库( 如 `asyncio <https://docs.python.org/3/library/asyncio.html>`__ 和 `Twisted <https://twistedmatrix.com/>`__ )更简单直观，同时功能完备。Trio 是我一直希望拥有的 Python I/O 库，它使构建 I/O 导向的程序变得更加轻松、减少错误，并且更加有趣。 `也许您会有相同的感受 <https://github.com/python-trio/trio/wiki/Testimonials>`__ 。

这个项目尚处于早期阶段，仍然具有一定的实验性：整体设计稳固，现有功能经过全面测试和文档化，但您可能会遇到一些缺失的功能或需要打磨的细节。我们 **鼓励您使用** ，但建议您 `阅读并订阅 issue #1 <https://github.com/python-trio/trio/issues/1>`__，以便在有任何影响兼容性的更改时获得通知并有机会提供反馈。


接下来去哪？
--------------

**我想试试看！** 太棒了！我们提供了一个 `友好的教程 <https://trio.readthedocs.io/en/stable/tutorial.html>`__ 帮助您入门；不需要任何异步编码的前置经验。

**唉，我不想读那么多内容——给我看看代码吧！** 如果您迫不及待，那么这里有一个 `简单的并发示例 <https://trio.readthedocs.io/en/stable/tutorial.html#tutorial-example-tasks-intro>`__、一个 `回显客户端 <https://trio.readthedocs.io/en/stable/tutorial.html#tutorial-echo-client-example>`__ 和一个 `回显服务器 <https://trio.readthedocs.io/en/stable/tutorial.html#tutorial-echo-server-example>`__。

**Trio 如何使程序比其他方法更易于阅读和推理？** Trio 基于一种我们称之为“结构化并发”的新思维方式。最好的理论介绍是文章 `《关于结构化并发的笔记，或者说：Go 语句有害》 <https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/>`__ 。或者，您也可以 `观看 PyCon 2018 的这个演讲 <https://www.youtube.com/watch?v=oLkfnc_UMcE>`__ ，其中演示了在旧库和 Trio 中实现“Happy Eyeballs”算法的对比。

**很酷，但它会在我的系统上运行吗？** 应该可以！只要您拥有某种 Python 3.9 或更高版本( CPython 或 `当前维护的 PyPy3 版本 <https://doc.pypy.org/en/latest/faq.html#which-python-versions-does-pypy-implement>`__ 均可 )，并且使用的是 Linux、macOS、Windows 或 FreeBSD，Trio 就会正常工作。其他环境也可能有效，但这些是我们测试过的。此外，所有依赖项都是纯 Python，除了 Windows 上的 CFFI( 它提供了轮子包 )，所以安装应该很简单( 不需要 C 编译器 )。

**我试过了，但它不起作用。** 很抱歉听到这个消息！您可以尝试在我们的 `聊天室 <https://gitter.im/python-trio/general>`__ 或 `论坛 <https://trio.discourse.group>`__ 中求助， `提交错误报告 <https://github.com/python-trio/trio/issues/new>`__，或在 StackOverflow 上 `发布问题 <https://stackoverflow.com/questions/ask?tags=python+python-trio>`__，我们会尽力帮助您。

**Trio 很棒，我想帮助让它更棒！** 您真是太好了！还有大量的工作需要完成——补全缺失的功能，构建一个基于 Trio 的库生态系统，进行可用性测试( 例如，尝试自学或教朋友使用 Trio，记录所有遇到的错误信息和疑惑之处？ )，改进文档……请查看我们的 `贡献者指南 <https://trio.readthedocs.io/en/stable/contributing.html>`__ ！

**我没有立即使用它的计划，但我喜欢深入研究 I/O 库设计！** 这有点奇怪？但说实话，您在这里会很合群。我们有一个 `专门讨论结构化并发的子论坛 <https://trio.discourse.group/c/structured-concurrency>`__( 欢迎其他系统的开发者加入！ )。或者，您可以查看我们的 `设计选择讨论 <https://trio.readthedocs.io/en/stable/design.html#user-level-api-principles>`__ 、 `阅读列表 <https://github.com/python-trio/trio/wiki/Reading-list>`__，以及 `标记为设计讨论的议题 <https://github.com/python-trio/trio/labels/design%20discussion>`__。

**我想确保公司法务不会对我发火！** 放心，Trio 是在 MIT 或 Apache 2 许可证下的宽松许可。详情请见 `LICENSE <https://github.com/python-trio/trio/blob/main/LICENSE>`__ 。

行为准则
---------------

我们要求所有项目空间的贡献者遵循我们的 `行为准则 <https://trio.readthedocs.io/en/stable/code-of-conduct.html>`__。
