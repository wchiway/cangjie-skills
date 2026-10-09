# 类型、集合与模块边界

## 值语义和引用语义

- 普通 `struct` 赋值和传参复制值；引用类型字段复制的是引用，不是深拷贝。`class` 是引用语义。
- `Array<T>` 虽以 struct 实现，其元素存储是共享的；`let b = a` 后 `b[0] = ...` 会影响 `a`。不要把“struct 会复制”简化成“数组深拷贝”。
- `Array` 长度固定，元素可变，索引为 `Int64`，越界会报错或抛异常；增删元素使用 `ArrayList` 等合适容器。
- `Array(size, repeat: object)` 的引用类型元素会指向同一对象；需要独立对象时按索引初始化并逐个构造。
- `VArray<T, $N>` 是固定长度值类型数组；大值的拷贝也有成本，不能一概认定其更快。
- `let` 绑定的 class/可变集合可以改变内部状态，但不能重新绑定。不可变绑定不是线程安全保证。
- 元组至少二元，元素不能原地替换；`tuple[0]` 下标是范围内的整数字面量，不是运行时索引。

来源：
- `docs/dev-guide/source_zh_cn/struct/create_instance.md`
- `docs/dev-guide/source_zh_cn/basic_data_type/array.md`
- `docs/dev-guide/source_zh_cn/basic_data_type/tuple.md`
- `docs/dev-guide/source_zh_cn/collections/collection_overview.md`

## class、struct、interface 与属性

- 继承/实现写 `<:`，多接口用 `&`。class 单继承；非抽象类要允许继承需声明 `open`，默认不是可继承的。
- 覆盖非抽象实例方法要求父方法可覆盖。`override` 可显式写以清晰表达意图，不能误称其在所有场景下都是必需。
- 通过 `init` 构造，不用 `new`。构造期间必须初始化所需字段；静态初始化规则、主构造函数和继承构造细节查对应章节。
- 修改 struct 自身字段的方法使用 `mut func`，相应接收变量及字段需要可变。class 禁止定义 `mut` 方法，但允许 `mut prop`。
- struct 实现接口的 `mut` 方法须保持修饰；class 实现时不写 `mut`。struct 转为接口值是复制，接口值上的修改不会反写原 struct 变量。
- struct 的 `mut` 方法不能从该 struct 实例抽取为一等函数；`mut` 方法里的 `this` 和实例字段捕获也有限制。
- 属性用 `prop`，可变属性用 `mut prop` 与 setter；不要把属性、字段和方法互换而忽略访问控制、覆盖及兼容性。

来源：
- `docs/dev-guide/source_zh_cn/class_and_interface/class.md`
- `docs/dev-guide/source_zh_cn/class_and_interface/interface.md`
- `docs/dev-guide/source_zh_cn/class_and_interface/prop.md`
- `docs/dev-guide/source_zh_cn/struct/define_struct.md`
- `docs/dev-guide/source_zh_cn/struct/mut.md`

## 泛型与扩展

- `func f<T>(x: T): T` 定义泛型；约束写 `where T <: InterfaceA & InterfaceB`，不同类型参数约束用逗号分隔。
- 不受约束的 `T` 不能假定可加、可比较、可哈希或可打印；根据操作选择真实接口，不凭空引入 trait/协议。
- 用户定义的泛型类型不型变，不能由 `Child <: Parent` 推出 `Box<Child> <: Box<Parent>`。内建函数和元组有特殊型变规则。
- 泛型类的静态存储是共享的，不应照搬“每个类型实参一份静态字段”的模型；静态字段/属性类型与初始化不能随意引用类型参数。
- `extend Type { ... }` 本身不能加可见性修饰符，成员可加；扩展不能访问原类型私有成员，也不能遮盖既有成员。
- 接口扩展受孤儿规则限制：不能在第三个无关包中把外部类型接到外部接口上；需要包装类型或在符合规则的包中实现。
- 外部类型的直接扩展不向其他包导出。接口扩展的可见性涉及类型、接口、泛型约束和导入，出现“方法找不到”时查访问规则而非不断增加通配导入。
- `type` 类型别名只在顶层定义，不要引入循环别名或照搬 `typealias` 关键字。

来源：
- `docs/dev-guide/source_zh_cn/generic/generic_constraint.md`
- `docs/dev-guide/source_zh_cn/generic/generic_subtype.md`
- `docs/dev-guide/source_zh_cn/generic/generic_class.md`
- `docs/dev-guide/source_zh_cn/generic/typealias.md`
- `docs/dev-guide/source_zh_cn/extension/direct_extension.md`
- `docs/dev-guide/source_zh_cn/extension/interface_extension.md`
- `docs/dev-guide/source_zh_cn/extension/access_rules.md`

## 集合

- `ArrayList`、`HashMap`、`HashSet` 的使用需导入 `std.collection` 下实际类型。
- `HashMap<K, V>` 的键要满足 `Hashable` 和 `Equatable<K>`。`HashSet` 元素同样有哈希/相等性要求；相等与哈希实现需一致。
- `map[key]` 遇到不存在的键会抛异常，不是返回 Option。可先 `contains`，或在核对 API 后用可选查询方法；共享可变 map 上的检查再访问需要同步。
- `HashMap` 和 `HashSet` 不保证插入顺序。不要让测试依赖偶然的遍历顺序。
- 构造一个新容器不必然深拷贝元素；容器修改和对象修改要分开考虑。
- 修改迭代中的集合、并发集合、排序与其他方法的完整约束应查标准库 API，不能仅靠此处示例推断。

来源：
- `docs/dev-guide/source_zh_cn/collections/collection_arraylist.md`
- `docs/dev-guide/source_zh_cn/collections/collection_hashmap.md`
- `docs/dev-guide/source_zh_cn/collections/collection_hashset.md`
- `docs/dev-guide/source_zh_cn/collections/collection_iterable_collections.md`

## 包、导入与访问控制

- 包是最小编译单元，模块是最小发布单元。一个目录的 `.cj` 组成一个包，子目录对应子包；root 包与模块配置一致。
- 同包不需要也不允许自导入；包之间不能循环依赖。每个有效包目录须直接有 `.cj`，父级也应是有效包。
- `std.core` 隐式导入；其他包使用 `import pkg.Type`、`import pkg.*` 或选择性导入。有组织名的依赖使用 `import org::pkg.Type`。
- 顶层可见性并非其他语言的同名语义：`private` 为当前文件，`internal` 为当前包及子包，`protected` 为当前模块，`public` 可跨模块。类成员的 protected 另有子类可见性规则。
- 普通顶层声明默认 `internal`；`package` 默认 `public`，`import` 默认 `private`。重导出应显式选择可见性，不能以为普通 import 会自动导出。

来源：
- `docs/dev-guide/source_zh_cn/package/package_overview.md`
- `docs/dev-guide/source_zh_cn/package/package_module_management.md`
- `docs/dev-guide/source_zh_cn/package/package_name.md`
- `docs/dev-guide/source_zh_cn/package/toplevel_access.md`
- `docs/dev-guide/source_zh_cn/package/import.md`
