======================
自省和扩展 Trio
======================

**Introspecting and extending Trio with** ``trio.lowlevel``

.. module:: trio.lowlevel

.. tab:: 中文

    :mod:`trio.lowlevel` 包含了用于检查和扩展 Trio 的低级 API。如果你正在编写普通的日常代码，那么可以完全忽略这个模块。但有时你可能需要一些更低级的操作。以下是一些你应该使用 :mod:`trio.lowlevel` 的情况示例：

    * 你想实现 Trio 尚未（但可能未来会）提供的新的 :ref:`同步原语 <synchronization>`，比如读写锁。
    * 你想提取低级别的指标来监控应用程序的健康状况。
    * 你想使用 Trio 尚未（但可能未来会）提供自己封装的低级操作系统接口，比如监听文件系统目录的变化。
    * 你想实现一个接口，在同一进程中调用 Trio 和另一个事件循环。
    * 你正在编写调试器，并希望可视化 Trio 的任务树。
    * 你需要与暴露原始文件描述符的 C 库进行互操作。

    只要你采取适当的预防措施，你不需要害怕 :mod:`trio.lowlevel`。这些是真正的公共 API，具有严格定义和仔细文档化的语义。它们是我们用来实现 :mod:`trio` 命名空间中所有漂亮的高级 API 的工具。但要小心。一些严格的语义有 `可怕的大尖牙
    <https://en.wikipedia.org/wiki/Rabbit_of_Caerbannog>`__ 。如果你犯了错误，Trio 可能无法优雅地处理它；在 Trio 的其他部分严格遵循的约定和保证在这里不一定适用。当你使用这个模块时，必须思考如何处理棘手的情况，从而为你的用户暴露一个友好的 Trio 风格 API。

.. tab:: 英文

    :mod:`trio.lowlevel` contains low-level APIs for introspecting and
    extending Trio. If you're writing ordinary, everyday code, then you
    can ignore this module completely. But sometimes you need something a
    bit lower level. Here are some examples of situations where you should
    reach for :mod:`trio.lowlevel`:

    * You want to implement a new :ref:`synchronization primitive <synchronization>` that Trio doesn't (yet) provide, like a reader-writer lock.
    * You want to extract low-level metrics to monitor the health of your application.
    * You want to use a low-level operating system interface that Trio doesn't (yet) provide its own wrappers for, like watching a filesystem directory for changes.
    * You want to implement an interface for calling between Trio and another event loop within the same process.
    * You're writing a debugger and want to visualize Trio's task tree.
    * You need to interoperate with a C library whose API exposes raw file descriptors.

    You don't need to be scared of :mod:`trio.lowlevel`, as long as you
    take proper precautions. These are real public APIs, with strictly
    defined and carefully documented semantics. They're the same tools we
    use to implement all the nice high-level APIs in the :mod:`trio`
    namespace. But, be careful. Some of those strict semantics have `nasty
    big pointy teeth
    <https://en.wikipedia.org/wiki/Rabbit_of_Caerbannog>`__. If you make a
    mistake, Trio may not be able to handle it gracefully; conventions and
    guarantees that are followed strictly in the rest of Trio do not
    always apply. When you use this module, it's your job to think about
    how you're going to handle the tricky cases so you can expose a
    friendly Trio-style API to your users.


调试和检测
=============================

**Debugging and instrumentation**

.. tab:: 中文

    Trio 努力提供有用的钩子用于调试和检测。上面记录了一些（nursery :ref:`自省属性 <instrumentation>` 、:meth:`trio.Lock.statistics` 等）。这里还有一些。

.. tab:: 英文

    Trio tries hard to provide useful hooks for debugging and
    instrumentation. Some are documented above (the nursery introspection
    attributes, :meth:`trio.Lock.statistics`, etc.). Here are some more.


全局统计
-----------------

**Global statistics**

.. tab:: 中文

    .. function:: current_statistics() -> RunStatistics

        返回包含运行循环级别调试信息的对象：

    .. autoclass:: RunStatistics()

.. tab:: 英文

    .. function:: current_statistics() -> RunStatistics
        :no-index:

        Returns an object containing run-loop-level debugging information:

    .. autoclass:: RunStatistics()
        :no-index:


当前时钟
-----------------

**The current clock**

.. autofunction:: current_clock


.. _instrumentation:

工具 API
--------------

**Instrument API**

.. tab:: 中文

    instrument API 提供了一种标准方式，可以将自定义的监控工具添加到运行循环中。想要制作一个调度延迟的直方图，记录任何阻塞运行循环超过 50 毫秒的任务的堆栈跟踪，或者测量进程运行时间中有多少百分比用于等待 I/O 吗？这里就是你需要的地方。

    一般来说，在任何给定时刻，:func:`trio.run` 都维护着一组“监控工具”，它们是实现了 :class:`trio.abc.Instrument` 接口的对象。当发生有趣的事件时，它会遍历这些监控工具，并通过调用适当的方法来通知它们。教程中有一个 :ref:`使用它进行追踪的简单示例 <tutorial-instrument-example>`。

    由于这在较低级别上钩入了 Trio，因此你必须小心。回调是同步运行的，在许多情况下，如果它们出错，可能没有合理的方式传播这个异常（例如，我们可能已经深入到异常传播机制的内部……）。因此，我们当前的 `策略 <https://github.com/python-trio/trio/issues/47>`__ 是 (a) 将异常记录到 ``"trio.abc.Instrument"`` 日志中，默认情况下会将堆栈跟踪打印到标准错误，并且 (b) 禁用引起问题的监控工具。

    你可以通过将监控工具传递给 :func:`trio.run` 来注册初始的监控工具列表。:func:`add_instrument` 和 :func:`remove_instrument` 允许你在运行时添加和移除监控工具。

    .. autofunction:: add_instrument

    .. autofunction:: remove_instrument
        
    如果你想构建自己的 :class:`~trio.abc.Instrument`，下面是你需要实现的接口：

    .. autoclass:: trio.abc.Instrument
        :members:

    教程中有一个 :ref:`完整示例 <tutorial-instrument-example>`，展示了如何定义自定义监控工具来记录 Trio 的内部调度决策。

.. tab:: 英文

    The instrument API provides a standard way to add custom
    instrumentation to the run loop. Want to make a histogram of
    scheduling latencies, log a stack trace of any task that blocks the
    run loop for >50 ms, or measure what percentage of your process's
    running time is spent waiting for I/O? This is the place.

    The general idea is that at any given moment, :func:`trio.run`
    maintains a set of "instruments", which are objects that implement the
    :class:`trio.abc.Instrument` interface. When an interesting event
    happens, it loops over these instruments and notifies them by calling
    an appropriate method. The tutorial has :ref:`a simple example of
    using this for tracing <tutorial-instrument-example>`.

    Since this hooks into Trio at a rather low level, you do have to be
    careful. The callbacks are run synchronously, and in many cases if
    they error out then there isn't any plausible way to propagate this
    exception (for instance, we might be deep in the guts of the exception
    propagation machinery...). Therefore our `current strategy
    <https://github.com/python-trio/trio/issues/47>`__ for handling
    exceptions raised by instruments is to (a) log an exception to the
    ``"trio.abc.Instrument"`` logger, which by default prints a stack
    trace to standard error and (b) disable the offending instrument.

    You can register an initial list of instruments by passing them to
    :func:`trio.run`. :func:`add_instrument` and
    :func:`remove_instrument` let you add and remove instruments at
    runtime.

    .. autofunction:: add_instrument
        :no-index:

    .. autofunction:: remove_instrument
        :no-index:

    And here's the interface to implement if you want to build your own
    :class:`~trio.abc.Instrument`:

    .. autoclass:: trio.abc.Instrument
        :members:
        :no-index:

    The tutorial has a :ref:`fully-worked example
    <tutorial-instrument-example>` of defining a custom instrument to log
    Trio's internal scheduling decisions.


低级进程生成
==========================

**Low-level process spawning**

.. autofunction:: trio.lowlevel.open_process


低级 I/O 原语
========================

**Low-level I/O primitives**

.. tab:: 中文

    不同的环境暴露了不同的低级 API 用于执行异步 I/O。:mod:`trio.lowlevel` 以相对直接的方式暴露这些 API，以便为更高级别的代码提供最大限度的能力和灵活性。然而，这也意味着提供的具体 API 可能会根据 Trio 运行的系统有所不同。

.. tab:: 英文

    Different environments expose different low-level APIs for performing
    async I/O. :mod:`trio.lowlevel` exposes these APIs in a relatively
    direct way, so as to allow maximum power and flexibility for higher
    level code. However, this means that the exact API provided may vary
    depending on what system Trio is running on.


通用 API
-------------------------

**Universally available API**

.. tab:: 中文

    所有环境都提供以下函数：

    .. function:: wait_readable(obj)
        :async:

        阻塞，直到内核报告给定对象可读。

        在 Unix 系统上，``obj`` 必须是一个整数文件描述符，或者是一个具有 ``.fileno()`` 方法并返回整数文件描述符的对象。任何类型的文件描述符都可以传递，尽管具体的语义会依赖于你的内核。例如，这可能对磁盘文件没有任何实质性的作用。

        在 Windows 系统上，``obj`` 必须是一个整数 ``SOCKET`` 句柄，或者是一个具有 ``.fileno()`` 方法并返回整数 ``SOCKET`` 句柄的对象。文件描述符不被支持，句柄也不能指向除 ``SOCKET`` 以外的任何对象。

        :raises trio.BusyResourceError:
            如果另一个任务已经在等待给定的套接字变为可读。
        :raises trio.ClosedResourceError:
            如果另一个任务在此函数仍在工作时调用了 :func:`notify_closing`。

    .. function:: wait_writable(obj)
        :async:

        阻塞，直到内核报告给定对象可写。

        请参阅 `wait_readable` 中对 ``obj`` 的定义。

        :raises trio.BusyResourceError:
            如果另一个任务已经在等待给定的套接字变为可写。
        :raises trio.ClosedResourceError:
            如果另一个任务在此函数仍在工作时调用了 :func:`notify_closing`。

    .. function:: notify_closing(obj)

        在关闭文件描述符（在 Unix 上）或套接字（在 Windows 上）之前调用此函数。这将导致对给定对象的任何 :func:`wait_readable` 或 :func:`wait_writable` 调用立即唤醒并引发 :exc:`~trio.ClosedResourceError`。

        这实际上并不会关闭对象——你仍然需要在之后自己关闭它。另外，在你调用此函数和实际关闭对象之间，你需要小心确保没有新的任务开始等待该对象。所以，正确关闭某个对象通常需要按以下步骤操作：

        1. 明确标记对象为已关闭，以便任何新的使用尝试在开始之前就会中止。
        2. 调用 :func:`notify_closing` 唤醒任何已经存在的使用者。
        3. 实际关闭对象。

        如果这更方便，也可以按不同的顺序执行这些步骤，*但前提是* 确保在步骤之间没有任何检查点。这样它们都会在一个原子步骤中完成，其他任务就无法知道它们的执行顺序了。

.. tab:: 英文

    All environments provide the following functions:

    .. function:: wait_readable(obj)
        :no-index:
        :async:

    Block until the kernel reports that the given object is readable.

    On Unix systems, ``obj`` must either be an integer file descriptor,
    or else an object with a ``.fileno()`` method which returns an
    integer file descriptor. Any kind of file descriptor can be passed,
    though the exact semantics will depend on your kernel. For example,
    this probably won't do anything useful for on-disk files.

    On Windows systems, ``obj`` must either be an integer ``SOCKET``
    handle, or else an object with a ``.fileno()`` method which returns
    an integer ``SOCKET`` handle. File descriptors aren't supported,
    and neither are handles that refer to anything besides a
    ``SOCKET``.

    :raises trio.BusyResourceError:
        if another task is already waiting for the given socket to
        become readable.
    :raises trio.ClosedResourceError:
        if another task calls :func:`notify_closing` while this
        function is still working.

    .. function:: wait_writable(obj)
        :no-index:
        :async:

    Block until the kernel reports that the given object is writable.

    See `wait_readable` for the definition of ``obj``.

    :raises trio.BusyResourceError:
        if another task is already waiting for the given socket to
        become writable.
    :raises trio.ClosedResourceError:
        if another task calls :func:`notify_closing` while this
        function is still working.


    .. function:: notify_closing(obj)
        :no-index:

        Call this before closing a file descriptor (on Unix) or socket (on
        Windows). This will cause any :func:`wait_readable` or :func:`wait_writable`
        calls on the given object to immediately wake up and raise
        :exc:`~trio.ClosedResourceError`.

        This doesn't actually close the object – you still have to do that
        yourself afterwards. Also, you want to be careful to make sure no
        new tasks start waiting on the object in between when you call this
        and when it's actually closed. So to close something properly, you
        usually want to do these steps in order:

        1. Explicitly mark the object as closed, so that any new attempts
            to use it will abort before they start.
        2. Call :func:`notify_closing` to wake up any already-existing users.
        3. Actually close the object.

        It's also possible to do them in a different order if that's more
        convenient, *but only if* you make sure not to have any checkpoints in
        between the steps. This way they all happen in a single atomic
        step, so other tasks won't be able to tell what order they happened
        in anyway.


Unix 特定 API
-----------------

**Unix-specific API**

.. tab:: 中文

    :class:`FdStream` 支持将 Unix 文件（例如管道或 TTY）包装为流。

    如果你有两个不同的文件描述符用于发送和接收，并希望将它们捆绑在一起形成一个单一的双向 :class:`~trio.abc.Stream`，那么可以使用 :class:`trio.StapledStream`：

    .. code-block:: python

        bidirectional_stream = trio.StapledStream(
            trio.lowlevel.FdStream(write_fd),
            trio.lowlevel.FdStream(read_fd)
        )

    .. autoclass:: FdStream
        :show-inheritance:
        :members:

.. tab:: 英文

    :class:`FdStream` supports wrapping Unix files (such as a pipe or TTY) as
    a stream.

    If you have two different file descriptors for sending and receiving,
    and want to bundle them together into a single bidirectional
    :class:`~trio.abc.Stream`, then use :class:`trio.StapledStream`:

    .. code-block:: python

        bidirectional_stream = trio.StapledStream(
            trio.lowlevel.FdStream(write_fd),
            trio.lowlevel.FdStream(read_fd)
        )

    .. autoclass:: FdStream
        :show-inheritance:
        :members:
        :no-index:


Kqueue 特定 API
-------------------

**Kqueue-specific API**

.. tab:: 中文

    TODO: 这些已经实现，但目前更像是草图而非实际功能。请参阅 `#26 <https://github.com/python-trio/trio/issues/26>`__。

    .. function:: current_kqueue()

    .. function:: wait_kevent(ident, filter, abort_func)
        :async:

    .. function:: monitor_kevent(ident, filter)
        :with: queue

.. tab:: 英文

    TODO: these are implemented, but are currently more of a sketch than anything real. See `#26 <https://github.com/python-trio/trio/issues/26>`__.

    .. function:: current_kqueue()
        :no-index:

    .. function:: wait_kevent(ident, filter, abort_func)
        :no-index:
        :async:

    .. function:: monitor_kevent(ident, filter)
        :no-index:
        :with: queue


Windows 特定 API
--------------------

**Windows-specific API**

.. function:: WaitForSingleObject(handle)
    :async:

    Async and cancellable variant of `WaitForSingleObject
    <https://msdn.microsoft.com/en-us/library/windows/desktop/ms687032(v=vs.85).aspx>`__.
    Windows only.

    :arg handle:
        A Win32 object handle, as a Python integer.
    :raises OSError:
        If the handle is invalid, e.g. when it is already closed.


TODO: these are implemented, but are currently more of a sketch than
anything real. See `#26
<https://github.com/python-trio/trio/issues/26>`__ and `#52
<https://github.com/python-trio/trio/issues/52>`__.

.. function:: register_with_iocp(handle)

.. function:: wait_overlapped(handle, lpOverlapped)
   :async:

.. function:: write_overlapped(handle, data)
   :async:

.. function:: readinto_overlapped(handle, data)
   :async:

.. function:: current_iocp()

.. function:: monitor_completion_key()
   :with: queue


全局状态：系统任务和运行局部变量
==================================================

**Global state: system tasks and run-local variables**

.. autoclass:: RunVar

.. autofunction:: spawn_system_task


Trio 令牌
===========

**Trio tokens**

.. autoclass:: TrioToken()
   :members:

.. autofunction:: current_trio_token


生成线程
================

**Spawning threads**

.. autofunction:: start_thread_soon


更安全的键盘中断处理
================================

**Safer KeyboardInterrupt handling**

.. tab:: 中文

    Trio 对 Ctrl-C 的处理旨在平衡可用性和安全性。一方面，在一些敏感区域（如核心调度循环）内，处理任意的 :exc:`KeyboardInterrupt` 异常是不可能的，同时又能保持核心正确性的约束。另一方面，如果用户不小心写了一个无限循环，我们确实希望能够中断它。我们的解决方案是安装一个默认的信号处理器，在信号接收到的地方检查是否可以安全地抛出 :exc:`KeyboardInterrupt`。如果可以，就抛出；否则，我们将在下一个可用的时机调度一个 :exc:`KeyboardInterrupt`，将其传递给主任务（类似于 :exc:`~trio.Cancelled` 如何传递）。

    这很好，但 – 我们如何知道自己是否在程序的敏感部分呢？

    这个问题是通过逐个函数来决定的。默认情况下：

    - 普通用户任务中的顶级函数是没有保护的。
    - 系统任务中的顶级函数是有保护的。
    - 如果一个函数没有特别说明，那么它会继承调用者的保护状态。

    这意味着你只需要在从受保护代码过渡到非受保护代码，或从非受保护代码过渡到受保护代码的地方覆盖默认设置。

    这些过渡是通过两个函数装饰器来实现的：

    .. function:: disable_ki_protection()
        :decorator:

        装饰器，用于标记给定的普通函数、生成器函数、异步函数或异步生成器函数在处理 :exc:`KeyboardInterrupt` 时没有保护，即该函数中的代码 *可以* 被 :exc:`KeyboardInterrupt` 在任何时候强行中断。

        如果同一个函数上有多个装饰器，应该将此装饰器放在最底部（最靠近实际函数的位置）。

        一个使用此装饰器的示例是在实现像 :func:`trio.from_thread.run` 这样的函数时，后者使用 :meth:`TrioToken.run_sync_soon` 进入 Trio 线程。:meth:`~TrioToken.run_sync_soon` 的回调是在启用 :exc:`KeyboardInterrupt` 保护的情况下运行的，而 :func:`trio.from_thread.run` 利用这一点安全地设置将响应发送回原线程的机制，但在进入用户提供的函数时使用 :func:`disable_ki_protection`。

    .. function:: enable_ki_protection()
        :decorator:

        装饰器，用于标记给定的普通函数、生成器函数、异步函数或异步生成器函数在处理 :exc:`KeyboardInterrupt` 时是受保护的，即该函数中的代码 *不会* 被 :exc:`KeyboardInterrupt` 强行中断。（尽管如果它包含任何 :ref:`检查点 <checkpoints>`，那么在这些检查点处仍然可以接收 :exc:`KeyboardInterrupt`，这被视为一种礼貌的中断。）

        .. warning::

            请非常小心，仅在你知道某个函数会在有限时间内退出，或者定期经过检查点时，才使用此装饰器。（当然，你的所有函数都应该具备这个特性，但如果在这里搞错了，你甚至无法使用 Ctrl-C 来退出！）

        如果同一个函数上有多个装饰器，应该将此装饰器放在最底部（最靠近实际函数的位置）。

        一个使用此装饰器的示例是在像 :class:`~trio.Lock` 这样的对象的 ``__exit__`` 实现中，如果 :exc:`KeyboardInterrupt` 发生在不恰当的时机，可能会导致锁处于不一致的状态，从而引发死锁。

        由于 :exc:`KeyboardInterrupt` 保护是按代码对象追踪的，任何尝试以不同方式条件性地保护相同代码块的做法可能不会按预期行为执行。如果你试图条件性地保护一个闭包，它会变成无条件保护::

            def example(protect: bool) -> bool:
                def inner() -> bool:
                    return trio.lowlevel.currently_ki_protected()
                if protect:
                    inner = trio.lowlevel.enable_ki_protection(inner)
                return inner()

            async def amain():
                assert example(False) == False
                assert example(True) == True  # 一旦被保护...
                assert example(False) == True  # ...总是被保护

            trio.run(amain)

        如果你确实需要条件性保护，可以通过为闭包的每个 KI 保护实例提供独立的代码对象来实现::

            def example(protect: bool) -> bool:
                def inner() -> bool:
                    return trio.lowlevel.currently_ki_protected()
                if protect:
                    inner.__code__ = inner.__code__.replace()
                    inner = trio.lowlevel.enable_ki_protection(inner)
                return inner()

            async def amain():
                assert example(False) == False
                assert example(True) == True
                assert example(False) == False

            trio.run(amain)

        （默认情况下不这样做，因为它会带来一些内存开销，并减少在 CPython 最新版本中优化特化的潜力。）

    .. autofunction:: currently_ki_protected


.. tab:: 英文

    Trio's handling of control-C is designed to balance usability and
    safety. On the one hand, there are sensitive regions (like the core
    scheduling loop) where it's simply impossible to handle arbitrary
    :exc:`KeyboardInterrupt` exceptions while maintaining our core
    correctness invariants. On the other, if the user accidentally writes
    an infinite loop, we do want to be able to break out of that. Our
    solution is to install a default signal handler which checks whether
    it's safe to raise :exc:`KeyboardInterrupt` at the place where the
    signal is received. If so, then we do; otherwise, we schedule a
    :exc:`KeyboardInterrupt` to be delivered to the main task at the next
    available opportunity (similar to how :exc:`~trio.Cancelled` is
    delivered).

    So that's great, but – how do we know whether we're in one of the
    sensitive parts of the program or not?

    This is determined on a function-by-function basis. By default:

    - The top-level function in regular user tasks is unprotected.
    - The top-level function in system tasks is protected.
    - If a function doesn't specify otherwise, then it inherits the
      protection state of its caller.

    This means you only need to override the defaults at places where you
    transition from protected code to unprotected code or vice-versa.

    These transitions are accomplished using two function decorators:

    .. function:: disable_ki_protection()
        :no-index:
        :decorator:

        Decorator that marks the given regular function, generator
        function, async function, or async generator function as
        unprotected against :exc:`KeyboardInterrupt`, i.e., the code inside
        this function *can* be rudely interrupted by
        :exc:`KeyboardInterrupt` at any moment.

        If you have multiple decorators on the same function, then this
        should be at the bottom of the stack (closest to the actual
        function).

        An example of where you'd use this is in implementing something
        like :func:`trio.from_thread.run`, which uses
        :meth:`TrioToken.run_sync_soon` to get into the Trio
        thread. :meth:`~TrioToken.run_sync_soon` callbacks are run with
        :exc:`KeyboardInterrupt` protection enabled, and
        :func:`trio.from_thread.run` takes advantage of this to safely set up
        the machinery for sending a response back to the original thread, but
        then uses :func:`disable_ki_protection` when entering the
        user-provided function.

    .. function:: enable_ki_protection()
        :no-index:
        :decorator:

        Decorator that marks the given regular function, generator
        function, async function, or async generator function as protected
        against :exc:`KeyboardInterrupt`, i.e., the code inside this
        function *won't* be rudely interrupted by
        :exc:`KeyboardInterrupt`. (Though if it contains any
        :ref:`checkpoints <checkpoints>`, then it can still receive
        :exc:`KeyboardInterrupt` at those. This is considered a polite
        interruption.)

        .. warning::

            Be very careful to only use this decorator on functions that you
            know will either exit in bounded time, or else pass through a
            checkpoint regularly. (Of course all of your functions should
            have this property, but if you mess it up here then you won't
            even be able to use control-C to escape!)

        If you have multiple decorators on the same function, then this
        should be at the bottom of the stack (closest to the actual
        function).

        An example of where you'd use this is on the ``__exit__``
        implementation for something like a :class:`~trio.Lock`, where a
        poorly-timed :exc:`KeyboardInterrupt` could leave the lock in an
        inconsistent state and cause a deadlock.

        Since KeyboardInterrupt protection is tracked per code object, any attempt to
        conditionally protect the same block of code in different ways is unlikely to behave
        how you expect. If you try to conditionally protect a closure, it will be
        unconditionally protected instead::

            def example(protect: bool) -> bool:
                def inner() -> bool:
                    return trio.lowlevel.currently_ki_protected()
                if protect:
                    inner = trio.lowlevel.enable_ki_protection(inner)
                return inner()

            async def amain():
                assert example(False) == False
                assert example(True) == True  # once protected ...
                assert example(False) == True  # ... always protected

            trio.run(amain)

        If you really need conditional protection, you can achieve it by giving each
        KI-protected instance of the closure its own code object::

            def example(protect: bool) -> bool:
                def inner() -> bool:
                    return trio.lowlevel.currently_ki_protected()
                if protect:
                    inner.__code__ = inner.__code__.replace()
                    inner = trio.lowlevel.enable_ki_protection(inner)
                return inner()

            async def amain():
                assert example(False) == False
                assert example(True) == True
                assert example(False) == False

            trio.run(amain)

        (This isn't done by default because it carries some memory overhead and reduces
        the potential for specializing optimizations in recent versions of CPython.)

    .. autofunction:: currently_ki_protected
        :no-index:


睡眠和唤醒
===================

**Sleeping and waking**

等待队列抽象
----------------------

**Wait queue abstraction**

.. autoclass:: ParkingLot
   :members:
   :undoc-members:

.. autoclass:: ParkingLotStatistics
   :members:

.. autofunction:: add_parking_lot_breaker

.. autofunction:: remove_parking_lot_breaker

低级检查点函数
------------------------------

**Low-level checkpoint functions**

.. tab:: 中文

    .. autofunction:: checkpoint

    接下来的两个函数是 *一起* 使用的，构成一个检查点：

    .. autofunction:: checkpoint_if_cancelled
    .. autofunction:: cancel_shielded_checkpoint

    这些函数通常用于那些可能会阻塞也可能不会阻塞的操作中，并且你想实现 Trio 的标准检查点语义。示例：

    .. code-block:: python

        async def operation_that_maybe_blocks():
            await checkpoint_if_cancelled()
            try:
                ret = attempt_operation()
            except BlockingIOError:
                # 需要阻塞并重试，下面会执行
                pass
            else:
                # 操作成功，完成检查点然后返回
                await cancel_shielded_checkpoint()
                return ret
            while True:
                await wait_for_operation_to_be_ready()
                try:
                    return attempt_operation()
                except BlockingIOError:
                    pass

    这个逻辑有点复杂，但它完成了以下所有操作：

    * 每个成功的执行路径都会经过一个检查点（假设 ``wait_for_operation_to_be_ready`` 是一个无条件的检查点）

    * 我们的 :ref:`取消语义 <cancellable-primitives>` 规定，只有当操作未执行时，才会抛出 :exc:`~trio.Cancelled`。在早期退出分支中使用 :func:`cancel_shielded_checkpoint` 实现了这一点。

    * 在我们最终会阻塞的路径上，我们在阻塞之前不会通过任何调度点，从而避免了一些不必要的工作。

    * 通过将 ``while True:`` 循环放在 ``except BlockingIOError:`` 块之外，避免了将 :exc:`BlockingIOError` 隐式地与 ``attempt_operation`` 或 ``wait_for_operation_to_be_ready`` 中抛出的任何错误串联起来。

    这些函数在其他情况下也非常有用。例如，当 :func:`trio.to_thread.run_sync` 在工作线程中调度一些工作时，它会阻塞直到工作完成（因此它是一个调度点），但默认情况下不允许取消。所以，为了确保该调用始终作为一个检查点执行，它会在启动线程之前调用 :func:`checkpoint_if_cancelled`。

.. tab:: 英文

    .. autofunction:: checkpoint
        :no-index:

    The next two functions are used *together* to make up a checkpoint:

    .. autofunction:: checkpoint_if_cancelled
        :no-index:
    .. autofunction:: cancel_shielded_checkpoint
        :no-index:

    These are commonly used in cases where you have an operation that
    might-or-might-not block, and you want to implement Trio's standard
    checkpoint semantics. Example:

    .. code-block:: python

        async def operation_that_maybe_blocks():
            await checkpoint_if_cancelled()
            try:
                ret = attempt_operation()
            except BlockingIOError:
                # need to block and then retry, which we do below
                pass
            else:
                # operation succeeded, finish the checkpoint then return
                await cancel_shielded_checkpoint()
                return ret
            while True:
                await wait_for_operation_to_be_ready()
                try:
                    return attempt_operation()
                except BlockingIOError:
                    pass

    This logic is a bit convoluted, but accomplishes all of the following:

    * Every successful execution path passes through a checkpoint (assuming that ``wait_for_operation_to_be_ready`` is an unconditional checkpoint)

    * Our :ref:`cancellation semantics <cancellable-primitives>` say that :exc:`~trio.Cancelled` should only be raised if the operation didn't happen. Using :func:`cancel_shielded_checkpoint` on the early-exit branch accomplishes this.

    * On the path where we do end up blocking, we don't pass through any schedule points before that, which avoids some unnecessary work.

    * Avoids implicitly chaining the :exc:`BlockingIOError` with any errors raised by ``attempt_operation`` or ``wait_for_operation_to_be_ready``, by keeping the ``while True:`` loop outside of the ``except BlockingIOError:`` block.

    These functions can also be useful in other situations. For example,
    when :func:`trio.to_thread.run_sync` schedules some work to run in a
    worker thread, it blocks until the work is finished (so it's a
    schedule point), but by default it doesn't allow cancellation. So to
    make sure that the call always acts as a checkpoint, it calls
    :func:`checkpoint_if_cancelled` before starting the thread.


低级阻塞
------------------

**Low-level blocking**

.. tab:: 中文

    .. autofunction:: wait_task_rescheduled
    .. autoclass:: Abort
    .. autofunction:: reschedule

    这里有一个使用 :func:`wait_task_rescheduled` 直接实现的锁类示例。该实现存在一些缺陷，包括缺乏公平性、O(n) 的取消操作、缺少错误检查、未在非阻塞路径上插入检查点等。如果你真的想实现自己的锁，应该研究 :class:`trio.Lock` 的实现，并使用 :class:`ParkingLot`，它为你解决了一些这些问题。但这个示例确实说明了 :func:`wait_task_rescheduled` API 的基本结构：

    .. code-block:: python

        class NotVeryGoodLock:
            def __init__(self):
                self._blocked_tasks = collections.deque()
                self._held = False

            async def acquire(self):
                # 我们可能需要多次尝试才能获得锁。
                while self._held:
                    # 有其他人持有锁，因此我们需要等待。
                    task = trio.lowlevel.current_task()
                    self._blocked_tasks.append(task)
                    def abort_fn(_):
                        self._blocked_tasks.remove(task)
                        return trio.lowlevel.Abort.SUCCEEDED
                    await trio.lowlevel.wait_task_rescheduled(abort_fn)
                    # 在这一点，锁已经被释放了——但是可能在我们醒来之前，
                    # 别人已经抢先拿到了锁。所以我们要重新检查 'while' 条件。
                # 如果我们到达这一点，意味着 'while' 条件刚刚失败，所以我们知道没有人持有锁，
                # 并且我们可以获取它。
                self._held = True

            def release(self):
                self._held = False
                if self._blocked_tasks:
                    woken_task = self._blocked_tasks.popleft()
                trio.lowlevel.reschedule(woken_task)

.. tab:: 英文

    .. autofunction:: wait_task_rescheduled
        :no-index:
    .. autoclass:: Abort
        :no-index:
    .. autofunction:: reschedule
        :no-index:

    Here's an example lock class implemented using
    :func:`wait_task_rescheduled` directly. This implementation has a
    number of flaws, including lack of fairness, O(n) cancellation,
    missing error checking, failure to insert a checkpoint on the
    non-blocking path, etc. If you really want to implement your own lock,
    then you should study the implementation of :class:`trio.Lock` and use
    :class:`ParkingLot`, which handles some of these issues for you. But
    this does serve to illustrate the basic structure of the
    :func:`wait_task_rescheduled` API:

    .. code-block:: python

        class NotVeryGoodLock:
            def __init__(self):
                self._blocked_tasks = collections.deque()
                self._held = False

            async def acquire(self):
                # We might have to try several times to acquire the lock.
                while self._held:
                    # Someone else has the lock, so we have to wait.
                    task = trio.lowlevel.current_task()
                    self._blocked_tasks.append(task)
                    def abort_fn(_):
                        self._blocked_tasks.remove(task)
                        return trio.lowlevel.Abort.SUCCEEDED
                    await trio.lowlevel.wait_task_rescheduled(abort_fn)
                    # At this point the lock was released -- but someone else
                    # might have swooped in and taken it again before we
                    # woke up. So we loop around to check the 'while' condition
                    # again.
                # if we reach this point, it means that the 'while' condition
                # has just failed, so we know no-one is holding the lock, and
                # we can take it.
                self._held = True

            def release(self):
                self._held = False
                if self._blocked_tasks:
                    woken_task = self._blocked_tasks.popleft()
                    trio.lowlevel.reschedule(woken_task)


任务 API
========

**Task API**

.. autofunction:: current_root_task()

.. autofunction:: current_task()

.. class:: Task()

   A :class:`Task` object represents a concurrent "thread" of
   execution. It has no public constructor; Trio internally creates a
   :class:`Task` object for each call to ``nursery.start(...)`` or
   ``nursery.start_soon(...)``.

   Its public members are mostly useful for introspection and
   debugging:

   .. attribute:: name

      String containing this :class:`Task`\'s name. Usually the name
      of the function this :class:`Task` is running, but can be
      overridden by passing ``name=`` to ``start`` or ``start_soon``.

   .. attribute:: coro

      This task's coroutine object.

   .. automethod:: iter_await_frames

   .. attribute:: context

      This task's :class:`contextvars.Context` object.

   .. autoattribute:: parent_nursery

   .. autoattribute:: eventual_parent_nursery

   .. autoattribute:: child_nurseries

   .. attribute:: custom_sleep_data

      Trio doesn't assign this variable any meaning, except that it
      sets it to ``None`` whenever a task is rescheduled. It can be
      used to share data between the different tasks involved in
      putting a task to sleep and then waking it up again. (See
      :func:`wait_task_rescheduled` for details.)

.. _guest-mode:

使用“访客模式”在其他事件循环之上运行 Trio
==========================================================

**Using "guest mode" to run Trio on top of other event loops**

什么是“访客模式”？
---------------------

**What is "guest mode"?**

