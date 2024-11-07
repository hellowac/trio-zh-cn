.. module:: trio

.. _synchronization:

任务同步和通信
============

**Synchronizing and communicating between tasks**

.. tab:: 中文

   Trio 提供了一组标准的同步和任务间通信原语。这些对象的 API 通常是根据标准库中的类似类建模的，但也存在一些差异。

.. tab:: 英文

   Trio provides a standard set of synchronization and inter-task
   communication primitives. These objects' APIs are generally modelled
   off of the analogous classes in the standard library, but with some
   differences.


阻塞和非阻塞方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Blocking and non-blocking methods**

.. tab:: 中文

   标准库的同步原语提供了多种机制来指定超时和阻塞行为，并且可以指示一个操作是因成功还是因超时返回的。

   在 Trio 中，我们统一采用以下约定：

   * 我们不提供超时参数。如果你需要超时，可以使用取消作用域（cancel scope）。

   * 对于具有非阻塞版本的操作，阻塞和非阻塞版本是不同的方法，分别命名为 ``X`` 和 ``X_nowait``。（这类似于 :class:`queue.Queue`，但不同于大多数 :mod:`threading` 中的类。）我们喜欢这种方法，因为它使我们能够将阻塞版本设为异步，而将非阻塞版本设为同步。

   * 当非阻塞方法无法成功执行时（例如通道为空、锁已经被占用等），它会引发 :exc:`trio.WouldBlock` 异常。没有类似于 :exc:`queue.Empty` 和 :exc:`queue.Full` 的区别 —— 我们只使用一个异常，并始终如一地使用它。

.. tab:: 英文

   The standard library synchronization primitives have a variety of
   mechanisms for specifying timeouts and blocking behavior, and of
   signaling whether an operation returned due to success versus a
   timeout.

   In Trio, we standardize on the following conventions:

   * We don't provide timeout arguments. If you want a timeout, then use
      a cancel scope.

   * For operations that have a non-blocking variant, the blocking and
      non-blocking variants are different methods with names like ``X``
      and ``X_nowait``, respectively. (This is similar to
      :class:`queue.Queue`, but unlike most of the classes in
      :mod:`threading`.) We like this approach because it allows us to
      make the blocking version async and the non-blocking version sync.

   * When a non-blocking method cannot succeed (the channel is empty, the
      lock is already held, etc.), then it raises :exc:`trio.WouldBlock`.
      There's no equivalent to the :exc:`queue.Empty` versus
      :exc:`queue.Full` distinction – we just have the one exception that
      we use consistently.


公平性
~~~~~~~~

**Fairness**

.. tab:: 中文

   这些类都保证是“公平的”，这意味着在选择谁将下一个获得锁、从队列中取出项等操作时，任务总是按照等待时间最长的顺序来决定。虽然目前尚不完全清楚这是否是最好的选择（参见 `issues#54 <https://github.com/python-trio/trio/issues/54>`__ ），但目前就是这样工作的。

   作为这个含义的一个例子，下面是一个小程序，其中两个任务竞争一个锁。请注意，释放锁的任务总是在其他任务有机会运行之前立即尝试重新获取锁。（请记住，我们这里使用的是协作式多任务，所以实际上是 *确定性* 的，释放锁的任务会在其他任务醒来之前调用 :meth:`~Lock.acquire`；在 Trio 中，释放锁不是一个检查点。）如果使用不公平的锁，这将导致同一个任务永远持有锁，另一个任务被饿死。但如果你运行这个程序，你会看到两个任务轮流获得锁：

   .. code-block:: python

      # fairness-demo.py

      import trio

      async def loopy_child(number, lock):
         while True:
            async with lock:
                  print(f"Child {number} has the lock!")
                  await trio.sleep(0.5)

      async def main():
         async with trio.open_nursery() as nursery:
            lock = trio.Lock()
            nursery.start_soon(loopy_child, 1, lock)
            nursery.start_soon(loopy_child, 2, lock)

      trio.run(main)

.. tab:: 英文

   These classes are all guaranteed to be "fair", meaning that when it
   comes time to choose who will be next to acquire a lock, get an item
   from a queue, etc., then it always goes to the task which has been
   waiting longest. It's `not entirely clear
   <https://github.com/python-trio/trio/issues/54>`__ whether this is the
   best choice, but for now that's how it works.

   As an example of what this means, here's a small program in which two
   tasks compete for a lock. Notice that the task which releases the lock
   always immediately attempts to re-acquire it, before the other task has
   a chance to run. (And remember that we're doing cooperative
   multi-tasking here, so it's actually *deterministic* that the task
   releasing the lock will call :meth:`~Lock.acquire` before the other
   task wakes up; in Trio releasing a lock is not a checkpoint.)  With
   an unfair lock, this would result in the same task holding the lock
   forever and the other task being starved out. But if you run this,
   you'll see that the two tasks politely take turns:

   .. code-block:: python

      # fairness-demo.py

      import trio

      async def loopy_child(number, lock):
         while True:
            async with lock:
                  print(f"Child {number} has the lock!")
                  await trio.sleep(0.5)

      async def main():
         async with trio.open_nursery() as nursery:
            lock = trio.Lock()
            nursery.start_soon(loopy_child, 1, lock)
            nursery.start_soon(loopy_child, 2, lock)

      trio.run(main)


使用 :class:`Event` 广播事件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Broadcasting an event with :class:`Event`**

.. autoclass:: trio.Event
   :members:

.. autoclass:: trio.EventStatistics
   :members:

.. _channels:

使用通道在任务之间传递值
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Using channels to pass values between tasks**

.. tab:: 中文

   *Channels* 允许你在不同任务之间安全且便捷地传递对象。它们特别适用于实现生产者/消费者模式。

   核心的通道 API 由抽象基类 :class:`trio.abc.SendChannel` 和 :class:`trio.abc.ReceiveChannel` 定义。你可以使用它们来实现自定义的通道，执行类似于在进程之间或通过网络传递对象的操作。但在许多情况下，你只想在单个进程内的不同任务之间传递对象，针对这种情况，你可以使用 :func:`trio.open_memory_channel`：

   .. autofunction:: trio.open_memory_channel(max_buffer_size)

   .. note:: 如果你曾经使用过 :mod:`threading` 或 :mod:`asyncio` 模块，你可能熟悉 :class:`queue.Queue` 或 :class:`asyncio.Queue`。在 Trio 中，:func:`open_memory_channel` 是你在寻找队列时使用的功能。主要的区别在于，Trio 将经典的队列接口分成了两个对象。这种做法的优势是，它使得将两端放置在不同进程中成为可能，而无需重写代码，并且我们可以分别关闭这两端。

   `MemorySendChannel` 和 `MemoryReceiveChannel` 还提供了超出核心通道接口的其他一些功能：

   .. autoclass:: trio.MemorySendChannel
      :members:

   .. autoclass:: trio.MemoryReceiveChannel
      :members:

   .. autoclass:: trio.MemoryChannelStatistics
      :members:

.. tab:: 英文

   *Channels* allow you to safely and conveniently send objects between
   different tasks. They're particularly useful for implementing
   producer/consumer patterns.

   The core channel API is defined by the abstract base classes
   :class:`trio.abc.SendChannel` and :class:`trio.abc.ReceiveChannel`.
   You can use these to implement your own custom channels, that do
   things like pass objects between processes or over the network. But in
   many cases, you just want to pass objects between different tasks
   inside a single process, and for that you can use
   :func:`trio.open_memory_channel`:

   .. autofunction:: trio.open_memory_channel(max_buffer_size)
      :no-index:

   .. note:: If you've used the :mod:`threading` or :mod:`asyncio`
      modules, you may be familiar with :class:`queue.Queue` or
      :class:`asyncio.Queue`. In Trio, :func:`open_memory_channel` is
      what you use when you're looking for a queue. The main difference
      is that Trio splits the classic queue interface up into two
      objects. The advantage of this is that it makes it possible to put
      the two ends in different processes without rewriting your code,
      and that we can close the two sides separately.

   `MemorySendChannel` and `MemoryReceiveChannel` also expose several
   more features beyond the core channel interface:

   .. autoclass:: trio.MemorySendChannel
      :members:
      :no-index:

   .. autoclass:: trio.MemoryReceiveChannel
      :members:
      :no-index:

   .. autoclass:: trio.MemoryChannelStatistics
      :members:
      :no-index:

一个简单的通道示例
^^^^^^^^^^^^^^^^^^^^^^^^

**A simple channel example**

.. tab:: 中文

   这是一个如何使用内存通道的简单示例：

   .. literalinclude:: reference-core/channels-simple.py

   如果你运行这个程序，它会打印：

   .. code-block:: none

      got value "message 0"
      got value "message 1"
      got value "message 2"

   然后它会一直挂起。（使用控制-C退出。）

.. tab:: 英文

   Here's a simple example of how to use memory channels:

   .. literalinclude:: reference-core/channels-simple.py

   If you run this, it prints:

   .. code-block:: none

      got value "message 0"
      got value "message 1"
      got value "message 2"

   And then it hangs forever. (Use control-C to quit.)


.. _channel-shutdown:

使用通道进行干净关闭
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Clean shutdown with channels**

.. tab:: 中文

   当然，我们通常不希望程序挂起。发生了什么？问题在于生产者发送了 3 条消息后退出了，但消费者无法得知生产者已经消失：对它来说，可能随时会有另一条消息到来。所以它会一直挂起，等待第四条消息。

   这是修复后的新版本：它产生与前一个版本相同的输出，然后干净地退出。唯一的变化是在生产者和消费者中增加了 ``async with`` 块：

   .. literalinclude:: reference-core/channels-shutdown.py
      :emphasize-lines: 12,18

   这里最重要的是生产者的 ``async with``。当生产者退出时，这会关闭 ``send_channel``，这就告诉消费者没有更多的消息要来了，因此它可以干净地退出 ``async for`` 循环。然后程序会退出，因为两个任务都已退出。

   我们还在消费者中添加了一个 ``async with``。这并不是那么重要，但它有助于我们捕捉错误或其他问题。例如，假设消费者由于某种原因提前退出了——可能是因为一个 bug。那么生产者就会把消息发送到空洞中，并可能无限期地卡住。但是，如果消费者关闭了 ``receive_channel``，生产者就会收到一个 :exc:`BrokenResourceError`，提醒它应该停止发送消息，因为没有人在接收。

   如果你想查看消费者提前退出的效果，可以尝试在 ``async for`` 循环中添加一个 ``break`` 语句——你应该会看到生产者收到一个 :exc:`BrokenResourceError`。

.. tab:: 英文

   Of course we don't generally like it when programs hang. What
   happened? The problem is that the producer sent 3 messages and then
   exited, but the consumer has no way to tell that the producer is gone:
   for all it knows, another message might be coming along any moment. So
   it hangs forever waiting for the 4th message.

   Here's a new version that fixes this: it produces the same output as
   the previous version, and then exits cleanly. The only change is the
   addition of ``async with`` blocks inside the producer and consumer:

   .. literalinclude:: reference-core/channels-shutdown.py
      :emphasize-lines: 12,18

   The really important thing here is the producer's ``async with`` .
   When the producer exits, this closes the ``send_channel``, and that
   tells the consumer that no more messages are coming, so it can cleanly
   exit its ``async for`` loop. Then the program shuts down because both
   tasks have exited.

   We also added an ``async with`` to the consumer. This isn't as
   important, but it can help us catch mistakes or other problems. For
   example, suppose that the consumer exited early for some reason –
   maybe because of a bug. Then the producer would be sending messages
   into the void, and might get stuck indefinitely. But, if the consumer
   closes its ``receive_channel``, then the producer will get a
   :exc:`BrokenResourceError` to alert it that it should stop sending
   messages because no-one is listening.

   If you want to see the effect of the consumer exiting early, try
   adding a ``break`` statement to the ``async for`` loop – you should
   see a :exc:`BrokenResourceError` from the producer.


.. _channel-mpmc:

管理多个生产者和/或多个消费者
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Managing multiple producers and/or multiple consumers**

.. tab:: 中文

   你也可以有多个生产者和多个消费者，共享同一个通道。不过，这样做会使得关闭过程稍微复杂一些。

   例如，考虑一下我们之前示例的简单扩展，现在有两个生产者和两个消费者：

   .. literalinclude:: reference-core/channels-mpmc-broken.py

   这两个生产者 A 和 B 每个发送 3 条消息。然后这些消息会随机分配给两个消费者 X 和 Y。因此，我们希望看到类似这样的输出：

   .. code-block:: none

      consumer Y got value '0 from producer B'
      consumer X got value '0 from producer A'
      consumer Y got value '1 from producer A'
      consumer Y got value '1 from producer B'
      consumer X got value '2 from producer B'
      consumer X got value '2 from producer A'

   然而，在大多数情况下，结果并非如此——输出的前一部分是正常的，但当程序运行到结束时，会因为 :exc:`ClosedResourceError` 崩溃。如果你运行几次这个程序，你会发现有时 tracebacks 显示是 ``send`` 崩溃，有时是 ``receive`` 崩溃，甚至有时它根本不会崩溃。

   发生了什么呢？假设生产者 A 最先完成。它退出了，并且它的 ``async with`` 块关闭了 ``send_channel``。但是等等！生产者 B 仍在使用这个 ``send_channel``... 所以下次 B 调用 ``send`` 时，它会遇到 :exc:`ClosedResourceError`。

   然而，有时如果我们幸运的话，两个生产者可能同时完成（或者足够接近），这样它们都在关闭 ``send_channel`` 之前完成最后一次 ``send``。

   但是，即使那样，我们仍然没有完全解决问题！在生产者退出后，两个消费者会争先恐后地检查 ``send_channel`` 是否已关闭。假设 X 赢得了比赛。它退出了 ``async for`` 循环，然后退出了 ``async with`` 块... 并关闭了 ``receive_channel``，而 Y 仍在使用它。再次，这会导致崩溃。

   我们本可以通过一些复杂的账务处理来确保只有 *最后* 一个生产者和 *最后* 一个消费者关闭它们的通道端点... 但那样做会非常繁琐且不可靠。幸运的是，有更好的方法！这是我们上面程序的修复版本：

   .. literalinclude:: reference-core/channels-mpmc-fixed.py
      :emphasize-lines: 8, 10, 11, 13, 14

   这个示例演示了如何使用 `MemorySendChannel.clone` 和 `MemoryReceiveChannel.clone` 方法。它们的作用是创建通道端点的副本，这些副本就像原始端点一样工作——唯一的区别是它们可以独立地关闭。而且，只有在 *所有* 副本都关闭之后，底层的通道才会关闭。因此，这完全解决了我们的关闭问题，如果你运行这个程序，你会看到它打印六行输出后干净地退出。

   请注意我们使用的一个小技巧：``main`` 中的代码创建了克隆对象并将它们传递给所有子任务，然后使用 ``async with`` 关闭原始对象。另一种选择是将副本传递给所有任务（除了最后一个），然后将原始对象传递给最后一个任务，如下所示：

   .. code-block:: python

      # 也有效，但更容易出错：
      send_channel, receive_channel = trio.open_memory_channel(0)
      nursery.start_soon(producer, "A", send_channel.clone())
      nursery.start_soon(producer, "B", send_channel)
      nursery.start_soon(consumer, "X", receive_channel.clone())
      nursery.start_soon(consumer, "Y", receive_channel)

   但是这样更容易出错，尤其是在你使用循环来启动生产者/消费者时。

   请确保不要写：

   .. code-block:: python

      # 错误，程序将挂起：
      send_channel, receive_channel = trio.open_memory_channel(0)
      nursery.start_soon(producer, "A", send_channel.clone())
      nursery.start_soon(producer, "B", send_channel.clone())
      nursery.start_soon(consumer, "X", receive_channel.clone())
      nursery.start_soon(consumer, "Y", receive_channel.clone())

   在这里，我们将副本传递给任务，但从未关闭原始对象。这意味着我们有 3 个发送通道对象（原始对象 + 两个副本），但我们只关闭了 2 个它们，因此消费者将永远等待最后一个通道被关闭。

