# 并发与 I/O

## 线程与 Future

- `spawn { ... }` 创建仓颉线程，得到 `Future<T>`，`T` 是任务返回值类型。不要凭其他语言习惯生成 `async/await`。
- 主线程结束可使新线程提前结束；需要结果或确保完成时保留 Future 并调用 `get()`。睡眠不是可靠的完成同步方式。
- `get(timeout)` 超时抛 `TimeoutException`，并不自动停止后台任务；本快照中 `timeout <= Duration.Zero` 等同于不设超时的 `get()`。
- `cancel()` 仅设置取消请求。任务检查 `Thread.currentThread.hasPendingCancellation` 并执行退出逻辑；阻塞中的任务还需要有可退出的等待/唤醒设计。
- 线程/闭包不能随意捕获局部 `var` 并逃逸。需要共享计数等状态时用 `let` 持有 `std.sync` 的原子类型，或用引用对象加锁。

以下示例已在 Cangjie 1.0.5 / CJNative / Linux x86_64 编译并运行，输出 `1`：

```cangjie
import std.sync.AtomicInt64

main() {
    let count = AtomicInt64(0)
    let task = spawn {
        count.fetchAdd(1)
    }
    task.get()
    println(count.load())
}
```

来源：
- `docs/dev-guide/source_zh_cn/concurrency/concurrency_overview.md`
- `docs/dev-guide/source_zh_cn/concurrency/create_thread.md`
- `docs/dev-guide/source_zh_cn/concurrency/use_thread.md`
- `docs/dev-guide/source_zh_cn/concurrency/terminal_thread.md`
- `docs/dev-guide/source_zh_cn/function/closure.md`

## 同步

- 原子的 `fetchAdd`、`swap` 等返回修改前的值，`compareAndSwap` 返回是否成功；不要按某个其他语言的 API 返回值理解。
- 本快照内存序参数仅支持顺序一致性。更弱内存序需查 SDK 实际能力，不自行编造枚举值。
- 临界区可用 `synchronized(mutex) { ... }` 自动管理互斥锁，或按手册正确配对显式锁操作，覆盖异常路径。
- 条件变量由特定 Mutex 创建。调用 `wait`、`notify`、`notifyAll` 时必须持有绑定的那把锁；`wait` 会释放并重新获得锁。
- 规范允许虚假唤醒，等待应围绕受同一锁保护的状态谓词循环，或用对应 `waitUntil`，不能把一次信号当作业务条件永久成立。
- 不要在持有锁时等待需要该锁才能完成的 Future；取消后的清理也不能破坏锁/资源的一致性。

来源：
- `docs/dev-guide/source_zh_cn/concurrency/sync.md`
- `docs/dev-guide/source_zh_cn/concurrency/sleep.md`

## 文件与流

- 文件、标准流、缓冲流分别查 `std.fs`、`std.env`、`std.io` 的 API；不能假定控制台 API 与 C/Java 相同。
- 字节流每次读取的数据量不一定填满缓冲区，按返回长度与结束条件处理；文本解码需考虑跨读取边界的多字节字符。
- `ConsoleWriter`、缓冲输出写完后按文档 `flush()`。仅写到缓冲区不代表已经输出完成。
- `File.create` 示例创建只写流；读写权限要与打开模式一致。资源用完关闭，支持 `Resource` 的用 try-with-resources，不靠 GC 自动及时释放。
- 创建、覆盖、删除文件仍按用户任务约定处理；官方示例路径不是可直接操作的用户文件路径。

来源：
- `docs/dev-guide/source_zh_cn/Basic_IO/basic_IO_overview.md`
- `docs/dev-guide/source_zh_cn/Basic_IO/basic_IO_source_stream.md`
- `docs/dev-guide/source_zh_cn/Basic_IO/basic_IO_process_stream.md`
- `docs/dev-guide/source_zh_cn/error_handle/handle.md`

## 网络与库边界

- 指南描述阻塞式网络 API：阻塞仓颉线程时可让渡系统线程，不能因此认为不存在任务阻塞或取消问题。
- Socket 示例导入 `std.net.*`；HTTP/WebSocket 示例导入 `stdx.net.http.*`，还使用若干 stdx 扩展。不能假定安装核心 SDK 就具备全部扩展库。
- 确认 stdx 对应 SDK/平台版本及构建链接配置后才给完整网络代码；缺少完整 API 时查 `cangjie_stdx` 文档，不从 Go/Java 的网络库猜方法。
- TCP 是字节流，读取不保证消息完整；定义帧/长度/分隔协议。配置实际 API 支持的连接/读写超时，处理对端关闭与异常清理。
- 本地示例的 sleep、固定端口和明文回环连接只是演示；服务代码需要明确启动同步、生命周期及部署要求。
- WebSocket 处理握手、消息类型、关闭与连接回收；HTTPS/WSS 的证书验证不能为方便演示默认关闭。
- 指南 HTTP 概览对 GET/POST 请求体有简化表述，不作为禁止其他 HTTP 语义的规范依据。

来源：
- `docs/dev-guide/source_zh_cn/Net/net_overview.md`
- `docs/dev-guide/source_zh_cn/Net/net_socket.md`
- `docs/dev-guide/source_zh_cn/Net/net_http.md`
- `docs/dev-guide/source_zh_cn/Net/net_websocket.md`
