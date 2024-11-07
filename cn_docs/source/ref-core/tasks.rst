.. _tasks:

任务
======


任务让您可以同时执行多项操作
----------------------------------------

**Tasks let you do multiple things at once**

.. tab:: 中文

   Trio 的核心设计原则之一是：*没有隐式并发*。每个函数按顺序执行，从上到下，完成每个操作后再进行下一个操作—— *正如 Guido 所期望的那样*。

   但是，当然，异步库的主要目的是让你能够同时做多件事。在 Trio 中，实现这一点的唯一方式是通过任务生成接口。因此，如果你希望你的程序既能走路又能嚼口香糖，那么这一节就是为你准备的。

.. tab:: 英文

   One of Trio's core design principles is: *no implicit
   concurrency*. Every function executes in a straightforward,
   top-to-bottom manner, finishing each operation before moving on to the
   next – *like Guido intended*.

   But, of course, the entire point of an async library is to let you do
   multiple things at once. The one and only way to do that in Trio is
   through the task spawning interface. So if you want your program to
   walk *and* chew gum, this is the section for you.

托儿所和生成
~~~~~~~~~~~~~~~~~~~~~~

**Nurseries and spawning**

.. tab:: 中文

   大多数并发编程库允许你在任何时候、任何地方随意启动新的子任务（或线程，或其他什么）。但 Trio 稍有不同：除非你准备好成为一个负责任的父母，否则你不能启动子任务。你通过创建一个托儿所来展示你的责任：

   .. code-block:: python

      async with trio.open_nursery() as nursery:
         ...

   一旦你有了托儿所对象的引用，你就可以在该托儿所中启动子任务：

   .. code-block:: python

      async def child():
         ...

      async def parent():
         async with trio.open_nursery() as nursery:
            # 同时调用两个 child() 任务
            nursery.start_soon(child)
            nursery.start_soon(child)

   这意味着任务形成了一棵树：当你调用 :func:`run` 时，它会创建一个初始任务，所有其他任务将是初始任务的子任务、孙任务等。

   本质上，``async with`` 块的主体就像是在托儿所中运行的初始任务，然后每次调用 ``nursery.start_soon`` 都会添加一个并行运行的任务。需要记住的两件关键事情：

   * 如果托儿所中的任何任务以未处理的异常结束，则托儿所会立即取消所有托儿所中的任务。

   * 由于所有任务都在 ``async with`` 块内并发运行，因此该块不会退出，直到 *所有* 任务都完成。如果你使用过其他并发框架，可以将其理解为，``async with`` 末尾的去缩进操作自动“等待”（join）托儿所中的所有任务。

   * 一旦所有任务完成：

   * 托儿所被标记为“关闭”，意味着不能再在其中启动新任务。

   * 任何未处理的异常将被重新引发，并作为一个单一的 :exc:`BaseExceptionGroup` 或 :exc:`ExceptionGroup` 异常返回给父任务。

   由于所有任务都是初始任务的后代，因此一个后果是 :func:`run` 在所有任务完成之前不能结束。

   .. note::

      如果托儿所中仍有任务正在运行，返回语句不会取消托儿所：

      .. code-block:: python

         async def main():
               async with trio.open_nursery() as nursery:
                  nursery.start_soon(trio.sleep, 5)
                  return

         trio.run(main)

      这段代码将等待 5 秒钟（直到子任务完成），然后返回。

