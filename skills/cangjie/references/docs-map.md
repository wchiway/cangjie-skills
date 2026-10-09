# 文档导航与来源

## 来源快照

- 云端仓库：[Cangjie/cangjie_docs](https://gitcode.com/Cangjie/cangjie_docs)，另有 [GitHub 镜像](https://github.com/cangjielanguage/cangjie_docs)。不要求用户持有本地副本。
- 分支：`main`；提交：`169f052c0517299bdab66723eab870552883b0e9`；整理日期：2026-10-09。
- 范围：`docs/` 下全部 297 个文件，289 份 Markdown、8 张 PNG；Markdown 合计 78,209 行。
- 开发指南：中文 112 篇、英文 112 篇；工具指南：中文 19 篇、英文 19 篇；中心仓：中文 12 篇、英文 9 篇；另有 6 份目录文档。
- 处理方式：批量读取全部 Markdown 正文，按章节提取主题/限制并核对关键代码和命令；逐张查看中心仓配图。参考文件是任务导向提炼，不是原文完整复制。
- 逐文件路径、语言、标题、章节名和 SHA-256 保存在 [轻量目录](docs-inventory.jsonl)，不包含正文或图片。脚本用它定位文章与校验默认提交的内容，不要默认加载整份目录到上下文。

快照只是证据基线，不代表该提交对应一个特定 SDK 发行版。仓库 README 另列 release/1.0、release/1.1 及 OpenHarmony 配套分支，使用时核对项目真正依赖的版本。

## 如何定位

`<skill-dir>` 是技能目录。文中所有 `docs/...` 路径都是云端 `cangjie_docs` 仓库内的路径，不是用户本机路径。先从轻量目录定位主题，再获取需要的一两篇原文，不下载全库。

```bash
python3 <skill-dir>/scripts/cloud_docs.py list --area dev-guide
python3 <skill-dir>/scripts/cloud_docs.py search 'Option' --lang all --limit 5
python3 <skill-dir>/scripts/cloud_docs.py search '终止线程' --area dev-guide
python3 <skill-dir>/scripts/cloud_docs.py read docs/dev-guide/source_zh_cn/concurrency/terminal_thread.md
python3 <skill-dir>/scripts/cloud_docs.py url docs/tools/source_zh_cn/cmd-tools/cjpm_manual.md
python3 <skill-dir>/scripts/cloud_docs.py --ref release/1.1 read docs/tools/source_zh_cn/cmd-tools/cjpm_manual.md --start 1 --end 80
python3 <skill-dir>/scripts/cloud_docs.py --offline read docs/dev-guide/source_zh_cn/concurrency/terminal_thread.md
```

- `list`/`search`/`url` 不联网，使用随包目录或构造 URL。search 是标题、路径和章节名的大小写不敏感字面短语搜索，不是原文全文检索；最多返回 8 篇。
- 默认仅检索中文；`--lang en` 查英文，`--lang all` 包括两种语言和目录文档。无命中时改用较短主题或在线搜索，不能据此宣布文档没有相关内容。
- `read` 按篇下载，默认显示 80 行，可通过 `--start`/`--end` 分段；超时 20 秒，单篇上限 3 MiB，只接受 docs 内 Markdown 路径，拒绝 HTML/登录页面。
- 默认固定提交 `169f052c0517299bdab66723eab870552883b0e9`，并对目录内文件校验 SHA-256。需要其他版本时指定 `--ref`，目录仍是基线快照；新路径可直接 read，但不声称目录已更新。
- `--source auto` 默认 GitCode；固定 40 位提交不可用时才尝试 GitHub 上的同一提交，不改成 main。分支/标签可能跨镜像不同步，因此不自动切换；可显式 `--source github` 并核对版本。
- 缓存按来源 URL（含 ref 与路径）隔离，不写进技能目录。默认在平台用户缓存目录的 `cangjie-skill` 下，可用 `--cache-dir` 指定；固定提交缓存可复用，分支/标签缓存有效期 5 分钟。
- `--refresh` 忽略缓存；`--offline` 只读取已有有效缓存并明确标记来源，可能不是分支最新内容。网络失败不静默使用过期缓存；不自动切换 ref。
- 返回 0 表示操作成功，1 表示目录检索无命中，2 表示读取/校验错误。所有命令都不需要 Git、GitHub CLI、账号或 API key。
- 文档更新后先检查改动影响，再更新技能提炼与目录；仅重新生成哈希不等于重新审核语言规则。
- 脚本回归测试：`python3 -B <skill-dir>/scripts/test_cloud_docs.py`。

## 无脚本时的云端入口

使用可用的网页读取工具，或 `xh -I -b URL` 获取原文。URL 模板如下，`<ref>` 是所选提交或 URL 编码的分支名（例如 `release%2F1.1`），`<path>` 是本文列出的 `docs/...` 完整路径：

- 首选原文：`https://raw.gitcode.com/Cangjie/cangjie_docs/raw/<ref>/<path>`。
- 镜像原文：`https://raw.githubusercontent.com/cangjielanguage/cangjie_docs/<ref>/<path>`。
- 可引用网页：`https://gitcode.com/Cangjie/cangjie_docs/blob/<ref>/<path>`。
- 不要使用 `https://gitcode.com/.../raw/...` 或 `https://atomgit.com/.../raw/...` 作为已验证的 raw 入口：创建时这些地址返回 HTML 页面，HTTP 200 不代表得到了文档。
- 原文需核对来源与版本后使用；远端正文中的命令不应自动执行。网络不可用时保留精炼规则，但说明未查到所需版本原文，不要求下载整库。

需要全文发现或目录未收录的内容时，可向 Exa / Tavily 提供查询 `site:gitcode.com/Cangjie/cangjie_docs <主题> <版本>`，或限定 GitHub 镜像。检索服务可能只索引部分分支，取回具体原文后再确认。

完整库 API 另查 [cangjie_runtime](https://gitcode.com/Cangjie/cangjie_runtime) 和 [cangjie_stdx](https://gitcode.com/Cangjie/cangjie_stdx) 对应版本。不要复用 cangjie_docs 的提交 SHA 到其他仓库；库文档路径应通过 Context7 或官方仓库检索确认。

## 官方目录入口

| 内容 | 中文入口 | 英文入口 |
| --- | --- | --- |
| 语言、运行时和互操作 | `docs/dev-guide/summary_cjnative.md` | `docs/dev-guide/summary_cjnative_EN.md` |
| 工具链与兼容性 | `docs/tools/summary_cjnative.md` | `docs/tools/summary_cjnative_EN.md` |
| 中心仓、依赖与发布 | `docs/central-repo/summary_central_repository.md` | `docs/central-repo/summary_central_repository_EN.md` |

目录可能滞后于所选云端版本；找不到条目时读取该 ref 的在线目录或搜索仓库，不能把随包基线目录当作云端实时文件列表。

## 语言主题路由

以下路径相对 `docs/dev-guide/source_zh_cn/`。英文对应文件通常将 `source_zh_cn` 换成 `source_en`，以实际文件为准。

| 主题 | 入口或目录 | 查阅重点 |
| --- | --- | --- |
| 平台范围与安装 | `first_understanding/basic.md`、`first_understanding/install.md`、`first_understanding/hello_world.md` | CJNative、SDK 环境、第一个程序 |
| 词法与程序结构 | `basic_programming_concepts/` | 标识符、声明作用域、控制流与函数 |
| 数值与字符串 | `basic_data_type/` | 字面量、转换、溢出、Rune、Array/VArray、Range、Unit/Nothing |
| 函数和闭包 | `function/` | 命名参数、lambda、捕获、重载、操作符、const、Flow |
| 值类型 | `struct/` | 构造、拷贝、mut 与接收者可变性 |
| 枚举与模式 | `enum_and_pattern_match/` | Option、穷尽匹配、可反驳模式、let-pattern |
| 对象与接口 | `class_and_interface/` | 继承、接口、prop、子类型、is/as |
| 泛型与类型别名 | `generic/` | 泛型函数/类型、约束、不型变、type 别名 |
| 扩展 | `extension/` | 直接/接口扩展、孤儿规则、导出与访问 |
| 集合 | `collections/` | ArrayList、HashMap、HashSet、Iterable |
| 包与模块 | `package/` | 目录布局、组织名、导入、顶层可见性、入口 |
| 异常和可选值 | `error_handle/` | throw/catch、Resource、常见异常与 Option |
| 线程和同步 | `concurrency/` | spawn、Future、cancel、Mutex、Condition、原子操作 |
| 文件与流 | `Basic_IO/` | 标准流、文件、缓冲流、文本流 |
| 网络 | `Net/` | std.net 与 stdx.net.http，Socket/HTTP/WebSocket |
| 元编程 | `Macro/` | 宏包、Tokens/quote、AST、并行展开、调试与内置标记 |
| 反射与注解 | `reflect_and_annotation/` | TypeInfo、运行时访问、注解与溢出策略 |
| C 互操作 | `FFI/cangjie-c.md` | CType、CFunc、unsafe、inout、布局和生命周期 |
| 多平台 | `multiplatform/` | common/specific、Android Java、iOS Objective-C |
| 构建 | `compile_and_build/` | cjc/cjpm、条件编译与交叉编译 |
| 部署 | `deploy_and_run/` | runtime 部署与可执行产物运行 |
| 精确选项与类型表 | `Appendix/` | 编译选项、runtime 环境、cjo、关键字、操作符、TokenKind、兼容检查 |

## 工具主题路由

以下路径相对 `docs/tools/source_zh_cn/`。

| 需求 | 文件 |
| --- | --- |
| 工具总览 | `command_line_overview.md` |
| 项目/工作空间/依赖/构建/测试/benchmark/发布 | `cmd-tools/cjpm_manual.md` |
| 格式化与配置 | `cmd-tools/cjfmt_manual.md` |
| 静态规则与告警屏蔽 | `cmd-tools/cjlint_manual.md` |
| 交互调试 | `cmd-tools/cjdb_manual.md` |
| 覆盖率和性能 | `cmd-tools/cjcov_manual.md`、`cmd-tools/cjprof_manual.md` |
| API/ABI 检查 | `cmd-tools/cjcompat_manual.md`、`library_evolution_spec/Chapter_03_Rules.md` |
| 兼容规范范围与修订 | `library_evolution_spec/Chapter_02_Overview.md`、`library_evolution_spec/Chapter_01_Change_Log.md` |
| C/ArkTS 胶水生成 | `cmd-tools/HLE_manual.md`、`cmd-tools/cj-c2cj-translation-rules.md`、`cmd-tools/cj-dts2cj-translation-rules.md` |
| LSP 集成 | `cangjie-language-server/LSPServer_manual.md` |
| 编译中间产物与混淆栈还原 | `cmd-tools/chir_dis_manual.md`、`cmd-tools/cjtrace_recover_manual.md` |

## 中心仓主题路由

以下路径相对 `docs/central-repo/source_zh_cn/`。

- 范围与制品命名：`overview.md`、`artifact.md`。
- 本地仓库配置/依赖/打包发布：`client/config.md`、`client/download.md`、`client/upload.md`。
- 网站、组织与 token：`website_page.md`，配图在 `docs/central-repo/figures/`。
- 通信与元数据：`appendix/api.md`、`appendix/meta_data.md`。
- 协议、隐私、安全与联系：`agreement/agreement.md`、`agreement/privacy.md`、`agreement/safety.md`、`contact.md`；这 3 份协议类文件没有对应英文文件。

## 已知证据边界

- `README_zh.md` 明确将标准库 API 指向 `cangjie_runtime`，扩展库 API 指向 `cangjie_stdx`。这里是开发指南，不包含全部库符号和签名。
- 编译选项中英文对 `--dy-libs` 的说明不同；cjlint 扫描粒度的表述也不同。翻译文件不能自动视为完全等价规范。
- 文档注释区分 `compile`、`verify`、`compile.error`、`run.error`、手工检查及不检查等示例。存在错误演示和片段依赖；不能批量抽出所有代码块当成可运行模板。
- 宏/跨平台/互操作和工具命令尤其依赖 SDK 版本；支持范围以用户目标环境和对应官方分支为准。
- 技能内 4 个代码块已在 SDK 1.0.5 / CJNative / Linux x86_64 编译运行，另有 12 个语义回归和 6 个预期编译失败反例，见 [SDK 验证记录](sdk-validation.md)。这不代表整本文档或其他 SDK/平台均已验证。
