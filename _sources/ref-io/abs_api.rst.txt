.. currentmodule:: trio


.. _abstract-stream-api:

抽象流 API
===========

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
---------------------

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
     - :class:`~trio.MemorySendChannel`
   * - :class:`ReceiveChannel`
     - :class:`AsyncResource`
     - :meth:`~ReceiveChannel.receive`
     - ``__aiter__``, ``__anext__``
     - :class:`~trio.MemoryReceiveChannel`
   * - :class:`Channel`
     - :class:`SendChannel`, :class:`ReceiveChannel`
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
--------------------

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
----------------------

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
-----------------

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
--------------------

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
      :show-inheritance:
      :no-index:

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