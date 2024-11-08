超棒的 Trio 库
======================

**Awesome Trio Libraries**

.. List of Trio Libraries

   A list of libraries that support Trio, similar to the awesome-python
   list here: https://github.com/vinta/awesome-python/


.. currentmodule:: trio

.. tab:: 中文

   您已经完成了教程，并且对构建具有异步功能的优秀新应用程序和库充满热情。然而，为了完成更多有用的工作，您将希望使用一些支持 Trio 风格并发的优秀库。这个列表并不完整，但它提供了一个起点。另一个发现 Trio 兼容库的好方法是通过在 PyPI 上搜索 ``Framework :: Trio`` 标签 -> `PyPI 搜索 <https://pypi.org/search/?c=Framework+%3A%3A+Trio>`__

.. tab:: 英文

   You have completed the tutorial, and are enthusiastic about building
   great new applications and libraries with async functionality.
   However, to get much useful work done you will want to use some of
   the great libraries that support Trio-flavoured concurrency. This list
   is not complete, but gives a starting point. Another great way to find
   Trio-compatible libraries is to search on PyPI for the ``Framework :: Trio``
   tag -> `PyPI Search <https://pypi.org/search/?c=Framework+%3A%3A+Trio>`__


入门
---------------

**Getting Started**

.. tab:: 中文

   * `cookiecutter-trio <https://github.com/python-trio/cookiecutter-trio>`__ - 这是使用 Trio 的 Python 项目的 cookiecutter 模板。通过提供一堆预配置的样板，它可以轻松启动新项目。
   * `pytest-trio <https://github.com/python-trio/pytest-trio>`__ - Pytest 插件，用于测试启用异步的 Trio 函数。
   * `sphinxcontrib-trio <https://github.com/python-trio/sphinxcontrib-trio>`__ - 使 Sphinx 更好地记录 Python 函数和方法。特别是，它可以轻松记录异步函数。

.. tab:: 英文

   * `cookiecutter-trio <https://github.com/python-trio/cookiecutter-trio>`__ - This is a cookiecutter template for Python projects that use Trio. It makes it easy to start a new project, by providing a bunch of preconfigured boilerplate.
   * `pytest-trio <https://github.com/python-trio/pytest-trio>`__ - Pytest plugin to test async-enabled Trio functions.
   * `sphinxcontrib-trio <https://github.com/python-trio/sphinxcontrib-trio>`__ - Make Sphinx better at documenting Python functions and methods. In particular, it makes it easy to document async functions.


Web 和 HTML
------------

**Web and HTML**

.. tab:: 中文

   * `httpx <https://www.python-httpx.org/>`__ - HTTPX 是一个功能完备的 Python 3 HTTP 客户端，提供同步和异步 API，支持 HTTP/1.1 和 HTTP/2。
   * `trio-websocket <https://github.com/HyperionGray/trio-websocket>`__ - 一个 WebSocket 客户端和服务器实现，致力于安全性、正确性和易用性。
   * `quart-trio <https://github.com/pgjones/quart-trio>`__ - 类似于 Flask，但适用于 Trio。一个简单而强大的框架，用于构建异步 Web 应用和 REST API。提示：这是一个基于 ASGI 的框架，因此您还需要一个支持 ASGI 的 HTTP 服务器。
   * `hypercorn <https://github.com/pgjones/hypercorn>`__ - 一个 HTTP 服务器，用于托管您的 ASGI 应用。支持 HTTP/1.1、HTTP/2、HTTP/3 和 WebSockets。可以作为独立服务器运行，或嵌入到更大的 Trio 应用中。与 ``quart-trio`` 或任何其他 Trio 兼容的 ASGI 框架一起使用。
   * `DeFramed <https://github.com/smurfix/deframed>`__ - DeFramed 是一个 Web 非框架，支持以 99% 服务器为中心的 Web 编程方法，包括对 `Remi <https://github.com/dddomodossola/remi>`__ GUI 库的支持。
   * `pura <https://github.com/groove-x/pura>`__ - 一个简单的 Web 框架，用于将实时图形可视化嵌入到 Trio 应用中，支持在开发过程中检查和操作程序状态。
   * `pyscalpel <https://scalpel.readthedocs.io/en/latest/>`__ - 一个快速且强大的网页抓取库。
   * `muffin <https://github.com/klen/muffin>`__ - Muffin 是一个快速、简单的 ASGI Web 框架。
   * `asgi-tools <https://github.com/klen/asgi-tools>`__ - 快速构建轻量级 ASGI 应用的工具（还包含一个具有生命周期和 WebSocket 支持的测试客户端）。
   * `starlette <https://github.com/encode/starlette>`__ - 一款小巧但闪亮的 ASGI 框架。

.. tab:: 英文

   * `httpx <https://www.python-httpx.org/>`__ - HTTPX is a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2.
   * `trio-websocket <https://github.com/HyperionGray/trio-websocket>`__ - A WebSocket client and server implementation striving for safety, correctness, and ergonomics.
   * `quart-trio <https://github.com/pgjones/quart-trio>`__ - Like Flask, but for Trio. A simple and powerful framework for building async web applications and REST APIs. Tip: this is an ASGI-based framework, so you'll also need an HTTP server with ASGI support.
   * `hypercorn <https://github.com/pgjones/hypercorn>`__ - An HTTP server for hosting your ASGI apps. Supports HTTP/1.1, HTTP/2, HTTP/3, and Websockets. Can be run as a standalone server, or embedded in a larger Trio app. Use it with ``quart-trio``, or any other Trio-compatible ASGI framework.
   * `DeFramed <https://github.com/smurfix/deframed>`__ - DeFramed is a Web non-framework that supports a 99%-server-centric approach to Web coding, including support for the `Remi <https://github.com/dddomodossola/remi>`__ GUI library.
   * `pura <https://github.com/groove-x/pura>`__ - A simple web framework for embedding realtime graphical visualization into Trio apps, enabling inspection and manipulation of program state during development.
   * `pyscalpel <https://scalpel.readthedocs.io/en/latest/>`__ - A fast and powerful webscraping library.
   * `muffin <https://github.com/klen/muffin>`_ - Muffin is a fast, simple ASGI web-framework
   * `asgi-tools <https://github.com/klen/asgi-tools>`_ - Tools to quickly build lightest ASGI apps (also contains a test client with lifespan, websocket support)
   * `starlette <https://github.com/encode/starlette>`_ - The little ASGI framework that shines.


数据库
--------

**Database**

.. tab:: 中文

   * `triopg <https://github.com/python-trio/triopg>`__ - 基于 asyncpg 的 Trio PostgreSQL 客户端。
   * `trio-mysql <https://github.com/python-trio/trio-mysql>`__ - 纯 Python MySQL 客户端。
   * `sqlalchemy_aio <https://github.com/RazerM/sqlalchemy_aio>`__ - 为 SQLAlchemy 核心添加 asyncio 和 Trio 支持，衍生自 alchimia。
   * `redio <https://github.com/Tronic/redio>`__ - 纯 Python 和 Trio 实现的 Redis 客户端。
   * `trio_redis <https://github.com/omnidots/trio_redis>`__ - 一个为 Trio 提供的 Redis 客户端，依赖 hiredis-py。
   * `asyncakumuli <https://github.com/M-o-a-T/asyncakumuli>`__ - `Akumuli <https://akumuli.org/>`__ 时间序列数据库的客户端。
   * `aio-databases <https://github.com/klen/aio-databases>`__ - 为各种数据库（如 triopg、trio-mysql）提供异步支持。
   * `peewee-aio <https://github.com/klen/peewee-aio>`__ - 支持 Trio 的 Peewee 异步 ORM（triopg、trio-mysql）。

.. tab:: 英文

   * `triopg <https://github.com/python-trio/triopg>`__ - PostgreSQL client for Trio based on asyncpg.
   * `trio-mysql <https://github.com/python-trio/trio-mysql>`__ - Pure Python MySQL Client.
   * `sqlalchemy_aio <https://github.com/RazerM/sqlalchemy_aio>`__ - Add asyncio and Trio support to SQLAlchemy core, derived from alchimia.
   * `redio <https://github.com/Tronic/redio>`__ - Redis client, pure Python and Trio.
   * `trio_redis <https://github.com/omnidots/trio_redis>`__ - A Redis client for Trio. Depends on hiredis-py.
   * `asyncakumuli <https://github.com/M-o-a-T/asyncakumuli>`__ - Client for the `Akumuli <https://akumuli.org/>`__ time series database.
   * `aio-databases <https://github.com/klen/aio-databases>`_ - Async Support for various databases (triopg, trio-mysql)
   * `peewee-aio <https://github.com/klen/peewee-aio>`_ - Peewee Async ORM with trio support (triopg, trio-mysql).


物联网
------

**IOT**

.. tab:: 中文

   * `DistMQTT <https://github.com/M-o-a-T/distmqtt>`__ - DistMQTT 是一个开源的 MQTT 客户端和代理实现。它是 hbmqtt 的一个分支，支持 anyio 和 DistKV。
   * `asyncgpio <https://github.com/python-trio/trio-gpio>`__ - 允许轻松访问您的 Raspberry Pi 或类似嵌入式计算机上的 GPIO 引脚。
   * `asyncowfs <https://github.com/M-o-a-T/asyncowfs>`__ - 为 1wire 传感器和执行器提供高级、面向对象的访问。
   * `DistKV <https://github.com/M-o-a-T/distkv>`__ - 一个持久的、分布式的、无主的键值存储，支持异步通知以及一些与 IoT 相关的插件。

.. tab:: 英文

   * `DistMQTT <https://github.com/M-o-a-T/distmqtt>`__ - DistMQTT is an open source MQTT client and broker implementation. It is a fork of hbmqtt with support for anyio and DistKV.
   * `asyncgpio <https://github.com/python-trio/trio-gpio>`__ - Allows easy access to the GPIO pins on your Raspberry Pi or similar embedded computer.
   * `asyncowfs <https://github.com/M-o-a-T/asyncowfs>`__ - High-level, object-oriented access to 1wire sensors and actors.
   * `DistKV <https://github.com/M-o-a-T/distkv>`__ - a persistent, distributed, master-less key/value storage with async notification and some IoT-related plug-ins.


构建命令行应用程序
--------------------------

**Building Command Line Apps**

.. tab:: 中文

   * `trio-click <https://github.com/python-trio/trio-click>`__ - Python 组合命令行工具，Trio 兼容版本。
   * `urwid <https://github.com/urwid/urwid>`__ - Urwid 是一个用于 Python 的控制台用户界面库。

.. tab:: 英文

   * `trio-click <https://github.com/python-trio/trio-click>`__ - Python composable command line utility, trio-compatible version.
   * `urwid <https://github.com/urwid/urwid>`__ - Urwid is a console user interface library for Python.


构建 GUI 应用程序
-----------------

**Building GUI Apps**

.. tab:: 中文

   * `QTrio <https://qtrio.readthedocs.io/en/stable/>`__ - Trio 与 PyQt 或 PySide Qt 包装库的集成。使用 Trio 的 :ref:`guest mode <guest-mode>`。

.. tab:: 英文

   * `QTrio <https://qtrio.readthedocs.io/en/stable/>`__ - Integration between Trio and either the PyQt or PySide Qt wrapper libraries.  Uses Trio's :ref:`guest mode <guest-mode>`.


多核/多处理
--------------------------

**Multi-Core/Multiprocessing**

.. tab:: 中文

   * `tractor <https://github.com/goodboy/tractor>`__ - 一个实验性的 Trionic（即结构化并发）"actor 模型"，用于分布式多核 Python。
   * `Trio run_in_process <https://github.com/ethereum/trio-run-in-process>`__ - 基于 Trio 的 API，用于在单独的进程中运行代码。
   * `trio-parallel <https://trio-parallel.readthedocs.io/>`__ - Trio 的 CPU 并行性支持

.. tab:: 英文

   * `tractor <https://github.com/goodboy/tractor>`__ - An experimental, trionic (aka structured concurrent) "actor model" for distributed multi-core Python.
   * `Trio run_in_process <https://github.com/ethereum/trio-run-in-process>`__ - Trio based API for running code in a separate process.
   * `trio-parallel <https://trio-parallel.readthedocs.io/>`__ - CPU parallelism for Trio


流处理
-----------------

**Stream Processing**

.. tab:: 中文

   * `Slurry <https://github.com/andersea/slurry>`__ - Slurry 是一个用于构建基于 Trio 的反应式数据处理应用程序的微框架。

.. tab:: 英文

   * `Slurry <https://github.com/andersea/slurry>`__ - Slurry is a microframework for building reactive, data processing applications with Trio.


RPC
---

.. tab:: 中文

   * `purepc <https://github.com/python-trio/purerpc>`__ - 使用 anyio 实现的原生异步 Python gRPC 客户端和服务器实现。

.. tab:: 英文

   * `purepc <https://github.com/python-trio/purerpc>`__ - Native, async Python gRPC client and server implementation using anyio.


测试
-------

**Testing**

.. tab:: 中文

   * `pytest-trio <https://github.com/python-trio/pytest-trio>`__ - Trio 的 Pytest 插件。
   * `hypothesis-trio <https://github.com/python-trio/hypothesis-trio>`__ - Hypothesis 开箱即用地支持 Trio 用于 ``@given(...)`` 测试；此扩展提供 Trio 兼容的有状态测试。
   * `trustme <https://github.com/python-trio/trustme>`__ - 为挑剔的测试者提供的高质量 TLS 证书，您可以随时等待。
   * `pytest-aio <https://github.com/klen/pytest-aio>`_ - 支持 trio、curio、asyncio 的 Pytest 插件。
   * `logot <https://github.com/etianen/logot>`_ - 测试您的异步代码是否正确记录日志。

