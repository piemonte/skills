---
name: advanced-swift-patterns
description: Use when implementing advanced Swift abstractions — property wrappers, interpolation and animation primitives, custom collection types, Combine-to-async bridging, async broadcast channels, and dynamicMemberLookup.
---

# Advanced Swift Patterns Reference

## Property Wrappers

### @FastPublished — Efficient @Published Bridging

```swift
import Combine

/// More efficient alternative to @Published that synchronizes via didSet
/// instead of willSet, avoiding unnecessary objectWillChange emissions.
@propertyWrapper
struct FastPublished<Value> {
    private var value: Value
    private let subject = PassthroughSubject<Value, Never>()

    init(wrappedValue: Value) {
        self.value = wrappedValue
    }

    var wrappedValue: Value {
        get { value }
        set {
            value = newValue
            subject.send(newValue)
        }
    }

    var projectedValue: AnyPublisher<Value, Never> {
        subject.eraseToAnyPublisher()
    }
}
```

### @DefaultValue — Generic Default Fallback

```swift
/// Property wrapper that provides a default value and tracks changes.
@propertyWrapper
struct DefaultValue<T: Equatable> {
    private var value: T?
    let defaultValue: T

    init(wrappedValue: T? = nil, default defaultValue: T) {
        self.value = wrappedValue
        self.defaultValue = defaultValue
    }

    var wrappedValue: T {
        get { value ?? defaultValue }
        set { value = newValue }
    }

    /// Whether the value differs from the default.
    var projectedValue: Bool {
        guard let value else { return false }
        return value != defaultValue
    }

    /// Reset to default.
    mutating func reset() {
        value = nil
    }
}

// Conditional conformances
extension DefaultValue: Codable where T: Codable {
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        self.value = try container.decode(T?.self)
        self.defaultValue = T.self as? any (Decodable & DefaultInitializable) != nil
            ? T() as? T ?? value!
            : value!
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(value)
    }
}

extension DefaultValue: Sendable where T: Sendable {}
extension DefaultValue: Hashable where T: Hashable {}
```

### @CodableBox — Custom Encoding Wrapper

```swift
/// Wraps types that need custom encoding/decoding (e.g., SIMD types).
protocol CustomCodable {
    associatedtype CodableRepresentation: Codable
    var codableRepresentation: CodableRepresentation { get }
    init(codableRepresentation: CodableRepresentation)
}

@propertyWrapper
struct CodableBox<T: CustomCodable>: Codable {
    var wrappedValue: T

    init(wrappedValue: T) {
        self.wrappedValue = wrappedValue
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let representation = try container.decode(T.CodableRepresentation.self)
        self.wrappedValue = T(codableRepresentation: representation)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(wrappedValue.codableRepresentation)
    }
}

// Example: Make SIMD3<Float> codable
extension SIMD3<Float>: CustomCodable {
    typealias CodableRepresentation = [Float]
    var codableRepresentation: [Float] { [x, y, z] }
    init(codableRepresentation: [Float]) {
        self.init(codableRepresentation[0], codableRepresentation[1], codableRepresentation[2])
    }
}
```

### @UserDefault — Type-Safe UserDefaults

```swift
@propertyWrapper
struct UserDefault<Value: Codable> {
    let key: String
    let defaultValue: Value
    private let subject = PassthroughSubject<Value, Never>()

    init(_ key: String, default defaultValue: Value) {
        self.key = key
        self.defaultValue = defaultValue
    }

    var wrappedValue: Value {
        get {
            guard let data = UserDefaults.standard.data(forKey: key) else { return defaultValue }
            return (try? JSONDecoder().decode(Value.self, from: data)) ?? defaultValue
        }
        set {
            let data = try? JSONEncoder().encode(newValue)
            UserDefaults.standard.set(data, forKey: key)
            subject.send(newValue)
        }
    }

    /// Async observation of value changes.
    var projectedValue: AsyncStream<Value> {
        AsyncStream { continuation in
            let cancellable = subject.sink { value in
                continuation.yield(value)
            }
            continuation.onTermination = { _ in
                cancellable.cancel()
            }
        }
    }
}

// Usage
struct Settings {
    @UserDefault("showOnboarding", default: true)
    static var showOnboarding: Bool

    @UserDefault("preferredTheme", default: "system")
    static var preferredTheme: String
}
```

---

## Interpolation & Animation

### Lerpable Protocol

```swift
/// Generic linear interpolation protocol.
protocol Lerpable {
    static func lerp(from: Self, to: Self, blend: Float) -> Self
}

extension Float: Lerpable {
    static func lerp(from: Float, to: Float, blend: Float) -> Float {
        from + (to - from) * blend
    }
}

extension Double: Lerpable {
    static func lerp(from: Double, to: Double, blend: Float) -> Double {
        from + (to - from) * Double(blend)
    }
}

extension SIMD2<Float>: Lerpable {
    static func lerp(from: SIMD2<Float>, to: SIMD2<Float>, blend: Float) -> SIMD2<Float> {
        from + (to - from) * blend
    }
}

extension SIMD3<Float>: Lerpable {
    static func lerp(from: SIMD3<Float>, to: SIMD3<Float>, blend: Float) -> SIMD3<Float> {
        from + (to - from) * blend
    }
}

extension SIMD4<Float>: Lerpable {
    static func lerp(from: SIMD4<Float>, to: SIMD4<Float>, blend: Float) -> SIMD4<Float> {
        from + (to - from) * blend
    }
}

extension simd_quatf: Lerpable {
    static func lerp(from: simd_quatf, to: simd_quatf, blend: Float) -> simd_quatf {
        simd_slerp(from, to, blend)
    }
}

extension ClosedRange: Lerpable where Bound: Lerpable {
    static func lerp(from: ClosedRange<Bound>, to: ClosedRange<Bound>, blend: Float) -> ClosedRange<Bound> {
        Bound.lerp(from: from.lowerBound, to: to.lowerBound, blend: blend)
        ...Bound.lerp(from: from.upperBound, to: to.upperBound, blend: blend)
    }
}
```

### ExponentialDamper

```swift
/// Smooth value tracking with exponential decay.
/// Provides natural-feeling transitions without spring oscillation.
struct ExponentialDamper<T: Lerpable> {
    var target: T
    var current: T
    let duration: Float

    init(initial: T, duration: Float = 0.2) {
        self.target = initial
        self.current = initial
        self.duration = duration
    }

    /// Update current value toward target. Call each frame.
    mutating func update(dt: Float) {
        guard duration > 0 else {
            current = target
            return
        }
        let blend = 1.0 - exp(-dt / duration)
        current = T.lerp(from: current, to: target, blend: blend)
    }

    /// Snap immediately to target.
    mutating func snap() {
        current = target
    }
}

// Usage
var positionDamper = ExponentialDamper<SIMD3<Float>>(initial: .zero, duration: 0.15)
positionDamper.target = newPosition
positionDamper.update(dt: deltaTime)
entity.position = positionDamper.current
```

### AsymmetricExponentialDamper

```swift
/// Separate durations for growth vs decay — useful for UI that should
/// appear quickly but fade slowly (or vice versa).
struct AsymmetricExponentialDamper<T: Lerpable & Comparable> {
    var target: T
    var current: T
    let growthDuration: Float
    let decayDuration: Float

    init(initial: T, growthDuration: Float = 0.1, decayDuration: Float = 0.3) {
        self.target = initial
        self.current = initial
        self.growthDuration = growthDuration
        self.decayDuration = decayDuration
    }

    mutating func update(dt: Float) {
        let duration = target > current ? growthDuration : decayDuration
        guard duration > 0 else {
            current = target
            return
        }
        let blend = 1.0 - exp(-dt / duration)
        current = T.lerp(from: current, to: target, blend: blend)
    }
}
```

### Interpolator Protocol

```swift
/// Protocol-based interpolation with distance tracking and clamping.
protocol Interpolable: Lerpable {
    static func distance(from: Self, to: Self) -> Float
    static func clamp(_ value: Self, min: Self, max: Self) -> Self
}

struct Interpolator<T: Interpolable> {
    var from: T
    var to: T
    private(set) var progress: Float = 0

    mutating func advance(by amount: Float) {
        progress = min(1.0, progress + amount)
    }

    var current: T {
        T.lerp(from: from, to: to, blend: progress)
    }

    var remainingDistance: Float {
        T.distance(from: current, to: to)
    }

    var isDone: Bool { progress >= 1.0 }

    mutating func reset(from: T, to: T) {
        self.from = from
        self.to = to
        self.progress = 0
    }
}
```

### Animation Runner (Async/Await)

