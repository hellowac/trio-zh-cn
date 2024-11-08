Trio 中的测试
=========================================

**Testing made easier with** ``trio.testing``

.. module:: trio.testing

.. tab:: 中文

   :mod:`trio.testing` 模块提供了各种工具，帮助更轻松地测试 Trio 代码。与 :mod:`trio` 命名空间中的其他子模块不同， :mod:`trio.testing` 在执行 ``import trio`` 时 *不会* 自动导入；你必须显式地执行 ``import trio.testing``。

.. tab:: 英文

   The :mod:`trio.testing` module provides various utilities to make it
   easier to test Trio code. Unlike the other submodules in the
   :mod:`trio` namespace, :mod:`trio.testing` is *not* automatically
   imported when you do ``import trio``; you must ``import trio.testing``
   explicitly.


测试工具集成
------------------------

**Test harness integration**

.. decorator:: trio_test


.. _testing-time:

时间和超时
-----------------

**Time and timeouts**

.. tab:: 中文

   :class:`trio.testing.MockClock` 是一个 :class:`~trio.abc.Clock`，它提供了一些技巧，帮助你高效地测试涉及超时的代码：

   * 默认情况下，它从时间 0 开始，时钟时间只有在你显式调用 :meth:`~MockClock.jump` 时才会前进。这为测试提供了一个极其可控的时钟。

   * 如果你希望它像普通时钟一样按真实时间运行，可以将 :attr:`~MockClock.rate` 设置为 1.0。你可以在测试中停止或启动时钟。你还可以将 :attr:`~MockClock.rate` 设置为 10.0，使时钟时间以 10 倍的真实速度流逝（例如，``await trio.sleep(10)`` 会在 1 秒后返回）。

   * 更有趣的是，你可以将 :attr:`~MockClock.autojump_threshold` 设置为零或一个小值，这样它就会观察运行循环的执行情况，每当所有任务都停下来等待超时时，它会将时钟跳跃到那个超时。 在许多情况下，这使得涉及超时的自然代码能够自动在几乎满负荷的 CPU 使用率下运行，而无需任何更改。（感谢 `fluxcapacitor <https://github.com/majek/fluxcapacitor>`__ 提供这个很棒的点子。）

   * 当然，这些功能可以根据需要任意组合使用。

   尽管有这些技巧，从 Trio "内部" 看，时间的流逝仍然是正常的，只要你限制自己使用 Trio 的时间函数（参见 :ref:`time-and-clocks`）。下面是一个示例，展示了两种让时间快速流逝的不同方式。请注意，在这两种情况下，两个任务保持一致的现实视图，事件按预期顺序发生，尽管它们与真实时间有很大的偏差：

   .. literalinclude:: reference-testing/across-realtime.py

   输出：

   .. literalinclude:: reference-testing/across-realtime.out
      :language: none

.. tab:: 英文

   :class:`trio.testing.MockClock` is a :class:`~trio.abc.Clock` with a
   few tricks up its sleeve to help you efficiently test code involving
   timeouts:

   * By default, it starts at time 0, and clock time only advances when
     you explicitly call :meth:`~MockClock.jump`. This provides an
     extremely controllable clock for testing.

   * You can set :attr:`~MockClock.rate` to 1.0 if you want it to start
     running in real time like a regular clock. You can stop and start
     the clock within a test. You can set :attr:`~MockClock.rate` to 10.0
     to make clock time pass at 10x real speed (so e.g. ``await
     trio.sleep(10)`` returns after 1 second).

   * But even more interestingly, you can set
     :attr:`~MockClock.autojump_threshold` to zero or a small value, and
     then it will watch the execution of the run loop, and any time
     things have settled down and everyone's waiting for a timeout, it
     jumps the clock forward to that timeout. In many cases this allows
     natural-looking code involving timeouts to be automatically run at
     near full CPU utilization with no changes. (Thanks to `fluxcapacitor
     <https://github.com/majek/fluxcapacitor>`__ for this awesome idea.)

   * And of course these can be mixed and matched at will.

   Regardless of these shenanigans, from "inside" Trio the passage of time
   still seems normal so long as you restrict yourself to Trio's time
   functions (see :ref:`time-and-clocks`). Below is an example
   demonstrating two different ways of making time pass quickly. Notice
   how in both cases, the two tasks keep a consistent view of reality and
   events happen in the expected order, despite being wildly divorced
   from real time:

   .. literalinclude:: reference-testing/across-realtime.py

   Output:

   .. literalinclude:: reference-testing/across-realtime.out
      :language: none

.. autoclass:: MockClock
   :members:


任务排序
-------------------

**Inter-task ordering**

.. autoclass:: Sequencer

.. autofunction:: wait_all_tasks_blocked

.. autofunction:: wait_all_threads_completed

.. autofunction:: active_thread_count


.. _testing-streams:

流
-------

**Streams**

连接到进程内套接字服务器
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Connecting to an in-process socket server**

.. autofunction:: open_stream_to_socket_listener


.. _virtual-streams:

虚拟、可控流
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Virtual, controllable streams**

.. tab:: 中文

   测试网络协议时，一个特别具有挑战性的问题是确保你的实现能够处理数据流被奇怪地切断并以奇怪的时序到达的情况：本地主机连接往往比真实网络表现得要好得多，因此如果你只在本地主机上进行测试，可能在后期会遇到问题。为了帮助你，Trio 提供了一些完全基于内存的流接口实现（参见 :ref:`abstract-stream-api`），让你可以编写各种有趣的恶意测试。

   这里有几个部分，它们是如何组合在一起的：

   :func:`memory_stream_pair` 提供了一对连接的双向流。它类似于 :func:`socket.socketpair`，但是不涉及那讨厌的操作系统及其网络栈。

   要构建一个双向流，:func:`memory_stream_pair` 使用了两个单向流。它通过调用 :func:`memory_stream_one_way_pair` 来获得这两个流。

   :func:`memory_stream_one_way_pair` 又是使用较低级别的类 :class:`MemorySendStream` 和 :class:`MemoryReceiveStream` 实现的。这些类是 (你猜对了) :class:`trio.abc.SendStream` 和 :class:`trio.abc.ReceiveStream` 的实现，它们本身不连接任何东西——“发送”和“接收”只是将数据放入和从各自拥有的私有内部缓冲区中取出数据。它们还提供了一些有趣的钩子，允许你自定义其方法的行为。如果你愿意，这里可以插入一些恶意代码。:func:`memory_stream_one_way_pair` 以相对简单的方式利用了这些钩子：它只是设置，当你调用 ``send_all`` 或关闭发送流时，它会自动触发对 :func:`memory_stream_pump` 的调用，后者是一个便捷函数，从 :class:`MemorySendStream` 的缓冲区中取出数据，并将其放入 :class:`MemoryReceiveStream` 的缓冲区。但这只是默认行为——你可以用任何你想要的自定义行为替换它。

   Trio 还提供了一些专门用于测试完全 **未** 缓冲流的函数：:func:`lockstep_stream_one_way_pair` 和 :func:`lockstep_stream_pair`。这些函数不可定制，但它们展现了一种极端的行为，对于捕捉协议实现中的边界情况非常有效。

.. tab:: 英文

   One particularly challenging problem when testing network protocols is
   making sure that your implementation can handle data whose flow gets
   broken up in weird ways and arrives with weird timings: localhost
   connections tend to be much better behaved than real networks, so if
   you only test on localhost then you might get bitten later. To help
   you out, Trio provides some fully in-memory implementations of the
   stream interfaces (see :ref:`abstract-stream-api`), that let you write
   all kinds of interestingly evil tests.

   There are a few pieces here, so here's how they fit together:

   :func:`memory_stream_pair` gives you a pair of connected,
   bidirectional streams. It's like :func:`socket.socketpair`, but
   without any involvement from that pesky operating system and its
   networking stack.

   To build a bidirectional stream, :func:`memory_stream_pair` uses
   two unidirectional streams. It gets these by calling
   :func:`memory_stream_one_way_pair`.

   :func:`memory_stream_one_way_pair`, in turn, is implemented using the
   low-ish level classes :class:`MemorySendStream` and
   :class:`MemoryReceiveStream`. These are implementations of (you
   guessed it) :class:`trio.abc.SendStream` and
   :class:`trio.abc.ReceiveStream` that on their own, aren't attached to
   anything – "sending" and "receiving" just put data into and get data
   out of a private internal buffer that each object owns. They also have
   some interesting hooks you can set, that let you customize the
   behavior of their methods. This is where you can insert the evil, if
   you want it. :func:`memory_stream_one_way_pair` takes advantage of
   these hooks in a relatively boring way: it just sets it up so that
   when you call ``send_all``, or when you close the send stream, then it
   automatically triggers a call to :func:`memory_stream_pump`, which is
   a convenience function that takes data out of a
   :class:`MemorySendStream`\´s buffer and puts it into a
   :class:`MemoryReceiveStream`\´s buffer. But that's just the default –
   you can replace this with whatever arbitrary behavior you want.

   Trio also provides some specialized functions for testing completely
   **un**\buffered streams: :func:`lockstep_stream_one_way_pair` and
   :func:`lockstep_stream_pair`. These aren't customizable, but they do
   exhibit an extreme kind of behavior that's good at catching out edge
   cases in protocol implementations.


