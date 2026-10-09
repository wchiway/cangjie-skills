# Cangjie Skills

面向 AI 编程助手的仓颉（Cangjie）语言技能集，帮助编写、解释、重构和排查仓颉代码。

目前提供一个技能：[`cangjie`](skills/cangjie/SKILL.md)。技能保留经过整理的语言规则与轻量章节目录，需要细节时按篇读取公开云端文档，**不要求使用者下载或克隆仓颉文档仓库**。

这是独立整理的社区技能项目，不是华为、仓颉项目或 OpenAI 官方发布的产品，也不代表获得其认可。

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
`-- skills/
    `-- cangjie/
        |-- SKILL.md
        |-- agents/openai.yaml
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

### 在 Codex 中加载

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

其他支持 `SKILL.md` 格式的助手可按其文档加载整个 `skills/cangjie` 文件夹；其自动发现机制和脚本执行能力需自行核对。

## 云端文档

在本项目根目录运行：

```bash
# 搜索随包的标题、路径和章节名，不进行云端全文搜索
python3 skills/cangjie/scripts/cloud_docs.py search '定义函数' --area dev-guide

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
- 只缓存请求过的文章，缓存位于用户平台缓存目录，不写入项目；`--cache-dir` 可指定路径，`--refresh` 可强制刷新。
- 固定提交缓存可复用；分支或标签缓存有效期为 5 分钟。`--offline` 明确使用已有缓存，不保证分支最新状态。
- 不需要 API key、账号、Git、GitHub CLI 或 ContextWeaver。Python 不可用时，可让助手使用网页读取工具打开原文 URL。

更完整的用法、来源与版本边界见 [文档导航](skills/cangjie/references/docs-map.md)。远端文章只作为参考数据，不会自动执行其中的命令。

## 验证

云端读取与缓存的回归测试不访问真实网络：

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
- 6 个错误写法由编译器按预期拒绝；18 项云端辅助脚本测试通过。

详细范围见 [SDK 验证记录](skills/cangjie/references/sdk-validation.md)。这不代表验证了官方文档的所有示例、全部平台或 SDK 1.1；宏、跨语言互操作和 stdx 网络程序仍需按实际项目另行测试。

## 来源与许可

本项目的语言规则、章节目录和仓颉示例基于 [Cangjie/cangjie_docs](https://gitcode.com/Cangjie/cangjie_docs) 的上述固定提交整理。原文档版权声明：

> Copyright (c) Huawei Technologies Co., Ltd. 2025. All rights reserved.

原文档按 [Creative Commons Attribution 4.0 International（CC BY 4.0）](https://creativecommons.org/licenses/by/4.0/) 授权。这里对文档进行了提炼、重组、示例组合及编译验证调整；不包含原文档整库或配图，不表示原作者认可这些修改。

- 文档、技能元数据、目录数据及仓颉示例/测试：CC BY 4.0，保留上游署名并注明修改。
- 原创 Python 辅助脚本（`skills/cangjie/scripts/*.py`）：MIT。
- 运行时从云端获取的其他材料仍遵循其原有许可证；本项目不重新授权第三方 SDK、库或商标。

两种许可证的适用范围、完整条款和上游署名均收录于 [LICENSE](LICENSE)。再分发时应一并保留 README、LICENSE 和来源说明；仅分发单个技能目录时也应附带许可文件。
