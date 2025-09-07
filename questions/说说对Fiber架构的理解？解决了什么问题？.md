# 说说对 Fiber 架构的理解？解决了什么问题？

## meta 元数据



```
{

&#x20; "id": "f1b2e3r4-f5i6-7890-berf-1234567890ab",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・Fiber 是 React 16 推出的新型协调引擎，是对堆栈的重新实现，目的是优化渲染性能。

・解决了传统 Stack reconciler 无法中断和恢复的问题，避免长时间占用主线程。

・实现了任务的分片处理和优先级调度，能暂停、继续甚至放弃任务执行。

・采用增量渲染，将渲染工作拆分成小单元，按优先级依次处理。

・借助双缓存机制提升渲染效率，减少页面卡顿现象。

## 答案 2：口语化扩展回答

Fiber 架构是 React 为解决大型应用渲染性能问题而设计的。在之前的版本中，React 采用递归方式更新组件，一旦开始就无法停止。要是组件树规模较大，会长期占用主线程，致使页面卡顿，用户操作没有响应。

Fiber 把渲染工作分解成很多小任务，每个任务执行一部分后，就会检查是否有更高优先级的工作，像用户输入、动画这些。如果有，就暂停当前任务，先处理更紧急的，处理完再回来继续执行原来的任务。这样一来，浏览器就有时间处理其他事务，页面也会更流畅。

在实际开发中，使用 Fiber 后，复杂页面的交互体验有了明显改善，尤其是在存在大量动画和用户输入的场景中。不过，它也并非完美无缺，由于要处理任务的暂停和恢复，需要保存更多的中间状态，内存占用会稍微增加。但总体而言，利远大于弊，如今它已成为 React 的核心架构。

## 答案 3：技术深度解析

### 什么是 Fiber 架构

Fiber 是 React 16 中引入的全新协调（reconciliation）引擎，其设计目标是实现增量渲染（Incremental Rendering），允许 React 中断、暂停、恢复甚至放弃渲染工作。

从技术角度看，Fiber 可以理解为：



*   一种数据结构：每个 Fiber 节点对应一个组件，存储了组件的类型、DOM 信息、指针信息等。

*   一种工作单元：每个 Fiber 节点代表一个工作单元，包含了需要执行的任务。

### 解决的核心问题

传统 Stack Reconciler 存在的问题：



1.  递归遍历组件树，过程无法中断，长时间占用主线程，影响其他任务执行。

2.  不能对任务进行优先级处理，对于动画、用户输入等紧急任务无法优先响应。

3.  在大型应用中，容易出现 UI 卡顿现象，严重影响用户体验。

Fiber 架构通过以下方式解决这些问题：



1.  **任务分解**：将渲染工作分解为多个小单元，每个单元对应一个 Fiber 节点，便于分步处理。

2.  **优先级调度**：根据任务类型为其分配不同优先级，高优先级任务可以中断低优先级任务的执行。

3.  **可中断与恢复**：记录任务执行的状态信息，使得任务可以被暂停、恢复甚至终止。

4.  **双缓存机制**：维护 current 和 workInProgress 两棵树，通过树的替换提高渲染效率。

### 核心实现原理

#### Fiber 数据结构



```
function FiberNode(tag, pendingProps, key, mode) {

&#x20; // 组件类型信息

&#x20; this.tag = tag; // 标识节点类型，如函数组件、类组件、宿主组件等

&#x20; this.key = key; // 节点key值

&#x20; this.elementType = null; // 元素类型

&#x20; this.type = null; // 节点类型，与elementType可能不同，如lazy组件

&#x20; this.stateNode = null; // 对应的真实DOM节点或组件实例

&#x20; // 指向其他Fiber节点的指针，形成Fiber树结构

&#x20; this.return = null; // 父节点

&#x20; this.child = null; // 子节点

&#x20; this.sibling = null; // 兄弟节点

&#x20; this.index = 0; // 索引

&#x20; this.ref = null; // ref引用

&#x20; // 工作单元相关属性

&#x20; this.pendingProps = pendingProps; // 待处理的props

&#x20; this.memoizedProps = null; // 上一次处理的props

&#x20; this.updateQueue = null; // 状态更新队列

&#x20; this.memoizedState = null; // 上一次处理的state

&#x20; this.dependencies = null; // 依赖项

&#x20; this.mode = mode; // 模式，如ConcurrentMode、StrictMode等

&#x20; // 用于任务调度的属性

&#x20; this.effectTag = NoEffect; // 标记需要执行的副作用类型

&#x20; this.nextEffect = null; // 下一个有副作用的Fiber节点

&#x20; this.firstEffect = null; // 第一个有副作用的Fiber节点

&#x20; this.lastEffect = null; // 最后一个有副作用的Fiber节点

&#x20; // 优先级相关

&#x20; this.lanes = NoLanes; // 节点的优先级 lanes

&#x20; this.childLanes = NoLanes; // 子节点的优先级 lanes

&#x20; // 用于调试

&#x20; this.debugID = debugCounter++;

&#x20; this.debugSource = null;

&#x20; this.debugOwner = null;

}
```

#### 工作流程

Fiber 架构的工作流程分为两个主要阶段：



1.  **调度阶段（Reconciliation）**：

*   遍历 Fiber 树，找出需要更新的部分。

*   该阶段可以被中断，以便进行优先级调度。

*   生成 Effect List（记录需要执行的副作用）。



```
// 简化的调度阶段逻辑

function workLoop(hasTimeRemaining, initialLane) {

&#x20; let currentTime = requestCurrentTimeForUpdate();

&#x20; let expirationTime = computeExpirationForFiber(initialLane, currentTime);

&#x20;&#x20;

&#x20; // 循环处理工作单元，当有剩余时间且存在工作单元时继续执行

&#x20; while (workInProgress !== null && !shouldYieldToRenderer()) {

&#x20;   workInProgress = performUnitOfWork(workInProgress);

&#x20; }

&#x20;&#x20;

&#x20; // 如果还有未完成的工作，请求下一次调度

&#x20; if (workInProgress !== null) {

&#x20;   return true;

&#x20; } else {

&#x20;   // 进入提交阶段

&#x20;   performSyncWorkOnRoot(root);

&#x20;   return false;

&#x20; }

}

// 处理单个工作单元

function performUnitOfWork(unitOfWork) {

&#x20; // 1. 处理当前Fiber节点

&#x20; const current = unitOfWork.alternate;

&#x20; const next = beginWork(current, unitOfWork, renderLanes);

&#x20;&#x20;

&#x20; // 2. 如果有子节点，下一个工作单元是子节点

&#x20; if (next !== null) {

&#x20;   workInProgress = next;

&#x20;   return next;

&#x20; }

&#x20;&#x20;

&#x20; // 3. 没有子节点，返回兄弟节点或父节点

&#x20; let completedWork = unitOfWork;

&#x20; while (completedWork !== null) {

&#x20;   completeUnitOfWork(completedWork);

&#x20;   const sibling = completedWork.sibling;

&#x20;   if (sibling !== null) {

&#x20;     workInProgress = sibling;

&#x20;     return sibling;

&#x20;   }

&#x20;   completedWork = completedWork.return;

&#x20; }

&#x20;&#x20;

&#x20; return null;

}
```



1.  **提交阶段（Commit）**：

*   执行实际的 DOM 操作。

*   该阶段不可中断，一旦开始必须执行完成。

*   分为 before mutation、mutation 和 layout 三个子阶段。



```
// 简化的提交阶段逻辑

function commitRoot(root) {

&#x20; const { finishedWork } = root;

&#x20;&#x20;

&#x20; // 1. before mutation阶段：执行DOM操作前的准备工作，如读取DOM属性等

&#x20; commitBeforeMutationEffects(finishedWork);

&#x20;&#x20;

&#x20; // 2. mutation阶段：执行实际的DOM操作，如添加、删除、更新DOM节点

&#x20; commitMutationEffects(finishedWork, root);

&#x20;&#x20;

&#x20; // 3. 将workInProgress树设置为current树，完成树的替换

&#x20; root.current = finishedWork;

&#x20;&#x20;

&#x20; // 4. layout阶段：执行DOM操作后的工作，如调用useLayoutEffect回调、更新ref等

&#x20; commitLayoutEffects(finishedWork, root);

}
```

#### 优先级调度机制

Fiber 架构定义了不同优先级的任务，紧急任务可以中断低优先级任务：



```
// 优先级定义（数值越小优先级越高）

const ImmediatePriority = 1; // 立即执行，如用户输入，需要马上响应

const UserBlockingPriority = 2; // 用户阻塞优先级，如动画，影响用户视觉体验

const NormalPriority = 3; // 正常优先级，如网络请求返回后的处理

const LowPriority = 4; // 低优先级，如非紧急数据处理

const IdlePriority = 5; // 空闲优先级，如日志记录，只有在浏览器空闲时才执行
```

调度器通过`requestIdleCallback`或`setTimeout`模拟浏览器空闲时间，判断是否应该让出主线程：



```
// 判断是否应该让出主线程

function shouldYieldToRenderer() {

&#x20; const currentTime = getCurrentTime();

&#x20; // 如果当前时间超过了任务的过期时间，继续执行，避免任务过期

&#x20; if (currentTime >= expirationTime) {

&#x20;   return false;

&#x20; }

&#x20; // 检查是否有更高优先级的任务，如果有则让出主线程

&#x20; if (hasHigherPriorityWork()) {

&#x20;   return true;

&#x20; }

&#x20; // 检查是否超过了浏览器每帧的时间（约16ms），避免影响页面流畅度

&#x20; return currentTime >= frameDeadline;

}
```

### 实际应用中的注意事项



1.  **避免长时间同步任务**：即使使用 Fiber 架构，长时间的同步计算仍然会阻塞渲染，导致页面卡顿。在开发中，应尽量将复杂计算拆分成小任务，或使用 Web Worker 处理。

2.  **合理使用 useDeferredValue**：`useDeferredValue`可以将低优先级状态更新延迟到空闲时间执行，避免影响高优先级任务，提升用户体验。

3.  **注意 useEffect 与 useLayoutEffect 的区别**：

*   `useEffect`在浏览器渲染后执行（异步），不会阻塞浏览器绘制。

*   `useLayoutEffect`在 DOM 更新后、浏览器绘制前执行（同步），会阻塞浏览器绘制，适用于需要在绘制前获取 DOM 信息并进行处理的场景。

### 未来演进

Fiber 架构在 React 18 中得到进一步增强，结合并发特性（Concurrent Features）提供了更精细的调度控制：



1.  **自动批处理更新**：合并多个状态更新，减少渲染次数，提高性能。

2.  **Transitions API**：区分紧急和非紧急更新，紧急更新立即执行，非紧急更新可被中断。

3.  **Suspense 改进**：更好地支持数据获取和代码分割，提升应用加载性能。

Fiber 架构的设计理念影响了许多现代前端框架，成为构建高性能 UI 库的重要参考，其核心思想在未来的前端发展中仍将具有重要意义。

