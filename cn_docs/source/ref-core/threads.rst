.. module:: trio

.. _threads:

线程（如果必须）
---------------------

**Threads (if you must)**

.. tab:: 中文

   在一个完美的世界里，所有的第三方库和低级 API 都应该是原生的异步，并且与 Trio 集成，一切都会是幸福和美好的。

   然而，遗憾的是，这个世界（目前）并不存在。在此之前，你可能需要与一些非 Trio 的 API 进行交互，这些 API 做一些类似“阻塞”的事情。

   为了应对这一现实，Trio 提供了两个有用的工具，用于处理真实的操作系统级别的、类似于 :mod:`threading` 模块风格的线程。首先，如果你在 Trio 中，但需要将一些阻塞 I/O 操作推送到线程中，你可以使用 :func:`trio.to_thread.run_sync` 。如果你在一个线程中，并且需要与 Trio 进行通信，你可以使用 :func:`trio.from_thread.run` 和 :func:`trio.from_thread.run_sync` 。

.. tab:: 英文

   In a perfect world, all third-party libraries and low-level APIs would
   be natively async and integrated into Trio, and all would be happiness
   and rainbows.

   That world, alas, does not (yet) exist. Until it does, you may find
   yourself needing to interact with non-Trio APIs that do rude things
   like "blocking".

   In acknowledgment of this reality, Trio provides two useful utilities
   for working with real, operating-system level,
   :mod:`threading`\-module-style threads. First, if you're in Trio but
   need to push some blocking I/O into a thread, there's
   :func:`trio.to_thread.run_sync`. And if you're in a thread and need
   to communicate back with Trio, you can use
   :func:`trio.from_thread.run` and :func:`trio.from_thread.run_sync`.


.. _worker-thread-limiting:

Trio 关于管理工作线程的理念
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Trio's philosophy about managing worker threads**



.. tab:: 中文

   如果你使用过其他 I/O 框架，可能会遇到“线程池”这个概念，线程池通常实现为一个固定大小的线程集合，线程在等待任务分配时挂起。这解决了两个不同的问题：首先，反复使用相同的线程比每次都启动和停止一个新线程更有效；本质上，线程池充当了空闲线程的缓存。其次，固定大小的线程池避免了出现同时提交 100,000 个任务的情况，然后启动 100,000 个线程，导致系统过载并崩溃。相反，N 个线程开始执行前 N 个任务，而其他 (100,000 - N) 个任务则排队等待。这通常是你想要的行为，而这也是 :func:`trio.to_thread.run_sync` 默认的工作方式。

   这种线程池的缺点是，有时你需要更复杂的逻辑来控制同时运行的线程数量。例如，你可能想要一种策略：“最多允许 20 个线程，但其中最多 3 个线程可以执行与同一个用户账户相关的任务”，或者你可能想要一个根据系统条件动态调整大小的线程池。

   固定大小的策略甚至可能导致意外的 `死锁 <https://en.wikipedia.org/wiki/Deadlock>`__。假设我们有两种不同类型的阻塞任务需要在线程池中运行，类型 A 和类型 B。类型 A 比较简单：它运行并很快完成。但是类型 B 更复杂：它必须在中间停下来，等待其他工作完成，而这些工作包括执行一个类型 A 的任务。现在，假设你提交了 N 个类型 B 的任务到线程池。它们开始执行，然后最终提交一个或多个类型 A 的任务。但由于池中的每个线程都已经在忙，类型 A 的任务实际上没有开始执行——它们只是排队等候类型 B 的任务完成。但是类型 B 的任务永远不会完成，因为它们在等待类型 A 的任务。我们的系统发生了死锁。解决这个问题的理想方案是避免首先出现类型 B 的任务——通常最好将复杂的同步逻辑保留在主 Trio 线程中。但如果你不能这么做，那么你需要一个自定义的线程分配策略来跟踪不同类型任务的单独限制，确保类型 B 的任务不会占满类型 A 任务需要执行的所有线程槽。

   因此，我们可以看到，能够改变控制线程分配给任务的策略是很重要的。但在许多框架中，这需要从头开始实现一个新的线程池，这非常复杂；如果不同类型的任务需要不同的策略，那么你可能需要创建多个线程池，这样效率就低了，因为你实际上拥有两个不同的线程缓存，它们不能共享资源。

   Trio 解决这个问题的办法是将工作线程管理分为两层。下层负责接收阻塞 I/O 任务，并安排它们立即在某个工作线程上执行。它解决了管理线程时涉及的复杂并发问题，并负责像线程重用这样的优化，但没有入池控制策略：如果你给它 100,000 个任务，它会启动 100,000 个线程。上层负责提供策略，以确保不会发生这种情况——但由于它*只*需要关注策略，它可以更简单。事实上，唯一需要做的就是传递给 :func:`trio.to_thread.run_sync` 的 ``limiter=`` 参数。默认情况下，它是一个全局的 :class:`CapacityLimiter` 对象，这为我们提供了经典的固定大小线程池行为。（请参阅 :func:`trio.to_thread.current_default_thread_limiter`。）但是，如果你想为类型 A 任务和类型 B 任务使用“独立的线程池”，那么只需创建两个独立的 :class:`CapacityLimiter` 对象，并在运行这些任务时传入它们。或者，下面是一个示例，定义了一个自定义策略，既尊重全局线程限制，同时又确保每个用户在任何时候最多只能使用 3 个线程：

   .. code-block:: python

      class CombinedLimiter:
         def __init__(self, first, second):
               self._first = first
               self._second = second

         async def acquire_on_behalf_of(self, borrower):
               # 获取两个限制器，确保出错时正确清理
               await self._first.acquire_on_behalf_of(borrower)
               try:
                  await self._second.acquire_on_behalf_of(borrower)
               except:
                  self._first.release_on_behalf_of(borrower)
                  raise

         def release_on_behalf_of(self, borrower):
               # 释放两个限制器，确保出错时正确清理
               try:
                  self._second.release_on_behalf_of(borrower)
               finally:
                  self._first.release_on_behalf_of(borrower)


      # 使用弱引用字典，以免浪费内存来保存没有正在运行的工作线程的用户的限制器对象。
      USER_LIMITERS = weakref.WeakValueDictionary()
      MAX_THREADS_PER_USER = 3

      def get_user_limiter(user_id):
         try:
            return USER_LIMITERS[user_id]
         except KeyError:
            per_user_limiter = trio.CapacityLimiter(MAX_THREADS_PER_USER)
            global_limiter = trio.current_default_thread_limiter()
            # 重要：首先获取 per_user_limiter，再获取 global_limiter。
            # 如果我们同时为某个用户提交 100 个任务，我们希望
            # 只允许其中 3 个任务竞争全局线程槽。
            combined_limiter = CombinedLimiter(per_user_limiter, global_limiter)
            USER_LIMITERS[user_id] = combined_limiter
            return combined_limiter


      async def run_sync_in_thread_for_user(user_id, sync_fn, *args):
         combined_limiter = get_user_limiter(user_id)
         return await trio.to_thread.run_sync(sync_fn, *args, limiter=combined_limiter)
   

.. tab:: 英文

   If you've used other I/O frameworks, you may have encountered the
   concept of a "thread pool", which is most commonly implemented as a
   fixed size collection of threads that hang around waiting for jobs to
   be assigned to them. These solve two different problems: First,
   re-using the same threads over and over is more efficient than
   starting and stopping a new thread for every job you need done;
   basically, the pool acts as a kind of cache for idle threads. And
   second, having a fixed size avoids getting into a situation where
   100,000 jobs are submitted simultaneously, and then 100,000 threads
   are spawned and the system gets overloaded and crashes. Instead, the N
   threads start executing the first N jobs, while the other
   (100,000 - N) jobs sit in a queue and wait their turn. Which is
   generally what you want, and this is how
   :func:`trio.to_thread.run_sync` works by default.

   The downside of this kind of thread pool is that sometimes, you need
   more sophisticated logic for controlling how many threads are run at
   once. For example, you might want a policy like "at most 20 threads
   total, but no more than 3 of those can be running jobs associated with
   the same user account", or you might want a pool whose size is
   dynamically adjusted over time in response to system conditions.

   It's even possible for a fixed-size policy to cause unexpected
   `deadlocks <https://en.wikipedia.org/wiki/Deadlock>`__. Imagine a
   situation where we have two different types of blocking jobs that you
   want to run in the thread pool, type A and type B. Type A is pretty
   simple: it just runs and completes pretty quickly. But type B is more
   complicated: it has to stop in the middle and wait for some other work
   to finish, and that other work includes running a type A job. Now,
   suppose you submit N jobs of type B to the pool. They all start
   running, and then eventually end up submitting one or more jobs of
   type A. But since every thread in our pool is already busy, the type A
   jobs don't actually start running – they just sit in a queue waiting
   for the type B jobs to finish. But the type B jobs will never finish,
   because they're waiting for the type A jobs. Our system has
   deadlocked. The ideal solution to this problem is to avoid having type
   B jobs in the first place – generally it's better to keep complex
   synchronization logic in the main Trio thread. But if you can't do
   that, then you need a custom thread allocation policy that tracks
   separate limits for different types of jobs, and make it impossible
   for type B jobs to fill up all the slots that type A jobs need to run.

   So, we can see that it's important to be able to change the policy
   controlling the allocation of threads to jobs. But in many frameworks,
   this requires implementing a new thread pool from scratch, which is
   highly non-trivial; and if different types of jobs need different
   policies, then you may have to create multiple pools, which is
   inefficient because now you effectively have two different thread
   caches that aren't sharing resources.

   Trio's solution to this problem is to split worker thread management
   into two layers. The lower layer is responsible for taking blocking
   I/O jobs and arranging for them to run immediately on some worker
   thread. It takes care of solving the tricky concurrency problems
   involved in managing threads and is responsible for optimizations like
   re-using threads, but has no admission control policy: if you give it
   100,000 jobs, it will spawn 100,000 threads. The upper layer is
   responsible for providing the policy to make sure that this doesn't
   happen – but since it *only* has to worry about policy, it can be much
   simpler. In fact, all there is to it is the ``limiter=`` argument
   passed to :func:`trio.to_thread.run_sync`. This defaults to a global
   :class:`CapacityLimiter` object, which gives us the classic fixed-size
   thread pool behavior. (See
   :func:`trio.to_thread.current_default_thread_limiter`.) But if you
   want to use "separate pools" for type A jobs and type B jobs, then
   it's just a matter of creating two separate :class:`CapacityLimiter`
   objects and passing them in when running these jobs. Or here's an
   example of defining a custom policy that respects the global thread
   limit, while making sure that no individual user can use more than 3
   threads at a time:

   .. code-block:: python

      class CombinedLimiter:
         def __init__(self, first, second):
               self._first = first
               self._second = second

         async def acquire_on_behalf_of(self, borrower):
               # Acquire both, being careful to clean up properly on error
               await self._first.acquire_on_behalf_of(borrower)
               try:
                  await self._second.acquire_on_behalf_of(borrower)
               except:
                  self._first.release_on_behalf_of(borrower)
                  raise

         def release_on_behalf_of(self, borrower):
               # Release both, being careful to clean up properly on error
               try:
                  self._second.release_on_behalf_of(borrower)
               finally:
                  self._first.release_on_behalf_of(borrower)


      # Use a weak value dictionary, so that we don't waste memory holding
      # limiter objects for users who don't have any worker threads running.
      USER_LIMITERS = weakref.WeakValueDictionary()
      MAX_THREADS_PER_USER = 3

      def get_user_limiter(user_id):
         try:
            return USER_LIMITERS[user_id]
         except KeyError:
            per_user_limiter = trio.CapacityLimiter(MAX_THREADS_PER_USER)
            global_limiter = trio.current_default_thread_limiter()
            # IMPORTANT: acquire the per_user_limiter before the global_limiter.
            # If we get 100 jobs for a user at the same time, we want
            # to only allow 3 of them at a time to even compete for the
            # global thread slots.
            combined_limiter = CombinedLimiter(per_user_limiter, global_limiter)
            USER_LIMITERS[user_id] = combined_limiter
            return combined_limiter


      async def run_sync_in_thread_for_user(user_id, sync_fn, *args):
         combined_limiter = get_user_limiter(user_id)
         return await trio.to_thread.run_sync(sync_fn, *args, limiter=combined_limiter)


.. module:: trio.to_thread

.. currentmodule:: trio

将阻塞 I/O 放入工作线程
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Putting blocking I/O into worker threads**

.. autofunction:: trio.to_thread.run_sync

.. autofunction:: trio.to_thread.current_default_thread_limiter


.. module:: trio.from_thread
.. currentmodule:: trio

从另一个线程返回 Trio 线程
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Getting back into the Trio thread from another thread**

.. tab:: 中文

   .. autofunction:: trio.from_thread.run

   .. autofunction:: trio.from_thread.run_sync

   这通过一个示例可能会更清晰。这里我们演示如何启动一个子线程，然后使用 :ref:`memory channel <channels>` 在线程和 Trio 任务之间发送消息：

   .. literalinclude:: reference-core/from-thread-example.py

   .. note::

      ``from_thread.run*`` 函数重用调用 :func:`trio.to_thread.run_sync` 来运行你提供的函数的主任务，只要你使用默认的 ``abandon_on_cancel=False``，这样 Trio 就可以确保任务会继续存在并执行工作。如果你一开始传递了 ``abandon_on_cancel=True``，或者在回调 Trio 时提供了 :class:`~trio.lowlevel.TrioToken`，那么你的函数将在一个新的系统任务中执行。因此， :func:`~trio.lowlevel.current_task`、:func:`current_effective_deadline` 或其他特定于任务树的值可能会根据关键字参数的值而有所不同。

   你还可以使用 :func:`trio.from_thread.check_cancelled` 来检查由 :func:`trio.to_thread.run_sync` 启动的线程是否已被取消。如果调用 :func:`~trio.to_thread.run_sync` 被取消， :func:`~trio.from_thread.check_cancelled` 将引发 :func:`trio.Cancelled` 。它类似于 ``trio.from_thread.run(trio.sleep, 0)``，但更快。

   .. autofunction:: trio.from_thread.check_cancelled
      

.. tab:: 英文

   .. autofunction:: trio.from_thread.run
      :no-index:

   .. autofunction:: trio.from_thread.run_sync
      :no-index:

   This will probably be clearer with an example. Here we demonstrate how
   to spawn a child thread, and then use a :ref:`memory channel
   <channels>` to send messages between the thread and a Trio task:

   .. literalinclude:: reference-core/from-thread-example.py

   .. note::

      The ``from_thread.run*`` functions reuse the host task that called
      :func:`trio.to_thread.run_sync` to run your provided function, as long as you're
      using the default ``abandon_on_cancel=False`` so Trio can be sure that the task will remain
      around to perform the work. If you pass ``abandon_on_cancel=True`` at the outset, or if
      you provide a :class:`~trio.lowlevel.TrioToken` when calling back in to Trio, your
      functions will be executed in a new system task. Therefore, the
      :func:`~trio.lowlevel.current_task`, :func:`current_effective_deadline`, or other
      task-tree specific values may differ depending on keyword argument values.

   You can also use :func:`trio.from_thread.check_cancelled` to check for cancellation from
   a thread that was spawned by :func:`trio.to_thread.run_sync`. If the call to
   :func:`~trio.to_thread.run_sync` was cancelled, then
   :func:`~trio.from_thread.check_cancelled` will raise :func:`trio.Cancelled`.
   It's like ``trio.from_thread.run(trio.sleep, 0)``, but much faster.

   .. autofunction:: trio.from_thread.check_cancelled
      :no-index:

线程和任务本地存储
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Threads and task-local storage**

.. tab:: 中文

   在使用线程时，你可以使用我们之前讨论的相同的 :mod:`contextvars`，因为它们的值会被保留。

   这是通过在使用以下任何一种方式时自动复制 :mod:`contextvars` 上下文来实现的：

   * :func:`trio.to_thread.run_sync`
   * :func:`trio.from_thread.run`
   * :func:`trio.from_thread.run_sync`

   这意味着即使在工作线程中，或者从这些工作线程中的主/父 Trio 线程使用 :func:`trio.from_thread.run` 发送一个要运行的函数时，上下文变量的值仍然可以访问。

   但这也意味着，由于上下文并不是相同的，而是一个副本，如果你在这些函数（在线程中工作的函数）内部 :py:func:`~contextvars.ContextVar.set` 上下文变量的值，新的值只会在该上下文（被复制的上下文）中可用。因此，新的值将对该函数以及其他内部/子任务可用，但在父线程中将无法使用该值。

   如果你需要修改会保存在上下文变量中的值，并且需要从子线程中进行这些修改，你可以改为在顶层/父 Trio 线程的上下文变量中设置一个可变对象（例如字典）。然后，在子线程中，你可以 :py:func:`~contextvars.ContextVar.get` 相同的对象，并修改其值。这样，你保持相同的对象在上下文变量中，并只在子线程中对其进行变更。

   通过这种方式，你可以在子线程中修改对象内容，并仍然能够在父线程中访问新的内容。

   以下是一个示例：

   .. literalinclude:: reference-core/thread-contextvars-example.py

   运行该脚本会输出：

   .. code-block:: none

      Processed user 2 with message Hello 2 in a thread worker
      Processed user 0 with message Hello 0 in a thread worker
      Processed user 1 with message Hello 1 in a thread worker
      New contextvar value from worker thread for user 2: Hello 2
      New contextvar value from worker thread for user 1: Hello 1
      New contextvar value from worker thread for user 0: Hello 0

   如果你使用 :mod:`contextvars` 或者你正在使用一个使用它们的库，现在你知道它们在 Trio 中使用线程时是如何交互的。

   但要记住，在许多情况下， *不* 在自己的代码中使用上下文变量，而是通过参数传递值，可能会更简单，因为它可能更明确，且更容易推理。

   .. note::

      上下文会自动被复制，而不是使用相同的父上下文，因为单个上下文不能在多个线程中使用， :mod:`contextvars` 不支持这种做法。

.. tab:: 英文

   When working with threads, you can use the same :mod:`contextvars` we discussed above,
   because their values are preserved.

   This is done by automatically copying the :mod:`contextvars` context when you use any of:

   * :func:`trio.to_thread.run_sync`
   * :func:`trio.from_thread.run`
   * :func:`trio.from_thread.run_sync`

   That means that the values of the context variables are accessible even in worker
   threads, or when sending a function to be run in the main/parent Trio thread using
   `trio.from_thread.run` *from* one of these worker threads.

   But it also means that as the context is not the same but a copy, if you :py:func:`~contextvars.ContextVar.set` the
   context variable value *inside* one of these functions that work in threads, the
   new value will only be available in that context (that was copied). So, the new value
   will be available for that function and other internal/children tasks, but the value
   won't be available in the parent thread.

   If you need to modify values that would live in the context variables and you need to
   make those modifications from the child threads, you can instead set a mutable object
   (e.g. a dictionary) in the context variable of the top level/parent Trio thread.
   Then in the children, instead of setting the context variable, you can :py:func:`~contextvars.ContextVar.get` the same
   object, and modify its values. That way you keep the same object in the context
   variable and only mutate it in child threads.

   This way, you can modify the object content in child threads and still access the
   new content in the parent thread.

   Here's an example:

   .. literalinclude:: reference-core/thread-contextvars-example.py

   Running that script will result in the output:

   .. code-block:: none

      Processed user 2 with message Hello 2 in a thread worker
      Processed user 0 with message Hello 0 in a thread worker
      Processed user 1 with message Hello 1 in a thread worker
      New contextvar value from worker thread for user 2: Hello 2
      New contextvar value from worker thread for user 1: Hello 1
      New contextvar value from worker thread for user 0: Hello 0

   If you are using :mod:`contextvars` or you are using a library that uses them, now you
   know how they interact when working with threads in Trio.

   But have in mind that in many cases it might be a lot simpler to *not* use context
   variables in your own code and instead pass values in arguments, as it might be more
   explicit and might be easier to reason about.

   .. note::

      The context is automatically copied instead of using the same parent context because
      a single context can't be used in more than one thread, it's not supported by
      :mod:`contextvars`.