.. tab:: 英文

   Most libraries for concurrent programming let you start new child
   tasks (or threads, or whatever) willy-nilly, whenever and where-ever
   you feel like it. Trio is a bit different: you can't start a child
   task unless you're prepared to be a responsible parent. The way you
   demonstrate your responsibility is by creating a nursery:

   .. code-block:: python

      async with trio.open_nursery() as nursery:
         ...

   And once you have a reference to a nursery object, you can start
   children in that nursery:

   .. code-block:: python

      async def child():
         ...

      async def parent():
         async with trio.open_nursery() as nursery:
            # Make two concurrent calls to child()
            nursery.start_soon(child)
            nursery.start_soon(child)

   This means that tasks form a tree: when you call :func:`run`, then
   this creates an initial task, and all your other tasks will be
   children, grandchildren, etc. of the initial task.

   Essentially, the body of the ``async with`` block acts like an initial
   task that's running inside the nursery, and then each call to
   ``nursery.start_soon`` adds another task that runs in parallel. Two
   crucial things to keep in mind:

   * If any task inside the nursery finishes with an unhandled exception,
   then the nursery immediately cancels all the tasks inside the
   nursery.

   * Since all of the tasks are running concurrently inside the ``async
   with`` block, the block does not exit until *all* tasks have
   completed. If you've used other concurrency frameworks, then you can
   think of it as, the de-indentation at the end of the ``async with``
   automatically "joins" (waits for) all of the tasks in the nursery.

   * Once all the tasks have finished, then:

   * The nursery is marked as "closed", meaning that no new tasks can
      be started inside it.

   * Any unhandled exceptions are re-raised inside the parent task, grouped into a
      single :exc:`BaseExceptionGroup` or :exc:`ExceptionGroup` exception.

   Since all tasks are descendents of the initial task, one consequence
   of this is that :func:`run` can't finish until all tasks have
   finished.

   .. note::

      A return statement will not cancel the nursery if it still has tasks running:

      .. code-block:: python

         async def main():
               async with trio.open_nursery() as nursery:
                  nursery.start_soon(trio.sleep, 5)
                  return

         trio.run(main)

      This code will wait 5 seconds (for the child task to finish), and then return.

子任务和取消
~~~~~~~~~~~~~~~~

**Child tasks and cancellation**

.. tab:: 中文

   在 Trio 中，子任务继承父托儿所的取消作用域。所以在这个示例中，当超时到期时，两个子任务都会被取消：

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
         async with trio.open_nursery() as nursery:
            nursery.start_soon(child1)
            nursery.start_soon(child2)

   请注意，这里重要的是在调用 :func:`open_nursery` 时处于活动状态的作用域，而不是在调用 ``start_soon`` 时处于活动状态的作用域。因此，下面的超时块实际上什么都不做：

   .. code-block:: python

      async with trio.open_nursery() as nursery:
         with trio.move_on_after(TIMEOUT):  # 不要这样做！
            nursery.start_soon(child)

   为什么会这样呢？原因在于，``start_soon()`` 会在调度新任务开始执行后立即返回。然后，父任务的执行流继续，退出 ``with trio.move_on_after(TIMEOUT):`` 块，此时 Trio 完全忘记了超时。为了让超时应用于子任务，Trio 必须能够确认其关联的取消作用域会持续有效，至少与子任务执行的时间一样长。而 Trio 只有在取消作用域块位于托儿所块之外时，才能确定这一点。

   你可能会想，为什么 Trio 不能仅仅记住“这个任务应该在 ``TIMEOUT`` 秒内取消”，即使 ``with trio.move_on_after(TIMEOUT):`` 块已经结束？原因与 :ref:`如何实现取消 <cancellation>` 相关。回想一下，取消是通过 `Cancelled` 异常表示的，这个异常最终需要由引发它的取消作用域捕获。（否则，这个异常会导致你的整个程序崩溃！）为了能够取消子任务，取消作用域必须能够“看到”它们引发的 `Cancelled` 异常——而这些异常是从 ``async with open_nursery()`` 块中抛出的，而不是从对 ``start_soon()`` 的调用中抛出的。

   如果你希望超时只对某个任务生效而不是其他任务，那么你需要将取消作用域放在该任务的函数内部——例如在这个示例中的 ``child()`` 函数内。

