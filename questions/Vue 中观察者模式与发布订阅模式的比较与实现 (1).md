# 请解释观察者模式在 Vue 响应式系统中的实现原理，与发布订阅模式的核心区别是什么？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue", "设计模式"]

}
```

## 答案 1：核心简洁的口语化回答

・Vue 响应式系统通过 Object.defineProperty 劫持数据，将数据转为响应式对象

・数据变化时，通知依赖的 Watcher（观察者）更新视图

・观察者模式是直接关联，发布订阅模式通过中间层（事件中心）解耦

・观察者模式中观察者知道被观察者，发布订阅模式中双方互不了解

・Vue 响应式核心是观察者模式，但事件系统使用发布订阅模式

## 答案 2：口语化扩展回答

Vue 的响应式系统本质上是用了观察者模式来实现数据和视图的联动。简单说，就是当你把数据传给 Vue 时，它会给这些数据加一层 "监听"，一旦数据变了，就马上告诉那些用到这些数据的地方（比如模板里的表达式），让它们更新。

这种模式在实际开发中表现就是我们不用手动操作 DOM，数据变了页面自动就跟着变。而观察者模式和发布订阅模式的主要区别在于有没有中间层。观察者模式里，观察者直接盯着被观察者，双方是知道彼此的；发布订阅模式则多了个类似 "中介" 的东西，发布者和订阅者互相不知道，都通过中介来传递消息。

在 Vue 里，响应式数据和 Watcher 之间是直接关联的观察者模式，而像 $on 和 $emit 这些事件方法，则更像是发布订阅模式，用起来更灵活，适合组件间通信这种场景。

## 答案 3：技术深度解析

### Vue 响应式系统中观察者模式的实现原理

Vue 的响应式系统核心实现依赖于三个关键角色：



1.  **Observer（被观察者）**：负责将数据对象转为响应式，劫持数据的 getter 和 setter

2.  **Watcher（观察者）**：负责收集依赖并接收数据变化通知，执行更新操作

3.  **Dep（依赖收集器）**：连接 Observer 和 Watcher 的桥梁，管理订阅关系

#### 核心实现代码解析



```
// 1. Observer 实现：将数据转为响应式

class Observer {

&#x20; constructor(value) {

&#x20;   this.value = value;

&#x20;   this.walk(value); // 遍历对象属性并转为响应式

&#x20; }

&#x20; // 遍历对象的所有属性，将它们转为响应式

&#x20; walk(obj) {

&#x20;   const keys = Object.keys(obj);

&#x20;   for (let i = 0; i < keys.length; i++) {

&#x20;     defineReactive(obj, keys\[i], obj\[keys\[i]]);

&#x20;   }

&#x20; }

}

// 核心函数：定义响应式属性

function defineReactive(obj, key, val) {

&#x20; // 递归处理嵌套对象

&#x20; if (typeof val === 'object') {

&#x20;   new Observer(val);

&#x20; }

&#x20;&#x20;

&#x20; // 创建依赖收集器，每个属性都有自己的Dep实例

&#x20; const dep = new Dep();

&#x20;&#x20;

&#x20; // 使用Object.defineProperty劫持getter和setter

&#x20; Object.defineProperty(obj, key, {

&#x20;   enumerable: true,

&#x20;   configurable: true,

&#x20;   // 当属性被访问时触发

&#x20;   get() {

&#x20;     // 收集依赖：将当前活跃的Watcher添加到依赖中

&#x20;     if (Dep.target) {

&#x20;       dep.depend(); // 建立属性与Watcher的关联

&#x20;     }

&#x20;     return val;

&#x20;   },

&#x20;   // 当属性被修改时触发

&#x20;   set(newVal) {

&#x20;     if (newVal === val) return;

&#x20;     val = newVal;

&#x20;     // 如果新值是对象，也需要转为响应式

&#x20;     if (typeof newVal === 'object') {

&#x20;       new Observer(newVal);

&#x20;     }

&#x20;     // 通知所有依赖的Watcher更新

&#x20;     dep.notify();

&#x20;   }

&#x20; });

}

// 2. Dep 实现：管理依赖关系

class Dep {

&#x20; constructor() {

&#x20;   this.subs = \[]; // 存储所有订阅该属性的Watcher

&#x20; }

&#x20;&#x20;

&#x20; // 添加订阅者

&#x20; addSub(sub) {

&#x20;   this.subs.push(sub);

&#x20; }

&#x20;&#x20;

&#x20; // 建立依赖关系

&#x20; depend() {

&#x20;   if (Dep.target) {

&#x20;     // 调用Watcher的addDep方法，双向关联

&#x20;     Dep.target.addDep(this);

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 通知所有订阅者更新

&#x20; notify() {

&#x20;   // 复制一份避免在更新过程中修改订阅列表

&#x20;   const subs = this.subs.slice();

&#x20;   for (let i = 0, l = subs.length; i < l; i++) {

&#x20;     // 调用每个Watcher的update方法

&#x20;     subs\[i].update();

&#x20;   }

&#x20; }

}

// 静态属性，用于存储当前正在处理的Watcher

Dep.target = null;

// 3. Watcher 实现：观察者

class Watcher {

&#x20; constructor(vm, expOrFn, cb) {

&#x20;   this.vm = vm;         // Vue实例

&#x20;   this.cb = cb;         // 数据变化时的回调函数

&#x20;   this.deps = \[];       // 存储该Watcher订阅的所有Dep

&#x20;   this.depIds = new Set(); // 用于去重Dep

&#x20;  &#x20;

&#x20;   // 解析表达式并编译成函数

&#x20;   this.getter = parsePath(expOrFn);

&#x20;   // 触发getter，收集依赖

&#x20;   this.value = this.get();

&#x20; }

&#x20;&#x20;

&#x20; // 执行getter，同时将当前Watcher设为活跃状态

&#x20; get() {

&#x20;   Dep.target = this;    // 将当前Watcher设置为Dep的目标

&#x20;   const value = this.getter.call(this.vm, this.vm); // 触发getter，收集依赖

&#x20;   Dep.target = null;    // 重置Dep的目标

&#x20;   return value;

&#x20; }

&#x20;&#x20;

&#x20; // 接收更新通知

&#x20; update() {

&#x20;   const oldValue = this.value;

&#x20;   this.value = this.get(); // 获取新值

&#x20;   this.cb.call(this.vm, this.value, oldValue); // 执行回调更新视图

&#x20; }

&#x20;&#x20;

&#x20; // 添加依赖

&#x20; addDep(dep) {

&#x20;   const id = dep.id;

&#x20;   // 避免重复添加依赖

&#x20;   if (!this.depIds.has(id)) {

&#x20;     this.depIds.add(id);

&#x20;     this.deps.push(dep);

&#x20;     dep.addSub(this); // 将当前Watcher添加到Dep的订阅列表

&#x20;   }

&#x20; }

}

// 辅助函数：解析表达式路径

function parsePath(path) {

&#x20; // 简单实现，实际Vue中更复杂

&#x20; const segments = path.split('.');

&#x20; return function(obj) {

&#x20;   for (let i = 0; i < segments.length; i++) {

&#x20;     if (!obj) return;

&#x20;     obj = obj\[segments\[i]];

&#x20;   }

&#x20;   return obj;

&#x20; };

}
```

#### 工作流程解析



1.  **初始化阶段**：Vue 实例初始化时，会将 data 选项中的对象通过 Observer 转为响应式对象

2.  **依赖收集阶段**：

*   当渲染模板时，会创建 Watcher 实例

*   访问数据时触发 getter，将当前 Watcher 添加到 Dep 中

*   建立数据属性与 Watcher 的关联关系

1.  **数据更新阶段**：

*   当数据被修改时触发 setter

*   Dep 通知所有订阅的 Watcher 执行 update 方法

*   Watcher 重新计算值并调用回调函数更新视图

### 观察者模式与发布订阅模式的核心区别



| 特性       | 观察者模式          | 发布订阅模式          |
| -------- | -------------- | --------------- |
| 耦合度      | 紧耦合，观察者知道被观察者  | 松耦合，双方通过事件中心通信  |
| 通信方式     | 直接通信           | 间接通信（通过事件中心）    |
| 适用场景     | 单一对象与多个依赖对象的联动 | 跨模块、跨层级的通信      |
| 实现复杂度    | 简单，无需中间层       | 较复杂，需要事件中心管理    |
| Vue 中的应用 | 响应式系统（数据与视图联动） | 事件系统（$on/$emit） |

#### 发布订阅模式的简单实现



```
// 事件中心：发布订阅模式的核心

class EventBus {

&#x20; constructor() {

&#x20;   this.events = {}; // 存储事件与订阅者的映射关系

&#x20; }

&#x20;&#x20;

&#x20; // 订阅事件

&#x20; on(eventName, callback) {

&#x20;   if (!this.events\[eventName]) {

&#x20;     this.events\[eventName] = \[];

&#x20;   }

&#x20;   this.events\[eventName].push(callback);

&#x20; }

&#x20;&#x20;

&#x20; // 发布事件

&#x20; emit(eventName, ...args) {

&#x20;   const callbacks = this.events\[eventName];

&#x20;   if (callbacks && callbacks.length) {

&#x20;     callbacks.forEach(callback => {

&#x20;       callback.apply(this, args);

&#x20;     });

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 取消订阅

&#x20; off(eventName, callback) {

&#x20;   const callbacks = this.events\[eventName];

&#x20;   if (callbacks && callbacks.length) {

&#x20;     this.events\[eventName] = callbacks.filter(cb => cb !== callback);

&#x20;   }

&#x20; }

}

// 使用示例

const bus = new EventBus();

// 订阅者1

bus.on('data-updated', (data) => {

&#x20; console.log('订阅者1收到数据更新:', data);

});

// 订阅者2

bus.on('data-updated', (data) => {

&#x20; console.log('订阅者2收到数据更新:', data);

});

// 发布者发布事件

bus.emit('data-updated', { message: '新数据' });
```

### 总结

Vue 的响应式系统采用观察者模式实现了数据与视图的自动同步，通过 Object.defineProperty 劫持数据的访问与修改，结合 Dep 进行依赖管理，最终通过 Watcher 完成视图更新。

与发布订阅模式相比，观察者模式是一种更直接的依赖关系，适合单一数据源与多个依赖项的场景；而发布订阅模式通过引入事件中心实现了完全解耦，更适合复杂系统中的跨模块通信。Vue 框架中同时应用了这两种模式，分别解决了不同的问题场景。

Vue 3 中响应式系统改为使用 Proxy 实现，但其核心的观察者模式思想保持不变，只是在劫持方式和性能上做了优化。

