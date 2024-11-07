

.. _task-local-storage:
任务存储
==========


任务本地存储
------------------

**Task-local storage**

.. tab:: 中文

   假设你正在编写一个响应网络请求的服务器，并在处理每个请求时记录一些信息。如果服务器很忙并且同时处理多个请求，那么你最终可能会得到如下日志：

   .. code-block:: none

      请求处理器启动
      请求处理器启动
      请求处理器完成
      请求处理器完成

   在这个日志中，很难知道哪些行来自哪个请求。（第一个启动的请求是否也是第一个完成的，还是不是？）解决这个问题的一种方法是为每个请求分配一个唯一的标识符，然后在每条日志消息中包含这个标识符：

   .. code-block:: none

      请求 1: 请求处理器启动
      请求 2: 请求处理器启动
      请求 2: 请求处理器完成
      请求 1: 请求处理器完成

   这样，我们就可以看到请求 1 比较慢：它在请求 2 之前启动，但在请求 2 之后完成。（你还可以做得更复杂一些 <https://opentracing.io/docs/>，但这对于一个例子来说已经足够了。）

   现在，问题来了：日志记录代码怎么知道请求标识符是什么？一种方法是显式地将其传递给每个可能需要输出日志的函数……但这基本上是每个函数，因为你永远不知道何时需要在调用栈深处的某个实用函数中添加 `log.debug(...)` 调用，而当你正在调试一个棘手的问题时，最不想做的事情就是首先停下来，重构所有内容以传递请求标识符！有时这是正确的解决方案，但有时如果我们能将标识符存储在一个全局变量中，那么每当日志函数需要它时就能查找它，这将更加方便。问题是……一个全局变量一次只能有一个值，所以如果我们有多个处理程序同时运行，这就无法实现。我们需要的是类似于全局变量的东西，但它可以根据哪个请求处理程序在访问它而具有不同的值。

   为了解决这个问题，Python 提供了一个标准库模块：:mod:`contextvars` 。

   下面是一个示例，演示如何使用 :mod:`contextvars` ：

   .. literalinclude:: reference-core/contextvar-example.py

   示例输出（你的输出可能略有不同）：

   .. code-block:: none

      请求 1: 请求处理器启动
      请求 2: 请求处理器启动
      请求 0: 请求处理器启动
      请求 2: 辅助任务 a 启动
      请求 2: 辅助任务 b 启动
      请求 1: 辅助任务 a 启动
      请求 1: 辅助任务 b 启动
      请求 0: 辅助任务 b 启动
      请求 0: 辅助任务 a 启动
      请求 2: 辅助任务 b 完成
      请求 2: 辅助任务 a 完成
      请求 2: 请求接收完成
      请求 0: 辅助任务 a 完成
      请求 1: 辅助任务 a 完成
      请求 1: 辅助任务 b 完成
      请求 1: 请求接收完成
      请求 0: 辅助任务 b 完成
      请求 0: 请求接收完成

   更多信息，请阅读 `contextvars 文档 <https://docs.python.org/3/library/contextvars.html>`__。

.. tab:: 英文

   Suppose you're writing a server that responds to network requests, and
   you log some information about each request as you process it. If the
   server is busy and there are multiple requests being handled at the
   same time, then you might end up with logs like this:

   .. code-block:: none

      Request handler started
      Request handler started
      Request handler finished
      Request handler finished

   In this log, it's hard to know which lines came from which
   request. (Did the request that started first also finish first, or
   not?) One way to solve this is to assign each request a unique
   identifier, and then include this identifier in each log message:

   .. code-block:: none

      request 1: Request handler started
      request 2: Request handler started
      request 2: Request handler finished
      request 1: Request handler finished

   This way we can see that request 1 was slow: it started before request
   2 but finished afterwards. (You can also get `much fancier
   <https://opentracing.io/docs/>`__, but this is enough for an
   example.)

   Now, here's the problem: how does the logging code know what the
   request identifier is? One approach would be to explicitly pass it
   around to every function that might want to emit logs... but that's
   basically every function, because you never know when you might need
   to add a ``log.debug(...)`` call to some utility function buried deep
   in the call stack, and when you're in the middle of a debugging a
   nasty problem that last thing you want is to have to stop first and
   refactor everything to pass through the request identifier! Sometimes
   this is the right solution, but other times it would be much more
   convenient if we could store the identifier in a global variable, so
   that the logging function could look it up whenever it needed
   it. Except... a global variable can only have one value at a time, so
   if we have multiple handlers running at once then this isn't going to
   work. What we need is something that's *like* a global variable, but
   that can have different values depending on which request handler is
   accessing it.

   To solve this problem, Python has a module in the standard
   library: :mod:`contextvars`.

   Here's a toy example demonstrating how to use :mod:`contextvars`:

   .. literalinclude:: reference-core/contextvar-example.py

   Example output (yours may differ slightly):

   .. code-block:: none

      request 1: Request handler started
      request 2: Request handler started
      request 0: Request handler started
      request 2: Helper task a started
      request 2: Helper task b started
      request 1: Helper task a started
      request 1: Helper task b started
      request 0: Helper task b started
      request 0: Helper task a started
      request 2: Helper task b finished
      request 2: Helper task a finished
      request 2: Request received finished
      request 0: Helper task a finished
      request 1: Helper task a finished
      request 1: Helper task b finished
      request 1: Request received finished
      request 0: Helper task b finished
      request 0: Request received finished

   For more information, read the
   `contextvars docs <https://docs.python.org/3/library/contextvars.html>`__.


