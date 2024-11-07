.. module:: trio
   
.. _cancellation:

取消和超时
-------------------------

**Cancellation and timeouts**

.. tab:: 中文

   Trio 具有丰富的可组合系统，用于明确取消工作或在超时到期时取消工作。

.. tab:: 英文

   Trio has a rich, composable system for cancelling work, either explicitly or when a timeout expires.


一个简单的超时示例
~~~~~~~~~~~~~~~~~~~~~~~~

**A simple timeout example**

.. tab:: 中文

   在最简单的情况下，您可以对一段代码块应用超时：

   .. code-block:: python

      with trio.move_on_after(30):
         result = await do_http_get("https://...")
         print("result is", result)
      print("with block finished")

   我们将 :func:`move_on_after` 称为创建一个“取消作用域”，它包含所有在 ``with`` 语句块内运行的代码。如果 HTTP 请求花费超过 30 秒，那么它将被取消：我们将中止请求，并且我们 *不会* 在控制台看到 ``result is ...`` 被打印；相反，我们将直接打印 ``with block finished`` 消息。

   .. note::

      请注意，这个超时是整个 ``with`` 语句体的一个 30 秒超时。这与您在其他 Python 库中可能看到的不同，在那些库中超时通常指的是 `更复杂的机制
      <https://requests.kennethreitz.org/en/master/user/quickstart/#timeouts>`__。我们认为这种方式更容易推理。

   这是如何工作的？这里没有魔法: Trio 是基于普通的 Python 功能构建的，因此我们不能仅仅放弃 ``with`` 语句块内的代码。相反，我们利用 Python 标准的方式来中止一大段复杂的代码：我们抛出一个异常。

   这里的想法是：每当您调用一个可取消的函数，比如 ``await trio.sleep(...)`` 或 ``await sock.recv(...)`` – 参见 :ref:`checkpoints` – 那么该函数首先会检查是否存在一个超时已过期或已被取消的包围作用域。如果有，那么该函数就会立即失败并抛出一个 :exc:`Cancelled` 异常。在这个例子中，这很可能发生在 ``do_http_get`` 的内部深处。然后，异常像正常异常一样传播出去（如果需要，您甚至可以捕获它，但通常这是不推荐的），直到它到达 ``with move_on_after(...):`` 处。此时， :exc:`Cancelled` 异常已经完成了它的工作——它成功地撤销了整个取消的作用域——所以 :func:`move_on_after` 捕获了它，并且在 ``with`` 块之后，执行将照常继续。即使您有嵌套的取消作用域，这一切也会正确工作，因为每个 :exc:`Cancelled` 对象都携带一个隐形标记，确保触发它的取消作用域是唯一会捕获它的作用域。

.. tab:: 英文

   In the simplest case, you can apply a timeout to a block of code:

   .. code-block:: python

      with trio.move_on_after(30):
         result = await do_http_get("https://...")
         print("result is", result)
      print("with block finished")

   We refer to :func:`move_on_after` as creating a "cancel scope", which
   contains all the code that runs inside the ``with`` block. If the HTTP
   request takes more than 30 seconds to run, then it will be cancelled:
   we'll abort the request and we *won't* see ``result is ...`` printed
   on the console; instead we'll go straight to printing the ``with block
   finished`` message.

   .. note::

      Note that this is a single 30 second timeout for the entire body of
      the ``with`` statement. This is different from what you might have
      seen with other Python libraries, where timeouts often refer to
      something `more complicated
      <https://requests.kennethreitz.org/en/master/user/quickstart/#timeouts>`__. We
      think this way is easier to reason about.

   How does this work? There's no magic here: Trio is built using
   ordinary Python functionality, so we can't just abandon the code
   inside the ``with`` block. Instead, we take advantage of Python's
   standard way of aborting a large and complex piece of code: we raise
   an exception.

   Here's the idea: whenever you call a cancellable function like ``await
   trio.sleep(...)`` or ``await sock.recv(...)`` – see :ref:`checkpoints`
   – then the first thing that function does is to check if there's a
   surrounding cancel scope whose timeout has expired, or otherwise been
   cancelled. If so, then instead of performing the requested operation,
   the function fails immediately with a :exc:`Cancelled` exception. In
   this example, this probably happens somewhere deep inside the bowels
   of ``do_http_get``. The exception then propagates out like any normal
   exception (you could even catch it if you wanted, but that's generally
   a bad idea), until it reaches the ``with move_on_after(...):``. And at
   this point, the :exc:`Cancelled` exception has done its job – it's
   successfully unwound the whole cancelled scope – so
   :func:`move_on_after` catches it, and execution continues as normal
   after the ``with`` block. And this all works correctly even if you
   have nested cancel scopes, because every :exc:`Cancelled` object
   carries an invisible marker that makes sure that the cancel scope that
   triggered it is the only one that will catch it.


处理取消
~~~~~~~~~~~~~~~~~~~~~

**Handling cancellation**

.. tab:: 中文

   几乎所有使用 Trio 编写的代码都需要有一些策略来处理 :exc:`Cancelled` 异常——即使您没有设置超时，您的调用者也可能会设置（并且很可能会）。

   您可以捕获 :exc:`Cancelled` 异常，但不应该捕获！更确切地说，如果您捕获了它，您应该进行一些清理工作，然后重新抛出它，或者让它继续传播（除非您遇到错误，在这种情况下，允许错误传播是可以的）。为了提醒您这一点， :exc:`Cancelled` 继承自 :exc:`BaseException`，就像 :exc:`KeyboardInterrupt` 和 :exc:`SystemExit` 一样，因此它不会被通用的 ``except Exception:`` 块捕获。

   在任何长时间运行的代码中，确保定期检查取消是非常重要的，因为否则超时将无法工作！每次调用可取消操作时，这都会隐式发生；有关详细信息，请参见 :ref:`below <cancellable-primitives>`。如果您有一个必须在没有任何 I/O 的情况下进行大量工作的任务，那么您可以使用 ``await sleep(0)`` 来插入一个显式的取消+调度点。

   这里有一个设计良好的 Trio 风格（“trionic”？）API 的经验法则：如果您正在编写一个可重用的函数，那么不应该接受 ``timeout=`` 参数，而是让您的调用者来处理它。这有几个优点。首先，它让调用者有更多选择来决定他们如何处理超时——例如，他们可能会觉得使用绝对截止时间比使用相对超时更容易。如果他们是调用取消机制的人，那么由他们来决定，您就不需要担心这个问题。其次，且更为重要的是，这使得其他人更容易重用您的代码。如果您编写了一个 ``http_get`` 函数，然后我稍后编写了一个 ``log_in_to_twitter`` 函数，需要在内部进行多个 ``http_get`` 调用，我不想还得去弄清楚如何为每个调用配置单独的超时——而使用 Trio 的超时系统，这完全不需要。

   当然，这条规则不适用于需要强制执行内部超时的 API。例如，如果您编写了一个 ``start_http_server`` 函数，那么您可能应该给调用者提供一种配置单个请求超时的方式。

.. tab:: 英文

   Pretty much any code you write using Trio needs to have some strategy
   to handle :exc:`Cancelled` exceptions – even if you didn't set a
   timeout, then your caller might (and probably will).

   You can catch :exc:`Cancelled`, but you shouldn't! Or more precisely,
   if you do catch it, then you should do some cleanup and then re-raise
   it or otherwise let it continue propagating (unless you encounter an
   error, in which case it's OK to let that propagate instead). To help
   remind you of this fact, :exc:`Cancelled` inherits from
   :exc:`BaseException`, like :exc:`KeyboardInterrupt` and
   :exc:`SystemExit` do, so that it won't be caught by catch-all ``except
   Exception:`` blocks.

   It's also important in any long-running code to make sure that you
   regularly check for cancellation, because otherwise timeouts won't
   work! This happens implicitly every time you call a cancellable
   operation; see :ref:`below <cancellable-primitives>` for details. If
   you have a task that has to do a lot of work without any I/O, then you
   can use ``await sleep(0)`` to insert an explicit cancel+schedule
   point.

   Here's a rule of thumb for designing good Trio-style ("trionic"?)
   APIs: if you're writing a reusable function, then you shouldn't take a
   ``timeout=`` parameter, and instead let your caller worry about
   it. This has several advantages. First, it leaves the caller's options
   open for deciding how they prefer to handle timeouts – for example,
   they might find it easier to work with absolute deadlines instead of
   relative timeouts. If they're the ones calling into the cancellation
   machinery, then they get to pick, and you don't have to worry about
   it. Second, and more importantly, this makes it easier for others to
   reuse your code. If you write a ``http_get`` function, and then I come
   along later and write a ``log_in_to_twitter`` function that needs to
   internally make several ``http_get`` calls, I don't want to have to
   figure out how to configure the individual timeouts on each of those
   calls – and with Trio's timeout system, it's totally unnecessary.

   Of course, this rule doesn't apply to APIs that need to impose
   internal timeouts. For example, if you write a ``start_http_server``
   function, then you probably should give your caller some way to
   configure timeouts on individual requests.


取消语义
~~~~~~~~~~~~~~~~~~~~~~

**Cancellation semantics**

.. tab:: 中文

   您可以自由嵌套取消块，每个 :exc:`Cancelled` 异常“知道”它属于哪个块。只要您不停止它，异常将继续传播，直到它到达引发它的块，在那时它会自动停止。

   这是一个例子：

   .. code-block:: python

      print("starting...")
      with trio.move_on_after(5):
         with trio.move_on_after(10):
            await trio.sleep(20)
            print("sleep finished without error")
         print("move_on_after(10) finished without error")
      print("move_on_after(5) finished without error")

   在这段代码中，外部作用域将在 5 秒后过期，导致 :func:`sleep` 调用提前返回并引发 :exc:`Cancelled` 异常。然后，这个异常将通过 ``with move_on_after(10)`` 行传播，直到它被 ``with move_on_after(5)`` 上下文管理器捕获。所以这段代码将打印：

   .. code-block:: none

      starting...
      move_on_after(5) finished without error

   最终结果是 Trio 成功地取消了正在取消作用域内的工作。

   看到这一点，您可能会想知道如何判断内部块是否超时——也许您想做一些不同的事情，例如尝试备用程序或向调用者报告失败。为了简化这一过程， :func:`move_on_after` 的 ``__enter__`` 函数返回一个表示此取消作用域的对象，我们可以用它来检查该作用域是否捕获了 :exc:`Cancelled` 异常：

   .. code-block:: python

      with trio.move_on_after(5) as cancel_scope:
         await trio.sleep(10)
      print(cancel_scope.cancelled_caught)  # prints "True"

   ``cancel_scope`` 对象还允许您检查或调整该作用域的截止时间，显式触发取消而不等待截止时间，检查该作用域是否已被取消，等等——有关详细信息，请参见 :class:`CancelScope` 下文。

   .. _blocking-cleanup-example:

   Trio 中的取消是“级别触发的”，这意味着一旦一个块被取消，*所有* 可取消的操作都将继续引发 :exc:`Cancelled` 异常。这有助于避免一些与资源清理相关的问题。例如，假设我们有一个函数，它连接到远程服务器并发送一些消息，然后在退出时进行清理：

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
         conn = make_connection()
         try:
            await conn.send_hello_msg()
         finally:
            await conn.send_goodbye_msg()

   现在假设远程服务器停止响应，因此我们对 ``await conn.send_hello_msg()`` 的调用永远挂起。幸运的是，我们足够聪明，在这段代码周围加了一个超时，因此最终超时会过期，``send_hello_msg`` 会引发 :exc:`Cancelled` 异常。但是在 ``finally`` 块中，我们又进行了一次阻塞操作，这也会永远挂起！此时，如果我们使用的是 :mod:`asyncio` 或其他具有“边缘触发”取消的库，我们会遇到问题：由于我们的超时已经触发，它不会再触发，应用程序会永远锁死。但在 Trio 中，这不会发生：``await conn.send_goodbye_msg()`` 调用仍然在已取消的块内，因此它也会引发 :exc:`Cancelled`。

   当然，如果您确实想在清理处理程序中进行另一个阻塞调用，Trio 允许您这么做；它是想防止您不小心自讨苦吃。故意自讨苦吃没问题（或者至少——这不是 Trio 的问题）。为了做到这一点，创建一个新的作用域，并将其 :attr:`~CancelScope.shield` 属性设置为 :data:`True`：

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
         conn = make_connection()
         try:
            await conn.send_hello_msg()
         finally:
            with trio.move_on_after(CLEANUP_TIMEOUT, shield=True) as cleanup_scope:
                  await conn.send_goodbye_msg()

   只要您在一个 ``shield = True`` 设置的作用域内，您就会受到外部取消的保护。但请注意，这*仅*适用于*外部*取消：如果 ``CLEANUP_TIMEOUT`` 过期，那么 ``await conn.send_goodbye_msg()`` 仍然会被取消，并且如果 ``await conn.send_goodbye_msg()`` 调用内部使用了任何超时，它们也将继续正常工作。这是一个相当高级的功能，大多数人可能不会使用，但在您需要时它已经准备好了。

.. tab:: 英文

   You can freely nest cancellation blocks, and each :exc:`Cancelled`
   exception "knows" which block it belongs to. So long as you don't stop
   it, the exception will keep propagating until it reaches the block
   that raised it, at which point it will stop automatically.

   Here's an example:

   .. code-block:: python

      print("starting...")
      with trio.move_on_after(5):
         with trio.move_on_after(10):
            await trio.sleep(20)
            print("sleep finished without error")
         print("move_on_after(10) finished without error")
      print("move_on_after(5) finished without error")

   In this code, the outer scope will expire after 5 seconds, causing the
   :func:`sleep` call to return early with a :exc:`Cancelled`
   exception. Then this exception will propagate through the ``with
   move_on_after(10)`` line until it's caught by the ``with
   move_on_after(5)`` context manager. So this code will print:

   .. code-block:: none

      starting...
      move_on_after(5) finished without error

   The end result is that Trio has successfully cancelled exactly the
   work that was happening within the scope that was cancelled.

   Looking at this, you might wonder how you can tell whether the inner
   block timed out – perhaps you want to do something different, like try
   a fallback procedure or report a failure to our caller. To make this
   easier, :func:`move_on_after`\´s ``__enter__`` function returns an
   object representing this cancel scope, which we can use to check
   whether this scope caught a :exc:`Cancelled` exception:

   .. code-block:: python

      with trio.move_on_after(5) as cancel_scope:
         await trio.sleep(10)
      print(cancel_scope.cancelled_caught)  # prints "True"

   The ``cancel_scope`` object also allows you to check or adjust this
   scope's deadline, explicitly trigger a cancellation without waiting
   for the deadline, check if the scope has already been cancelled, and
   so forth – see :class:`CancelScope` below for the full details.

   .. _blocking-cleanup-example:

   Cancellations in Trio are "level triggered", meaning that once a block
   has been cancelled, *all* cancellable operations in that block will
   keep raising :exc:`Cancelled`. This helps avoid some pitfalls around
   resource clean-up. For example, imagine that we have a function that
   connects to a remote server and sends some messages, and then cleans
   up on the way out:

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
         conn = make_connection()
         try:
            await conn.send_hello_msg()
         finally:
            await conn.send_goodbye_msg()

   Now suppose that the remote server stops responding, so our call to
   ``await conn.send_hello_msg()`` hangs forever. Fortunately, we were
   clever enough to put a timeout around this code, so eventually the
   timeout will expire and ``send_hello_msg`` will raise
   :exc:`Cancelled`. But then, in the ``finally`` block, we make another
   blocking operation, which will also hang forever! At this point, if we
   were using :mod:`asyncio` or another library with "edge-triggered"
   cancellation, we'd be in trouble: since our timeout already fired, it
   wouldn't fire again, and at this point our application would lock up
   forever. But in Trio, this *doesn't* happen: the ``await
   conn.send_goodbye_msg()`` call is still inside the cancelled block, so
   it will also raise :exc:`Cancelled`.

   Of course, if you really want to make another blocking call in your
   cleanup handler, Trio will let you; it's trying to prevent you from
   accidentally shooting yourself in the foot. Intentional foot-shooting
   is no problem (or at least – it's not Trio's problem). To do this,
   create a new scope, and set its :attr:`~CancelScope.shield`
   attribute to :data:`True`:

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
         conn = make_connection()
         try:
            await conn.send_hello_msg()
         finally:
            with trio.move_on_after(CLEANUP_TIMEOUT, shield=True) as cleanup_scope:
                  await conn.send_goodbye_msg()

   So long as you're inside a scope with ``shield = True`` set, then
   you'll be protected from outside cancellations. Note though that this
   *only* applies to *outside* cancellations: if ``CLEANUP_TIMEOUT``
   expires then ``await conn.send_goodbye_msg()`` will still be
   cancelled, and if ``await conn.send_goodbye_msg()`` call uses any
   timeouts internally, then those will continue to work normally as
   well. This is a pretty advanced feature that most people probably
   won't use, but it's there for the rare cases where you need it.


.. _cancellable-primitives:

取消和原始操作
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cancellation and primitive operations**

.. tab:: 中文

   我们已经讨论了操作被取消时会发生什么，以及在调用可取消操作时需要做好准备……但我们还没有深入讨论哪些操作是可取消的，以及它们在被取消时的具体行为。

   规则是这样的：如果它位于 ``trio`` 命名空间中，并且你使用 ``await`` 来调用它，那么它是可取消的（请参见上面的 :ref:`checkpoints`）。可取消的意思是：

   * 如果你在取消的作用域内尝试调用它，它将引发 :exc:`Cancelled`。

   * 如果它阻塞，并且在阻塞时，周围的某个作用域变为取消状态，它将提前返回并引发 :exc:`Cancelled`。

   * 引发 :exc:`Cancelled` 意味着操作*没有发生*。例如，如果 Trio 套接字的 ``send`` 方法引发 :exc:`Cancelled`，则没有数据被发送。如果 Trio 套接字的 ``recv`` 方法引发 :exc:`Cancelled`，则没有数据丢失——它仍然保留在套接字接收缓冲区中，等待你再次调用 ``recv``。等等。

   有一些特殊情况，由于外部约束，无法完全实现这些语义。这些情况总是会被记录下来。还有一个系统性的例外：

   * 异步清理操作——如 ``__aexit__`` 方法或异步关闭方法——和其他操作一样是可取消的，*但*如果它们被取消，它们仍然会在引发 :exc:`Cancelled` 之前执行最低级别的清理。

   例如，关闭 TLS 包装的套接字通常涉及向远程对等方发送通知，以便它们可以通过加密方式确保你确实打算关闭套接字，而不是中间人攻击者破坏了你的连接。但要健壮地处理这一过程有点棘手。还记得我们上面提到的 :ref:`示例 <blocking-cleanup-example>` 吗？其中阻塞的 ``send_goodbye_msg`` 引发了问题？这正是关闭 TLS 套接字的工作方式：如果远程对等方消失了，那么我们的代码可能永远无法实际发送关闭通知，而如果它一直尝试发送，那就会永远阻塞。因此，关闭 TLS 包装的套接字的方法会*尝试*发送该通知——如果它被取消，那么它会放弃发送消息，但*仍然*会在引发 :exc:`Cancelled` 之前关闭底层套接字，这样至少不会泄漏资源。

.. tab:: 英文

   We've talked a lot about what happens when an operation is cancelled,
   and how you need to be prepared for this whenever calling a
   cancellable operation... but we haven't gone into the details about
   which operations are cancellable, and how exactly they behave when
   they're cancelled.

   Here's the rule: if it's in the ``trio`` namespace, and you use ``await``
   to call it, then it's cancellable (see :ref:`checkpoints`
   above). Cancellable means:

   * If you try to call it when inside a cancelled scope, then it will
   raise :exc:`Cancelled`.

   * If it blocks, and while it's blocked then one of the scopes around
   it becomes cancelled, it will return early and raise
   :exc:`Cancelled`.

   * Raising :exc:`Cancelled` means that the operation *did not
   happen*. If a Trio socket's ``send`` method raises :exc:`Cancelled`,
   then no data was sent. If a Trio socket's ``recv`` method raises
   :exc:`Cancelled` then no data was lost – it's still sitting in the
   socket receive buffer waiting for you to call ``recv`` again. And so
   forth.

   There are a few idiosyncratic cases where external constraints make it
   impossible to fully implement these semantics. These are always
   documented. There is also one systematic exception:

   * Async cleanup operations – like ``__aexit__`` methods or async close
   methods – are cancellable just like anything else *except* that if
   they are cancelled, they still perform a minimum level of cleanup
   before raising :exc:`Cancelled`.

   For example, closing a TLS-wrapped socket normally involves sending a
   notification to the remote peer, so that they can be cryptographically
   assured that you really meant to close the socket, and your connection
   wasn't just broken by a man-in-the-middle attacker. But handling this
   robustly is a bit tricky. Remember our :ref:`example
   <blocking-cleanup-example>` above where the blocking
   ``send_goodbye_msg`` caused problems? That's exactly how closing a TLS
   socket works: if the remote peer has disappeared, then our code may
   never be able to actually send our shutdown notification, and it would
   be nice if it didn't block forever trying. Therefore, the method for
   closing a TLS-wrapped socket will *try* to send that notification –
   and if it gets cancelled, then it will give up on sending the message,
   but *will* still close the underlying socket before raising
   :exc:`Cancelled`, so at least you don't leak that resource.


取消 API 详细信息
~~~~~~~~~~~~~~~~~~~~~~~~

**Cancellation API details**

.. tab:: 中文

   :func:`move_on_after` 以及 Trio 提供的所有其他取消机制，最终是通过 :class:`CancelScope` 对象来实现的。

   .. autoclass:: trio.CancelScope

      .. autoattribute:: deadline

      .. autoattribute:: relative_deadline

      .. autoattribute:: shield

      .. automethod:: is_relative()

      .. automethod:: cancel()

      .. attribute:: cancelled_caught

         只读 :class:`bool`。记录此作用域是否捕获了 :exc:`~trio.Cancelled` 异常。需要满足两个条件：（1） ``with`` 块以 :exc:`~trio.Cancelled` 异常退出，且（2）此作用域是触发该 :exc:`~trio.Cancelled` 异常的责任作用域。

      .. autoattribute:: cancel_called

   通常不需要创建 :class:`CancelScope` 对象。Trio 已经在与任务相关的 :class:`Nursery` 对象中包含了 :attr:`~trio.Nursery.cancel_scope` 属性。我们将在后续手册中讨论育儿任务（nurseries）。

   Trio 还提供了几个便利函数，用于常见的仅对某段代码施加超时的场景：

   .. autofunction:: trio.move_on_after
      :with: cancel_scope

   .. autofunction:: trio.move_on_at
      :with: cancel_scope

   .. autofunction:: trio.fail_after
      :with: cancel_scope

   .. autofunction:: trio.fail_at
      :with: cancel_scope

.. tab:: 英文

   :func:`move_on_after` and all the other cancellation facilities provided
   by Trio are ultimately implemented in terms of :class:`CancelScope`
   objects.

   .. autoclass:: trio.CancelScope
      :no-index:

      .. autoattribute:: deadline
         :no-index:

      .. autoattribute:: relative_deadline
         :no-index:

      .. autoattribute:: shield
         :no-index:

      .. automethod:: is_relative()
         :no-index:

      .. automethod:: cancel()
         :no-index:

      .. attribute:: cancelled_caught
         :no-index:

         Readonly :class:`bool`. Records whether this scope caught a
         :exc:`~trio.Cancelled` exception. This requires two things: (1)
         the ``with`` block exited with a :exc:`~trio.Cancelled`
         exception, and (2) this scope is the one that was responsible
         for triggering this :exc:`~trio.Cancelled` exception.

      .. autoattribute:: cancel_called
         :no-index:

   Often there is no need to create :class:`CancelScope` object. Trio
   already includes :attr:`~trio.Nursery.cancel_scope` attribute in a
   task-related :class:`Nursery` object. We will cover nurseries later in
   the manual.

   Trio also provides several convenience functions for the common
   situation of just wanting to impose a timeout on some code:

   .. autofunction:: trio.move_on_after
      :with: cancel_scope
      :no-index:

   .. autofunction:: trio.move_on_at
      :with: cancel_scope
      :no-index:

   .. autofunction:: trio.fail_after
      :with: cancel_scope
      :no-index:

   .. autofunction:: trio.fail_at
      :with: cancel_scope
      :no-index:

备忘单
^^^^^^^^^

**Cheat sheet**

.. tab:: 中文

   * 如果你想对一个函数施加超时，但不关心是否超时：

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
            await do_whatever()
      # 继续执行！

   * 如果你想对一个函数施加超时，并在超时后进行一些恢复操作：

   .. code-block:: python

      with trio.move_on_after(TIMEOUT) as cancel_scope:
            await do_whatever()
      if cancel_scope.cancelled_caught:
            # 操作超时，尝试其他方法
            try_to_recover()

   * 如果你想对一个函数施加超时，并且如果超时，则直接放弃并抛出错误，由调用者处理：

   .. code-block:: python

      with trio.fail_after(TIMEOUT):
            await do_whatever()

   也可以检查当前的有效截止时间，这有时非常有用：

   .. autofunction:: trio.current_effective_deadline

.. tab:: 英文

   * If you want to impose a timeout on a function, but you don't care
   whether it timed out or not:

   .. code-block:: python

      with trio.move_on_after(TIMEOUT):
            await do_whatever()
      # carry on!

   * If you want to impose a timeout on a function, and then do some
   recovery if it timed out:

   .. code-block:: python

      with trio.move_on_after(TIMEOUT) as cancel_scope:
            await do_whatever()
      if cancel_scope.cancelled_caught:
            # The operation timed out, try something else
            try_to_recover()

   * If you want to impose a timeout on a function, and then if it times
   out then just give up and raise an error for your caller to deal
   with:

   .. code-block:: python

      with trio.fail_after(TIMEOUT):
            await do_whatever()

   It's also possible to check what the current effective deadline is,
   which is sometimes useful:

   .. autofunction:: trio.current_effective_deadline
      :no-index:
