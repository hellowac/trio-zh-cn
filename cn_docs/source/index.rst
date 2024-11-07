.. Trio documentation master file, created by
   sphinx-quickstart on Sat Jan 21 19:11:14 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================================================
Trio: 一个用于异步并发和 I/O 的友好 Python 库
=============================================================

**Trio: a friendly Python library for async concurrency and I/O**

.. tabs::

    .. tab:: 中文

        Trio 项目的目标是创建一个 **生产级**、 `宽松许可 <https://github.com/python-trio/trio/blob/main/LICENSE>`__ 的、原生支持 `async/await` 的 Python I/O 库。和所有异步库一样，它的主要目的是帮助您编写能够 **同时执行多项任务** 并实现 **并行化 I/O** 的程序。比如，一个需要并行抓取大量页面的网络爬虫、一个需要同时处理多个下载和 WebSocket 连接的 Web 服务器、一个监控多个子进程的进程管理器……诸如此类的需求。相比其他库，Trio 力求通过专注于 **可用性** 和 **正确性** 来脱颖而出。并发编程很复杂，而我们试图使其 *简单易用*，以帮助开发者 *正确地* 完成任务。

        Trio 从头开始设计，以充分利用 `最新的 Python 特性 <https://www.python.org/dev/peps/pep-0492/>`__，并从 `多个来源 <https://github.com/python-trio/trio/wiki/Reading-list>`__ 汲取灵感，特别是 Dave Beazley 的 `Curio <https://curio.readthedocs.io/>`__。最终的设计比传统库（如 `asyncio <https://docs.python.org/3/library/asyncio.html>`__ 和 `Twisted <https://twistedmatrix.com/>`__）更简单直观，但同样功能完备。Trio 是我一直希望拥有的 Python I/O 库，它使构建 I/O 导向的程序更加轻松、减少错误，并且更有趣。也许您会有相同的感受。

        这个项目仍然较年轻，带有一定的实验性质：整体设计稳固，现有功能经过全面测试和文档化，但您可能会遇到一些功能缺失或需要改进的地方。我们 **鼓励您使用**，但建议您 `阅读并订阅 issue #1 <https://github.com/python-trio/trio/issues/1>`__，以便在有任何影响兼容性的更改时获得通知并有机会提供反馈。

        关键统计信息：

        * 支持的环境：我们测试的环境包括

          - Python: 3.9+（CPython 和 PyPy）
          - Windows、macOS、Linux（glibc 和 musl）、FreeBSD

          其他环境可能也可以工作；试试看吧。

        * 安装： ``python3 -m pip install -U trio``（在 Windows 上，可能需要 ``py -3 -m pip install -U trio``）。不需要编译器。

        * 教程和参考手册： https://trio.readthedocs.io

        * Bug 跟踪和源代码： https://github.com/python-trio/trio

        * 实时聊天： https://gitter.im/python-trio/general

        * 讨论论坛： https://trio.discourse.group

        * 许可证: MIT 或 Apache 2，您可以任选其一

        * 贡献者指南： https://trio.readthedocs.io/en/latest/contributing.html

        * 行为准则：我们要求所有项目空间的贡献者遵循我们的 :ref:`行为准则 <code-of-conduct>` 。

    .. tab:: 英文

        The Trio project's goal is to produce a production-quality,
        `permissively licensed
        <https://github.com/python-trio/trio/blob/main/LICENSE>`__,
        async/await-native I/O library for Python. Like all async libraries,
        its main purpose is to help you write programs that do **multiple
        things at the same time** with **parallelized I/O**. A web spider that
        wants to fetch lots of pages in parallel, a web server that needs to
        juggle lots of downloads and websocket connections at the same time, a
        process supervisor monitoring multiple subprocesses... that sort of
        thing. Compared to other libraries, Trio attempts to distinguish
        itself with an obsessive focus on **usability** and
        **correctness**. Concurrency is complicated; we try to make it *easy*
        to get things *right*.

        Trio was built from the ground up to take advantage of the `latest
        Python features <https://www.python.org/dev/peps/pep-0492/>`__, and
        draws inspiration from `many sources
        <https://github.com/python-trio/trio/wiki/Reading-list>`__, in
        particular Dave Beazley's `Curio <https://curio.readthedocs.io/>`__.
        The resulting design is radically simpler than older competitors like
        `asyncio <https://docs.python.org/3/library/asyncio.html>`__ and
        `Twisted <https://twistedmatrix.com/>`__, yet just as capable. Trio is
        the Python I/O library I always wanted; I find it makes building
        I/O-oriented programs easier, less error-prone, and just plain more
        fun. Perhaps you'll find the same.

        This project is young and still somewhat experimental: the overall
        design is solid and the existing features are fully tested and
        documented, but you may encounter missing functionality or rough
        edges. We *do* encourage you do use it, but you should `read and
        subscribe to issue #1
        <https://github.com/python-trio/trio/issues/1>`__ to get warning and a
        chance to give feedback about any compatibility-breaking changes.

        Vital statistics:

        * Supported environments: We test on

          - Python: 3.9+ (CPython and PyPy)
          - Windows, macOS, Linux (glibc and musl), FreeBSD

          Other environments might also work; give it a try and see.

        * Install: ``python3 -m pip install -U trio`` (or on Windows, maybe
          ``py -3 -m pip install -U trio``). No compiler needed.

        * Tutorial and reference manual: https://trio.readthedocs.io

        * Bug tracker and source code: https://github.com/python-trio/trio

        * Real-time chat: https://gitter.im/python-trio/general

        * Discussion forum: https://trio.discourse.group

        * License: MIT or Apache 2, your choice

        * Contributor guide: https://trio.readthedocs.io/en/latest/contributing.html

        * Code of conduct: Contributors are requested to follow our `code of
          conduct
          <https://trio.readthedocs.io/en/latest/code-of-conduct.html>`_
          in all project spaces.


.. toctree::
   :maxdepth: 2
   :caption: Trio 友好且全面的手册：

   tutorial.rst
   awesome-trio-libraries.rst
   ref-core/index.rst
   reference-io.rst
   reference-testing.rst
   reference-lowlevel.rst
   design.rst
   history.rst
   contributing.rst
   releasing.rst
   code-of-conduct.rst

====================
 索引表
====================

**Indices and tables**

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`
