# 中心仓、发布与兼容

## 使用依赖

- 中心仓制品对应 cjpm 模块。源码依赖放在正确的依赖表中，不能把 `cjpm install` 当作添加普通库依赖的通用操作。
- 示例：`dep = "1.0.0"`、`dep = { version = "1.0.0" }`、`"org::dep" = "[1.0.0, 2.0.0)"`。版本范围使用文档的数学区间语法，不照搬 npm 的 `^`/`~`。
- 分清源码、测试和脚本依赖；平台隔离项和公共项冲突时会报错。`[replace]` 是强制依赖替换，需要评估兼容性，不能只为压下解析错误。
- `cjpm update` 会更新依赖相关信息，不要在无关修复中随意升级；先查看版本冲突来源。
- 可执行制品可通过 `cjpm install [org::]name-version` 安装到配置缓存相关目录；安装影响用户环境，按请求执行，不默认安装。

来源：
- `docs/central-repo/source_zh_cn/client/download.md`
- `docs/tools/source_zh_cn/cmd-tools/cjpm_manual.md`

## 配置与发布边界

- 仓库配置为 `cangjie-repo.toml`。按项目目录、用户 `.cjpm` 目录、SDK `tools/config` 的顺序查找；项目配置可遮盖用户配置。
- token 用于上传认证，不需要为了纯粹阅读语言文档而获取。不要将真实 token 写入技能、提交文件、示例或日志；仅指导用户在受控配置中设置。
- `cjpm bundle` 生成 `.cjp` 源码归档与 `meta-data.json`，默认包含构建、测试和静态检查；不是上传。`cjpm publish` 会上传，可能在产物缺失/不匹配时重新 bundle。
- 发布之前确认组织/模块名、版本、许可证、依赖来源、元数据和打包内容；发布请求需明确目标与版本，不能由“编译通过”推定获得授权。
- 制品名/组织名有 3–64 字符等规则，不能直接以任意目录名发布。bundle 要求 README、description 等，且依赖为中心仓形式，详细规则读原文。
- include/exclude 是 gitignore 风格的子集，无 `!` 否定规则；隐藏文件和若干保留文件默认排除。仍检查归档实际内容，不据此保证绝不会泄露私密文件。
- 同组织、同名称、同版本不能重复发布。认证、唯一性或安全扫描失败时检查具体原因，不自动换版本重试上传。
- 网站协议、安全和隐私文档与 8 张配图属于账号/发布工作流资料，不是语言规范；仅在相关任务读取，不代替用户接受协议或作法律判断。

来源：
- `docs/central-repo/source_zh_cn/client/config.md`
- `docs/central-repo/source_zh_cn/client/upload.md`
- `docs/central-repo/source_zh_cn/artifact.md`
- `docs/central-repo/source_zh_cn/appendix/meta_data.md`
- `docs/central-repo/source_zh_cn/appendix/api.md`
- `docs/central-repo/source_zh_cn/website_page.md`
- `docs/central-repo/source_zh_cn/agreement/agreement.md`
- `docs/central-repo/source_zh_cn/agreement/privacy.md`
- `docs/central-repo/source_zh_cn/agreement/safety.md`

## API/ABI 与运行时兼容

- API 兼容关注下游重新编译；ABI 兼容还要求下游不重新编译即可重新链接。运行时包版本检查不是完整 API/ABI 证明。
- 修改公开函数参数，即使新增参数带默认值，也可能破坏 API/ABI；函数可以作为一等值，不能仅用旧调用点能否补默认值判断。
- `const`、`@Frozen`、默认参数、布局、继承、可见性和宏/条件编译的变化各有规则；以展开宏并处理条件编译后的代码判断。
- 按模块公共接口建立下游编译/链接验证；需要兼容性检查时使用目标 SDK 的 cjcompat 和兼容版本编译器产生的 `.cjo`。

```bash
cjcompat --old path/to/old.cjo --new path/to/new.cjo
```

上述为手册基本形态；选项须以安装版本帮助核对。默认检查 API 和 ABI，报告不能代替实际目标平台测试。

来源：
- `docs/tools/source_zh_cn/cmd-tools/cjcompat_manual.md`
- `docs/tools/source_zh_cn/library_evolution_spec/Chapter_02_Overview.md`
- `docs/tools/source_zh_cn/library_evolution_spec/Chapter_03_Rules.md`
- `docs/dev-guide/source_zh_cn/Appendix/cangjie_package_compatibility.md`
- `docs/dev-guide/source_zh_cn/Appendix/cjo_artifacts.md`
