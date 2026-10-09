package demo

import std.collection.HashMap
import std.sync.{AtomicInt64, Mutex, SyncCounter}
import std.unittest.*
import std.unittest.testmacro.*

struct ValueCounter {
    public var value: Int64 = 0

    public mut func increment(): Unit {
        value += 1
    }
}

class RefCounter {
    public var value: Int64 = 0
}

class TestResource <: Resource {
    public var closed: Bool = false

    public func isClosed(): Bool {
        closed
    }

    public func close(): Unit {
        closed = true
    }
}

func addNamed(a: Int64, b!: Int64 = 1): Int64 {
    a + b
}

func optionDefault(value: ?Int64): Int64 {
    value ?? 0
}

func makeCounter(): () -> Int64 {
    let state = RefCounter()
    return {
        =>
            state.value += 1
            state.value
    }
}

func incrementSmall(value: Int8): Int8 {
    value + 1
}

@Test
public class SemanticsTests {
    @TestCase
    public func namedParameters(): Unit {
        @Expect(5, addNamed(4))
        @Expect(7, addNamed(4, b: 3))
    }

    @TestCase
    public func optionAndCast(): Unit {
        @Expect(0, optionDefault(None))
        @Expect(7, optionDefault(Some(7)))
        let value: Any = "cangjie"
        let cast: ?String = value as String
        @Expect("cangjie", cast ?? "missing")
        let bad: ?Int64 = value as Int64
        @Expect(0, optionDefault(bad))
    }

    @TestCase
    public func arrayStorageIsShared(): Unit {
        let original = [1, 2]
        let alias = original
        alias[0] = 9
        @Expect(9, original[0])
        let objects = Array<RefCounter>(2, repeat: RefCounter())
        objects[0].value = 7
        @Expect(7, objects[1].value)
    }

    @TestCase
    public func structCopyAndMut(): Unit {
        var original = ValueCounter()
        var copy = original
        copy.increment()
        @Expect(0, original.value)
        @Expect(1, copy.value)
        original.increment()
        @Expect(1, original.value)
    }

    @TestCase
    public func missingHashMapKeyThrows(): Unit {
        let map = HashMap<String, Int64>([("present", 7)])
        @Expect(7, map["present"])
        var caught = false
        try {
            let value = map["absent"]
            println(value)
        } catch (_: Exception) {
            caught = true
        }
        @Expect(true, caught)
    }

    @TestCase
    public func referenceClosureCanEscape(): Unit {
        let next = makeCounter()
        @Expect(1, next())
        @Expect(2, next())
    }

    @TestCase
    public func defaultOverflowThrows(): Unit {
        var caught = false
        try {
            let value = incrementSmall(127)
            println(value)
        } catch (_: OverflowException) {
            caught = true
        }
        @Expect(true, caught)
    }

    @TestCase
    public func cancellationIsCooperative(): Unit {
        let gate = SyncCounter(1)
        let finished = AtomicInt64(0)
        let task = spawn {
            gate.waitUntilZero()
            let requested = Thread.currentThread.hasPendingCancellation
            finished.store(1)
            requested
        }
        task.cancel()
        gate.dec()
        @Expect(true, task.get())
        @Expect(1, finished.load())
    }

    @TestCase
    public func timeoutDoesNotCancel(): Unit {
        let gate = SyncCounter(1)
        let task = spawn {
            gate.waitUntilZero()
            Thread.currentThread.hasPendingCancellation
        }
        var timedOut = false
        try {
            let cancelled = task.get(Duration.millisecond)
            println(cancelled)
        } catch (_: TimeoutException) {
            timedOut = true
        } finally {
            gate.dec()
        }
        @Expect(true, timedOut)
        @Expect(false, task.get())
    }

    @TestCase
    public func mutexAndAtomicResults(): Unit {
        let state = RefCounter()
        let lock = Mutex()
        let task = spawn {
            synchronized(lock) {
                state.value += 1
            }
        }
        synchronized(lock) {
            state.value += 1
        }
        task.get()
        @Expect(2, state.value)
        let atomic = AtomicInt64(3)
        @Expect(3, atomic.fetchAdd(2))
        @Expect(5, atomic.load())
    }

    @TestCase
    public func resourceClosesOnException(): Unit {
        let resource = TestResource()
        try (held = resource) {
            @Expect(false, held.isClosed())
            throw IllegalArgumentException("expected")
        } catch (_: IllegalArgumentException) {
            @Expect(true, resource.isClosed())
        }
        @Expect(true, resource.isClosed())
    }

    @TestCase
    public func rangeAndTuple(): Unit {
        var exclusive = 0
        for (i in 0..3) {
            exclusive += i
        }
        var inclusive = 0
        for (i in 0..=3) {
            inclusive += i
        }
        let sums = (exclusive, inclusive)
        @Expect(3, sums[0])
        @Expect(6, sums[1])
    }
}
