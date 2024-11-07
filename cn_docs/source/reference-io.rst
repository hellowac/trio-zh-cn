.. currentmodule:: trio

Trio 中的 I/O
===========

**I/O in Trio**

.. _abstract-stream-api:

抽象流 API
-----------------------

**The abstract Stream API**

.. tab:: 中文

   Trio 提供了一组抽象基类, 用于定义单向和双向字节流的标准接口。

   为什么这很有用？因为它允许你编写通用的协议实现, 这些实现可以在任意传输层上工作, 并且能够轻松创建复杂的传输配置。以下是一些示例：

   * :class:`trio.SocketStream` 封装一个原始套接字 (比如通过网络的 TCP 连接 ) , 并将其转换为标准的流接口。

   * :class:`trio.SSLStream` 是一个“流适配器”, 可以将任何实现了 :class:`trio.abc.Stream` 接口的对象转换为加密流。在 Trio 中, 通过在 :class:`~trio.SocketStream` 周围包装一个 :class:`~trio.SSLStream`, 是实现网络 SSL 通信的标准方式。

   * 如果你启动一个 :ref:`子进程 <subprocess>`, 你可以获得一个 :class:`~trio.abc.SendStream`, 它允许你写入子进程的 stdin, 以及一个 :class:`~trio.abc.ReceiveStream`, 它允许你从子进程的 stdout 中读取。如果你出于某种原因想要通过 SSL 与子进程通信, 可以使用 :class:`StapledStream` 将子进程的 stdin/stdout 合并成一个双向的 :class:`~trio.abc.Stream`, 然后将其包装在一个 :class:`~trio.SSLStream` 中：

     .. code-block:: python

         ssl_context = ssl.create_default_context()
         ssl_context.check_hostname = False
         s = SSLStream(StapledStream(process.stdin, process.stdout), ssl_context)

   * 有时你需要连接到一个 HTTPS 服务器, 但必须通过一个 Web 代理, 而代理本身也使用 HTTPS。这时, 你就需要进行 `SSL-on-top-of-SSL <https://daniel.haxx.se/blog/2016/11/26/https-proxy-with-curl/>`__。在 Trio 中, 这非常简单——只需将第一个 :class:`~trio.SSLStream` 再次包装在第二个 :class:`~trio.SSLStream` 中：

     .. code-block:: python

         # 获取到代理的原始 SocketStream 连接：
         s0 = await open_tcp_stream("proxy", 443)

         # 设置与代理的 SSL 连接：
         s1 = SSLStream(s0, proxy_ssl_context, server_hostname="proxy")
         # 请求连接到网站
         await s1.send_all(b"CONNECT website:443 / HTTP/1.0\r\n\r\n")
         await check_CONNECT_response(s1)

         # 设置与真实网站的 SSL 连接。注意, s1 已经是一个 SSLStream 对象, 
         # 这里我们将第二个 SSLStream 对象包装在它周围。
         s2 = SSLStream(s1, website_ssl_context, server_hostname="website")
         # 发出请求
         await s2.send_all(b"GET /index.html HTTP/1.0\r\n\r\n")
         ...

   * :mod:`trio.testing` 模块提供了一组 :ref:`灵活的内存流对象实现 <testing-streams>`, 因此如果你有一个协议实现需要测试, 你可以启动两个任务, 设置一个虚拟的“套接字”连接它们, 然后进行诸如在连接中注入随机但可重复的延迟之类的操作。

.. tab:: 英文

   Trio provides a set of abstract base classes that define a standard interface for unidirectional and bidirectional byte streams.

   Why is this useful? Because it lets you write generic protocol implementations that can work over arbitrary transports, and easily create complex transport configurations. Here's some examples:

   * :class:`trio.SocketStream` wraps a raw socket (like a TCP connection over the network), and converts it to the standard stream interface.

   * :class:`trio.SSLStream` is a "stream adapter" that can take any object that implements the :class:`trio.abc.Stream` interface, and convert it into an encrypted stream. In Trio the standard way to speak SSL over the network is to wrap an :class:`~trio.SSLStream` around a :class:`~trio.SocketStream`.

   * If you spawn a :ref:`subprocess <subprocess>`, you can get a :class:`~trio.abc.SendStream` that lets you write to its stdin, and a :class:`~trio.abc.ReceiveStream` that lets you read from its stdout. If for some reason you wanted to speak SSL to a subprocess, you could use a :class:`StapledStream` to combine its stdin/stdout into a single bidirectional :class:`~trio.abc.Stream`, and then wrap that in an :class:`~trio.SSLStream`:

      .. code-block:: python

         ssl_context = ssl.create_default_context()
         ssl_context.check_hostname = False
         s = SSLStream(StapledStream(process.stdin, process.stdout), ssl_context)

   * It sometimes happens that you want to connect to an HTTPS server, but you have to go through a web proxy... and the proxy also uses HTTPS. So you end up having to do `SSL-on-top-of-SSL <https://daniel.haxx.se/blog/2016/11/26/https-proxy-with-curl/>`__. In Trio this is trivial – just wrap your first :class:`~trio.SSLStream` in a second :class:`~trio.SSLStream`:

      .. code-block:: python

         # Get a raw SocketStream connection to the proxy:
         s0 = await open_tcp_stream("proxy", 443)

         # Set up SSL connection to proxy:
         s1 = SSLStream(s0, proxy_ssl_context, server_hostname="proxy")
         # Request a connection to the website
         await s1.send_all(b"CONNECT website:443 / HTTP/1.0\r\n\r\n")
         await check_CONNECT_response(s1)

         # Set up SSL connection to the real website. Notice that s1 is
         # already an SSLStream object, and here we're wrapping a second
         # SSLStream object around it.
         s2 = SSLStream(s1, website_ssl_context, server_hostname="website")
         # Make our request
         await s2.send_all(b"GET /index.html HTTP/1.0\r\n\r\n")
         ...

   * The :mod:`trio.testing` module provides a set of :ref:`flexible in-memory stream object implementations <testing-streams>`, so if you have a protocol implementation to test then you can start two tasks, set up a virtual "socket" connecting them, and then do things like inject random-but-repeatable delays into the connection.


抽象基类
~~~~~~~~~~~~~~~~~~~~~

**Abstract base classes**

.. currentmodule:: trio.abc

.. http://docutils.sourceforge.net/docs/ref/rst/directives.html#list-table

.. list-table:: Overview: abstract base classes for I/O
   :widths: auto
   :header-rows: 1

   * - Abstract base class
     - Inherits from...
     - Adds these abstract methods...
     - And these concrete methods.
     - Example implementations
   * - :class:`AsyncResource`
     -
     - :meth:`~AsyncResource.aclose`
     - ``__aenter__``, ``__aexit__``
     - :ref:`async-file-objects`
   * - :class:`SendStream`
     - :class:`AsyncResource`
     - :meth:`~SendStream.send_all`,
       :meth:`~SendStream.wait_send_all_might_not_block`
     -
     - :class:`~trio.testing.MemorySendStream`
   * - :class:`ReceiveStream`
     - :class:`AsyncResource`
     - :meth:`~ReceiveStream.receive_some`
     - ``__aiter__``, ``__anext__``
     - :class:`~trio.testing.MemoryReceiveStream`
   * - :class:`Stream`
     - :class:`SendStream`, :class:`ReceiveStream`
     -
     -
     - :class:`~trio.SSLStream`
   * - :class:`HalfCloseableStream`
     - :class:`Stream`
     - :meth:`~HalfCloseableStream.send_eof`
     -
     - :class:`~trio.SocketStream`, :class:`~trio.StapledStream`
   * - :class:`Listener`
     - :class:`AsyncResource`
     - :meth:`~Listener.accept`
     -
     - :class:`~trio.SocketListener`, :class:`~trio.SSLListener`
   * - :class:`SendChannel`
     - :class:`AsyncResource`
     - :meth:`~SendChannel.send`
     -
     - `~trio.MemorySendChannel`
   * - :class:`ReceiveChannel`
     - :class:`AsyncResource`
     - :meth:`~ReceiveChannel.receive`
     - ``__aiter__``, ``__anext__``
     - `~trio.MemoryReceiveChannel`
   * - `Channel`
     - `SendChannel`, `ReceiveChannel`
     -
     -
     -

.. autoclass:: trio.abc.AsyncResource
   :members:

.. currentmodule:: trio

.. autofunction:: aclose_forcefully

.. currentmodule:: trio.abc

.. autoclass:: trio.abc.SendStream
   :members:
   :show-inheritance:

.. autoclass:: trio.abc.ReceiveStream
   :members:
   :show-inheritance:

.. autoclass:: trio.abc.Stream
   :members:
   :show-inheritance:

.. autoclass:: trio.abc.HalfCloseableStream
   :members:
   :show-inheritance:

.. currentmodule:: trio.abc

.. autoclass:: trio.abc.Listener
   :members:
   :show-inheritance:

.. autoclass:: trio.abc.SendChannel
   :members:
   :show-inheritance:

.. autoclass:: trio.abc.ReceiveChannel
   :members:
   :show-inheritance:

.. autoclass:: trio.abc.Channel
   :members:
   :show-inheritance:

.. currentmodule:: trio


通用流工具
~~~~~~~~~~~~~~~~~~~~

**Generic stream tools**

.. tab:: 中文

   Trio 目前提供了一个通用的助手, 用于编写监听连接的服务器, 使用一个或多个 :class:`~trio.abc.Listener`\s, 并且提供了一个通用的工具类, 用于处理流。如果你想测试针对流接口编写的代码, 应该查看 :mod:`trio.testing` 中的 :ref:`testing-streams`。

   .. autofunction:: serve_listeners

   .. autoclass:: StapledStream
      :members:
      :show-inheritance:

.. tab:: 英文

   Trio currently provides a generic helper for writing servers that
   listen for connections using one or more
   :class:`~trio.abc.Listener`\s, and a generic utility class for working
   with streams. And if you want to test code that's written against the
   streams interface, you should also check out :ref:`testing-streams` in
   :mod:`trio.testing`.

   .. autofunction:: serve_listeners
      :no-index:

   .. autoclass:: StapledStream
      :no-index:
      :members:
      :show-inheritance:


.. _high-level-networking:

套接字和网络
~~~~~~~~~~~~~~~~~~~~~~

**Sockets and networking**

.. tab:: 中文

   高级网络接口是建立在我们的流抽象之上的。

   .. autofunction:: open_tcp_stream

   .. autofunction:: serve_tcp

   .. autofunction:: open_ssl_over_tcp_stream

   .. autofunction:: serve_ssl_over_tcp

   .. autofunction:: open_unix_socket

   .. autoclass:: SocketStream
      :members:
      :undoc-members:
      :show-inheritance:

   .. autoclass:: SocketListener
      :members:
      :show-inheritance:

   .. autofunction:: open_tcp_listeners

   .. autofunction:: open_ssl_over_tcp_listeners

.. tab:: 英文

   The high-level network interface is built on top of our stream
   abstraction.

   .. autofunction:: open_tcp_stream
      :no-index:

   .. autofunction:: serve_tcp
      :no-index:

   .. autofunction:: open_ssl_over_tcp_stream
      :no-index:

   .. autofunction:: serve_ssl_over_tcp
      :no-index:

   .. autofunction:: open_unix_socket
      :no-index:

   .. autoclass:: SocketStream
      :no-index:
      :members:
      :undoc-members:
      :show-inheritance:

   .. autoclass:: SocketListener
      :no-index:
      :members:
      :show-inheritance:

   .. autofunction:: open_tcp_listeners
      :no-index:

   .. autofunction:: open_ssl_over_tcp_listeners
      :no-index:


SSL / TLS 支持
~~~~~~~~~~~~~~~~~

**SSL / TLS support**

.. tab:: 中文

   Trio 提供了基于标准库 :mod:`ssl` 模块的 SSL/TLS 支持。Trio 的 :class:`SSLStream` 和 :class:`SSLListener` 从 :class:`ssl.SSLContext` 获取其配置, 您可以使用 :func:`ssl.create_default_context` 创建该上下文, 并使用 :mod:`ssl` 模块中的其他常量和函数进行自定义。

   .. warning:: 避免直接实例化 `ssl.SSLContext`。
      新创建的 :class:`ssl.SSLContext` 的默认配置不如通过 :func:`ssl.create_default_context` 返回的上下文安全。

   您可以通过创建 :class:`SSLStream` 来代替使用 :meth:`ssl.SSLContext.wrap_socket`：

   .. autoclass:: SSLStream
      :show-inheritance:
      :members:

   如果您正在实现一个服务器, 您可以使用 :class:`SSLListener`：

   .. autoclass:: SSLListener
      :show-inheritance:
      :members:

   在 :class:`SSLStream` 上的某些方法如果在握手完成之前调用, 将会引发 :exc:`NeedHandshakeError`：

   .. autoexception:: NeedHandshakeError

.. tab:: 英文

   Trio provides SSL/TLS support based on the standard library :mod:`ssl`
   module. Trio's :class:`SSLStream` and :class:`SSLListener` take their
   configuration from a :class:`ssl.SSLContext`, which you can create
   using :func:`ssl.create_default_context` and customize using the
   other constants and functions in the :mod:`ssl` module.

   .. warning:: Avoid instantiating :class:`ssl.SSLContext` directly.
      A newly constructed :class:`~ssl.SSLContext` has less secure
      defaults than one returned by :func:`ssl.create_default_context`.

   Instead of using :meth:`ssl.SSLContext.wrap_socket`, you
   create a :class:`SSLStream`:

   .. autoclass:: SSLStream
      :no-index:
      :show-inheritance:
      :members:

   And if you're implementing a server, you can use :class:`SSLListener`:

   .. autoclass:: SSLListener
      :no-index:
      :show-inheritance:
      :members:

   Some methods on :class:`SSLStream` raise :exc:`NeedHandshakeError` if
   you call them before the handshake completes:

   .. autoexception:: NeedHandshakeError
      :no-index:


数据报 TLS 支持
~~~~~~~~~~~~~~~~~~~~

**Datagram TLS support**

.. tab:: 中文

   Trio 还支持数据报 TLS (DTLS ) , 它类似于 TLS, 但用于不可靠的 UDP 连接。对于那些 TCP 的可靠顺序交付存在问题的应用程序, 如视频会议, 延迟敏感的游戏和 VPN, 这非常有用。

   目前, 使用 DTLS 与 Trio 需要 PyOpenSSL。我们希望最终能够使用标准库的 `ssl` 模块, 但不幸的是, 目前尚不可能。

   .. warning:: 请注意, PyOpenSSL 在许多方面比 `ssl` 模块更底层——尤其是, 它当前 **没有内置的机制来验证证书**。我们 *强烈* 推荐您使用 `service-identity
      <https://pypi.org/project/service-identity/>`__ 库来验证主机名和证书。

   .. autoclass:: DTLSEndpoint

      .. automethod:: connect

      .. automethod:: serve

      .. automethod:: close

   .. autoclass:: DTLSChannel
      :show-inheritance:

      .. automethod:: do_handshake

      .. automethod:: send

      .. automethod:: receive

      .. automethod:: close

      .. automethod:: aclose

      .. automethod:: set_ciphertext_mtu

      .. automethod:: get_cleartext_mtu

      .. automethod:: statistics

   .. autoclass:: DTLSChannelStatistics
      :members:

.. tab:: 英文

   Trio also has support for Datagram TLS (DTLS), which is like TLS but
   for unreliable UDP connections. This can be useful for applications
   where TCP's reliable in-order delivery is problematic, like
   teleconferencing, latency-sensitive games, and VPNs.

   Currently, using DTLS with Trio requires PyOpenSSL. We hope to
   eventually allow the use of the stdlib `ssl` module as well, but
   unfortunately that's not yet possible.

   .. warning:: Note that PyOpenSSL is in many ways lower-level than the
      `ssl` module – in particular, it currently **HAS NO BUILT-IN
      MECHANISM TO VALIDATE CERTIFICATES**. We *strongly* recommend that
      you use the `service-identity
      <https://pypi.org/project/service-identity/>`__ library to validate
      hostnames and certificates.

   .. autoclass:: DTLSEndpoint
      :no-index:

      .. automethod:: connect
         :no-index:

      .. automethod:: serve
         :no-index:

      .. automethod:: close
         :no-index:

   .. autoclass:: DTLSChannel
      :no-index:
      :show-inheritance:

      .. automethod:: do_handshake
         :no-index:

      .. automethod:: send
         :no-index:

      .. automethod:: receive
         :no-index:

      .. automethod:: close
         :no-index:

      .. automethod:: aclose
         :no-index:

      .. automethod:: set_ciphertext_mtu
         :no-index:

      .. automethod:: get_cleartext_mtu
         :no-index:

      .. automethod:: statistics
         :no-index:

   .. autoclass:: DTLSChannelStatistics
      :no-index:
      :members:

.. module:: trio.socket

使用 :mod:`trio.socket` 进行低级网络
---------------------------------------------

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
~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~

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


   .. currentmodule:: trio


.. _async-file-io:

异步文件系统 I/O
---------------------------

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~

**Asynchronous path objects**

.. autoclass:: Path
   :members:
   :inherited-members:

.. autoclass:: PosixPath

.. autoclass:: WindowsPath


.. _async-file-objects:

异步文件对象
~~~~~~~~~~~~~~~~~~~~~~~~~

**Asynchronous file objects**

.. 在此处抑制类型注释, 它们涉及许多内部类型。
   普通的 Python 文档对此有更详细的描述。

.. Suppress type annotations here, they refer to lots of internal types.
   The normal Python docs go into better detail.

.. tab:: 中文

   .. autofunction:: open_file(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=None, opener=None)

   .. autofunction:: wrap_file(file)

   .. interface:: Asynchronous file interface(异步文件接口)

      Trio 的异步文件对象具有一个接口, 该接口会自动适应被包装的对象。直观地说, 您可以将它们像常规的 :term:`文件对象 <file object>` 一样使用, 只是在执行 I/O 的任何方法前添加 ``await``。不过, Python 中的 :term:`文件对象` 定义有点模糊, 因此这里列出了具体细节：

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


.. _subprocess:

生成子进程
---------------------

**Spawning subprocesses**

.. tab:: 中文

   Trio 提供了支持生成其他程序作为子进程、通过管道与它们通信、发送信号并等待它们退出的功能。

   大多数情况下，这通过我们的高级接口 :func:`trio.run_process` 来完成。它允许您运行一个进程直到完成，同时可选地捕获输出，或者将其运行在后台任务中，并在进程运行时与之交互：

   .. autofunction:: trio.run_process

   .. autoclass:: trio._subprocess.HasFileno(Protocol)

      .. automethod:: fileno

   .. autoclass:: trio._subprocess.StrOrBytesPath

   .. autoclass:: trio.Process()

      .. autoattribute:: returncode

      .. automethod:: wait

      .. automethod:: poll

      .. automethod:: kill

      .. automethod:: terminate

      .. automethod:: send_signal

      .. note:: :meth:`~subprocess.Popen.communicate` 不是 :class:`~trio.Process` 对象上的方法；对于简单的捕获，正常调用 :func:`~trio.run_process`，或者如果您有特殊需求，可以自己编写循环。 :meth:`~subprocess.Popen.communicate` 在标准库中有非常不寻常的取消行为（在某些平台上，它会生成一个后台线程，在超时过期后仍然继续从子进程读取），我们希望提供一个更少惊讶的接口。

   如果 :func:`trio.run_process` 太有限制，我们还提供了一个低级 API， :func:`trio.lowlevel.open_process`。例如，如果您想生成一个将比父进程生命周期更长并且会成为孤儿的子进程，那么 :func:`~trio.run_process` 做不到这一点，但 :func:`~trio.lowlevel.open_process` 可以。

.. tab:: 英文

   Trio provides support for spawning other programs as subprocesses,
   communicating with them via pipes, sending them signals, and waiting
   for them to exit.

   Most of the time, this is done through our high-level interface,
   :func:`trio.run_process`. It lets you either run a process to completion
   while optionally capturing the output, or else run it in a background
   task and interact with it while it's running:

   .. autofunction:: trio.run_process
      :no-index:

   .. autoclass:: trio._subprocess.HasFileno(Protocol)
      :no-index:

      .. automethod:: fileno
         :no-index:

   .. autoclass:: trio._subprocess.StrOrBytesPath
      :no-index:

   .. autoclass:: trio.Process()
      :no-index:

      .. autoattribute:: returncode
         :no-index:

      .. automethod:: wait
         :no-index:

      .. automethod:: poll
         :no-index:

      .. automethod:: kill
         :no-index:

      .. automethod:: terminate
         :no-index:

      .. automethod:: send_signal
         :no-index:

      .. note:: :meth:`~subprocess.Popen.communicate` is not provided as a
         method on :class:`~trio.Process` objects; call :func:`~trio.run_process`
         normally for simple capturing, or write the loop yourself if you
         have unusual needs. :meth:`~subprocess.Popen.communicate` has
         quite unusual cancellation behavior in the standard library (on
         some platforms it spawns a background thread which continues to
         read from the child process even after the timeout has expired)
         and we wanted to provide an interface with fewer surprises.

   If `trio.run_process` is too limiting, we also offer a low-level API,
   `trio.lowlevel.open_process`. For example, if you want to spawn a
   child process that will outlive the parent process and be
   orphaned, then `~trio.run_process` can't do that, but
   `~trio.lowlevel.open_process` can.


.. _subprocess-options:

启动子进程的选项
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Options for starting subprocesses**

.. tab:: 中文

   Trio 的所有子进程 API 都接受标准 :mod:`subprocess` 模块使用的众多关键字参数，用于控制进程启动的环境以及与之通信的机制。这些参数可以在以下文档中看到 ``**options`` 时传递。请参见 :mod:`subprocess` 文档中的 `完整列表 <https://docs.python.org/3/library/subprocess.html#popen-constructor>`__ 或者 `常用参数 <https://docs.python.org/3/library/subprocess.html#frequently-used-arguments>`__ 。（您可能需要 ``import subprocess`` 才能访问像 ``PIPE`` 或 ``DEVNULL`` 这样的常量。）

   目前，Trio 始终使用无缓冲的字节流与进程通信，因此不支持 ``encoding``、 ``errors``、``universal_newlines`` （别名 ``text`` ）和 ``bufsize`` 选项。

.. tab:: 英文

   All of Trio's subprocess APIs accept the numerous keyword arguments used
   by the standard :mod:`subprocess` module to control the environment in
   which a process starts and the mechanisms used for communicating with
   it.  These may be passed wherever you see ``**options`` in the
   documentation below.  See the `full list
   <https://docs.python.org/3/library/subprocess.html#popen-constructor>`__
   or just the `frequently used ones
   <https://docs.python.org/3/library/subprocess.html#frequently-used-arguments>`__
   in the :mod:`subprocess` documentation. (You may need to ``import
   subprocess`` in order to access constants such as ``PIPE`` or
   ``DEVNULL``.)

   Currently, Trio always uses unbuffered byte streams for communicating
   with a process, so it does not support the ``encoding``, ``errors``,
   ``universal_newlines`` (alias ``text``), and ``bufsize``
   options.


.. _subprocess-quoting:

引用：比您想知道的更多
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Quoting: more than you wanted to know**

.. tab:: 中文

   Trio 的子进程 API 通常需要将要运行的命令及其参数作为字符串序列传递，其中序列的第一个元素指定要运行的命令，剩余的元素指定命令的参数，每个参数占一个元素。采用这种形式是因为它可以避免潜在的引号陷阱；例如，你可以运行 ``["cp", "-f", source_file, dest_file]``，而无需担心 ``source_file`` 或 ``dest_file`` 是否包含空格。

   如果你只在 UNIX 上运行不使用 ``shell=True`` 的子进程，那么指定命令时只需知道这些。如果你使用 ``shell=True`` 或在 Windows 上运行，可能需要阅读本节的其余部分，以便了解潜在的陷阱。

   在 UNIX 上使用 ``shell=True`` 时，必须将命令指定为一个单一字符串，这个字符串将被传递给 shell，类似于你在交互式提示符下输入的方式。这个选项的优点是它允许你使用 shell 功能，比如管道和重定向，而不需要编写处理它们的代码。例如，你可以写 ``Process("ls | grep some_string", shell=True)``。缺点是你必须考虑到 shell 的引用规则，通常需要通过 :func:`shlex.quote` 来包装可能包含空格、引号或其他 shell 元字符的任何参数。如果你不这样做，那么看似安全的 ``f"ls | grep {some_string}"`` 在调用时，若 ``some_string = "foo; rm -rf /"``，可能会导致灾难。

   在 Windows 上，进程生成的基本 API（``CreateProcess()`` 系统调用）接受一个字符串而不是列表，实际上是子进程决定如何将这个字符串拆分为单独的参数。由于 C 语言规定 ``main()`` 应该接受一个参数列表，*大多数* 你遇到的程序将遵循 Microsoft C/C++ 运行时使用的规则。:class:`subprocess.Popen`，因此 Trio 也使用这些规则将参数序列转换为字符串，这些规则在 :mod:`subprocess` 模块中有 `文档记录 <https://docs.python.org/3/library/subprocess.html#converting-argument-sequence>`__。没有文档化的 Python 标准库函数可以直接执行该转换，因此即使在 Windows 上，你几乎总是需要传递参数序列而不是字符串。但如果你启动的程序不能按标准方式将命令行拆分回单独的参数，那么你可能需要传递一个字符串来解决这个问题。（或者你可能只是运气不好：据我所知，Windows 批处理文件没有办法传递包含双引号的参数。）

   在 Windows 上使用 ``shell=True`` 时，情况变得更加混乱。现在，有两个独立的引用规则应用：一个由 Windows 命令 shell ``CMD.EXE`` 使用，另一个由被启动的进程使用，而且它们是 *不同的*。（而且没有 :func:`shlex.quote` 来帮助你：它使用 UNIX 风格的引用规则，即使在 Windows 上也是如此。）大多数由 shell 解释的特殊字符 ``&<>()^|`` 如果 shell 认为它们在双引号内，则不被视为特殊字符，但 ``%FOO%`` 环境变量替换仍然有效，而且 shell 没有提供在双引号字符串内写入双引号的办法。双引号外部，任何字符（包括双引号）都可以使用前导 ``^`` 来转义。但由于管道通过在子 shell 中运行每个命令来处理，因此可能需要多层转义：

   .. code-block:: sh

      echo ^^^&x | find "x" | find "x"          # prints: &x

   如果你将管道与 ``()`` 分组结合使用，可能需要更多层的转义：

   .. code-block:: sh

      (echo ^^^^^^^&x | find "x") | find "x"    # prints: &x

   由于进程创建接受一个字符串参数，``CMD.EXE`` 的引用规则不会影响单词拆分，并且在 ``CMD.EXE`` 扩展过程中不会删除双引号。双引号很麻烦，因为 ``CMD.EXE`` 处理它们的方式与 MSVC 运行时规则不同；例如：

   .. code-block:: sh

      prog.exe "foo \"bar\" baz"

   程序会看到一个参数 ``foo "bar" baz``，但 ``CMD.EXE`` 认为 ``bar\`` 没有被引用，而 ``foo \`` 和 ``baz`` 被认为是引用的。所有这些使得在 Windows 上可靠地插入任何内容到 ``shell=True`` 命令行中变得非常困难，Trio 退回到 :mod:`subprocess` 的行为：如果你传递一个包含 ``shell=True`` 的序列，它会像 ``shell=False`` 一样进行引用，并且最好不要包含你未计划使用的任何 shell 元字符。

   进一步阅读：

   * https://stackoverflow.com/questions/30620876/how-to-properly-escape-filenames-in-windows-cmd-exe

   * https://stackoverflow.com/questions/4094699/how-does-the-windows-command-interpreter-cmd-exe-parse-scripts

.. tab:: 英文

   The command to run and its arguments usually must be passed to Trio's
   subprocess APIs as a sequence of strings, where the first element in
   the sequence specifies the command to run and the remaining elements
   specify its arguments, one argument per element. This form is used
   because it avoids potential quoting pitfalls; for example, you can run
   ``["cp", "-f", source_file, dest_file]`` without worrying about
   whether ``source_file`` or ``dest_file`` contains spaces.

   If you only run subprocesses without ``shell=True`` and on UNIX,
   that's all you need to know about specifying the command. If you use
   ``shell=True`` or run on Windows, you probably should read the
   rest of this section to be aware of potential pitfalls.

   With ``shell=True`` on UNIX, you must specify the command as a single
   string, which will be passed to the shell as if you'd entered it at an
   interactive prompt. The advantage of this option is that it lets you
   use shell features like pipes and redirection without writing code to
   handle them. For example, you can write ``Process("ls | grep
   some_string", shell=True)``.  The disadvantage is that you must
   account for the shell's quoting rules, generally by wrapping in
   :func:`shlex.quote` any argument that might contain spaces, quotes, or
   other shell metacharacters.  If you don't do that, your safe-looking
   ``f"ls | grep {some_string}"`` might end in disaster when invoked with
   ``some_string = "foo; rm -rf /"``.

   On Windows, the fundamental API for process spawning (the
   ``CreateProcess()`` system call) takes a string, not a list, and it's
   actually up to the child process to decide how it wants to split that
   string into individual arguments. Since the C language specifies that
   ``main()`` should take a list of arguments, *most* programs you
   encounter will follow the rules used by the Microsoft C/C++ runtime.
   :class:`subprocess.Popen`, and thus also Trio, uses these rules
   when it converts an argument sequence to a string, and they
   are `documented
   <https://docs.python.org/3/library/subprocess.html#converting-argument-sequence>`__
   alongside the :mod:`subprocess` module. There is no documented
   Python standard library function that can directly perform that
   conversion, so even on Windows, you almost always want to pass an
   argument sequence rather than a string. But if the program you're
   spawning doesn't split its command line back into individual arguments
   in the standard way, you might need to pass a string to work around this.
   (Or you might just be out of luck: as far as I can tell, there's simply
   no way to pass an argument containing a double-quote to a Windows
   batch file.)

   On Windows with ``shell=True``, things get even more chaotic. Now
   there are two separate sets of quoting rules applied, one by the
   Windows command shell ``CMD.EXE`` and one by the process being
   spawned, and they're *different*. (And there's no :func:`shlex.quote`
   to save you: it uses UNIX-style quoting rules, even on Windows.)  Most
   special characters interpreted by the shell ``&<>()^|`` are not
   treated as special if the shell thinks they're inside double quotes,
   but ``%FOO%`` environment variable substitutions still are, and the
   shell doesn't provide any way to write a double quote inside a
   double-quoted string. Outside double quotes, any character (including
   a double quote) can be escaped using a leading ``^``.  But since a
   pipeline is processed by running each command in the pipeline in a
   subshell, multiple layers of escaping can be needed:

   .. code-block:: sh

      echo ^^^&x | find "x" | find "x"          # prints: &x

   And if you combine pipelines with () grouping, you can need even more
   levels of escaping:

   .. code-block:: sh

      (echo ^^^^^^^&x | find "x") | find "x"    # prints: &x

   Since process creation takes a single arguments string, ``CMD.EXE``\'s
   quoting does not influence word splitting, and double quotes are not
   removed during CMD.EXE's expansion pass. Double quotes are troublesome
   because CMD.EXE handles them differently from the MSVC runtime rules; in:

   .. code-block:: sh

      prog.exe "foo \"bar\" baz"

   the program will see one argument ``foo "bar" baz`` but CMD.EXE thinks
   ``bar\`` is not quoted while ``foo \`` and ``baz`` are. All of this
   makes it a formidable task to reliably interpolate anything into a
   ``shell=True`` command line on Windows, and Trio falls back on the
   :mod:`subprocess` behavior: If you pass a sequence with
   ``shell=True``, it's quoted in the same way as a sequence with
   ``shell=False``, and had better not contain any shell metacharacters
   you weren't planning on.

   Further reading:

   * https://stackoverflow.com/questions/30620876/how-to-properly-escape-filenames-in-windows-cmd-exe

   * https://stackoverflow.com/questions/4094699/how-does-the-windows-command-interpreter-cmd-exe-parse-scripts


信号
-------

**Signals**

.. currentmodule:: trio

.. autofunction:: open_signal_receiver
   :with: signal_aiter