```swift
/// Protocol for async animations with per-frame updates.
protocol Animatable {
    var isDone: Bool { get }
    mutating func update(interval: TimeInterval)
}

/// Run an animation to completion using async/await.
func runAnimation<A: Animatable>(
    _ animation: A,
    frameRate: Double = 60.0
) async throws -> A {
    var anim = animation
    let interval = 1.0 / frameRate

    while !anim.isDone {
        try Task.checkCancellation()
        try await Task.sleep(for: .milliseconds(Int(interval * 1000)))
        anim.update(interval: interval)
    }
    return anim
}

/// Run animation with completion continuation.
func withAnimation<A: Animatable>(
    _ animation: A,
    frameRate: Double = 60.0
) async throws {
    _ = try await runAnimation(animation, frameRate: frameRate)
}
```

---

## Collection Types

### NonEmpty — Compile-Time Non-Empty Guarantee

```swift
/// A collection wrapper that guarantees at least one element.
struct NonEmpty<C: Collection> {
    let head: C.Element
    let tail: C

    init(_ head: C.Element, _ tail: C) {
        self.head = head
        self.tail = tail
    }

    /// Safe access — always succeeds.
    var first: C.Element { head }
}

extension NonEmpty where C: RangeReplaceableCollection {
    init?(_ collection: C) {
        guard let first = collection.first else { return nil }
        var remaining = collection
        remaining.removeFirst()
        self.head = first
        self.tail = remaining
    }

    var count: Int { 1 + tail.count }

    var allElements: [C.Element] {
        [head] + Array(tail)
    }
}

extension NonEmpty where C.Element: Comparable {
    var min: C.Element {
        tail.min().map { Swift.min(head, $0) } ?? head
    }

    var max: C.Element {
        tail.max().map { Swift.max(head, $0) } ?? head
    }
}

// Usage
let items = NonEmpty([1, 2, 3])!  // Safe: we know it's non-empty
print(items.first)  // 1 — no optional
print(items.min)    // 1 — no optional
```

### CountedSet — Multiset with Per-Element Counts

```swift
/// A set that tracks how many times each element has been inserted.
struct CountedSet<Element: Hashable> {
    private var storage: [Element: Int] = [:]

    var count: Int { storage.values.reduce(0, +) }
    var uniqueCount: Int { storage.count }
    var isEmpty: Bool { storage.isEmpty }

    mutating func insert(_ element: Element) {
        storage[element, default: 0] += 1
    }

    @discardableResult
    mutating func remove(_ element: Element) -> Int {
        guard let count = storage[element] else { return 0 }
        if count <= 1 {
            storage.removeValue(forKey: element)
        } else {
            storage[element] = count - 1
        }
        return count
    }

    func count(for element: Element) -> Int {
        storage[element] ?? 0
    }

    func contains(_ element: Element) -> Bool {
        storage[element] != nil
    }

    var elements: Dictionary<Element, Int>.Keys { storage.keys }
}

extension CountedSet: Sendable where Element: Sendable {}
```

### OrderedDictionary — Insertion-Order Preservation

```swift
/// Dictionary that maintains insertion order with O(1) lookup.
struct OrderedDictionary<Key: Hashable, Value> {
    private var keys: [Key] = []
    private var values: [Key: Value] = [:]

    var count: Int { keys.count }
    var isEmpty: Bool { keys.isEmpty }

    subscript(key: Key) -> Value? {
        get { values[key] }
        set {
            if let newValue {
                if values[key] == nil {
                    keys.append(key)
                }
                values[key] = newValue
            } else {
                values.removeValue(forKey: key)
                keys.removeAll { $0 == key }
            }
        }
    }

    var orderedKeys: [Key] { keys }
    var orderedValues: [Value] { keys.compactMap { values[$0] } }
    var orderedPairs: [(key: Key, value: Value)] {
        keys.compactMap { key in values[key].map { (key, $0) } }
    }

    @discardableResult
    mutating func removeValue(forKey key: Key) -> Value? {
        keys.removeAll { $0 == key }
        return values.removeValue(forKey: key)
    }
}

extension OrderedDictionary: Sendable where Key: Sendable, Value: Sendable {}
```

### Table — Enum-Keyed Dictionary with Guaranteed Coverage

```swift
/// Dictionary keyed by a CaseIterable enum, guaranteeing a value for every case.
struct Table<E: CaseIterable & Hashable, V> {
    private var storage: [E: V]

    init(_ builder: (E) -> V) {
        var storage = [E: V]()
        for key in E.allCases {
            storage[key] = builder(key)
        }
        self.storage = storage
    }

    subscript(key: E) -> V {
        get { storage[key]! }  // Safe: all cases populated in init
        set { storage[key] = newValue }
    }

    func map<U>(_ transform: (V) throws -> U) rethrows -> Table<E, U> {
        Table<E, U> { key in
            try transform(self[key])
        }
    }
}

extension Table: Sendable where E: Sendable, V: Sendable {}

// Usage
enum Priority: CaseIterable, Hashable {
    case low, medium, high, critical
}

let thresholds = Table<Priority, Int> { priority in
    switch priority {
    case .low: return 100
    case .medium: return 50
    case .high: return 10
    case .critical: return 1
    }
}
print(thresholds[.high])  // 10
```

---

## Combine-to-Async Bridging

### Get Single Value from Publisher

```swift
import Combine

extension Publisher where Failure: Error {
    /// Await a single value from a Publisher, then cancel.
    func sinkSingleValue() async throws -> Output {
        try await withCheckedThrowingContinuation { continuation in
            var cancellable: AnyCancellable?
            cancellable = self.first()
                .sink(
                    receiveCompletion: { completion in
                        switch completion {
                        case .finished: break
                        case .failure(let error):
                            continuation.resume(throwing: error)
                        }
                        cancellable?.cancel()
                    },
                    receiveValue: { value in
                        continuation.resume(returning: value)
                    }
                )
        }
    }
}

// Usage
let user = try await userPublisher.sinkSingleValue()
```

### Await Void Publisher Completion

```swift
extension Publisher where Failure: Error {
    /// Await completion of a Publisher that doesn't produce meaningful values.
    func sink() async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            var cancellable: AnyCancellable?
            cancellable = self.sink(
                receiveCompletion: { completion in
                    switch completion {
                    case .finished:
                        continuation.resume()
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                    cancellable?.cancel()
                },
                receiveValue: { _ in }
            )
        }
    }
}
```

### AsyncSequence to Combine Publisher

```swift
struct AsyncSequencePublisher<S: AsyncSequence>: Publisher where S.Element: Sendable {
    typealias Output = S.Element
    typealias Failure = Error

    let sequence: S

    func receive<Sub: Subscriber>(subscriber: Sub) where Sub.Input == Output, Sub.Failure == Failure {
        let subscription = AsyncSubscription(sequence: sequence, subscriber: subscriber)
        subscriber.receive(subscription: subscription)
    }

    final class AsyncSubscription<Sub: Subscriber>: Subscription where Sub.Input == S.Element, Sub.Failure == Error {
        private var task: Task<Void, Never>?
        private let sequence: S

        init(sequence: S, subscriber: Sub) {
            self.sequence = sequence
            self.task = Task {
                do {
                    for try await element in sequence {
                        _ = subscriber.receive(element)
                    }
                    subscriber.receive(completion: .finished)
                } catch {
                    subscriber.receive(completion: .failure(error))
                }
            }
        }

        func request(_ demand: Subscribers.Demand) {}
        func cancel() { task?.cancel() }
    }
}

extension AsyncSequence where Element: Sendable {
    var publisher: AsyncSequencePublisher<Self> {
        AsyncSequencePublisher(sequence: self)
    }
}
```

### Callback-to-Async Bridging

```swift
/// Convert callback-based APIs to async/await.
func loadImage(named name: String) async throws -> UIImage {
    try await withCheckedThrowingContinuation { continuation in
        ImageLoader.load(name: name) { result in
            switch result {
            case .success(let image):
                continuation.resume(returning: image)
            case .failure(let error):
                continuation.resume(throwing: error)
            }
        }
    }
}

/// Non-throwing version for APIs that always succeed.
func currentLocation() async -> CLLocation {
    await withCheckedContinuation { continuation in
        locationManager.requestLocation { location in
            continuation.resume(returning: location)
        }
    }
}
```

---

## Advanced AsyncSequence Abstractions

### AsyncBroadcastChannel — Multi-Consumer with Back-Pressure

```swift
/// Broadcast channel that supports multiple consumers with back-pressure handling.
/// Each consumer gets its own buffered stream and can consume at its own pace.
final class AsyncBroadcastChannel<Element: Sendable>: Sendable {
    private struct ConsumerState {
        var continuation: AsyncStream<Element>.Continuation
        var id: UUID
    }

    private struct State {
        var consumers: [ConsumerState] = []
        var isFinished: Bool = false
    }

    private let state = OSAllocatedUnfairLock(initialState: State())

    /// Broadcast an element to all consumers.
    func send(_ element: Element) {
        let consumers = state.withLock { $0.consumers }
        for consumer in consumers {
            consumer.continuation.yield(element)
        }
    }

    /// Signal that no more elements will be sent.
    func finish() {
        let consumers = state.withLock { state in
            state.isFinished = true
            return state.consumers
        }
        for consumer in consumers {
            consumer.continuation.finish()
        }
    }

    /// Create a new consumer stream. Each consumer receives all
    /// elements broadcast after subscription.
    func subscribe() -> AsyncStream<Element> {
        let id = UUID()
        let (stream, continuation) = AsyncStream<Element>.makeStream(
            bufferingPolicy: .bufferingNewest(64)
        )

        state.withLock { state in
            if state.isFinished {
                continuation.finish()
            } else {
                state.consumers.append(ConsumerState(continuation: continuation, id: id))
            }
        }

        continuation.onTermination = { [weak self] _ in
            self?.state.withLock { state in
                state.consumers.removeAll { $0.id == id }
            }
        }

        return stream
    }
}

// Usage
let channel = AsyncBroadcastChannel<SensorReading>()

// Consumer 1
Task {
    for await reading in channel.subscribe() {
        updateUI(reading)
    }
}

// Consumer 2
Task {
    for await reading in channel.subscribe() {
        logToFile(reading)
    }
}

// Producer
channel.send(SensorReading(value: 42.0))
```

### Enhanced AsyncNotifier with Back-Pressure

```swift
/// Actor-isolated notifier with back-pressure support via discarding task groups.
actor AsyncNotifier<Value: Sendable> {
    private var subscriptions: [UUID: AsyncStream<Value>.Continuation] = [:]
    private var currentValue: Value?

    var value: Value? { currentValue }

    /// Subscribe to value updates.
    var sequence: AsyncStream<Value> {
        let id = UUID()
        let (stream, continuation) = AsyncStream<Value>.makeStream()

        subscriptions[id] = continuation
        if let current = currentValue {
            continuation.yield(current)
        }

        continuation.onTermination = { [weak self] _ in
            Task { [weak self] in
                await self?.removeSubscription(id)
            }
        }

        return stream
    }

    private func removeSubscription(_ id: UUID) {
        subscriptions.removeValue(forKey: id)
    }

    /// Yield a value to all subscribers with back-pressure handling.
    func yield(_ value: Value) async {
        currentValue = value
        await withDiscardingTaskGroup { group in
            for (_, continuation) in subscriptions {
                group.addTask {
                    continuation.yield(value)
                }
            }
        }
    }

    /// Synchronous yield for bridging from Combine — use sparingly.
    nonisolated func discouragedSyncYield(_ value: Value) {
        Task { await self.yield(value) }
    }
}
```

### DynamicJoinedAsyncNotifier

```swift
/// Combines multiple async sources dynamically, adding/removing at runtime.
actor DynamicJoinedAsyncNotifier<Value: Sendable> {
    private var sources: [UUID: Task<Void, Never>] = [:]
    private let output = AsyncBroadcastChannel<Value>()

    /// Add a new async source.
    func add<S: AsyncSequence>(
        _ source: S
    ) -> UUID where S.Element == Value, S: Sendable {
        let id = UUID()
        let task = Task { [weak self] in
            do {
                for try await value in source {
                    self?.output.send(value)
                }
            } catch {
                // Source completed or failed
            }
        }
        sources[id] = task
        return id
    }

    /// Remove a source by its ID.
    func remove(_ id: UUID) {
        sources[id]?.cancel()
        sources.removeValue(forKey: id)
    }

    /// Subscribe to combined output from all sources.
    func subscribe() -> AsyncStream<Value> {
        output.subscribe()
    }
}
```

### ChunkedSequence — Batching Elements

```swift
/// Groups elements from an async sequence into fixed-size chunks.
struct ChunkedSequence<Base: AsyncSequence>: AsyncSequence {
    typealias Element = [Base.Element]

    let base: Base
    let chunkSize: Int

    struct AsyncIterator: AsyncIteratorProtocol {
        var baseIterator: Base.AsyncIterator
        let chunkSize: Int

        mutating func next() async throws -> [Base.Element]? {
            var chunk: [Base.Element] = []
            chunk.reserveCapacity(chunkSize)

            while chunk.count < chunkSize {
                try Task.checkCancellation()
                guard let element = try await baseIterator.next() else {
                    break
                }
                chunk.append(element)
            }

            return chunk.isEmpty ? nil : chunk
        }
    }

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(baseIterator: base.makeAsyncIterator(), chunkSize: chunkSize)
    }
}

extension AsyncSequence {
    func chunked(into size: Int) -> ChunkedSequence<Self> {
        ChunkedSequence(base: self, chunkSize: size)
    }
}

// Usage
for try await batch in dataStream.chunked(into: 50) {
    try await processBatch(batch)
}
```

### AsyncJustSequence — Single-Value Async Sequence

```swift
/// An async sequence that yields exactly one value.
struct AsyncJustSequence<Element>: AsyncSequence {
    let element: Element

    struct AsyncIterator: AsyncIteratorProtocol {
        var element: Element?

        mutating func next() async -> Element? {
            defer { element = nil }
            return element
        }
    }

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(element: element)
    }
}

extension AsyncSequence {
    static func just(_ element: Element) -> AsyncJustSequence<Element> {
        AsyncJustSequence(element: element)
    }
}
```

### Parallel Sequence Operations

```swift
extension Sequence where Element: Sendable {
    /// Execute an async operation on each element in parallel.
    func asyncForEach(
        _ operation: @escaping @Sendable (Element) async throws -> Void
    ) async throws {
        try await withThrowingTaskGroup(of: Void.self) { group in
            for element in self {
                group.addTask {
                    try await operation(element)
                }
            }
            try await group.waitForAll()
        }
    }

    /// Map elements in parallel, preserving order.
    func parallelMap<T: Sendable>(
        _ transform: @escaping @Sendable (Element) async throws -> T
    ) async throws -> [T] {
        try await withThrowingTaskGroup(of: (Int, T).self) { group in
            for (index, element) in self.enumerated() {
                group.addTask {
                    let result = try await transform(element)
                    return (index, result)
                }
            }
            var results = [(Int, T)]()
            for try await pair in group {
                results.append(pair)
            }
            return results.sorted { $0.0 < $1.0 }.map(\.1)
        }
    }
}

// Usage
let images = try await urls.parallelMap { url in
    try await downloadImage(from: url)
}
```

---

## @dynamicMemberLookup

### KeyPath-Based Fluent APIs

```swift
/// Accessor that navigates a type hierarchy via key paths.
@dynamicMemberLookup
struct InputAccessor<Root, Value> {
    let keyPath: KeyPath<Root, Value>

    subscript<Next>(dynamicMember next: KeyPath<Value, Next>) -> InputAccessor<Root, Next> {
        InputAccessor<Root, Next>(keyPath: keyPath.appending(path: next))
    }
}

@dynamicMemberLookup
struct OutputAccessor<Root, Value> {
    let keyPath: WritableKeyPath<Root, Value>

    subscript<Next>(dynamicMember next: WritableKeyPath<Value, Next>) -> OutputAccessor<Root, Next> {
        OutputAccessor<Root, Next>(keyPath: keyPath.appending(path: next))
    }
}

// Usage: declarative data binding
struct NodeGraph {
    static var input: InputAccessor<NodeGraph, NodeGraph> {
        InputAccessor(keyPath: \.self)
    }

    var position: SIMD3<Float> = .zero
    var rotation: simd_quatf = .init()
    var scale: Float = 1.0
}

// Access via fluent path
let positionPath = NodeGraph.input.position  // KeyPath<NodeGraph, SIMD3<Float>>
```

### Operator Overloading for Declarative Connections

```swift
/// Dataflow operator: connects an output to an input.
infix operator <<: AssignmentPrecedence

func << <Root, Value>(
    lhs: OutputAccessor<Root, Value>,
    rhs: InputAccessor<Root, Value>
) -> Connection<Root, Value> {
    Connection(from: rhs.keyPath, to: lhs.keyPath)
}

struct Connection<Root, Value> {
    let from: KeyPath<Root, Value>
    let to: WritableKeyPath<Root, Value>

    func apply(from source: Root, to target: inout Root) {
        target[keyPath: to] = source[keyPath: from]
    }
}

// Usage: declarative data flow
// output.position << input.position
```
