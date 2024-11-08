设计和内部结构
====================

**Design and internals**

.. currentmodule:: trio

.. tab:: 中文

   在这里，我们将讨论 Trio 的整体设计和架构：它是如何结合在一起的，以及我们做出这些决策的原因。如果你只是想使用 Trio，那么你不需要阅读这一部分——尽管你可能会觉得它很有趣。本节的主要目标读者是：(a) 想要阅读代码并可能贡献代码的人，(b) 希望了解我们正在做什么的类似库开发者，(c) 对 I/O 库设计感兴趣的任何人。

   编写异步 I/O 库有许多有效的方式。这是我们的方式。


.. tab:: 英文

   Here we'll discuss Trio's overall design and architecture: how it fits
   together and why we made the decisions we did. If all you want to do
   is use Trio, then you don't need to read this – though you might find
   it interesting. The main target audience here is (a) folks who want to
   read the code and potentially contribute, (b) anyone working on
   similar libraries who want to understand what we're up to, (c) anyone
   interested in I/O library design generally.

   There are many valid approaches to writing an async I/O library. This
   is ours.


高级设计原则
----------------------------

**High-level design principles**

.. tab:: 中文

    Trio 的两个主要目标是 **可用性** 和 **正确性**：我们希望让你 *轻松* 地做到 *正确*。

    当然，还有许多其他重要因素，如速度、可维护性等。我们也希望尽可能地达到这些目标。但有时这些目标之间会发生冲突，而在这种情况下，以上两个目标是我们的优先事项。

    从某种意义上讲，本文件的其余部分都在描述这些目标是如何实现的，但举个简单的例子: Trio 的 ``KeyboardInterrupt`` 处理机制有点复杂且难以测试，因此它在简单性和可维护性方面评分较低。但我们认为，可用性+正确性的提升弥补了这一点。

    这里有一些细微之处。注意到我们特别强调“让事情变得容易正确”。有些情况下（例如编写一次性的脚本），最“易用”的工具可能是那个会无视错误并继续执行的工具，或者不处理资源清理的工具。（参见 PHP 的成功案例。）这是一个完全有效的用例和可用性的定义，但这不是我们使用的定义：我们认为，如果异常传播直到被处理，如果系统在你犯下可能危险的资源处理错误时能够 `捕获你 <https://github.com/python-trio/trio/issues/265>`__，那么构建可靠且正确的系统会更容易，因此我们会优化这个目标。

    也值得谈谈速度，因为在 I/O 库的比较中，速度通常是一个重要因素。这是一个相当微妙且复杂的话题。

    通常来说，速度当然很重要——但是人们有时选择使用 Python 而不是 C，实际上已经很好地表明了在实践中，可用性往往比速度更重要。我们希望让 Trio 快，但它没有出现在我们上面列出的主要目标中，这不是巧合：如果需要的话，我们愿意为可用性和可靠性牺牲一些速度。

    更详细地分解：

    首先，存在一些速度直接影响正确性的情况，比如你不小心写了一个 ``O(N**2)`` 的算法，导致程序实际上被锁住。Trio 非常小心地使用具有良好最坏情况表现的算法和数据结构（即使这可能意味着在平均情况下牺牲几个百分点的速度）。

    同样，当发生冲突时，我们更关心的是 99 百分位的延迟，而不是原始吞吐量，因为不足的吞吐量——如果是一致的！——通常可以通过水平扩展来预算和处理，但一旦丧失延迟，它就永远消失了，而且延迟激增很容易变成一个正确性问题（例如，一个 RPC 服务器响应慢到触发超时，它实际上就不能用了）。当然，这并不意味着我们不关心吞吐量——但有时工程需要做出取舍，特别是对于还没有时间为所有用例进行优化的早期项目。

    最后：我们确实非常关心真实世界应用中的速度，但微基准测试中的速度几乎是我们最低的优先级。我们不想参与构建“西部最快的回显服务器”之类的比赛。我的意思是，如果它发生了也不错，微基准测试是理解系统行为的宝贵工具。但如果你为了赢得这个游戏而去做，那就很容易陷入一个严重的不匹配激励的局面，在这种局面中，你必须为了获得一个对真实应用毫无意义的速度提升而开始妥协功能和正确性。在大多数情况下（我们怀疑），是应用代码成为了瓶颈，你通过在 PyPy 下运行整个应用程序，获得的收益可能比对 I/O 层做任何英雄式的优化更大。（这也是为什么 Trio *确实* 优先考虑 PyPy 兼容性的原因。）

    作为一种策略，我们还注意到，在 Trio 的生命周期的这个阶段，过于关注速度可能是个错误。花大量精力优化一个语义仍在变化的 API 是不明智的。

.. tab:: 英文

    Trio's two overriding goals are **usability** and **correctness**: we
    want to make it *easy* to get things *right*.

    Of course there are lots of other things that matter too, like speed,
    maintainability, etc. We want those too, as much as we can get. But
    sometimes these things come in conflict, and when that happens, these
    are our priorities.

    In some sense the entire rest of this document is a description of how
    these play out, but to give a simple example: Trio's
    ``KeyboardInterrupt`` handling machinery is a bit tricky and hard to
    test, so it scores poorly on simplicity and maintainability. But we
    think the usability+correctness gains outweigh this.

    There are some subtleties here. Notice that it's specifically "easy to
    get things right". There are situations (e.g. writing one-off scripts)
    where the most "usable" tool is the one that will happily ignore
    errors and keep going no matter what, or that doesn't bother with
    resource cleanup. (Cf. the success of PHP.) This is a totally valid
    use case and valid definition of usability, but it's not the one we
    use: we think it's easier to build reliable and correct systems if
    exceptions propagate until handled and if the system `catches you when
    you make potentially dangerous resource handling errors
    <https://github.com/python-trio/trio/issues/265>`__, so that's what we
    optimize for.

    It's also worth saying something about speed, since it often looms
    large in comparisons between I/O libraries. This is a rather subtle
    and complex topic.

    In general, speed is certainly important – but the fact that people
    sometimes use Python instead of C is a pretty good indicator that
    usability often trumps speed in practice. We want to make Trio fast,
    but it's not an accident that it's left off our list of overriding
    goals at the top: if necessary we are willing to accept some slowdowns
    in the service of usability and reliability.

    To break things down in more detail:

    First of all, there are the cases where speed directly impacts
    correctness, like when you hit an accidental ``O(N**2)`` algorithm and
    your program effectively locks up. Trio is very careful to use
    algorithms and data structures that have good worst-case behavior
    (even if this might mean sacrificing a few percentage points of speed
    in the average case).

    Similarly, when there's a conflict, we care more about 99th percentile
    latencies than we do about raw throughput, because insufficient
    throughput – if it's consistent! – can often be budgeted for and
    handled with horizontal scaling, but once you lose latency it's gone
    forever, and latency spikes can easily cross over to become a
    correctness issue (e.g., an RPC server that responds slowly enough to
    trigger timeouts is effectively non-functional). Again, of course,
    this doesn't mean we don't care about throughput – but sometimes
    engineering requires making trade-offs, especially for early-stage
    projects that haven't had time to optimize for all use cases yet.

    And finally: we care about speed on real-world applications quite a
    bit, but speed on microbenchmarks is just about our lowest
    priority. We aren't interested in competing to build "the fastest echo
    server in the West". I mean, it's nice if it happens or whatever, and
    microbenchmarks are an invaluable tool for understanding a system's
    behavior. But if you play that game to win then it's very easy to get
    yourself into a situation with seriously misaligned incentives, where
    you have to start compromising on features and correctness in order to
    get a speedup that's totally irrelevant to real-world applications. In
    most cases (we suspect) it's the application code that's the
    bottleneck, and you'll get more of a win out of running the whole app
    under PyPy than out of any heroic optimizations to the I/O
    layer. (And this is why Trio *does* place a priority on PyPy
    compatibility.)

    As a matter of tactics, we also note that at this stage in Trio's
    lifecycle, it'd probably be a mistake to worry about speed too
    much. It doesn't make sense to spend lots of effort optimizing an API
    whose semantics are still in flux.


用户级 API 原则
-------------------------

**User-level API principles**

基本原则
~~~~~~~~~~~~~~~~

**Basic principles**

.. tab:: 中文

    Trio 是 `这篇博客文章 <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/>`__ 思想的延续，特别是其中提到的 `原理 <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#review-and-summing-up-what-is-async-await-native-anyway>`__，这些原理使得 Curio 比 asyncio 更容易正确使用。因此，Trio 也采纳了这些规则，特别是：

    * 唯一的并发形式是任务（task）。

    * 任务保证会执行到完成。

    * 任务的创建总是显式的。没有回调、没有隐式并发、没有 futures/deferreds/promises/其他涉及回调的 API。除非用于显式创建任务的 API，否则所有 API 都是 `"因果" <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#review-and-summing-up-what-is-async-await-native-anyway>`__。

    * 异常用于错误处理； ``try`` / ``finally`` 和 ``with`` 块用于清理处理。

.. tab:: 英文

    Trio is very much a continuation of the ideas explored in `this blog post <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/>`__, and in particular the `principles identified there <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#review-and-summing-up-what-is-async-await-native-anyway>`__ that make curio easier to use correctly than asyncio. So Trio also adopts these rules, in particular:

    * The only form of concurrency is the task.

    * Tasks are guaranteed to run to completion.

    * Task spawning is always explicit. No callbacks, no implicit concurrency, no futures/deferreds/promises/other APIs that involve callbacks. All APIs are `"causal" <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#review-and-summing-up-what-is-async-await-native-anyway>`__ except for those that are explicitly used for task spawning.

    * Exceptions are used for error handling; ``try``/``finally`` and ``with`` blocks for handling cleanup.


取消点和安排点
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cancel points and schedule points**

.. tab:: 中文

    Trio 与 Curio 的第一个重大区别在于，它决定让更多的 API 使用同步函数而非异步函数，并提供关于取消点和调度点的强大约定。（此时，Trio 和 Curio 已经有很多不同之处。但这实际上是起点——我意识到，探索这些思想需要一个新的库，而不能在 Curio 内部完成。）完整的推理需要一些解释。

    首先，一些定义：*取消点* 是代码检查是否已被取消的地方 —— 例如，由于超时过期 —— 并可能引发 :exc:`Cancelled` 异常。*调度点* 是当前任务可能会被挂起并允许其他任务运行的地方。

    在 Curio 中，约定是所有以任何方式与运行循环交互的操作都是语法上异步的，而且无法定义哪些操作是取消/调度点；用户被告知假设其中任何操作 *可能* 是取消/调度点，但除非它们实际上会阻塞，否则没有保证它们是取消/调度点。（即，某个特定调用是否作为取消/调度点在不同的 Curio 版本中可以有所不同，且还可能根据网络负载等运行时因素而变化。）

    但在使用异步库时，您需要意识到取消点和调度点是有充分理由的。它们为您的代码引入了一组复杂且部分冲突的约束：

    您需要确保每个任务定期通过一个取消点，因为否则超时将变得无效，您的代码将容易受到 DoS 攻击和其他问题的影响。因此，为了正确性，确保有足够的取消点非常重要。

    但是... 每个取消点也会增加程序中出现细微 bug 的机会，因为这是一个需要准备处理 :exc:`Cancelled` 异常并正确清理的地方。尽管我们尽力使这一过程尽可能简单，但这些清理路径往往在测试中被遗漏，并隐藏着微妙的 bug。因此，取消点越多，确保代码正确性就越难。

    类似地，您需要确保每个任务定期通过一个调度点，否则该任务可能会占用事件循环，导致其他代码无法运行，从而造成延迟峰值。因此，为了正确性，确保有足够的调度点非常重要。

    但是... 在这里也必须小心，因为每个调度点都是一个可能执行任意其他代码的地方，并可能在不知情的情况下改变程序的状态，导致经典的并发错误。因此，随着调度点的增加，`推理代码如何交错并确保其正确性变得成倍困难 <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`__。

    因此，一个异步 I/O 库的一个重要问题是：我们如何帮助用户管理这些权衡？

    Trio 的答案受到了两个进一步观察的启发：

    首先，任何时间任务阻塞（例如，因为它执行了 ``await sock.recv()`` 但没有数据可接收），都必须是一个取消点（因为如果 I/O 永远不来，我们需要能够超时），并且它必须是一个调度点（因为异步编程的整个概念就是当一个任务等待时，我们可以切换到另一个任务去完成一些有用的事情）。

    其次，一个有时充当取消/调度点、而有时不充当取消/调度点的函数，是最糟糕的两种情况的结合：你已经付出努力确保代码正确地处理了取消或交替执行，但却无法指望它能帮助满足延迟要求。

    考虑到这一点，Trio 采取了以下方法：

    规则 1：为了减少需要跟踪的概念数量，我们将取消点和调度点合并在一起。每个取消点同时也是一个调度点，反之亦然。这些在理论上和实际实现中是不同的概念，但我们将这一区别隐藏起来，以便用户只需要跟踪一个概念。

    规则 2：取消+调度点是 *静态确定* 的。Trio 原语要么 *始终* 是取消+调度点，要么 *永远* 不是取消+调度点，无论运行时条件如何。这是因为我们希望能够通过查看源代码来确定某些代码是否具有“足够”的取消/调度点。

    实际上，为了简化这一点，我们使得您甚至无需查看函数参数：每个 *函数* 要么是 *每次* 调用时的取消+调度点，要么是 *从不* 调用时的取消+调度点。

    （务实的例外：当一个 Trio 原语抛出异常时，即使它在成功返回的情况下会充当取消+调度点，仍不要求它作为取消+调度点。更多细节请参见 `issue 474 <https://github.com/python-trio/trio/issues/474>`__；基本上，要求所有异常路径都设置检查点增加了大量的实现复杂性，而对用户的好处微乎其微。）

    观察：由于阻塞总是取消+调度点，规则 2 意味着任何 *有时* 会阻塞的函数 *总是* 取消+调度点。

    这样我们就得到了许多取消+调度点：所有可能会阻塞的函数。还有其他的吗？Trio 的答案是：没有。显式添加新的点很容易（比如抛一个 ``sleep(0)`` 或类似的），但当你不希望它们时，很难去除它们。（这是一个实际问题 —— “潜在的取消点太多” 绝对是我在尝试构建类似任务监控器的东西时遇到的紧张点，`见此 <https://github.com/dabeaz/curio/issues/149#issuecomment-269745283>`__。）我们预计，大多数 Trio 程序将“足够频繁”地执行潜在阻塞操作，以产生合理的行为。所以，规则 3：*唯一* 的取消+调度点就是那些可能阻塞的操作。

    既然我们已经知道了取消+调度点的位置，接下来就是如何有效地将这一信息传达给用户。我们希望有一种方式标出可能阻塞或触发任务切换的函数类别，这样它们就可以明显地区别于不会这样做的函数。如果有某种 Python 特性，能够自然地将函数分为两类，并且可能在能够做一些奇怪事情（比如阻塞和任务切换）的函数上加上一些特殊的语法标记，那岂不是很好？多么巧合，这正是异步函数的工作方式！规则 4：在 Trio 中，只有潜在阻塞的函数才是异步的。所以例如 :meth:`Event.wait` 是异步的，但 :meth:`Event.set` 是同步的。

    总结：在实际设计空间中，虽然可能有很多选择，我们通过规定法宣布，Trio 原语中的所有这些类别是相同的：

    * 异步函数
    * 在至少某些情况下可能会阻塞的函数
    * 调用者需要准备好处理潜在的 :exc:`Cancelled` 异常的函数
    * 保证能够察觉任何挂起取消的函数
    * 需要为潜在的任务切换做好准备的函数
    * 保证在适当时进行任务切换的函数

    这需要内部做一些不小的工作 —— 使得这四个取消/调度类别对齐实际上需要相当多的精心设计，并且还需要一些技巧，以让同步和异步 API 在与运行循环交互时处于同等地位。但这一切对用户是不可见的，我们认为这在可用性和正确性方面是值得的。

    这些规则有一个例外，适用于异步上下文管理器。上下文管理器由两个操作组成 —— 进入和退出 —— 有时只有其中一个操作是潜在的阻塞操作。（示例：“``async with lock:``” 在进入时可能阻塞，但退出时永远不会；“``async with open_nursery() as ...:``” 在退出时可能阻塞，但进入时永远不会。）但是，Python 并没有“半异步”上下文管理器：要么两个操作都是异步风格的，要么都不是。在 Trio 中，我们采取务实的做法：对于这种异步上下文管理器，我们只在潜在阻塞的操作上强制执行上述规则，而允许另一个操作在语法上是 ``async``，但语义上是同步的。异步上下文管理器应始终记录其操作中哪些是取消+调度点。

.. tab:: 英文

    The first major place that Trio departs from curio is in its decision
    to make a much larger fraction of the API use sync functions rather
    than async functions, and to provide strong conventions about cancel
    points and schedule points. (At this point, there are a lot of ways
    that Trio and curio have diverged. But this was really the origin –
    the tipping point where I realized that exploring these ideas would
    require a new library, and couldn't be done inside curio.) The full
    reasoning here takes some unpacking.

    First, some definitions: a *cancel point* is a point where your code
    checks if it has been cancelled – e.g., due to a timeout having
    expired – and potentially raises a :exc:`Cancelled` error. A *schedule
    point* is a point where the current task can potentially be suspended,
    and another task allowed to run.

    In curio, the convention is that all operations that interact with the
    run loop in any way are syntactically async, and it's undefined which
    of these operations are cancel/schedule points; users are instructed
    to assume that any of them *might* be cancel/schedule points, but with
    a few exceptions there's no guarantee that any of them are unless they
    actually block. (I.e., whether a given call acts as a cancel/schedule
    point is allowed to vary across curio versions and also depending on
    runtime factors like network load.)

    But when using an async library, there are good reasons why you need
    to be aware of cancel and schedule points. They introduce a set of
    complex and partially conflicting constraints on your code:

    You need to make sure that every task passes through a cancel
    point regularly, because otherwise timeouts become ineffective
    and your code becomes subject to DoS attacks and other
    problems. So for correctness, it's important to make sure you
    have enough cancel points.

    But... every cancel point also increases the chance of subtle
    bugs in your program, because it's a place where you have to be
    prepared to handle a :exc:`Cancelled` exception and clean up
    properly. And while we try to make this as easy as possible,
    these kinds of clean-up paths are notorious for getting missed
    in testing and harboring subtle bugs. So the more cancel points
    you have, the harder it is to make sure your code is correct.

    Similarly, you need to make sure that every task passes through
    a schedule point regularly, because otherwise this task could
    end up hogging the event loop and preventing other code from
    running, causing a latency spike. So for correctness, it's
    important to make sure you have enough schedule points.

    But... you have to be careful here too, because every schedule
    point is a point where arbitrary other code could run, and
    alter your program's state out from under you, introducing
    classic concurrency bugs. So as you add more schedule points,
    it `becomes exponentially harder to reason about how your code
    is interleaved and be sure that it's correct
    <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`__.

    So an important question for an async I/O library is: how do we help
    the user manage these trade-offs?

    Trio's answer is informed by two further observations:

    First, any time a task blocks (e.g., because it does an ``await
    sock.recv()`` but there's no data available to receive), that
    has to be a cancel point (because if the I/O never arrives, we
    need to be able to time out), and it has to be a schedule point
    (because the whole idea of asynchronous programming is that
    when one task is waiting we can switch to another task to get
    something useful done).

    And second, a function which sometimes counts as a cancel/schedule
    point, and sometimes doesn't, is the worst of both worlds: you have
    put in the effort to make sure your code handles cancellation or
    interleaving correctly, but you can't count on it to help meet latency
    requirements.

    With all that in mind, Trio takes the following approach:

    Rule 1: to reduce the number of concepts to keep track of, we collapse
    cancel points and schedule points together. Every point that is a
    cancel point is also a schedule point and vice versa. These are
    distinct concepts both theoretically and in the actual implementation,
    but we hide that distinction from the user so that there's only one
    concept they need to keep track of.

    Rule 2: Cancel+schedule points are determined *statically*. A Trio
    primitive is either *always* a cancel+schedule point, or *never* a
    cancel+schedule point, regardless of runtime conditions. This is
    because we want it to be possible to determine whether some code has
    "enough" cancel/schedule points by reading the source code.

    In fact, to make this even simpler, we make it so you don't even have
    to look at the function arguments: each *function* is either a
    cancel+schedule point on *every* call or on *no* calls.

    (Pragmatic exception: a Trio primitive is not required to act as a
    cancel+schedule point when it raises an exception, even if it would
    act as one in the case of a successful return. See `issue 474
    <https://github.com/python-trio/trio/issues/474>`__ for more details;
    basically, requiring checkpoints on all exception paths added a lot of
    implementation complexity with negligible user-facing benefit.)

    Observation: since blocking is always a cancel+schedule point, rule 2
    implies that any function that *sometimes* blocks is *always* a
    cancel+schedule point.

    So that gives us a number of cancel+schedule points: all the functions
    that can block. Are there any others? Trio's answer is: no. It's easy
    to add new points explicitly (throw in a ``sleep(0)`` or whatever) but
    hard to get rid of them when you don't want them. (And this is a real
    issue – "too many potential cancel points" is definitely a tension
    `I've felt
    <https://github.com/dabeaz/curio/issues/149#issuecomment-269745283>`__
    while trying to build things like task supervisors in curio.) And we
    expect that most Trio programs will execute potentially-blocking
    operations "often enough" to produce reasonable behavior. So, rule 3:
    the *only* cancel+schedule points are the potentially-blocking
    operations.

    And now that we know where our cancel+schedule points are, there's the
    question of how to effectively communicate this information to the
    user. We want some way to mark out a category of functions that might
    block or trigger a task switch, so that they're clearly distinguished
    from functions that don't do this. Wouldn't it be nice if there were
    some Python feature, that naturally divided functions into two
    categories, and maybe put some sort of special syntactic marking on
    with the functions that can do weird things like block and task
    switch...? What a coincidence, that's exactly how async functions
    work! Rule 4: in Trio, only the potentially blocking functions are
    async. So e.g. :meth:`Event.wait` is async, but :meth:`Event.set` is
    sync.

    Summing up: out of what's actually a pretty vast space of design
    possibilities, we declare by fiat that when it comes to Trio
    primitives, all of these categories are identical:

    * async functions
    * functions that can, under at least some circumstances, block
    * functions where the caller needs to be prepared to handle potential :exc:`Cancelled` exceptions
    * functions that are guaranteed to notice any pending cancellation
    * functions where you need to be prepared for a potential task switch
    * functions that are guaranteed to take care of switching tasks if appropriate

    This requires some non-trivial work internally – it actually takes a
    fair amount of care to make those 4 cancel/schedule categories line
    up, and there are some shenanigans required to let sync and async APIs
    both interact with the run loop on an equal footing. But this is all
    invisible to the user, we feel that it pays off in terms of usability
    and correctness.

    There is one exception to these rules, for async context
    managers. Context managers are composed of two operations – enter and
    exit – and sometimes only one of these is potentially
    blocking. (Examples: ``async with lock:`` can block when entering but
    never when exiting; ``async with open_nursery() as ...:`` can block
    when exiting but never when entering.) But, Python doesn't have
    "half-asynchronous" context managers: either both operations are
    async-flavored, or neither is. In Trio we take a pragmatic approach:
    for this kind of async context manager, we enforce the above rules
    only on the potentially blocking operation, and the other operation is
    allowed to be syntactically ``async`` but semantically
    synchronous. And async context managers should always document which
    of their operations are schedule+cancel points.


异常始终传播
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Exceptions always propagate**

.. tab:: 中文

    Trio 遵循的另一个规则是 *异常必须始终传播*。这就像 `Zen <https://www.python.org/dev/peps/pep-0020/>`__ 中关于“错误不应默默无闻”的那行话，不同之处在于，在 Python 的其他所有并发库（线程、asyncio、curio 等）中，遇到无法传递的异常通常会打印到 stderr，然后被丢弃。虽然我们理解这些库采用这种方法的务实约束，但我们认为有太多情况下没有人会查看 stderr 并注意到问题，因此我们坚持认为 Trio 的 API 必须找到一种方法，将异常“向上传播”——无论这意味着什么。

    遵循这个规则通常是一个挑战 —— 例如， `call soon` 代码必须做一些弯路才能实现 —— 但它最具戏剧性的影响可以在 Trio 的任务生成接口中看到，这种设计激发了“托儿所”（nurseries）的使用：

    .. code-block:: python

        async def parent():
            async with trio.open_nursery() as nursery:
                nursery.start_soon(child)

    （详见 :ref:`tasks`。）

    如果你眯着眼看，你可以看到 Erlang 的“任务链接”和“任务树”概念的影响，尽管细节有所不同。

    这个设计还导致了一个显著、意外的不变性。

    在 `这篇博客文章
    <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#c-c-c-c-causality-breaker>`__ 中，我提到过 curio 的任务生成 API 中的一个优点，即由于生成是打破因果关系的唯一方式，而在 curio 中，``spawn`` 是异步的，这意味着在 curio 中同步函数被保证是有因果关系的。然而，这个不变性实际上并不太具有预测性：在 curio 中有很多异步函数可能会生成子任务并破坏因果关系，但大多数不会，且没有明确的标记来区分哪些会破坏因果关系。

    我们的 API 并不完全提供这种保证，但实际上提供了一个更好的保证。在 Trio 中：

    * 同步函数不能创建托儿所，因为托儿所需要 ``async with``。

    * 任何异步函数都可以创建托儿所并启动新任务……但创建托儿所 *允许任务启动但不允许打破因果关系*，因为子任务必须在函数返回之前退出。因此，我们可以在不放弃并发性的情况下保留因果关系！

    * 唯一能够打破因果关系的方式（这是一项重要功能，只是需要小心处理）是显式地在一个任务中创建托儿所对象，然后将其传递到另一个任务中。这提供了一个非常清晰、精确的信号，表明有奇怪的事情发生 —— 只要注意托儿所对象的传递。

.. tab:: 英文

    Another rule that Trio follows is that *exceptions must always
    propagate*. This is like the `zen
    <https://www.python.org/dev/peps/pep-0020/>`__ line about "Errors
    should never pass silently", except that in every other concurrency
    library for Python (threads, asyncio, curio, ...), it's fairly common
    to end up with an undeliverable exception, which just gets printed to
    stderr and then discarded. While we understand the pragmatic
    constraints that motivated these libraries to adopt this approach, we
    feel that there are far too many situations where no human will ever
    look at stderr and notice the problem, and insist that Trio APIs find
    a way to propagate exceptions "up the stack" – whatever that might
    mean.

    This is often a challenging rule to follow – for example, the call
    soon code has to jump through some hoops to make it happen – but its
    most dramatic influence can seen in Trio's task-spawning interface,
    where it motivates the use of "nurseries":

    .. code-block:: python

        async def parent():
            async with trio.open_nursery() as nursery:
                nursery.start_soon(child)

    (See :ref:`tasks` for full details.)

    If you squint you can see the conceptual influence of Erlang's "task
    linking" and "task tree" ideas here, though the details are different.

    This design also turns out to enforce a remarkable, unexpected
    invariant.

    In `the blog post
    <https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#c-c-c-c-causality-breaker>`__
    I called out a nice feature of curio's spawning API, which is that
    since spawning is the only way to break causality, and in curio
    ``spawn`` is async, which means that in curio sync functions are
    guaranteed to be causal. One limitation though is that this invariant
    is actually not very predictive: in curio there are lots of async
    functions that could spawn off children and violate causality, but
    most of them don't, but there's no clear marker for the ones that do.

    Our API doesn't quite give that guarantee, but actually a better
    one. In Trio:

    * Sync functions can't create nurseries, because nurseries require an ``async with``

    * Any async function can create a nursery and start new tasks... but creating a nursery *allows task starting but does not permit causality breaking*, because the children have to exit before the function is allowed to return. So we can preserve causality without having to give up concurrency!

    * The only way to violate causality (which is an important feature, just one that needs to be handled carefully) is to explicitly create a nursery object in one task and then pass it into another task. And this provides a very clear and precise signal about where the funny stuff is happening – just watch for the nursery object getting passed around.


自省、调试、测试
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Introspection, debugging, testing**

.. tab:: 中文

    反射和调试工具对实现实际的可用性和正确性至关重要，因此它们应该是 Trio 中的头等考虑因素。

    类似地，强大的测试工具的可用性对可用性和正确性有巨大影响；我们认为测试助手是 Trio 项目中非常重要的一部分。

.. tab:: 英文

    Tools for introspection and debugging are critical to achieving
    usability and correctness in practice, so they should be first-class
    considerations in Trio.

    Similarly, the availability of powerful testing tools has a huge
    impact on usability and correctness; we consider testing helpers to be
    very much in scope for the Trio project.


特定样式指南
-------------------------

**Specific style guidelines**

.. tab:: 中文

    * 如上所述，非阻塞函数应标记为同步（sync）颜色，而可能阻塞的函数应标记为异步（async）颜色，并无条件地充当取消+调度点。

    * 任何接受可调用对象（callable）作为参数的函数，其签名应类似于：

      .. code-block:: python

        def call_the_thing(fn, *args, kwonly1, kwonly2):
            ...

      其中 ``fn(*args)`` 是要调用的函数， ``kwonly1`` 和 ``kwonly2`` 是属于 ``call_the_thing`` 的关键字参数。即使 ``call_the_thing`` 没有自己的参数，此规则依然适用，即在这种情况下，它的签名看起来像：

      .. code-block:: python

        def call_the_thing(fn, *args):
            ...

      这样，用户在大多数情况下可以跳过使用 :func:`functools.partial`，同时仍然提供一种明确且可扩展的方式来传递参数给调用者。
      （向 asyncio 致敬，我们从中借用了这一约定。）

    * 每当合适时，Trio 类应具有一个名为 ``statistics()`` 的方法，该方法返回一个不可变对象，包含有关对象的内部统计信息，这些信息对调试或反射很有用（ :ref:`examples <synchronization>`）。

    * 用于等待条件变为真的函数或方法应命名为 ``wait_<condition>``。这样可以避免诸如“``await readable()`` 是*检查*可读性（返回布尔值），还是*等待*可读性？”的歧义。

      有时这会导致看起来稍微有点怪异的 ``await wait_...``。抱歉。就我所知，所有其他选项都不如这个约定清晰，而且你会很快习惯这种约定。

    * 如果需要提供阻塞版本和非阻塞版本的函数，它们应看起来像：

      .. code-block:: python

        async def OPERATION(arg1, arg2):
            ...

        def OPERATION_nowait(arg1, arg2):
            ...

      并且 ``nowait`` 版本如果会阻塞，则会引发 :exc:`trio.WouldBlock`。

    * ...我们应该有，但目前没有，明确的约定来区分接受异步可调用对象和同步可调用对象的函数。详见 `issue #68 <https://github.com/python-trio/trio/issues/68>`__。

.. tab:: 英文

    * As noted above, functions that don't block should be sync-colored, and functions that might block should be async-colored and unconditionally act as cancel+schedule points.

    * Any function that takes a callable to run should have a signature like:

      .. code-block:: python

        def call_the_thing(fn, *args, kwonly1, kwonly2):
            ...

      where ``fn(*args)`` is the thing to be called, and ``kwonly1``,
      ``kwonly2``, are keyword-only arguments that belong to
      ``call_the_thing``. This applies even if ``call_the_thing`` doesn't
      take any arguments of its own, i.e. in this case its signature looks
      like:

      .. code-block:: python

        def call_the_thing(fn, *args):
            ...

      This allows users to skip faffing about with
      :func:`functools.partial` in most cases, while still providing an
      unambiguous and extensible way to pass arguments to the caller.
      (Hat-tip to asyncio, who we stole this convention from.)

    * Whenever it makes sense, Trio classes should have a method called
      ``statistics()`` which returns an immutable object with named fields
      containing internal statistics about the object that are useful for
      debugging or introspection (:ref:`examples <synchronization>`).

    * Functions or methods whose purpose is to wait for a condition to
      become true should be called ``wait_<condition>``. This avoids
      ambiguities like "does ``await readable()`` *check* readability
      (returning a bool) or *wait for* readability?".

      Sometimes this leads to the slightly funny looking ``await
      wait_...``. Sorry. As far as I can tell all the alternatives are
      worse, and you get used to the convention pretty quick.

    * If it's desirable to have both blocking and non-blocking versions of
      a function, then they look like:

      .. code-block:: python

        async def OPERATION(arg1, arg2):
            ...

        def OPERATION_nowait(arg1, arg2):
            ...

      and the ``nowait`` version raises :exc:`trio.WouldBlock` if it would block.

    * ...we should, but currently don't, have a solid convention to
      distinguish between functions that take an async callable and those
      that take a sync callable. See `issue #68
      <https://github.com/python-trio/trio/issues/68>`__.


Trio 内部结构简介
--------------------------------

**A brief tour of Trio's internals**

.. tab:: 中文

    如果你想了解 Trio 内部是如何构建的，那么首先要知道的是，Trio 有一个非常严格的内部分层： ``trio._core`` 包是调度/取消/IO 处理逻辑的完全自包含实现，其他 ``trio.*`` 模块则是基于它暴露的 API 来实现的。（如果你想查看这个 API 是什么样的，可以运行 ``import trio; print(trio._core.__all__)``）。从 ``trio._core`` 导出的所有内容*也*作为 ``trio``、 ``trio.lowlevel`` 或 ``trio.testing`` 命名空间的一部分进行导出。（详情请参阅它们各自的 ``__init__.py`` 文件；有一个测试来强制执行这一点。）

    理由: 目前，Trio 是一个新项目，处于设计空间的一个新领域，因此我们不做任何稳定性保证。但我们的目标是达到一个能够声明 API 稳定的阶段。我们不太可能快速探索设计空间的所有可能角落并覆盖所有可能的 I/O 类型。因此，我们的策略是确保独立包可以在 Trio 的基础上添加新功能。强制执行 ``trio`` 和 ``trio._core`` 的拆分是我们 `吃自己的狗粮 <https://en.wikipedia.org/wiki/Eating_your_own_dog_food>`__：像 :class:`trio.Lock` 和 :mod:`trio.socket` 这样的基本功能实际上完全通过公开 API 实现。我们的希望是，通过这样做，我们增加了这样的可能性：某些人如果想要提出一种更好的队列方式，或者想添加一些新的功能，比如文件系统变化监视，能够在不修改 Trio 内部的情况下，通过我们的公开 API 实现这些功能。

.. tab:: 英文

    If you want to understand how Trio is put together internally, then
    the first thing to know is that there's a very strict internal
    layering: the ``trio._core`` package is a fully self-contained
    implementation of the core scheduling/cancellation/IO handling logic,
    and then the other ``trio.*`` modules are implemented in terms of the
    API it exposes. (If you want to see what this API looks like, then
    ``import trio; print(trio._core.__all__)``). Everything exported from
    ``trio._core`` is *also* exported as part of the ``trio``,
    ``trio.lowlevel``, or ``trio.testing`` namespaces. (See their
    respective ``__init__.py`` files for details; there's a test to
    enforce this.)

    Rationale: currently, Trio is a new project in a novel part of the
    design space, so we don't make any stability guarantees. But the goal
    is to reach the point where we *can* declare the API stable. It's
    unlikely that we'll be able to quickly explore all possible corners of
    the design space and cover all possible types of I/O. So instead, our
    strategy is to make sure that it's possible for independent packages
    to add new features on top of Trio. Enforcing the ``trio`` vs
    ``trio._core`` split is a way of `eating our own dogfood
    <https://en.wikipedia.org/wiki/Eating_your_own_dog_food>`__: basic
    functionality like :class:`trio.Lock` and :mod:`trio.socket` is
    actually implemented solely in terms of public APIs. And the hope is
    that by doing this, we increase the chances that someone who comes up
    with a better kind of queue or wants to add some new functionality
    like, say, file system change watching, will be able to do that on top
    of our public APIs without having to modify Trio internals.


``trio._core`` 内部
~~~~~~~~~~~~~~~~~~~~~

**Inside** ``trio._core``

.. tab:: 中文

    ``_ki.py`` 模块实现了安全处理 :class:`KeyboardInterrupt` 的核心基础设施。它在很大程度上独立于 Trio 的其他部分，并且可以（可能应该？）提取到自己的独立包中。

    最重要的子模块是 ``_run.py``，这是所有东西集成的地方。（这也是迄今为止最大的子模块；虽然希望在可能的情况下将它的一些部分提取出来，但这很棘手，因为核心功能确实是相当紧密地交织在一起的。）特别是，这是定义取消作用域、托儿所和 :class:`~trio.lowlevel.Task` 的地方；它也是调度器状态和 :func:`trio.run` 所在的地方。

    唯一不在 ``_run.py`` 中的是 I/O 处理。这部分委托给了一个 ``IOManager`` 类，目前有三种实现：

    * ``EpollIOManager`` 在 ``_io_epoll.py`` 中（用于 Linux、illumos）

    * ``KqueueIOManager`` 在 ``_io_kqueue.py`` 中（用于 macOS、\*BSD）

    * ``WindowsIOManager`` 在 ``_io_windows.py`` 中（用于 Windows）

    epoll 和 kqueue 后端利用了标准库 :mod:`select` 模块中的 epoll 和 kqueue 封装。Windows 后端使用 CFFI 直接访问 Win32 API（见 ``trio/_core/_windows_cffi.py``）。通常来说，我们更倾向于直接使用操作系统的原生功能，而不是使用 :mod:`selectors`，原因有几个：

    * **控制我们的命运**：I/O 处理是 Trio 的核心，而 :mod:`selectors` （截至 2017-03-01）有一些 bug（例如 `issue 29256 <https://bugs.python.org/issue29256>`__ ，`issue 29255 <https://bugs.python.org/issue29255>`__）。这本身可能不算什么大问题，但由于 :mod:`selectors` 是标准库的一部分，我们无法修复它并发布更新版本；只能使用现有的版本。我们希望能对用户的体验有更多控制权。

    * **阻抗不匹配**： :mod:`selectors` API 与我们希望使用它的方式不太匹配。例如，kqueue 本地将对某个 fd 可读性的兴趣与对该 fd 可写性的兴趣分开处理，这正好与 Trio 的模型匹配。 :class:`selectors.KqueueSelector` 会在内部做很多工作，将所有对同一 fd 的兴趣合并到一起，如果要使用它，我们还得跳过更多的障碍来反转这一点。当然，原生的 epoll API 与 :mod:`selectors` API 一样以 fd 为中心，因此我们仍然需要写代码来绕过这些障碍，但关键是 :mod:`selectors` 的抽象没有提供很多额外的价值。

    * **（最重要的）访问原生平台功能**： :mod:`selectors` 在 Windows 上非常不足，甚至在类似 Unix 的系统上，它也隐藏了很多强大的功能（例如 kqueue 可以做的不只是检查 fd 的可读性/可写性！）。

    ``IOManager`` 层提供了对每个系统功能的较为原始的暴露，具有根据不同后端变化的公共 API 函数。（这在某种程度上受到 :mod:`os` 工作方式的启发。）这些公共 API 然后作为 :mod:`trio.lowlevel` 的一部分进行导出，而像 :mod:`trio.socket` 这样的高级 API 则抽象了这些系统特定的 API，以提供统一的体验。

    目前，后端的选择是在导入时静态决定的，并且没有提供“可插拔”的后端。这种直觉是，我们更愿意将精力集中在制作一套稳定的官方后端上，这些后端在所有支持的系统上都能提供开箱即用的高质量体验。

.. tab:: 英文

    The ``_ki.py`` module implements the core infrastructure for safe handling
    of :class:`KeyboardInterrupt`.  It's largely independent of the rest of Trio,
    and could (possibly should?) be extracted into its own independent package.

    The most important submodule, where everything is integrated, is
    ``_run.py``. (This is also by far the largest submodule; it'd be nice
    to factor bits of it out where possible, but it's tricky because the
    core functionality genuinely is pretty intertwined.) Notably, this is
    where cancel scopes, nurseries, and :class:`~trio.lowlevel.Task` are
    defined; it's also where the scheduler state and :func:`trio.run`
    live.

    The one thing that *isn't* in ``_run.py`` is I/O handling. This is
    delegated to an ``IOManager`` class, of which there are currently
    three implementations:

    * ``EpollIOManager`` in ``_io_epoll.py`` (used on Linux, illumos)

    * ``KqueueIOManager`` in ``_io_kqueue.py`` (used on macOS, \*BSD)

    * ``WindowsIOManager`` in ``_io_windows.py`` (used on Windows)

    The epoll and kqueue backends take advantage of the epoll and kqueue
    wrappers in the stdlib :mod:`select` module. The windows backend uses
    CFFI to access to the Win32 API directly (see
    ``trio/_core/_windows_cffi.py``). In general, we prefer to go directly
    to the raw OS functionality rather than use :mod:`selectors`, for
    several reasons:

    * Controlling our own fate: I/O handling is pretty core to what Trio
      is about, and :mod:`selectors` is (as of 2017-03-01) somewhat buggy
      (e.g. `issue 29256 <https://bugs.python.org/issue29256>`__, `issue
      29255 <https://bugs.python.org/issue29255>`__). Which isn't a big
      deal on its own, but since :mod:`selectors` is part of the standard
      library we can't fix it and ship an updated version; we're stuck
      with whatever we get. We want more control over our users'
      experience than that.

    * Impedance mismatch: the :mod:`selectors` API isn't particularly
      well-fitted to how we want to use it. For example, kqueue natively
      treats an interest in readability of some fd as a separate thing
      from an interest in that same fd's writability, which neatly matches
      Trio's model. :class:`selectors.KqueueSelector` goes to some effort
      internally to lump together all interests in a single fd, and to use
      it we'd then we'd have to jump through more hoops to reverse
      this. Of course, the native epoll API is fd-centric in the same way
      as the :mod:`selectors` API so we do still have to write code to
      jump through these hoops, but the point is that the :mod:`selectors`
      abstractions aren't providing a lot of extra value.

    * (Most important) Access to raw platform capabilities:
      :mod:`selectors` is highly inadequate on Windows, and even on
      Unix-like systems it hides a lot of power (e.g. kqueue can do a lot
      more than just check fd readability/writability!).

    The ``IOManager`` layer provides a fairly raw exposure of the capabilities
    of each system, with public API functions that vary between different
    backends. (This is somewhat inspired by how :mod:`os` works.) These
    public APIs are then exported as part of :mod:`trio.lowlevel`, and
    higher-level APIs like :mod:`trio.socket` abstract over these
    system-specific APIs to provide a uniform experience.

    Currently the choice of backend is made statically at import time, and
    there is no provision for "pluggable" backends. The intuition here is
    that we'd rather focus our energy on making one set of solid, official
    backends that provide a high-quality experience out-of-the-box on all
    supported systems.
