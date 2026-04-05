---
name: metal-graphics
description: Use when writing Metal GPU code — compute and render pipelines, buffer management, textures, IOSurface, compute dispatch, ring buffers, shaders, and frame pacing.
---

# Metal GPU Programming Reference

## Device & Command Queue Setup

```swift
import Metal

guard let device = MTLCreateSystemDefaultDevice() else {
    fatalError("Metal is not supported on this device")
}

let commandQueue = device.makeCommandQueue()!

// Command buffer lifecycle
func executeGPUWork() {
    guard let commandBuffer = commandQueue.makeCommandBuffer() else { return }
    defer { commandBuffer.commit() }

    // Encode compute or render work here
    guard let encoder = commandBuffer.makeComputeCommandEncoder() else { return }
    // ... encode work ...
    encoder.endEncoding()
}
```

### Command Buffer with Completion

```swift
let commandBuffer = commandQueue.makeCommandBuffer()!
commandBuffer.addCompletedHandler { buffer in
    if let error = buffer.error {
        print("GPU error: \(error)")
    }
}
// ... encode work ...
commandBuffer.commit()
```

---

## Compute Pipeline Creation

```swift
// Basic compute pipeline
let library = device.makeDefaultLibrary()!
let function = library.makeFunction(name: "myKernel")!
let pipelineState = try device.makeComputePipelineState(function: function)
```

### With Function Constants

```swift
let constants = MTLFunctionConstantValues()
var useHighQuality: Bool = true
constants.setConstantValue(&useHighQuality, type: .bool, index: 0)

var gridSize: UInt32 = 256
constants.setConstantValue(&gridSize, type: .uint, index: 1)

let function = try library.makeFunction(name: "myKernel", constantValues: constants)
let pipelineState = try device.makeComputePipelineState(function: function)
```

### With Binary Archive Caching

```swift
let descriptor = MTLComputePipelineDescriptor()
descriptor.computeFunction = function
descriptor.label = "MyComputePipeline"

// Create or load binary archive for caching compiled pipelines
let archiveDescriptor = MTLBinaryArchiveDescriptor()
archiveDescriptor.url = cacheURL
let archive = try device.makeBinaryArchive(descriptor: archiveDescriptor)

descriptor.binaryArchives = [archive]
let pipelineState = try device.makeComputePipelineState(
    descriptor: descriptor,
    options: [],
    reflection: nil
)

// Serialize archive for next launch
try archive.serialize(to: cacheURL)
```

---

## Render Pipeline Creation

```swift
let vertexFunction = library.makeFunction(name: "vertexShader")
let fragmentFunction = library.makeFunction(name: "fragmentShader")

let descriptor = MTLRenderPipelineDescriptor()
descriptor.vertexFunction = vertexFunction
descriptor.fragmentFunction = fragmentFunction
descriptor.colorAttachments[0].pixelFormat = .bgra8Unorm

// Alpha blending
descriptor.colorAttachments[0].isBlendingEnabled = true
descriptor.colorAttachments[0].sourceRGBBlendFactor = .sourceAlpha
descriptor.colorAttachments[0].destinationRGBBlendFactor = .oneMinusSourceAlpha
descriptor.colorAttachments[0].sourceAlphaBlendFactor = .one
descriptor.colorAttachments[0].destinationAlphaBlendFactor = .oneMinusSourceAlpha

descriptor.depthAttachmentPixelFormat = .depth32Float
descriptor.label = "MyRenderPipeline"

let renderPipelineState = try device.makeRenderPipelineState(descriptor: descriptor)
```

### Vertex Descriptor

```swift
let vertexDescriptor = MTLVertexDescriptor()

// Position attribute
vertexDescriptor.attributes[0].format = .float3
vertexDescriptor.attributes[0].offset = 0
vertexDescriptor.attributes[0].bufferIndex = 0

// UV attribute
vertexDescriptor.attributes[1].format = .float2
vertexDescriptor.attributes[1].offset = MemoryLayout<SIMD3<Float>>.stride
vertexDescriptor.attributes[1].bufferIndex = 0

// Layout
vertexDescriptor.layouts[0].stride = MemoryLayout<SIMD3<Float>>.stride + MemoryLayout<SIMD2<Float>>.stride

descriptor.vertexDescriptor = vertexDescriptor
```

### Render Pass Descriptor

```swift
let renderPassDescriptor = MTLRenderPassDescriptor()
renderPassDescriptor.colorAttachments[0].texture = drawable.texture
renderPassDescriptor.colorAttachments[0].loadAction = .clear
renderPassDescriptor.colorAttachments[0].storeAction = .store
renderPassDescriptor.colorAttachments[0].clearColor = MTLClearColor(red: 0, green: 0, blue: 0, alpha: 1)

renderPassDescriptor.depthAttachment.texture = depthTexture
renderPassDescriptor.depthAttachment.loadAction = .clear
renderPassDescriptor.depthAttachment.storeAction = .dontCare
renderPassDescriptor.depthAttachment.clearDepth = 1.0

guard let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: renderPassDescriptor) else { return }
encoder.setRenderPipelineState(renderPipelineState)
// ... draw calls ...
encoder.endEncoding()
```

---

## Generic Buffer Management

```swift
/// Type-safe Metal buffer wrapper with stride and count tracking.
struct MetalBuffer<Element> {
    let buffer: MTLBuffer
    let count: Int
    let stride: Int
    let index: Int

    init(device: MTLDevice, array: [Element], index: Int, options: MTLResourceOptions = []) {
        self.stride = MemoryLayout<Element>.stride
        self.count = array.count
        self.index = index
        self.buffer = device.makeBuffer(
            bytes: array,
            length: stride * count,
            options: options
        )!
    }

    init(device: MTLDevice, count: Int, index: Int, options: MTLResourceOptions = []) {
        self.stride = MemoryLayout<Element>.stride
        self.count = count
        self.index = index
        self.buffer = device.makeBuffer(
            length: stride * count,
            options: options
        )!
    }

    /// Access buffer contents as typed pointer.
    func contents() -> UnsafeMutablePointer<Element> {
        buffer.contents().bindMemory(to: Element.self, capacity: count)
    }
}

// Usage
let vertexBuffer = MetalBuffer<Vertex>(device: device, array: vertices, index: 0)
encoder.setVertexBuffer(vertexBuffer.buffer, offset: 0, index: vertexBuffer.index)
```

---

## Ring Buffer Pattern

```swift
/// Multi-frame GPU pipelining buffer. Cycles through a pool of buffers
/// to avoid CPU-GPU synchronization stalls.
final class MTLRingBuffer<Element> {
    private let buffers: [MTLBuffer]
    private let stride: Int
    private let count: Int
    private var readIndex: Int = 0
    private var writeIndex: Int = 0
    private let poolSize: Int

    init(device: MTLDevice, count: Int, poolSize: Int = 3, options: MTLResourceOptions = []) {
        self.stride = MemoryLayout<Element>.stride
        self.count = count
        self.poolSize = poolSize
        self.buffers = (0..<poolSize).map { _ in
            device.makeBuffer(length: MemoryLayout<Element>.stride * count, options: options)!
        }
    }

    /// Current buffer for writing (CPU side).
    var writeBuffer: MTLBuffer { buffers[writeIndex % poolSize] }

    /// Current buffer for reading (GPU side).
    var readBuffer: MTLBuffer { buffers[readIndex % poolSize] }

    /// Write contents to current write buffer.
    func write(_ data: [Element]) {
        let pointer = writeBuffer.contents().bindMemory(to: Element.self, capacity: count)
        data.withUnsafeBufferPointer { src in
            pointer.update(from: src.baseAddress!, count: min(data.count, count))
        }
    }

    /// Advance to next buffer after frame submission.
    func tick() {
        writeIndex += 1
    }

    /// Advance read pointer after GPU completion.
    func tickRead() {
        readIndex += 1
    }
}

// Usage: triple-buffered uniforms
let uniformRing = MTLRingBuffer<Uniforms>(device: device, count: 1, poolSize: 3)
uniformRing.write([currentUniforms])
encoder.setVertexBuffer(uniformRing.writeBuffer, offset: 0, index: 1)
uniformRing.tick()
```

---

## Texture Management

### Creating Textures

```swift
let descriptor = MTLTextureDescriptor()
descriptor.pixelFormat = .rgba8Unorm
descriptor.width = width
descriptor.height = height
descriptor.usage = [.shaderRead, .shaderWrite]
descriptor.storageMode = .private  // GPU-only

let texture = device.makeTexture(descriptor: descriptor)!
```

### IOSurface-Backed Textures

```swift
/// Textures backed by IOSurface allow sharing between processes and frameworks.
let descriptor = MTLTextureDescriptor.texture2DDescriptor(
    pixelFormat: .bgra8Unorm,
    width: width,
    height: height,
    mipmapped: false
)
descriptor.usage = [.shaderRead, .renderTarget]
descriptor.storageMode = .shared

let surface: IOSurface = // ... obtained IOSurface
let texture = device.makeTexture(descriptor: descriptor, iosurface: surface, plane: 0)!
```

### Ring Buffer Texture (Lazy Allocation)

```swift
/// Lazily allocated texture pool for multi-frame rendering.
final class RingBufferTexture {
    private var textures: [MTLTexture?]
    private let descriptor: MTLTextureDescriptor
    private let device: MTLDevice
    private var index: Int = 0
    private let poolSize: Int

    init(device: MTLDevice, descriptor: MTLTextureDescriptor, poolSize: Int = 3) {
        self.device = device
        self.descriptor = descriptor
        self.poolSize = poolSize
        self.textures = Array(repeating: nil, count: poolSize)
    }

    /// Get current texture, creating lazily if needed.
    var current: MTLTexture {
        if textures[index % poolSize] == nil {
            textures[index % poolSize] = device.makeTexture(descriptor: descriptor)
        }
        return textures[index % poolSize]!
    }

    func tick() { index += 1 }
}
```

---

## IOSurface Helpers

```swift
import IOSurface

/// Create an IOSurface with specified dimensions and pixel format.
func createIOSurface(width: Int, height: Int, bytesPerElement: Int = 4, pixelFormat: OSType = kCVPixelFormatType_32BGRA) -> IOSurface {
    let properties: [IOSurfacePropertyKey: Any] = [
        .width: width,
        .height: height,
        .bytesPerElement: bytesPerElement,
        .bytesPerRow: width * bytesPerElement,
        .allocSize: width * height * bytesPerElement,
        .pixelFormat: pixelFormat
    ]
    return IOSurface(properties: properties)!
}

/// Lock/unlock pattern for safe CPU access to IOSurface data.
func withIOSurfaceLock<T>(_ surface: IOSurface, _ body: (UnsafeMutableRawPointer) throws -> T) rethrows -> T {
    surface.lock(options: [], seed: nil)
    defer { surface.unlock(options: [], seed: nil) }
    return try body(surface.baseAddress)
}

/// Copy pixel data into an IOSurface.
func fillIOSurface(_ surface: IOSurface, with data: Data) {
    withIOSurfaceLock(surface) { baseAddress in
        data.withUnsafeBytes { bytes in
            baseAddress.copyMemory(
                from: bytes.baseAddress!,
                byteCount: min(data.count, surface.allocationSize)
            )
        }
    }
}
```

---

## Compute Dispatch Patterns

### Threadgroup Sizing

```swift
/// Calculate optimal threadgroup size from pipeline state.
func optimalThreadgroupSize(for pipelineState: MTLComputePipelineState) -> MTLSize {
    let maxThreads = pipelineState.maxTotalThreadsPerThreadgroup
    let threadWidth = pipelineState.threadExecutionWidth
    return MTLSize(width: threadWidth, height: maxThreads / threadWidth, depth: 1)
}
```

### 1D Dispatch

```swift
func dispatch1D(
    encoder: MTLComputeCommandEncoder,
    pipelineState: MTLComputePipelineState,
    elementCount: Int
) {
    let threadsPerGroup = min(
        elementCount,
        pipelineState.maxTotalThreadsPerThreadgroup
    )
    let threadgroupSize = MTLSize(width: threadsPerGroup, height: 1, depth: 1)
    let gridSize = MTLSize(width: elementCount, height: 1, depth: 1)

    encoder.setComputePipelineState(pipelineState)
    encoder.dispatchThreads(gridSize, threadsPerThreadgroup: threadgroupSize)
}
```

### 2D Dispatch

```swift
func dispatch2D(
    encoder: MTLComputeCommandEncoder,
    pipelineState: MTLComputePipelineState,
    width: Int,
    height: Int
) {
    let threadWidth = pipelineState.threadExecutionWidth
    let maxThreads = pipelineState.maxTotalThreadsPerThreadgroup
    let threadHeight = maxThreads / threadWidth

    let threadgroupSize = MTLSize(width: threadWidth, height: threadHeight, depth: 1)
    let gridSize = MTLSize(width: width, height: height, depth: 1)

    encoder.setComputePipelineState(pipelineState)
    encoder.dispatchThreads(gridSize, threadsPerThreadgroup: threadgroupSize)
}
```

---

## Shader Function Loading

### Loading from Bundle Library

```swift
func loadFunction(
    name: String,
    from library: MTLLibrary,
    constants: MTLFunctionConstantValues? = nil
) throws -> MTLFunction {
    if let constants {
        return try library.makeFunction(name: name, constantValues: constants)
    }
    guard let function = library.makeFunction(name: name) else {
        throw MetalError.functionNotFound(name)
    }
    return function
}
```

### Function Constants with Type Mapping

```swift
/// Build function constants from a dictionary of values.
func makeFunctionConstants(_ values: [(index: Int, value: Any, type: MTLDataType)]) -> MTLFunctionConstantValues {
    let constants = MTLFunctionConstantValues()
    for entry in values {
        var value = entry.value
        constants.setConstantValue(&value, type: entry.type, index: entry.index)
    }
    return constants
}

// Usage
let constants = makeFunctionConstants([
    (index: 0, value: true, type: .bool),
    (index: 1, value: UInt32(256), type: .uint),
    (index: 2, value: Float(0.5), type: .float)
])
```

---

## Metal Shader Structure

### Compute Kernel

```metal
#include <metal_stdlib>
using namespace metal;

// Function constants for compile-time specialization
constant bool useHighQuality [[function_constant(0)]];
constant uint gridSize [[function_constant(1)]];

kernel void processData(
    device float4 *input [[buffer(0)]],
    device float4 *output [[buffer(1)]],
    constant Uniforms &uniforms [[buffer(2)]],
    uint tid [[thread_position_in_grid]],
    uint tgid [[thread_position_in_threadgroup]],
    uint tgSize [[threads_per_threadgroup]]
) {
    if (tid >= uniforms.elementCount) return;

    float4 value = input[tid];
    // ... processing ...
    output[tid] = value;
}
```

### Vertex/Fragment Shaders

```metal
struct VertexIn {
    float3 position [[attribute(0)]];
    float2 texCoord [[attribute(1)]];
};

struct VertexOut {
    float4 position [[position]];
    float2 texCoord;
};

vertex VertexOut vertexShader(
    VertexIn in [[stage_in]],
    constant float4x4 &mvp [[buffer(1)]]
) {
    VertexOut out;
    out.position = mvp * float4(in.position, 1.0);
    out.texCoord = in.texCoord;
    return out;
}

fragment half4 fragmentShader(
    VertexOut in [[stage_in]],
    texture2d<half> colorTexture [[texture(0)]],
    sampler textureSampler [[sampler(0)]]
) {
    return colorTexture.sample(textureSampler, in.texCoord);
}
```

### Threadgroup Memory

```metal
kernel void reductionKernel(
    device float *input [[buffer(0)]],
    device float *output [[buffer(1)]],
    threadgroup float *shared [[threadgroup(0)]],
    uint tid [[thread_position_in_grid]],
    uint localId [[thread_position_in_threadgroup]],
    uint groupSize [[threads_per_threadgroup]]
) {
    shared[localId] = input[tid];
    threadgroup_barrier(mem_flags::mem_threadgroup);

    // Parallel reduction
    for (uint stride = groupSize / 2; stride > 0; stride >>= 1) {
        if (localId < stride) {
            shared[localId] += shared[localId + stride];
        }
        threadgroup_barrier(mem_flags::mem_threadgroup);
    }

    if (localId == 0) {
        output[tid / groupSize] = shared[0];
    }
}
```

### Common Metal Types

| Swift | Metal | Notes |
|-------|-------|-------|
| `SIMD2<Float>` | `float2` | 2D vector |
| `SIMD3<Float>` | `float3` | 3D vector |
| `SIMD4<Float>` | `float4` / `half4` | 4D vector, half precision for color |
| `simd_float4x4` | `float4x4` | Transform matrix |
| `UInt32` | `uint` | Unsigned integer |
| `Float` | `float` | Single precision |
| `Bool` | `bool` | Boolean |

---

## Frame Pacing

```swift
import os

/// Manages GPU frame submission to prevent CPU from getting too far ahead.
final class FramePacer {
    private let maxInFlight: Int
    private let semaphore: DispatchSemaphore
    private let inFlightCount = OSAllocatedUnfairLock(initialState: 0)

    init(maxInFlight: Int = 3) {
        self.maxInFlight = maxInFlight
        self.semaphore = DispatchSemaphore(value: maxInFlight)
    }

    /// Wait for a slot to become available before encoding.
    func waitForSlot() {
        semaphore.wait()
        inFlightCount.withLock { $0 += 1 }
    }

    /// Signal completion from command buffer's completed handler.
    func signalCompletion() {
        inFlightCount.withLock { $0 -= 1 }
        semaphore.signal()
    }

    var currentInFlight: Int {
        inFlightCount.withLock { $0 }
    }
}

// Usage in render loop
let framePacer = FramePacer(maxInFlight: 3)

func render() {
    framePacer.waitForSlot()

    guard let commandBuffer = commandQueue.makeCommandBuffer() else {
        framePacer.signalCompletion()
        return
    }

    commandBuffer.addCompletedHandler { [framePacer] _ in
        framePacer.signalCompletion()
    }

    // ... encode frame ...
    commandBuffer.commit()
}
```

### Metal Error Type

```swift
enum MetalError: LocalizedError, Sendable {
    case deviceNotFound
    case functionNotFound(String)
    case pipelineCreationFailed(String)
    case bufferCreationFailed

    var errorDescription: String? {
        switch self {
        case .deviceNotFound: return "No Metal-compatible GPU found"
        case .functionNotFound(let name): return "Shader function not found: \(name)"
        case .pipelineCreationFailed(let reason): return "Pipeline creation failed: \(reason)"
        case .bufferCreationFailed: return "Failed to create Metal buffer"
        }
    }
}
```
