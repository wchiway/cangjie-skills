# 工具链、测试与排错

## 确认环境和构建模型

- 先检查 `cjc -v`、`cjpm -v`、目标架构、SDK 路径、项目 `cjpm.toml`、`cjpm.lock` 和 `build.cj`。没有 SDK 时停止实际编译，不自动安装或修改 shell 配置。
- `cjc-version` 表示最低兼容编译器要求，不是精确版本锁。此技能的 main 快照也不是 SDK 版本声明。
- SDK 环境脚本因平台而异，按 `first_understanding/install.md` 操作；项目环境变量只在需要的进程范围设置，避免破坏其他工具链。
- SDK 已安装但非交互 shell 找不到命令时，检查是否只有交互式启动脚本加载了 SDK 环境；在当前测试进程 source 用户已安装的环境脚本，不急于重装或修改全局配置。
- 新模块优先在用户指定的空目录运行 `cjpm init --name demo`。已有模块不要为“修复”而重新初始化。
- `cjpm.toml` 输出类型用 `executable` / `static` / `dynamic`；`cjc --output-type` 用 `exe` / `staticlib` / `dylib` 等，二者不能混写。
- `[dependencies]`、`[test-dependencies]`、`[script-dependencies]` 有不同作用域；构建脚本不自动继承源码依赖。workspace、平台隔离、二进制依赖须查手册对应节。
- 普通构建可能编译并执行 `build.cj` 和依赖构建逻辑。对陌生项目先检查脚本；技能不提供绕过执行授权的许可。

来源：
- `docs/dev-guide/source_zh_cn/first_understanding/install.md`
- `docs/dev-guide/source_zh_cn/first_understanding/hello_world.md`
- `docs/tools/source_zh_cn/cmd-tools/cjpm_manual.md`
- `docs/central-repo/source_zh_cn/client/download.md`

## 常用命令

以下为此快照的命令，实际执行前按目标版本 `-h` 核对新增或不熟悉的选项。命令是按需选择的示例，不是需要全部执行的流水线。

```bash
cjpm build
cjpm run
cjpm build -g
cjpm test
cjpm test src/example
cjpm test --filter='Tests.*'
cjpm test --no-run
cjpm test --coverage
```

- 默认构建是 release，`-g` 生成 debug；常见路径分别为 `target/release/bin`、`target/debug/bin`，但可由配置覆盖。
- `cjpm run` 会触发相应构建。传程序参数、工作空间成员、交叉目标时按该版本 run 帮助使用，不猜 `--` 语义。
- `cjpm check` 主要检查依赖，不是源码静态检查器。需要编译检查用 build，需要规则检查用 cjlint。
- build/run/install/bundle 的普通编译阶段忽略 `_test.cj` 与普通文件内测试用例；`build` 成功不能证明测试代码可编译。
- `cjpm test` 默认测试当前模块，不自动运行全部依赖的测试；workspace 按成员配置选择。`test --no-run` 仅编译，`--dry-run` 不执行测试，二者不是测试通过。
- 单文件程序可用 `cjc main.cj -o main`；多包项目优先用项目原有构建方式，不能只编译入口文件后判断整个项目正常。

来源：
- `docs/tools/source_zh_cn/cmd-tools/cjpm_manual.md`
- `docs/dev-guide/source_zh_cn/compile_and_build/cjc_usage.md`
- `docs/dev-guide/source_zh_cn/Appendix/compile_options.md`

## 最小单元测试形态

下面的示例已在 Cangjie 1.0.5 / CJNative / Linux x86_64 通过 `cjpm test` 执行，1 个用例通过。将 `package` 与类名改为项目实际值，放入同包的 `_test.cj`，保持既有测试风格。

```cangjie
package demo

import std.unittest.*
import std.unittest.testmacro.*

@Test
public class SmokeTests {
    @TestCase
    public func addsNumbers(): Unit {
        @Expect(3, 1 + 2)
    }
}
```

- 测试框架生成入口；不要额外编写测试 `main`。测试实际生产函数时替换恒定表达式，而不是只断言测试代码本身。
- `std.unittest` 的断言顺序、fixture、参数化、mock 和 benchmark 等完整 API 应读同版本标准库文档，不能凭上述烟雾示例猜测。
- 核对构建成功、实际执行的测试数量、失败/跳过情况与退出码。测试筛选空集、仅编译或 dry-run 都应明确说明。
- SDK 1.0.5 的筛选测试 XML 仍列出未选中用例并标为 skipped；不要把 XML 的总条数当作实际执行数。完整测试与筛选测试分别检查期望执行/跳过数。
- 修复 Option、溢出、别名或取消问题时，分别覆盖缺失值、边界、共享状态和退出路径，而不只测试正常输入。

技能维护者可按 [SDK 验证记录](sdk-validation.md) 重新执行全部示例及语义回归；此过程不下载文档仓库。

来源：
- `docs/dev-guide/source_zh_cn/Appendix/compile_options.md` 的 `--test` 节
- `docs/dev-guide/source_zh_cn/compile_and_build/conditional_compilation.md` 的 `test` 节
- `docs/tools/source_zh_cn/cmd-tools/cjpm_manual.md` 的 `test`、`bench` 节

## 格式化和静态检查

```bash
cjfmt -f src/example.cj -o /tmp/example.formatted.cj
cjfmt -f src/example.cj -c ./cangjie-format.toml
cjlint -f src -o /tmp/cangjie-lint-report -r json
```

- `cjfmt -f` 不带 `-o` 会覆盖源文件；`-d` 处理目录。只格式化相关文件，遵守项目配置，不全仓重排无关内容。
- `cjlint -f` 的输入是源码目录，不是单个文件。本快照中英文对模块/包扫描范围的表述有差异，按安装版本帮助确认支持粒度。
- cjlint 的 `-r` 要配 `-o` 才输出报告；依赖搜索问题可核对 `--import-path`、SDK modules 与配置目录，不能将缺依赖的失败当成“无告警”。

来源：
- `docs/tools/source_zh_cn/cmd-tools/cjfmt_manual.md`
- `docs/tools/source_zh_cn/cmd-tools/cjlint_manual.md`
- `docs/tools/source_en/cmd-tools/cjlint_manual.md`

## 故障分层

| 表现 | 优先检查 |
| --- | --- |
| 语法或类型不匹配 | 命名参数、`as` 的 Option 返回值、lambda、mut、数值类型及泛型约束 |
| 包/符号找不到 | 目录与包名、import 可见性、依赖配置、`.cjo` 搜索路径及 SDK 兼容性 |
| 链接符号未定义 | 目标架构、库名、静态/动态产物、依赖闭包、编译与链接选项 |
| 启动时动态库找不到 | 部署的 runtime/第三方库、目标平台 loader 搜索路径 |
| 测试未执行 | 文件后缀、测试宏、filter、workspace 成员和 no-run/dry-run |
| 并发程序不退出/提前退出 | Future 等待、协作取消、锁与条件、阻塞 I/O 退出路径 |
| 性能问题 | 先测量再选择 cjprof/cjcov/benchmark，不凭示例调 GC 参数 |

- `.cjo` 是接口/依赖产物，不是可执行文件；应与对应库同步，不能假定跨平台通用。
- 本快照英文编译选项提及动态链接需 `--dy-std` 和 `--dy-libs`，中文相关段落仅提 `--dy-std`。不要拼接两版说明；核对目标 SDK 帮助与其发布分支。
- `cjdb` 是交互式调试器，需要有 `-g` 调试信息。命令行自动化会话中不要启动无退出条件的交互会话；可向用户提供调试命令。
- `cjprof` 的 CPU 能力有平台和 perf 权限要求；不要自动修改内核安全配置。`cjcov` 需要覆盖率产物；`cjtrace-recover`、`chir-dis` 仅在对应产物问题中使用。
- runtime 环境变量不是任意平台通用；本快照说明 OpenHarmony 下相关初始化变量无效。先查目标平台，不套用 Linux GC/线程参数。

来源：
- `docs/dev-guide/source_zh_cn/Appendix/cjo_artifacts.md`
- `docs/dev-guide/source_zh_cn/deploy_and_run/runtime_deploy.md`
- `docs/dev-guide/source_zh_cn/Appendix/runtime_env.md`
- `docs/tools/source_zh_cn/cmd-tools/cjdb_manual.md`
- `docs/tools/source_zh_cn/cmd-tools/cjprof_manual.md`
- `docs/tools/source_zh_cn/cmd-tools/cjcov_manual.md`
- `docs/tools/source_zh_cn/cmd-tools/cjtrace_recover_manual.md`
- `docs/tools/source_zh_cn/cmd-tools/chir_dis_manual.md`
