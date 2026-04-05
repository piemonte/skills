---
name: swift-concurrency
description: Use when writing concurrent Swift code — actors, Sendable, AsyncSequence, task cancellation, synchronization, state machines, reactive patterns, generics, testing, and diagnostics. Targets Swift 6 strict concurrency.
---

# Swift Concurrency & Patterns Reference

## Swift 6 Strict Concurrency

### Configuration

```swift
// Package.swift
swiftSettings: [
    .enableUpcomingFeature("StrictConcurrency")
]
```

```xcconfig
// Xcconfig
SWIFT_VERSION = 6.0
SWIFT_STRICT_CONCURRENCY = complete
SWIFT_TREAT_WARNINGS_AS_ERRORS = YES
```

### Thread-Safety Checklist

- All shared data types conform to `Sendable`
- Mutable state protected by actors or synchronization primitives
- Closures marked with `@Sendable` when crossing concurrency boundaries
- No data races detected by compiler

---

## Actor Patterns

### Standard Actor

```swift
actor DataProcessor {
    private var state: ProcessingState = .idle
    private var subscriptions = [UUID: Subscription]()

    nonisolated let identifier: UUID  // Safe cross-actor access

    func process(_ data: Data) async throws -> Result {
        // Automatically isolated to this actor
    }
}
```

### Actor Service (Preferred for Services)

```swift
actor APIService {
    private let session: URLSession

    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 60.0
        self.session = URLSession(configuration: config)
    }

    func fetchData() async throws -> [Item] {
        let (data, _) = try await session.data(for: request)
        return try JSONDecoder().decode([Item].self, from: data)
    }
}
```

### Isolation Context Propagation

```swift
protocol ServiceDelegate: Sendable {
    func serviceDidUpdate(
        isolation: isolated (any Actor)?,
        value: SomeValue
    ) async
}
```

### Safe Delegation in Actors

```swift
actor Service {
    private nonisolated(unsafe) weak var _delegate: Delegate?

    private var delegate: Delegate {
        get throws {
            guard let _delegate else {
                throw ServiceError.delegateUnavailable
            }
            return _delegate
        }
    }

    func notifyDelegate() async throws {
        try await delegate.serviceDidUpdate(self)
    }
}
```

---

## Sendable Conformance

### Structs (Preferred)

```swift
struct DataModel: Codable, Identifiable, Hashable, Sendable {
    let id: UUID
    let name: String
    let timestamp: Date
    // All properties must be Sendable types
}
```

### Sendable-Compatible Types

- Primitive types: `String`, `Int`, `Bool`, `Double`, `Float`
- Standard library: `Date`, `URL`, `UUID`, `Data`
- Collections of Sendable: `[String]`, `[Int: String]`
- Enums with Sendable associated values
- Other Sendable structs

### Classes with Manual Thread Safety

```swift
final class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    private var cache: [String: Data] = [:]

    func get(_ key: String) -> Data? {
        lock.lock()
        defer { lock.unlock() }
        return cache[key]
    }

    func set(_ key: String, value: Data) {
        lock.lock()
        defer { lock.unlock() }
        cache[key] = value
    }
}
```

### Non-Sendable Third-Party Libraries

```swift
@preconcurrency import ThirdPartyLib
@preconcurrency import AVFoundation
@preconcurrency import FirebaseFirestore
```

---

## AsyncSequence & AsyncStream

### AsyncThrowingStream for Progress

```swift
func export() -> AsyncThrowingStream<ExportEvent, Error> {
    AsyncThrowingStream { continuation in
        Task {
            do {
                for progress in stride(from: 0.0, through: 1.0, by: 0.1) {
                    try Task.checkCancellation()
                    continuation.yield(.progress(Float(progress)))
                }
                continuation.yield(.completed(outputURL))
                continuation.finish()
            } catch {
                continuation.finish(throwing: error)
            }
        }
    }
}

// Consumption
for try await update in service.export() {
    switch update {
    case .progress(let value): print("Progress: \(value)")
    case .completed(let url): print("Done: \(url)")
    }
}
```

### AsyncStream for Real-Time Updates (Firebase, Location, etc.)

```swift
func observeChanges(id: String) -> AsyncStream<[Item]> {
    AsyncStream { continuation in
        let listener = database.collection("items")
            .document(id)
            .addSnapshotListener { snapshot, error in
                guard let snapshot = snapshot else { return }
                let items = snapshot.documents.compactMap { doc in
                    try? Item(from: doc.data())
                }
                continuation.yield(items)
            }

        continuation.onTermination = { _ in
            listener.remove()  // Clean up listener
        }
    }
}
```

### AsyncNotifier (Multi-Subscriber Broadcast)

```swift
final class AsyncNotifier<Value: Sendable>: Sendable {
    private struct State {
        var continuations: [UUID: AsyncStream<Value>.Continuation] = [:]
        var currentValue: Value?
    }

    private let state = OSAllocatedUnfairLock(initialState: State())

    func yield(_ value: Value) {
        let continuations = state.withLock { state in
            state.currentValue = value
            return Array(state.continuations.values)
        }
        for continuation in continuations {
            continuation.yield(value)
        }
    }

    var sequence: AsyncStream<Value> {
        let (stream, continuation) = AsyncStream<Value>.makeStream()
        let id = UUID()
        state.withLock { state in
            state.continuations[id] = continuation
            if let current = state.currentValue {
                continuation.yield(current)
            }
        }
        continuation.onTermination = { [weak self] _ in
            self?.state.withLock { state in
                state.continuations[id] = nil
            }
        }
        return stream
    }
}
```

### AsyncBroadcastChannel

```swift
final class AsyncBroadcastChannel<Element: Sendable>: Sendable, AsyncSequence {
    func makeAsyncIterator() -> AsyncIterator { /* ... */ }
    func broadcast(_ element: Element) async { /* ... */ }
}
```

---

## Task Cancellation & Resource Management

```swift
@MainActor
final class ViewModel: ObservableObject {
    @Published var isLoading = false
    private var loadingTask: Task<Void, Never>?

    deinit {
        loadingTask?.cancel()  // Prevent memory leaks
    }

    func startLoading() {
        loadingTask?.cancel()  // Cancel previous
        loadingTask = Task { @MainActor [weak self] in
            guard let self, !Task.isCancelled else { return }
            do {
                let result = try await service.fetchData()
                guard !Task.isCancelled else { return }
                self.data = result
            } catch {
                guard !Task.isCancelled else { return }
                self.errorMessage = error.localizedDescription
            }
        }
    }
}
```

### Cancellation Checklist

- Store long-running tasks as properties
- Cancel tasks in `deinit`
- Check `Task.isCancelled` before updating state
- Use `[weak self]` in Task closures
- Cancel previous tasks before starting new ones
- Invalidate timers in deinit

---

## Synchronization Primitives

### Mutex (Preferred for Simple State)

```swift
import Synchronization

final class StateContainer: @unchecked Sendable {
    private let state = Mutex<State>()

    struct State {
        var pending: [Job] = []
        var active: Job?
    }

    func enqueue(_ job: Job) {
        state.withLock { $0.pending.append(job) }
    }

    func dequeue() -> Job? {
        state.withLock { $0.pending.isEmpty ? nil : $0.pending.removeFirst() }
    }
}
```

### Selection Criteria

| Need | Use |
|------|-----|
| Complex stateful objects | `actor` |
| Simple value protection | `Mutex` |
| Low-level synchronization | `OSAllocatedUnfairLock` |
| Avoid manual locking when possible | `actor` |

---

## State Machines

```swift
actor StateMachine<State: Hashable, Event: Hashable> {
    private(set) var currentState: State
    private var transitions: [State: [Event: State]]

    init(initial: State) {
        self.currentState = initial
        self.transitions = [:]
    }

    func addTransition(from: State, on: Event, to: State) {
        transitions[from, default: [:]][on] = to
    }

    func execute(_ event: Event) -> Bool {
        guard let next = transitions[currentState]?[event] else { return false }
        currentState = next
        return true
    }
}
```

---

## Reactive Patterns

### AsyncNotifying Protocol

```swift
protocol AsyncNotifying: Sendable {
    associatedtype Value: Sendable
    var value: Value { get async }
    func subscribe(
        receiveValue: @escaping @isolated(any) @Sendable (_ newValue: Value) async -> ()
    ) -> Subscription
}
```

### Reactive Property Wrapper

```swift
@propertyWrapper
struct UserDefault<Value: Codable> {
    let key: String
    let defaultValue: Value
    var wrappedValue: Value { get set }
    var projectedValue: AsyncStream<Value> { get }  // Observe changes
}
```

---

## Error Handling

### Domain-Specific LocalizedError

```swift
enum NetworkError: LocalizedError, Sendable {
    case connectionFailed(reason: String)
    case timeout(duration: TimeInterval)
    case invalidResponse(statusCode: Int)

    var errorDescription: String? {
        switch self {
        case .connectionFailed(let reason):
            return "Connection failed: \(reason)"
        case .timeout(let duration):
            return "Request timed out after \(duration)s"
        case .invalidResponse(let code):
            return "Invalid response: HTTP \(code)"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .timeout:
            return "Check your network connection and try again"
        default:
            return nil
        }
    }
}
```

### Error Handling Best Practices

- Define errors in the same file as the service
- Handle at ViewModel layer, not in Views
- Use descriptive case names (`.invalidURL` not `.error1`)
- Include context via associated values
- User-friendly messages in `errorDescription`
- Make all error enums `Sendable`
- Never use generic `NSError` in new code

---

## Data Persistence

### Generic Record Store

```swift
protocol RecordStore: Sendable {
    associatedtype Record: Sendable
    func record(for key: String) async -> Record?
    func allRecords() async -> [String: Record]
    func store(_ record: Record, for key: String) async
    func delete(key: String) async
}
```

### Type-Safe File I/O

```swift
final class DiskIO<T: Codable>: Sendable {
    let fileURL: URL
    let protectionType: FileProtectionType

    func read() async throws -> T
    func write(_ value: T) async throws
    func delete() async throws
    var changes: AsyncStream<T> { get }
}
```

---

## Networking & Flow Control

### Rate Limiting (Token Bucket)

```swift
actor RateLimiter {
    let capacity: Int
    let refillRate: TimeInterval
    private var tokens: Double
    private var lastRefill: Date

    func allowRequest() async -> Bool {
        let now = Date()
        let elapsed = now.timeIntervalSince(lastRefill)
        tokens = min(Double(capacity), tokens + elapsed / refillRate)
        lastRefill = now
        guard tokens >= 1 else { return false }
        tokens -= 1
        return true
    }
}
```

### Back-Pressure

```swift
final class BackPressureChannel<Element: Sendable>: AsyncSequence {
    func send(_ element: Element) async {
        // Suspends until consumers process the value
    }
}
```

---

## Generics & Type Safety

### Generic Constraints

```swift
protocol DataTransformer {
    associatedtype Input
    associatedtype Output
    func transform(_ input: Input) async throws -> Output
}

extension DataTransformer where Input: Codable, Output: Codable {
    func transformAndSerialize(_ input: Input) async throws -> Data {
        let output = try await transform(input)
        return try JSONEncoder().encode(output)
    }
}
```

### Type Erasure

```swift
struct AnyDataProvider<Element: Sendable>: DataProvider {
    private let _start: @Sendable () async throws -> Void
    private let _elements: @Sendable () async -> AsyncStream<Element>

    init<P: DataProvider>(_ provider: P) where P.Element == Element {
        _start = provider.start
        _elements = { await provider.elements }
    }
}
```

### Type Aliases for Domain Clarity

```swift
typealias UserIdentifier = String
typealias SessionToken = String
typealias Timestamp = UInt64
```

---

## IPC (Inter-Process Communication)

```swift
protocol Message: Sendable, Codable {
    associatedtype Reply: Sendable, Codable
}

protocol IPCInterface {
    associatedtype ClientMessages: MessagesProtocol
    associatedtype HostMessages: MessagesProtocol
}
```

---

## Testing Patterns

### Async Testing

```swift
final class ServiceTests: XCTestCase {
    var sut: SystemUnderTest!
    var mockDependency: MockDependency!

    override func setUp() async throws {
        mockDependency = MockDependency()
        sut = SystemUnderTest(dependency: mockDependency)
    }

    override func tearDown() async throws {
        await sut.cleanup()
        sut = nil
    }

    func testFeatureBehavior() async throws {
        // Arrange
        mockDependency.configureResponse(.success)
        // Act
        let result = try await sut.performAction()
        // Assert
        XCTAssertEqual(result, expectedValue)
        XCTAssertTrue(mockDependency.methodWasCalled)
    }
}
```

### Cancellation Testing

```swift
func testCancellation() async throws {
    let task = Task { try await service.longRunningWork() }
    try await Task.sleep(nanoseconds: 100_000_000)
    task.cancel()
    do {
        _ = try await task.value
        XCTFail("Should have been cancelled")
    } catch is CancellationError {
        // Expected
    }
}
```

### Async Sequence Test Iterator

```swift
actor AsyncSequenceTestIterator<S: AsyncSequence> {
    func waitForNext(timeout: Duration = .seconds(1)) async throws -> S.Element
    func assertRemainsEmpty(for duration: Duration) async throws
    func finish() async
}
```

### Mock Guidelines

- Complete protocol implementations
- Configurable behavior (success/failure modes)
- Capture method calls for verification
- Support async/await patterns

### Test Organization

```
Tests/
├── Unit/              # Isolated component tests
├── Integration/       # Multi-component tests
├── Mocks/            # Mock implementations
└── Utilities/        # Test helpers and assertions
```

---

## Logging & Diagnostics

### Unified Logging

```swift
import OSLog

extension Logger {
    static let networking = Logger(subsystem: "com.app", category: "networking")
    static let storage = Logger(subsystem: "com.app", category: "storage")
    static let services = Logger(subsystem: "com.app", category: "services")
}

// Usage
Logger.networking.info("Request started: \(url)")
Logger.networking.error("Request failed: \(error)")
```

### Performance Monitoring

```swift
import OSLog

let signposter = OSSignposter(logger: Logger.performance)

func performCriticalOperation() async {
    let state = signposter.beginInterval("CriticalOperation")
    defer { signposter.endInterval("CriticalOperation", state) }
    // Operation
}
```

---

## Service-Oriented Architecture

### Protocol-Based Services

```swift
protocol ServiceProtocol: Sendable {
    func stop() async
}

actor ServiceManager {
    static let shared = ServiceManager()
    private var services: [String: any ServiceProtocol] = [:]

    func register<T: ServiceProtocol>(_ service: T, for key: String) {
        services[key] = service
    }

    func service<T: ServiceProtocol>(for key: String) -> T? {
        services[key] as? T
    }
}
```

### Provider Pattern

```swift
protocol DataProvider: Sendable {
    associatedtype Element: Sendable
    var state: ProviderState { get async }
    var elements: AsyncStream<Element> { get async }
    func start() async throws
    func pause() async
    func resume() async
    func stop() async
}

enum ProviderState: Sendable {
    case initialized, running, paused, stopped
}
```

---

## CLI Tools

```swift
import ArgumentParser

@main
struct CLI: AsyncParsableCommand {
    static let configuration = CommandConfiguration(
        commandName: "tool",
        abstract: "A utility for managing the framework",
        subcommands: [Start.self, Stop.self, Status.self]
    )
}

struct Start: AsyncParsableCommand {
    @Option(help: "Configuration file path")
    var config: String?

    @Flag(help: "Enable verbose output")
    var verbose = false

    mutating func run() async throws { }
}
```

---

## Documentation Standards

### DocC Format

```swift
/// Performs an asynchronous operation with retry logic.
///
/// - Parameters:
///   - operation: The async operation to perform
///   - maxRetries: Maximum number of retry attempts
/// - Returns: The result of the operation
/// - Throws: The last error encountered if all retries fail
///
/// ## Example
/// ```swift
/// let result = try await performWithRetry { try await fetchData() }
/// ```
func performWithRetry<T>(
    operation: @Sendable () async throws -> T,
    maxRetries: Int = 3
) async throws -> T
```

### Code Organization

```swift
// MARK: - Lifecycle
init() { }

// MARK: - Public API
public func performAction() async throws { }

// MARK: - Private Implementation
private func helperMethod() { }

// MARK: - Protocol Conformance
extension MyClass: SomeProtocol { }
```

---

## Access Control

| Level | Use |
|-------|-----|
| `public` | Framework API surface |
| `package` | Shared between framework targets |
| `internal` | Default, implementation details |
| `private` | Narrowest scope possible |

Start with most restrictive access level. Expand only when necessary.

---

## Build Configuration

### Xcconfig Structure

```
Configs/
├── Base.xcconfig           # Shared settings
├── Framework.xcconfig      # Framework-specific
├── Tests.xcconfig         # Test target settings
└── Tools.xcconfig         # CLI tools
```

### Base Settings

```xcconfig
SWIFT_VERSION = 6.0
SWIFT_STRICT_CONCURRENCY = complete
SWIFT_TREAT_WARNINGS_AS_ERRORS = YES
GCC_TREAT_WARNINGS_AS_ERRORS = YES
CLANG_ANALYZER_NONNULL = YES
CLANG_STATIC_ANALYZER_MODE = deep
ENABLE_TESTABILITY = YES
CLANG_ENABLE_MODULES = YES
```