.. tab:: 中文

    事件循环充当中央协调器，管理程序中的所有 IO 操作。通常，这意味着你的应用程序需要选择一个事件循环，并将其用于所有操作。但如果你喜欢 Trio，并且还需要使用像 `Qt <https://en.wikipedia.org/wiki/Qt_(software)>`__ 或 `PyGame <https://www.pygame.org/>`__ 这样有自己事件循环的框架呢？那你就需要一种方法同时运行这两个事件循环。

    确实可以将多个事件循环结合起来，但标准的做法都有显著的缺点：

    - **轮询：** 这种方式是使用 `忙等待 <https://en.wikipedia.org/wiki/Busy_waiting>`__ 来手动检查两个事件循环的 IO，每秒多次。这会增加延迟，浪费 CPU 时间和电力。

    - **可插拔 IO 后端：** 这种方式是将一个事件循环的 API 重新实现为另一个事件循环的 API，这样你实际上只有一个事件循环。这需要为每对你想要集成的事件循环进行大量工作，并且不同的后端最终会导致不一致的行为，迫使用户按照最小公分母来编程。如果两个事件循环暴露的功能集不同，甚至可能无法将其中一个事件循环实现为另一个的形式。

    - **在不同的线程中运行两个事件循环：** 这种方法可行，但大多数事件循环的 API 都不是线程安全的，因此在这种方法中，你需要小心追踪哪些代码在哪个事件循环中运行，并且每次与另一个事件循环交互时都必须使用显式的线程间消息传递——否则就可能面临隐晦的竞态条件和数据损坏。

    因此，Trio 提供了第四种选择：**来宾模式**。来宾模式允许你在其他“主机”事件循环（如 Qt）上运行 :func:`trio.run`。它的优点有：

    - **高效性：** 来宾模式是事件驱动的，而不是使用忙等待，因此它具有低延迟，不浪费电力。

    - **无需考虑线程：** 你的 Trio 代码与主机事件循环运行在同一个线程中，因此你可以自由地从主机调用同步的 Trio API，并且从 Trio 调用同步的主机 API。例如，如果你正在使用 Qt 作为主机循环制作 GUI 应用，那么创建一个 `取消按钮 <https://doc.qt.io/qt-5/qpushbutton.html>`__ 并将其连接到 :class:`trio.CancelScope` 就像编写以下代码一样简单：

      .. code-block:: python

            # Trio 代码可以创建 Qt 对象而不需要任何特别的步骤...
            my_cancel_button = QPushButton("Cancel")
            # ...Qt 也可以轻松地回调 Trio
            my_cancel_button.clicked.connect(my_cancel_scope.cancel)

      （对于异步 API，事情就不那么简单了，但你可以使用同步 API 在两个世界之间建立显式的桥梁，例如通过队列来传递异步函数及其结果。）

    - **一致的行为：** 来宾模式使用与常规 Trio 相同的代码：相同的调度器，相同的 IO 代码，完全相同的实现。所以你可以获得完整的功能集，所有东西都会按预期行为工作。

    - **简单的集成和广泛的兼容性：** 几乎所有的事件循环都提供某种线程安全的“调度回调”操作，而这正是你需要的，可以用它作为主机事件循环。


.. tab:: 英文

    An event loop acts as a central coordinator to manage all the IO happening in your program. Normally, that means that your application has to pick one event loop, and use it for everything. But what if you like Trio, but also need to use a framework like `Qt <https://en.wikipedia.org/wiki/Qt_(software)>`__ or `PyGame <https://www.pygame.org/>`__ that has its own event loop? Then you need some way to run both event loops at once.

    It is possible to combine event loops, but the standard approaches all have significant downsides:

    - **Polling:** this is where you use a `busy-loop <https://en.wikipedia.org/wiki/Busy_waiting>`__ to manually check for IO on both event loops many times per second. This adds latency, and wastes CPU time and electricity.

    - **Pluggable IO backends:** this is where you reimplement one of the event loop APIs on top of the other, so you effectively end up with just one event loop. This requires a significant amount of work for each pair of event loops you want to integrate, and different backends inevitably end up with inconsistent behavior, forcing users to program against the least-common-denominator. And if the two event loops expose different feature sets, it may not even be possible to implement one in terms of the other.

    - **Running the two event loops in separate threads:** This works, but most event loop APIs aren't thread-safe, so in this approach you need to keep careful track of which code runs on which event loop, and remember to use explicit inter-thread messaging whenever you interact with the other loop – or else risk obscure race conditions and data corruption.

    That's why Trio offers a fourth option: **guest mode**. Guest mode lets you execute `trio.run` on top of some other "host" event loop, like Qt. Its advantages are:

    - Efficiency: guest mode is event-driven instead of using a busy-loop, so it has low latency and doesn't waste electricity.

    - No need to think about threads: your Trio code runs in the same thread as the host event loop, so you can freely call sync Trio APIs from the host, and call sync host APIs from Trio. For example, if you're making a GUI app with Qt as the host loop, then making a `cancel button <https://doc.qt.io/qt-5/qpushbutton.html>`__ and connecting it to a `trio.CancelScope` is as easy as writing:

        .. code-block:: python

            # Trio code can create Qt objects without any special ceremony...
            my_cancel_button = QPushButton("Cancel")
            # ...and Qt can call back to Trio just as easily
            my_cancel_button.clicked.connect(my_cancel_scope.cancel)

        (For async APIs, it's not that simple, but you can use sync APIs to
        build explicit bridges between the two worlds, e.g. by passing async
        functions and their results back and forth through queues.)

    - Consistent behavior: guest mode uses the same code as regular Trio: the same scheduler, same IO code, same everything. So you get the full feature set and everything acts the way you expect.

    - Simple integration and broad compatibility: pretty much every event loop offers some threadsafe "schedule a callback" operation, and that's all you need to use it as a host loop.


真的吗？怎么可能？
-----------------------------

**Really? How is that possible?**

.. tab:: 中文

    .. note::

        你可以在不阅读本节的情况下使用来宾模式。此部分是为那些喜欢了解工作原理的人准备的。

    所有事件循环的基本结构是相同的。它们反复执行两个操作：

    1. 等待操作系统通知它们发生了某些有趣的事情，比如数据到达一个套接字或者超时已过。它们通过调用平台特定的 ``sleep_until_something_happens()`` 系统调用来实现这一点——例如 ``select``、 ``epoll``、 ``kqueue``、 ``GetQueuedCompletionEvents`` 等等。

    2. 执行所有关心所发生事情的用户任务，然后返回第一步。

    问题出在第一步。两个不同的事件循环在同一个线程中可以轮流执行第二步中的用户任务，但当它们处于空闲状态且没有任何事情发生时，它们不能同时调用各自的 ``sleep_until_something_happens()`` 函数。

    “轮询”和“可插拔后端”策略通过修改事件循环来解决这个问题，让两个第一步可以在同一线程中同时运行。将所有内容保持在一个线程中对第二步很好，但第一步的修改会引发问题。

    “分离线程”策略通过将两个步骤移动到不同的线程中来解决这个问题。这使得第一步可以正常工作，但缺点是，第二步中的用户任务也会在单独的线程中运行，因此用户必须处理线程间的协调问题。

    来宾模式的想法是结合每种方法的优点：我们将 Trio 的第一步移到一个独立的工作线程中，同时将 Trio 的第二步保持在主机主线程中。这样，当应用程序空闲时，两个事件循环会在各自的线程中同时执行 ``sleep_until_something_happens()``。但是，当应用程序唤醒并且你的代码实际运行时，所有操作都发生在一个线程中。线程的复杂性完全由 Trio 透明地处理。

    具体来说，我们将 Trio 的内部事件循环展开成一个回调链，每当一个回调完成时，它会根据需要将下一个回调安排到主机事件循环或工作线程中。因此，主机事件循环需要提供的唯一功能是将回调从工作线程调度到主线程。

    Trio 与主机事件循环之间的协调确实增加了一些开销。主要的成本是在线程之间切换，因为这需要线程间消息传递。这个成本是比较低的（大约几微秒，假设主机事件循环高效实现），但并不是免费的。

    不过，我们可以进行一个不错的优化：我们只在 ``sleep_until_something_happens()`` 调用实际上进入休眠时需要线程，也就是说，当 Trio 部分的程序空闲且没有任务时。在切换到工作线程之前，我们会再次检查是否空闲，如果不是，就跳过工作线程，直接进入第二步。这意味着你的应用程序只有在它本该休眠的时候才会支付额外的线程切换成本，因此它对应用程序整体性能的影响应该是最小的。

    总的开销将取决于你的主机事件循环、平台、应用程序等。但我们预计，在大多数情况下，以来宾模式运行的应用程序应该比使用 :func:`trio.run` 的相同代码慢 5-10%。如果你发现这个估算不适用于你的应用，请告诉我们，我们会看看是否能解决它！

