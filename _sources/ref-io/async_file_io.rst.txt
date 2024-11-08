.. currentmodule:: trio

.. _async-file-io:

异步文件系统 I/O
=========================

**Asynchronous filesystem I/O**

.. tab:: 中文

   Trio 提供了内置功能, 用于执行异步文件系统操作, 例如读取或重命名文件。通常, 我们建议您使用这些功能, 而不是 Python 的正常同步文件 API。但这里的权衡有些微妙：有时人们切换到异步 I/O, 然后发现它并没有加速程序, 反而感到惊讶和困惑。下一节将解释异步文件 I/O 背后的理论, 帮助您更好地理解代码的行为。或者, 如果您只是想开始使用, 可以 :ref:`跳到 API 概览 <async-file-io-overview>`。

.. tab:: 英文

   Trio provides built-in facilities for performing asynchronous
   filesystem operations like reading or renaming a file. Generally, we
   recommend that you use these instead of Python's normal synchronous
   file APIs. But the tradeoffs here are somewhat subtle: sometimes
   people switch to async I/O, and then they're surprised and confused
   when they find it doesn't speed up their program. The next section
   explains the theory behind async file I/O, to help you better
   understand your code's behavior. Or, if you just want to get started,
   you can :ref:`jump down to the API overview <async-file-io-overview>`.


背景：异步文件 I/O 为何有用？答案可能会让您大吃一惊
---------------------------------------------------

**Background: Why is async file I/O useful? The answer may surprise you**

.. tab:: 中文

   许多人认为从同步文件 I/O 切换到异步文件 I/O 总是能加速程序的运行。事实并非如此!如果我们仅仅看总体吞吐量, 那么异步文件 I/O 可能更快, 也可能更慢, 或者差不多一样, 这取决于诸如磁盘访问模式或内存大小等复杂因素。异步文件 I/O 的主要动机并不是提高吞吐量, 而是 **减少延迟波动的频率**。

   要理解这一点, 您需要知道两件事。

   首先, 目前没有主流操作系统提供通用的, 可靠的本地 API 来进行异步文件或文件系统操作, 因此我们必须通过使用线程 (具体来说, 使用 :func:`trio.to_thread.run_sync` ) 来模拟实现。这虽然便宜, 但并不是免费的：在典型的 PC 上, 调度到一个工作线程会为每次操作增加大约 ~100 微秒的开销。 (“µs”表示“微秒”, 一秒钟有 1,000,000 微秒。请注意, 这里所有的数字都是粗略的数量级, 用来给您一个规模的概念；如果您需要您环境中的精确数字, 请进行测量! ) 

   .. file.read benchmark is notes-to-self/file-read-latency.py
   .. 硬盘和 SSD 的数字来自于从 http://www.storagereview.com/best_drives 中随机选取的几篇近期评测, 并查看其“4K 写入延迟”测试结果中的“平均毫秒数”和“最大毫秒数”：
      http://www.storagereview.com/samsung_ssd_850_evo_ssd_review
      http://www.storagereview.com/wd_black_6tb_hdd_review

   其次, 磁盘操作的成本是极其双峰的。有时, 您需要的数据已经缓存到内存中, 这时访问数据非常, 非常快——对一个缓存的文件调用 :class:`io.FileIO` 的 ``read`` 方法只需大约 ~1 微秒。但当数据没有缓存时, 访问它要慢得多：SSD 的平均延迟大约是 ~100 微秒, 旋转磁盘则大约是 ~10,000 微秒。如果您查看尾部延迟, 您会发现对于这两种存储类型, 偶尔有些操作的延迟会比平均值慢 10 倍甚至 100 倍。而且这是假设您的程序是唯一在使用那个磁盘的——如果您使用的是超卖的云虚拟机, 与其他租户争抢 I/O, 那谁知道会发生什么。有些操作可能需要多次磁盘访问。

   将这些因素结合起来：如果您的数据已经在内存中, 那么显然使用线程是一个糟糕的主意——如果您在一个 1 微秒的操作上加上 100 微秒的开销, 那就意味着速度变慢了 100 倍!另一方面, 如果您的数据在旋转磁盘上, 那么使用线程是 *非常好* 的——我们不再阻塞主线程和所有任务 10,000 微秒, 而是仅仅阻塞它们 100 微秒, 并可以利用剩余的时间运行其他任务完成有用的工作, 这样就能有效地提升 100 倍的速度。

   但问题在于：对于任何单独的 I/O 操作, 我们无法预先知道它是会是快操作还是慢操作, 因此无法选择性地使用它们。当您切换到异步文件 I/O 时, 它会使所有快操作变慢, 所有慢操作变快。这算是一个优势吗？从整体速度上讲, 很难说：这取决于您使用的磁盘类型, 以及您的内核磁盘缓存命中率, 这又取决于您的文件访问模式, 可用内存, 服务负载……各种因素。如果这个问题对您很重要, 那么没有什么能替代在您实际部署环境中测量代码实际行为的方式。但我们 *可以* 说的是, 异步磁盘 I/O 可以让性能在更广泛的运行时条件下变得更加可预测。

   **如果您不确定该做什么, 我们建议默认使用异步磁盘 I/O, ** 因为它能让您的代码在条件不佳时更为稳健, 特别是在处理尾部延迟时；这提高了用户看到的结果与您在测试中看到的结果一致的可能性。阻塞主线程会导致 *所有* 任务在那段时间内都无法运行。10,000 微秒是 10 毫秒, 而只需要几次 10 毫秒的延迟就能导致 `实际损失
   <https://google.com/search?q=latency+cost>`__；异步磁盘 I/O 可以帮助防止这些情况发生。只要不要期望它是魔法, 并且意识到其中的权衡。

.. tab:: 英文

   Many people expect that switching from synchronous file I/O to
   async file I/O will always make their program faster. This is not
   true! If we just look at total throughput, then async file I/O might
   be faster, slower, or about the same, and it depends in a complicated
   way on things like your exact patterns of disk access, or how much RAM
   you have. The main motivation for async file I/O is not to improve
   throughput, but to **reduce the frequency of latency glitches.**

   To understand why, you need to know two things.

   First, right now no mainstream operating system offers a generic,
   reliable, native API for async file or filesystem operations, so we
   have to fake it by using threads (specifically,
   :func:`trio.to_thread.run_sync`). This is cheap but isn't free: on a
   typical PC, dispatching to a worker thread adds something like ~100 µs
   of overhead to each operation. ("µs" is pronounced "microseconds", and
   there are 1,000,000 µs in a second. Note that all the numbers here are
   going to be rough orders of magnitude to give you a sense of scale; if
   you need precise numbers for your environment, measure!)

   .. file.read benchmark is notes-to-self/file-read-latency.py
   .. Numbers for spinning disks and SSDs are from taking a few random
      recent reviews from http://www.storagereview.com/best_drives and
      looking at their "4K Write Latency" test results for "Average MS"
      and "Max MS":
      http://www.storagereview.com/samsung_ssd_850_evo_ssd_review
      http://www.storagereview.com/wd_black_6tb_hdd_review

   And second, the cost of a disk operation is incredibly
   bimodal. Sometimes, the data you need is already cached in RAM, and
   then accessing it is very, very fast – calling :class:`io.FileIO`\'s
   ``read`` method on a cached file takes on the order of ~1 µs. But when
   the data isn't cached, then accessing it is much, much slower: the
   average is ~100 µs for SSDs and ~10,000 µs for spinning disks, and if
   you look at tail latencies then for both types of storage you'll see
   cases where occasionally some operation will be 10x or 100x slower
   than average. And that's assuming your program is the only thing
   trying to use that disk – if you're on some oversold cloud VM fighting
   for I/O with other tenants then who knows what will happen. And some
   operations can require multiple disk accesses.

   Putting these together: if your data is in RAM then it should be clear
   that using a thread is a terrible idea – if you add 100 µs of overhead
   to a 1 µs operation, then that's a 100x slowdown! On the other hand,
   if your data's on a spinning disk, then using a thread is *great* –
   instead of blocking the main thread and all tasks for 10,000 µs, we
   only block them for 100 µs and can spend the rest of that time running
   other tasks to get useful work done, which can effectively be a 100x
   speedup.

   But here's the problem: for any individual I/O operation, there's no
   way to know in advance whether it's going to be one of the fast ones
   or one of the slow ones, so you can't pick and choose. When you switch
   to async file I/O, it makes all the fast operations slower, and all
   the slow operations faster. Is that a win? In terms of overall speed,
   it's hard to say: it depends what kind of disks you're using and your
   kernel's disk cache hit rate, which in turn depends on your file
   access patterns, how much spare RAM you have, the load on your
   service, ... all kinds of things. If the answer is important to you,
   then there's no substitute for measuring your code's actual behavior
   in your actual deployment environment. But what we *can* say is that
   async disk I/O makes performance much more predictable across a wider
   range of runtime conditions.

   **If you're not sure what to do, then we recommend that you use async
   disk I/O by default,** because it makes your code more robust when
   conditions are bad, especially with regards to tail latencies; this
   improves the chances that what your users see matches what you saw in
   testing. Blocking the main thread stops *all* tasks from running for
   that time. 10,000 µs is 10 ms, and it doesn't take many 10 ms glitches
   to start adding up to `real money
   <https://google.com/search?q=latency+cost>`__; async disk I/O can help
   prevent those. Just don't expect it to be magic, and be aware of the
   tradeoffs.


.. _async-file-io-overview:

API 概述
------------

**API overview**

.. tab:: 中文

   如果您想执行一般的文件系统操作, 例如创建和列出目录, 重命名文件或检查文件元数据, 或者如果您只是想以一种友好的方式处理文件系统路径, 那么您需要使用 :class:`trio.Path`。它是标准库 :class:`pathlib.Path` 的异步替代品, 并提供相同的全面操作集。

   对于文件和类文件对象的读取和写入, Trio 还提供了一种机制, 可以将任何同步的类文件对象包装为异步接口。如果您拥有一个 :class:`trio.Path` 对象, 可以通过调用其 :meth:`~trio.Path.open` 方法来获取一个异步文件对象；或者, 如果您知道文件名, 也可以直接使用 :func:`trio.open_file` 打开文件。或者, 如果您已经有一个打开的类文件对象, 可以通过 :func:`trio.wrap_file` 将其包装起来——在编写测试时, 特别有用的一种情况是将 :class:`io.BytesIO` 或 :class:`io.StringIO` 包装起来。

.. tab:: 英文

   If you want to perform general filesystem operations like creating and
   listing directories, renaming files, or checking file metadata – or if
   you just want a friendly way to work with filesystem paths – then you
   want :class:`trio.Path`. It's an asyncified replacement for the
   standard library's :class:`pathlib.Path`, and provides the same
   comprehensive set of operations.

   For reading and writing to files and file-like objects, Trio also
   provides a mechanism for wrapping any synchronous file-like object
   into an asynchronous interface. If you have a :class:`trio.Path`
   object you can get one of these by calling its :meth:`~trio.Path.open`
   method; or if you know the file's name you can open it directly with
   :func:`trio.open_file`. Alternatively, if you already have an open
   file-like object, you can wrap it with :func:`trio.wrap_file` – one
   case where this is especially useful is to wrap :class:`io.BytesIO` or
   :class:`io.StringIO` when writing tests.


异步路径对象
--------------------------

**Asynchronous path objects**

.. autoclass:: Path
   :members:
   :inherited-members:

.. autoclass:: PosixPath

.. autoclass:: WindowsPath


.. _async-file-objects:

异步文件对象
-------------------------

**Asynchronous file objects**

.. 在此处抑制类型注释, 它们涉及许多内部类型。
   普通的 Python 文档对此有更详细的描述。

.. Suppress type annotations here, they refer to lots of internal types.
   The normal Python docs go into better detail.

