# CodeKick Quick Start

## 1. 复制到目标项目

将本仓库中的以下内容放到项目根目录：

```text
AGENTS.md
.ai/
skills/
templates/
scripts/
```

## 2. 第一次接手

要求 AI 执行：

```text
Read AGENTS.md, then follow skills/bootstrap/SKILL.md and build .ai/PROJECT.md.
Do a shallow onboarding only; do not attempt to fully understand the repository.
```

## 3. 理解一个问题

```text
Follow skills/understand/SKILL.md:
为什么订单取消后会释放库存？
```

## 4. 修改一个需求

```text
Follow skills/change/SKILL.md:
订单审核时增加客户信用额度校验。
```

## 5. 复杂任务

```bash
python scripts/new-task.py JIRA-1234 "订单审核增加信用额度校验"
```

随后让 AI 把调查过程持续写入 `.ai/tasks/JIRA-1234.md`。

## 6. 修改后验证

```text
Follow skills/verify/SKILL.md and verify the actual diff against the requirement.
```

## 7. 每次任务结束

只问两个问题：

1. 是否发现了以后能帮助导航的稳定项目结构？如果有，更新 PROJECT.md。
2. 是否发现了源码无法低成本重新推导的知识？如果有，更新 KNOWLEDGE.md。

其余信息不要长期保存。
