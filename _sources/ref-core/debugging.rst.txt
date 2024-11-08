.. _interactive debugging:


交互式调试
---------------------

**Interactive debugging**

.. tab:: 中文

   当你启动一个交互式 Python 会话来调试任何异步程序（无论是基于 ``asyncio`` 、Trio 还是其他框架），每个 `await` 表达式都需要在异步函数内：

   .. code-block:: console

      $ python
      Python 3.10.6
      Type "help", "copyright", "credits" or "license" for more information.
      >>> import trio
      >>> await trio.sleep(1)
      File "<stdin>", line 1
      SyntaxError: 'await' outside function
      >>> async def main():
      ...     print("hello...")
      ...     await trio.sleep(1)
      ...     print("world!")
      ...
      >>> trio.run(main)
      hello...
      world!

   这可能会让你很难快速迭代，因为每次进行修改时，你都必须重新定义整个函数体。

   Trio 提供了一个修改过的交互式控制台，允许你在顶层直接使用 ``await``。你可以通过运行 ``python -m trio`` 来访问这个控制台：

   .. code-block:: console

      $ python -m trio
      Trio 0.21.0+dev, Python 3.10.6
      Use "await" directly instead of "trio.run()".
      Type "help", "copyright", "credits" or "license" for more information.
      >>> import trio
      >>> print("hello..."); await trio.sleep(1); print("world!")
      hello...
      world!

   如果你是 IPython 用户，你可以使用 IPython 的 `autoawait
   <https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-autoawait>`__
   功能。你可以通过在 IPython shell 中运行魔法命令 ``%autoawait trio`` 来启用它。要在每次安装 Trio 时都启用 ``autoawait``，你可以将以下内容添加到你的 IPython 启动文件中。
   （例如 ``~/.ipython/profile_default/startup/10-async.py``）

   .. code-block::

      try:
         import trio
         get_ipython().run_line_magic("autoawait", "trio")
      except ImportError:
         pass

.. tab:: 英文

   When you start an interactive Python session to debug any async program
   (whether it's based on ``asyncio``, Trio, or something else), every await
   expression needs to be inside an async function:

   .. code-block:: console

      $ python
      Python 3.10.6
      Type "help", "copyright", "credits" or "license" for more information.
      >>> import trio
      >>> await trio.sleep(1)
      File "<stdin>", line 1
      SyntaxError: 'await' outside function
      >>> async def main():
      ...     print("hello...")
      ...     await trio.sleep(1)
      ...     print("world!")
      ...
      >>> trio.run(main)
      hello...
      world!

   This can make it difficult to iterate quickly since you have to redefine the
   whole function body whenever you make a tweak.

   Trio provides a modified interactive console that lets you ``await`` at the top
   level. You can access this console by running ``python -m trio``:

   .. code-block:: console

      $ python -m trio
      Trio 0.21.0+dev, Python 3.10.6
      Use "await" directly instead of "trio.run()".
      Type "help", "copyright", "credits" or "license" for more information.
      >>> import trio
      >>> print("hello..."); await trio.sleep(1); print("world!")
      hello...
      world!

   If you are an IPython user, you can use IPython's `autoawait
   <https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-autoawait>`__
   function. This can be enabled within the IPython shell by running the magic command
   ``%autoawait trio``. To have ``autoawait`` enabled whenever Trio installed, you can
   add the following to your IPython startup files.
   (e.g. ``~/.ipython/profile_default/startup/10-async.py``)

   .. code-block::

      try:
         import trio
         get_ipython().run_line_magic("autoawait", "trio")
      except ImportError:
         pass