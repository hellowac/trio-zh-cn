.. currentmodule:: trio

.. module:: trio.socket

使用 :mod:`trio.socket` 进行低级网络编程
=======================================================

**Low-level networking with :mod:`trio.socket`**


.. tab:: 中文

   :mod:`trio.socket` 模块提供了 Trio 的基本底层网络 API。如果您正在通过 IPv4/IPv6/Unix 域套接字进行普通的流式连接操作, 那么您可能希望使用上面描述的高层 API。如果您想使用 UDP, 或使用像 ``AF_BLUETOOTH`` 这样的特殊地址族, 或者需要直接访问系统网络 API 的所有奇怪部分, 那么您来对地方了。

.. tab:: 英文

   The :mod:`trio.socket` module provides Trio's basic low-level
   networking API. If you're doing ordinary things with stream-oriented
   connections over IPv4/IPv6/Unix domain sockets, then you probably want
   to stick to the high-level API described above. If you want to use
   UDP, or exotic address families like ``AF_BLUETOOTH``, or otherwise
   get direct access to all the quirky bits of your system's networking
   API, then you're in the right place.


顶级导出
------------------

**Top-level exports**

.. tab:: 中文

   通常, :mod:`trio.socket` 模块暴露的 API 与标准库的 :mod:`socket` 模块相似。大多数常量 (如 ``SOL_SOCKET`` ) 和简单的工具函数 (如 :func:`~socket.inet_aton` ) 都只是重新导出了, 保持不变。但也有一些不同之处, 下面将进行描述。

   首先, Trio 提供了所有返回套接字对象的标准库函数的类比；它们的接口完全相同, 只是它们被修改为返回 Trio 套接字对象：

   .. autofunction:: socket

   .. autofunction:: socketpair

   .. autofunction:: fromfd

   .. function:: fromshare(data)

      类似于 :func:`socket.fromshare`, 但返回一个 Trio 套接字对象。

   此外, 还有一个新函数可以直接将标准库的套接字转换为 Trio 套接字：

   .. autofunction:: from_stdlib_socket

   与 :class:`socket.socket` 不同, :func:`trio.socket.socket` 是一个函数, 而不是一个类；如果您想检查一个对象是否是 Trio 套接字, 请使用 ``isinstance(obj, trio.socket.SocketType)``。

   对于名称查找, Trio 提供了标准的函数, 但做了一些修改：

   .. autofunction:: getaddrinfo

   .. autofunction:: getnameinfo

   .. autofunction:: getprotobyname

   Trio 特意不包含一些过时的, 冗余的或损坏的功能：

   * :func:`~socket.gethostbyname`, :func:`~socket.gethostbyname_ex`, :func:`~socket.gethostbyaddr`：已过时；请改用 :func:`~socket.getaddrinfo` 和 :func:`~socket.getnameinfo`。

   * :func:`~socket.getservbyport`：已过时且存在 `bug <https://bugs.python.org/issue30482>`__；请改用：

   .. code-block:: python

      _, service_name = await getnameinfo(('127.0.0.1', port), NI_NUMERICHOST)

   * :func:`~socket.getservbyname`：已过时且存在 `bug <https://bugs.python.org/issue30482>`__；请改用：

   .. code-block:: python

      await getaddrinfo(None, service_name)

   * :func:`~socket.getfqdn`：已过时；请使用 :func:`getaddrinfo` 并带上 ``AI_CANONNAME`` 标志。

   * :func:`~socket.getdefaulttimeout`, :func:`~socket.setdefaulttimeout`：请使用 Trio 的标准支持来进行 :ref:`取消 <cancellation>` 。

   * 在 Windows 上,  ``SO_REUSEADDR`` 没有被导出, 因为它是一个陷阱：这个名字与 Unix 上的 ``SO_REUSEADDR`` 相同, 但语义是 `不同且极为破坏性的 <https://msdn.microsoft.com/en-us/library/windows/desktop/ms740621(v=vs.85).aspx>`__ 。在非常罕见的情况下, 如果您确实需要在 Windows 上使用 ``SO_REUSEADDR`` , 它仍然可以通过标准库的 :mod:`socket` 模块访问。

.. tab:: 英文

   Generally, the API exposed by :mod:`trio.socket` mirrors that of the
   standard library :mod:`socket` module. Most constants (like
   ``SOL_SOCKET``) and simple utilities (like :func:`~socket.inet_aton`)
   are simply re-exported unchanged. But there are also some differences,
   which are described here.

   First, Trio provides analogues to all the standard library functions
   that return socket objects; their interface is identical, except that
   they're modified to return Trio socket objects instead:

   .. autofunction:: socket
      :no-index:

   .. autofunction:: socketpair
      :no-index:

   .. autofunction:: fromfd
      :no-index:

   .. function:: fromshare(data)
      :no-index:

      Like :func:`socket.fromshare`, but returns a Trio socket object.

   In addition, there is a new function to directly convert a standard
   library socket into a Trio socket:

   .. autofunction:: from_stdlib_socket
      :no-index:

   Unlike :class:`socket.socket`, :func:`trio.socket.socket` is a
   function, not a class; if you want to check whether an object is a
   Trio socket, use ``isinstance(obj, trio.socket.SocketType)``.

   For name lookup, Trio provides the standard functions, but with some
   changes:

   .. autofunction:: getaddrinfo
      :no-index:

   .. autofunction:: getnameinfo
      :no-index:

   .. autofunction:: getprotobyname
      :no-index:

   Trio intentionally DOES NOT include some obsolete, redundant, or
   broken features:

   * :func:`~socket.gethostbyname`, :func:`~socket.gethostbyname_ex`,
     :func:`~socket.gethostbyaddr`: obsolete; use
     :func:`~socket.getaddrinfo` and :func:`~socket.getnameinfo` instead.

   * :func:`~socket.getservbyport`: obsolete and `buggy
     <https://bugs.python.org/issue30482>`__; instead, do:

   .. code-block:: python

      _, service_name = await getnameinfo(('127.0.0.1', port), NI_NUMERICHOST)

   * :func:`~socket.getservbyname`: obsolete and `buggy
     <https://bugs.python.org/issue30482>`__ ; instead, do:

   .. code-block:: python

      await getaddrinfo(None, service_name)

   * :func:`~socket.getfqdn`: obsolete; use :func:`getaddrinfo` with the
     ``AI_CANONNAME`` flag.

   * :func:`~socket.getdefaulttimeout`,
     :func:`~socket.setdefaulttimeout`: instead, use Trio's standard
     support for :ref:`cancellation`.

   * On Windows, ``SO_REUSEADDR`` is not exported, because it's a trap:
     the name is the same as Unix ``SO_REUSEADDR``, but the semantics are
     `different and extremely broken
     <https://msdn.microsoft.com/en-us/library/windows/desktop/ms740621(v=vs.85).aspx>`__. In
     the very rare cases where you actually want ``SO_REUSEADDR`` on
     Windows, then it can still be accessed from the standard library's
     :mod:`socket` module.




套接字对象
--------------

**Socket objects**

.. tab:: 中文

   .. class:: SocketType

      .. note:: :class:`trio.socket.SocketType` 是一个抽象类, 不能直接实例化；您可以通过调用构造函数, 如 :func:`trio.socket.socket`, 来获得具体的套接字对象。然而, 您可以使用它来检查一个对象是否是 Trio 套接字, 方法是 ``isinstance(obj, trio.socket.SocketType)``。

      Trio 套接字对象总体上与 :ref:`标准库套接字对象 <python:socket-objects>` 非常相似, 但有一些重要的区别：

      首先, 也是最显著的, 所有内容都被改造成了“Trio 风格”：
      阻塞方法变为异步方法, 并且以下属性 *不* 支持：

      * :meth:`~socket.socket.setblocking`：Trio 套接字始终表现得像阻塞套接字；如果您需要同时从多个套接字读取/写入, 应该创建多个任务。
      * :meth:`~socket.socket.settimeout`：请改用 :ref:`取消 <cancellation>`。
      * :meth:`~socket.socket.makefile`：Python 的类文件 API 是同步的, 因此无法在异步套接字上实现。
      * :meth:`~socket.socket.sendall`：可能支持, 但您最好使用更高层次的 :class:`~trio.SocketStream`, 特别是它的 :meth:`~trio.SocketStream.send_all` 方法, 这个方法还会执行额外的错误检查。

      此外, 以下方法与 :class:`socket.socket` 中的相似, 但有一些 Trio 特有的怪癖：

      .. method:: connect
         :async:

         将套接字连接到远程地址。

         类似于 :meth:`socket.socket.connect`, 但它是异步的。

         .. warning::

            由于底层操作系统 API 的限制, 一旦连接尝试开始, 可能无法正确取消该连接。如果 :meth:`connect` 被取消, 且无法中止连接尝试, 则它将：

            1. 强制关闭套接字以防止意外重用
            2. 引发 :exc:`~trio.Cancelled`。

            简而言之：如果 :meth:`connect` 被取消, 则套接字处于未知状态——可能是打开的, 也可能是关闭的。唯一合理的做法是关闭它。

      .. method:: is_readable

         检查套接字是否可读。

      .. method:: sendfile

         `尚未实现! <https://github.com/python-trio/trio/issues/45>`__

      我们还跟踪一个额外的状态位, 因为它对 :class:`trio.SocketStream` 很有用：

      .. attribute:: did_shutdown_SHUT_WR

         如果您调用了 ``sock.shutdown(SHUT_WR)`` 或 ``sock.shutdown(SHUT_RDWR)``, 则此 :class:`bool` 属性为 True, 否则为 False。

      以下方法与 :class:`socket.socket` 中的对应方法相同, 唯一不同的是它们是异步的, 并且那些接受地址参数的方法需要预先解析的地址：

      * :meth:`~socket.socket.accept`
      * :meth:`~socket.socket.bind`
      * :meth:`~socket.socket.recv`
      * :meth:`~socket.socket.recv_into`
      * :meth:`~socket.socket.recvfrom`
      * :meth:`~socket.socket.recvfrom_into`
      * :meth:`~socket.socket.recvmsg`  (如果可用 ) 
      * :meth:`~socket.socket.recvmsg_into`  (如果可用 ) 
      * :meth:`~socket.socket.send`
      * :meth:`~socket.socket.sendto`
      * :meth:`~socket.socket.sendmsg`  (如果可用 ) 

      所有未在上面提到的方法和属性都与 :class:`socket.socket` 中的对应项相同：

      * :attr:`~socket.socket.family`
      * :attr:`~socket.socket.type`
      * :attr:`~socket.socket.proto`
      * :meth:`~socket.socket.fileno`
      * :meth:`~socket.socket.listen`
      * :meth:`~socket.socket.getpeername`
      * :meth:`~socket.socket.getsockname`
      * :meth:`~socket.socket.close`
      * :meth:`~socket.socket.shutdown`
      * :meth:`~socket.socket.setsockopt`
      * :meth:`~socket.socket.getsockopt`
      * :meth:`~socket.socket.dup`
      * :meth:`~socket.socket.detach`
      * :meth:`~socket.socket.share`
      * :meth:`~socket.socket.set_inheritable`
      * :meth:`~socket.socket.get_inheritable`

.. tab:: 英文

   .. class:: SocketType
      :no-index:

      .. note:: :class:`trio.socket.SocketType` is an abstract class and cannot be instantiated directly; you get concrete socket objects by calling constructors like :func:`trio.socket.socket`. However, you can use it to check if an object is a Trio socket via ``isinstance(obj, trio.socket.SocketType)``.

      Trio socket objects are overall very similar to the :ref:`standard
      library socket objects <python:socket-objects>`, with a few
      important differences:

      First, and most obviously, everything is made "Trio-style":
      blocking methods become async methods, and the following attributes
      are *not* supported:

      * :meth:`~socket.socket.setblocking`: Trio sockets always act like blocking sockets; if you need to read/write from multiple sockets at once, then create multiple tasks.
      * :meth:`~socket.socket.settimeout`: see :ref:`cancellation` instead.
      * :meth:`~socket.socket.makefile`: Python's file-like API is synchronous, so it can't be implemented on top of an async socket.
      * :meth:`~socket.socket.sendall`: Could be supported, but you're better off using the higher-level :class:`~trio.SocketStream`, and specifically its :meth:`~trio.SocketStream.send_all` method, which also does additional error checking.

      In addition, the following methods are similar to the equivalents in :class:`socket.socket`, but have some Trio-specific quirks:

      .. method:: connect
         :no-index:
         :async:

         Connect the socket to a remote address.

         Similar to :meth:`socket.socket.connect`, except async.

         .. warning::

            Due to limitations of the underlying operating system APIs, it is
            not always possible to properly cancel a connection attempt once it
            has begun. If :meth:`connect` is cancelled, and is unable to
            abort the connection attempt, then it will:

            1. forcibly close the socket to prevent accidental reuse
            2. raise :exc:`~trio.Cancelled`.

            tl;dr: if :meth:`connect` is cancelled then the socket is
            left in an unknown state – possibly open, and possibly
            closed. The only reasonable thing to do is to close it.

      .. method:: is_readable
         :no-index:

         Check whether the socket is readable or not.

      .. method:: sendfile
         :no-index:

         `Not implemented yet! <https://github.com/python-trio/trio/issues/45>`__

      We also keep track of an extra bit of state, because it turns out
      to be useful for :class:`trio.SocketStream`:

      .. attribute:: did_shutdown_SHUT_WR
         :no-index:

         This :class:`bool` attribute is True if you've called
         ``sock.shutdown(SHUT_WR)`` or ``sock.shutdown(SHUT_RDWR)``, and
         False otherwise.

      The following methods are identical to their equivalents in
      :class:`socket.socket`, except async, and the ones that take address
      arguments require pre-resolved addresses:

      * :meth:`~socket.socket.accept`
      * :meth:`~socket.socket.bind`
      * :meth:`~socket.socket.recv`
      * :meth:`~socket.socket.recv_into`
      * :meth:`~socket.socket.recvfrom`
      * :meth:`~socket.socket.recvfrom_into`
      * :meth:`~socket.socket.recvmsg` (if available)
      * :meth:`~socket.socket.recvmsg_into` (if available)
      * :meth:`~socket.socket.send`
      * :meth:`~socket.socket.sendto`
      * :meth:`~socket.socket.sendmsg` (if available)

      All methods and attributes *not* mentioned above are identical to
      their equivalents in :class:`socket.socket`:

      * :attr:`~socket.socket.family`
      * :attr:`~socket.socket.type`
      * :attr:`~socket.socket.proto`
      * :meth:`~socket.socket.fileno`
      * :meth:`~socket.socket.listen`
      * :meth:`~socket.socket.getpeername`
      * :meth:`~socket.socket.getsockname`
      * :meth:`~socket.socket.close`
      * :meth:`~socket.socket.shutdown`
      * :meth:`~socket.socket.setsockopt`
      * :meth:`~socket.socket.getsockopt`
      * :meth:`~socket.socket.dup`
      * :meth:`~socket.socket.detach`
      * :meth:`~socket.socket.share`
      * :meth:`~socket.socket.set_inheritable`
      * :meth:`~socket.socket.get_inheritable`

