教程
========

**Tutorial**

.. The Trio tutorial

   the spiel about what a concurrent library is

   Traditionally Python is a synchronous language, and we assume
   you're familiar with that kind of programming, but don't assume any
   knowledge of concurrent programming. (And even if you are familiar
   with concurrent programming using another library like Twisted or
   asyncio, or another language like Go or Erlang, then you should
   still probably read this, because Trio is different.)

   Trio turns Python into a concurrent language. It takes the core
   async/await syntax introduced in 3.5, and uses it to add two
   new pieces of semantics:

   - cancel scopes: a generic system for managing timeouts and
     cancellation
   - nurseries: which let your program do multiple things at the same
     time

   Of course it also provides a complete suite of APIs for doing
   networking, file I/O, using worker threads,

   We'll go through and explain each of these

   simple cancellation
   applied to an HTTP request
     with fail_after(5):
         response = await asks.get("https://httpbin.org/delay/1")
         print(response)
   and then again with /delay/10

   value of async/await: show you where the cancellation exceptions
   can happen -- see pillar re: explicit cancel points

   (also briefly discuss cancel scopes and cancel() + the query APIs,
   fail_after vs move_on_after, current_time() and
   current_effective_deadline())

   simple multi-task concurrency
   applied to do multiple HTTP requests
   adding a per-request timeout
   adding a timeout on the whole thing -- demonstrating wrapping
       cancel around a nursery

   pillars: implicit concurrency and exception raising
   and explicit schedule points

   example: the scheduling trace

   implicit concurrency -> use echo example to introduce networking
   API, and show how to do explicit concurrency
   and demonstrate start()
   then point out that you can just use serve_tcp()

   example: catch-all logging in our echo server

   review of the three (or four) core language extensions
   and how they fit together and

.. currentmodule:: trio

.. tab:: 中文

   欢迎来到 Trio 教程！Trio 是一个现代 Python 库，用于编写异步应用程序——也就是说，用于编写那些需要通过并行化 I/O 来同时完成多项任务的程序，比如一个并行抓取大量页面的网络爬虫，或是一个处理多个下载请求的 Web 服务器……诸如此类的任务。在这里，我们将尝试以温和的方式介绍使用 Trio 的异步编程。

   我们假设您对 Python 已有一定了解，但别担心——我们不假设您对异步编程或 Python 的新特性 ``async/await`` 有任何基础。

   另外，与许多 ``async/await`` 教程不同，我们假设您的目标是*使用* Trio 编写有趣的程序，因此我们不会深入探讨 Python 解释器内部如何实现 ``async/await`` 的细节。“协程”这个词也不会出现。事实上，除非您想要*实现*一个像 Trio 这样的库，否则您实际上并不*需要*了解这些内容（不过，我们会提供一些链接，供想深入学习的读者参考）。

   好了，准备好了吗？我们开始吧。

.. tab:: 英文

   Welcome to the Trio tutorial! Trio is a modern Python library for
   writing asynchronous applications – that is, programs that want to do
   multiple things at the same time with parallelized I/O, like a web
   spider that fetches lots of pages in parallel, a web server juggling
   lots of simultaneous downloads... that sort of thing. Here we'll try
   to give a gentle introduction to asynchronous programming with Trio.

   We assume that you're familiar with Python in general, but don't worry
   – we don't assume you know anything about asynchronous programming or
   Python's new ``async/await`` feature.

   Also, unlike many ``async/await`` tutorials, we assume that your goal
   is to *use* Trio to write interesting programs, so we won't go into
   the nitty-gritty details of how ``async/await`` is implemented inside
   the Python interpreter. The word "coroutine" is never mentioned. The
   fact is, you really don't *need* to know any of that stuff unless you
   want to *implement* a library like Trio, so we leave it out (though
   we'll throw in a few links for those who want to dig deeper).

   Okay, ready? Let's get started.


开始之前
----------------

**Before you begin**

.. tab:: 中文

   1. 确保您使用的是 Python 3.9 或更高版本。

   2. ``python3 -m pip install --upgrade trio``（在 Windows 上可能需要
      ``py -3 -m pip install --upgrade trio`` – `详情请见 <https://packaging.python.org/installing/>`__）

   3. 能否运行 ``import trio``？如果可以，那您就可以开始了！

.. tab:: 英文

   4. Make sure you're using Python 3.9 or newer.

   5. ``python3 -m pip install --upgrade trio`` (or on Windows, maybe
      ``py -3 -m pip install --upgrade trio`` – `details
      <https://packaging.python.org/installing/>`__)

   6. Can you ``import trio``? If so then you're good to go!

如果您迷失或感到困惑……
------------------------------

**If you get lost or confused...**

.. tab:: 中文

   ……那么我们希望知道！我们有一个友好的 `聊天频道 <https://gitter.im/python-trio/general>`__，您可以在 StackOverflow 上使用 `"python-trio" 标签提问 <https://stackoverflow.com/questions/ask?tags=python+python-trio>`__，或者直接 `提交一个问题 <https://github.com/python-trio/trio/issues/new>`__ （如果我们的文档令人困惑，这是我们的责任，我们希望能修正它！）。


.. tab:: 英文

   ...then we want to know! We have a friendly `chat channel
   <https://gitter.im/python-trio/general>`__, you can ask questions
   `using the "python-trio" tag on StackOverflow
   <https://stackoverflow.com/questions/ask?tags=python+python-trio>`__, or just
   `file a bug <https://github.com/python-trio/trio/issues/new>`__ (if
   our documentation is confusing, that's our fault, and we want to fix
   it!).

异步函数
---------------

**Async functions**

.. tab:: 中文

   Python 3.5 添加了一个重要的新特性：异步函数。使用 Trio 的核心就是编写异步函数，因此让我们从这里开始。

   异步函数的定义与普通函数相似，只是将 ``def`` 替换为 ``async def``：

   .. code-block:: python

      # 普通函数
      def regular_double(x):
         return 2 * x

      # 异步函数
      async def async_double(x):
         return 2 * x

   “Async” 是 “asynchronous”（异步）的缩写；有时我们将像 ``regular_double`` 这样的普通函数称为“同步函数”，以将其与异步函数区分开来。

   从用户的角度来看，异步函数与普通函数之间有两个区别：

   1. 要调用异步函数，必须使用 ``await`` 关键字。因此，您需要写成 ``await async_double(3)`` 而不是 ``regular_double(3)``。

   2. 您不能在普通函数的主体内使用 ``await`` 关键字。如果尝试这样做，将会出现语法错误：

      .. code-block:: python

         def print_double(x):
            print(await async_double(x))   # <-- 这里会出现 SyntaxError

      但是在异步函数内部，``await`` 是允许的：

      .. code-block:: python

         async def print_double(x):
            print(await async_double(x))   # <-- 没问题！

   现在，让我们思考一下其中的影响：如果调用异步函数需要 ``await``，并且只有异步函数可以使用 ``await`` …… 这里有一个小表格：

   =======================  ==================================  ===================
   如果一个函数是这样          想要调用一个这样的函数               是否可以实现？
   =======================  ==================================  ===================
   sync                     sync                                ✓
   sync                     async                               **NOPE**
   async                    sync                                ✓
   async                    async                               ✓
   =======================  ==================================  ===================

   总结一下：对用户来说，异步函数相较于普通函数的唯一优势在于异步函数拥有一个特权：它们可以调用其他异步函数。

   这会立刻引发两个问题：怎么实现？以及为什么要实现？具体来说：

   当 Python 程序启动时，它是在运行普通的同步代码。这就引发了一个先有鸡还是先有蛋的问题：一旦我们运行了一个异步函数，我们就可以调用其他异步函数，但是 *如何* 调用第一个异步函数呢？

   而且，如果编写异步函数的唯一原因是它可以调用其他异步函数，那么 *为什么* 我们一开始会想使用它们？这看上去作为一个特权有些没有意义。难道不更简单直接地……完全不用任何异步函数吗？

   这就是像 Trio 这样的异步库的作用所在。它提供了两件东西：

   3. 一个运行器函数，这是一个特殊的 *同步* 函数，可以接收并调用一个 *异步* 函数。在 Trio 中，这个函数是 ``trio.run``:

      .. code-block:: python

         import trio

         async def async_double(x):
            return 2 * x

         trio.run(async_double, 3)  # 返回 6

      这就解答了“如何实现”的问题。

   4. 一组有用的异步函数——特别是用于执行 I/O 的函数。这就解答了“为什么要实现”的问题：这些函数是异步的，并且很有用，所以如果您想使用它们，就必须编写异步代码。如果您觉得跟踪这些 ``async`` 和 ``await`` 很麻烦，那也无能为力——这是必然的！（好吧，您可以选择不使用 Trio。这是一个合理的选项。但事实证明，这些 ``async/await`` 其实是有好处的，我们稍后会讨论。）

      这里是一个使用 :func:`trio.sleep` 的示例函数。(:func:`trio.sleep` 类似于 :func:`time.sleep`，但具有更多的异步特性。）

      .. code-block:: python

         import trio

         async def double_sleep(x):
            await trio.sleep(2 * x)

         trio.run(double_sleep, 3)  # 无操作持续 6 秒后返回

   .. _async-sandwich:

   所以，实际上我们这个 ``async_double`` 函数是一个不太好的示例。意思是，它可以运行，没有什么 *问题* ，但它其实是多余的：完全可以写成普通函数，这样反而会更实用。而 ``double_sleep`` 则更为典型：我们必须将其设为异步函数，因为它调用了另一个异步函数。最终结果形成了一种异步三明治结构，两边是 Trio 中的代码，中间是我们的代码：

   .. code-block:: none

      trio.run -> double_sleep -> trio.sleep

   这种“三明治”结构是异步代码的典型模式；一般来说，结构如下：

   .. code-block:: none

      trio.run -> [异步函数] -> ... -> [异步函数] -> trio.whatever

   正是位于 :func:`trio.run` 和 ``trio.whatever`` 之间路径上的这些函数需要是异步的。Trio 提供了异步的“面包”，然后您的代码就成为了这个异步三明治中的“美味异步夹心”。其他函数（例如，您在过程中调用的辅助函数）通常应该是常规的非异步函数。

.. tab:: 英文

   Python 3.5 added a major new feature: async functions. Using Trio is
   all about writing async functions, so let's start there.

   An async function is defined like a normal function, except you write
   ``async def`` instead of ``def``:

   .. code-block:: python

      # A regular function
      def regular_double(x):
         return 2 * x

      # An async function
      async def async_double(x):
         return 2 * x

   "Async" is short for "asynchronous"; we'll sometimes refer to regular
   functions like ``regular_double`` as "synchronous functions", to
   distinguish them from async functions.

   From a user's point of view, there are two differences between an
   async function and a regular function:

   5. To call an async function, you have to use the ``await``
      keyword. So instead of writing ``regular_double(3)``, you write
      ``await async_double(3)``.

   6. You can't use the ``await`` keyword inside the body of a regular
      function. If you try it, you'll get a syntax error:

      .. code-block:: python

         def print_double(x):
            print(await async_double(x))   # <-- SyntaxError here

      But inside an async function, ``await`` is allowed:

      .. code-block:: python

         async def print_double(x):
            print(await async_double(x))   # <-- OK!

   Now, let's think about the consequences here: if you need ``await`` to
   call an async function, and only async functions can use
   ``await``... here's a little table:

   =======================  ==================================  ===================
   If a function like this  wants to call a function like this  is it gonna happen?
   =======================  ==================================  ===================
   sync                     sync                                ✓
   sync                     async                               **NOPE**
   async                    sync                                ✓
   async                    async                               ✓
   =======================  ==================================  ===================

   So in summary: As a user, the entire advantage of async functions over
   regular functions is that async functions have a superpower: they can
   call other async functions.

   This immediately raises two questions: how, and why? Specifically:

   When your Python program starts up, it's running regular old sync
   code. So there's a chicken-and-the-egg problem: once we're running an
   async function we can call other async functions, but *how* do we call
   that first async function?

   And, if the only reason to write an async function is that it can call
   other async functions, *why* on earth would we ever use them in
   the first place? I mean, as superpowers go this seems a bit
   pointless. Wouldn't it be simpler to just... not use any async
   functions at all?

   This is where an async library like Trio comes in. It provides two
   things:

   7. A runner function, which is a special *synchronous* function that
      takes and calls an *asynchronous* function. In Trio, this is
      ``trio.run``:

      .. code-block:: python

         import trio

         async def async_double(x):
            return 2 * x

         trio.run(async_double, 3)  # returns 6

      So that answers the "how" part.

   8. A bunch of useful async functions – in particular, functions for
      doing I/O. So that answers the "why": these functions are async,
      and they're useful, so if you want to use them, you have to write
      async code. If you think keeping track of these ``async`` and
      ``await`` things is annoying, then too bad – you've got no choice
      in the matter! (Well, OK, you could just not use Trio. That's a
      legitimate option. But it turns out that the ``async/await`` stuff
      is actually a good thing, for reasons we'll discuss a little bit
      later.)

      Here's an example function that uses
      :func:`trio.sleep`. (:func:`trio.sleep` is like :func:`time.sleep`,
      but with more async.)

      .. code-block:: python

         import trio

         async def double_sleep(x):
            await trio.sleep(2 * x)

         trio.run(double_sleep, 3)  # does nothing for 6 seconds then returns

   So it turns out our ``async_double`` function is actually a bad
   example. I mean, it works, it's fine, there's nothing *wrong* with it,
   but it's pointless: it could just as easily be written as a regular
   function, and it would be more useful that way. ``double_sleep`` is a
   much more typical example: we have to make it async, because it calls
   another async function. The end result is a kind of async sandwich,
   with Trio on both sides and our code in the middle:

   .. code-block:: none

      trio.run -> double_sleep -> trio.sleep

   This "sandwich" structure is typical for async code; in general, it
   looks like:

   .. code-block:: none

      trio.run -> [async function] -> ... -> [async function] -> trio.whatever

   It's exactly the functions on the path between :func:`trio.run` and
   ``trio.whatever`` that have to be async. Trio provides the async
   bread, and then your code makes up the async sandwich's tasty async
   filling. Other functions (e.g., helpers you call along the way) should
   generally be regular, non-async functions.


警告：不要忘记 ``await`` ！
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Warning: don't forget that** ``await`` ! 

.. tab:: 中文

   现在是个好时机，可以打开 Python 提示符，尝试编写简单的异步函数，并使用 ``trio.run`` 运行它们。

   在这个过程中，您可能会编写类似以下的代码，尝试调用一个异步函数，却遗漏了 ``await`` ：

   .. code-block:: python

      import time
      import trio

      async def broken_double_sleep(x):
         print("*打哈欠* 准备入睡")
         start_time = time.perf_counter()

         # 哎呀，我们忘了加 'await'！
         trio.sleep(2 * x)

         sleep_time = time.perf_counter() - start_time
         print(f"醒来后感觉精神抖擞！一共睡了 {sleep_time:.2f} 秒。")

      trio.run(broken_double_sleep, 3)

   您可能认为 Python 会在这里引发错误，就像我们有时调用函数时犯下的其他错误一样。例如，如果我们忘记给 :func:`trio.sleep` 提供所需的参数，那么我们会收到一个友好的 :exc:`TypeError`，提示我们。但是不幸的是，如果忘记 ``await``，并不会出现这样的错误。您实际得到的结果是：

   .. code-block:: pycon

      >>> trio.run(broken_double_sleep, 3)
      *打哈欠* 准备入睡
      醒来后感觉精神抖擞！一共睡了 0.00 秒。
      __main__:4: RuntimeWarning: coroutine 'sleep' was never awaited
      >>>

   显然这段代码是有问题的——0.00 秒根本不够让人休息好！但是代码看起来却像是成功执行了——没有引发任何异常。唯一的提示是它打印出 ``RuntimeWarning: coroutine 'sleep' was never awaited`` 。另外，警告的确切显示位置可能会有所不同，因为这取决于垃圾收集器的运行方式。如果您使用的是 PyPy，可能在下一次垃圾回收运行之前根本不会看到警告：

   .. code-block:: pycon

      # 在 PyPy 中：
      >>> trio.run(broken_double_sleep, 3)
      *打哈欠* 准备入睡
      醒来后感觉精神抖擞！一共睡了 0.00 秒！
      >>> # 什么……？？？没有任何警告！

      >>> # 强制执行一次垃圾回收后则会看到警告：
      >>> import gc
      >>> gc.collect()
      /home/njs/pypy-3.8-nightly/lib-python/3/importlib/_bootstrap.py:191: RuntimeWarning: coroutine 'sleep' was never awaited
      if _module_locks.get(name) is wr:    # XXX PyPy 修复？
      0

   （如果您看不到上面的警告，可以尝试向右滚动查看。）

   遗漏 ``await`` 是 *极为常见的错误*。每个人都会犯这个错误。而 Python 并不会像您希望的那样提供足够的帮助 😞。关键点在于：如果您看到 ``RuntimeWarning: coroutine '...' was never awaited`` 这句魔法般的提示，那么这 *总是* 意味着您遗漏了某处的 ``await``，应忽略其他错误信息，先修复这个问题，因为很可能其他问题只是由此引发的附带损害。我甚至不确定 PyPy 输出的那些其他信息到底是什么。但幸运的是，我不需要知道这些细节，只需要修复我的函数！

   （“我以为你说过不会提到协程！” 是的，但是 *我* 没有提到协程，是 Python 提到的。这个问题可以去找 Guido！不过说正经的，这确实是内部实现细节泄露的一个地方。）

   为什么会出现这种情况？在 Trio 中，每次我们使用 ``await``，都是在调用一个异步函数，而每次调用异步函数都需要使用 ``await``。但 Python 希望保留一些灵活性，以适应其他 *稍微* 不那么有组织的库。因此，虽然我们可以将 ``await trio.sleep(...)`` 看作一个完整的语法单元，但在 Python 看来它是两部分：首先是一个函数调用，返回一个奇怪的“协程”对象：

   .. code-block:: pycon

      >>> trio.sleep(3)
      <coroutine object sleep at 0x7f5ac77be6d0>

   然后这个对象会被传递给 ``await``，实际执行该函数。所以如果您忘记了 ``await``，会发生两件坏事：函数实际上没有被调用，您得到的“协程”对象可能并不是您期望的结果，比如数字：

   .. code-block:: pycon

      >>> async_double(3) + 1
      TypeError: unsupported operand type(s) for +: 'coroutine' and 'int'

   如果您还没有自然地犯下这个错误，可以故意尝试一下：写一些缺少 ``await`` 或多余 ``await`` 的代码，看看会发生什么。这样，当真正遇到这种情况时，您就做好了准备。

   记住：小心 ``RuntimeWarning: coroutine '...' was never awaited``；它意味着您需要找到并修复遗漏的 ``await``。

.. tab:: 英文

   Now would be a good time to open up a Python prompt and experiment a
   little with writing simple async functions and running them with
   ``trio.run``.

   At some point in this process, you'll probably write some code like
   this, that tries to call an async function but leaves out the
   ``await``:

   .. code-block:: python

      import time
      import trio

      async def broken_double_sleep(x):
         print("*yawn* Going to sleep")
         start_time = time.perf_counter()

         # Whoops, we forgot the 'await'!
         trio.sleep(2 * x)

         sleep_time = time.perf_counter() - start_time
         print(f"Woke up after {sleep_time:.2f} seconds, feeling well rested!")

      trio.run(broken_double_sleep, 3)

   You might think that Python would raise an error here, like it does
   for other kinds of mistakes we sometimes make when calling a
   function. Like, if we forgot to pass :func:`trio.sleep` its required
   argument, then we would get a nice :exc:`TypeError` saying so. But
   unfortunately, if you forget an ``await``, you don't get that. What
   you actually get is:

   .. code-block:: pycon

      >>> trio.run(broken_double_sleep, 3)
      *yawn* Going to sleep
      Woke up after 0.00 seconds, feeling well rested!
      __main__:4: RuntimeWarning: coroutine 'sleep' was never awaited
      >>>

   This is clearly broken – 0.00 seconds is not long enough to feel well
   rested! Yet the code acts like it succeeded – no exception was
   raised. The only clue that something went wrong is that it prints
   ``RuntimeWarning: coroutine 'sleep' was never awaited``. Also, the
   exact place where the warning is printed might vary, because it
   depends on the whims of the garbage collector. If you're using PyPy,
   you might not even get a warning at all until the next GC collection
   runs:

   .. code-block:: pycon

      # On PyPy:
      >>> trio.run(broken_double_sleep, 3)
      *yawn* Going to sleep
      Woke up after 0.00 seconds, feeling well rested!
      >>> # what the ... ?? not even a warning!

      >>> # but forcing a garbage collection gives us a warning:
      >>> import gc
      >>> gc.collect()
      /home/njs/pypy-3.8-nightly/lib-python/3/importlib/_bootstrap.py:191: RuntimeWarning: coroutine 'sleep' was never awaited
      if _module_locks.get(name) is wr:    # XXX PyPy fix?
      0

   (If you can't see the warning above, try scrolling right.)

   Forgetting an ``await`` like this is an *incredibly common
   mistake*. You will mess this up. Everyone does. And Python will not
   help you as much as you'd hope 😞. The key thing to remember is: if
   you see the magic words ``RuntimeWarning: coroutine '...' was never
   awaited``, then this *always* means that you made the mistake of
   leaving out an ``await`` somewhere, and you should ignore all the
   other error messages you see and go fix that first, because there's a
   good chance the other stuff is just collateral damage. I'm not even
   sure what all that other junk in the PyPy output is. Fortunately I
   don't need to know, I just need to fix my function!

   ("I thought you said you weren't going to mention coroutines!" Yes,
   well, *I* didn't mention coroutines, Python did. Take it up with
   Guido! But seriously, this is unfortunately a place where the internal
   implementation details do leak out a bit.)

   Why does this happen? In Trio, every time we use ``await`` it's to
   call an async function, and every time we call an async function we
   use ``await``. But Python's trying to keep its options open for other
   libraries that are *ahem* a little less organized about things. So
   while for our purposes we can think of ``await trio.sleep(...)`` as a
   single piece of syntax, Python thinks of it as two things: first a
   function call that returns this weird "coroutine" object:

   .. code-block:: pycon

      >>> trio.sleep(3)
      <coroutine object sleep at 0x7f5ac77be6d0>

   and then that object gets passed to ``await``, which actually runs the
   function. So if you forget ``await``, then two bad things happen: your
   function doesn't actually get called, and you get a "coroutine" object
   where you might have been expecting something else, like a number:

   .. code-block:: pycon

      >>> async_double(3) + 1
      TypeError: unsupported operand type(s) for +: 'coroutine' and 'int'

   If you didn't already mess this up naturally, then give it a try on
   purpose: try writing some code with a missing ``await``, or an extra
   ``await``, and see what you get. This way you'll be prepared for when
   it happens to you for real.

   And remember: watch out for ``RuntimeWarning: coroutine '...' was
   never awaited``; it means you need to find and fix your missing
   ``await``.


好的，让我们看一些很酷的东西
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Okay, let's see something cool already**

.. _tutorial-example-tasks-intro:

.. tab:: 中文

   现在我们开始使用 Trio 了，但到目前为止我们所做的只是编写打印内容和等待不同时间长度的函数。这固然有趣，但我们也可以用 :func:`time.sleep` 来实现这些功能。 ``async/await`` 看起来似乎没什么用！

   当然，事实并非如此。Trio 还有一个隐藏的技巧，它使得异步函数比普通函数更强大：它可以*同时*运行多个异步函数。以下是一个示例：

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:

   这里有很多内容，所以我们将逐步解释。首先，我们定义了两个异步函数 ``child1`` 和 ``child2``。这些内容您应该在上一节中看到过：

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:
      :lineno-match:
      :start-at: async def child1
      :end-at: child2: exiting

   接下来，我们定义了 ``parent`` 作为一个异步函数，它将同时调用 ``child1`` 和 ``child2``：

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:
      :lineno-match:
      :start-at: async def parent
      :end-at: all done!

   实现这一点的方法是使用一个神秘的 ``async with`` 语句来创建一个“nursery”，然后将 ``child1`` 和 ``child2`` 启动在该 nursery 中。

   让我们先从 ``async with`` 说起。其实这非常简单。在普通的 Python 中，类似 ``with someobj: ...`` 的语句会指示解释器在代码块的开始调用 ``someobj.__enter__()``，在代码块的结束时调用 ``someobj.__exit__()``。我们称 ``someobj`` 为“上下文管理器”。而 ``async with`` 做的完全相同，只不过普通的 ``with`` 语句调用的是普通方法，而 ``async with`` 语句则调用异步方法：在代码块的开始，它会执行 ``await someobj.__aenter__()``，在代码块的结束则会执行 ``await someobj.__aexit__()``。在这种情况下，我们称 ``someobj`` 为“异步上下文管理器”。简单来说：``with`` 语句只是调用一些函数的简写，由于 Python 引入了 async/await 使得有了两种不同的函数，因此也需要两种不同的 ``with`` 语句。就是这么简单！如果您理解异步函数，那么您也就理解了 ``async with``。

   .. note::

      虽然这个例子中没有使用到，但我们还是顺便提一下 async/await 新增的另一个语法：``async for``。这与 ``async with`` 和 ``with`` 的对比类似：一个 ``async for`` 循环和普通的 ``for`` 循环几乎一样，区别在于普通的 ``for`` 循环通过 ``iterator.__next__()`` 来获取下一个项，而 ``async for`` 循环则通过 ``await async_iterator.__anext__()`` 来获取。现在您已经了解了所有关于 async/await 的内容了。记住，这基本就是在创建 sandwich（嵌套结构）时在所有内容前面加上 "async"，您会发现这样就能轻松驾驭它。

   既然我们了解了 ``async with``，让我们再回到 ``parent`` 的实现：

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:
      :lineno-match:
      :start-at: async def parent
      :end-at: all done!

   这里只有 4 行代码是实际操作的。第 20 行中，我们使用 :func:`trio.open_nursery` 获取一个“nursery”对象，然后在 ``async with`` 代码块中分别在第 22 行和第 25 行调用 ``nursery.start_soon``。调用异步函数其实有两种方式：一种是我们之前见到的 ``await async_fn()``，新的方式是 ``nursery.start_soon(async_fn)``：它请求 Trio 启动该异步函数，*但会立即返回而不等待函数完成*。因此，在两次调用 ``nursery.start_soon`` 之后，``child1`` 和 ``child2`` 已经在后台运行了。然后在第 28 行（带注释的那一行），我们到了 ``async with`` 代码块的末尾，触发 nursery 的 ``__aexit__`` 方法。这会强制 ``parent`` 在此停下，并等待 nursery 中所有的子任务结束。这就是为什么使用 ``async with`` 来获取 nursery 的原因：它确保子任务不会自行运行而被遗弃。这样做的一个重要原因是，如果子任务中有一个出现了错误或其他问题并引发异常，那么该异常可以被传递到父任务中；而在许多其他框架中，这样的异常通常会被忽略。Trio 永远不会忽略异常。

   好了！让我们运行一下，看看会得到什么输出：

   .. code-block:: none

      parent: started!
      parent: spawning child1...
      parent: spawning child2...
      parent: waiting for children to finish...
      child2: started! sleeping now...
      child1: started! sleeping now...
         [... 1 秒后 ...]
      child1: exiting!
      child2: exiting!
      parent: all done!

   （您的输出中“started”和/或“exiting”行的顺序可能会有所不同。）

   请注意，``child1`` 和 ``child2`` 都几乎同时启动并一起退出。而且，尽管我们调用了两次 ``trio.sleep(1)``，程序却在总共一秒内完成了。所以看起来 ``child1`` 和 ``child2`` 真的是同时运行的！

   如果您对线程编程比较熟悉，这可能会让您感到熟悉——这是有意的。但需要注意的是 *这里没有任何线程* 。所有这些操作都在一个线程中完成。为提醒我们这一点，我们使用了不同的术语：我们不是生成两个“线程”，而是生成两个“任务”。任务和线程之间有两个不同点：(1) 单个线程可以轮流运行多个任务；(2) 在线程中，Python 解释器/操作系统可以随意切换正在运行的线程，而在任务中，我们只能在某些特定的地方（我们称之为 :ref:`"checkpoints" <checkpoints>`）切换任务。在下一节中，我们将深入探讨这意味着什么。

.. tab:: 英文

   So now we've started using Trio, but so far all we've learned to do is
   write functions that print things and sleep for various lengths of
   time. Interesting enough, but we could just as easily have done that
   with :func:`time.sleep`. ``async/await`` is useless!

   Well, not really. Trio has one more trick up its sleeve, that makes
   async functions more powerful than regular functions: it can run
   multiple async functions *at the same time*. Here's an example:

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:

   There's a lot going on in here, so we'll take it one step at a
   time. In the first part, we define two async functions ``child1`` and
   ``child2``. These should look familiar from the last section:

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:
      :lineno-match:
      :start-at: async def child1
      :end-at: child2: exiting

   Next, we define ``parent`` as an async function that's going to call
   ``child1`` and ``child2`` concurrently:

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:
      :lineno-match:
      :start-at: async def parent
      :end-at: all done!

   It does this by using a mysterious ``async with`` statement to create
   a "nursery", and then "spawns" ``child1`` and ``child2`` into the
   nursery.

   Let's start with this ``async with`` thing. It's actually pretty
   simple. In regular Python, a statement like ``with someobj: ...``
   instructs the interpreter to call ``someobj.__enter__()`` at the
   beginning of the block, and to call ``someobj.__exit__()`` at the end
   of the block. We call ``someobj`` a "context manager". An ``async
   with`` does exactly the same thing, except that where a regular
   ``with`` statement calls regular methods, an ``async with`` statement
   calls async methods: at the start of the block it does ``await
   someobj.__aenter__()`` and at that end of the block it does ``await
   someobj.__aexit__()``. In this case we call ``someobj`` an "async
   context manager". So in short: ``with`` blocks are a shorthand for
   calling some functions, and since with async/await Python now has two
   kinds of functions, it also needs two kinds of ``with`` blocks. That's
   all there is to it! If you understand async functions, then you
   understand ``async with``.

   .. note::

      This example doesn't use them, but while we're here we might as
      well mention the one other piece of new syntax that async/await
      added: ``async for``. It's basically the same idea as ``async
      with`` versus ``with``: An ``async for`` loop is just like a
      ``for`` loop, except that where a ``for`` loop does
      ``iterator.__next__()`` to fetch the next item, an ``async for``
      does ``await async_iterator.__anext__()``. Now you understand all
      of async/await. Basically just remember that it involves making
      sandwiches and sticking the word "async" in front of everything,
      and you'll do fine.

   Now that we understand ``async with``, let's look at ``parent`` again:

   .. literalinclude:: tutorial/tasks-intro.py
      :linenos:
      :lineno-match:
      :start-at: async def parent
      :end-at: all done!

   There are only 4 lines of code that really do anything here. On line
   20, we use :func:`trio.open_nursery` to get a "nursery" object, and
   then inside the ``async with`` block we call ``nursery.start_soon`` twice,
   on lines 22 and 25. There are actually two ways to call an async
   function: the first one is the one we already saw, using ``await
   async_fn()``; the new one is ``nursery.start_soon(async_fn)``: it asks Trio
   to start running this async function, *but then returns immediately
   without waiting for the function to finish*. So after our two calls to
   ``nursery.start_soon``, ``child1`` and ``child2`` are now running in the
   background. And then at line 28, the commented line, we hit the end of
   the ``async with`` block, and the nursery's ``__aexit__`` function
   runs. What this does is force ``parent`` to stop here and wait for all
   the children in the nursery to exit. This is why you have to use
   ``async with`` to get a nursery: it gives us a way to make sure that
   the child calls can't run away and get lost. One reason this is
   important is that if there's a bug or other problem in one of the
   children, and it raises an exception, then it lets us propagate that
   exception into the parent; in many other frameworks, exceptions like
   this are just discarded. Trio never discards exceptions.

   Ok! Let's try running it and see what we get:

   .. code-block:: none

      parent: started!
      parent: spawning child1...
      parent: spawning child2...
      parent: waiting for children to finish...
      child2: started! sleeping now...
      child1: started! sleeping now...
         [... 1 second passes ...]
      child1: exiting!
      child2: exiting!
      parent: all done!

   (Your output might have the order of the "started" and/or "exiting"
   lines swapped compared to mine.)

   Notice that ``child1`` and ``child2`` both start together and then
   both exit together. And, even though we made two calls to
   ``trio.sleep(1)``, the program finished in just one second total.
   So it looks like ``child1`` and ``child2`` really are running at the
   same time!

   Now, if you're familiar with programming using threads, this might
   look familiar – and that's intentional. But it's important to realize
   that *there are no threads here*. All of this is happening in a single
   thread. To remind ourselves of this, we use slightly different
   terminology: instead of spawning two "threads", we say that we spawned
   two "tasks". There are two differences between tasks and threads: (1)
   many tasks can take turns running on a single thread, and (2) with
   threads, the Python interpreter/operating system can switch which
   thread is running whenever they feel like it; with tasks, we can only
   switch at certain designated places we call :ref:`"checkpoints"
   <checkpoints>`. In the next section, we'll dig into what this means.


.. _tutorial-instrument-example:

任务切换说明
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Task switching illustrated**

.. tab:: 中文

   基于 async/await 的库（如 Trio）背后的核心思想是通过在适当的地方切换任务，使得在单线程上同时运行多个任务——例如，如果我们在实现一个 Web 服务器，那么一个任务可以在另一个任务等待新连接时发送 HTTP 响应。如果您只想使用 Trio，那么您不需要理解这些切换是如何工作的所有细节——但至少对 Trio 在执行代码时“幕后”做了什么有一个大致的直觉是很有用的。为了帮助建立这种直觉，让我们仔细看看 Trio 是如何运行我们上一节中的示例的。

   幸运的是，Trio 提供了一套 :ref:`丰富的工具集用于检查和调试程序 <instrumentation>`。在这里，我们想要观察 :func:`trio.run` 的工作过程，可以通过编写一个名为 ``Tracer`` 的类来实现，它实现了 Trio 的 :class:`~trio.abc.Instrument` 接口。它的任务是记录各种事件的发生：

   .. literalinclude:: tutorial/tasks-with-trace.py
      :pyobject: Tracer

   然后我们重新运行上一节中的示例程序，但这次我们将一个 ``Tracer`` 对象传递给 :func:`trio.run`：

   .. literalinclude:: tutorial/tasks-with-trace.py
      :start-at: trio.run

   这将产生 *大量* 的输出，因此我们将逐步进行分析。

   首先，在 Trio 准备好运行代码时，会有一些初步的输出。大部分内容目前对我们来说并不重要，但在其中我们可以看到，Trio 为 ``__main__.parent`` 函数创建了一个任务，并“调度”了它（即，记录了应该尽快运行它）：

   .. code-block:: none

      $ python3 tutorial/tasks-with-trace.py
      !!! run started
      ### new task spawned: <init>
      ### task scheduled: <init>
      ### doing a quick check for I/O
      ### finished I/O check (took 1.1122087016701698e-05 seconds)
      >>> about to run one step of task: <init>
      ### new task spawned: <call soon task>
      ### task scheduled: <call soon task>
      ### new task spawned: __main__.parent
      ### task scheduled: __main__.parent
      <<< task step finished: <init>
      ### doing a quick check for I/O
      ### finished I/O check (took 6.4980704337358475e-06 seconds)

   一旦初步的准备工作完成，Trio 就开始运行 ``parent`` 函数，并且您可以看到 ``parent`` 创建了两个子任务。然后它遇到 ``async with`` 代码块的末尾并暂停：

   .. code-block:: none

      >>> about to run one step of task: __main__.parent
      parent: started!
      parent: spawning child1...
      ### new task spawned: __main__.child1
      ### task scheduled: __main__.child1
      parent: spawning child2...
      ### new task spawned: __main__.child2
      ### task scheduled: __main__.child2
      parent: waiting for children to finish...
      <<< task step finished: __main__.parent

   接下来控制返回给 :func:`trio.run`，它记录了一些内部的额外输出：

   .. code-block:: none

      >>> about to run one step of task: <call soon task>
      <<< task step finished: <call soon task>
      ### doing a quick check for I/O
      ### finished I/O check (took 5.476875230669975e-06 seconds)

   然后给两个子任务一个运行的机会：

   .. code-block:: none

      >>> about to run one step of task: __main__.child2
      child2 started! sleeping now...
      <<< task step finished: __main__.child2

      >>> about to run one step of task: __main__.child1
      child1: started! sleeping now...
      <<< task step finished: __main__.child1

   每个任务运行直到遇到 :func:`trio.sleep` 的调用，然后我们就会回到 :func:`trio.run` 来决定接下来要运行什么。这个过程是如何发生的呢？秘密在于 :func:`trio.run` 和 :func:`trio.sleep` 的协同工作： :func:`trio.sleep` 具有一些特殊的魔法，允许它暂停自己，因此它会发送一个通知给 :func:`trio.run`，请求在 1 秒后再次唤醒它，然后暂停任务。一旦任务被暂停，Python 就会将控制权交回给 :func:`trio.run`，后者决定接下来要做什么。（如果这听起来类似于生成器通过执行 ``yield`` 来暂停执行，那不是巧合：在 Python 解释器内部，生成器和异步函数的实现有很多重叠。）

   .. note::

      您可能会想知道是否可以将不同异步库的原语混合使用。例如，我们能不能将 :func:`trio.run` 和 :func:`asyncio.sleep` 一起使用？答案是否定的，我们不能这样做，上面的一段解释了原因：我们的异步三明治的两侧使用了不同的私有语言来互相通信，而不同的库使用不同的语言。因此，如果您试图在 :func:`trio.run` 中调用 :func:`asyncio.sleep`，Trio 会变得非常混乱，可能会以某种戏剧性的方式崩溃。

   只有异步函数才能访问暂停任务的特殊魔法，因此只有异步函数才能导致程序切换到不同的任务。这意味着，如果一个调用 *没有* 加上 ``await``，那么你就知道它 *不能* 成为任务被暂停的地方。这使得任务比线程更容易推理，因为任务之间可以交替执行并互相干扰状态的方式少得多。（例如，在 Trio 中，像 ``a += 1`` 这样的语句总是原子的——即使 ``a`` 是某个任意复杂的自定义对象！）Trio 还提供了一些 :ref:`额外的保证 <checkpoints>`，但这是其中最重要的一条。

   现在你也知道为什么 ``parent`` 必须使用 ``async with`` 来打开育儿所：如果我们使用常规的 ``with`` 块，它就不能在结束时暂停并等待子任务完成；我们需要清理函数是异步的，这正是 ``async with`` 为我们提供的。

   现在，回到我们的执行点。总结一下：此时 ``parent`` 正在等待 ``child1`` 和 ``child2``, 而这两个子任务都在睡眠。所以 :func:`trio.run` 检查它的记录，发现直到这些睡眠完成之前没有什么可以做的——除非可能发生一些外部的 I/O 事件。如果发生了这种情况，它可能会给我们一些事情去做。当然，我们这里没有进行 I/O 操作，所以不会发生，但在其他情况下是可能的。所以接下来它调用操作系统的原语让整个进程进入睡眠状态：

   .. code-block:: none

      ### waiting for I/O for up to 0.9999009938910604 seconds

   事实上，I/O 并没有到来，所以一秒钟后我们再次醒来，Trio 再次检查它的记录。此时它检查当前时间，将其与 :func:`trio.sleep` 发送的记录进行比较，记录中指出两个子任务应该在何时再次被唤醒，Trio 意识到它们已经睡了足够长的时间，因此它将它们调度尽快运行：

   .. code-block:: none

      ### finished I/O check (took 1.0006483688484877 seconds)
      ### task scheduled: __main__.child1
      ### task scheduled: __main__.child2

   然后，子任务开始运行，这一次它们运行到完成。记得 ``parent`` 正在等待它们完成吗？注意当第一个子任务退出时， ``parent`` 是如何被调度的：

   .. code-block:: none

      >>> about to run one step of task: __main__.child1
      child1: exiting!
      ### task scheduled: __main__.parent
      ### task exited: __main__.child1
      <<< task step finished: __main__.child1

      >>> about to run one step of task: __main__.child2
      child2 exiting!
      ### task exited: __main__.child2
      <<< task step finished: __main__.child2

   然后，在再次检查 I/O 后， ``parent`` 醒来。育儿所清理代码注意到它的所有子任务都已退出，并允许育儿所块完成。接着， ``parent`` 打印最终结果并退出：

   .. code-block:: none

      ### doing a quick check for I/O
      ### finished I/O check (took 9.045004844665527e-06 seconds)

      >>> about to run one step of task: __main__.parent
      parent: all done!
      ### task scheduled: <init>
      ### task exited: __main__.parent
      <<< task step finished: __main__.parent

   最后，经过一些内部的账务处理，:func:`trio.run` 也退出了：

   .. code-block:: none

      ### doing a quick check for I/O
      ### finished I/O check (took 5.996786057949066e-06 seconds)
      >>> about to run one step of task: <init>
      ### task scheduled: <call soon task>
      ### task scheduled: <init>
      <<< task step finished: <init>
      ### doing a quick check for I/O
      ### finished I/O check (took 6.258022040128708e-06 seconds)
      >>> about to run one step of task: <call soon task>
      ### task exited: <call soon task>
      <<< task step finished: <call soon task>
      >>> about to run one step of task: <init>
      ### task exited: <init>
      <<< task step finished: <init>
      !!! run finished

   你完成了！

   这段文本有点长，但再次强调，你不需要理解所有内容就能使用 Trio——事实上，Trio 竭尽全力使每个任务看起来像是以简单、线性的方式执行的。（就像你的操作系统竭尽全力让你感觉单线程的代码是以简单线性的方式执行的，尽管在背后操作系统像 Trio 一样在不同的线程和进程之间进行切换。）但了解你编写的代码是如何实际执行的，以及最重要的——它对并行性的影响——是有帮助的。

   另外，如果这段内容激起了你进一步了解 ``async/await`` 内部工作原理的兴趣，那么 `这篇博客文章 <https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/>`__ 是一个很好的深入探讨，或者可以查看 `这个很棒的教程 <https://github.com/AndreLouisCaron/a-tale-of-event-loops>`__，了解如何从零开始构建一个简单的异步 I/O 框架。

.. tab:: 英文

   The big idea behind async/await-based libraries like Trio is to run
   lots of tasks simultaneously on a single thread by switching between
   them at appropriate places – so for example, if we're implementing a
   web server, then one task could be sending an HTTP response at the
   same time as another task is waiting for new connections. If all you
   want to do is use Trio, then you don't need to understand all the
   nitty-gritty detail of how this switching works – but it's very useful
   to have at least a general intuition about what Trio is doing "under
   the hood" when your code is executing. To help build that intuition,
   let's look more closely at how Trio ran our example from the last
   section.

   Fortunately, Trio provides a :ref:`rich set of tools for inspecting
   and debugging your programs <instrumentation>`. Here we want to watch
   :func:`trio.run` at work, which we can do by writing a class we'll
   call ``Tracer``, which implements Trio's :class:`~trio.abc.Instrument`
   interface. Its job is to log various events as they happen:

   .. literalinclude:: tutorial/tasks-with-trace.py
      :pyobject: Tracer

   Then we re-run our example program from the previous section, but this
   time we pass :func:`trio.run` a ``Tracer`` object:

   .. literalinclude:: tutorial/tasks-with-trace.py
      :start-at: trio.run

   This generates a *lot* of output, so we'll go through it one step at a
   time.

   First, there's a bit of chatter while Trio gets ready to run our
   code. Most of this is irrelevant to us for now, but in the middle you
   can see that Trio has created a task for the ``__main__.parent``
   function, and "scheduled" it (i.e., made a note that it should be run
   soon):

   .. code-block:: none

      $ python3 tutorial/tasks-with-trace.py
      !!! run started
      ### new task spawned: <init>
      ### task scheduled: <init>
      ### doing a quick check for I/O
      ### finished I/O check (took 1.1122087016701698e-05 seconds)
      >>> about to run one step of task: <init>
      ### new task spawned: <call soon task>
      ### task scheduled: <call soon task>
      ### new task spawned: __main__.parent
      ### task scheduled: __main__.parent
      <<< task step finished: <init>
      ### doing a quick check for I/O
      ### finished I/O check (took 6.4980704337358475e-06 seconds)

   Once the initial housekeeping is done, Trio starts running the
   ``parent`` function, and you can see ``parent`` creating the two child
   tasks. Then it hits the end of the ``async with`` block, and pauses:

   .. code-block:: none

      >>> about to run one step of task: __main__.parent
      parent: started!
      parent: spawning child1...
      ### new task spawned: __main__.child1
      ### task scheduled: __main__.child1
      parent: spawning child2...
      ### new task spawned: __main__.child2
      ### task scheduled: __main__.child2
      parent: waiting for children to finish...
      <<< task step finished: __main__.parent

   Control then goes back to :func:`trio.run`, which logs a bit more
   internal chatter:

   .. code-block:: none

      >>> about to run one step of task: <call soon task>
      <<< task step finished: <call soon task>
      ### doing a quick check for I/O
      ### finished I/O check (took 5.476875230669975e-06 seconds)

   And then gives the two child tasks a chance to run:

   .. code-block:: none

      >>> about to run one step of task: __main__.child2
      child2 started! sleeping now...
      <<< task step finished: __main__.child2

      >>> about to run one step of task: __main__.child1
      child1: started! sleeping now...
      <<< task step finished: __main__.child1

   Each task runs until it hits the call to :func:`trio.sleep`, and then
   suddenly we're back in :func:`trio.run` deciding what to run next. How
   does this happen? The secret is that :func:`trio.run` and
   :func:`trio.sleep` work together to make it happen: :func:`trio.sleep`
   has access to some special magic that lets it pause itself,
   so it sends a note to :func:`trio.run` requesting to be
   woken again after 1 second, and then suspends the task. And once the
   task is suspended, Python gives control back to :func:`trio.run`,
   which decides what to do next. (If this sounds similar to the way that
   generators can suspend execution by doing a ``yield``, then that's not
   a coincidence: inside the Python interpreter, there's a lot of overlap
   between the implementation of generators and async functions.)

   .. note::

      You might wonder whether you can mix-and-match primitives from
      different async libraries. For example, could we use
      :func:`trio.run` together with :func:`asyncio.sleep`? The answer is
      no, we can't, and the paragraph above explains why: the two sides
      of our async sandwich have a private language they use to talk to
      each other, and different libraries use different languages. So if
      you try to call :func:`asyncio.sleep` from inside a
      :func:`trio.run`, then Trio will get very confused indeed and
      probably blow up in some dramatic way.

   Only async functions have access to the special magic for suspending a
   task, so only async functions can cause the program to switch to a
   different task. What this means is that if a call *doesn't* have an ``await``
   on it, then you know that it *can't* be a place where your task will
   be suspended. This makes tasks much `easier to reason about
   <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`__ than
   threads, because there are far fewer ways that tasks can be
   interleaved with each other and stomp on each others' state. (For
   example, in Trio a statement like ``a += 1`` is always atomic – even
   if ``a`` is some arbitrarily complicated custom object!) Trio also
   makes some :ref:`further guarantees beyond that <checkpoints>`, but
   that's the big one.

   And now you also know why ``parent`` had to use an ``async with`` to
   open the nursery: if we had used a regular ``with`` block, then it
   wouldn't have been able to pause at the end and wait for the children
   to finish; we need our cleanup function to be async, which is exactly
   what ``async with`` gives us.

   Now, back to our execution point. To recap: at this point ``parent``
   is waiting on ``child1`` and ``child2``, and both children are
   sleeping. So :func:`trio.run` checks its notes, and sees that there's
   nothing to be done until those sleeps finish – unless possibly some
   external I/O event comes in. If that happened, then it might give us
   something to do. Of course we aren't doing any I/O here so it won't
   happen, but in other situations it could. So next it calls an
   operating system primitive to put the whole process to sleep:

   .. code-block:: none

      ### waiting for I/O for up to 0.9999009938910604 seconds

   And in fact no I/O does arrive, so one second later we wake up again,
   and Trio checks its notes again. At this point it checks the current
   time, compares it to the notes that :func:`trio.sleep` sent saying
   when the two child tasks should be woken up again, and realizes
   that they've slept for long enough, so it schedules them to run soon:

   .. code-block:: none

      ### finished I/O check (took 1.0006483688484877 seconds)
      ### task scheduled: __main__.child1
      ### task scheduled: __main__.child2

   And then the children get to run, and this time they run to
   completion. Remember how ``parent`` is waiting for them to finish?
   Notice how ``parent`` gets scheduled when the first child exits:

   .. code-block:: none

      >>> about to run one step of task: __main__.child1
      child1: exiting!
      ### task scheduled: __main__.parent
      ### task exited: __main__.child1
      <<< task step finished: __main__.child1

      >>> about to run one step of task: __main__.child2
      child2 exiting!
      ### task exited: __main__.child2
      <<< task step finished: __main__.child2

   Then, after another check for I/O, ``parent`` wakes up. The nursery
   cleanup code notices that all its children have exited, and lets the
   nursery block finish. And then ``parent`` makes a final print and
   exits:

   .. code-block:: none

      ### doing a quick check for I/O
      ### finished I/O check (took 9.045004844665527e-06 seconds)

      >>> about to run one step of task: __main__.parent
      parent: all done!
      ### task scheduled: <init>
      ### task exited: __main__.parent
      <<< task step finished: __main__.parent

   And finally, after a bit more internal bookkeeping, :func:`trio.run`
   exits too:

   .. code-block:: none

      ### doing a quick check for I/O
      ### finished I/O check (took 5.996786057949066e-06 seconds)
      >>> about to run one step of task: <init>
      ### task scheduled: <call soon task>
      ### task scheduled: <init>
      <<< task step finished: <init>
      ### doing a quick check for I/O
      ### finished I/O check (took 6.258022040128708e-06 seconds)
      >>> about to run one step of task: <call soon task>
      ### task exited: <call soon task>
      <<< task step finished: <call soon task>
      >>> about to run one step of task: <init>
      ### task exited: <init>
      <<< task step finished: <init>
      !!! run finished

   You made it!

   That was a lot of text, but again, you don't need to understand
   everything here to use Trio – in fact, Trio goes to great lengths to
   make each task feel like it executes in a simple, linear way. (Just
   like your operating system goes to great lengths to make it feel like
   your single-threaded code executes in a simple linear way, even though
   under the covers the operating system juggles between different
   threads and processes in essentially the same way Trio does.) But it
   is useful to have a rough model in your head of how the code you write
   is actually executed, and – most importantly – the consequences of
   that for parallelism.

   Alternatively, if this has just whetted your appetite and you want to
   know more about how ``async/await`` works internally, then `this blog
   post
   <https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/>`__
   is a good deep dive, or check out `this great walkthrough
   <https://github.com/AndreLouisCaron/a-tale-of-event-loops>`__ to see
   how to build a simple async I/O framework from the ground up.


更友好、更温和的 GIL
---------------------

**A kinder, gentler GIL**

.. tab:: 中文

   说到并行性——让我们稍微拉远一点，讨论一下 `async/await` 与 Python 中处理并发的其他方式的比较。

   正如我们已经提到的，Trio 任务在概念上与 Python 内建的线程非常相似，这些线程是通过 :mod:`threading` 模块提供的。在所有常见的 Python 实现中，线程有一个著名的限制: 全局解释器锁（Global Interpreter Lock，简称 GIL）。GIL 意味着即使你使用多个线程，你的代码仍然（大多数情况下）会在单核上运行。人们往往会觉得这很让人沮丧。

   但从 Trio 的角度来看，GIL 的问题不是它限制了并行性。当然，如果 Python 有更好的方法来利用多个核心那会很好，但这是一个极其困难的问题，而在此期间，很多时候单核就足够用了——或者如果单核不够用，进程级或机器级的并行性也可以很好地解决问题。

   不，GIL 的问题在于它是一个 *糟糕的交易*：我们放弃了使用多个核心，而得到的却是……几乎所有真正并行编程带来的挑战和令人困惑的 bug，而且——雪上加霜的是，`相当差的可扩展性 <https://twitter.com/hynek/status/771790449057132544>`__。Python 中的线程实在没有什么吸引力。

   Trio 并不会让你的代码在多个核心上运行；实际上，正如我们上面所看到的，Trio 的设计本身就规定了当它有多个任务时，这些任务会轮流执行，因此在任何时刻，只有一个任务在积极运行。我们并不是在克服 GIL，而是在接受它。但是，如果你愿意接受这一点，并且额外花点时间把新的 ``async`` 和 ``await`` 关键字放在正确的位置，那么作为回报，你将获得：

   * 极好的可扩展性：只要它们的总 CPU 需求不超过单个核心的处理能力，Trio 可以同时运行 10,000 个以上的任务，而不感到吃力。（例如，这在网络服务器中很常见，服务器可能有大量的客户端连接，但在任何时刻只有少数几个客户端是活跃的。）

   * 强大的功能：大多数线程系统都是用 C 实现的，并且受限于操作系统提供的功能。在 Trio 中，我们的逻辑完全用 Python 实现，这使得可以实现强大且符合人体工学的功能，例如 :ref:`Trio 的取消系统 <cancellation>`。

   * 更容易推理的代码：``await`` 关键字意味着每个函数中潜在的任务切换点是显式标记的。这使得 Trio 代码比使用线程的等效程序更容易推理，`可以大大简化推理过程 <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`__。

   当然，这并不适用于每个应用程序……但在很多情况下，这里的权衡看起来相当有吸引力。

   然而，有一个缺点需要特别注意。使检查点显式化让你可以更好地控制任务如何交替执行——但强大的控制力带来了巨大的责任。对于线程，运行时环境负责确保每个线程得到公平的运行时间。而在 Trio 中，如果某个任务运行几秒钟而没有执行检查点，那么……你所有的其他任务就得等着了。

   以下是一个如何出错的示例。以我们之前的 :ref:`示例 <tutorial-example-tasks-intro>` 为例，替换掉调用 :func:`trio.sleep` 的地方，改为调用 :func:`time.sleep`。如果我们运行修改后的程序，我们会看到类似这样的输出：

   .. code-block:: none

      parent: started!
      parent: spawning child1...
      parent: spawning child2...
      parent: waiting for children to finish...
      child2 started! sleeping now...
         [... 暂停 1 秒 ...]
      child2 exiting!
      child1: started! sleeping now...
         [... 暂停 1 秒 ...]
      child1: exiting!
      parent: all done!

   Trio 之所以拥有如此丰富的 :ref:`工具 API <tutorial-instrument-example>`，主要是为了使编写调试工具成为可能，帮助捕捉到像这样的潜在问题。

.. tab:: 英文

   Speaking of parallelism – let's zoom out for a moment and talk about
   how async/await compares to other ways of handling concurrency in
   Python.

   As we've already noted, Trio tasks are conceptually rather similar to
   Python's built-in threads, as provided by the :mod:`threading`
   module. And in all common Python implementations, threads have a
   famous limitation: the Global Interpreter Lock, or "GIL" for
   short. The GIL means that even if you use multiple threads, your code
   still (mostly) ends up running on a single core. People tend to find
   this frustrating.

   But from Trio's point of view, the problem with the GIL isn't that it
   restricts parallelism. Of course it would be nice if Python had better
   options for taking advantage of multiple cores, but that's an
   extremely difficult problem to solve, and in the meantime there are
   lots of problems where a single core is totally adequate – or where if
   it isn't, then process-level or machine-level parallelism works fine.

   No, the problem with the GIL is that it's a *lousy deal*: we give up
   on using multiple cores, and in exchange we get... almost all the same
   challenges and mind-bending bugs that come with real parallel
   programming, and – to add insult to injury – `pretty poor scalability
   <https://twitter.com/hynek/status/771790449057132544>`__. Threads in
   Python just aren't that appealing.

   Trio doesn't make your code run on multiple cores; in fact, as we saw
   above, it's baked into Trio's design that when it has multiple tasks,
   they take turns, so at each moment only one of them is actively running.
   We're not so much overcoming the GIL as embracing it. But if you're
   willing to accept that, plus a bit of extra work to put these new
   ``async`` and ``await`` keywords in the right places, then in exchange
   you get:

   * Excellent scalability: Trio can run 10,000+ tasks simultaneously
     without breaking a sweat, so long as their total CPU demands don't
     exceed what a single core can provide. (This is common in, for
     example, network servers that have lots of clients connected, but
     only a few active at any given time.)

   * Fancy features: most threading systems are implemented in C and
     restricted to whatever features the operating system provides. In
     Trio our logic is all in Python, which makes it possible to
     implement powerful and ergonomic features like :ref:`Trio's
     cancellation system <cancellation>`.

   * Code that's easier to reason about: the ``await`` keyword means that
     potential task-switching points are explicitly marked within each
     function. This can make Trio code `dramatically easier to reason
     about <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`__
     than the equivalent program using threads.

   Certainly it's not appropriate for every app... but there are a lot of
   situations where the trade-offs here look pretty appealing.

   There is one downside that's important to keep in mind, though. Making
   checkpoints explicit gives you more control over how your tasks can be
   interleaved – but with great power comes great responsibility. With
   threads, the runtime environment is responsible for making sure that
   each thread gets its fair share of running time. With Trio, if some
   task runs off and does stuff for seconds on end without executing a
   checkpoint, then... all your other tasks will just have to wait.

   Here's an example of how this can go wrong. Take our :ref:`example
   from above <tutorial-example-tasks-intro>`, and replace the calls to
   :func:`trio.sleep` with calls to :func:`time.sleep`. If we run our
   modified program, we'll see something like:

   .. code-block:: none

      parent: started!
      parent: spawning child1...
      parent: spawning child2...
      parent: waiting for children to finish...
      child2 started! sleeping now...
         [... pauses for 1 second ...]
      child2 exiting!
      child1: started! sleeping now...
         [... pauses for 1 second ...]
      child1: exiting!
      parent: all done!

   One of the major reasons why Trio has such a rich
   :ref:`instrumentation API <tutorial-instrument-example>` is to make it
   possible to write debugging tools to catch issues like this.


使用 Trio 进行网络编程
---------------------------

**Networking with Trio**

.. tab:: 中文

   现在让我们利用所学的知识来进行一些 I/O 操作，这正是 `async/await` 真正展现优势的地方。

   传统的用于演示网络 API 的小型应用程序是“回显服务器”：一个程序，它等待来自远程客户端的任意数据，然后将相同的数据原封不动地发送回去。（也许现在一个更相关的例子是一个执行大量并发 HTTP 请求的应用程序，但对于那个你需要一个 `HTTP 库 <https://github.com/python-trio/trio/issues/236#issuecomment-310784001>`__ ，比如 `asks <https://asks.readthedocs.io>`__，所以我们还是沿用回显服务器的传统。）

   在本教程中，我们展示了管道的两端：客户端和服务器。客户端定期向服务器发送数据，并显示其响应。服务器等待连接；当一个客户端连接时，它会将接收到的数据重新发送回管道。

.. tab:: 英文

   Now let's take what we've learned and use it to do some I/O, which is
   where async/await really shines.

   The traditional toy application for demonstrating network APIs is an
   "echo server": a program that awaits arbitrary data from  remote clients,
   and then sends that same data right back. (Probably a more relevant example
   these days would be an application that does lots of concurrent HTTP
   requests, but for that `you need an HTTP library
   <https://github.com/python-trio/trio/issues/236#issuecomment-310784001>`__
   such as `asks <https://asks.readthedocs.io>`__, so we'll stick
   with the echo server tradition.)

   In this tutorial, we present both ends of the pipe: the client, and the
   server. The client periodically sends data to the server, and displays its
   answers. The server awaits connections; when a client connects, it recopies
   the received data back on the pipe.


回显客户端
~~~~~~~~~~~~~~

**An echo client**

.. tab:: 中文

   首先，这是一个回显 *客户端* 的示例，也就是一个将数据发送到我们的回显服务器并接收响应的程序：

   .. _tutorial-echo-client-example:

   .. literalinclude:: tutorial/echo-client.py
      :linenos:

   请注意，这段代码如果没有我们下面实现的 TCP 服务器将无法正常工作。

   这里的整体结构应该是熟悉的，因为它就像我们之前的 :ref:`示例 <tutorial-example-tasks-intro>`：我们有一个父任务，它生成两个子任务来执行实际工作，然后在 ``async with`` 块的末尾，它切换到全职的父任务模式，等待子任务完成。但现在，子任务不仅仅调用 :func:`trio.sleep`，它们使用了 Trio 的一些网络 API。

   我们先来看一下父任务：

   .. literalinclude:: tutorial/echo-client.py
      :linenos:
      :lineno-match:
      :pyobject: parent

   首先，我们调用 :func:`trio.open_tcp_stream` 来与服务器建立 TCP 连接。``127.0.0.1`` 是一个特殊的 `IP 地址 <https://en.wikipedia.org/wiki/IP_address>`__，表示“我正在运行的计算机”，所以这将连接到本地计算机上使用 ``PORT`` 作为其联系点的程序。该函数返回一个实现了 Trio 的 :class:`~trio.abc.Stream` 接口的对象，该接口提供了发送和接收字节的方法，以及在完成时关闭连接的方法。我们使用 ``async with`` 块来确保我们关闭连接 —— 在像这样的玩具示例中，这并不是什么大问题，但这是一个很好的习惯，而且 Trio 被设计成使得 ``with`` 和 ``async with`` 块易于使用。

   最后，我们启动两个子任务，并将流的引用传递给它们每一个。（这也是一个很好的示例，展示了 ``nursery.start_soon`` 如何让你传递位置参数给生成的函数。）

   第一个任务的工作是向服务器发送数据：

   .. literalinclude:: tutorial/echo-client.py
      :linenos:
      :lineno-match:
      :pyobject: sender

   它使用一个循环，在调用 ``await client_stream.send_all(...)`` 发送一些数据（这是你在任何类型的 Trio 流上发送数据时使用的方法）和休眠一秒钟之间交替进行，以避免在终端上输出滚动得太快。

   第二个任务的工作是处理服务器返回的数据：

   .. literalinclude:: tutorial/echo-client.py
      :linenos:
      :lineno-match:
      :pyobject: receiver

   它使用 ``async for`` 循环从服务器获取数据。或者，它可以使用 `~trio.abc.ReceiveStream.receive_some`，这是 `~trio.abc.SendStream.send_all` 的反向操作，但使用 ``async for`` 可以节省一些样板代码。

   现在我们准备来看服务器部分。

.. tab:: 英文


   To start with, here's an example echo *client*, i.e., the program that
   will send some data at our echo server and get responses back:

   .. literalinclude:: tutorial/echo-client.py
      :linenos:

   Note that this code will not work without a TCP server such as the one
   we'll implement below.

   The overall structure here should be familiar, because it's just like
   our :ref:`last example <tutorial-example-tasks-intro>`: we have a
   parent task, which spawns two child tasks to do the actual work, and
   then at the end of the ``async with`` block it switches into full-time
   parenting mode while waiting for them to finish. But now instead of
   just calling :func:`trio.sleep`, the children use some of Trio's
   networking APIs.

   Let's look at the parent first:

   .. literalinclude:: tutorial/echo-client.py
      :linenos:
      :lineno-match:
      :pyobject: parent

   First we call :func:`trio.open_tcp_stream` to make a TCP connection to
   the server. ``127.0.0.1`` is a magic `IP address
   <https://en.wikipedia.org/wiki/IP_address>`__ meaning "the computer
   I'm running on", so this connects us to whatever program on the local
   computer is using ``PORT`` as its contact point. This function returns
   an object implementing Trio's :class:`~trio.abc.Stream` interface,
   which gives us methods to send and receive bytes, and to close the
   connection when we're done. We use an ``async with`` block to make
   sure that we do close the connection – not a big deal in a toy example
   like this, but it's a good habit to get into, and Trio is designed to
   make ``with`` and ``async with`` blocks easy to use.

   Finally, we start up two child tasks, and pass each of them a
   reference to the stream. (This is also a good example of how
   ``nursery.start_soon`` lets you pass positional arguments to the
   spawned function.)

   Our first task's job is to send data to the server:

   .. literalinclude:: tutorial/echo-client.py
      :linenos:
      :lineno-match:
      :pyobject: sender

   It uses a loop that alternates between calling ``await
   client_stream.send_all(...)`` to send some data (this is the method
   you use for sending data on any kind of Trio stream), and then
   sleeping for a second to avoid making the output scroll by too fast on
   your terminal.

   And the second task's job is to process the data the server sends back:

   .. literalinclude:: tutorial/echo-client.py
      :linenos:
      :lineno-match:
      :pyobject: receiver

   It uses an ``async for`` loop to fetch data from the server.
   Alternatively, it could use `~trio.abc.ReceiveStream.receive_some`,
   which is the opposite of `~trio.abc.SendStream.send_all`, but using
   ``async for`` saves some boilerplate.

   And now we're ready to look at the server.


.. _tutorial-echo-server-example:

回显服务器
~~~~~~~~~~~~~~

**An echo server**

.. tab:: 中文

   像往常一样，让我们先看一下完整的代码，然后再逐个讨论各个部分：

   .. literalinclude:: tutorial/echo-server.py
      :linenos:

   我们从 ``main`` 开始，它只有一行：

   .. literalinclude:: tutorial/echo-server.py
      :linenos:
      :lineno-match:
      :pyobject: main

   这段代码调用了 :func:`serve_tcp`，这是 Trio 提供的一个便捷函数，它会一直运行下去（或者至少直到你按下 Ctrl-C 或者以其他方式取消它）。这个函数执行了几件有用的事情：

   * 它在内部创建了一个 `nursery`，以便我们的服务器能够同时处理多个连接。

   * 它监听指定的 ``PORT`` 上的传入 TCP 连接。

   * 每当一个连接到来时，它就会启动一个新的任务，运行我们传递的函数（在这个示例中是 ``echo_server``），并将表示该连接的流传递给它。

   * 每当一个任务退出时，它会确保关闭相应的连接。（这就是为什么你在服务器端看不到任何 ``async with server_stream`` 的原因 —— :func:`serve_tcp` 为我们处理了这个问题。）

   因此，:func:`serve_tcp` 非常方便！这一部分几乎适用于任何服务器，无论是回显服务器、HTTP 服务器、SSH 服务器，还是其他类型的服务器，因此将这些功能封装成像这样的帮助函数是很有意义的。

   接下来我们来看一下 ``echo_server``，它处理每个客户端连接——因此如果有多个客户端，可能会有多个 ``echo_server`` 调用同时运行。这是我们实现服务器“回显”行为的地方。理解起来应该相当简单，因为它使用了我们在上一节中看到的相同流函数：

   .. literalinclude:: tutorial/echo-server.py
      :linenos:
      :lineno-match:
      :pyobject: echo_server

   参数 ``server_stream`` 是由 :func:`serve_tcp` 提供的，它是我们在客户端创建的连接的另一端：因此客户端传递给 ``send_all`` 的数据会从这里传出。然后我们有一个 ``try`` 块，稍后讨论，最后是服务器循环，循环在从套接字读取一些数据和将数据发送回去之间交替进行（除非套接字已关闭，这时我们会退出）。

   那么这个 ``try`` 块是干什么的呢？记住，在 Trio 中，像 Python 一样，异常会一直传播，直到被捕获。这里我们认为可能会有一些意外的异常发生，因此我们希望将它们局限于让这一任务崩溃，而不影响整个程序的运行。例如，如果客户端在错误的时刻关闭连接，那么可能会导致这段代码在已关闭的连接上调用 ``send_all`` 并引发 :exc:`BrokenResourceError`；这虽然不太理想，在更复杂的程序中我们可能希望更明确地处理它，但它并不表示 *其他* 连接有问题。另一方面，如果异常是像 :exc:`KeyboardInterrupt` 这样的，我们确实希望它传播到父任务并导致整个程序退出。为了表达这一点，我们使用了一个带有 ``except Exception:`` 处理程序的 ``try`` 块。

   通常，Trio 和 Python 一样，允许你自己决定是否以及如何处理异常。

.. tab:: 英文

   As usual, let's look at the whole thing first, and then we'll discuss
   the pieces:

   .. literalinclude:: tutorial/echo-server.py
      :linenos:

   Let's start with ``main``, which is just one line long:

   .. literalinclude:: tutorial/echo-server.py
      :linenos:
      :lineno-match:
      :pyobject: main

   What this does is call :func:`serve_tcp`, which is a convenience
   function Trio provides that runs forever (or at least until you hit
   control-C or otherwise cancel it). This function does several helpful
   things:

   * It creates a nursery internally, so that our server will be able to
     handle multiple connections at the same time.

   * It listens for incoming TCP connections on the specified ``PORT``.

   * Whenever a connection arrives, it starts a new task running the
     function we pass (in this example it's ``echo_server``), and passes
     it a stream representing that connection.
  
   * When each task exits, it makes sure to close the corresponding
     connection. (That's why you don't see any ``async with
     server_stream`` in the server – :func:`serve_tcp` takes care of this
     for us.)

   So :func:`serve_tcp` is pretty handy! This part works pretty much the
   same for any server, whether it's an echo server, HTTP server, SSH
   server, or whatever, so it makes sense to bundle it all up together in
   a helper function like this.

   Now let's look at ``echo_server``, which handles each client
   connection – so if there are multiple clients, there might be multiple
   calls to ``echo_server`` running at the same time. This is where we
   implement our server's "echo" behavior. This should be pretty
   straightforward to understand, because it uses the same stream
   functions we saw in the last section:

   .. literalinclude:: tutorial/echo-server.py
      :linenos:
      :lineno-match:
      :pyobject: echo_server

   The argument ``server_stream`` is provided by :func:`serve_tcp`, and
   is the other end of the connection we made in the client: so the data
   that the client passes to ``send_all`` will come out here. Then we
   have a ``try`` block discussed below, and finally the server loop
   which alternates between reading some data from the socket and then
   sending it back out again (unless the socket was closed, in which case
   we quit).

   So what's that ``try`` block for? Remember that in Trio, like Python
   in general, exceptions keep propagating until they're caught. Here we
   think it's plausible there might be unexpected exceptions, and we want
   to isolate that to making just this one task crash, without taking
   down the whole program. For example, if the client closes the
   connection at the wrong moment then it's possible this code will end
   up calling ``send_all`` on a closed connection and get a
   :exc:`BrokenResourceError`; that's unfortunate, and in a more serious
   program we might want to handle it more explicitly, but it doesn't
   indicate a problem for any *other* connections. On the other hand, if
   the exception is something like a :exc:`KeyboardInterrupt`, we *do*
   want that to propagate out into the parent task and cause the whole
   program to exit. To express this, we use a ``try`` block with an
   ``except Exception:`` handler.

   In general, Trio leaves it up to you to decide whether and how you
   want to handle exceptions, just like Python in general.


尝试一下
~~~~~~~~~~

**Try it out**

.. tab:: 中文

   打开几个终端，在一个终端中运行 ``echo-server.py``，在另一个终端中运行 ``echo-client.py``，然后观察消息的滚动！当你感到无聊时，可以通过按 Ctrl-C 来退出。

   可以尝试的几件事：

   * 打开多个终端，同时运行多个客户端，所有客户端都与同一个服务器进行通信。

   * 观察当你在客户端按下 Ctrl-C 时，服务器的反应。

   * 观察当你在服务器按下 Ctrl-C 时，客户端的反应。

.. tab:: 英文

   Open a few terminals, run ``echo-server.py`` in one, run
   ``echo-client.py`` in another, and watch the messages scroll by! When
   you get bored, you can exit by hitting control-C.

   Some things to try:

   * Open several terminals, and run multiple clients at the same time,
     all talking to the same server.

   * See how the server reacts when you hit control-C on the client.

   * See how the client reacts when you hit control-C on the server.


回显客户端和服务器中的流控制
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Flow control in our echo client and server**

.. tab:: 中文

   你可能会有一个疑问：为什么我们的客户端使用两个独立的任务来发送和接收数据，而不是像服务器那样使用一个任务来交替执行发送和接收？例如，我们的客户端可以使用一个像这样的单一任务：

   .. code-block:: python

      # 你能发现这段代码的两个问题吗？
      async def send_and_receive(client_stream):
         while True:
            data = ...
            await client_stream.send_all(data)
            received = await client_stream.receive_some()
            if not received:
                  sys.exit()
            await trio.sleep(1)

   事实证明，这段代码有两个问题——一个是小问题，一个是大问题。两个问题都与流量控制有关。小问题是，当我们调用 ``receive_some`` 时，我们并没有等待 *所有* 数据都可用； ``receive_some`` 会在 *任何* 数据可用时立即返回。如果 ``data`` 很小，那么操作系统/网络/服务器 *可能* 会把它们一起发送，但没有保证。如果服务器发送的是 ``hello``，我们可能会收到 ``hello``、 ``he`` ``llo``、 ``h`` ``e`` ``l`` ``l`` ``o``，或者... 总之，每当我们期望的数据超过一个字节时，我们就必须准备好多次调用 ``receive_some``。

   特别是在这种情况下，如果 ``data`` 足够大，超过了某个内部阈值，操作系统或网络可能决定总是将其分成多个部分。现在在每次循环中，我们发送了 ``len(data)`` 字节，但读取的却少于这个数量。结果就像是内存泄漏：数据会越来越多地堆积在网络中，直到最终某个地方出问题。

   .. note:: 如果你想知道 *如何* 出问题，可以使用
      :func:`~trio.abc.ReceiveStream.receive_some` 的可选参数来限制每次读取的字节数，然后看看会发生什么。

   我们可以通过跟踪每一时刻预期的数据量，并一直调用 ``receive_some``，直到我们接收到所有数据，从而修复这个问题：

   .. code-block:: python

      expected = len(data)
      while expected > 0:
         received = await client_stream.receive_some(expected)
         if not received:
            sys.exit(1)
         expected -= len(received)

   虽然这有点繁琐，但它能解决这个问题。

   然而，还有一个更深层次的问题。我们仍然在交替执行发送和接收操作。注意，当我们发送数据时，我们使用了 ``await``：这意味着发送操作可能会 *阻塞*。为什么会这样？我们发送的任何数据首先都会进入操作系统的缓冲区，然后传输到网络，接着进入接收计算机的另一个操作系统缓冲区，最后接收程序调用 ``receive_some`` 来从这些缓冲区中取出数据。如果我们用少量数据调用 ``send_all``，它会进入这些缓冲区，``send_all`` 会立即返回。但是，如果我们足够快速地发送大量数据，缓冲区最终会填满，``send_all`` 会阻塞，直到远端调用 ``receive_some`` 并释放一些空间。

   现在从服务器的角度考虑。每次它调用 ``receive_some`` 时，都会获取一些数据，并且需要将这些数据发送回去。在发送数据之前，暂时存储在内存中的数据占用了内存。计算机的 RAM 是有限的，所以如果我们的服务器行为规范，那么在某些时刻，它需要停止调用 ``receive_some``，直到它通过自己的 ``send_all`` 调用清理掉一些旧数据。所以对于服务器而言，唯一可行的方案是交替执行接收和发送。

   但是我们需要记住，不仅是客户端的 ``send_all`` 可能会阻塞：服务器的 ``send_all`` 也可能进入阻塞状态，直到客户端调用 ``receive_some``。所以如果服务器在调用 ``receive_some`` 之前等待 ``send_all`` 完成，而我们的客户端也在等待 ``send_all`` 完成后再调用 ``receive_some``，... 我们就遇到问题了！客户端不会调用 ``receive_some``，直到服务器调用了 ``receive_some``；而服务器不会调用 ``receive_some``，直到客户端调用了 ``receive_some``。如果我们的客户端是按发送和接收交替进行编写的，而且它尝试发送的那块数据足够大（例如，10MB 的数据在大多数配置下应该就能触发问题），那么这两个进程就会 `死锁
   <https://en.wikipedia.org/wiki/Deadlock>`__。

   教训：Trio 提供了强大的工具来管理顺序和并发执行。在这个例子中，我们看到服务器需要 ``send`` 和 ``receive_some`` 按顺序交替执行，而客户端则需要它们并发执行，且两者都很容易实现。但是当你在实现像这样的网络代码时，必须小心地考虑流量控制和缓冲问题，因为你必须选择正确的执行模式！

   其他流行的异步库，比如 `Twisted
   <https://twistedmatrix.com/>`__ 和 :mod:`asyncio`，通常通过到处放置无限制的缓冲区来掩盖这些问题。这可以避免死锁，但也会带来其他问题，特别是会使得 `内存使用和延迟
   <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#three-bugs>`__ 难以控制。虽然这两种方法都有其优点，但 Trio 的立场是，最好尽可能直接暴露底层问题，并提供良好的工具来直面它。

   .. note::

      如果你想试着故意制造死锁来亲自看看发生什么，并且你使用的是 Windows，那么你可能需要将 ``send_all`` 调用分成两个分别发送一半数据的调用。这是因为 Windows 在处理缓冲区时有一个 `有些不寻常的方式
      <https://stackoverflow.com/questions/28785626/what-is-the-size-of-a-socket-send-buffer-in-windows>`__。

.. tab:: 英文

   Here's a question you might be wondering about: why does our client
   use two separate tasks for sending and receiving, instead of a single
   task that alternates between them – like the server has? For example,
   our client could use a single task like:

   .. code-block:: python

      # Can you spot the two problems with this code?
      async def send_and_receive(client_stream):
         while True:
            data = ...
            await client_stream.send_all(data)
            received = await client_stream.receive_some()
            if not received:
                  sys.exit()
            await trio.sleep(1)

   It turns out there are two problems with this – one minor and one
   major. Both relate to flow control. The minor problem is that when we
   call ``receive_some`` here we're not waiting for *all* the data to be
   available; ``receive_some`` returns as soon as *any* data is available. If
   ``data`` is small, then our operating systems / network / server will
   *probably* keep it all together in a single chunk, but there's no
   guarantee. If the server sends ``hello`` then we might get ``hello``,
   or ``he`` ``llo``, or ``h`` ``e`` ``l`` ``l`` ``o``, or ... bottom
   line, any time we're expecting more than one byte of data, we have to
   be prepared to call ``receive_some`` multiple times.

   And where this would go especially wrong is if we find ourselves in
   the situation where ``data`` is big enough that it passes some
   internal threshold, and the operating system or network decide to
   always break it up into multiple pieces. Now on each pass through the
   loop, we send ``len(data)`` bytes, but read less than that. The result
   is something like a memory leak: we'll end up with more and more data
   backed up in the network, until eventually something breaks.

   .. note:: If you're curious *how* things break, then you can use
      :func:`~trio.abc.ReceiveStream.receive_some`\'s optional argument to put
      a limit on how many bytes you read each time, and see what happens.

   We could fix this by keeping track of how much data we're expecting at
   each moment, and then keep calling ``receive_some`` until we get it all:

   .. code-block:: python

      expected = len(data)
      while expected > 0:
         received = await client_stream.receive_some(expected)
         if not received:
            sys.exit(1)
         expected -= len(received)

   This is a bit cumbersome, but it would solve this problem.

   There's another problem, though, that's deeper. We're still
   alternating between sending and receiving. Notice that when we send
   data, we use ``await``: this means that sending can potentially
   *block*. Why does this happen? Any data that we send goes first into
   an operating system buffer, and from there onto the network, and then
   another operating system buffer on the receiving computer, before the
   receiving program finally calls ``receive_some`` to take the data out
   of these buffers. If we call ``send_all`` with a small amount of data,
   then it goes into these buffers and ``send_all`` returns immediately.
   But if we send enough data fast enough, eventually the buffers fill
   up, and ``send_all`` will block until the remote side calls
   ``receive_some`` and frees up some space.

   Now let's think about this from the server's point of view. Each time
   it calls ``receive_some``, it gets some data that it needs to send
   back. And until it sends it back, the data that is sitting around takes up
   memory. Computers have finite amounts of RAM, so if our server is well
   behaved then at some point it needs to stop calling ``receive_some``
   until it gets rid of some of the old data by doing its own call to
   ``send_all``. So for the server, really the only viable option is to
   alternate between receiving and sending.

   But we need to remember that it's not just the client's call to
   ``send_all`` that might block: the server's call to ``send_all`` can
   also get into a situation where it blocks until the client calls
   ``receive_some``. So if the server is waiting for ``send_all`` to
   finish before it calls ``receive_some``, and our client also waits for
   ``send_all`` to finish before it calls ``receive_some``,... we have a
   problem! The client won't call ``receive_some`` until the server has
   called ``receive_some``, and the server won't call ``receive_some``
   until the client has called ``receive_some``. If our client is written
   to alternate between sending and receiving, and the chunk of data it's
   trying to send is large enough (e.g. 10 megabytes will probably do it
   in most configurations), then the two processes will `deadlock
   <https://en.wikipedia.org/wiki/Deadlock>`__.

   Moral: Trio gives you powerful tools to manage sequential and
   concurrent execution. In this example we saw that the server needs
   ``send`` and ``receive_some`` to alternate in sequence, while the
   client needs them to run concurrently, and both were straightforward
   to implement. But when you're implementing network code like this then
   it's important to think carefully about flow control and buffering,
   because it's up to you to choose the right execution mode!

   Other popular async libraries like `Twisted
   <https://twistedmatrix.com/>`__ and :mod:`asyncio` tend to paper over
   these kinds of issues by throwing in unbounded buffers everywhere.
   This can avoid deadlocks, but can introduce its own problems and in
   particular can make it difficult to keep `memory usage and latency
   under control
   <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#three-bugs>`__.
   While both approaches have their advantages, Trio takes the position
   that it's better to expose the underlying problem as directly as
   possible and provide good tools to confront it head-on.

   .. note::

      If you want to try and make the deadlock happen on purpose to see
      for yourself, and you're using Windows, then you might need to
      split the ``send_all`` call up into two calls that each send half of
      the data. This is because Windows has a `somewhat unusual way of
      handling buffering
      <https://stackoverflow.com/questions/28785626/what-is-the-size-of-a-socket-send-buffer-in-windows>`__.


当出现问题时：并发任务中的超时、取消和异常
-------------------------------------------------------------------------------

**When things go wrong: timeouts, cancellation and exceptions in concurrent tasks**

.. tab:: 中文

   TODO: 给出一个使用 :func:`fail_after` 的例子

   TODO: 解释 :exc:`Cancelled`

   TODO: 解释当一个子任务抛出异常时如何使用取消

   TODO: 可能简要讨论 :exc:`KeyboardInterrupt` 的处理方式？

.. tab:: 英文

   TODO: give an example using :func:`fail_after`

   TODO: explain :exc:`Cancelled`

   TODO: explain how cancellation is also used when one child raises an
   exception

   TODO: maybe a brief discussion of :exc:`KeyboardInterrupt` handling?

..
   Timeouts
   --------

   XX todo

   timeout example:

   .. code-block:: python

      async def counter():
          for i in range(100000):
              print(i)
              await trio.sleep(1)

      async def main():
          with trio.fail_after(10):
              await counter()

   you can stick anything inside a timeout block, even child tasks

     [show something like the first example but with a timeout – they
     both get cancelled, the cancelleds get packed into an ExceptionGroup, and
     then the timeout block catches the cancelled]

   brief discussion of KI?
   tasks-with-trace.py + control-C is pretty interesting
   or maybe leave it for a blog post?