.. tab:: 英文

    .. note::

        You can use guest mode without reading this section. It's included for those who enjoy understanding how things work.

    All event loops have the same basic structure. They loop through two operations, over and over:

    1. Wait for the operating system to notify them that something interesting has happened, like data arriving on a socket or a timeout passing. They do this by invoking a platform-specific ``sleep_until_something_happens()`` system call – ``select``, ``epoll``, ``kqueue``, ``GetQueuedCompletionEvents``, etc.

    2. Run all the user tasks that care about whatever happened, then go back to step 1.

    The problem here is step 1. Two different event loops on the same
    thread can take turns running user tasks in step 2, but when they're
    idle and nothing is happening, they can't both invoke their own
    ``sleep_until_something_happens()`` function at the same time.

    The "polling" and "pluggable backend" strategies solve this by hacking
    the loops so both step 1s can run at the same time in the same thread.
    Keeping everything in one thread is great for step 2, but the step 1
    hacks create problems.

    The "separate threads" strategy solves this by moving both steps into
    separate threads. This makes step 1 work, but the downside is that now
    the user tasks in step 2 are running separate threads as well, so
    users are forced to deal with inter-thread coordination.

    The idea behind guest mode is to combine the best parts of each
    approach: we move Trio's step 1 into a separate worker thread, while
    keeping Trio's step 2 in the main host thread. This way, when the
    application is idle, both event loops do their
    ``sleep_until_something_happens()`` at the same time in their own
    threads. But when the app wakes up and your code is actually running,
    it all happens in a single thread. The threading trickiness is all
    handled transparently inside Trio.

    Concretely, we unroll Trio's internal event loop into a chain of
    callbacks, and as each callback finishes, it schedules the next
    callback onto the host loop or a worker thread as appropriate. So the
    only thing the host loop has to provide is a way to schedule a
    callback onto the main thread from a worker thread.

    Coordinating between Trio and the host loop does add some overhead.
    The main cost is switching in and out of the background thread, since
    this requires cross-thread messaging. This is cheap (on the order of a
    few microseconds, assuming your host loop is implemented efficiently),
    but it's not free.

    But, there's a nice optimization we can make: we only *need* the
    thread when our ``sleep_until_something_happens()`` call actually
    sleeps, that is, when the Trio part of your program is idle and has
    nothing to do. So before we switch into the worker thread, we
    double-check whether we're idle, and if not, then we skip the worker
    thread and jump directly to step 2. This means that your app only pays
    the extra thread-switching penalty at moments when it would otherwise
    be sleeping, so it should have minimal effect on your app's overall
    performance.

    The total overhead will depend on your host loop, your platform, your
    application, etc. But we expect that in most cases, apps running in
    guest mode should only be 5-10% slower than the same code using
    :func:`trio.run`. If you find that's not true for your app, then please let
    us know and we'll see if we can fix it!


.. _guest-run-implementation:

为您最喜欢的事件循环实现访客模式
----------------------------------------------------

**Implementing guest mode for your favorite event loop**

.. tab:: 中文

    让我们看看你需要做些什么，将 Trio 的来宾模式与最喜欢的事件循环结合起来。将本节视为一个检查清单。

    **入门：** 第一步是让一些基本功能工作。这里是一个在 asyncio 上运行 Trio 的最小示例，你可以将其作为模板：

    .. code-block:: python

        import asyncio
        import trio

        # 一个小型的 Trio 程序
        async def trio_main():
            for _ in range(5):
                print("Hello from Trio!")
                # 这是在 Trio 内部，所以我们必须使用 Trio 的 API
                await trio.sleep(1)
            return "trio done!"

        # 将其作为来宾运行在 asyncio 中的代码
        async def asyncio_main():
            asyncio_loop = asyncio.get_running_loop()

            def run_sync_soon_threadsafe(fn):
                asyncio_loop.call_soon_threadsafe(fn)

            def done_callback(trio_main_outcome):
                print(f"Trio 程序结束，结果是: {trio_main_outcome}")

            # 这是魔法发生的地方：
            trio.lowlevel.start_guest_run(
                trio_main,
                run_sync_soon_threadsafe=run_sync_soon_threadsafe,
                done_callback=done_callback,
            )

            # 让主机循环运行一段时间，以便 trio_main 有时间完成。
            # （警告：这是一种 hack，下面会讨论更好的方法。）
            #
            # 这个函数在 asyncio 中，因此我们必须使用 asyncio 的 API。
            await asyncio.sleep(10)

        asyncio.run(asyncio_main())

    你可以看到，我们使用了特定于 asyncio 的 API 启动一个事件循环，
    然后调用了 :func:`trio.lowlevel.start_guest_run`。这个函数与 :func:`trio.run` 非常相似，
    并且接受相同的所有参数。但它有两个区别：

    首先，它不会阻塞直到 ``trio_main`` 完成，而是将 ``trio_main`` 安排在主机循环上运行，
    然后立即返回。所以 ``trio_main`` 是在后台运行的——这就是为什么我们需要等待并给它时间完成的原因。

    其次，它需要两个额外的关键字参数：
    ``run_sync_soon_threadsafe`` 和 ``done_callback``。

    对于 ``run_sync_soon_threadsafe``，我们需要一个函数，这个函数接收一个同步回调并将其安排在主机事件循环中运行。这个函数需要是“线程安全的”，也就是说，你可以从任何线程安全地调用它。所以你需要搞清楚如何使用主机循环的 API 编写一个这样的函数。对于 asyncio，这很简单，因为 :func:`asyncio.loop.call_soon_threadsafe` 正好做了我们需要的事情；而对于其他事件循环，可能会更加复杂。

    对于 ``done_callback``，你传入一个函数，当 Trio 运行结束时，Trio 会自动调用该函数，这样你就能知道它完成了并了解发生了什么。对于这个基本的入门版本，我们只是打印结果；在下一节中，我们会讨论更好的替代方案。

    到这个阶段，你应该能够在主机事件循环中运行一个简单的 Trio 程序。接下来，我们将把这个原型转变为更稳健的实现。

    **事件循环的生命周期：** 大多数事件循环中最棘手的事情之一是正确地关闭事件循环。并且当有两个事件循环时，这变得更加困难！

    如果可能的话，我们建议遵循以下模式：

    - 启动主机事件循环
    - 立即调用 :func:`start_guest_run` 来启动 Trio
    - 当 Trio 完成并且你的 ``done_callback`` 被调用时，关闭主机事件循环
    - 确保没有其他代码关闭主机事件循环

    这样，你的两个事件循环就有相同的生命周期，当 Trio 函数完成时，程序会自动退出。

    下面是如何扩展我们的 asyncio 示例来实现这个模式：

    .. code-block:: python3
        :emphasize-lines: 8-11,19-22

        # 改进版本，在 Trio 完成后正确关闭
        async def asyncio_main():
            asyncio_loop = asyncio.get_running_loop()

            def run_sync_soon_threadsafe(fn):
                asyncio_loop.call_soon_threadsafe(fn)

            # 修改后的 'done' 回调：设置一个 Future
            done_fut = asyncio_loop.create_future()
            def done_callback(trio_main_outcome):
                done_fut.set_result(trio_main_outcome)

            trio.lowlevel.start_guest_run(
                trio_main,
                run_sync_soon_threadsafe=run_sync_soon_threadsafe,
                done_callback=done_callback,
            )

            # 等待来宾程序完成
            trio_main_outcome = await done_fut
            # 传递返回值或异常
            return trio_main_outcome.unwrap()

    然后，你可以将所有这些机制封装在一个实用函数中，
    它暴露一个类似于 :func:`trio.run` 的 API，但能同时运行两个事件循环：

    .. code-block:: python

        def trio_run_with_asyncio(trio_main, *args, **trio_run_kwargs):
            async def asyncio_main():
                # 同上
                ...

            return asyncio.run(asyncio_main())
    
    从技术上讲，使用其他模式也是可能的。但你必须遵守一些重要的限制：

    - **你必须让 Trio 程序运行到完成。** 许多事件循环允许你在任何时刻停止事件循环，而任何挂起的回调/任务等...就不会运行了。Trio 遵循一种更结构化的系统，你可以取消任务，但代码总是会运行到完成，因此 ``finally`` 块会执行，资源会被清理等。如果你在 ``done_callback`` 被调用之前提前停止了主机事件循环，那么这会中断 Trio 程序的运行，且没有机会进行清理。这可能会导致代码处于不一致的状态，并且肯定会导致 Trio 的内部状态不一致，若你在该线程中再次使用 Trio，将会发生错误。

      有些程序需要能够随时退出，例如响应 GUI 窗口的关闭或用户从菜单中选择“退出”。在这些情况下，我们建议将整个程序包装在一个 :class:`trio.CancelScope` 中，并在你想退出时取消它。

    - 每个主机事件循环只能同时运行一个 :func:`start_guest_run`。如果你尝试启动第二个，将会引发错误。如果你需要同时运行多个 Trio 函数，那么应该启动一个单独的 Trio 运行，打开一个 nursery，然后将函数作为子任务启动在这个 nursery 中。

    - 除非你或你的主机事件循环在启动 Trio 之前注册了 :data:`signal.SIGINT` 的处理程序（这并不常见），否则 Trio 会接管对 :exc:`KeyboardInterrupt` 的处理。由于 Trio 无法判断哪个主机代码是安全的进行中断，它将只向 Trio 部分的代码传递 :exc:`KeyboardInterrupt`。如果你的程序设置为在 Trio 部分退出时退出，这没问题，因为 :exc:`KeyboardInterrupt` 会从 Trio 传播出去，然后触发主机事件循环的关闭，这正是你希望的行为。

    鉴于这些限制，我们认为最简单的方法是始终将两个事件循环一起启动和停止。

    **信号管理：** `"信号"
    <https://en.wikipedia.org/wiki/Signal_(IPC)>`__ 是一种低级的进程间通信原语。当你按下控制-C来终止程序时，就是使用了一个信号。Python 中的信号处理有 `很多复杂的部分
    <https://vorpus.org/blog/control-c-handling-in-python-and-trio/>`__。
    其中一部分是 :func:`signal.set_wakeup_fd`，它用于确保事件循环在信号到达时能够唤醒并做出响应。
    （如果你曾经遇到事件循环忽视控制-C的情况，可能是因为它们没有正确使用
    :func:`signal.set_wakeup_fd`。）

    但是，只有一个事件循环可以同时使用 :func:`signal.set_wakeup_fd`。在来宾模式下，这可能会导致问题：Trio 和主机事件循环可能会争夺谁来使用 :func:`signal.set_wakeup_fd`。

    某些事件循环（如 asyncio）如果没有在这场争斗中获胜，则无法正常工作。幸运的是，Trio 对此并不那么挑剔：只要 *有人* 确保程序在信号到达时能唤醒，它应该能正常工作。所以，如果你的主机事件循环需要使用 :func:`signal.set_wakeup_fd`，那么你应该禁用 Trio 的 :func:`signal.set_wakeup_fd` 支持，这样两个事件循环就能正常工作。

    另一方面，如果你的主机事件循环不使用 :func:`signal.set_wakeup_fd`，那么确保一切正常工作的唯一方法是 *启用* Trio 的 :func:`signal.set_wakeup_fd` 支持。

    默认情况下，Trio 假设你的主机事件循环没有使用 :func:`signal.set_wakeup_fd`。它会尝试检测这种与主机事件循环冲突的情况，并打印警告——但不幸的是，在检测到时，损害已经发生。因此，如果你收到此警告，则应通过传递 ``host_uses_signal_set_wakeup_fd=True`` 给 :func:`start_guest_run` 来禁用 Trio 的 :func:`signal.set_wakeup_fd` 支持。

    如果在初始原型中没有看到任何警告，你 *可能* 没问题。但要确保无误，最好的办法是检查你的主机事件循环源代码。例如，asyncio 可能会根据 Python 版本和操作系统使用或不使用 :func:`signal.set_wakeup_fd`。

    **一个小优化：** 最后，考虑进行一个小优化。有些事件循环提供了它们的“尽快调用此函数” API 的两个版本：一个可以从任何线程使用，另一个只能在事件循环线程中使用，后者更便宜。例如，asyncio 提供了 :func:`asyncio.loop.call_soon_threadsafe` 和 :func:`asyncio.loop.call_soon`。

    如果你的事件循环有这样的区分，那么你还可以传递 ``run_sync_soon_not_threadsafe=...`` 关键字参数给 :func:`start_guest_run`，在适当的时候，Trio 会自动使用它。

    如果你的事件循环没有这样的区分，那就不用担心； ``run_sync_soon_not_threadsafe=`` 是可选的。（如果没有传递，Trio 会在所有情况下使用线程安全的版本。）

    **就这样！** 如果你按照这些步骤操作，你应该已经成功地将两个事件循环干净地集成在一起了。去做一些酷炫的 GUI / 游戏 / 其他的项目吧！