.. tab:: 英文

   * `pytest-trio <https://github.com/python-trio/pytest-trio>`__ - Pytest plugin for trio.
   * `hypothesis-trio <https://github.com/python-trio/hypothesis-trio>`__ - Hypothesis supports Trio out of the box for ``@given(...)`` tests; this extension provides Trio-compatible stateful testing.
   * `trustme <https://github.com/python-trio/trustme>`__ - #1 quality TLS certs while you wait, for the discerning tester.
   * `pytest-aio <https://github.com/klen/pytest-aio>`_ - Pytest plugin with support for trio, curio, asyncio
   * `logot <https://github.com/etianen/logot>`_ - Test whether your async code is logging correctly.


工具和实用程序
-------------------

**Tools and Utilities**

.. tab:: 中文

   * `trio-util <https://github.com/groove-x/trio-util>`__ - 一组用于 Trio 异步/等待框架的工具。
   * `flake8-async <https://github.com/python-trio/flake8-async>`__ - 用于 Trio、AnyIO 和/或 asyncio 中各种问题的高度意见化的 linter。可以作为 flake8 插件运行，或作为独立工具，支持自动修复某些错误。
   * `tricycle <https://github.com/oremanj/tricycle>`__ - 这是一个有趣但可能尚未完全证明的 Trio 扩展库。
   * `tenacity <https://github.com/jd/tenacity>`__ - 支持异步/等待的 Python 重试库。
   * `perf-timer <https://github.com/belm0/perf-timer>`__ - 带有 Trio 异步支持的代码计时器（参见 ``TrioPerfTimer``）。收集代码块的执行时间，排除协程未调度时的时间，例如阻塞 I/O 和睡眠期间。还提供 ``trio_perf_counter()`` 用于低级计时。
   * `aiometer <https://github.com/florimondmanca/aiometer>`__ - 并发执行大量任务，同时控制并发限制。
   * `triotp <https://linkdd.github.io/triotp>`__ - Python Trio 的 OTP 框架。
   * `aioresult <https://github.com/arthur-tacca/aioresult>`__ - 获取 Trio 或 anyio 中后台异步函数的返回值，带有一个简单的 Future 类和等待工具。

.. tab:: 英文

   * `trio-util <https://github.com/groove-x/trio-util>`__ - An assortment of utilities for the Trio async/await framework.
   * `flake8-async <https://github.com/python-trio/flake8-async>`__ - Highly opinionated linter for various sorts of problems in Trio, AnyIO and/or asyncio. Can run as a flake8 plugin, or standalone with support for autofixing some errors.
   * `tricycle <https://github.com/oremanj/tricycle>`__ - This is a library of interesting-but-maybe-not-yet-fully-proven extensions to Trio.
   * `tenacity <https://github.com/jd/tenacity>`__ - Retrying library for Python with async/await support.
   * `perf-timer <https://github.com/belm0/perf-timer>`__ - A code timer with Trio async support (see ``TrioPerfTimer``).  Collects execution time of a block of code excluding time when the coroutine isn't scheduled, such as during blocking I/O and sleep.  Also offers ``trio_perf_counter()`` for low-level timing.
   * `aiometer <https://github.com/florimondmanca/aiometer>`__ - Execute lots of tasks concurrently while controlling concurrency limits
   * `triotp <https://linkdd.github.io/triotp>`__ - OTP framework for Python Trio
   * `aioresult <https://github.com/arthur-tacca/aioresult>`__ - Get the return value of a background async function in Trio or anyio, along with a simple Future class and wait utilities


Trio/Asyncio 互操作性
-----------------------------

**Trio/Asyncio Interoperability**

.. tab:: 中文

   * `anyio <https://github.com/hellowac/anyio-zh-cn>`__ - AnyIO 是一个异步兼容性 API，允许针对它编写的应用程序和库在 asyncio 或 trio 上无需修改即可运行。
   * `sniffio <https://github.com/python-trio/sniffio>`__ - 这是一个小型包，唯一的目的就是让你检测你的代码正在使用哪个异步库。
   * `trio-asyncio <https://github.com/python-trio/trio-asyncio>`__ - Trio-Asyncio 让你可以在 Trio 应用中使用许多 asyncio 库。

.. tab:: 英文

   * `anyio <https://github.com/agronholm/anyio>`__ - AnyIO is a asynchronous compatibility API that allows applications and libraries written against it to run unmodified on asyncio or trio.
   * `sniffio <https://github.com/python-trio/sniffio>`__ - This is a tiny package whose only purpose is to let you detect which async library your code is running under.
   * `trio-asyncio <https://github.com/python-trio/trio-asyncio>`__ - Trio-Asyncio lets you use many asyncio libraries from your Trio app.
