.. module:: trio
   
.. _async-generators:

异步生成器注意事项
-------------------------

**Notes on async generators**

.. tab:: 中文

   Python 3.6 增加了对 *异步生成器* 的支持，这些生成器可以在它们的 ``yield`` 语句之间使用 ``await``、``async for`` 和 ``async with``。正如你所期望的那样，你可以使用 ``async for`` 来迭代它们。如果你需要更多细节，可以参考 :pep:`525` 。

   例如，以下是一个间接的方式，用于打印从 0 到 9 的数字，并在每个数字前添加 1 秒的延迟：

   .. code-block:: python

      async def range_slowly(*args):
         """像 range()，但在每个值之前添加 1 秒的延迟。"""
         for value in range(*args):
               await trio.sleep(1)
               yield value

      async def use_it():
         async for value in range_slowly(10):
               print(value)

      trio.run(use_it)

   Trio 支持异步生成器，但本节中描述了一些需要注意的事项。

.. tab:: 英文

   Python 3.6 added support for *async generators*, which can use
   ``await``, ``async for``, and ``async with`` in between their ``yield``
   statements. As you might expect, you use ``async for`` to iterate
   over them. :pep:`525` has many more details if you want them.

   For example, the following is a roundabout way to print
   the numbers 0 through 9 with a 1-second delay before each one:

   .. code-block:: python

      async def range_slowly(*args):
         """Like range(), but adds a 1-second sleep before each value."""
         for value in range(*args):
               await trio.sleep(1)
               yield value

      async def use_it():
         async for value in range_slowly(10):
               print(value)

      trio.run(use_it)

   Trio supports async generators, with some caveats described in this section.

Finalization
~~~~~~~~~~~~

**Finalization**

.. tab:: 中文

   如果你完全迭代一个异步生成器，就像上面的示例那样，那么异步生成器的执行将在迭代它的代码上下文中完全进行，通常不会有太多意外。

   然而，如果你放弃了一个部分完成的异步生成器，比如通过在迭代中使用 ``break`` 跳出循环，那么情况就不那么简单了。异步生成器的迭代器对象仍然存在，等待你恢复迭代以便它可以生成更多的值。到某个时刻，Python 会意识到你已经丢弃了对该迭代器的所有引用，并会请求 Trio 抛出 `GeneratorExit` 异常，以便生成器内部的任何剩余清理代码有机会运行：例如 ``finally`` 块、``__aexit__`` 处理程序等。

   到这里为止，一切正常。不幸的是，Python 对 *何时* 发生这种情况没有任何保证。它可能会在你跳出 ``async for`` 循环时发生，或者在任意时间之后发生。它甚至可能发生在整个 Trio 运行结束之后！唯一可以保证的是，它 *不会* 在使用生成器的任务中发生。该任务将继续执行它正在做的其他事情，异步生成器的清理将在 "稍后的某个时候、某个地方" 发生：可能使用不同的上下文变量，不受超时限制，和/或在你使用的任何托儿所关闭之后。

   如果你不喜欢这种模糊性，并且希望确保生成器的 ``finally`` 块和 ``__aexit__`` 处理程序在你完成使用时立即执行，那么你需要将生成器的使用包装在类似 `async_generator.aclosing() <https://async-generator.readthedocs.io/en/latest/reference.html#context-managers>`__ 的结构中：

   .. code-block:: python

      # 替代这一部分:
      async for value in my_generator():
         if value == 42:
               break

      # 使用这个:
      async with aclosing(my_generator()) as aiter:
         async for value in aiter:
               if value == 42:
                  break

   这虽然有点繁琐，但不幸的是，Python 并没有提供其他可靠的选项。如果你使用 ``aclosing()``，那么生成器的清理代码将在与其余迭代相同的上下文中执行，因此超时、异常和上下文变量会按预期工作。

   如果你不使用 ``aclosing()``，那么 Trio 仍会尽力处理，但你需要处理以下语义：

   * 生成器的清理发生在一个已取消的上下文中，即所有在清理过程中执行的阻塞调用将引发 `Cancelled` 异常。这是为了弥补原始使用生成器时的任何超时已被遗忘的事实。

   * 清理过程无法访问任何在生成器最初使用时可能存在的 :ref:`上下文变量 <task-local-storage>`。

   * 如果生成器在清理过程中引发异常，它会被打印到 ``trio.async_generator_errors`` 日志器，并且会被忽略。

   * 如果一个异步生成器在整个 :func:`trio.run` 调用结束时仍然存在，那么它将在所有任务退出后，并且在 :func:`trio.run` 返回之前被清理。由于此时 "系统托儿所" 已经关闭，Trio 无法支持任何新的 :func:`trio.lowlevel.spawn_system_task` 调用。

   如果你计划在 PyPy 上运行你的代码以利用其更好的性能，你应该意识到 PyPy 比 CPython 更有可能在生成器的最后一次使用之后较长时间执行异步生成器的清理。（这是因为 PyPy 不使用引用计数来管理内存。）为了帮助捕捉此类问题，Trio 会为每个需要通过后备清理路径处理的异步生成器发出 `ResourceWarning`（默认情况下被忽略，但例如在 ``python -X dev`` 下运行时会启用）。

.. tab:: 英文

   If you iterate over an async generator in its entirety, like the
   example above does, then the execution of the async generator will
   occur completely in the context of the code that's iterating over it,
   and there aren't too many surprises.

   If you abandon a partially-completed async generator, though, such as
   by ``break``\ing out of the iteration, things aren't so simple.  The
   async generator iterator object is still alive, waiting for you to
   resume iterating it so it can produce more values. At some point,
   Python will realize that you've dropped all references to the
   iterator, and will call on Trio to throw in a `GeneratorExit` exception
   so that any remaining cleanup code inside the generator has a chance
   to run: ``finally`` blocks, ``__aexit__`` handlers, and so on.

   So far, so good. Unfortunately, Python provides no guarantees about
   *when* this happens. It could be as soon as you break out of the
   ``async for`` loop, or an arbitrary amount of time later. It could
   even be after the entire Trio run has finished! Just about the only
   guarantee is that it *won't* happen in the task that was using the
   generator. That task will continue on with whatever else it's doing,
   and the async generator cleanup will happen "sometime later,
   somewhere else": potentially with different context variables,
   not subject to timeouts, and/or after any nurseries you're using have
   been closed.

   If you don't like that ambiguity, and you want to ensure that a
   generator's ``finally`` blocks and ``__aexit__`` handlers execute as
   soon as you're done using it, then you'll need to wrap your use of the
   generator in something like `async_generator.aclosing()
   <https://async-generator.readthedocs.io/en/latest/reference.html#context-managers>`__:

   .. code-block:: python

      # Instead of this:
      async for value in my_generator():
         if value == 42:
               break

      # Do this:
      async with aclosing(my_generator()) as aiter:
         async for value in aiter:
               if value == 42:
                  break

   This is cumbersome, but Python unfortunately doesn't provide any other
   reliable options. If you use ``aclosing()``, then
   your generator's cleanup code executes in the same context as the
   rest of its iterations, so timeouts, exceptions, and context
   variables work like you'd expect.

   If you don't use ``aclosing()``, then Trio will do
   its best anyway, but you'll have to contend with the following semantics:

   * The cleanup of the generator occurs in a cancelled context, i.e.,
   all blocking calls executed during cleanup will raise `Cancelled`.
   This is to compensate for the fact that any timeouts surrounding
   the original use of the generator have been long since forgotten.

   * The cleanup runs without access to any :ref:`context variables
   <task-local-storage>` that may have been present when the generator
   was originally being used.

   * If the generator raises an exception during cleanup, then it's
   printed to the ``trio.async_generator_errors`` logger and otherwise
   ignored.

   * If an async generator is still alive at the end of the whole
   call to :func:`trio.run`, then it will be cleaned up after all
   tasks have exited and before :func:`trio.run` returns.
   Since the "system nursery" has already been closed at this point,
   Trio isn't able to support any new calls to
   :func:`trio.lowlevel.spawn_system_task`.

   If you plan to run your code on PyPy to take advantage of its better
   performance, you should be aware that PyPy is *far more likely* than
   CPython to perform async generator cleanup at a time well after the
   last use of the generator. (This is a consequence of the fact that
   PyPy does not use reference counting to manage memory.)  To help catch
   issues like this, Trio will issue a `ResourceWarning` (ignored by
   default, but enabled when running under ``python -X dev`` for example)
   for each async generator that needs to be handled through the fallback
   finalization path.

取消范围和托儿所
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cancel scopes and nurseries**

.. tab:: 中文

   .. warning:: 你不能在异步生成器内部的 `CancelScope` 或 `Nursery` 中写出一个挂起异步生成器的 ``yield`` 语句。

   也就是说，下面是可以的：

   .. code-block:: python

      async def some_agen():
         with trio.move_on_after(1):
               await long_operation()
         yield "first"
         async with trio.open_nursery() as nursery:
               nursery.start_soon(task1)
               nursery.start_soon(task2)
         yield "second"
         ...

   但下面的代码则不可以：

   .. code-block:: python

      async def some_agen():
         with trio.move_on_after(1):
               yield "first"
         async with trio.open_nursery() as nursery:
               yield "second"
         ...

   使用 ``@asynccontextmanager`` 装饰的异步生成器作为异步上下文管理器的模板 *不* 受此限制，因为 ``@asynccontextmanager`` 以一种有限的方式使用它们，这样就不会产生问题。

   违反本节中描述的规则有时会给出有用的错误信息，但 Trio 无法检测到所有此类情况，所以有时你可能会遇到一个无用的 `TrioInternalError`。（有时它看起来会正常工作，这可能是最糟糕的结果，因为你可能直到进行一些小的重构，或者代码迭代生成器时才注意到问题，或者只是运气不好。至少有一个 `提议的 Python 增强功能 <https://discuss.python.org/t/preventing-yield-inside-certain-context-managers/1091>`__，它会让这个问题一致地失败。）

   关于取消范围的限制，原因在于很难察觉到生成器何时被挂起和恢复。生成器内部的取消范围不应影响生成器外部的代码，但 Trio 并未参与退出和重新进入生成器的过程，因此它很难保持其取消机制的正确状态。托儿所内部使用了取消范围，所以它们不仅有取消范围的问题，还有自己的问题：例如，当生成器被挂起时，后台任务应该做什么？没有好的方法来挂起它们，但如果它们继续运行并抛出异常，这个异常应该在哪里重新抛出？

   如果你有一个希望在托儿所或取消范围内 ``yield`` 的异步生成器，最好的做法是将它重构为一个单独的任务，通过内存通道进行通信。``trio_util`` 包提供了一个 `装饰器，可以透明地为你完成这个操作
   <https://trio-util.readthedocs.io/en/latest/#trio_util.trio_async_generator>`__。

   有关更多讨论，请参见 Trio 问题 `264 <https://github.com/python-trio/trio/issues/264>`__ （尤其是 `这个评论
   <https://github.com/python-trio/trio/issues/264#issuecomment-418989328>`__ ）和 `638 <https://github.com/python-trio/trio/issues/638>`__ 。
 
.. tab:: 英文

   .. warning:: You may not write a ``yield`` statement that suspends an async generator
      inside a `CancelScope` or `Nursery` that was entered within the generator.

   That is, this is OK:

   .. code-block:: python

      async def some_agen():
         with trio.move_on_after(1):
               await long_operation()
         yield "first"
         async with trio.open_nursery() as nursery:
               nursery.start_soon(task1)
               nursery.start_soon(task2)
         yield "second"
         ...

   But this is not:

   .. code-block:: python

      async def some_agen():
         with trio.move_on_after(1):
               yield "first"
         async with trio.open_nursery() as nursery:
               yield "second"
         ...

   Async generators decorated with ``@asynccontextmanager`` to serve as
   the template for an async context manager are *not* subject to this
   constraint, because ``@asynccontextmanager`` uses them in a limited
   way that doesn't create problems.

   Violating the rule described in this section will sometimes get you a
   useful error message, but Trio is not able to detect all such cases,
   so sometimes you'll get an unhelpful `TrioInternalError`. (And
   sometimes it will seem to work, which is probably the worst outcome of
   all, since then you might not notice the issue until you perform some
   minor refactoring of the generator or the code that's iterating it, or
   just get unlucky. There is a `proposed Python enhancement
   <https://discuss.python.org/t/preventing-yield-inside-certain-context-managers/1091>`__
   that would at least make it fail consistently.)

   The reason for the restriction on cancel scopes has to do with the
   difficulty of noticing when a generator gets suspended and
   resumed. The cancel scopes inside the generator shouldn't affect code
   running outside the generator, but Trio isn't involved in the process
   of exiting and reentering the generator, so it would be hard pressed
   to keep its cancellation plumbing in the correct state. Nurseries
   use a cancel scope internally, so they have all the problems of cancel
   scopes plus a number of problems of their own: for example, when
   the generator is suspended, what should the background tasks do?
   There's no good way to suspend them, but if they keep running and throw
   an exception, where can that exception be reraised?

   If you have an async generator that wants to ``yield`` from within a nursery
   or cancel scope, your best bet is to refactor it to be a separate task
   that communicates over memory channels.  The ``trio_util`` package offers a
   `decorator that does this for you transparently
   <https://trio-util.readthedocs.io/en/latest/#trio_util.trio_async_generator>`__.

   For more discussion, see
   Trio issues `264 <https://github.com/python-trio/trio/issues/264>`__
   (especially `this comment
   <https://github.com/python-trio/trio/issues/264#issuecomment-418989328>`__)
   and `638 <https://github.com/python-trio/trio/issues/638>`__.