.. tab:: 英文

    Let's walk through what you need to do to integrate Trio's guest mode
    with your favorite event loop. Treat this section like a checklist.

    **Getting started:** The first step is to get something basic working.
    Here's a minimal example of running Trio on top of asyncio, that you
    can use as a model:

    .. code-block:: python

        import asyncio
        import trio

        # A tiny Trio program
        async def trio_main():
            for _ in range(5):
                print("Hello from Trio!")
                # This is inside Trio, so we have to use Trio APIs
                await trio.sleep(1)
            return "trio done!"

        # The code to run it as a guest inside asyncio
        async def asyncio_main():
            asyncio_loop = asyncio.get_running_loop()

            def run_sync_soon_threadsafe(fn):
                asyncio_loop.call_soon_threadsafe(fn)

            def done_callback(trio_main_outcome):
                print(f"Trio program ended with: {trio_main_outcome}")

            # This is where the magic happens:
            trio.lowlevel.start_guest_run(
                trio_main,
                run_sync_soon_threadsafe=run_sync_soon_threadsafe,
                done_callback=done_callback,
            )

            # Let the host loop run for a while to give trio_main time to
            # finish. (WARNING: This is a hack. See below for better
            # approaches.)
            #
            # This function is in asyncio, so we have to use asyncio APIs.
            await asyncio.sleep(10)

        asyncio.run(asyncio_main())

    You can see we're using asyncio-specific APIs to start up a loop, and
    then we call :func:`trio.lowlevel.start_guest_run`. This function is very
    similar to :func:`trio.run`, and takes all the same arguments. But it has
    two differences:

    First, instead of blocking until ``trio_main`` has finished, it
    schedules ``trio_main`` to start running on top of the host loop, and
    then returns immediately. So ``trio_main`` is running in the
    background – that's why we have to sleep and give it time to finish.

    And second, it requires two extra keyword arguments:
    ``run_sync_soon_threadsafe``, and ``done_callback``.

    For ``run_sync_soon_threadsafe``, we need a function that takes a
    synchronous callback, and schedules it to run on your host loop. And
    this function needs to be "threadsafe" in the sense that you can
    safely call it from any thread. So you need to figure out how to write
    a function that does that using your host loop's API. For asyncio,
    this is easy because :func:`asyncio.loop.call_soon_threadsafe` does exactly
    what we need; for your loop, it might be more or less complicated.

    For ``done_callback``, you pass in a function that Trio will
    automatically invoke when the Trio run finishes, so you know it's done
    and what happened. For this basic starting version, we just print the
    result; in the next section we'll discuss better alternatives.

    At this stage you should be able to run a simple Trio program inside
    your host loop. Now we'll turn that prototype into something solid.


    **Loop lifetimes:** One of the trickiest things in most event loops is
    shutting down correctly. And having two event loops makes this even
    harder!

    If you can, we recommend following this pattern:

    - Start up your host loop
    - Immediately call :func:`start_guest_run` to start Trio
    - When Trio finishes and your ``done_callback`` is invoked, shut down the host loop
    - Make sure that nothing else shuts down your host loop

    This way, your two event loops have the same lifetime, and your
    program automatically exits when your Trio function finishes.

    Here's how we'd extend our asyncio example to implement this pattern:

    .. code-block:: python3
        :emphasize-lines: 8-11,19-22

        # Improved version, that shuts down properly after Trio finishes
        async def asyncio_main():
            asyncio_loop = asyncio.get_running_loop()

            def run_sync_soon_threadsafe(fn):
                asyncio_loop.call_soon_threadsafe(fn)

            # Revised 'done' callback: set a Future
            done_fut = asyncio_loop.create_future()
            def done_callback(trio_main_outcome):
                done_fut.set_result(trio_main_outcome)

            trio.lowlevel.start_guest_run(
                trio_main,
                run_sync_soon_threadsafe=run_sync_soon_threadsafe,
                done_callback=done_callback,
            )

            # Wait for the guest run to finish
            trio_main_outcome = await done_fut
            # Pass through the return value or exception from the guest run
            return trio_main_outcome.unwrap()

    And then you can encapsulate all this machinery in a utility function
    that exposes a :func:`trio.run`-like API, but runs both loops together:

    .. code-block:: python

        def trio_run_with_asyncio(trio_main, *args, **trio_run_kwargs):
            async def asyncio_main():
                # same as above
                ...

            return asyncio.run(asyncio_main())

    Technically, it is possible to use other patterns. But there are some
    important limitations you have to respect:

    - **You must let the Trio program run to completion.** Many event loops let you stop the event loop at any point, and any pending callbacks/tasks/etc. just... don't run. Trio follows a more structured system, where you can cancel things, but the code always runs to completion, so ``finally`` blocks run, resources are cleaned up, etc. If you stop your host loop early, before the ``done_callback`` is invoked, then that cuts off the Trio run in the middle without a chance to clean up. This can leave your code in an inconsistent state, and will definitely leave Trio's internals in an inconsistent state, which will cause errors if you try to use Trio again in that thread.

      Some programs need to be able to quit at any time, for example in response to a GUI window being closed or a user selecting a "Quit" from a menu. In these cases, we recommend wrapping your whole program in a :class:`trio.CancelScope`, and cancelling it when you want to quit.

    - Each host loop can only have one :func:`start_guest_run` at a time. If you try to start a second one, you'll get an error. If you need to run multiple Trio functions at the same time, then start up a single Trio run, open a nursery, and then start your functions as child tasks in that nursery.

    - Unless you or your host loop register a handler for :data:`signal.SIGINT` before starting Trio (this is not common), then Trio will take over delivery of :exc:`KeyboardInterrupt`\s. And since Trio can't tell which host code is safe to interrupt, it will only deliver :exc:`KeyboardInterrupt` into the Trio part of your code. This is fine if your program is set up to exit when the Trio part exits, because the :exc:`KeyboardInterrupt` will propagate out of Trio and then trigger the shutdown of your host loop, which is just what you want.

    Given these constraints, we think the simplest approach is to always
    start and stop the two loops together.

    **Signal management:** `"Signals"
    <https://en.wikipedia.org/wiki/Signal_(IPC)>`__ are a low-level
    inter-process communication primitive. When you hit control-C to kill
    a program, that uses a signal. Signal handling in Python has `a lot of
    moving parts
    <https://vorpus.org/blog/control-c-handling-in-python-and-trio/>`__.
    One of those parts is :func:`signal.set_wakeup_fd`, which event loops use to
    make sure that they wake up when a signal arrives so they can respond
    to it. (If you've ever had an event loop ignore you when you hit
    control-C, it was probably because they weren't using
    :func:`signal.set_wakeup_fd` correctly.)

    But, only one event loop can use :func:`signal.set_wakeup_fd` at a time. And
    in guest mode that can cause problems: Trio and the host loop might
    start fighting over who's using :func:`signal.set_wakeup_fd`.

    Some event loops, like asyncio, won't work correctly unless they win
    this fight. Fortunately, Trio is a little less picky: as long as
    *someone* makes sure that the program wakes up when a signal arrives,
    it should work correctly. So if your host loop wants
    :func:`signal.set_wakeup_fd`, then you should disable Trio's
    :func:`signal.set_wakeup_fd` support, and then both loops will work
    correctly.

    On the other hand, if your host loop doesn't use
    :func:`signal.set_wakeup_fd`, then the only way to make everything work
    correctly is to *enable* Trio's :func:`signal.set_wakeup_fd` support.

    By default, Trio assumes that your host loop doesn't use
    :func:`signal.set_wakeup_fd`. It does try to detect when this creates a
    conflict with the host loop, and print a warning – but unfortunately,
    by the time it detects it, the damage has already been done. So if
    you're getting this warning, then you should disable Trio's
    :func:`signal.set_wakeup_fd` support by passing
    ``host_uses_signal_set_wakeup_fd=True`` to :func:`start_guest_run`.

    If you aren't seeing any warnings with your initial prototype, you're
    *probably* fine. But the only way to be certain is to check your host
    loop's source. For example, asyncio may or may not use
    :func:`signal.set_wakeup_fd` depending on the Python version and operating
    system.


    **A small optimization:** Finally, consider a small optimization. Some
    event loops offer two versions of their "call this function soon" API:
    one that can be used from any thread, and one that can only be used
    from the event loop thread, with the latter being cheaper. For
    example, asyncio has both :func:`asyncio.loop.call_soon_threadsafe` and
    :func:`asyncio.loop.call_soon`.

    If you have a loop like this, then you can also pass a
    ``run_sync_soon_not_threadsafe=...`` kwarg to :func:`start_guest_run`, and
    Trio will automatically use it when appropriate.

    If your loop doesn't have a split like this, then don't worry about
    it; ``run_sync_soon_not_threadsafe=`` is optional. (If it's not
    passed, then Trio will just use your threadsafe version in all cases.)

    **That's it!** If you've followed all these steps, you should now have
    a cleanly-integrated hybrid event loop. Go make some cool
    GUIs/games/whatever!


限制
-----------

**Limitations**

.. tab:: 中文

    通常，几乎所有的 Trio 功能在来宾模式下都应该可以正常工作。唯一的例外是那些依赖于 Trio 完全了解程序正在做什么的功能，因为显然，它不能控制主机事件循环或查看它的行为。

    自定义时钟可以在来宾模式下使用，但它们只会影响 Trio 的超时，而不会影响主机事件循环的超时。并且 :ref:`autojump clock <testing-time>` 以及相关的 :func:`trio.testing.wait_all_tasks_blocked` 技术上可以在来宾模式下使用，但它们只会考虑 Trio 任务，来决定是否跳过时钟或是否所有任务都被阻塞。

.. tab:: 英文

    In general, almost all Trio features should work in guest mode. The
    exception is features which rely on Trio having a complete picture of
    everything that your program is doing, since obviously, it can't
    control the host loop or see what it's doing.

    Custom clocks can be used in guest mode, but they only affect Trio
    timeouts, not host loop timeouts. And the :ref:`autojump clock
    <testing-time>` and related :func:`trio.testing.wait_all_tasks_blocked` can
    technically be used in guest mode, but they'll only take Trio tasks
    into account when decided whether to jump the clock or whether all
    tasks are blocked.


参考
---------

**Reference**

.. autofunction:: start_guest_run


.. _live-coroutine-handoff:

在协程运行器之间交接实时协程对象
============================================================

**Handing off live coroutine objects between coroutine runners**

.. tab:: 中文

    
    在内部，Python 的 async/await 语法是基于“协程对象”和“协程运行器”这一概念构建的。协程对象表示异步调用栈的状态。但单独来看，这只是一个静态对象，什么都不做。如果你希望它执行任何操作，你需要一个协程运行器来推动它向前执行。每个 Trio 任务都有一个关联的协程对象（见 :data:`Task.coro`），而 Trio 调度器充当了它们的协程运行器。

    但当然，Trio 并不是 Python 中唯一的协程运行器——:mod:`asyncio` 有一个，其他事件循环也有，甚至你可以自己定义一个。

    在一些非常、非常不寻常的情况下，甚至有意义将一个协程对象在不同的协程运行器之间来回传递。这就是本节内容的主题。这是一个 *极其* 特殊的用例，需要对 Python 的 async/await 内部工作原理有较高的理解。有关动机示例，请参见 `trio-asyncio issue #42 <https://github.com/python-trio/trio-asyncio/issues/42>`__ 和 `trio issue #649 <https://github.com/python-trio/trio/issues/649>`__。有关协程工作原理的更多细节，我们推荐 André Caron 的 `A tale of event loops <https://github.com/AndreLouisCaron/a-tale-of-event-loops>`__，或者直接查看 `PEP 492 <https://www.python.org/dev/peps/pep-0492/>`__ 获取完整细节。

    .. autofunction:: permanently_detach_coroutine_object

    .. autofunction:: temporarily_detach_coroutine_object

    .. autofunction:: reattach_detached_coroutine_object

.. tab:: 英文

    Internally, Python's async/await syntax is built around the idea of
    "coroutine objects" and "coroutine runners". A coroutine object
    represents the state of an async callstack. But by itself, this is
    just a static object that sits there. If you want it to do anything,
    you need a coroutine runner to push it forward. Every Trio task has an
    associated coroutine object (see :data:`Task.coro`), and the Trio
    scheduler acts as their coroutine runner.

    But of course, Trio isn't the only coroutine runner in Python –
    :mod:`asyncio` has one, other event loops have them, you can even
    define your own.

    And in some very, very unusual circumstances, it even makes sense to
    transfer a single coroutine object back and forth between different
    coroutine runners. That's what this section is about. This is an
    *extremely* exotic use case, and assumes a lot of expertise in how
    Python async/await works internally. For motivating examples, see
    `trio-asyncio issue #42
    <https://github.com/python-trio/trio-asyncio/issues/42>`__, and `trio
    issue #649 <https://github.com/python-trio/trio/issues/649>`__. For
    more details on how coroutines work, we recommend André Caron's `A
    tale of event loops
    <https://github.com/AndreLouisCaron/a-tale-of-event-loops>`__, or
    going straight to `PEP 492
    <https://www.python.org/dev/peps/pep-0492/>`__ for the full details.

    .. autofunction:: permanently_detach_coroutine_object
        :no-index:

    .. autofunction:: temporarily_detach_coroutine_object
        :no-index:

    .. autofunction:: reattach_detached_coroutine_object
        :no-index:
