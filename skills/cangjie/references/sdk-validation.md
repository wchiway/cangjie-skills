# SDK 验证记录

验证日期：2026-10-09。编译器和项目管理工具均为 **1.0.5**，后端 **CJNative**，目标 **x86_64-unknown-linux-gnu**。

## 范围与结果

- 技能 Markdown 中全部 4 个 `cangjie` 代码块：3 个可执行程序通过编译和精确输出检查；1 个单元测试示例通过 cjpm 执行。正例不允许编译警告。
- `cjpm init`、release build/run、debug build、test `--no-run` 通过；仅编译结果不计为用例执行。
- Release、Debug、coverage 各执行 **13 个用例**：技能示例 1 个、语义回归 12 个；各模式零失败、零跳过，XML 中每个执行用例均含断言。
- `--filter=SmokeTests.*` 执行 1 个、明确跳过 12 个，无失败；coverage 产生 `.gcda` 和 `.gcno` 原始数据，不据此声称特定覆盖率百分比。
- 6 个负例均被编译器拒绝，并人工核对错误原因：位置参数默认值、let struct 调 mut、class mut 方法、局部 var 闭包逃逸、将 as 结果直接赋给非 Option、非穷尽 match。
- 原 Option 示例可运行但产生不可达表达式警告；现改为参数函数中执行 `??`，无须关闭警告。

语义回归覆盖：命名参数、Option/as、数组及 repeat 对象共享、struct 值拷贝与 mut、HashMap 缺失键异常、引用状态闭包、默认溢出异常、协作取消、超时不取消、Mutex 与原子返回值、异常时 Resource 关闭、Range 与 Tuple。

## 重新验证

先激活已安装的 SDK 环境，使 `cjc`、`cjpm` 及运行时动态库可用。Linux SDK 通常提供 `envsetup.sh`，按实际安装路径在当前 shell 中 source；不要把维护者路径写进用户配置。

```bash
python3 -B <skill-dir>/scripts/test_sdk.py
```

脚本使用 Python 标准库，不联网、不克隆仓库、不安装 SDK，也不执行用户项目的构建脚本。它在新建的系统临时目录中提取技能代码块，创建独立 cjpm 项目，并复制 [语义测试](../scripts/sdk_semantics_test.cj)。每条命令有 120 秒超时。

输出目录包含源码、编译产物、逐命令日志、XML 报告和 `results.json`；结束时打印路径并保留，便于检查。可用 `--work-dir <新目录>` 指定位置，但拒绝复用已存在目录，避免覆写用户文件。

如新增/修改技能代码块，更新 `test_sdk.py` 中的预期输出与用例计数；脚本会拒绝未登记的代码块。其他 SDK 版本行为变化时先核对文档与诊断，不应仅放宽断言或屏蔽警告使测试通过。

## 尚未验证

未对 `docs/` 全部示例做批量编译，也未实际构建宏包、C/Java/ObjC/ArkTS 互操作或 stdx 网络程序；未覆盖 Windows、macOS、OpenHarmony、交叉编译及 SDK 1.1。运行时参数、发布与 API/ABI 规则仍需按具体项目单独验证。