.. tab:: 英文

   You can also have multiple producers, and multiple consumers, all
   sharing the same channel. However, this makes shutdown a little more
   complicated.

   For example, consider this naive extension of our previous example,
   now with two producers and two consumers:

   .. literalinclude:: reference-core/channels-mpmc-broken.py

   The two producers, A and B, send 3 messages apiece. These are then
   randomly distributed between the two consumers, X and Y. So we're
   hoping to see some output like:

   .. code-block:: none

      consumer Y got value '0 from producer B'
      consumer X got value '0 from producer A'
      consumer Y got value '1 from producer A'
      consumer Y got value '1 from producer B'
      consumer X got value '2 from producer B'
      consumer X got value '2 from producer A'

   However, on most runs, that's not what happens – the first part of the
   output is OK, and then when we get to the end the program crashes with
   :exc:`ClosedResourceError`. If you run the program a few times, you'll
   see that sometimes the traceback shows ``send`` crashing, and other
   times it shows ``receive`` crashing, and you might even find that on
   some runs it doesn't crash at all.

   Here's what's happening: suppose that producer A finishes first. It
   exits, and its ``async with`` block closes the ``send_channel``. But
   wait! Producer B was still using that ``send_channel``... so the next
   time B calls ``send``, it gets a :exc:`ClosedResourceError`.

   Sometimes, though if we're lucky, the two producers might finish at
   the same time (or close enough), so they both make their last ``send``
   before either of them closes the ``send_channel``.

   But, even if that happens, we're not out of the woods yet! After the
   producers exit, the two consumers race to be the first to notice that
   the ``send_channel`` has closed. Suppose that X wins the race. It
   exits its ``async for`` loop, then exits the ``async with`` block...
   and closes the ``receive_channel``, while Y is still using it. Again,
   this causes a crash.

   We could avoid this by using some complicated bookkeeping to make sure
   that only the *last* producer and the *last* consumer close their
   channel endpoints... but that would be tiresome and fragile.
   Fortunately, there's a better way! Here's a fixed version of our
   program above:

   .. literalinclude:: reference-core/channels-mpmc-fixed.py
      :emphasize-lines: 8, 10, 11, 13, 14

   This example demonstrates using the `MemorySendChannel.clone` and
   `MemoryReceiveChannel.clone` methods. What these do is create copies
   of our endpoints, that act just like the original – except that they
   can be closed independently. And the underlying channel is only closed
   after *all* the clones have been closed. So this completely solves our
   problem with shutdown, and if you run this program, you'll see it
   print its six lines of output and then exits cleanly.

   Notice a small trick we use: the code in ``main`` creates clone
   objects to pass into all the child tasks, and then closes the original
   objects using ``async with``. Another option is to pass clones into
   all-but-one of the child tasks, and then pass the original object into
   the last task, like:

   .. code-block:: python

      # Also works, but is more finicky:
      send_channel, receive_channel = trio.open_memory_channel(0)
      nursery.start_soon(producer, "A", send_channel.clone())
      nursery.start_soon(producer, "B", send_channel)
      nursery.start_soon(consumer, "X", receive_channel.clone())
      nursery.start_soon(consumer, "Y", receive_channel)

   But this is more error-prone, especially if you use a loop to spawn
   the producers/consumers.

   Just make sure that you don't write:

   .. code-block:: python

      # Broken, will cause program to hang:
      send_channel, receive_channel = trio.open_memory_channel(0)
      nursery.start_soon(producer, "A", send_channel.clone())
      nursery.start_soon(producer, "B", send_channel.clone())
      nursery.start_soon(consumer, "X", receive_channel.clone())
      nursery.start_soon(consumer, "Y", receive_channel.clone())

   Here we pass clones into the tasks, but never close the original
   objects. That means we have 3 send channel objects (the original + two
   clones), but we only close 2 of them, so the consumers will hang
   around forever waiting for that last one to be closed.


.. _channel-buffering:

在通道中缓冲
^^^^^^^^^^^^^^^^^^^^^

**Buffering in channels**

.. tab:: 中文

   当你调用 :func:`open_memory_channel` 时，必须指定通道中可以缓冲多少个值。如果缓冲区已满，那么任何调用 :meth:`~trio.abc.SendChannel.send` 的任务都会停止，并等待另一个任务调用 :meth:`~trio.abc.ReceiveChannel.receive`。这是有用的，因为它会产生 *背压*：如果通道的生产者运行速度快于消费者，它会迫使生产者放慢速度。

   你可以通过 ``open_memory_channel(0)`` 完全禁用缓冲。在这种情况下，任何调用 :meth:`~trio.abc.SendChannel.send` 的任务都会等待，直到另一个任务调用 :meth:`~trio.abc.ReceiveChannel.receive`，反之亦然。这类似于 `经典的通信顺序进程模型 <https://en.wikipedia.org/wiki/Channel_(programming)>`__ 中通道的工作方式，并且如果你不确定应该使用多大的缓冲区，这是一个合理的默认值。（这就是我们在上面示例中使用它的原因。）

   在另一个极端，你可以通过使用 ``open_memory_channel(math.inf)`` 来使缓冲区无限大。在这种情况下，:meth:`~trio.abc.SendChannel.send` *始终* 会立即返回。通常，这不是一个好主意。为了看清楚为什么，考虑一个生产者运行速度快于消费者的程序：

   .. literalinclude:: reference-core/channels-backpressure.py

   如果你运行这个程序，你会看到类似这样的输出：

   .. code-block:: none

      Sent message: 0
      Received message: 0
      Sent message: 1
      Sent message: 2
      Sent message: 3
      Sent message: 4
      Sent message: 5
      Sent message: 6
      Sent message: 7
      Sent message: 8
      Sent message: 9
      Received message: 1
      Sent message: 10
      Sent message: 11
      Sent message: 12
      ...

   平均而言，生产者每秒发送十条消息，但消费者每秒只调用一次 ``receive``。这意味着每秒，通道的内部缓冲区必须增长以容纳额外的九个项。经过一分钟，缓冲区将包含大约 540 条消息；经过一小时，它将增加到大约 32,400 条。最终，程序将耗尽内存。在我们耗尽内存之前，处理单个消息的延迟将变得极其糟糕。例如，在一分钟时，生产者正在发送大约第 600 条消息，但消费者仍在处理第 60 条消息。第 600 条消息将在通道中等待大约 9 分钟，直到消费者赶上并处理它。

   现在，尝试将 ``open_memory_channel(math.inf)`` 替换为 ``open_memory_channel(0)``，然后再次运行它。我们会看到类似这样的输出：

   .. code-block:: none

      Sent message: 0
      Received message: 0
      Received message: 1
      Sent message: 1
      Received message: 2
      Sent message: 2
      Sent message: 3
      Received message: 3
      ...

   现在， ``send`` 调用会等待 ``receive`` 调用完成，这迫使生产者放慢速度以匹配消费者的速度。（可能看起来有些奇怪的是，一些值在报告为 "Sent" 之前先报告为 "Received"；这是因为实际的发送/接收操作是同时发生的，因此哪一行先打印是随机的。）

   现在，让我们尝试设置一个小但非零的缓冲区大小，如 ``open_memory_channel(3)``。你认为会发生什么？

   我得到的是：

   .. code-block:: none

      Sent message: 0
      Received message: 0
      Sent message: 1
      Sent message: 2
      Sent message: 3
      Received message: 1
      Sent message: 4
      Received message: 2
      Sent message: 5
      ...

   所以你可以看到，生产者提前发送了 3 条消息，然后停止等待：当消费者读取消息 1 时，它发送消息 4，然后当消费者读取消息 2 时，它发送消息 5，依此类推。一旦它达到稳定状态，这个版本的行为就像我们之前将缓冲区大小设置为 0 的版本一样，只是它使用了更多的内存，并且每条消息在被处理之前在缓冲区中停留的时间更长（即消息的延迟更高）。

   当然，真实的生产者和消费者通常比这更复杂，在某些情况下，适量的缓冲可能会提高吞吐量。但过多的缓冲会浪费内存并增加延迟，因此如果你想调整应用程序的性能，应该进行实验，以找出最适合你的缓冲区大小。

   **那么我们为什么还要支持无限缓冲呢？** 好问题！尽管我们上面看到的所有问题，在某些情况下，你确实需要一个无限缓冲区。例如，考虑一个使用通道跟踪所有它仍然想抓取的 URL 的网页爬虫。每个爬虫运行一个循环，它从通道中获取一个 URL，抓取它，检查 HTML 中的外部链接，然后将新的 URL 添加到通道中。这创建了一个 *循环流*，其中每个消费者也是一个生产者。在这种情况下，如果你的通道缓冲区满了，那么爬虫在尝试将新 URL 添加到通道时会被阻塞，如果所有的爬虫都被阻塞，那么它们就无法从通道中取出任何 URL，因此它们永远会陷入死锁。使用无限通道可以避免这种情况，因为它意味着 :meth:`~trio.abc.SendChannel.send` 永远不会阻塞。

.. tab:: 英文

   When you call :func:`open_memory_channel`, you have to specify how
   many values can be buffered internally in the channel. If the buffer
   is full, then any task that calls :meth:`~trio.abc.SendChannel.send`
   will stop and wait for another task to call
   :meth:`~trio.abc.ReceiveChannel.receive`. This is useful because it
   produces *backpressure*: if the channel producers are running faster
   than the consumers, then it forces the producers to slow down.

   You can disable buffering entirely, by doing
   ``open_memory_channel(0)``. In that case any task that calls
   :meth:`~trio.abc.SendChannel.send` will wait until another task calls
   :meth:`~trio.abc.ReceiveChannel.receive`, and vice versa. This is similar to
   how channels work in the `classic Communicating Sequential Processes
   model <https://en.wikipedia.org/wiki/Channel_(programming)>`__, and is
   a reasonable default if you aren't sure what size buffer to use.
   (That's why we used it in the examples above.)

   At the other extreme, you can make the buffer unbounded by using
   ``open_memory_channel(math.inf)``. In this case,
   :meth:`~trio.abc.SendChannel.send` *always* returns immediately.
   Normally, this is a bad idea. To see why, consider a program where the
   producer runs more quickly than the consumer:

   .. literalinclude:: reference-core/channels-backpressure.py

   If you run this program, you'll see output like:

   .. code-block:: none

      Sent message: 0
      Received message: 0
      Sent message: 1
      Sent message: 2
      Sent message: 3
      Sent message: 4
      Sent message: 5
      Sent message: 6
      Sent message: 7
      Sent message: 8
      Sent message: 9
      Received message: 1
      Sent message: 10
      Sent message: 11
      Sent message: 12
      ...

   On average, the producer sends ten messages per second, but the
   consumer only calls ``receive`` once per second. That means that each
   second, the channel's internal buffer has to grow to hold an extra
   nine items. After a minute, the buffer will have ~540 items in it;
   after an hour, that grows to ~32,400. Eventually, the program will run
   out of memory. And well before we run out of memory, our latency on
   handling individual messages will become abysmal. For example, at the
   one minute mark, the producer is sending message ~600, but the
   consumer is still processing message ~60. Message 600 will have to sit
   in the channel for ~9 minutes before the consumer catches up and
   processes it.

   Now try replacing ``open_memory_channel(math.inf)`` with
   ``open_memory_channel(0)``, and run it again. We get output like:

   .. code-block:: none

      Sent message: 0
      Received message: 0
      Received message: 1
      Sent message: 1
      Received message: 2
      Sent message: 2
      Sent message: 3
      Received message: 3
      ...

   Now the ``send`` calls wait for the ``receive`` calls to finish, which
   forces the producer to slow down to match the consumer's speed. (It
   might look strange that some values are reported as "Received" before
   they're reported as "Sent"; this happens because the actual
   send/receive happen at the same time, so which line gets printed first
   is random.)

   Now, let's try setting a small but nonzero buffer size, like
   ``open_memory_channel(3)``. what do you think will happen?

   I get:

   .. code-block:: none

      Sent message: 0
      Received message: 0
      Sent message: 1
      Sent message: 2
      Sent message: 3
      Received message: 1
      Sent message: 4
      Received message: 2
      Sent message: 5
      ...

   So you can see that the producer runs ahead by 3 messages, and then
   stops to wait: when the consumer reads message 1, it sends message 4,
   then when the consumer reads message 2, it sends message 5, and so on.
   Once it reaches the steady state, this version acts just like our
   previous version where we set the buffer size to 0, except that it
   uses a bit more memory and each message sits in the buffer for a bit
   longer before being processed (i.e., the message latency is higher).

   Of course real producers and consumers are usually more complicated
   than this, and in some situations, a modest amount of buffering might
   improve throughput. But too much buffering wastes memory and increases
   latency, so if you want to tune your application you should experiment
   to see what value works best for you.

   **Why do we even support unbounded buffers then?** Good question!
   Despite everything we saw above, there are times when you actually do
   need an unbounded buffer. For example, consider a web crawler that
   uses a channel to keep track of all the URLs it still wants to crawl.
   Each crawler runs a loop where it takes a URL from the channel,
   fetches it, checks the HTML for outgoing links, and then adds the new
   URLs to the channel. This creates a *circular flow*, where each
   consumer is also a producer. In this case, if your channel buffer gets
   full, then the crawlers will block when they try to add new URLs to
   the channel, and if all the crawlers got blocked, then they aren't
   taking any URLs out of the channel, so they're stuck forever in a
   deadlock. Using an unbounded channel avoids this, because it means
   that :meth:`~trio.abc.SendChannel.send` never blocks.


较低级别的同步原语
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Lower-level synchronization primitives**

.. tab:: 中文

   就我个人而言，我发现事件和通道通常足够实现我关心的大多数功能，而且它们比本节中讨论的低级原语更易于阅读代码。但如果你需要它们，它们在这里。（如果你发现自己在使用这些原语来实现新的更高级别的同步原语，那么你可能还想查看 :mod:`trio.lowlevel` 中的设施，以便更直接地接触 Trio 的底层同步逻辑。本节中讨论的所有类都是基于 :mod:`trio.lowlevel` 中的公共 API 实现的；它们没有对 Trio 内部的特殊访问权限。）

   .. autoclass:: trio.CapacityLimiter
      :members:

   .. autoclass:: trio.Semaphore
      :members:

   .. 我们必须在这里使用 :inherited-members:，因为所有实际的锁方法都存储在 _LockImpl 中。这是同时拥有 Lock 和 StrictFIFOLock 的一个奇怪副作用，但希望两者都被标记为 Final，因此它们不能从彼此继承。

   .. autoclass:: trio.Lock
      :members:
      :inherited-members:

   .. autoclass:: trio.StrictFIFOLock
      :members:

   .. autoclass:: trio.Condition
      :members:

   这些原语返回可以被检查的统计对象。

   .. autoclass:: trio.CapacityLimiterStatistics
      :members:

   .. autoclass:: trio.LockStatistics
      :members:

   .. autoclass:: trio.ConditionStatistics
      :members:

.. tab:: 英文

   Personally, I find that events and channels are usually enough to
   implement most things I care about, and lead to easier to read code
   than the lower-level primitives discussed in this section. But if you
   need them, they're here. (If you find yourself reaching for these
   because you're trying to implement a new higher-level synchronization
   primitive, then you might also want to check out the facilities in
   :mod:`trio.lowlevel` for a more direct exposure of Trio's underlying
   synchronization logic. All of classes discussed in this section are
   implemented on top of the public APIs in :mod:`trio.lowlevel`; they
   don't have any special access to Trio's internals.)

   .. autoclass:: trio.CapacityLimiter
      :members:
      :no-index:

   .. autoclass:: trio.Semaphore
      :members:
      :no-index:

   .. We have to use :inherited-members: here because all the actual lock
      methods are stashed in _LockImpl. Weird side-effect of having both
      Lock and StrictFIFOLock, but wanting both to be marked Final so
      neither can inherit from the other.

   .. autoclass:: trio.Lock
      :members:
      :no-index:
      :inherited-members:

   .. autoclass:: trio.StrictFIFOLock
      :members:
      :no-index:

   .. autoclass:: trio.Condition
      :members:
      :no-index:

   These primitives return statistics objects that can be inspected.

   .. autoclass:: trio.CapacityLimiterStatistics
      :members:
      :no-index:

   .. autoclass:: trio.LockStatistics
      :members:
      :no-index:

   .. autoclass:: trio.ConditionStatistics
      :members:
      :no-index: