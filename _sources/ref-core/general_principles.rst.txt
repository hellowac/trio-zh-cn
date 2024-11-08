.. module:: trio

一般原则
------------------

**General principles**

.. _checkpoints:

检查点
~~~~~~~~~~~

**Checkpoints**

.. tab:: 中文

   在使用 Trio 编写代码时，理解 *检查点* 的概念非常重要。Trio 的许多函数充当了检查点。

   检查点有两个作用：

   1. 它是 Trio 检查取消操作的一个点。例如，如果调用您函数的代码设置了超时，并且超时已经过期，那么在您的函数执行到下一个检查点时，Trio 会引发一个 :exc:`Cancelled` 异常。有关更多详细信息，请参见下文的 :ref:`cancellation`。

   2. 它是 Trio 调度器检查其调度策略的一个点，用来判断是否是切换到另一个任务的好时机，并可能会执行此操作。（目前，这个检查非常简单：调度器在每个检查点都会切换。但 `将来这可能会改变 <https://github.com/python-trio/trio/issues/32>`__。）

   在编写 Trio 代码时，您需要跟踪检查点的位置。为什么？首先，因为检查点需要额外的注意：每当您执行检查点时，您需要准备好处理 :exc:`Cancelled` 错误，或者准备好让另一个任务运行并 `重新安排一些状态
   <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`__。其次，您还需要确保有 *足够* 的检查点：如果您的代码没有定期通过检查点，那么它会慢慢发现并响应取消操作，而且—更糟糕的是—由于 Trio 是一个协作多任务系统，调度器 *唯一* 可以切换任务的地方就是检查点，这也会阻止调度器在不同任务之间公平分配时间，并对所有其他代码在同一进程中的响应延迟产生不利影响。（非正式地说，一个做这种事情的任务被称为“霸占运行循环”。）

   因此，当您进行使用 Trio 的项目的代码审查时，您需要考虑的一件事是是否有足够的检查点，以及每个检查点是否被正确处理。当然，这意味着您需要一种识别检查点的方法。如何做到这一点呢？基本原则是，任何阻塞操作都必须是一个检查点。这是有道理的：如果一个操作阻塞，那么它可能会阻塞很长时间，而您希望能够在超时过期时取消它；无论如何，在这个任务被阻塞时，我们希望调度另一个任务来运行，这样我们的代码就能充分利用 CPU。

   但是，如果我们想要编写正确的代码，那么这个原则有点太模糊和不精确，无法提供足够的帮助。我们如何知道哪些函数可能会阻塞？如果一个函数有时会阻塞，但有时不会，这取决于传入的参数/网络速度/月相如何？当我们感到压力山大、睡眠不足，但仍希望正确进行代码审查时，我们如何找到检查点的位置，并希望将思维精力保留用于思考实际的逻辑，而不是担心检查点？

.. tab:: 英文

   When writing code using Trio, it's very important to understand the
   concept of a *checkpoint*. Many of Trio's functions act as checkpoints.

   A checkpoint is two things:

   1. It's a point where Trio checks for cancellation. For example, if
      the code that called your function set a timeout, and that timeout
      has expired, then the next time your function executes a checkpoint
      Trio will raise a :exc:`Cancelled` exception. See
      :ref:`cancellation` below for more details.

   2. It's a point where the Trio scheduler checks its scheduling policy
      to see if it's a good time to switch to another task, and
      potentially does so. (Currently, this check is very simple: the
      scheduler always switches at every checkpoint. But `this might
      change in the future
      <https://github.com/python-trio/trio/issues/32>`__.)

   When writing Trio code, you need to keep track of where your
   checkpoints are. Why? First, because checkpoints require extra
   scrutiny: whenever you execute a checkpoint, you need to be prepared
   to handle a :exc:`Cancelled` error, or for another task to run and
   `rearrange some state out from under you
   <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`__. And
   second, because you also need to make sure that you have *enough*
   checkpoints: if your code doesn't pass through a checkpoint on a
   regular basis, then it will be slow to notice and respond to
   cancellation and – much worse – since Trio is a cooperative
   multi-tasking system where the *only* place the scheduler can switch
   tasks is at checkpoints, it'll also prevent the scheduler from fairly
   allocating time between different tasks and adversely effect the
   response latency of all the other code running in the same
   process. (Informally we say that a task that does this is "hogging the
   run loop".)

   So when you're doing code review on a project that uses Trio, one of
   the things you'll want to think about is whether there are enough
   checkpoints, and whether each one is handled correctly. Of course this
   means you need a way to recognize checkpoints. How do you do that?
   The underlying principle is that any operation that blocks has to be a
   checkpoint. This makes sense: if an operation blocks, then it might
   block for a long time, and you'll want to be able to cancel it if a
   timeout expires; and in any case, while this task is blocked we want
   another task to be scheduled to run so our code can make full use of
   the CPU.

   But if we want to write correct code in practice, then this principle
   is a little too sloppy and imprecise to be useful. How do we know
   which functions might block?  What if a function blocks sometimes, but
   not others, depending on the arguments passed / network speed / phase
   of the moon? How do we figure out where the checkpoints are when
   we're stressed and sleep deprived but still want to get this code
   review right, and would prefer to reserve our mental energy for
   thinking about the actual logic instead of worrying about checkpoints?

.. _checkpoint-rule:

检查点规则
^^^^^^^^^^^^^^^^^^

**Checkpoint Rule**

.. tab:: 中文

   不用担心——Trio 会为您提供帮助。由于检查点非常重要并且无处不在，我们使得跟踪它们变得尽可能简单。以下是一些规则：

   * 常规（同步）函数永远不包含任何检查点。

   * 如果您调用 Trio 提供的异步函数（``await <something in trio>``），并且它没有引发异常，那么它 *始终* 会作为一个检查点。（如果它引发异常，它可能会充当检查点，也可能不会。）

   * 这包括异步迭代器：如果您写了 ``async for ... in <Trio object>``，那么在每次循环迭代中至少会有一个检查点，即使可迭代对象为空，它也会执行检查点。

   * 异步上下文管理器的部分例外： ``async with`` 块的入口和退出都被定义为异步函数；但是，对于某些类型的异步上下文管理器，通常只有其中一个能够阻塞，这意味着只有那个函数会作为检查点。具体情况会在每个案例中进行文档说明。

     * :func:`trio.open_nursery` 是该规则的一个进一步例外。

   * 第三方异步函数/迭代器/上下文管理器也可以充当检查点；如果您看到 ``await <something>`` 或其类似函数，那么它 *可能* 是一个检查点。因此，为了安全起见，您应该准备好在这里发生调度或取消。

   我们区分 Trio 函数和其他函数的原因是我们不能对第三方代码做任何保证。检查点属性是一个传递性属性：如果函数 A 充当检查点，并且您编写一个调用函数 A 的函数，那么您的函数也会充当检查点。如果您没有这么做，那么它就不是。因此，没人会阻止某人编写一个像这样的函数：

   .. code-block:: python

      # 技术上是合法的，但风格很差：
      async def why_is_this_async():
         return 7

   它从不调用 Trio 的任何异步函数。虽然这是一个异步函数，但它不是一个检查点。但是，为什么要让一个函数变成异步函数，如果它从不调用任何异步函数呢？这是可能的，但这是一个坏主意。如果您有一个没有调用任何异步函数的函数，那么您应该将其设置为同步。使用您函数的人会感谢您，因为这样可以明确表示您的函数不是一个检查点，他们的代码审查也会更快。

   （还记得在教程中我们强调了 :ref:`"async sandwich" <async-sandwich>` 的重要性吗？它意味着 ``await`` 最终成为一个标记，显示您在调用一个调用一个 ... 最终调用 Trio 内置的异步函数的函数？异步性的传递性是 Python 强加的技术要求，但由于它恰好与检查点的传递性相匹配，我们能够利用它帮助您跟踪检查点。很巧妙吧？）

   一个稍微棘手的情况是像这样的函数：

   .. code-block:: python

      async def sleep_or_not(should_sleep):
         if should_sleep:
            await trio.sleep(1)
         else:
            pass

   如果您传递给它一个 `should_sleep` 为真值，它将作为一个检查点，但在其他情况下则不会。这就是为什么我们强调 Trio 自己的异步函数是 *无条件* 检查点的原因：它们 *始终* 会检查取消操作并检查调度，而不管传递给它们的参数是什么。如果您发现 Trio 中的某个异步函数没有遵循这个规则，那么它就是一个 bug，您应该 `告诉我们
   <https://github.com/python-trio/trio/issues>`__。

   在 Trio 内部，我们对这一点非常挑剔，因为 Trio 是整个系统的基础，因此我们认为付出额外的努力使事情更加可预测是值得的。至于您的代码有多挑剔，就由您决定。为了给您一个更现实的例子，看看实际生活中这种问题是什么样的，考虑以下函数：

   .. code-block:: python

      async def recv_exactly(sock, nbytes):
         data = bytearray()
         while nbytes > 0:
               # recv() 每次最多读取 'nbytes' 字节
               chunk = await sock.recv(nbytes)
               if not chunk:
                  raise RuntimeError("socket 意外关闭")
               nbytes -= len(chunk)
               data += chunk
         return data

   如果 `nbytes` 大于零，则它将至少调用一次 ``sock.recv``，而 ``recv`` 是一个 Trio 异步函数，因此是一个无条件检查点。因此，在这种情况下，``recv_exactly`` 充当了检查点。但是如果我们执行 ``await recv_exactly(sock, 0)``，它将立即返回一个空缓冲区，而不会执行任何检查点。如果这是 Trio 本身的一个函数，那么这是不可接受的，但您可能会决定不想在自己的代码中担心这种小的边缘情况。

   如果您确实想要小心，或者如果您有一些没有足够检查点的 CPU 密集型代码，那么了解 ``await trio.sleep(0)`` 是一种惯用方法，可以在不做任何其他操作的情况下执行一个检查点，并且 :func:`trio.testing.assert_checkpoints` 可以用来测试任意代码块是否包含检查点，这将非常有用。

.. tab:: 英文

   Don't worry – Trio's got your back. Since checkpoints are important
   and ubiquitous, we make it as simple as possible to keep track of
   them. Here are the rules:

   * Regular (synchronous) functions never contain any checkpoints.

   * If you call an async function provided by Trio (``await
   <something in trio>``), and it doesn't raise an exception,
   then it *always* acts as a checkpoint. (If it does raise an
   exception, it might act as a checkpoint or might not.)

   * This includes async iterators: If you write ``async for ... in <a
      trio object>``, then there will be at least one checkpoint in
      each iteration of the loop, and it will still checkpoint if the
      iterable is empty.

   * Partial exception for async context managers:
      Both the entry and exit of an ``async with`` block are
      defined as async functions; but for a
      particular type of async context manager, it's often the
      case that only one of them is able to block, which means
      only that one will act as a checkpoint. This is documented
      on a case-by-case basis.

      * :func:`trio.open_nursery` is a further exception to this rule.

   * Third-party async functions / iterators / context managers can act
   as checkpoints; if you see ``await <something>`` or one of its
   friends, then that *might* be a checkpoint. So to be safe, you
   should prepare for scheduling or cancellation happening there.

   The reason we distinguish between Trio functions and other functions
   is that we can't make any guarantees about third party
   code. Checkpoint-ness is a transitive property: if function A acts as
   a checkpoint, and you write a function that calls function A, then
   your function also acts as a checkpoint. If you don't, then it
   isn't. So there's nothing stopping someone from writing a function
   like:

   .. code-block:: python

      # technically legal, but bad style:
      async def why_is_this_async():
         return 7

   that never calls any of Trio's async functions. This is an async
   function, but it's not a checkpoint. But why make a function async if
   it never calls any async functions? It's possible, but it's a bad
   idea. If you have a function that's not calling any async functions,
   then you should make it synchronous. The people who use your function
   will thank you, because it makes it obvious that your function is not
   a checkpoint, and their code reviews will go faster.

   (Remember how in the tutorial we emphasized the importance of the
   :ref:`"async sandwich" <async-sandwich>`, and the way it means that
   ``await`` ends up being a marker that shows when you're calling a
   function that calls a function that ... eventually calls one of Trio's
   built-in async functions? The transitivity of async-ness is a
   technical requirement that Python imposes, but since it exactly
   matches the transitivity of checkpoint-ness, we're able to exploit it
   to help you keep track of checkpoints. Pretty sneaky, eh?)

   A slightly trickier case is a function like:

   .. code-block:: python

      async def sleep_or_not(should_sleep):
         if should_sleep:
            await trio.sleep(1)
         else:
            pass

   Here the function acts as a checkpoint if you call it with
   ``should_sleep`` set to a true value, but not otherwise. This is why
   we emphasize that Trio's own async functions are *unconditional* checkpoints:
   they *always* check for cancellation and check for scheduling,
   regardless of what arguments they're passed. If you find an async
   function in Trio that doesn't follow this rule, then it's a bug and
   you should `let us know
   <https://github.com/python-trio/trio/issues>`__.

   Inside Trio, we're very picky about this, because Trio is the
   foundation of the whole system so we think it's worth the extra effort
   to make things extra predictable. It's up to you how picky you want to
   be in your code. To give you a more realistic example of what this
   kind of issue looks like in real life, consider this function:

   .. code-block:: python

      async def recv_exactly(sock, nbytes):
         data = bytearray()
         while nbytes > 0:
               # recv() reads up to 'nbytes' bytes each time
               chunk = await sock.recv(nbytes)
               if not chunk:
                  raise RuntimeError("socket unexpected closed")
               nbytes -= len(chunk)
               data += chunk
         return data

   If called with an ``nbytes`` that's greater than zero, then it will
   call ``sock.recv`` at least once, and ``recv`` is an async Trio
   function, and thus an unconditional checkpoint. So in this case,
   ``recv_exactly`` acts as a checkpoint. But if we do ``await
   recv_exactly(sock, 0)``, then it will immediately return an empty
   buffer without executing a checkpoint. If this were a function in
   Trio itself, then this wouldn't be acceptable, but you may decide you
   don't want to worry about this kind of minor edge case in your own
   code.

   If you do want to be careful, or if you have some CPU-bound code that
   doesn't have enough checkpoints in it, then it's useful to know that
   ``await trio.sleep(0)`` is an idiomatic way to execute a checkpoint
   without doing anything else, and that
   :func:`trio.testing.assert_checkpoints` can be used to test that an
   arbitrary block of code contains a checkpoint.


线程安全
~~~~~~~~~~~~~

**Thread safety**

.. tab:: 中文

   Trio 的绝大多数 API *不是* 线程安全的：它只能在 :func:`trio.run` 的调用内部使用。本手册不会在各个调用上单独说明这一点；除非特别注明，否则您应该假设除 Trio 线程外的任何地方都不安全调用任何 Trio 函数。（但如果您确实需要与线程一起工作，请 :ref:`参见下面 <threads>`。）

.. tab:: 英文

   The vast majority of Trio's API is *not* thread safe: it can only be
   used from inside a call to :func:`trio.run`. This manual doesn't
   bother documenting this on individual calls; unless specifically noted
   otherwise, you should assume that it isn't safe to call any Trio
   functions from anywhere except the Trio thread. (But :ref:`see below
   <threads>` if you really do need to work with threads.)
