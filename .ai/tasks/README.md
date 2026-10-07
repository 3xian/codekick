# Task Artifacts

复杂任务才创建 task artifact。

适合创建的情况：

- 跨模块；
- 需求复杂或有歧义；
- 需要多轮调查；
- 需要第二天继续；
- 可能切换模型/会话；
- 风险较高；
- 需要完整保留验证证据。

使用 `templates/TASK.md`，或运行：

```bash
python scripts/new-task.py JIRA-1234 "订单审核增加信用额度校验"
```

任务完成后：

1. Verification 标记为 `verified` / `partial` / `failed`；
2. 有长期价值的隐含知识提炼到 `../KNOWLEDGE.md`；
3. 新的稳定项目结构补充到 `../PROJECT.md`；
4. task artifact 本身可以继续保留作为历史记录，但默认不进入后续任务上下文。