.. tab:: 英文

   In Trio, child tasks inherit the parent nursery's cancel scopes. So in
   this example, both the child tasks will be cancelled when the timeout
   expires:

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
         async with trio.open_nursery() as nursery:
            nursery.start_soon(child1)
            nursery.start_soon(child2)

   Note that what matters here is the scopes that were active when
   :func:`open_nursery` was called, *not* the scopes active when
   ``start_soon`` is called. So for example, the timeout block below does
   nothing at all:

   .. code-block:: python

      async with trio.open_nursery() as nursery:
         with trio.move_on_after(TIMEOUT):  # don't do this!
            nursery.start_soon(child)

   Why is this so? Well, ``start_soon()`` returns as soon as it has scheduled the new task to start running. The flow of execution in the parent then continues on to exit the ``with trio.move_on_after(TIMEOUT):`` block, at which point Trio forgets about the timeout entirely. In order for the timeout to apply to the child task, Trio must be able to tell that its associated cancel scope will stay open for at least as long as the child task is executing. And Trio can only know that for sure if the cancel scope block is outside the nursery block.

   You might wonder why Trio can't just remember "this task should be cancelled in ``TIMEOUT`` seconds", even after the ``with trio.move_on_after(TIMEOUT):`` block is gone. The reason has to do with :ref:`how cancellation is implemented <cancellation>`. Recall that cancellation is represented by a `Cancelled` exception, which eventually needs to be caught by the cancel scope that caused it. (Otherwise, the exception would take down your whole program!) In order to be able to cancel the child tasks, the cancel scope has to be able to "see" the `Cancelled` exceptions that they raise -- and those exceptions come out of the ``async with open_nursery()`` block, not out of the call to ``start_soon()``.

   If you want a timeout to apply to one task but not another, then you need to put the cancel scope in that individual task's function -- ``child()``, in this example.

.. _exceptiongroups:

多个子任务中的错误
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Errors in multiple child tasks**

.. tab:: 中文

   在 Python 中，通常一次只有一件事情发生，这意味着一次只能出错一件事。Trio 没有这种限制。考虑以下代码：

   .. code-block:: python

      async def broken1():
         d = {}
         return d["missing"]

      async def broken2():
         seq = range(10)
         return seq[20]

      async def parent():
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)
               nursery.start_soon(broken2)

   ``broken1`` 会引发 ``KeyError``，``broken2`` 会引发 ``IndexError``。显然，``parent`` 应该引发某种错误，但是什么错误呢？答案是，这两个异常被分组在一个 :exc:`ExceptionGroup` 中。 :exc:`ExceptionGroup` 及其父类 :exc:`BaseExceptionGroup` 用于封装同时抛出的多个异常。

   为了捕获被异常组封装的单个异常，Python 3.11 引入了 ``except*`` 语句（见 :pep:`654`）。它的工作方式如下：

   .. code-block:: python

      try:
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)
               nursery.start_soon(broken2)
      except* KeyError as excgroup:
         for exc in excgroup.exceptions:
               ...  # 处理每个 KeyError
      except* IndexError as excgroup:
         for exc in excgroup.exceptions:
               ...  # 处理每个 IndexError

   如果你想重新抛出异常，或者抛出新的异常，也是可以的，但请注意，``except*`` 语句中的异常会作为一个新的异常组一起抛出。

   但是如果你还不能使用 Python 3.11，因此还不能使用 ``except*`` 呢？同样，`ExceptionGroup` 的回溯库 exceptiongroup_ 也允许你通过异常处理回调函数来近似这种行为：

   .. code-block:: python

      from exceptiongroup import catch

      def handle_keyerrors(excgroup):
         for exc in excgroup.exceptions:
               ...  # 处理每个 KeyError

      def handle_indexerrors(excgroup):
         for exc in excgroup.exceptions:
               ...  # 处理每个 IndexError

      with catch({
         KeyError: handle_keyerrors,
         IndexError: handle_indexerrors
      }):
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)
               nursery.start_soon(broken2)

   这些处理函数的语义与 ``except*`` 块相同，唯一不同的是设置局部变量。如果你需要在处理函数中设置局部变量，你需要使用 ``nonlocal`` 关键字在处理函数内声明它们：

   .. code-block:: python

      def handle_keyerrors(excgroup):
         nonlocal myflag
         myflag = True

      myflag = False
      with catch({KeyError: handle_keyerrors}):
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)

