# Vue3 的响应式系统如何处理数组和对象的新增 / 删除属性？

## meta 元数据



```
{

&#x20; "id": "d2e3f4g5-h6i7-8901-jklm-2345678901ab",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue3"]

}
```

## 答案 1：核心简洁的口语化回答

・对象处理：通过 Proxy 拦截，新增属性直接赋值即可响应；删除属性需用 delete 运算符，会被自动追踪。

・数组处理：对数组索引赋值、修改 length 不触发响应；需用 push、pop 等数组方法，或通过 ref 包装后修改.value。

・特殊情况：对象新增属性若为嵌套对象，会自动转为响应式；数组用索引修改元素可通过 toRefs 处理。

・底层原理：依赖 Proxy 的 set 和 deleteProperty 陷阱，相比 Vue2 的 Object.defineProperty 更灵活。

## 答案 2：口语化扩展回答

Vue3 的响应式系统对对象和数组的新增、删除属性处理方式不太一样。对于对象来说，比 Vue2 方便多了，直接给对象加新属性，比如 obj.newProp = 'value'，页面就能跟着更新，不用再像 Vue2 那样用 \$set 了。删除属性的时候，直接用 delete obj.prop，也能触发响应，这是因为 Vue3 用了 Proxy，能直接监控到这些操作。

数组的情况稍微特殊点，如果直接通过索引修改数组元素，比如 arr \[0] = 1，或者改数组的 length，默认是不会触发响应的。这时候得用数组的方法，像 push、pop、splice 这些，Vue3 对这些方法做了包装，调用它们就能让页面更新。另外，如果用 ref 定义数组，修改的时候通过.value 访问，比如 arr.value \[0] = 1，也能生效。

还有个细节，对象新增的属性如果是个嵌套对象，Vue3 会自动把它也变成响应式的，不用额外处理。如果确实需要通过索引操作数组，可以先把数组转成 ref，或者用 toRefs 处理一下，这样修改索引就能触发响应了。总的来说，Vue3 的响应式系统比 Vue2 更直观，大部分场景下直接操作就行，不用记太多特殊规则。

## 答案 3：技术深度解析

### 1. 响应式系统核心原理

Vue3 的响应式系统基于**ES6 Proxy**实现，相比 Vue2 的 Object.defineProperty，能原生支持对象和数组的动态操作。其核心是通过 Proxy 创建对象的代理，拦截并追踪对象的各种操作（如属性读写、新增、删除等）。



```
// 简化的响应式创建函数

function reactive(target) {

&#x20; return new Proxy(target, {

&#x20;   // 拦截属性读取

&#x20;   get(target, key, receiver) {

&#x20;     track(target, key); // 收集依赖

&#x20;     const value = Reflect.get(target, key, receiver);

&#x20;     // 递归处理嵌套对象

&#x20;     if (isObject(value)) {

&#x20;       return reactive(value);

&#x20;     }

&#x20;     return value;

&#x20;   },

&#x20;   // 拦截属性设置

&#x20;   set(target, key, value, receiver) {

&#x20;     const oldValue = Reflect.get(target, key, receiver);

&#x20;     const result = Reflect.set(target, key, value, receiver);

&#x20;     if (oldValue !== value) {

&#x20;       trigger(target, key); // 触发更新

&#x20;     }

&#x20;     return result;

&#x20;   },

&#x20;   // 拦截属性删除

&#x20;   deleteProperty(target, key) {

&#x20;     const hadKey = hasOwn(target, key);

&#x20;     const result = Reflect.deleteProperty(target, key);

&#x20;     if (hadKey) {

&#x20;       trigger(target, key); // 触发更新

&#x20;     }

&#x20;     return result;

&#x20;   }

&#x20; });

}
```

### 2. 对象的新增与删除属性处理

#### 新增属性

Vue3 的 Proxy 可以直接拦截对象的新增属性操作，无需额外 API：



```
const obj = reactive({ name: 'Vue3' });

// 新增属性 - 自动响应

obj.version = '3.3.4'; // 触发更新

// 新增嵌套对象 - 自动转为响应式

obj.author = { name: 'Evan You' };

obj.author.age = 30; // 嵌套属性也会触发更新
```

**原理**：当新增属性时，Proxy 的 set 陷阱会被触发，执行依赖追踪和更新触发逻辑。对于嵌套对象，get 陷阱会递归将其转为响应式对象。

#### 删除属性

使用 delete 运算符删除属性时，会被 Proxy 的 deleteProperty 陷阱拦截：



```
const obj = reactive({ name: 'Vue3', version: '3.3.4' });

// 删除属性 - 自动响应

delete obj.version; // 触发更新
```

**注意**：删除不存在的属性不会触发更新，因为 deleteProperty 陷阱中会先检查属性是否存在（hadKey）。

### 3. 数组的新增与删除元素处理

#### 支持的数组操作

Vue3 对数组的以下操作提供响应式支持：



*   数组方法：push、pop、shift、unshift、splice、sort、reverse

*   通过 ref 包装的数组修改.value

*   通过 toRefs 处理后的数组索引访问



```
const arr = reactive(\['a', 'b', 'c']);

// 支持的操作

arr.push('d'); // 触发更新

arr.splice(1, 1); // 触发更新

arr.reverse(); // 触发更新
```

#### 不直接支持的操作及解决方案



1.  **通过索引修改元素**



```
const arr = reactive(\['a', 'b', 'c']);

// 不触发更新

arr\[0] = 'x';

// 解决方案1：使用splice

arr.splice(0, 1, 'x'); // 触发更新

// 解决方案2：使用ref包装

const arrRef = ref(\['a', 'b', 'c']);

arrRef.value\[0] = 'x'; // 触发更新

// 解决方案3：使用toRefs

const arrRefs = toRefs(reactive(\['a', 'b', 'c']));

arrRefs\[0].value = 'x'; // 触发更新
```



1.  **修改数组 length**



```
const arr = reactive(\['a', 'b', 'c']);

// 不触发更新

arr.length = 1;

// 解决方案：使用splice

arr.splice(1); // 触发更新，效果等同于length=1
```

#### 数组响应式的特殊处理

Vue3 对数组方法进行了包装，使其能触发响应式更新：



```
// 简化的数组方法包装逻辑

const arrayMethods = \['push', 'pop', 'shift', 'unshift', 'splice', 'sort', 'reverse'];

arrayMethods.forEach(method => {

&#x20; const original = Array.prototype\[method];

&#x20; // 重写数组方法

&#x20; Array.prototype\[method] = function(...args) {

&#x20;   const result = original.apply(this, args);

&#x20;   // 触发更新

&#x20;   trigger(this, 'length');&#x20;

&#x20;   return result;

&#x20; };

});
```

### 4. 实际开发中的最佳实践

#### 对象操作最佳实践



1.  优先直接新增 / 删除属性，无需使用额外 API



```
const user = reactive({ name: '张三' });

// 推荐

user.age = 30; // 直接新增

delete user.age; // 直接删除

// 不推荐（Vue2遗留习惯）

// this.\$set(user, 'age', 30);&#x20;

// this.\$delete(user, 'age');
```



1.  预定义可能用到的属性（如果已知）



```
// 推荐：提前定义属性，避免undefined状态

const form = reactive({

&#x20; name: '',

&#x20; // 预定义可能用到的属性

&#x20; address: {

&#x20;   city: '',

&#x20;   street: ''

&#x20; }

});
```

#### 数组操作最佳实践



1.  优先使用响应式数组方法



```
const list = reactive(\[1, 2, 3]);

// 推荐

list.push(4); // 添加元素

list.splice(0, 1); // 删除元素

list.sort((a, b) => a - b); // 排序

// 不推荐

list\[list.length] = 4; // 直接添加
```



1.  复杂数组操作使用 ref



```
// 推荐：对于需要频繁索引操作的数组，使用ref

const list = ref(\[1, 2, 3]);

// 直接通过索引修改

list.value\[0] = 100; // 触发更新

list.value.length = 2; // 触发更新
```



1.  处理大型数组的性能优化



```
// 对于大型数组，批量操作后再赋值

const bigList = ref(\[]);

// 推荐：先在非响应式数组中操作，再整体赋值

const temp = \[];

for (let i = 0; i < 1000; i++) {

&#x20; temp.push(i);

}

bigList.value = temp; // 只触发一次更新
```

### 5. 与 Vue2 响应式系统的对比



| 操作           | Vue2 (Object.defineProperty) | Vue3 (Proxy)    |
| ------------ | ---------------------------- | --------------- |
| 对象新增属性       | 需要使用 this.\$set              | 直接赋值即可          |
| 对象删除属性       | 需要使用 this.\$delete           | 直接使用 delete     |
| 数组索引修改       | 需要使用 this.\$set              | 可用 splice 或 ref |
| 数组 length 修改 | 不支持                          | 可用 splice 或 ref |
| 数组方法         | 支持（重写方法）                     | 支持（重写方法）        |
| 嵌套对象         | 需要递归监听                       | 自动递归响应式         |

Vue3 的响应式系统通过 Proxy 从根本上解决了 Vue2 中对象和数组动态操作的限制，使得开发者可以更自然地操作数据，减少了对特殊 API 的依赖，提升了开发效率和代码可读性。

### 6. 常见问题与解决方案



1.  **问题**：为什么修改数组索引有时生效有时不生效？

    **解答**：当数组被 reactive 包装时，直接修改索引不会触发更新；但如果数组被 ref 包装（通过.value 访问）或通过 toRefs 处理，则会触发更新。

2.  **问题**：对象新增的属性为什么在模板中不更新？

    **解答**：可能是因为新增属性在模板首次渲染后添加，且未被追踪。确保在组件渲染前或响应式上下文内新增属性。

3.  **问题**：如何批量修改数组而不频繁触发更新？

    **解答**：可以先创建一个临时数组进行操作，完成后整体赋值给响应式数组（适用于 ref 包装的数组）。

通过理解 Vue3 响应式系统对数组和对象的处理机制，开发者可以更灵活地运用响应式数据，避免常见的响应性丢失问题，写出更符合直觉的代码。

