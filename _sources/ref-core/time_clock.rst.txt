.. module:: trio

.. _time-and-clocks:

时间和时钟
---------------

**Time and clocks**

.. tab:: 中文

   每次调用 :func:`run` 都会关联一个时钟。

   默认情况下，Trio 使用一个未指定的单调时钟，但可以通过将自定义时钟对象传递给 :func:`run` 来更改（例如用于测试）。

   您不应假设 Trio 的内部时钟与您可以访问的任何其他时钟匹配，包括在其他进程或线程中同时调用 :func:`trio.run` 的时钟！

   当前默认时钟实现为 :func:`time.perf_counter` 加上一个大的随机偏移量。这样做的目的是捕捉到那些不小心过早使用 :func:`time.perf_counter` 的代码，这有助于保持我们将来 `更改时钟实现的选项
   <https://github.com/python-trio/trio/issues/33>`__，并且（更重要的是）确保您可以确信，像 :class:`trio.testing.MockClock` 这样的自定义时钟将在您无法控制的第三方库中正常工作。

   .. autofunction:: trio.current_time

   .. autofunction:: trio.sleep  
      
   .. autofunction:: trio.sleep_until  

   .. autofunction:: trio.sleep_forever

   如果您是个疯狂的科学家，或者出于其他原因，觉得有必要直接控制 时间的流逝本身，那么您可以实现一个自定义的 :class:`~trio.abc.Clock` 类：

   .. autoclass:: trio.abc.Clock
      :members:

.. tab:: 英文

   Every call to :func:`run` has an associated clock.

   By default, Trio uses an unspecified monotonic clock, but this can be
   changed by passing a custom clock object to :func:`run` (e.g. for
   testing).

   You should not assume that Trio's internal clock matches any other
   clock you have access to, including the clocks of simultaneous calls
   to :func:`trio.run` happening in other processes or threads!

   The default clock is currently implemented as :func:`time.perf_counter`
   plus a large random offset. The idea here is to catch code that
   accidentally uses :func:`time.perf_counter` early, which should help keep
   our options open for `changing the clock implementation later
   <https://github.com/python-trio/trio/issues/33>`__, and (more importantly)
   make sure you can be confident that custom clocks like
   :class:`trio.testing.MockClock` will work with third-party libraries
   you don't control.

   .. autofunction:: trio.current_time
      :no-index:

   .. autofunction:: trio.sleep  
      :no-index:

   .. autofunction:: trio.sleep_until  
      :no-index:

   .. autofunction:: trio.sleep_forever
      :no-index:

   If you're a mad scientist or otherwise feel the need to take direct
   control over the PASSAGE OF TIME ITSELF, then you can implement a
   custom :class:`~trio.abc.Clock` class:

   .. autoclass:: trio.abc.Clock
      :no-index:
      :members:
