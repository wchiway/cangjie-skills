# 语言要点

仅在编写或排查基础语言代码时阅读。路径均相对文档仓库根目录；完整章节入口见 [文档导航](docs-map.md)。

## 声明与入口

- 源文件扩展名为 `.cj`。声明顺序为可选 `package`、`import`、顶层定义；自定义类型不能放在函数局部作用域。
- `main()` 或 `main(args: Array<String>)` 是模块 root 包的顶层入口，返回整数或 `Unit`；不写 `func` 或可见性修饰符。模块最多一个入口。
- `let` 只能初始化一次，`var` 可以重新赋值，`const` 用于编译期常量；不要将三者混同。
- 函数形参不可重新赋值。需要工作变量时创建局部 `var`，不能用同名局部声明覆盖形参。
- `Unit` 的值是 `()`；赋值、自增自减和循环表达式返回 `Unit`。`Nothing` 是无值的底类型，但此快照的编译器不允许显式写在类型位置。

来源：
- `docs/dev-guide/source_zh_cn/basic_programming_concepts/program_structure.md`
- `docs/dev-guide/source_zh_cn/package/entry.md`
- `docs/dev-guide/source_zh_cn/basic_data_type/unit.md`
- `docs/dev-guide/source_zh_cn/basic_data_type/nothing.md`

## 数值、字符与控制流

- 无类型上下文的整数字面量默认推断为 `Int64`。不同数值类型不自动提升；使用 `Int32(x)` 等显式转换，检查范围和精度损失。
- 整数运算和转换默认溢出抛异常。`@OverflowThrowing`、`@OverflowWrapping`、`@OverflowSaturating` 是函数级策略；改变策略是行为变更，不是随意消除错误的方法。
- 字符为 `Rune`，明确的字符字面量写 `r'a'`，ASCII 字节可写 `b'a'`。单引号也可表示字符串，不要按其他语言判断类型。
- 字符串插值写 `"${value}"`。区分 Unicode 字符、UTF-8 字节和用户感知字符；需要索引或切片时查询目标版本 API，不从字符串示例猜测单位。
- `if (condition)` 的条件必须是 `Bool` 或合法的 let-pattern 条件；没有整数 truthiness。作为有意义返回值使用的分支须满足类型要求。
- 循环写 `for (item in items)`。`0..n` 不含上界，`0..=n` 含上界，`n..0 : -1` 是递减区间；步长不得为零，反向边界不会自动改变步长。
- `match (value) { case pattern => ... }` 必须穷尽，守卫为 `where condition`，不是 `if`。非穷尽枚举的匹配需要兜底模式。`match { case condition => ... }` 是无匹配值形式。

来源：
- `docs/dev-guide/source_zh_cn/basic_data_type/integer.md`
- `docs/dev-guide/source_zh_cn/basic_data_type/characters.md`
- `docs/dev-guide/source_zh_cn/basic_data_type/strings.md`
- `docs/dev-guide/source_zh_cn/basic_data_type/range.md`
- `docs/dev-guide/source_zh_cn/basic_programming_concepts/expression.md`
- `docs/dev-guide/source_zh_cn/enum_and_pattern_match/match.md`
- `docs/dev-guide/source_zh_cn/reflect_and_annotation/anno.md`

## 函数与闭包

```cangjie
func add(a: Int64, b!: Int64 = 1): Int64 {
    a + b
}

main(): Int64 {
    let twice: (Int64) -> Int64 = { x: Int64 => x * 2 }
    println(add(twice(2), b: 3))
    return 0
}
```

该示例已在 Cangjie 1.0.5 / CJNative / Linux x86_64 编译并运行，输出 `7`。其他 SDK 版本仍需核对。

- 位置形参在命名形参之前；声明用 `b!:`，调用用 `b:`。默认值只能出现在命名形参上。
- 函数类型是 `(T1, T2) -> R`；lambda 使用 `=>`，不能在 lambda 本身显式标注返回类型。
- 普通函数允许用最后一个表达式返回值，也可显式 `return`；不要无意把尾表达式改成 `Unit` 操作。
- 捕获时变量必须可见且已初始化。捕获局部 `var` 的函数/闭包只能调用，不能作为一等值传递、赋值或返回；捕获可传递。
- 对于需逃逸的有状态闭包，可以捕获 `let` 绑定的引用对象，明确共享语义；多线程访问仍需同步。不能仅通过把 `var` 改成 `let` 就假设业务语义保持不变。
- 重载依赖参数，不凭返回值区分；自定义操作符要用 `operator func`，不能改优先级和结合性，不能声明为静态或泛型操作符函数。
- `|>` 管道、`~>` 组合、尾随 lambda 和 `const func` 有各自约束，需要时读原文，而不是转写另一语言的语法糖。

来源：
- `docs/dev-guide/source_zh_cn/function/define_functions.md`
- `docs/dev-guide/source_zh_cn/function/call_functions.md`
- `docs/dev-guide/source_zh_cn/function/lambda.md`
- `docs/dev-guide/source_zh_cn/function/closure.md`
- `docs/dev-guide/source_zh_cn/function/function_overloading.md`
- `docs/dev-guide/source_zh_cn/function/operator_overloading.md`
- `docs/dev-guide/source_zh_cn/function/function_call_desugar.md`
- `docs/dev-guide/source_zh_cn/function/const_func_and_eval.md`

## Option、转换与错误处理

```cangjie
func describe(value: ?Int64): String {
    match (value) {
        case Some(n) => "value=${n}"
        case None => "missing"
    }
}

func defaultValue(value: ?Int64): Int64 {
    value ?? 0
}

main() {
    let missing: ?Int64 = None
    println(describe(missing))
    println(defaultValue(missing))
    if (let Some(n) <- Some(7)) {
        println(n)
    }
}
```

该示例已在 Cangjie 1.0.5 / CJNative / Linux x86_64 无警告编译并运行，依次输出 `missing`、`0`、`7`。通过参数演示 `??`，避免此 SDK 对已知为 `None` 的局部值产生不可达表达式警告。

- `?T` 是 `Option<T>` 的简写，构造器是 `Some(value)` 和 `None`；没有上下文时可用 `None<Int64>`。
- `??` 提供缺省值；`?.`、`?()`、`?[]` 等是可选链，不是 Rust 的错误传播 `?`。
- `getOrThrow()` 遇到 `None` 抛异常；不确定存在性时优先匹配或有业务意义的缺省，不盲目解包。
- `value is T` 得到 `Bool`；`value as T` 得到 `Option<T>`。数值转换另用类型转换表达式，不能将 `as` 当数值截断。
- 用户 `throw` 的值必须是 `Exception` 子类，不能手动 `throw Error`。`catch (e: SomeException)` 或 `catch (_)` 处理 Exception，不是恢复一切 Error 的机制。
- 自动资源管理写 `try (resource = expression) { ... }`，资源类型须实现 `Resource`。否则按 API 使用 `finally` 做清理；不要用 GC 代替确定性的文件/连接关闭。

来源：
- `docs/dev-guide/source_zh_cn/enum_and_pattern_match/option_type.md`
- `docs/dev-guide/source_zh_cn/enum_and_pattern_match/other.md`
- `docs/dev-guide/source_zh_cn/error_handle/use_option.md`
- `docs/dev-guide/source_zh_cn/error_handle/handle.md`
- `docs/dev-guide/source_zh_cn/error_handle/common_runtime_exceptions.md`
- `docs/dev-guide/source_zh_cn/class_and_interface/typecast.md`
