# Vue3 的响应式系统为何使用 Proxy 替代 Object.defineProperty？

## meta 元数据



```
{

&#x20; "id": "vue3-reactive-proxy-vs-object-defineproperty",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue3"]

}
```

## 答案 1：核心简洁的口语化回答

・Proxy 能直接监听对象整体，无需遍历每个属性，初始化性能更好

・支持检测对象属性的新增和删除，解决 Vue2 需手动调用 Vue.set 的问题

・原生支持数组索引修改和 length 变化，无需特殊处理数组方法

・可监听 Map、Set 等复杂数据结构，拓展响应式覆盖范围

・劫持的是对象本身而非属性，能拦截更多操作（如 in、delete 等）

## 答案 2：口语化扩展回答

Vue2 用 Object.defineProperty 实现响应式时，得遍历对象的每个属性逐个设置 getter/setter，要是对象层级深，递归遍历就很耗性能。而且它管不了属性新增和删除，比如给对象加个新字段，页面不会自动更新，还得手动调用 Vue.set 才行，特别麻烦。

数组也是个问题，修改数组索引或者长度的时候，Vue2 监听不到，只能重写 push、pop 这些数组方法来曲线救国，用起来总有种限制。

Vue3 换成 Proxy 后，这些问题基本都解决了。Proxy 直接代理整个对象，不用提前遍历属性，新增属性也能自动响应，数组操作也和原生一样自然。另外，Proxy 还能处理 Map、Set 这些 Vue2 搞不定的数据结构，响应式的覆盖范围更广了。

## 答案 3：技术深度解析

### 1. Vue2 响应式系统的局限性（基于 Object.defineProperty）

Vue2 的响应式实现核心代码如下：



```
// Vue2响应式核心实现

function defineReactive(obj, key, val) {

&#x20; // 递归处理嵌套对象

&#x20; observe(val);

&#x20;&#x20;

&#x20; // 定义属性的getter和setter

&#x20; Object.defineProperty(obj, key, {

&#x20;   get() {

&#x20;     // 收集依赖

&#x20;     dep.depend();

&#x20;     return val;

&#x20;   },

&#x20;   set(newVal) {

&#x20;     if (newVal === val) return;

&#x20;     val = newVal;

&#x20;     // 递归处理新值

&#x20;     observe(newVal);

&#x20;     // 触发更新

&#x20;     dep.notify();

&#x20;   }

&#x20; });

}

function observe(obj) {

&#x20; // 只处理对象和数组

&#x20; if (typeof obj !== 'object' || obj === null) return;

&#x20;&#x20;

&#x20; // 遍历对象属性，逐个定义响应式

&#x20; Object.keys(obj).forEach(key => {

&#x20;   defineReactive(obj, key, obj\[key]);

&#x20; });

}
```

这种实现存在以下固有缺陷：

#### 1.1 无法检测对象属性的新增和删除



```
const obj = { name: 'vue' };

observe(obj);

// 新增属性，不会触发更新

obj.version = '3.0';&#x20;

// 删除属性，不会触发更新

delete obj.name;
```

原因是 Object.defineProperty 只能对**已存在的属性**进行劫持，新增属性不在初始遍历范围内，因此无法自动成为响应式。Vue2 中需要通过`Vue.set`和`Vue.delete`手动处理，增加了使用成本。

#### 1.2 对数组的支持有限



```
const arr = \[1, 2, 3];

observe(arr);

// 直接修改索引，不会触发更新

arr\[0] = 100;

// 修改数组长度，不会触发更新

arr.length = 0;
```

Vue2 的解决方案是**重写数组原型方法**（如 push、pop、splice 等），但这种方式：



*   只能覆盖部分数组操作，无法处理索引和 length 修改

*   破坏了原生数组的特性，可能导致意想不到的问题

*   增加了代码复杂度和维护成本

#### 1.3 初始化性能问题

由于需要**递归遍历对象的所有属性**并逐个定义 getter/setter，对于包含大量属性的复杂对象，初始化响应式的过程会产生明显性能开销。

特别是当对象存在深层嵌套时，递归遍历的成本会显著增加。

### 2. Proxy 的优势与解决方案

Proxy 是 ES6 引入的原生对象，用于创建一个对象的代理，能够拦截并自定义对象的基本操作。Vue3 利用这些特性彻底解决了 Vue2 的响应式局限。

#### 2.1 Proxy 的基本用法



```
// 创建对象代理

const proxy = new Proxy(target, {

&#x20; // 拦截属性读取

&#x20; get(target, key, receiver) {

&#x20;   console.log(\`读取属性: \${key}\`);

&#x20;   return Reflect.get(target, key, receiver);

&#x20; },

&#x20;&#x20;

&#x20; // 拦截属性设置

&#x20; set(target, key, value, receiver) {

&#x20;   console.log(\`设置属性: \${key} = \${value}\`);

&#x20;   return Reflect.set(target, key, value, receiver);

&#x20; },

&#x20;&#x20;

&#x20; // 拦截属性删除

&#x20; deleteProperty(target, key) {

&#x20;   console.log(\`删除属性: \${key}\`);

&#x20;   return Reflect.deleteProperty(target, key);

&#x20; }

});
```

与 Object.defineProperty 相比，Proxy 的核心优势在于：



*   直接代理整个对象而非单个属性

*   拦截操作更全面（13 种拦截方法）

*   懒代理特性，无需提前遍历属性

#### 2.2 Vue3 响应式核心实现（基于 Proxy）



```
// Vue3响应式核心实现简化版

function reactive(target) {

&#x20; // 仅对对象类型进行代理（null除外）

&#x20; if (typeof target !== 'object' || target === null) {

&#x20;   return target;

&#x20; }

&#x20;&#x20;

&#x20; // 创建代理对象

&#x20; const handler = {

&#x20;   // 拦截属性读取

&#x20;   get(target, key, receiver) {

&#x20;     // 收集依赖

&#x20;     track(target, key);

&#x20;    &#x20;

&#x20;     // 获取属性值

&#x20;     const result = Reflect.get(target, key, receiver);

&#x20;    &#x20;

&#x20;     // 递归代理：只有当属性被访问时才会对其进行代理

&#x20;     // 实现懒加载，提升初始化性能

&#x20;     if (typeof result === 'object' && result !== null) {

&#x20;       return reactive(result);

&#x20;     }

&#x20;    &#x20;

&#x20;     return result;

&#x20;   },

&#x20;  &#x20;

&#x20;   // 拦截属性设置

&#x20;   set(target, key, value, receiver) {

&#x20;     // 获取旧值

&#x20;     const oldValue = Reflect.get(target, key, receiver);

&#x20;    &#x20;

&#x20;     // 如果值未变化，直接返回

&#x20;     if (oldValue === value) {

&#x20;       return true;

&#x20;     }

&#x20;    &#x20;

&#x20;     // 设置新值

&#x20;     const result = Reflect.set(target, key, value, receiver);

&#x20;    &#x20;

&#x20;     // 触发更新

&#x20;     trigger(target, key);

&#x20;    &#x20;

&#x20;     return result;

&#x20;   },

&#x20;  &#x20;

&#x20;   // 拦截属性删除

&#x20;   deleteProperty(target, key) {

&#x20;     // 检查属性是否存在

&#x20;     const hadKey = hasOwn(target, key);

&#x20;    &#x20;

&#x20;     // 删除属性

&#x20;     const result = Reflect.deleteProperty(target, key);

&#x20;    &#x20;

&#x20;     // 如果属性确实存在且删除成功，触发更新

&#x20;     if (hadKey && result) {

&#x20;       trigger(target, key);

&#x20;     }

&#x20;    &#x20;

&#x20;     return result;

&#x20;   }

&#x20; };

&#x20;&#x20;

&#x20; return new Proxy(target, handler);

}
```

#### 2.3 解决 Vue2 响应式局限的具体实现



1.  **支持属性新增和删除**



```
const obj = reactive({ name: 'vue' });

// 新增属性：会被Proxy的set拦截器捕获

obj.version = '3.0'; // 自动触发更新

// 删除属性：会被Proxy的deleteProperty拦截器捕获

delete obj.name; // 自动触发更新
```



1.  **完善的数组支持**



```
const arr = reactive(\[1, 2, 3]);

// 修改索引：被set拦截器捕获

arr\[0] = 100; // 触发更新

// 修改长度：被set拦截器捕获

arr.length = 0; // 触发更新

// 数组方法：同样会被拦截

arr.push(4); // 触发更新
```



1.  **支持复杂数据结构**



```
// 支持Map

const map = reactive(new Map());

map.set('key', 'value'); // 触发更新

map.get('key'); // 收集依赖

// 支持Set

const set = reactive(new Set());

set.add('item'); // 触发更新
```



1.  **性能优化**

*   **懒代理**：只在属性被访问时才进行递归代理，避免初始化时的全量递归

*   **无预遍历**：无需提前遍历对象所有属性，直接代理整个对象

*   **更少的内存占用**：不需要为每个属性定义 getter/setter，减少内存消耗

### 3. Proxy 的浏览器兼容性与 Vue3 的应对

Proxy 作为 ES6 特性，不支持 IE 浏览器，这也是 Vue2 坚持使用 Object.defineProperty 的重要原因。

Vue3 的应对策略：



*   放弃对 IE 的支持（IE 已停止维护）

*   对于需要兼容 IE 的项目，提供 Vue2 作为替代方案

*   利用现代浏览器对 ES6 的普遍支持，充分发挥 Proxy 优势

这种取舍使 Vue3 能够采用更先进的技术方案，同时兼顾大多数开发场景的需求。

### 4. 总结：Proxy 带来的核心改进



| 改进点          | Vue2（Object.defineProperty） | Vue3（Proxy）        |
| ------------ | --------------------------- | ------------------ |
| 属性新增         | 不支持，需手动调用 Vue.set           | 原生支持               |
| 属性删除         | 不支持，需手动调用 Vue.delete        | 原生支持               |
| 数组索引修改       | 不支持                         | 原生支持               |
| 数组 length 修改 | 不支持                         | 原生支持               |
| 复杂数据结构       | 仅支持 Object 和 Array          | 支持 Map、Set 等所有对象类型 |
| 初始化性能        | 需全量递归遍历，性能较差                | 懒代理，性能更优           |
| 拦截操作范围       | 仅能拦截 get 和 set              | 支持 13 种拦截操作        |

通过采用 Proxy，Vue3 的响应式系统实现了更全面、更自然、性能更优的响应式能力，为复杂应用开发提供了更坚实的基础。这种底层技术的升级，是 Vue3 性能提升和功能增强的重要原因之一。

