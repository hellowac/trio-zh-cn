.. _contributing:

为 Trio 及相关项目做出贡献
=========================================

**Contributing to Trio and related projects**

.. tab:: 中文

    你有兴趣为 Trio 或 `我们的相关项目 <https://github.com/python-trio>`__ 做贡献吗？太棒了！Trio 是一个由非正式志愿者团队维护的开源项目。我们的目标是让 Python 中的异步 I/O 更加有趣、易用和可靠，而我们无法在没有像你这样的人帮助的情况下完成这一目标。我们欢迎任何愿意与其他贡献者和社区成员真诚合作的人参与贡献（另见我们的 :ref:`行为准则 <code-of-conduct>`）。

    贡献的方式有很多种，任何贡献都不会被忽视，所有贡献都受到重视。例如，你可以：

    - 在我们的 `聊天室 <https://gitter.im/python-trio/general>`__ 闲逛并帮助有问题的人。
    - 注册我们的 `论坛 <https://trio.discourse.group>`__，设置通知以便关注有趣的对话并参与其中。
    - 在 StackOverflow 上回答问题（ `最近的问题 <https://stackexchange.com/filters/289914/trio-project-tags-on-stackoverflow-filter>`__）。
    - 在项目中使用 Trio，并向我们反馈哪些地方有效，哪些地方无效。
    - 写一篇关于你使用 Trio 的经历的博客文章，无论是好是坏。
    - 发布使用 Trio 的开源程序和库。
    - 改进文档。
    - 评论问题。
    - 添加测试。
    - 修复 bug。
    - 增加新特性。

    我们希望贡献过程既愉快又互利；本文档旨在为你提供一些有用的建议，帮助实现这一目标，适用于 `python-trio GitHub 组织下的所有项目 <https://github.com/python-trio>`__。如果你有任何改进意见，请告诉我们。

.. tab:: 英文

    So you're interested in contributing to Trio or `one of our associated
    projects <https://github.com/python-trio>`__? That's awesome! Trio is
    an open-source project maintained by an informal group of
    volunteers. Our goal is to make async I/O in Python more fun, easy,
    and reliable, and we can't do it without help from people like you. We
    welcome contributions from anyone willing to work in good faith with
    other contributors and the community (see also our
    :ref:`code-of-conduct`).

    There are many ways to contribute, no contribution is too small, and
    all contributions are valued.  For example, you could:

    - Hang out in our `chatroom <https://gitter.im/python-trio/general>`__ and help people with questions.
    - Sign up for our `forum <https://trio.discourse.group>`__, set up your notifications so you notice interesting conversations, and join in.
    - Answer questions on StackOverflow (`recent questions <https://stackexchange.com/filters/289914/trio-project-tags-on-stackoverflow-filter>`__).
    - Use Trio in a project, and give us feedback on what worked and what
      didn't.
    - Write a blog post about your experiences with Trio, good or bad.
    - Release open-source programs and libraries that use Trio.
    - Improve documentation.
    - Comment on issues.
    - Add tests.
    - Fix bugs.
    - Add features.

    We want contributing to be enjoyable and mutually beneficial; this
    document tries to give you some tips to help that happen, and applies
    to all of the projects under the `python-trio organization on Github
    <https://github.com/python-trio>`__. If you have thoughts on how it
    can be improved then please let us know.


入门
---------------

Getting started

.. tab:: 中文

    如果你对开源不太熟悉，可能会发现 `opensource.guide 的开源贡献教程 <https://opensource.guide/how-to-contribute/>`__ 很有帮助，或者如果你更喜欢看视频的话， `egghead.io 提供了一个免费的短视频课程 <https://egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github>`__ 。

    Trio 和相关项目是在 GitHub 上开发的，属于 `python-trio <https://github.com/python-trio>`__ 组织。代码和文档的修改是通过拉取请求（pull requests）进行的（见下文的 :ref:`准备拉取请求 <preparing-pull-requests>`）。

    我们还采取了一项不太寻常的策略来管理提交权限：任何其拉取请求被合并的人，都会自动被邀请加入 GitHub 组织，并获得我们所有仓库的提交权限。更多详情见下文 :ref:`加入团队 <joining-the-team>`。

    如果你想找个好地方开始，可以看看我们标记为 `good first issue <https://github.com/search?utf8=%E2%9C%93&q=user%3Apython-trio+label%3A%22good+first+issue%22+state%3Aopen&type=Issues&ref=advsearch&l=&l=>`__ 的问题，或者随时在 `论坛 <https://trio.discourse.group>`__ 或 `聊天室 <https://gitter.im/python-trio/general>`__ 中提问。

.. tab:: 英文

    If you're new to open source in general, you might find it useful to check out `opensource.guide's How to Contribute to Open Source tutorial <https://opensource.guide/how-to-contribute/>`__, or if video's more your thing, `egghead.io has a short free video course <https://egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github>`__.

    Trio and associated projects are developed on GitHub, under the `python-trio <https://github.com/python-trio>`__ organization. Code and documentation changes are made through pull requests (see :ref:`preparing-pull-requests` below).

    We also have an unusual policy for managing commit rights: anyone whose pull request is merged is automatically invited to join the GitHub organization, and gets commit rights to all of our repositories. See :ref:`joining-the-team` below for more details.

    If you're looking for a good place to start, then check out our issues labeled `good first issue <https://github.com/search?utf8=%E2%9C%93&q=user%3Apython-trio+label%3A%22good+first+issue%22+state%3Aopen&type=Issues&ref=advsearch&l=&l=>`__, or feel free to ask `on the forum <https://trio.discourse.group>`__ or `in chat <https://gitter.im/python-trio/general>`__.


提供支持
-----------------

Providing support

.. tab:: 中文

    在帮助他人使用 Trio 时，请记住你是在代表我们的社区，我们希望这是一个友好和欢迎的地方。

    并发编程对于初学者来说 *真的很困惑* 。与初学者交流时，记住你曾经也是初学者，我们的目标是创建一个顶级的并发库，既易于访问，又能带来愉悦的使用体验。如果有人带着初学者的问题出现，*这意味着我们在成功*。我们如何回应问题是开发者体验的一部分，就像我们的 API、文档或测试工具一样。而且，作为额外的收获，帮助初学者通常是发现改进想法的最佳方式。如果你开始感到精疲力尽或心情暴躁，我们每个人都曾经历过，休息一下直到你感觉好些是完全可以的。但不可以把情绪发泄到随机用户身上。

    请记住，竞争项目的作者和用户都是聪明、深思熟虑的人，他们在尽力平衡复杂且相互冲突的需求，就像我们一样。当然，针对具体技术问题进行批评是完全可以的（“在项目 X 中，这是通过做 Y 来处理的，Trio 使用 Z，我更喜欢这样，因为……”）或者谈谈你的个人经历（“我尝试使用 X，但我变得非常沮丧和困惑”），但请避免做出泛泛的评论，如“X 很糟糕”或“我真不敢相信有人会用 X”。

    请尽量不要对他人的性别做出假设，特别要记住我们并非都是男性。如果你没有特定的理由假设其他性别，那么 `singular they <https://en.wikipedia.org/wiki/Third-person_pronoun#Singular_they>`__ 是一个很好的代词，还有许多性别中立的集体词： "Hey folks", "Hi all", ...

    我们还喜欢 Recurse Center 的 `社交规则 <https://www.recurse.com/manual#sub-sec-social-rules>`__：

    * 不装作惊讶（也可以通过 `甜美漫画版本 <https://jvns.ca/blog/2017/04/27/no-feigning-surprise/>`__ 查看）
    * 不要说“其实是……”
    * 不做微妙的歧视主义（ `更多细节 <https://www.recurse.com/blog/38-subtle-isms-at-hacker-school>`__）

.. tab:: 英文

    When helping others use Trio, please remember that you are
    representing our community, and we want this to be a friendly and
    welcoming place.

    Concurrency is *really confusing* when you're first learning. When
    talking to beginners, remember that you were a beginner once too, and
    the whole goal here is to make a top-tier concurrency library that's
    accessible to everyone and a joy to use. If people are showing up with
    beginner questions, *that means we're succeeding*. How we respond to
    questions is part of that developer experience, just as much as our
    API, documentation, or testing tools. And as a bonus, helping
    beginners is often the best way to discover ideas for improvements. If
    you start getting burned out and cranky, we've all been there, and
    it's OK to take a break until you feel better. But it's not OK to take
    that out on random users.

    Please remember that the authors and users of competing projects are
    smart, thoughtful people doing their best to balance complicated and
    conflicting requirements, just like us. Of course it's totally fine to
    make specific technical critiques ("In project X, this is handled by
    doing Y, Trio does Z instead, which I prefer because...") or talk
    about your personal experience ("I tried using X but I got super
    frustrated and confused"), but refrain from generic statements like "X
    sucks" or "I can't believe anyone uses X".

    Please try not to make assumptions about people's gender, and in
    particular remember that we're not all dudes. If you don't have a
    specific reason to assume otherwise, then `singular they
    <https://en.wikipedia.org/wiki/Third-person_pronoun#Singular_they>`__
    makes a fine pronoun, and there are plenty of gender-neutral
    collective terms: "Hey folks", "Hi all", ...

    We also like the Recurse Center's `social rules <https://www.recurse.com/manual#sub-sec-social-rules>`__:

    * no feigning surprise (also available in a `sweet comic version <https://jvns.ca/blog/2017/04/27/no-feigning-surprise/>`__)
    * no well-actually's
    * no subtle -isms (`more details <https://www.recurse.com/blog/38-subtle-isms-at-hacker-school>`__)


.. _preparing-pull-requests:

准备拉取请求
-----------------------

Preparing pull requests

.. tab:: 中文

    如果你想提交文档或代码更改到 Trio 项目，那么你需要准备一个 GitHub 拉取请求（简称“PR”）。我们会尽最大努力快速审查你的 PR。如果过了一两周你还没有收到回应，可以随时发表评论提醒我们。（这只需要评论一个“ping”字眼，完全不算无礼。）

    以下是整理一个好 PR 的快速检查清单，详细信息请见下文的各个部分：

    * :ref:`pull-request-scope`：你的 PR 是否解决了一个单一的、自包含的问题？

    * :ref:`pull-request-tests`：你的测试是否通过？你是否添加了必要的测试？代码更改几乎总是需要相应的测试更改，因为如果代码值得修复，那么就值得添加一个测试，确保修复保持有效。

    * :ref:`pull-request-formatting`：如果你更改了 Python 代码，你是否运行了 ``black trio``？（对于其他包，将 ``trio`` 替换为包名。）

    * :ref:`pull-request-release-notes`：如果你的更改影响了用户可见的功能，你是否在 ``newsfragments/`` 目录下添加了发布说明？

    * :ref:`pull-request-docs`：你是否进行了必要的文档更新？

    * 许可：通过提交 PR 到 Trio 项目，你将你的更改提供给该项目的许可证。对于大多数项目，这是双重 MIT/Apache 2 许可，除了 cookiecutter-trio，它使用 CC0 许可。

.. tab:: 英文

    If you want to submit a documentation or code change to one of the
    Trio projects, then that's done by preparing a Github pull request (or
    "PR" for short). We'll do our best to review your PR quickly. If it's
    been a week or two and you're still waiting for a response, feel free
    to post a comment poking us. (This can just be a comment with the
    single word "ping"; it's not rude at all.)

    Here's a quick checklist for putting together a good PR, with details
    in separate sections below:

    * :ref:`pull-request-scope`: Does your PR address a single, self-contained issue?

    * :ref:`pull-request-tests`: Are your tests passing? Did you add any necessary tests? Code changes pretty much always require test changes, because if it's worth fixing the code then it's worth adding a test to make sure it stays fixed.

    * :ref:`pull-request-formatting`: If you changed Python code, then did you run ``black trio``? (Or for other packages, replace ``trio`` with the package name.)

    * :ref:`pull-request-release-notes`: If your change affects user-visible functionality, then did you add a release note to the ``newsfragments/`` directory?

    * :ref:`pull-request-docs`: Did you make any necessary documentation updates?

    * License: by submitting a PR to a Trio project, you're offering your changes under that project's license. For most projects, that's dual MIT/Apache 2, except for cookiecutter-trio, which is CC0.


.. _pull-request-scope:

在 PR 中要放什么
~~~~~~~~~~~~~~~~~~~

What to put in a PR

.. tab:: 中文

    每个 PR 应尽可能只解决一个问题并且是自包含的。如果你有十个小的、不相关的更改，那么请提交十个 PR —— 审查十个小更改比审查一个包含所有更改的大 PR 更容易，而且这样做如果某个更改存在问题，也不会拖延其他更改的进度。

    如果你不确定某个更改是否是一个好主意，并且在投入时间之前想要一些反馈，可以随时在 issue 或聊天室中询问。如果你有部分更改想要获得反馈，可以提交为 PR。（在这种情况下，传统上 PR 的标题会以 ``[WIP]`` 开头，表示“进行中的工作”。）

    当你提交 PR 时，可以在提交信息或 PR 描述中包含 ``Closes #123``、 ``Fixes: #123`` 或
    `某种变体 <https://help.github.com/en/articles/closing-issues-using-keywords>`__，
    这样当 PR 被合并时，会自动关闭引用的 issue。
    这有助于保持我们所期望的状态，即每个开放的 issue 都反映了某项仍需完成的工作。

.. tab:: 英文

    Each PR should, as much as possible, address just one issue and be
    self-contained. If you have ten small, unrelated changes, then go
    ahead and submit ten PRs – it's much easier to review ten small
    changes than one big change with them all mixed together, and this way
    if there's some problem with one of the changes it won't hold up all
    the others.

    If you're uncertain about whether a change is a good idea and want
    some feedback before putting time into it, feel free to ask in an
    issue or in the chat room. If you have a partial change that you want
    to get feedback on, feel free to submit it as a PR. (In this case it's
    traditional to start the PR title with ``[WIP]``, for "work in
    progress".)

    When you are submitting your PR, you can include ``Closes #123``,
    ``Fixes: #123`` or
    `some variation <https://help.github.com/en/articles/closing-issues-using-keywords>`__
    in either your commit message or the PR description, in order to
    automatically close the referenced issue when the PR is merged.
    This keeps us closer to the desired state where each open issue reflects some
    work that still needs to be done.


环境
~~~~~~~~~~~

Environment

.. tab:: 中文

    我们强烈建议使用虚拟环境来管理依赖项，例如使用 `venv <https://docs.python.org/3/library/venv.html>`__。因此，要设置你的环境并安装依赖项，你应该运行类似如下的命令：

    .. code-block:: shell

        cd path/to/trio/checkout/
        python -m venv .venv # 在 .venv 中创建虚拟环境
        source .venv/bin/activate # 激活虚拟环境
        pip install -e . # 安装 trio，pytest 插件所需
        pip install -r test-requirements.txt # 安装测试依赖

    你不需要经常重建虚拟环境，但在未来的终端中需要重新激活它。如果 `test-requirements.txt` 中的版本更新了，你可能还需要重新从该文件中安装依赖。

.. tab:: 英文

    We strongly suggest using a virtual environment for managing dependencies,
    for example with `venv <https://docs.python.org/3/library/venv.html>`__. So to
    set up your environment and install dependencies, you should run something like:

    .. code-block:: shell

        cd path/to/trio/checkout/
        python -m venv .venv # create virtual env in .venv
        source .venv/bin/activate # activate it
        pip install -e . # install trio, needed for pytest plugin
        pip install -r test-requirements.txt # install test requirements

    you rarely need to recreate the virtual environment, but you need to re-activate it
    in future terminals. You might also need to re-install from test-requirements.txt if
    the versions in it get updated.

.. _pull-request-tests:

测试
~~~~~

Tests

.. tab:: 中文

    我们使用 `pytest <https://pytest.org/>`__ 进行测试。要在本地运行测试，你应该执行以下命令：

    .. code-block:: shell

        source .venv/bin/activate # 如果尚未激活虚拟环境
        pytest src

    这并不会尝试进行全面的测试——它仅仅检查代码在你机器上是否能正常工作，并且会跳过一些耗时较长的测试。但它是一个快速检查代码是否正常的好方法，当你提交 PR 后，我们会自动运行完整的测试套件，所以你有机会看到并修复任何剩余的问题。

    每个更改应该确保 100% 的代码和测试覆盖率。不过，你可以使用 ``# pragma: no cover`` 来标记那些没有覆盖的行，且我们并不希望修复的部分（而不是因为难以修复）。例如：

    .. code-block:: python

        if ...:
            ...
        else:  # pragma: no cover
            raise AssertionError("这不可能发生！")

    我们使用 Codecov 来跟踪覆盖率，因为它能方便地合并不同配置下的覆盖率数据。在本地运行覆盖率测试可能会很有用：

    .. code-block:: shell

        coverage run -m pytest
        coverage combine
        coverage report

    但如果你看到的覆盖率比 Codecov 报告中低一些，不要惊讶，因为有些代码行可能只会在 Windows、macOS、PyPy 或 CPython 上执行，或者……你明白的。提交 PR 后，Codecov 会自动报告覆盖率，因此你可以检查自己实际的覆盖情况。（但请注意，直到所有测试通过之前，结果可能不准确。如果测试失败，请先修复，再关注覆盖率。）

    编写良好测试的一些规则：

    * `测试必须是确定性的 <https://github.com/python-trio/trio/issues/200>`__。不稳定的测试会让开发者感到痛苦。一个常见的不确定性来源是调度器顺序；如果你在这方面遇到问题，:mod:`trio.testing` 提供了强大的工具来帮助控制顺序，比如 :func:`trio.testing.wait_all_tasks_blocked`、:class:`trio.testing.Sequencer` 和 :class:`trio.testing.MockClock` （通常作为一个 fixture 使用：``async def test_whatever(autojump_clock): ...``）。如果你需要更多的工具，我们应该添加它们。

    * （仅限 Trio 包）慢速测试——任何耗时超过大约 0.25 秒的测试——应该使用 ``@slow`` 标记。这样它们只有在你运行 ``pytest trio --run-slow`` 时才会执行。我们的 CI 脚本会运行慢速测试，因此你可以确保代码仍然会得到充分测试，这样你就不必在本地迭代更改时浪费时间等待一些不相关的慢速测试。

      你可以通过向 pytest 传递 ``--durations=10`` 来检查慢速测试。大多数测试应该在 0.01 秒内完成。

    * 说到等待测试：除非 *绝对必要*，测试中永远不应使用 sleep。然而，在使用 ``autojump_clock`` 时调用 :func:`trio.sleep` 是可以的，因为这实际上并不是在休眠，并不会浪费开发者的时间等待测试完成。

    * 我们希望测试能够验证实际的功能。例如，如果你正在添加子进程启动功能，那么你的测试应该至少启动一个进程！有时这可能有些棘手——例如，Trio 的 :class:`KeyboardInterrupt` 测试必须通过一些技巧来在正确的时机生成真实的 SIGINT 信号，以覆盖不同的代码路径。但几乎总是值得这样做的。

    * 对于那些实际测试不相关或不充分的情况，我们强烈推荐使用伪造或存根（fakes or stubs），而非 mocks。以下是一些有用的文章：

      * `Test Doubles - Fakes, Mocks and Stubs <https://dev.to/milipski/test-doubles---fakes-mocks-and-stubs>`__

      * `Mocks aren't stubs <https://martinfowler.com/articles/mocksArentStubs.html>`__

      * `Write test doubles you can trust using verified fakes <https://codewithoutrules.com/2016/07/31/verified-fakes/>`__

      大多数主要功能都有真实测试和使用伪造或存根的测试。例如，:class:`~trio.SSLStream` 有一些测试，使用 Trio 实际与 SSL 服务器建立连接，这是一个使用阻塞 I/O 实现的真实连接，因为如果这个不起作用就很尴尬。然后，还有一些使用内存中的伪造传输流的测试，我们可以完全控制时序，确保所有微妙的边界情况都能正确处理。

    编写可靠的测试来验证一些不常见的边缘情况通常比实现一个功能还要困难，但坚持下去：这是值得的！如果你需要帮助，别害怕请求帮助。有时候，换一个新视角能帮助你想出一些巧妙的解决方案。

.. tab:: 英文

    We use `pytest <https://pytest.org/>`__ for testing. To run the tests
    locally, you should run:

    .. code-block:: shell

        source .venv/bin/activate # if not already activated
        pytest src

    This doesn't try to be completely exhaustive – it only checks that
    things work on your machine, and it will skip some slow tests. But it's
    a good way to quickly check that things seem to be working, and we'll
    automatically run the full test suite when your PR is submitted, so
    you'll have a chance to see and fix any remaining issues then.

    Every change should have 100% coverage for both code and tests. But,
    you can use ``# pragma: no cover`` to mark lines where
    lack-of-coverage isn't something that we'd want to fix (as opposed to
    it being merely hard to fix). For example:

    .. code-block:: python

        if ...:
            ...
        else:  # pragma: no cover
            raise AssertionError("this can't happen!")

    We use Codecov to track coverage, because it makes it easy to combine
    coverage from running in different configurations. Running coverage
    locally can be useful

    .. code-block:: shell

        coverage run -m pytest
        coverage combine
        coverage report

    but don't be surprised if you get lower coverage than when looking at Codecov
    reports, because there are some lines that are only executed on
    Windows, or macOS, or PyPy, or CPython, or... you get the idea. After
    you create a PR, Codecov will automatically report back with the
    coverage, so you can check how you're really doing. (But note that the
    results can be inaccurate until all the tests are passing. If the
    tests failed, then fix that before worrying about coverage.)

    Some rules for writing good tests:

    * `Tests MUST pass deterministically <https://github.com/python-trio/trio/issues/200>`__. Flakey tests make for miserable developers. One common source of indeterminism is scheduler ordering; if you're having trouble with this, then :mod:`trio.testing` provides powerful tools to help control ordering, like :func:`trio.testing.wait_all_tasks_blocked`, :class:`trio.testing.Sequencer`, and :class:`trio.testing.MockClock` (usually used as a fixture: ``async def test_whatever(autojump_clock): ...``). And if you need more tools than this then we should add them.

    * (Trio package only) Slow tests – anything that takes more than about 0.25 seconds – should be marked with ``@slow``. This makes it so they only run if you do ``pytest trio --run-slow``. Our CI scripts do run slow tests, so you can be sure that the code will still be thoroughly tested, and this way you don't have to sit around waiting for a few irrelevant multi-second tests to run while you're iterating on a change locally.

      You can check for slow tests by passing ``--durations=10`` to pytest. Most tests should take 0.01 seconds or less.

    * Speaking of waiting around for tests: Tests should never sleep unless *absolutely* necessary. However, calling :func:`trio.sleep` when using ``autojump_clock`` is fine, because that's not really sleeping, and doesn't waste developers time waiting for the test to run.

    * We like tests to exercise real functionality. For example, if you're adding subprocess spawning functionality, then your tests should spawn at least one process! Sometimes this is tricky – for example, Trio's :class:`KeyboardInterrupt` tests have to jump through quite some hoops to generate real SIGINT signals at the right times to exercise different paths. But it's almost always worth it.

    * For cases where real testing isn't relevant or sufficient, then we strongly prefer fakes or stubs over mocks. Useful articles:

      * `Test Doubles - Fakes, Mocks and Stubs <https://dev.to/milipski/test-doubles---fakes-mocks-and-stubs>`__

      * `Mocks aren't stubs <https://martinfowler.com/articles/mocksArentStubs.html>`__

      * `Write test doubles you can trust using verified fakes <https://codewithoutrules.com/2016/07/31/verified-fakes/>`__

      Most major features have both real tests and tests using fakes or stubs. For example, :class:`~trio.SSLStream` has some tests that use Trio to make a real socket connection to real SSL server implemented using blocking I/O, because it sure would be embarrassing if that didn't work. And then there are also a bunch of tests that use a fake in-memory transport stream where we have complete control over timing and can make sure all the subtle edge cases work correctly.

    Writing reliable tests for obscure corner cases is often harder than implementing a feature in the first place, but stick with it: it's worth it! And don't be afraid to ask for help. Sometimes a fresh pair of eyes can be helpful when trying to come up with devious tricks.


.. _pull-request-formatting:

代码格式
~~~~~~~~~~~~~~~

Code formatting

.. tab:: 中文

    为了避免浪费时间争论代码格式问题，我们使用 `black <https://github.com/psf/black>`__ 以及其他工具来自动将所有代码格式化为标准样式。在编辑代码时，你可以随意处理空白字符；然后在提交之前，只需运行：

    .. code-block::

        pip install -U pre-commit
        pre-commit

    来自动修复格式问题。（如果忘记了也没关系——当你提交 pull request 时，我们会自动检查并提醒你。）希望这能让你专注于更重要的样式问题，比如选择合适的命名、编写有用的注释，以及确保你的 docstring 格式正确。（black 不会重新格式化注释或 docstring。）

    如果你愿意，你甚至可以在提交前让 pre-commit 自动运行，只需运行：

    .. code-block::

        pre-commit install

    这样，在 git 提交之前，pre-commit 就会自动运行。你随时可以通过运行以下命令卸载 pre-commit 钩子：

    .. code-block::

        pre-commit uninstall

    偶尔，你可能需要覆盖 black 格式化。为此，你可以在代码中添加 ``# fmt: off`` 和 ``# fmt: on`` 注释。

    如果你想查看 black 会做出哪些更改，可以使用：

    .. code-block::

        black --diff trio

    （``--diff`` 会显示差异，而默认模式则是直接修复文件。）

    此外，在某些情况下，你可能需要禁用 isort 更改导入顺序。为此，你可以添加 ``# isort: split`` 注释。更多信息，请参见 `isort 的文档 <https://pycqa.github.io/isort/docs/configuration/action_comments.html>`__。

.. tab:: 英文

    Instead of wasting time arguing about code formatting, we use `black
    <https://github.com/psf/black>`__ as well as other tools to automatically
    format all our code to a standard style. While you're editing code you
    can be as sloppy as you like about whitespace; and then before you commit,
    just run:

    .. code-block::

        pip install -U pre-commit
        pre-commit

    to fix it up. (And don't worry if you forget – when you submit a pull
    request then we'll automatically check and remind you.) Hopefully this
    will let you focus on more important style issues like choosing good
    names, writing useful comments, and making sure your docstrings are
    nicely formatted. (black doesn't reformat comments or docstrings.)

    If you would like, you can even have pre-commit run before you commit by
    running:

    .. code-block::

        pre-commit install

    and now pre-commit will run before git commits. You can uninstall the
    pre-commit hook at any time by running:

    .. code-block::

        pre-commit uninstall


    Very occasionally, you'll want to override black formatting. To do so,
    you can can add ``# fmt: off`` and ``# fmt: on`` comments.

    If you want to see what changes black will make, you can use:

    .. code-block::

        black --diff trio

    (``--diff`` displays a diff, versus the default mode which fixes files
    in-place.)


    Additionally, in some cases it is necessary to disable isort changing the
    order of imports. To do so you can add ``# isort: split`` comments.
    For more information, please see `isort's docs <https://pycqa.github.io/isort/docs/configuration/action_comments.html>`__.


.. _pull-request-release-notes:

发布说明
~~~~~~~~~~~~~

Release notes

.. tab:: 中文

    我们使用 `towncrier <https://github.com/hawkowl/towncrier>`__ 来管理我们的 `发布说明 <https://trio.readthedocs.io/en/latest/history.html>`__。
    基本上，每个对用户可见的 pull request 都应该在 ``newsfragments/`` 目录中添加一个简短的文件，描述更改，文件名应类似于 ``<ISSUE NUMBER>.<TYPE>.rst``。有关详细信息，请参阅 `newsfragments/README.rst <https://github.com/python-trio/trio/blob/main/newsfragments/README.rst>`__。通过这种方式，我们可以在开发过程中保持一份良好的更改列表，这让发布经理很高兴，也意味着我们能更频繁地发布版本，从而使你的更改能更快地到达用户手中。

.. tab:: 英文

    We use `towncrier <https://github.com/hawkowl/towncrier>`__ to manage
    our `release notes <https://trio.readthedocs.io/en/latest/history.html>`__.
    Basically, every pull request that has a user
    visible effect should add a short file to the ``newsfragments/``
    directory describing the change, with a name like ``<ISSUE
    NUMBER>.<TYPE>.rst``. See `newsfragments/README.rst
    <https://github.com/python-trio/trio/blob/main/newsfragments/README.rst>`__
    for details. This way we can keep a good list of changes as we go,
    which makes the release manager happy, which means we get more
    frequent releases, which means your change gets into users' hands
    faster.


.. _pull-request-commit-messages:

提交消息
~~~~~~~~~~~~~~~

Commit messages

.. tab:: 中文

    我们不强制要求提交信息采用特定格式。在你的提交信息中，尽量提供上下文，以解释 *为什么* 做出某个更改。

    发布说明的目标受众是用户，他们希望了解可能影响他们使用库的更改，或者在升级后想弄明白为什么发生了某些变化。

    提交信息的目标受众是某个无助的开发者（想象一下：六个月后…或五年后的你），他们试图弄清楚为什么某些代码是这样写的。 *强烈* 建议在提交信息中包含指向问题的链接以及任何其他导致该提交的讨论。

.. tab:: 英文

    We don't enforce any particular format on commit messages. In your
    commit messages, try to give the context to explain *why* a change was
    made.

    The target audience for release notes is users, who want to find out
    about changes that might affect how they use the library, or who are
    trying to figure out why something changed after they upgraded.

    The target audience for commit messages is some hapless developer
    (think: you in six months... or five years) who is trying to figure
    out why some code looks the way it does. Including links to issues and
    any other discussion that led up to the commit is *strongly*
    recommended.


.. _pull-request-docs:

文档
~~~~~~~~~~~~~

Documentation

.. tab:: 中文

  我们以提供友好且全面的文档为荣。文档存储在 ``docs/source/*.rst`` 中，并使用 `Sphinx <http://www.sphinx-doc.org/>`__ 和 `sphinxcontrib-trio <https://sphinxcontrib-trio.readthedocs.io/en/latest/>`__ 扩展进行渲染。文档托管在 `Read the Docs <https://readthedocs.org/>`__ 上，并会在每次提交后自动重新构建。

  对于文档字符串，我们使用 `Google 文档字符串格式 <https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google-style-python-docstrings>`__。如果你添加了新的函数或类，文档不会自动更新：你至少需要在适当的位置添加一行 ``.. autofunction:: <your function>``。在许多情况下，最好还加入一些更长形式的叙述性文档。

  我们启用了 Sphinx 的“nitpick 模式”，该模式会将悬挂的引用视为错误 – 这有助于捕获拼写错误。（当你提交 PR 时，系统会自动检查这一点。）如果你故意想允许悬挂的引用，可以将其添加到 ``docs/source/conf.py`` 中的 `nitpick_ignore <http://www.sphinx-doc.org/en/stable/config.html#confval-nitpick_ignore>`__ 白名单中。

  要在本地构建文档，可以使用我们的 ``docs-requirements.txt`` 文件安装所有必需的包（可能需要使用虚拟环境）。安装后，可以在文档目录中使用 ``make html`` 构建文档。整个过程可能像这样：

  .. code-block::

      cd path/to/project/checkout/
      pip install -r docs-requirements.txt
      cd docs
      make html

  然后，你可以使用 Python 内建的 HTTP 服务器浏览文档：
  ``python -m http.server 8000 --bind 127.0.0.1 --directory build/html``
  并在浏览器中打开 ``http://127.0.0.1:8000/``。

.. tab:: 英文

    We take pride in providing friendly and comprehensive documentation.
    Documentation is stored in ``docs/source/*.rst`` and is rendered using
    `Sphinx <http://www.sphinx-doc.org/>`__ with the `sphinxcontrib-trio
    <https://sphinxcontrib-trio.readthedocs.io/en/latest/>`__ extension.
    Documentation is hosted at `Read the Docs
    <https://readthedocs.org/>`__, who take care of automatically
    rebuilding it after every commit.

    For docstrings, we use `the Google docstring format
    <https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google-style-python-docstrings>`__.
    If you add a new function or class, there's no mechanism for
    automatically adding that to the docs: you'll have to at least add a
    line like ``.. autofunction:: <your function>`` in the appropriate
    place. In many cases it's also nice to add some longer-form narrative
    documentation around that.

    We enable Sphinx's "nitpick mode", which turns dangling references
    into an error – this helps catch typos. (This will be automatically
    checked when your PR is submitted.) If you intentionally want to allow
    a dangling reference, you can add it to the `nitpick_ignore
    <http://www.sphinx-doc.org/en/stable/config.html#confval-nitpick_ignore>`__
    whitelist in ``docs/source/conf.py``.

    To build the docs locally, use our handy ``docs-requirements.txt``
    file to install all of the required packages (possibly using a
    virtualenv). After that, build the docs using ``make html`` in the
    docs directory. The whole process might look something like this:

    .. code-block::

        cd path/to/project/checkout/
        pip install -r docs-requirements.txt
        cd docs
        make html

    You can then browse the docs using Python's builtin http server:
    ``python -m http.server 8000 --bind 127.0.0.1 --directory build/html``
    and then opening ``http://127.0.0.1:8000/`` in your web browser.

.. _joining-the-team:

加入团队
----------------

Joining the team

.. tab:: 中文

    在你的第一个 PR 合并后，你应该会收到一个加入 ``python-trio`` 组织的 Github 邀请。如果没有收到，问题不在你，是我们这边的失误。可以在聊天中提醒我们，或者 `给 @njsmith 发送电子邮件 <mailto:njs@pobox.com>`__，我们会尽快修复。

    是否接受邀请完全由你决定，如果你接受，欢迎你根据自己的意愿参与，多少都可以。我们发出邀请是因为我们希望你能加入我们，一起让 Python 并发变得更加友好和强大，但没有压力：人生太短暂，不能在自己不感兴趣的事情上浪费志愿时间。

    在这个时候，人们通常会有一些问题。

    **你怎么能信任我拥有这种权限？如果我搞砸了怎么办？！**

    放松，你可以的！我们会支持你。记住，这只是软件，一切都有版本控制：最坏的情况就是我们回滚并集思广益，避免再次发生同样的问题。我们认为，欢迎新成员并帮助他们成长，比担心偶尔的小失误更为重要。

    **我觉得我不配得到这个。**

    决定权在你，但如果我们认为你不配，我们是不会邀请你的。

    **如果我接受邀请，具体会发生什么？点击错了按钮就会把一切搞垮吗？**

    具体来说，如果你接受邀请，将会有以下三个效果：

    * 你可以管理所有 ``python-trio`` 项目的问题（通过标记、关闭等方式）。

    * 你可以在所有 ``python-trio`` 项目中合并 PR，只要所有测试都通过，就可以点击 Github 上的大绿色“合并”按钮。

    * 它会自动让你订阅 ``python-trio`` 仓库的通知（但你也可以通过 Github 界面取消订阅）。

    需要注意的是，接受邀请并不会让你在没有提交 PR 的情况下直接推送更改，也不会让你合并未通过测试的 PR —— 这一点是通过 Github 的“分支保护”功能来强制执行的，这适用于从新贡献者到项目创始人的所有人。

    **好的，这是我能做的，但是我应该做什么呢？**

    简短的回答：做你感到舒适的事情。

    我们确实有一条规则，这是大多数 F/OSS 项目使用的规则：不要合并自己的 PR。我们发现，由其他人审查每个 PR 会导致更好的质量。

    除此之外，一切都取决于你自己。如果你觉得自己对复杂的代码更改了解不够，完全不必强迫自己去审查 —— 你可以先浏览一遍，做一些评论，即使你不打算做出最终的合并或不合并的决定。或者你可以只处理一些简单的文档修复和给问题添加标签，这也很有帮助。如果在参与一段时间后，你开始觉得自己对项目的运作有了更好的理解，并且想要做得更多，那太好了；如果没有，那也没关系。

    如果在任何时候你不确定是否某个行为合适，可以随时提问。例如，完全可以接受在第一次审查 PR 时，你希望让其他人检查一下你的工作，然后再点击合并按钮。

    我知道的关于审查 Pull Request 的最佳文章是 Sage Sharp 的 `The gentle art of patch review
    <http://sage.thesharps.us/2014/09/01/the-gentle-art-of-patch-review/>`__。 `node.js 指南
    <https://github.com/nodejs/node/blob/master/doc/guides/contributing/pull-requests.md#reviewing-pull-requests>`__
    也有一些很好的建议， `这篇博客文章 <http://verraes.net/2013/10/pre-merge-code-reviews/>`__ 也是如此。

.. tab:: 英文

    After your first PR is merged, you should receive a Github invitation
    to join the ``python-trio`` organization. If you don't, that's not
    your fault, it's because we made a mistake on our end. Give us a
    nudge on chat or `send @njsmith an email <mailto:njs@pobox.com>`__ and
    we'll fix it.

    It's totally up to you whether you accept or not, and if you do
    accept, you're welcome to participate as much or as little as you
    want. We're offering the invitation because we'd love for you to join
    us in making Python concurrency more friendly and robust, but there's
    no pressure: life is too short to spend volunteer time on things that
    you don't find fulfilling.

    At this point people tend to have questions.

    **How can you trust me with this kind of power? What if I mess
    everything up?!?**

    Relax, you got this! And we've got your back. Remember, it's just
    software, and everything's in version control: worst case we'll just
    roll things back and brainstorm ways to avoid the issue happening
    again. We think it's more important to welcome people and help them
    grow than to worry about the occasional minor mishap.

    **I don't think I really deserve this.**

    It's up to you, but we wouldn't be offering if we didn't think
    you did.

    **What exactly happens if I accept? Does it mean I'll break everything
    if I click the wrong button?**

    Concretely, if you accept the invitation, this does three things:

    * It lets you manage incoming issues on all of the ``python-trio``
      projects by labelling them, closing them, etc.

    * It lets you merge pull requests on all of the ``python-trio``
      projects by clicking Github's big green "Merge" button, but only if
      all their tests have passed.

    * It automatically subscribes you to notifications on the
      ``python-trio`` repositories (but you can unsubscribe again if you
      want through the Github interface)

    Note that it does *not* allow you to push changes directly to Github
    without submitting a PR, and it doesn't let you merge broken PRs –
    this is enforced through Github's "branch protection" feature, and it
    applies to everyone from the newest contributor up to the project
    founder.

    **Okay, that's what I CAN do, but what SHOULD I do?**

    Short answer: whatever you feel comfortable with.

    We do have one rule, which is the same one most F/OSS projects use:
    don't merge your own PRs. We find that having another person look at
    each PR leads to better quality.

    Beyond that, it all comes down to what you feel up to. If you don't
    feel like you know enough to review a complex code change, then you
    don't have to – you can just look it over and make some comments, even
    if you don't feel up to making the final merge/no-merge decision. Or
    you can just stick to merging trivial doc fixes and adding tags to
    issues, that's helpful too. If after hanging around for a while you
    start to feel like you have better handle on how things work and want
    to start doing more, that's excellent; if it doesn't happen, that's
    fine too.

    If at any point you're unsure about whether doing something would be
    appropriate, feel free to ask. For example, it's *totally OK* if the
    first time you review a PR, you want someone else to check over your
    work before you hit the merge button.

    The best essay I know about reviewing pull request's is Sage Sharp's
    `The gentle art of patch review
    <http://sage.thesharps.us/2014/09/01/the-gentle-art-of-patch-review/>`__.
    The `node.js guide
    <https://github.com/nodejs/node/blob/master/doc/guides/contributing/pull-requests.md#reviewing-pull-requests>`__
    also has some good suggestions, and `so does this blog post
    <http://verraes.net/2013/10/pre-merge-code-reviews/>`__.


管理问题
---------------

Managing issues

.. tab:: 中文

    随着问题的提出，它们需要得到响应、跟踪，并且 —— 希望如此！ —— 最终被关闭。

    一般来说，每个未关闭的问题都应该代表我们需要完成的某项任务。有时，这个任务可能是“弄清楚该怎么做”，或者甚至是“弄清楚我们是否想解决这个问题”；有时可能是“回答这个人的问题”。但是，如果没有后续需要做的事情，那么这个问题就应该关闭。

.. tab:: 英文

    As issues come in, they need to be responded to, tracked, and –
    hopefully! – eventually closed.

    As a general rule, each open issue should represent some kind of task
    that we need to do. Sometimes that task might be "figure out what to
    do here", or even "figure out whether we want to address this issue";
    sometimes it will be "answer this person's question". But if there's
    no followup to be done, then the issue should be closed.


问题标签
~~~~~~~~~~~~

Issue labels

.. tab:: 中文

    Trio 仓库特别使用了一些标签来帮助跟踪问题。目前的标签列表有些临时，并且随着时间的推移可能会变得不再有用 —— 如果你想到一个新的有用标签、为现有标签想出一个更好的名字，或者认为某个标签已经不再适用，请提出意见。

    * `good first issue
      <https://github.com/python-trio/trio/labels/good%20first%20issue>`__：
      用于标记相对简单的问题，适合新贡献者开始。

    * `todo soon
      <https://github.com/python-trio/trio/labels/todo%20soon>`__：
      标记那些已经不再有疑问是否或如何进行的任务，只是等待某人动手解决。

    * `missing piece
      <https://github.com/python-trio/trio/labels/missing%20piece>`__：
      通常用于标记缺少的重要自包含功能模块。如果你正在寻找更具挑战性的项目来处理，这个标签可能会有用。

    * `potential API breaker
      <https://github.com/python-trio/trio/labels/potential%20API%20breaker>`__：
      如标签所示。这很重要，因为这些问题是我们需要特别注意的，尤其是当 Trio 开始稳定下来时，尤其是在我们准备发布 1.0 版本之前。

    * `design discussion
      <https://github.com/python-trio/trio/labels/design%20discussion>`__：
      标记那些涉及重大设计问题的任务；如果你喜欢深入的理论讨论和 API 设计的探讨，浏览这个标签可能会很有趣。

    * `polish <https://github.com/python-trio/trio/labels/polish>`__：
      标记那些最终需要解决的问题，因为它们是正确的做法，但它们处理的是边缘情况，不是最小可行产品的必要部分。有时与 "user happiness"（用户体验）标签重叠。

    * `user happiness
      <https://github.com/python-trio/trio/labels/user%20happiness>`__：
      仅从名称来看，这个标签可能适用于任何 bug（修复 bug 肯定会让用户更开心！），但我们指的并非如此。这个标签用于标记那些可能让用户“踢到铁板”的地方，或者那些会让用户惊讶并感到兴奋的“生活质量”功能 —— 比如能够“即插即用”的高级测试工具。

.. tab:: 英文

    The Trio repository in particular uses a number of labels to try and
    keep track of issues. The current list is somewhat ad hoc, and may or
    may not remain useful over time – if you think of a new label that
    would be useful, a better name for an existing label, or think a label
    has outlived its usefulness, then speak up.

    * `good first issue
      <https://github.com/python-trio/trio/labels/good%20first%20issue>`__:
      Used to mark issues that are relatively straightforward, and could
      be good places for a new contributor to start.

    * `todo soon
      <https://github.com/python-trio/trio/labels/todo%20soon>`__: This
      marks issues where there aren't questions left about whether or how
      to do it, it's just waiting for someone to dig in and do the work.

    * `missing piece
      <https://github.com/python-trio/trio/labels/missing%20piece>`__:
      This generally marks significant self-contained chunks of missing
      functionality. If you're looking for a more ambitious project to
      work on, this might be useful.

    * `potential API breaker
      <https://github.com/python-trio/trio/labels/potential%20API%20breaker>`__:
      What it says. This is useful because these are issues that we'll
      want to make sure to review aggressively as Trio starts to
      stabilize, and certainly before we reach 1.0.

    * `design discussion
      <https://github.com/python-trio/trio/labels/design%20discussion>`__:
      This marks issues where there's significant design questions to be
      discussed; if you like meaty theoretical debates and discussions of
      API design, then browsing this might be interesting.

    * `polish <https://github.com/python-trio/trio/labels/polish>`__:
      Marks issues that it'd be nice to resolve eventually, because it's
      the Right Thing To Do, but it's addressing a kind of edge case thing
      that isn't necessary for a minimum viable product. Sometimes
      overlaps with "user happiness".

    * `user happiness
      <https://github.com/python-trio/trio/labels/user%20happiness>`__:
      From the name alone, this could apply to any bug (users certainly
      are happier when you fix bugs!), but that's not what we mean. This
      label is used for issues involving places where users stub their
      toes, or for the kinds of quality-of-life features that leave users
      surprised and excited – e.g. fancy testing tools that Just Work.


治理
----------

Governance

.. tab:: 中文

    `Nathaniel J. Smith <https://github.com/njsmith>`__ 是 Trio 的 `BDFL <https://en.wikipedia.org/wiki/Benevolent_dictator_for_life>`__ （终身仁慈独裁者）。如果项目发展到需要更多结构化管理的程度，我们将考虑其他方案。

    .. 可能的未来参考内容：

      """
      第一次跳入一个陌生的代码库（或者任何代码库）可能会让人感到害怕。
      更何况，如果这是你第一次贡献开源，可能会更加可怕！

      但我们在 webpack 相信：

          任何人（即使是非技术人员）都应该感到欢迎来贡献。
          不管你决定以什么方式贡献，它应该是有趣和愉快的！
          即使是你的第一次提交，你也将收获更多关于 webpack 或 JavaScript 的理解。
          因此，你可能会在这个过程中变得更好的开发者、写作者、设计师等，
          我们致力于帮助促进这种成长。
      """

      冒名顶替症候群免责声明
      https://github.com/Unidata/MetPy#contributing

      提交检查清单
      https://github.com/nayafia/contributing-template/blob/master/CONTRIBUTING-template.md

      https://medium.com/the-node-js-collection/healthy-open-source-967fa8be7951

      http://sweng.the-davies.net/Home/rustys-api-design-manifesto

.. tab:: 英文

    `Nathaniel J. Smith <https://github.com/njsmith>`__ is the Trio `BDFL
    <https://en.wikipedia.org/wiki/Benevolent_dictator_for_life>`__. If
    the project grows to the point where we'd benefit from more structure,
    then we'll figure something out.


    .. Possible references for future additions:

      """
      Jumping into an unfamiliar codebase (or any for that matter) for the first time can be scary.
      Plus, if it's your first time contributing to open source, it can even be scarier!

      But, we at webpack believe:

          Any (even non-technical) individual should feel welcome to contribute.
          However you decide to contribute, it should be fun and enjoyable for you!
          Even after your first commit, you will walk away understanding more about webpack or JavaScript.
          Consequently, you could become a better developer, writer,
            designer, etc. along the way, and we are committed to helping
            foster this growth.
      """

      imposter syndrome disclaimer
      https://github.com/Unidata/MetPy#contributing

      checklist
      https://github.com/nayafia/contributing-template/blob/master/CONTRIBUTING-template.md

      https://medium.com/the-node-js-collection/healthy-open-source-967fa8be7951

      http://sweng.the-davies.net/Home/rustys-api-design-manifesto
