# 宏、互操作与跨平台

仅加载相关章节；这些能力对编译顺序、SDK 版本、平台与内存生命周期敏感。

## 宏

- 宏定义放在独立的 `macro package`，以 `public macro` 导出。定义和使用不能在同一个包；先构建宏包，再构建使用方。
- 宏包仅允许宏定义对外可见，不能同时导出普通 public 函数；辅助实现放在合适的非宏包或包内作用域。
- 使用 `std.ast` 的 `Tokens`、语法节点与解析函数，输出仍须是合法仓颉代码。宏展开结果不能包含 package 声明或 import。
- `quote(...)` 使用 `$(...)` 插值，不是字符串模板 `${...}`。不匹配括号和需作为普通 token 的符号须按 quote 规则转义。
- 优先解析 AST 并验证输入形状，保留源码位置信息并用 `diagReport` 给出定位明确的错误；避免多次求值有副作用的输入表达式或意外捕获用户变量。
- 宏展开可并行；不要依赖无同步的全局可变状态。编译和 `--debug-macro` 的细节、动态库产物命名与加载路径需查看该版本手册。
- `@FastNative` 不是通用性能开关：只适用于合规的 foreign C 函数，要求短时、非阻塞且不能回调仓颉。
- `@Frozen` 是未来版本不改签名/实现的兼容性承诺，不是随手添加的优化提示。

来源：
- `docs/dev-guide/source_zh_cn/Macro/macro_introduction.md`
- `docs/dev-guide/source_zh_cn/Macro/defining_and_importing_macro_package.md`
- `docs/dev-guide/source_zh_cn/Macro/Tokens_types_and_quote_expressions.md`
- `docs/dev-guide/source_zh_cn/Macro/syntax_node.md`
- `docs/dev-guide/source_zh_cn/Macro/implementation_of_macros.md`
- `docs/dev-guide/source_zh_cn/Macro/compiling_error_reporting_and_debugging.md`
- `docs/dev-guide/source_zh_cn/Macro/practical_case.md`
- `docs/dev-guide/source_zh_cn/Macro/builtin_compilation_flags.md`
- `docs/dev-guide/source_zh_cn/Appendix/tokenkind_type.md`

## C FFI

- 外部函数用 `foreign func` 声明，无函数体；调用置于 `unsafe` 上下文。`@C` 修饰 foreign 时可省略，导出仓颉函数给 C 则按映射规则使用 `@C`。
- 参数、返回值、结构布局和调用约定必须与 C 头文件/ABI 一致；不能用 `Int64` 替代所有 C 整数类型，也不能把普通 String 直接视为 C 字符串。
- `CFunc<(Args) -> Return>` 对应 C 函数指针，其 lambda 不能捕获变量，调用需要 unsafe。不要将任意或空 `CPointer` 转成可调用函数。
- foreign/CFunc 不支持命名参数及默认值；可变参数须满足 CType 等限制。桥接 C 库更复杂布局时优先明确的 C 包装层。
- `CPointer<T>`、`CString` 的有效期和释放责任必须明确。使用 `LibC.mallocCString` 等分配时配对正确释放，覆盖错误路径；不要释放借用指针或让借用指针逃逸。
- `inout` 仅用于 CFunc 调用中的受限引用传值，不能通用于普通仓颉函数；要求 CType、可变存储，排除 CString、let/临时值及直接或间接来源于 class 实例字段的值。
- `inout` 得到的地址只保证在调用期间有效，C 侧不能保存到调用后使用。宏定义中该特性另有限制。
- C 调用栈大小对仓颉栈扩容机制不可见；真实深栈调用按运行时手册评估，不盲目增大全局参数。
- HLE 是胶水生成起点，不是 ABI 正确性证明。位域、联合体、packed 对齐、宏和调用约定必须人工核对；平台支持范围查看工具文档。

来源：
- `docs/dev-guide/source_zh_cn/FFI/cangjie-c.md`
- `docs/tools/source_zh_cn/cmd-tools/HLE_manual.md`
- `docs/tools/source_zh_cn/cmd-tools/cj-c2cj-translation-rules.md`

## Java、Objective-C、ArkTS 与多平台

- 明确区分普通 CJNative 工程、Android 仓颉 SDK、iOS 仓颉 SDK 和 OpenHarmony/ArkTS 工程；不能把所有平台 glue 互换。
- Java 桥接涉及 `@JavaMirror`、`@JavaImpl`、Java 兼容类型和生成胶水。按最低 Android API 核对可用的 Java 平台 API，不能假定 Java 8+ API 自动可用。
- Objective-C 桥接涉及 `@ObjCMirror`、`@ObjCImpl`、镜像类型/协议和平台构建流程；继承、泛型、可见成员及方法签名有专门约束。
- HLE 的 d.ts/ArkTS 转换不覆盖全部 TypeScript 语法；索引签名、联合/交叉类型、可选成员等按转换规则逐项判断，不凭 TS 类型外观生成仓颉实现。
- `common`/`specific` 用于公共与平台声明匹配，不等于简单预处理字符串替换；可用修饰符、类型签名、注解和默认值位置都有一致性要求。
- 条件编译用 `@When` 等实际语法与项目 cfg；不要引入 `#ifdef` 到 `.cj`。交叉编译还需匹配 SDK、sysroot、链接器和目标依赖，不能只改 `--target`。

来源：
- `docs/dev-guide/source_zh_cn/multiplatform/cangjie-android-Java.md`
- `docs/dev-guide/source_zh_cn/multiplatform/cangjie-ios-objc.md`
- `docs/dev-guide/source_zh_cn/multiplatform/common_platform.md`
- `docs/dev-guide/source_zh_cn/compile_and_build/conditional_compilation.md`
- `docs/dev-guide/source_zh_cn/compile_and_build/cross_compilation.md`
- `docs/tools/source_zh_cn/cmd-tools/cj-dts2cj-translation-rules.md`

## 反射与注解

- 反射从实际类型信息 API 入手，核对可查询成员及编译设置；按名字查类型可能抛出 `InfoNotFoundException`。
- 类型名查找遵守完整限定规则，预导入 core/内建类型有特殊命名规则，不要总加 `std.core` 前缀。
- 自定义注解类用 `@Annotation`，须提供 `const init`，不能是 open/abstract/sealed 类；参数须是合法常量表达式。
- 不将内部测试编译标记当作普通应用 API；测试 mock 的 public 入口应查 `std.unittest` 同版本文档。

来源：
- `docs/dev-guide/source_zh_cn/reflect_and_annotation/dynamic_feature.md`
- `docs/dev-guide/source_zh_cn/reflect_and_annotation/anno.md`
- `docs/dev-guide/source_zh_cn/function/const_func_and_eval.md`
