---
name: realitykit-visionos
description: Use when building visionOS apps or using RealityKit — entity-component-system architecture, custom Systems, scene subscriptions, immersive spaces, hand tracking, and multi-window scenes.
---

# RealityKit & visionOS Reference

## Entity Hierarchy

```swift
import RealityKit

// Create and configure entities
let rootEntity = Entity()
rootEntity.name = "SceneRoot"

let childEntity = ModelEntity(
    mesh: .generateSphere(radius: 0.1),
    materials: [SimpleMaterial(color: .blue, isMetallic: true)]
)
childEntity.name = "Sphere"
childEntity.position = [0, 1.5, -2]

rootEntity.addChild(childEntity)

// Traverse hierarchy
for child in rootEntity.children {
    print(child.name)
}

// Find by name
if let found = rootEntity.findEntity(named: "Sphere") {
    found.isEnabled = false
}
```

---

## Component Pattern

### Standard Component

```swift
/// Components hold data. Entities gain behavior by attaching components.
struct HighlightComponent: Component, Codable, Hashable {
    var color: SIMD3<Float> = [1, 1, 0]
    var intensity: Float = 1.0
    var isActive: Bool = false
}
```

### Transient Component (Non-Serialized)

```swift
/// Use TransientComponent for runtime-only state that shouldn't be saved.
struct RuntimeStateComponent: TransientComponent {
    var lastUpdateTime: TimeInterval = 0
    var velocityEstimate: SIMD3<Float> = .zero
    weak var delegate: (any EntityDelegate)?
}
```

### Registering Components

```swift
// Register custom components at app launch
HighlightComponent.registerComponent()
RuntimeStateComponent.registerComponent()
```

---

## System Pattern

```swift
/// Systems process entities with matching components each frame.
final class HighlightSystem: System {
    private static let query = EntityQuery(where: .has(HighlightComponent.self))
    private var trackedEntities: Set<Entity> = []

    required init(scene: RealityKit.Scene) {
        // Subscribe to component lifecycle events
        _ = scene.subscribe(to: ComponentEvents.DidActivate.self, componentType: HighlightComponent.self) { [weak self] event in
            self?.trackedEntities.insert(event.entity)
        }

        _ = scene.subscribe(to: ComponentEvents.WillDeactivate.self, componentType: HighlightComponent.self) { [weak self] event in
            self?.trackedEntities.remove(event.entity)
        }
    }

    func update(context: SceneUpdateContext) {
        for entity in context.entities(matching: Self.query, updatingSystemWhen: .rendering) {
            guard var highlight = entity.components[HighlightComponent.self] else { continue }

            // Update component state
            highlight.intensity *= 0.99
            entity.components[HighlightComponent.self] = highlight
        }
    }
}

// Register system at app launch
HighlightSystem.registerSystem()
```

### Ticking Layers

```swift
// Systems can specify when they update
func update(context: SceneUpdateContext) {
    // updatingSystemWhen controls the ticking layer:
    // .rendering  — every frame (default)
    // .physics    — physics tick rate
    for entity in context.entities(matching: Self.query, updatingSystemWhen: .rendering) {
        // ...
    }
}
```

---

## Scene Subscriptions

### Component Events

```swift
// In System.init(scene:) or from a RealityView
let activateSub = scene.subscribe(
    to: ComponentEvents.DidActivate.self,
    componentType: MyComponent.self
) { event in
    let entity = event.entity
    // Component was added and activated
}

let deactivateSub = scene.subscribe(
    to: ComponentEvents.WillDeactivate.self,
    componentType: MyComponent.self
) { event in
    // Component about to be removed
}

let changeSub = scene.subscribe(
    to: ComponentEvents.DidChange.self,
    componentType: MyComponent.self
) { event in
    // Component values changed
}
```

### Scene Events

```swift
// Subscribe to per-frame updates
let updateSub = scene.subscribe(to: SceneEvents.Update.self) { event in
    let deltaTime = event.deltaTime
    // Per-frame logic
}

// Subscribe to anchor changes
let anchorSub = scene.subscribe(to: SceneEvents.AnchoredStateChanged.self) { event in
    // Anchor tracking state changed
}
```

### Component Change Publisher (Combine)

```swift
extension Entity {
    /// Observe changes to a specific component type on this entity.
    func componentChangePublisher<C: Component>(
        _ componentType: C.Type
    ) -> AnyPublisher<C, Never> {
        scene?.publisher(for: ComponentEvents.DidChange.self, on: self, componentType: C.self)
            .compactMap { [weak self] _ in
                self?.components[C.self]
            }
            .eraseToAnyPublisher()
            ?? Empty().eraseToAnyPublisher()
    }
}

// Usage
entity.componentChangePublisher(HighlightComponent.self)
    .sink { updatedComponent in
        print("Highlight changed: \(updatedComponent.intensity)")
    }
    .store(in: &cancellables)
```

---

## RealityView Integration

