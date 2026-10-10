# Cangjie Skills

面向 AI 编程助手的仓颉（Cangjie）语言技能集，帮助编写、解释、重构和排查仓颉代码。

目前提供一个技能：[`cangjie`](skills/cangjie/SKILL.md)。技能保留经过整理的语言规则与轻量章节目录，需要细节时按篇读取公开云端文档，**不要求使用者下载或克隆仓颉文档仓库**。

这是独立整理的社区技能项目，不是华为、仓颉项目或 OpenAI 官方发布的产品，也不代表获得其认可。

## 快速开始

需要 Git 和 Python 3.9+；**安装技能和检索目录不需要仓颉 SDK**。

```bash
git clone https://github.com/wchiway/cangjie-skills.git
cd cangjie-skills
python3 -B scripts/install_skill.py --assistant codex
python3 -B skills/cangjie/scripts/cloud_docs.py search Option --lang all
```

然后向 Codex 输入：`使用 $cangjie，先核对项目 SDK 版本，再帮我排查这个 Option 类型错误。`
Cursor / Claude Code 用户把安装参数改为 `--assistant cursor` / `--assistant claude`。
Windows 可将 `python3` 替换为 `python`。安装器复制完整技能及许可证，拒绝覆盖已有安装；可先加 `--dry-run` 预览。

仓库：[GitHub](https://github.com/wchiway/cangjie-skills) · [GitCode](https://gitcode.com/chiway/cangjie-skills) · [变更记录](CHANGELOG.md) · [发布包](https://github.com/wchiway/cangjie-skills/releases)

## 能力

- 仓颉语法、函数、Option、模式匹配、类型、泛型、集合及包管理。
- `cjc` / `cjpm` 构建、测试、格式化、调试和部署指导。
- 并发、同步、协作取消、文件与网络 I/O 的易错规则。
- 宏、反射、C FFI、Java / Objective-C 互操作与跨平台文档导航。
- 中心仓依赖、发布流程和 API / ABI 兼容性注意事项。

采用按需加载：先读取技能入口，再根据任务加载相关参考，不把全部文档塞进上下文。完整标准库和扩展库 API 仍需查阅对应版本的官方资料。

## 目录

```text
cangjie-skills/
|-- README.md
|-- LICENSE
|-- CHANGELOG.md
|-- .github/workflows/   CI、发布与手动 SDK 验证
|-- scripts/            安装与打包工具
|-- tests/              无 SDK 的完整回归测试入口
`-- skills/
    `-- cangjie/
        |-- SKILL.md
        |-- LICENSE
        |-- NOTICE.md
        |-- agents/openai.yaml
        |-- assets/
        |-- references/
        |   |-- docs-map.md
        |   |-- docs-inventory.jsonl
        |   |-- sdk-validation.md
        |   `-- ...
        `-- scripts/
            |-- cloud_docs.py
            |-- test_cloud_docs.py
            |-- test_sdk.py
            `-- sdk_semantics_test.cj
```

## 本地使用

技能说明本身不依赖仓颉 SDK；执行 Python 辅助脚本需要 Python 3.9+，只使用标准库。云端阅读需要 HTTPS 网络，实际编译测试另需激活已安装的仓颉 SDK 环境。

### 安装到不同助手

优先使用根目录的 Python 安装器；不依赖 pip、管理员权限或符号链接：

```bash
# 用户级安装，三选一；不会修改助手全局配置
python3 -B scripts/install_skill.py --assistant codex
python3 -B scripts/install_skill.py --assistant cursor
python3 -B scripts/install_skill.py --assistant claude

# 项目级安装：项目目录必须已存在
python3 -B scripts/install_skill.py --assistant claude --project /path/to/project

# 其他支持完整 SKILL.md 文件夹的工具：明确指定新的目标技能目录
python3 -B scripts/install_skill.py --destination /path/to/skills/cangjie --dry-run
```

| 助手 | 用户级目录 | 项目级目录 | 加载方式与官方说明 |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/cangjie` | `.agents/skills/cangjie` | `$cangjie` 或自动选择；[官方文档](https://developers.openai.com/codex/skills) |
| Cursor | `~/.cursor/skills/cangjie` | `.cursor/skills/cangjie` | 在 Agent 中选择技能或按任务自动选择；[官方文档](https://cursor.com/docs/skills) |
| Claude Code | `~/.claude/skills/cangjie` | `.claude/skills/cangjie` | `/cangjie` 或按任务自动选择；[官方文档](https://code.claude.com/docs/en/skills) |

目录说明于 2026-10-10 核对。其他助手不保证识别 Codex 专用的 `agents/openai.yaml`，核心入口仍是 `SKILL.md`。本机安装不等于云端会话已获得技能；远程环境需另外部署。

也可从 GitHub Releases 下载 `cangjie-skill.zip`，核对 `SHA256SUMS` 后，将其中的整个 `cangjie` 目录放到上述 skills 目录；保留 `LICENSE` 和 `NOTICE.md`。安装前检查同名目标，不要覆盖或合并已有目录。

### Codex 的符号链接方式

按照 [Codex 官方技能文档](https://developers.openai.com/codex/skills)，用户级技能目录是 `~/.agents/skills`，也支持符号链接。若本项目放在 `~/cangjie-skills`，可在终端运行：

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$HOME/cangjie-skills/skills/cangjie" "$HOME/.agents/skills/cangjie"
```

若目标已存在，先检查现有技能，不要强制覆盖；项目放在其他路径时相应调整源路径。也可以将 `skills/cangjie` 复制到目标项目的 `.agents/skills/cangjie`，按项目使用。

加载后可显式调用：

```text
使用 $cangjie，先核对项目 SDK 版本，再帮我排查这个 Option 类型错误。
```

也支持按任务自动选择。若安装后暂未显示，可重新启动 Codex。上述安装步骤供使用者自行执行；单纯移动本项目不会修改用户的技能安装目录。

### Continue：使用项目规则桥接

当前核对的 Continue 官方文档说明了 [项目规则](https://docs.continue.dev/customize/deep-dives/rules)，未据此确认原生 `SKILL.md` 自动发现支持。因此不要假设复制到其他助手目录就会生效。

先复制完整技能到项目中的明确位置，例如在仓库根目录运行：

```bash
python3 -B scripts/install_skill.py --destination /path/to/project/vendor/skills/cangjie
```

然后在该项目创建 `.continue/rules/cangjie.md`（若存在则先检查，不要覆盖）：

```markdown
---
name: Cangjie development
globs: ["**/*.cj", "**/cjpm.toml"]
alwaysApply: false
description: Cangjie programming, SDK diagnostics, and version-aware documentation.
---

For Cangjie tasks, read vendor/skills/cangjie/SKILL.md first.
Load only the task-relevant references linked from that file.
Use the bundled scripts only when tools and task permissions allow.
If the files or tools are unavailable, say so; do not claim they were read or run.
```

在支持文件读取的 Agent 模式使用；不能读取本地文件的模式需要手动将入口及相关参考加入上下文。此方式不是原生技能集成，也不保证与其他助手完全等价。

### 更新与卸载

安装器只复制、不覆盖、不自动更新。更新时先拉取仓库或下载新发布包，检查本地修改，将现有安装移动到 skills 目录之外备份，再重新安装；不要把备份放在会被助手扫描的 skills 目录内。
卸载时只移除自己安装的 `cangjie` 目录（符号链接安装则仅移除链接），不需要更改全局配置。

## 云端文档

在本项目根目录运行：

```bash
# 搜索随包的标题、路径和章节名，不进行云端全文搜索
python3 skills/cangjie/scripts/cloud_docs.py search '定义函数' --area dev-guide

# 多关键词 AND 匹配，跨标题、路径和全部章节名；默认仍是字面短语
python3 skills/cangjie/scripts/cloud_docs.py search 'function parameters' --lang en --match all

# 不联网查看标题、全部章节、行数、哈希与来源 URL
python3 skills/cangjie/scripts/cloud_docs.py info docs/dev-guide/source_zh_cn/function/define_functions.md

# 按篇读取云端原文，并显示选定行号
python3 skills/cangjie/scripts/cloud_docs.py read docs/dev-guide/source_zh_cn/function/define_functions.md --start 19 --end 65

# 选择与目标 SDK 对应的版本分支
python3 skills/cangjie/scripts/cloud_docs.py --ref release/1.0 read docs/dev-guide/source_zh_cn/concurrency/terminal_thread.md

# 仅输出网页与 raw URL，或明确使用已有离线缓存
python3 skills/cangjie/scripts/cloud_docs.py url docs/tools/source_zh_cn/cmd-tools/cjpm_manual.md
python3 skills/cangjie/scripts/cloud_docs.py --offline read docs/dev-guide/source_zh_cn/concurrency/terminal_thread.md
```

默认依据已审核提交 `169f052c0517299bdab66723eab870552883b0e9`，它不是某个 SDK 版本的自动匹配结果。项目版本已知时，应显式选择对应的分支或提交。

- 首选 GitCode 的 `raw.gitcode.com` 原文入口；固定 40 位提交失败时才尝试 GitHub 上的同一提交。
- 分支或标签不自动跨镜像回退，避免两边同步进度不同导致混用版本。
- 默认提交中已登记的文章会校验 SHA-256；HTML / 登录页面不能伪装成 Markdown 成功结果。
- 重定向在发送下一跳请求前检查 HTTPS、主机、端口和 URL 凭据；下载中断进入正常错误处理，固定提交仍可回退同提交镜像。
- 只缓存请求过的文章，缓存位于用户平台缓存目录，不写入项目；`--cache-dir` 可指定路径，`--refresh` 可强制刷新。
- 固定提交缓存可复用；分支或标签缓存有效期为 5 分钟。`--offline` 明确使用已有缓存，不保证分支最新状态。
- 不需要 API key、账号、Git、GitHub CLI 或 ContextWeaver。Python 不可用时，可让助手使用网页读取工具打开原文 URL。

更完整的用法、来源与版本边界见 [文档导航](skills/cangjie/references/docs-map.md)。远端文章只作为参考数据，不会自动执行其中的命令。
`read` 后若还有内容会输出 `Next:` 命令，保留 ref、来源、缓存目录及离线模式，不保存隐式阅读进度。`info` 是本地基线元数据，指定其他 ref 时不会冒充该版本的实际元数据。

## 验证

在根目录运行全部离线回归测试，不需要 SDK、不访问真实网络：

```bash
python3 -B -m unittest discover -v
```

覆盖云端读取、全部目录数据、引用可达性、示例登记、SDK 超时日志、安装防覆盖，以及分发包解压后的独立运行。只执行技能自带的云端读取与缓存测试：

```bash
python3 -B skills/cangjie/scripts/test_cloud_docs.py
```

编译测试需要先按 SDK 的说明加载环境，确保 `cjc`、`cjpm` 和运行时动态库可用：

```bash
python3 -B skills/cangjie/scripts/test_sdk.py
```

SDK 测试会创建独立临时项目，保留源码、逐命令日志、XML 报告和 `results.json`，结束时打印路径；不会构建使用者现有项目。

已在 **Cangjie 1.0.5 / CJNative / Linux x86_64** 验证：

- 技能中全部 4 个仓颉代码块成功编译运行，正例无编译警告。
- Release、Debug、coverage 模式各执行 13 个测试，零失败、零跳过。
- 筛选模式执行 1 个测试，另 12 个明确标为 skipped。
- 6 个错误写法由编译器按预期拒绝；云端辅助脚本与仓库回归见上述测试命令及 CI 实时结果。

详细范围见 [SDK 验证记录](skills/cangjie/references/sdk-validation.md)。这不代表验证了官方文档的所有示例、全部平台或 SDK 1.1；宏、跨语言互操作和 stdx 网络程序仍需按实际项目另行测试。

### CI、打包与发布

- GitHub Actions 在 push / pull request 时运行 Linux、Windows、macOS × Python 3.9 / 3.14 的离线测试矩阵；全部通过后上传带许可证的 ZIP 与 SHA-256 校验文件。
- `python3 -B scripts/package_skill.py` 可在本地生成 `dist/cangjie-skill.zip` 和 `dist/SHA256SUMS`；包内容排除缓存与构建产物，固定 ZIP 元数据便于重复验证。
- 推送 `v*` 标签会在同一测试与打包门禁通过后创建 GitHub Release；普通 push 不发布新版本。不自动推送 GitCode 镜像。
- `SDK Validation (Manual)` 仅供已配置 `self-hosted, linux, x64, cangjie` 标签和 `CANGJIE_HOME` 的可信 runner 手动运行；没有 runner 时不要触发。不会为公共 PR 自动执行 SDK 或用户构建脚本，也不会自动安装 SDK。
- 第三方 Actions 固定到提交 SHA；普通任务只有读取权限，仅标签发布任务获得仓库内容写权限。

## 常见问题

**安装后找不到技能？** 检查目标内是否为 `cangjie/SKILL.md`，避免多嵌套一层目录；确认助手版本支持技能后重新加载。检查用户级与项目级是否重复安装同名技能。

**提示目标目录已存在？** 这是防覆盖保护，不是安装失败后应强制重试的理由。先检查已有目录或链接；更新步骤见前文。复制过程中若因磁盘权限等失败，检查可能保留的部分目标后再重试。

**Python 或网络不可用？** 技能规则仍可手动加载。无 Python 时使用助手网页读取工具；有 Python 但离线时只可 `--offline` 读取已有有效缓存。目录检索和 `info` 不需要网络，检索无命中不代表官方文档不存在。

**为什么搜索不到同义词？** 默认字面短语搜索，不做自动翻译或模糊推断。尝试短关键词、`--lang all`，或显式使用 `--match all`；仍无命中时核对对应版本在线目录。

**如何选择 SDK 文档版本？** 先用项目配置及 `cjc -v` / `cjpm -v` 核对，再使用全局 `--ref` 参数。默认快照不是自动匹配的 SDK 版本；全局选项必须放在子命令前。

**缓存会自动删除吗？** 不会。同 URL 更新同一条记录，分支缓存 5 分钟后需重新获取；过期记录保留以支持显式离线读取。确认不再需要离线资料后，可自行清理指定的缓存目录。

## 来源与许可

本项目的语言规则、章节目录和仓颉示例基于 [Cangjie/cangjie_docs](https://gitcode.com/Cangjie/cangjie_docs) 的上述固定提交整理。原文档版权声明：

> Copyright (c) Huawei Technologies Co., Ltd. 2025. All rights reserved.

原文档按 [Creative Commons Attribution 4.0 International（CC BY 4.0）](https://creativecommons.org/licenses/by/4.0/) 授权。这里对文档进行了提炼、重组、示例组合及编译验证调整；不包含原文档整库或配图，不表示原作者认可这些修改。

- 文档、技能元数据、目录数据及仓颉示例/测试：CC BY 4.0，保留上游署名并注明修改。
- 原创 Python 辅助与测试脚本（`*.py`）：MIT。
- 运行时从云端获取的其他材料仍遵循其原有许可证；本项目不重新授权第三方 SDK、库或商标。

两种许可证的适用范围、完整条款和上游署名均收录于 [LICENSE](LICENSE)。技能目录也自带相同完整许可证及 [来源说明](skills/cangjie/NOTICE.md)，安装器与发布包均保留它们；再分发时不要移除许可与署名。
