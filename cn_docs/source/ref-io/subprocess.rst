.. currentmodule:: trio

.. _subprocess:

生成子进程
=============

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
---------------------------------

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
-------------------------------------

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