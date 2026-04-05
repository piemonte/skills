---
name: swiftui-architecture
description: Use when building SwiftUI apps — MVVM architecture, ViewModel and View guidelines, service layer patterns, state management, data flow, App Intents, and file organization.
---

# SwiftUI & App Architecture Reference

## MVVM Architecture

### Core Rules

1. **Never put business logic in Views** - Views are for UI only
2. **Always use ViewModels** for state management and business logic
3. **Each feature has both a View and ViewModel** in its own subfolder
4. **ViewModels use `@MainActor`** and conform to `ObservableObject`
5. **Services are accessed through ViewModels**, never directly from Views

### Data Flow

```
User Interaction → View calls ViewModel method
    → ViewModel processes request
    → ViewModel calls Service layer
    → ViewModel updates @Published properties
    → View automatically reacts to state changes
```

---

## ViewModel Pattern

```swift
@MainActor
final class FeatureViewModel: ObservableObject {
    // MARK: - Published Properties (State)
    @Published var items: [ItemModel] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    // MARK: - Private Properties
    private let service = ItemService()  // Actor service
    private var loadingTask: Task<Void, Never>?

    // MARK: - Initialization
    init() {
        loadData()
    }

    deinit {
        loadingTask?.cancel()
    }

    // MARK: - Public Methods (Called by View)
    func loadData() {
        loadingTask?.cancel()
        loadingTask = Task { @MainActor [weak self] in
            guard let self, !Task.isCancelled else { return }
            isLoading = true
            defer { isLoading = false }
            do {
                self.items = try await service.fetchItems()
            } catch {
                guard !Task.isCancelled else { return }
                self.errorMessage = error.localizedDescription
            }
        }
    }

    func handleUserAction() {
        Task {
            do {
                try await service.performAction()
            } catch let error as ServiceError {
                errorMessage = error.localizedDescription
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
}
```

### ViewModel Rules

- `@MainActor` on all ViewModels
- `@Published` for all reactive state
- `final class` conforming to `ObservableObject`
- Task cancellation in `deinit`
- `[weak self]` in Task closures
- Check `Task.isCancelled` before state updates
- ViewModel manages `isLoading`, `error` state (not the service)

---

## View Pattern

```swift
struct FeatureView: View {
    @StateObject private var viewModel = FeatureViewModel()
    @State private var animationState = false  // UI-only state

    var body: some View {
        ScrollView {
            if viewModel.isLoading {
                SkeletonLoadingView()
            } else {
                LazyVStack(spacing: 0) {
                    ForEach(viewModel.items) { item in
                        ItemRowView(item: item)
                    }
                }
            }
        }
        .refreshable {
            await viewModel.refresh()
        }
    }
}
```

### View Rules

- `@StateObject` for ViewModel ownership
- `@ObservedObject` for passed ViewModels
- `@State` only for UI-specific state (animations, sheet presentation)
- No business logic in Views
- Delegate all actions to ViewModel methods
- Use `LazyVStack`/`LazyHStack` for scrollable content

---

## Service Layer Patterns

### Actor Service (Default - 99% of services)

```swift
import Foundation

// MARK: - Service Errors

enum ItemServiceError: LocalizedError, Sendable {
    case invalidURL
    case fetchFailed(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid API URL"
        case .fetchFailed(let msg): return "Fetch failed: \(msg)"
        }
    }
}

// MARK: - Service Implementation

actor ItemService {
    private let session: URLSession

    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 60.0
        self.session = URLSession(configuration: config)
    }

    func fetchItems() async throws -> [ItemModel] {
        let (data, _) = try await session.data(for: request)
        return try JSONDecoder().decode([ItemModel].self, from: data)
    }
}
```

### @MainActor Service (Exception - Only for UI-Observed State)

```swift
@MainActor
final class SharedStateService: ObservableObject {
    static let shared = SharedStateService()
    private init() {}

    @Published var items: [ItemModel] = []
    @Published var isLoading = false

    // Use ONLY when Views directly observe @Published properties
    func addItem(_ item: ItemModel) {
        items.append(item)
    }
}
```

### When to Use Each

| Scenario | Pattern |
|----------|---------|
| API calls, data operations | `actor` |
| Views observe `@Published` properties directly | `@MainActor ObservableObject` |
| Singleton shared state manager | `@MainActor ObservableObject` with `static let shared` |

---

## State Management

### Property Types by Location

| Location | Property Wrapper | Use For |
|----------|-----------------|---------|
| ViewModel | `@Published` | Business state, data, loading, errors |
| View | `@State` | UI-only state (animations, sheet flags) |
| View | `@StateObject` | Owning a ViewModel |
| View | `@ObservedObject` | Receiving a ViewModel from parent |
| View | `@Binding` | Two-way connection to parent state |

### State Rules

- All business state lives in ViewModels
- Only UI state (`@State`) in Views
- Unidirectional data flow: ViewModel -> View
- Views call ViewModel methods for user actions

---

## Loading States

Every data-driven view should show loading skeleton:

```swift
import Shimmer

struct SkeletonRowView: View {
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Circle()
                .fill(Color.gray.opacity(0.2))
                .frame(width: 40, height: 40)
            VStack(alignment: .leading, spacing: 8) {
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.gray.opacity(0.2))
                    .frame(width: 100, height: 12)
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 12)
            }
        }
        .padding()
        .shimmering(
            active: true,
            animation: .linear(duration: 1.5).repeatForever(autoreverses: false)
        )
    }
}
```

---

## Async Patterns in SwiftUI

### Replacing DispatchQueue

```swift
// DispatchQueue.main.asyncAfter → Task.sleep
Task {
    try await Task.sleep(nanoseconds: 2_000_000_000)
    await performAction()
}
```

### Retry Logic

```swift
func fetchWithRetry(maxAttempts: Int = 3) async throws -> Data {
    for attempt in 0..<maxAttempts {
        do {
            return try await performFetch()
        } catch {
            if attempt == maxAttempts - 1 { throw error }
            try await Task.sleep(nanoseconds: 1_000_000_000)
        }
    }
    fatalError("Unreachable")
}
```

### AsyncStream Consumption in ViewModels

```swift
@MainActor
class ObservingViewModel: ObservableObject {
    @Published var messages: [Message] = []
    private var observerTask: Task<Void, Never>?

    init(channelId: String) {
        observerTask = Task {
            for await newMessages in service.observe(channelId) {
                self.messages = newMessages
            }
        }
    }

    deinit {
        observerTask?.cancel()
    }
}
```

---

## Common Swift 6 Warnings & Fixes

**"Main actor-isolated property cannot be mutated from a Sendable closure"**
```swift
// Fix: Already on @MainActor, update directly - no DispatchQueue.main needed
func updateState() {
    isLoading = false
}
```

**"Expression is 'async' but is not marked with 'await'"**
```swift
// Fix: Add async to function signature and await to call
func loadData() async {
    let data = try await service.fetchData()
}
```

---

## File Organization

### Recommended Structure

```
App/
├── AppEntry.swift              # @main SwiftUI app lifecycle
├── ContentView.swift           # Root navigation

Experiences/                    # Feature modules (MVVM)
└── FeatureName/
    ├── FeatureNameView.swift
    └── FeatureNameViewModel.swift

Interface/                      # Shared UI components
├── Shared/                    # Atomic UI elements
└── Views/                     # Composite components

Services/                       # Business logic & APIs

Models/                         # Data structures

Extensions/                     # Type extensions

Resources/                      # Assets, configs
└── Assets.xcassets/           # Single asset catalog
```

### File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Views | `FeatureNameView.swift` | `ProfileView.swift` |
| ViewModels | `FeatureNameViewModel.swift` | `ProfileViewModel.swift` |
| Models | `EntityNameModel.swift` | `UserModel.swift` |
| Services | `PurposeService.swift` | `AuthService.swift` |
| Extensions | `TypeName+Purpose.swift` | `Date+Formatting.swift` |

### When to Create

- **New Experience**: Complete user-facing feature with its own navigation
- **New Service**: External API integration or shared business logic
- **New Interface component**: UI element used in 2+ experiences

---

## iOS 26 App Intents

### IntentValueQuery for Screenshot/Image Search

```swift
// 1. Define query
struct ImageSearchQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [SearchResult] {
        // Process image, extract text via OCR
        // Return matching entities
    }
}

// 2. Define entities
struct PostEntity: AppEntity {
    var displayRepresentation: DisplayRepresentation { /* ... */ }
}

// 3. CRITICAL: OpenIntent MUST exist for each entity type
struct OpenPostIntent: OpenIntent {
    func perform() async throws -> some IntentResult {
        // Deep link to content
    }
}

// 4. Register in shortcuts provider
static var imageSearchQueries: [any IntentValueQuery.Type] {
    if #available(iOS 26.0, *) {
        return [ImageSearchQuery.self]
    }
    return []
}
```

### App Intents Best Practices

- Return multiple pages of results for better matches
- Avoid long search times to prevent unresponsiveness
- Provide "Continue Search" option to open full app
- Implement `OpenIntent` for every entity type returned

---

## SwiftUI Best Practices

- Use `@ViewBuilder` for complex conditional views
- Prefer `LazyVStack`/`LazyHStack` for scrollable content
- Apply animation modifiers consistently
- Use SF Symbols when possible instead of custom images
- Group related assets with prefixes (`icon-*`, `profile-*`, `tab-*`)
- Single asset catalog - never create duplicates

---

## Performance Optimizations

- **Lazy Loading**: `LazyVStack`/`LazyHStack` for large lists
- **Image Caching**: Cache generated/downloaded images
- **Background Processing**: Heavy operations off main thread (actor services)
- **Pagination**: Load data in chunks for infinite scrolling
- **State Minimization**: Keep only necessary state in memory
- **Debouncing**: Debounce frequent updates to avoid excessive re-renders