.. tab:: 中文

   .. autofunction:: open_file(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=None, opener=None)

   .. autofunction:: wrap_file(file)

   .. interface:: Asynchronous file interface(异步文件接口)

      Trio 的异步文件对象具有一个接口, 该接口会自动适应被包装的对象。直观地说, 您可以将它们像常规的 :term:`文件对象 <file object>` 一样使用, 只是在执行 I/O 的任何方法前添加 ``await``。不过, Python 中的 :term:`文件对象 <file object>` 定义有点模糊, 因此这里列出了具体细节：

      * 同步属性/方法：如果存在以下任何属性或方法, 它们将保持不变并重新导出：``closed``, ``encoding``, ``errors``, ``fileno``, ``isatty``, ``newlines``, ``readable``, ``seekable``, ``writable``, ``buffer``, ``raw``, ``line_buffering``, ``closefd``, ``name``, ``mode``, ``getvalue``, ``getbuffer``。

      * 异步方法：如果存在以下任何方法, 它们将作为异步方法重新导出：``flush``, ``read``, ``read1``, ``readall``, ``readinto``, ``readline``, ``readlines``, ``seek``, ``tell``, ``truncate``, ``write``, ``writelines``, ``readinto1``, ``peek``, ``detach``。

      特别说明：

      * 异步文件对象实现了 Trio 的 :class:`~trio.abc.AsyncResource` 接口：您通过调用 :meth:`~trio.abc.AsyncResource.aclose` 来关闭它们, 而不是使用 ``close`` (!!) , 并且它们可以作为异步上下文管理器使用。像所有的 :meth:`~trio.abc.AsyncResource.aclose` 方法一样, 异步文件对象上的 ``aclose`` 方法在返回之前保证关闭文件, 即使它被取消或以其他方式引发错误。

      * 从多个任务同时使用同一个异步文件对象：由于异步文件对象上的异步方法是通过线程实现的, 只有当底层同步文件对象是线程安全时, 才可以从不同任务中同时安全地调用两个方法。您应该查阅您正在包装的对象的文档。对于 :func:`trio.open_file` 或 :meth:`trio.Path.open` 返回的对象, 这取决于您是以二进制模式还是文本模式打开文件：`二进制模式文件是任务安全/线程安全的, 文本模式文件则不是 <https://docs.python.org/3/library/io.html#multi-threading>`__ 。

      * 异步文件对象可以作为异步迭代器, 用于迭代文件的每一行：

      .. code-block:: python

         async with await trio.open_file(...) as f:
               async for line in f:
                  print(line)

      * ``detach`` 方法 (如果存在 ) 返回一个异步文件对象。

      这应该包括 :mod:`io` 中的类所暴露的所有属性。如果您正在包装的对象有其他未在上述列表中的属性, 您可以通过 ``.wrapped`` 属性访问它们：

      .. attribute:: wrapped

         底层同步文件对象。

.. tab:: 英文

   .. autofunction:: open_file(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=None, opener=None)
      :no-index:

   .. autofunction:: wrap_file(file)
      :no-index:

   .. interface:: Asynchronous file interface
      :no-index:

      Trio's asynchronous file objects have an interface that
      automatically adapts to the object being wrapped. Intuitively, you
      can mostly treat them like a regular :term:`file object`, except
      adding an ``await`` in front of any of methods that do I/O. The
      definition of :term:`file object` is a little vague in Python
      though, so here are the details:

      * Synchronous attributes/methods: if any of the following
        attributes or methods are present, then they're re-exported
        unchanged: ``closed``, ``encoding``, ``errors``, ``fileno``,
        ``isatty``, ``newlines``, ``readable``, ``seekable``,
        ``writable``, ``buffer``, ``raw``, ``line_buffering``,
        ``closefd``, ``name``, ``mode``, ``getvalue``, ``getbuffer``.

      * Async methods: if any of the following methods are present, then
        they're re-exported as an async method: ``flush``, ``read``,
        ``read1``, ``readall``, ``readinto``, ``readline``,
        ``readlines``, ``seek``, ``tell``, ``truncate``, ``write``,
        ``writelines``, ``readinto1``, ``peek``, ``detach``.

      Special notes:

      * Async file objects implement Trio's
        :class:`~trio.abc.AsyncResource` interface: you close them by
        calling :meth:`~trio.abc.AsyncResource.aclose` instead of
        ``close`` (!!), and they can be used as async context
        managers. Like all :meth:`~trio.abc.AsyncResource.aclose`
        methods, the ``aclose`` method on async file objects is
        guaranteed to close the file before returning, even if it is
        cancelled or otherwise raises an error.

      * Using the same async file object from multiple tasks
        simultaneously: because the async methods on async file objects
        are implemented using threads, it's only safe to call two of them
        at the same time from different tasks IF the underlying
        synchronous file object is thread-safe. You should consult the
        documentation for the object you're wrapping. For objects
        returned from :func:`trio.open_file` or :meth:`trio.Path.open`,
        it depends on whether you open the file in binary mode or text
        mode: `binary mode files are task-safe/thread-safe, text mode
        files are not
        <https://docs.python.org/3/library/io.html#multi-threading>`__.

      * Async file objects can be used as async iterators to iterate over
        the lines of the file:

      .. code-block:: python

         async with await trio.open_file(...) as f:
               async for line in f:
                  print(line)

      * The ``detach`` method, if present, returns an async file object.

      This should include all the attributes exposed by classes in
      :mod:`io`. But if you're wrapping an object that has other
      attributes that aren't on the list above, then you can access them
      via the ``.wrapped`` attribute:

      .. attribute:: wrapped
         :no-index:

         The underlying synchronous file object.