```swift
import SwiftUI
import RealityKit

struct ImmersiveContentView: View {
    @State private var rootEntity = Entity()

    var body: some View {
        RealityView { content in
            // Initial setup — called once
            let sphere = ModelEntity(
                mesh: .generateSphere(radius: 0.1),
                materials: [SimpleMaterial(color: .blue, isMetallic: true)]
            )
            sphere.position = [0, 1.5, -2]
            rootEntity.addChild(sphere)
            content.add(rootEntity)
        } update: { content in
            // Called when SwiftUI state changes
            // Use to sync SwiftUI state → RealityKit entities
        }
        .gesture(tapGesture)
    }

    var tapGesture: some Gesture {
        SpatialTapGesture()
            .targetedToAnyEntity()
            .onEnded { value in
                let tappedEntity = value.entity
                // Handle tap on entity
            }
    }
}
```

### Lifecycle Management

```swift
struct SceneView: View {
    @State private var rootEntity = Entity()
    @State private var subscriptions: [EventSubscription] = []

    var body: some View {
        RealityView { content in
            content.add(rootEntity)

            // Store subscriptions to keep them alive
            let sub = content.subscribe(to: SceneEvents.Update.self) { event in
                // Per-frame work
            }
            subscriptions.append(sub)
        }
        .onDisappear {
            subscriptions.removeAll()
            rootEntity.children.removeAll()
        }
    }
}
```

---

## Entity Component Operations

```swift
// Read a component
if let highlight = entity.components[HighlightComponent.self] {
    print(highlight.intensity)
}

// Write a component (copy-on-write)
entity.components[HighlightComponent.self] = HighlightComponent(intensity: 0.5)

// Modify in place
entity.components[HighlightComponent.self]?.intensity = 0.5

// Check for component
let hasHighlight = entity.components.has(HighlightComponent.self)

// Remove component
entity.components.remove(HighlightComponent.self)

// Set multiple components
entity.components.set([
    HighlightComponent(intensity: 1.0),
    OpacityComponent(opacity: 0.8)
])
```

---

## AnchorEntity Patterns

```swift
// Head-relative anchor
let headAnchor = AnchorEntity(.head)
headAnchor.position = [0, 0, -1]  // 1 meter in front of user
content.add(headAnchor)

// Plane detection anchor
let floorAnchor = AnchorEntity(.plane(.horizontal, classification: .floor, minimumBounds: [0.5, 0.5]))
content.add(floorAnchor)

// Wall anchor
let wallAnchor = AnchorEntity(.plane(.vertical, classification: .wall, minimumBounds: [0.3, 0.3]))
content.add(wallAnchor)

// Hand anchor
let handAnchor = AnchorEntity(.hand(.left, location: .palm))
content.add(handAnchor)
```

---

## visionOS Scene Types

### ImmersiveSpace

```swift
@main
struct MyApp: App {
    var body: some Scene {
        // Standard window
        WindowGroup {
            ContentView()
        }

        // Immersive space — mixed with passthrough
        ImmersiveSpace(id: "mixedSpace") {
            ImmersiveContentView()
        }
        .immersionStyle(selection: .constant(.mixed), in: .mixed)

        // Full immersion — replaces passthrough
        ImmersiveSpace(id: "fullSpace") {
            FullImmersionView()
        }
        .immersionStyle(selection: .constant(.full), in: .full)

        // Progressive immersion
        ImmersiveSpace(id: "progressiveSpace") {
            ProgressiveView()
        }
        .immersionStyle(selection: .constant(.progressive), in: .progressive)
    }
}
```

### Opening/Dismissing Spaces

```swift
@Environment(\.openImmersiveSpace) private var openImmersiveSpace
@Environment(\.dismissImmersiveSpace) private var dismissImmersiveSpace

func enterImmersive() async {
    let result = await openImmersiveSpace(id: "mixedSpace")
    switch result {
    case .opened: break
    case .userCancelled: break
    case .error(let error): print("Error: \(error)")
    @unknown default: break
    }
}

func exitImmersive() async {
    await dismissImmersiveSpace()
}
```

### Multi-Window Architecture

```swift
@main
struct MultiWindowApp: App {
    var body: some Scene {
        WindowGroup {
            MainView()
        }
        .defaultSize(width: 800, height: 600)

        WindowGroup(id: "detail", for: UUID.self) { $itemId in
            DetailView(itemId: itemId)
        }
        .defaultSize(width: 400, height: 300)

        WindowGroup(id: "settings") {
            SettingsView()
        }
        .defaultSize(width: 500, height: 400)
    }
}
```

---

## Window Placement

```swift
@Environment(\.openWindow) private var openWindow

func openDetailWindow(itemId: UUID) {
    openWindow(id: "detail", value: itemId)
}
```

### Placement Callbacks

```swift
WindowGroup(id: "detail") {
    DetailView()
}
.defaultWindowPlacement { content, context in
    // Place relative to another window
    if let mainWindow = context.windows.first(where: { $0.id == "main" }) {
        return WindowPlacement(.trailing(mainWindow))
    }
    return WindowPlacement(.none)
}
```

---

## Hand Tracking

```swift
import ARKit

actor HandTrackingProvider {
    private let session = ARKitSession()
    private let handTracking = HandTrackingProvider()

    func startTracking() async throws {
        try await session.run([handTracking])
    }

    func latestAnchors() async -> (left: HandAnchor?, right: HandAnchor?) {
        let anchors = handTracking.latestAnchors
        return (left: anchors.leftHand, right: anchors.rightHand)
    }
}
```

### Joint Hierarchy

```swift
// Access specific joints
func fingerTipPosition(hand: HandAnchor, finger: HandSkeleton.JointName.NameCodingKey) -> SIMD3<Float>? {
    guard let skeleton = hand.handSkeleton else { return nil }

    let joint = skeleton.joint(.indexFingerTip)
    guard joint.isTracked else { return nil }

    // Joint transform is relative to hand anchor
    let jointTransform = hand.originFromAnchorTransform * joint.anchorFromJointTransform
    return SIMD3<Float>(jointTransform.columns.3.x, jointTransform.columns.3.y, jointTransform.columns.3.z)
}
```

### Gesture Confidence

```swift
/// Track pinch gesture with confidence scoring.
func pinchDistance(hand: HandAnchor) -> Float? {
    guard let skeleton = hand.handSkeleton else { return nil }

    let thumbTip = skeleton.joint(.thumbTip)
    let indexTip = skeleton.joint(.indexFingerTip)

    guard thumbTip.isTracked, indexTip.isTracked else { return nil }

    let thumbPos = thumbTip.anchorFromJointTransform.columns.3
    let indexPos = indexTip.anchorFromJointTransform.columns.3

    return simd_distance(
        SIMD3(thumbPos.x, thumbPos.y, thumbPos.z),
        SIMD3(indexPos.x, indexPos.y, indexPos.z)
    )
}

let pinchThreshold: Float = 0.02  // 2cm
```

### Palm Velocity Tracking

```swift
/// Track palm movement velocity for gesture detection.
struct PalmTracker {
    private var previousPosition: SIMD3<Float>?
    private var previousTime: TimeInterval?

    mutating func update(hand: HandAnchor, time: TimeInterval) -> SIMD3<Float>? {
        guard let skeleton = hand.handSkeleton else { return nil }
        let wrist = skeleton.joint(.wrist)
        guard wrist.isTracked else { return nil }

        let position = SIMD3<Float>(
            hand.originFromAnchorTransform.columns.3.x,
            hand.originFromAnchorTransform.columns.3.y,
            hand.originFromAnchorTransform.columns.3.z
        )

        defer {
            previousPosition = position
            previousTime = time
        }

        guard let prev = previousPosition, let prevTime = previousTime else { return nil }
        let dt = Float(time - prevTime)
        guard dt > 0 else { return nil }

        return (position - prev) / dt
    }
}
```

---

## @Observable vs @ObservableObject

### Comparison

| Feature | `@Observable` (iOS 17+) | `ObservableObject` |
|---------|------------------------|--------------------|
| Import | `import Observation` | `import Combine` |
| Declaration | `@Observable class` | `class: ObservableObject` |
| Properties | Plain properties (auto-tracked) | `@Published var` required |
| View usage | `@State` or just pass reference | `@StateObject` / `@ObservedObject` |
| Tracking | Per-property (fine-grained) | Whole-object (any `@Published` change) |
| Actor | Works with any isolation | Typically `@MainActor` |
| Performance | Better — only re-renders on accessed property changes | Worse — re-renders on any `@Published` change |

### @Observable (Preferred for iOS 17+)

```swift
import Observation

@Observable
final class FeatureModel {
    var items: [Item] = []
    var isLoading = false
    var errorMessage: String?

    func loadItems() async throws {
        isLoading = true
        defer { isLoading = false }
        items = try await service.fetchItems()
    }
}

struct FeatureView: View {
    @State private var model = FeatureModel()

    var body: some View {
        // Only re-renders when `items` or `isLoading` changes
        // (whichever properties are actually read in body)
        List(model.items) { item in
            Text(item.name)
        }
        .overlay {
            if model.isLoading { ProgressView() }
        }
    }
}
```

### ObservableObject (Pre-iOS 17 or Combine Integration)

```swift
@MainActor
final class FeatureViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var isLoading = false

    func loadItems() async throws {
        isLoading = true
        defer { isLoading = false }
        items = try await service.fetchItems()
    }
}

struct FeatureView: View {
    @StateObject private var viewModel = FeatureViewModel()

    var body: some View {
        // Re-renders on ANY @Published change
        List(viewModel.items) { item in
            Text(item.name)
        }
    }
}
```

### Migration Guidance

- **New projects targeting iOS 17+**: Use `@Observable`
- **Existing projects with Combine pipelines**: Keep `ObservableObject`, migrate gradually
- **Shared ViewModels observed by many views**: `@Observable` gives significant performance gains
- **Need `objectWillChange` publisher**: Stay with `ObservableObject`
- **visionOS apps**: Prefer `@Observable` — it's the standard pattern