.. tab:: 英文

   Normally, in Python, only one thing happens at a time, which means
   that only one thing can go wrong at a time. Trio has no such
   limitation. Consider code like:

   .. code-block:: python

      async def broken1():
         d = {}
         return d["missing"]

      async def broken2():
         seq = range(10)
         return seq[20]

      async def parent():
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)
               nursery.start_soon(broken2)

   ``broken1`` raises ``KeyError``. ``broken2`` raises
   ``IndexError``. Obviously ``parent`` should raise some error, but
   what? The answer is that both exceptions are grouped in an :exc:`ExceptionGroup`.
   :exc:`ExceptionGroup` and its parent class :exc:`BaseExceptionGroup` are used to
   encapsulate multiple exceptions being raised at once.

   To catch individual exceptions encapsulated in an exception group, the ``except*``
   clause was introduced in Python 3.11 (:pep:`654`). Here's how it works:

   .. code-block:: python

      try:
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)
               nursery.start_soon(broken2)
      except* KeyError as excgroup:
         for exc in excgroup.exceptions:
               ...  # handle each KeyError
      except* IndexError as excgroup:
         for exc in excgroup.exceptions:
               ...  # handle each IndexError

   If you want to reraise exceptions, or raise new ones, you can do so, but be aware that
   exceptions raised in ``except*`` sections will be raised together in a new exception
   group.

   But what if you can't use Python 3.11, and therefore ``except*``, just yet?
   The same exceptiongroup_ library which backports `ExceptionGroup`  also lets
   you approximate this behavior with exception handler callbacks:

   .. code-block:: python

      from exceptiongroup import catch

      def handle_keyerrors(excgroup):
         for exc in excgroup.exceptions:
               ...  # handle each KeyError

      def handle_indexerrors(excgroup):
         for exc in excgroup.exceptions:
               ...  # handle each IndexError

      with catch({
         KeyError: handle_keyerrors,
         IndexError: handle_indexerrors
      }):
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)
               nursery.start_soon(broken2)

   The semantics for the handler functions are equal to ``except*`` blocks, except for
   setting local variables. If you need to set local variables, you need to declare them
   inside the handler function(s) with the ``nonlocal`` keyword:

   .. code-block:: python

      def handle_keyerrors(excgroup):
         nonlocal myflag
         myflag = True

      myflag = False
      with catch({KeyError: handle_keyerrors}):
         async with trio.open_nursery() as nursery:
               nursery.start_soon(broken1)

.. _handling_exception_groups:

针对多个错误进行设计
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Designing for multiple errors**

.. tab:: 中文

   结构化并发仍然是一个较新的设计模式，但我们已经识别出几种模式，您（或您的用户）可能希望处理异常组的方式。请注意，最后一种模式，即直接引发 `ExceptionGroup`，是最常见的——而且 nurseries 会自动为您执行此操作。

   **首先**，您可能希望“优先处理”某个特定的异常类型，如果该类型的异常出现在异常组中，就只引发该类型的异常。例如：`KeyboardInterrupt` 对于周围的代码具有明确的意义，可以合理地优先于其他类型的错误，无论您有一个还是多个这样的异常，都没有太大区别。

   这种模式通常可以使用装饰器或上下文管理器实现，例如 :func:`trio_util.multi_error_defer_to` 或 :func:`trio_util.defer_to_cancelled`。然而，请注意，重新引发“叶子”异常会丢失附加到 `ExceptionGroup` 本身的 traceback，因此我们不推荐在会向人类展示的错误中使用这种方式。

   ..
      TODO: `Cancelled` 呢？它与 `KeyboardInterrupt` 有些相似，但是如果您有多个指向不同范围的 `Cancelled` 异常，似乎放弃除一个之外的所有异常可能不好——我们可能会尝试执行一些代码，结果又被取消，导致更多的清理工作。尽管如此，这只是一种轻微的低效，整体语义是合理的。

   **第二**，您可能希望将代码中的并发处理视为对用户隐藏的实现细节——例如，将涉及数据发送和接收的协议抽象为一个简单的只接收接口，或实现一个在 ``async with`` 块的生命周期内维护某些后台任务的上下文管理器。

   这里的简单选项是 ``raise MySpecificError from group``，允许用户处理您库中特定的错误。这很简单且可靠，但并不能完全隐藏 nursery。*不要* 解包单个异常，如果可能会有多个异常，这样做总会导致潜在的 bug 和故障。

   更复杂的选项是确保一次只能发生一个异常。这是 *非常难* 的，例如，您需要以某种方式处理 `KeyboardInterrupt`，我们强烈建议在出现多个异常的情况时，使用 ``raise PleaseReportBug from group`` 作为回退。如果您正在编写一个启动后台任务的上下文管理器，并将控制权交给用户代码，这种方式非常有用，用户代码有效地在 nursery 块的主体内运行。在这种情况下，您可以使用例如 `outcome
   <https://pypi.org/project/outcome/>`__ 库来确保只引发一个异常（来自最终用户代码）；然后，如果后台任务失败，您可以 ``raise SomeInternalError``，或者如果那是唯一的错误，则解包用户异常。

   ..
      更多关于此模式的内容，请参见 https://github.com/python-trio/trio/issues/2929
      以及 trio-websocket 上的相关问题。我们可能希望提供一个 nursery 模式，
      自动处理此情况；这虽然麻烦，但并不复杂，似乎是一个不错的功能，适合在此类情况下发布。

   **第三且最常见的是**，您代码中 nursery 的存在不仅仅是一个实现细节，调用者 *应该* 准备好处理以 `ExceptionGroup` 形式出现的多个异常，无论是通过 ``except*``，手动检查，还是让它传播到 *他们的* 调用者。因为这种情况非常常见，所以 nurseries 的默认行为就是如此，您无需做任何事情。

.. tab:: 英文

   Structured concurrency is still a young design pattern, but there are a few patterns
   we've identified for how you (or your users) might want to handle groups of exceptions.
   Note that the final pattern, simply raising an `ExceptionGroup`, is the most common -
   and nurseries automatically do that for you.

   **First**, you might want to 'defer to' a particular exception type, raising just that if
   there is any such instance in the group.  For example: `KeyboardInterrupt` has a clear
   meaning for the surrounding code, could reasonably take priority over errors of other
   types, and whether you have one or several of them doesn't really matter.

   This pattern can often be implemented using a decorator or a context manager, such
   as :func:`trio_util.multi_error_defer_to` or :func:`trio_util.defer_to_cancelled`.
   Note however that re-raising a 'leaf' exception will discard whatever part of the
   traceback is attached to the `ExceptionGroup` itself, so we don't recommend this for
   errors that will be presented to humans.

   ..
      TODO: what about `Cancelled`?  It's relevantly similar to `KeyboardInterrupt`,
      but if you have multiple Cancelleds destined for different scopes, it seems
      like it might be bad to abandon all-but-one of those - we might try to execute
      some more code which then itself gets cancelled again, and incur more cleanup.
      That's only a mild inefficiency though, and the semantics are fine overall.

   **Second**, you might want to treat the concurrency inside your code as an implementation
   detail which is hidden from your users - for example, abstracting a protocol which
   involves sending and receiving data to a simple receive-only interface, or implementing
   a context manager which maintains some background tasks for the length of the
   ``async with`` block.

   The simple option here is to ``raise MySpecificError from group``, allowing users to
   handle your library-specific error.  This is simple and reliable, but doesn't completely
   hide the nursery.  *Do not* unwrap single exceptions if there could ever be multiple
   exceptions though; that always ends in latent bugs and then tears.

   The more complex option is to ensure that only one exception can in fact happen at a time.
   This is *very hard*, for example you'll need to handle `KeyboardInterrupt` somehow, and
   we strongly recommend having a ``raise PleaseReportBug from group`` fallback just in case
   you get a group containing more than one exception.
   This is useful when writing a context manager which starts some background tasks, and then
   yields to user code which effectively runs 'inline' in the body of the nursery block.
   In this case, the background tasks can be wrapped with e.g. the `outcome
   <https://pypi.org/project/outcome/>`__ library to ensure that only one exception
   can be raised (from end-user code); and then you can either ``raise SomeInternalError``
   if a background task failed, or unwrap the user exception if that was the only error.

   ..
      For more on this pattern, see https://github.com/python-trio/trio/issues/2929
      and the linked issue on trio-websocket.  We may want to provide a nursery mode
      which handles this automatically; it's annoying but not too complicated and
      seems like it might be a good feature to ship for such cases.

   **Third and most often**, the existence of a nursery in your code is not just an
   implementation detail, and callers *should* be prepared to handle multiple exceptions
   in the form of an `ExceptionGroup`, whether with ``except*`` or manual inspection
   or by just letting it propagate to *their* callers.  Because this is so common,
   it's nurseries' default behavior and you don't need to do anything.

.. _strict_exception_groups:

注意历史: “非严格” ExceptionGroups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Historical Note: "non-strict" ExceptionGroups**

.. tab:: 中文

   在早期版本的 Trio 中， ``except*`` 语法还没有被构思出来，我们当时还没有长时间或在大型代码库中使用结构化并发。为了方便起见，一些 API 会引发单个异常，只有在发生两个或更多并发异常时，才会将它们包装成旧的 ``trio.MultiError`` 类型。

   不幸的是，结果并不好：调用代码通常没有意识到某个函数 *可能* 会引发 ``MultiError``，因此只处理了常见的情况——这导致在测试中一切正常，但在更大的负载下（通常是在生产环境中）崩溃。 :py:class:`asyncio.TaskGroup` 从这一经验中吸取了教训， *始终* 将错误包装成 :exc:`ExceptionGroup` ， ``anyio`` 也如此，从 Trio 0.25 开始，这也是我们的默认行为。

   我们当前支持一个兼容性参数 ``strict_exception_groups=False``，用于 :func:`trio.run` 和 :func:`trio.open_nursery`，它恢复了旧的行为（尽管 ``MultiError`` 本身已被完全移除）。我们强烈建议新的代码不要使用此选项，并鼓励现有的使用者进行迁移——我们视此选项为废弃，计划在一段时间的文档和运行时警告后移除它。

.. tab:: 英文

   In early versions of Trio, the ``except*`` syntax hadn't be dreamt up yet, and we
   hadn't worked with structured concurrency for long or in large codebases.
   As a concession to convenience, some APIs would therefore raise single exceptions,
   and only wrap concurrent exceptions in the old ``trio.MultiError`` type if there
   were two or more.

   Unfortunately, the results were not good: calling code often didn't realize that
   some function *could* raise a ``MultiError``, and therefore handle only the common
   case - with the result that things would work well in testing, and then crash under
   heavier load (typically in production).  :py:class:`asyncio.TaskGroup` learned from this
   experience and *always* wraps errors into an :exc:`ExceptionGroup`, as does ``anyio``,
   and as of Trio 0.25 that's our default behavior too.

   We currently support a compatibility argument ``strict_exception_groups=False`` to
   :func:`trio.run` and :func:`trio.open_nursery`, which restores the old behavior (although
   ``MultiError`` itself has been fully removed).  We strongly advise against it for
   new code, and encourage existing uses to migrate - we consider the option deprecated
   and plan to remove it after a period of documented and then runtime warnings.

.. _exceptiongroup: https://pypi.org/project/exceptiongroup/

生成任务而不成为父级
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Spawning tasks without becoming a parent**

.. tab:: 中文

   有时，对于启动子任务的任务来说，承担监视该任务的责任并不合适。例如，服务器任务可能希望为每个连接启动一个新的任务，但它无法同时监听连接和监督子任务。

   一旦你明白了这一点，解决方案就很简单：并没有要求一个 nursery 对象必须保持在创建它的任务中！我们可以像这样编写代码：

   .. code-block:: python

      async def new_connection_listener(handler, nursery):
         while True:
            conn = await get_new_connection()
            nursery.start_soon(handler, conn)

      async def server(handler):
         async with trio.open_nursery() as nursery:
            nursery.start_soon(new_connection_listener, handler, nursery)

   注意， ``server`` 打开了一个 nursery，并将其传递给了 ``new_connection_listener``，然后 ``new_connection_listener`` 就能够像“兄弟任务”一样启动新任务。当然，在这个例子中，我们也可以这样写：

   .. code-block:: python

      async def server(handler):
         async with trio.open_nursery() as nursery:
            while True:
                  conn = await get_new_connection()
                  nursery.start_soon(handler, conn)

   \...但有时事情并不那么简单，这个技巧就派上了用场。

   不过有一点需要记住：取消作用域是从 nursery 继承的， **而不是** 从调用 ``start_soon`` 的任务继承的。所以在这个例子中，超时并不会应用于 ``child`` （或其他任何任务）：

   .. code-block:: python

      async def do_spawn(nursery):
         with trio.move_on_after(TIMEOUT):  # 不要这样做，它没有效果
            nursery.start_soon(child)

      async with trio.open_nursery() as nursery:
         nursery.start_soon(do_spawn, nursery)

.. tab:: 英文

   Sometimes it doesn't make sense for the task that starts a child to
   take on responsibility for watching it. For example, a server task may
   want to start a new task for each connection, but it can't listen for
   connections and supervise children at the same time.

   The solution here is simple once you see it: there's no requirement
   that a nursery object stay in the task that created it! We can write
   code like this:

   .. code-block:: python

      async def new_connection_listener(handler, nursery):
         while True:
            conn = await get_new_connection()
            nursery.start_soon(handler, conn)

      async def server(handler):
         async with trio.open_nursery() as nursery:
            nursery.start_soon(new_connection_listener, handler, nursery)

   Notice that ``server`` opens a nursery and passes it to
   ``new_connection_listener``, and then ``new_connection_listener`` is
   able to start new tasks as "siblings" of itself. Of course, in this
   case, we could just as well have written:

   .. code-block:: python

      async def server(handler):
         async with trio.open_nursery() as nursery:
            while True:
                  conn = await get_new_connection()
                  nursery.start_soon(handler, conn)

   \...but sometimes things aren't so simple, and this trick comes in
   handy.

   One thing to remember, though: cancel scopes are inherited from the
   nursery, **not** from the task that calls ``start_soon``. So in this
   example, the timeout does *not* apply to ``child`` (or to anything
   else):

   .. code-block:: python

      async def do_spawn(nursery):
         with trio.move_on_after(TIMEOUT):  # don't do this, it has no effect
            nursery.start_soon(child)

      async with trio.open_nursery() as nursery:
         nursery.start_soon(do_spawn, nursery)


自定义主管
~~~~~~~~~~~~~~~~~~

**Custom supervisors**

.. tab:: 中文

   默认的清理逻辑通常足以应对简单情况，但如果你想要一个更复杂的监控器呢？例如，也许你有 `Erlang envy <http://learnyousomeerlang.com/supervisors>`__ ，并希望拥有自动重启崩溃任务之类的功能。Trio 本身并不提供这些功能，但你可以在其基础上构建它们；Trio 的目标是强制执行基本的清理规范，然后不干扰你的操作。（具体来说：Trio 不允许你构建一个退出并留下孤儿任务的监控器，如果你因为错误或懒惰而有未处理的异常，Trio 会确保它们传播。）然后，你可以将你精致的监控器封装到一个库中并发布到 PyPI，因为监控器很棘手，没必要每个人都重新写一个。

   例如，这里有一个函数，它接收一个函数列表，所有函数并发执行，并返回第一个完成的任务的结果：

   .. code-block:: python

      async def race(*async_fns):
         if not async_fns:
            raise ValueError("must pass at least one argument")

         winner = None

         async def jockey(async_fn, cancel_scope):
            nonlocal winner
            winner = await async_fn()
            cancel_scope.cancel()

         async with trio.open_nursery() as nursery:
            for async_fn in async_fns:
                  nursery.start_soon(jockey, async_fn, nursery.cancel_scope)

         return winner

   这段代码通过启动一组任务，每个任务尝试执行它们各自的函数。只要第一个函数完成执行，任务就会将外部作用域中的 `winner` 非局部变量设置为该函数的结果，并使用传入的取消作用域取消其他任务。一旦所有任务被取消（这会退出 nursery 块），就会返回 `winner` 变量。

   在这里，如果一个或多个竞赛函数抛出未处理的异常，Trio 的正常处理机制会启动：它取消其他任务，然后传播该异常。如果你希望有不同的行为，可以通过在 `jockey` 函数中添加一个 `try` 块来捕获异常，并按你的需求处理这些异常。

.. tab:: 英文

   The default cleanup logic is often sufficient for simple cases, but
   what if you want a more sophisticated supervisor? For example, maybe
   you have `Erlang envy <http://learnyousomeerlang.com/supervisors>`__
   and want features like automatic restart of crashed tasks. Trio itself
   doesn't provide these kinds of features, but you can build them on
   top; Trio's goal is to enforce basic hygiene and then get out of your
   way. (Specifically: Trio won't let you build a supervisor that exits
   and leaves orphaned tasks behind, and if you have an unhandled
   exception due to bugs or laziness then Trio will make sure they
   propagate.) And then you can wrap your fancy supervisor up in a
   library and put it on PyPI, because supervisors are tricky and there's
   no reason everyone should have to write their own.

   For example, here's a function that takes a list of functions, runs
   them all concurrently, and returns the result from the one that
   finishes first:

   .. code-block:: python

      async def race(*async_fns):
         if not async_fns:
            raise ValueError("must pass at least one argument")

         winner = None

         async def jockey(async_fn, cancel_scope):
            nonlocal winner
            winner = await async_fn()
            cancel_scope.cancel()

         async with trio.open_nursery() as nursery:
            for async_fn in async_fns:
                  nursery.start_soon(jockey, async_fn, nursery.cancel_scope)

         return winner

   This works by starting a set of tasks which each try to run their
   function. As soon as the first function completes its execution, the task will set the nonlocal variable ``winner``
   from the outer scope to the result of the function, and cancel the other tasks using the passed in cancel scope. Once all tasks
   have been cancelled (which exits the nursery block), the variable ``winner`` will be returned.

   Here if one or more of the racing functions raises an unhandled
   exception then Trio's normal handling kicks in: it cancels the others
   and then propagates the exception. If you want different behavior, you
   can get that by adding a ``try`` block to the ``jockey`` function to
   catch exceptions and handle them however you like.


与任务相关的 API 详细信息
~~~~~~~~~~~~~~~~~~~~~~~~

**Task-related API details**

托儿所 API
^^^^^^^^^^^^^^^

**The nursery API**

.. autofunction:: trio.open_nursery
   :async-with: nursery


.. autoclass:: trio.Nursery()
   :members: child_tasks, parent_task

   .. automethod:: start(async_fn, *args, name = None)

   .. automethod:: start_soon(async_fn, *args, name = None)

.. attribute:: trio.TASK_STATUS_IGNORED
   :type: TaskStatus

   See :meth:`Nursery.start`.

.. autoclass:: trio.TaskStatus(Protocol[StatusT])
   :members: