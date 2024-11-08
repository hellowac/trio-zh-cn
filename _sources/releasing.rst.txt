.. _releasing:

准备发布
-------------------

**Preparing a release**

.. tab:: 中文

   发布时需要做的事情：

   * 在 Gitter 上宣布发布意图

   * 检查是否有未完成的 Issues / Pull Requests 需要包含在发布中

     + 在这些完成后回来继续

     + … 或者忽略它们，下周再做一次发布

   * 检查是否有“足够长时间前”（两个月或两个版本，较长者）的废弃功能

     + 移除受影响的代码

   * 做实际的发布变更集

     + 提升版本号

       - 根据语义版本控制规则递增版本号

       - 移除版本号中的 ``+dev`` 标签

     + 运行 ``towncrier``

       - 审查历史变更

       - 使用 ``git rm`` 删除现在过时的 newfragments

     + 提交更改

   * 推送到你的个人仓库

   * 创建一个 Pull Request 到 ``python-trio/trio`` 的 "main" 分支

   * 确保所有检查都已通过

   * 打标签为 vVERSION，并将标签推送到 ``python-trio/trio`` （不要推送到你的个人仓库）

   * 批准发布工作流的发布任务

   * 在同一个 Pull Request 中更新版本号

     + 在末尾添加 ``+dev`` 标签

   * 合并发布 Pull Request

   * 创建 GitHub 发布（去标签页并点击“从标签创建发布”）

     + 将 ``history.rst`` 中的新内容粘贴进去，并转换为 markdown 格式：将部分内容下的章节转换为 ``---``，更新链接为纯链接，其他必要的更改。

     + 包括任何其他可能相关的内容，例如链接到最新版本和当前版本之间的提交记录。

   * 在 Gitter 上宣布发布

.. tab:: 英文

   Things to do for releasing:

   * announce intent to release on gitter

   * check for open issues / pull requests that really should be in the release

      + come back when these are done

      + … or ignore them and do another release next week

   * check for deprecations "long enough ago" (two months or two releases, whichever is longer)

      + remove affected code

   * Do the actual release changeset

      + bump version number

         - increment as per Semantic Versioning rules

         - remove ``+dev`` tag from version number

      + Run ``towncrier``

         - review history change

         - ``git rm`` the now outdated newfragments

      + commit

   * push to your personal repository

   * create pull request to ``python-trio/trio``'s "main" branch

   * verify that all checks succeeded

   * tag with vVERSION, push tag on ``python-trio/trio`` (not on your personal repository)

   * approve the release workflow's publish job

   * update version number in the same pull request

      + add ``+dev`` tag to the end

   * merge the release pull request

   * make a GitHub release (go to the tag and press "Create release from tag")

      + paste in the new content in ``history.rst`` and convert it to markdown: turn the parts under section into ``---``, update links to just be the links, and whatever else is necessary.

      + include anything else that might be pertinent, like a link to the commits between the latest and current release.

   * announce on gitter
