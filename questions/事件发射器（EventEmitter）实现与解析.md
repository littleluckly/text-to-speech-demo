# 实现一个简易的事件发射器（EventEmitter），支持 on、off、emit 方法。

## meta 元数据



```
{

&#x20; "id": "a2b3c4d5-e6f7-8901-abcd-1234567890ab",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["javascript"]

}
```

## 答案 1：核心简洁的口语化回答

・on 方法用于注册事件监听器，将回调函数与事件名关联存储

・off 方法用于移除指定指定事件的特定回调函数，清理事件关联

・emit 方法用于触发指定事件，执行所有关联的回调函数并传递参数

・内部通过对象存储事件与回调的映射关系，键为事件名，值为回调数组

・需处理回调函数的添加、移除和批量执行逻辑

## 答案 2：口语化扩展回答

事件发射器主要用来实现事件驱动的编程模式，核心就是把函数和事件名绑定，触发时执行对应的函数。

on 方法就是注册事件，比如给 "click" 事件绑个函数，以后触发 "click" 就会执行它。实际用的时候，同一个事件可以绑多个函数，所以内部得用数组存。

off 方法是取消绑定，得找到对应的事件名，再从数组里移除特定的函数。如果移除后数组空了，最好把这个事件也删掉，省点内存。

emit 方法就是触发事件，当调用时，会把这个事件名下所有绑着的函数都执行一遍，还能传参数过去。要注意的是，触发的时候如果有人同时移除事件，得避免出问题，一般会复制一份数组再执行。

这种模式在前端很常用，比如 DOM 事件、组件通信都用类似的思路，能解耦代码，让逻辑更灵活。

## 答案 3：技术深度解析

### 实现原理

事件发射器（EventEmitter）基于发布 - 订阅模式，核心是维护一个事件与回调函数的映射关系，实现事件的注册、移除和触发功能。

### 完整实现代码



```
class EventEmitter {

&#x20; constructor() {

&#x20;   // 用对象存储事件映射，键为事件名称，值为回调函数数组

&#x20;   // 这样设计可以高效地根据事件名查找对应的回调函数

&#x20;   this.events = Object.create(null); // 使用无原型对象，避免原型链污染

&#x20; }

&#x20; /\*\*

&#x20;  \* 注册事件监听器

&#x20;  \* @param {string} eventName - 事件名称

&#x20;  \* @param {Function} callback - 回调函数

&#x20;  \*/

&#x20; on(eventName, callback) {

&#x20;   // 类型校验：确保回调是函数

&#x20;   if (typeof callback !== 'function') {

&#x20;     throw new TypeError('The callback must be a function');

&#x20;   }

&#x20;   // 如果事件不存在，初始化一个空数组

&#x20;   if (!this.events\[eventName]) {

&#x20;     this.events\[eventName] = \[];

&#x20;   }

&#x20;   // 将回调添加到事件数组中

&#x20;   this.events\[eventName].push(callback);

&#x20; }

&#x20; /\*\*

&#x20;  \* 移除事件监听器

&#x20;  \* @param {string} eventName - 事件名称

&#x20;  \* @param {Function} callback - 要移除的回调函数

&#x20;  \*/

&#x20; off(eventName, callback) {

&#x20;   // 如果事件不存在，直接返回

&#x20;   if (!this.events\[eventName]) {

&#x20;     return;

&#x20;   }

&#x20;   // 类型校验

&#x20;   if (typeof callback !== 'function') {

&#x20;     throw new TypeError('The callback must be a function');

&#x20;   }

&#x20;   // 过滤掉要移除的回调函数

&#x20;   this.events\[eventName] = this.events\[eventName].filter(

&#x20;     cb => cb !== callback

&#x20;   );

&#x20;   // 如果事件回调数组为空，删除该事件以释放内存

&#x20;   if (this.events\[eventName].length === 0) {

&#x20;     delete this.events\[eventName];

&#x20;   }

&#x20; }

&#x20; /\*\*

&#x20;  \* 触发事件

&#x20;  \* @param {string} eventName - 事件名称

&#x20;  \* @param {...any} args - 传递给回调函数的参数

&#x20;  \*/

&#x20; emit(eventName, ...args) {

&#x20;   // 如果事件不存在，直接返回

&#x20;   if (!this.events\[eventName]) {

&#x20;     return;

&#x20;   }

&#x20;   // 复制一份回调数组，防止在触发过程中修改原数组（如off操作）导致的问题

&#x20;   const callbacks = \[...this.events\[eventName]];

&#x20;   // 依次执行所有回调函数，并传递参数

&#x20;   callbacks.forEach(callback => {

&#x20;     try {

&#x20;       // 执行回调并传入参数

&#x20;       callback.apply(this, args);

&#x20;     } catch (error) {

&#x20;       // 捕获并处理回调执行中的错误，避免单个回调错误影响其他回调

&#x20;       console.error(\`Error in \${eventName} event handler:\`, error);

&#x20;     }

&#x20;   });

&#x20; }

}
```

### 关键技术点解析



1.  **数据结构设计**

*   使用`Object.create(null)`创建无原型对象，避免意外访问原型链上的属性

*   事件名作为键，回调函数数组作为值，实现 O (1) 的事件查找效率

1.  **on 方法实现**

*   增加类型校验，确保回调是函数

*   自动初始化不存在的事件，简化使用

*   支持同一事件注册多个回调函数

1.  **off 方法实现**

*   通过严格相等 (`===`) 判断回调函数，确保准确移除

*   清理空事件，优化内存占用

*   同样包含类型校验，增强健壮性

1.  **emit 方法实现**

*   使用数组复制 (`[...callbacks]`) 避免迭代中修改数组导致的问题

*   通过`apply`传递上下文和参数，保持调用的灵活性

*   增加错误捕获，防止单个回调错误中断整个事件触发流程

### 使用示例



```
// 创建事件发射器实例

const emitter = new EventEmitter();

// 注册事件

const handleMessage = (message) => {

&#x20; console.log('Received message:', message);

};

emitter.on('message', handleMessage);

emitter.on('message', (message) => {

&#x20; console.log('Another handler:', message);

});

// 触发事件

emitter.emit('message', 'Hello World');

// 输出:

// Received message: Hello World

// Another handler: Hello World

// 移除事件

emitter.off('message', handleMessage);

// 再次触发事件

emitter.emit('message', 'Hello Again');

// 输出:

// Another handler: Hello Again
```

### 扩展方向



1.  **once 方法**：支持只执行一次的事件监听

2.  **事件命名空间**：支持类似`click.button`的命名空间，方便批量管理

3.  **最大监听器限制**：防止内存泄漏

4.  **获取事件列表**：增加`eventNames()`方法查看已注册事件

这个实现保持了简洁性同时兼顾了实用性和健壮性，适合作为基础版本理解事件发射器的核心原理。

