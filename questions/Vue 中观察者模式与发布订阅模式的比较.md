# 观察者模式在 Vue 响应式系统中的实现原理，与发布订阅模式的核心区别是什么？

## meta 元数据



```
{

&#x20; "id": "b8c9d0e1-f2a3-4567-bcde-890abcdef123",

&#x20; "type": "answer",

&#x20; "difficulty": "difficult",

&#x20; "tags": \["Vue", "设计模式"]

}
```

## 答案 1：核心简洁的口语化回答

・Vue 响应式系统通过观察者模式实现：数据对象作为被观察者，组件渲染函数作为观察者

・核心是数据劫持（Object.defineProperty 或 Proxy）+ 依赖收集，数据变化时自动通知更新

・依赖收集发生在模板编译 / 渲染阶段，建立数据与视图的对应关系

・与发布订阅模式的区别：Vue 中观察者（Watcher）与被观察者（数据）直接关联，无中间事件总线

・发布订阅模式有独立事件中心，发布者和订阅者完全解耦，彼此不知对方存在

## 答案 2：口语化扩展回答

Vue 的响应式系统本质上是用了观察者模式来实现数据驱动视图。当我们把数据对象传入 Vue 实例时，Vue 会通过 Object.defineProperty（Vue2）或 Proxy（Vue3）对数据进行劫持，这样就能知道数据什么时候被读取、什么时候被修改了。

在组件渲染的时候，Vue 会去读取数据，这时候就会触发 getter，把当前的渲染函数（或者说 Watcher）记录下来，这就是依赖收集。以后当数据发生变化时，会触发 setter，这时候 Vue 就知道哪些地方用到了这个数据，会通知对应的 Watcher 去重新执行，也就是重新渲染组件。

这和发布订阅模式不一样的是，Vue 里的数据和使用数据的组件是直接关联的，数据知道有哪些组件在用它。而发布订阅模式里有个中间的事件中心，发布者只负责发消息，订阅者只负责收消息，双方根本不认识，完全通过事件名来联系。所以 Vue 的响应式是更直接的依赖关系，而发布订阅模式耦合度更低，适合更复杂的跨模块通信。

## 答案 3：技术深度解析

### Vue 响应式系统的观察者模式实现原理

Vue 的响应式系统是观察者模式的经典实践，其核心机制可概括为：**数据劫持 + 依赖收集 + 通知更新**。下面以 Vue2 为例详细解析实现原理：

#### 1. 核心组件

Vue 响应式系统包含三个核心角色，对应观察者模式的经典结构：



*   **被观察者（Observable）**：经过劫持处理的数据对象，能感知自身变化

*   **观察者（Watcher）**：负责接收数据变化通知并执行相应操作（如重新渲染）

*   **依赖收集器（Dep）**：连接被观察者和观察者的桥梁，管理依赖关系

#### 2. 实现流程



```
// 1. 数据劫持：将普通对象转换为响应式对象

function observe(data) {

&#x20; // 非对象类型直接返回

&#x20; if (typeof data !== 'object' || data === null) {

&#x20;   return;

&#x20; }

&#x20;&#x20;

&#x20; // 为对象创建观察者实例

&#x20; return new Observer(data);

}

// 2. 观察者类（被观察者的管理者）

class Observer {

&#x20; constructor(data) {

&#x20;   this.data = data;

&#x20;   // 为每个响应式对象创建依赖收集器

&#x20;   this.dep = new Dep();

&#x20;   // 遍历对象属性进行劫持

&#x20;   this.walk(data);

&#x20; }

&#x20;&#x20;

&#x20; // 遍历对象属性

&#x20; walk(data) {

&#x20;   Object.keys(data).forEach(key => {

&#x20;     this.defineReactive(data, key, data\[key]);

&#x20;   });

&#x20; }

&#x20;&#x20;

&#x20; // 劫持属性：定义 getter 和 setter

&#x20; defineReactive(obj, key, val) {

&#x20;   const dep = this.dep;

&#x20;   // 递归处理子属性

&#x20;   const childOb = observe(val);

&#x20;  &#x20;

&#x20;   // 核心：重定义属性的 getter 和 setter

&#x20;   Object.defineProperty(obj, key, {

&#x20;     enumerable: true,

&#x20;     configurable: true,

&#x20;    &#x20;

&#x20;     // 3. 依赖收集：当属性被访问时触发

&#x20;     get() {

&#x20;       // 如果存在当前活跃的 Watcher，建立依赖关系

&#x20;       if (Dep.target) {

&#x20;         // 当前属性收集依赖

&#x20;         dep.depend();

&#x20;         // 如果子属性也是响应式对象，也收集依赖

&#x20;         if (childOb) {

&#x20;           childOb.dep.depend();

&#x20;         }

&#x20;       }

&#x20;       return val;

&#x20;     },

&#x20;    &#x20;

&#x20;     // 4. 通知更新：当属性被修改时触发

&#x20;     set(newVal) {

&#x20;       // 值未变化则不处理

&#x20;       if (val === newVal) return;

&#x20;      &#x20;

&#x20;       val = newVal;

&#x20;       // 新值也需要变为响应式

&#x20;       observe(newVal);

&#x20;      &#x20;

&#x20;       // 通知所有依赖该属性的 Watcher 更新

&#x20;       dep.notify();

&#x20;     }

&#x20;   });

&#x20; }

}

// 5. 依赖收集器（连接被观察者和观察者）

class Dep {

&#x20; constructor() {

&#x20;   // 存储所有依赖（Watcher 实例）

&#x20;   this.subs = \[];

&#x20; }

&#x20;&#x20;

&#x20; // 添加依赖

&#x20; addSub(sub) {

&#x20;   this.subs.push(sub);

&#x20; }

&#x20;&#x20;

&#x20; // 移除依赖

&#x20; removeSub(sub) {

&#x20;   const index = this.subs.indexOf(sub);

&#x20;   if (index > -1) {

&#x20;     this.subs.splice(index, 1);

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 建立依赖关系（让 Watcher 记住当前 Dep）

&#x20; depend() {

&#x20;   if (Dep.target) {

&#x20;     Dep.target.addDep(this);

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 通知所有依赖更新

&#x20; notify() {

&#x20;   // 复制一份避免循环中修改数组

&#x20;   const subs = this.subs.slice();

&#x20;   // 遍历所有依赖，触发更新

&#x20;   subs.forEach(sub => sub.update());

&#x20; }

}

// 6. 观察者（Watcher）

class Watcher {

&#x20; /\*\*

&#x20;  \* 初始化观察者

&#x20;  \* @param {Object} vm - Vue 实例

&#x20;  \* @param {Function|string} expOrFn - 表达式或更新函数

&#x20;  \* @param {Function} cb - 回调函数

&#x20;  \*/

&#x20; constructor(vm, expOrFn, cb) {

&#x20;   this.vm = vm;

&#x20;   this.cb = cb; // 数据变化后的回调

&#x20;   this.deps = \[]; // 存储该 Watcher 依赖的所有 Dep

&#x20;   this.depIds = new Set(); // 用于去重

&#x20;  &#x20;

&#x20;   // 解析表达式，获取更新函数

&#x20;   if (typeof expOrFn === 'function') {

&#x20;     this.getter = expOrFn;

&#x20;   } else {

&#x20;     this.getter = this.parsePath(expOrFn);

&#x20;   }

&#x20;  &#x20;

&#x20;   // 初始化：执行 getter 进行依赖收集

&#x20;   this.value = this.get();

&#x20; }

&#x20;&#x20;

&#x20; // 执行 getter 并收集依赖

&#x20; get() {

&#x20;   // 将当前 Watcher 设为全局目标

&#x20;   Dep.target = this;

&#x20;   // 执行 getter，触发数据的 getter，从而收集依赖

&#x20;   const value = this.getter.call(this.vm, this.vm);

&#x20;   // 重置全局目标

&#x20;   Dep.target = null;

&#x20;   return value;

&#x20; }

&#x20;&#x20;

&#x20; // 更新方法：数据变化时被调用

&#x20; update() {

&#x20;   // 异步更新队列（Vue 优化点）

&#x20;   queueWatcher(this);

&#x20; }

&#x20;&#x20;

&#x20; // 实际执行更新

&#x20; run() {

&#x20;   const newValue = this.get();

&#x20;   const oldValue = this.value;

&#x20;   if (newValue !== oldValue) {

&#x20;     this.value = newValue;

&#x20;     // 执行回调（如重新渲染组件）

&#x20;     this.cb.call(this.vm, newValue, oldValue);

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 添加依赖

&#x20; addDep(dep) {

&#x20;   const id = dep.id;

&#x20;   // 避免重复添加依赖

&#x20;   if (!this.depIds.has(id)) {

&#x20;     this.depIds.add(id);

&#x20;     this.deps.push(dep);

&#x20;     // 让 Dep 也记住当前 Watcher

&#x20;     dep.addSub(this);

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 解析路径表达式（如 'user.name'）

&#x20; parsePath(path) {

&#x20;   const segments = path.split('.');

&#x20;   return function(obj) {

&#x20;     for (let i = 0; i < segments.length; i++) {

&#x20;       if (!obj) return;

&#x20;       obj = obj\[segments\[i]];

&#x20;     }

&#x20;     return obj;

&#x20;   };

&#x20; }

}

// 简化的异步更新队列

const queue = \[];

let has = {};

function queueWatcher(watcher) {

&#x20; const id = watcher.id;

&#x20; if (!has\[id]) {

&#x20;   has\[id] = true;

&#x20;   queue.push(watcher);

&#x20;   // 使用 setTimeout 异步执行所有更新

&#x20;   setTimeout(flushSchedulerQueue, 0);

&#x20; }

}

function flushSchedulerQueue() {

&#x20; const watchers = queue.slice(0);

&#x20; queue.length = 0;

&#x20; has = {};

&#x20; // 执行所有 Watcher 的 run 方法

&#x20; watchers.forEach(watcher => watcher.run());

}
```

#### 3. 工作流程解析



1.  **初始化阶段**：

*   Vue 实例初始化时，会调用 `observe()` 方法将 data 对象转换为响应式对象

*   对 data 中的每个属性通过 `Object.defineProperty` 定义 getter 和 setter

1.  **依赖收集阶段**：

*   组件渲染时，会创建一个 Watcher 实例，执行渲染函数（getter）

*   渲染函数访问数据时触发 getter，将当前 Watcher 记录到 Dep 中

*   建立数据 -> Dep -> Watcher 的依赖关系

1.  **数据更新阶段**：

*   当数据被修改时，触发 setter 方法

*   setter 调用 Dep 的 `notify()` 方法，通知所有依赖的 Watcher

*   Watcher 被触发后，执行 `update()` 方法，最终重新执行渲染函数更新视图

### Vue 观察者模式与发布订阅模式的核心区别



| 对比维度   | Vue 响应式系统（观察者模式）          | 发布订阅模式            |
| ------ | ------------------------- | ----------------- |
| 通信方式   | 直接通信：被观察者直接通知观察者          | 间接通信：通过事件中心中转     |
| 依赖关系   | 双向依赖：被观察者知道观察者，反之亦然       | 无直接依赖：发布者和订阅者互不知晓 |
| 核心组件   | 被观察者（数据）、观察者（Watcher）、Dep | 发布者、订阅者、事件中心      |
| 耦合程度   | 较高：数据与视图直接关联              | 较低：模块间通过事件名松耦合    |
| 事件触发方式 | 数据变化自动触发                  | 手动调用发布方法触发        |
| 适用场景   | 数据与视图的同步更新                | 跨模块、跨系统的消息传递      |
| 灵活性    | 固定对应关系，扩展需要修改依赖           | 灵活扩展，新增事件无需修改原有代码 |

### 具体差异分析



1.  **依赖关系的可见性**：

*   在 Vue 响应式系统中，数据对象（被观察者）通过 Dep 明确知道有哪些 Watcher（观察者）依赖它

*   发布订阅模式中，发布者不知道哪些订阅者存在，订阅者也不知道谁发布了事件

1.  **通信中介的存在**：

*   Vue 中的 Dep 虽然起到了收集依赖的作用，但它是被观察者的一部分，并非独立的事件中心

*   发布订阅模式必须有独立的事件中心（如 EventBus），所有通信都通过它完成

1.  **事件的粒度**：

*   Vue 响应式系统中，事件是 "数据变化"，粒度非常细，精确到具体属性

*   发布订阅模式中，事件是自定义的事件名，粒度由开发者定义，通常是业务事件

1.  **使用方式**：

*   Vue 响应式系统是自动的：开发者只需修改数据，视图更新由框架自动完成

*   发布订阅模式是手动的：需要手动调用发布方法，手动订阅事件

### Vue3 中的响应式系统变化

Vue3 改用 Proxy 实现数据劫持，替代了 Vue2 中的 Object.defineProperty，但核心依然是观察者模式：



1.  **Proxy 的优势**：

*   原生支持监听对象而非单个属性

*   能监听数组变化（无需像 Vue2 那样重写数组方法）

*   能监听新增 / 删除属性

1.  **核心流程不变**：

*   依然通过 getter 收集依赖，setter 触发更新

*   保持了数据与视图的直接依赖关系

*   与发布订阅模式的核心区别依然存在

### 总结

Vue 响应式系统是观察者模式的优秀实践，通过数据劫持实现了数据与视图的自动同步，其核心是**建立数据与使用数据的代码之间的直接依赖关系**。

与发布订阅模式相比，Vue 选择观察者模式是因为：



1.  响应式系统需要精确的依赖追踪，数据变化需要精准通知到使用它的地方

2.  直接依赖关系能提供更高的性能，避免不必要的更新

3.  自动化的依赖管理降低了开发者的心智负担

而发布订阅模式更适合解决跨模块、低耦合的通信问题，两者各有适用场景，但核心思想都是 "事件驱动"，只是在耦合程度和实现方式上有所不同。