API 详细信息
~~~~~~~~~~~~~~~

**API details**

.. autoclass:: MemorySendStream
   :members:

.. autoclass:: MemoryReceiveStream
   :members:

.. autofunction:: memory_stream_pump

.. autofunction:: memory_stream_one_way_pair

.. autofunction:: memory_stream_pair

.. autofunction:: lockstep_stream_one_way_pair

.. autofunction:: lockstep_stream_pair


.. _testing-custom-streams:

测试自定义流实现
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Testing custom stream implementations**

.. tab:: 中文

   Trio 还提供了一些功能来帮助您测试自定义流实现：

   .. autofunction:: check_one_way_stream

   .. autofunction:: check_two_way_stream

   .. autofunction:: check_half_closeable_stream

.. tab:: 英文

   Trio also provides some functions to help you test your custom stream implementations:

   .. autofunction:: check_one_way_stream
      :no-index:

   .. autofunction:: check_two_way_stream
      :no-index:

   .. autofunction:: check_half_closeable_stream
      :no-index:


.. _virtual-network-hooks:

用于测试的虚拟网络
------------------------------

**Virtual networking for testing**

.. tab:: 中文

   在前一节中，你学到了如何使用虚拟的内存流来测试基于 Trio 的 :class:`~trio.abc.Stream` 抽象编写的协议。但是，如果你有更复杂的网络代码——比如那种连接多个主机、打开监听套接字或发送 UDP 数据包的代码，该怎么办呢？

   Trio 本身并没有提供用于测试的虚拟内存网络实现——但 :mod:`trio.socket` 模块提供了你需要的钩子，来让你自己编写！如果你有兴趣帮助实现一个可重用的虚拟网络用于测试， `请联系我们 <https://github.com/python-trio/trio/issues/170>`__ 。

   请注意，这些 API 实际上位于 :mod:`trio.socket` 和 :mod:`trio.abc` 中，但我们在这里文档化它们，因为它们主要用于测试。

   .. currentmodule:: trio.socket

   .. autofunction:: trio.socket.set_custom_hostname_resolver

   .. currentmodule:: trio.abc

   .. autoclass:: trio.abc.HostnameResolver
      :members:

   .. currentmodule:: trio.socket

   .. autofunction:: trio.socket.set_custom_socket_factory

   .. currentmodule:: trio.abc

   .. autoclass:: trio.abc.SocketFactory
      :members:


.. tab:: 英文

   In the previous section you learned how to use virtual in-memory
   streams to test protocols that are written against Trio's
   :class:`~trio.abc.Stream` abstraction. But what if you have more
   complicated networking code – the kind of code that makes connections
   to multiple hosts, or opens a listening socket, or sends UDP packets?

   Trio doesn't itself provide a virtual in-memory network implementation
   for testing – but :mod:`trio.socket` module does provide the hooks you
   need to write your own! And if you're interested in helping implement
   a reusable virtual network for testing, then `please get in touch
   <https://github.com/python-trio/trio/issues/170>`__.

   Note that these APIs are actually in :mod:`trio.socket` and
   :mod:`trio.abc`, but we document them here because they're primarily
   intended for testing.

   .. currentmodule:: trio.socket

   .. autofunction:: trio.socket.set_custom_hostname_resolver
      :no-index:

   .. currentmodule:: trio.abc

   .. autoclass:: trio.abc.HostnameResolver
      :members:
      :no-index:

   .. currentmodule:: trio.socket

   .. autofunction:: trio.socket.set_custom_socket_factory
      :no-index:

   .. currentmodule:: trio.abc

   .. autoclass:: trio.abc.SocketFactory
      :members:
      :no-index:

.. currentmodule:: trio.testing

测试检查点
--------------------

**Testing checkpoints**

.. autofunction:: assert_checkpoints
   :with:

.. autofunction:: assert_no_checkpoints
   :with:


ExceptionGroup 助手
----------------------

**ExceptionGroup helpers**

.. autoclass:: RaisesGroup
   :members:

.. autoclass:: Matcher
   :members:

.. autoclass:: trio.testing._raises_group._ExceptionInfo
   :members:
