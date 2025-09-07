# ref 和 reactive reactive 的区别是什么？如何在模板中访问它们的值？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue3"]

}
```

## 答案 1：核心简洁的口语化回答

・数据类型：ref 用于基本类型和对象，reactive 仅用于对象

・响应式原理：ref 通过 .value 包装，reactive 通过 Proxy 实现

・访问方式：ref 在模板中直接用变量名，reactive 直接访问属性

・转换行为：ref 对象会被自动解包，reactive 不支持基本类型

・适用场景：ref 适合简单值和独立状态，reactive 适合复杂对象结构

## 答案 2：口语化扩展回答

ref 和 reactive 都是 Vue 中实现响应式的方法，但用法不太一样。ref 比较灵活，不管是数字、字符串这些基本类型，还是对象数组都能处理，不过在代码里访问时得加上 .value。而 reactive 只能处理对象类型，如果传基本类型会无效。

在模板里用的时候，ref 定义的变量可以直接用，不用加 .value，Vue 会自动处理。reactive 定义的对象，直接用对象。属性的方式访问就行。

实际开发中，如果是简单的状态，比如一个计数器，用 ref 更方便。如果是比较复杂的数据结构，像用户信息这种包含多个字段的对象，用 reactive 会更合适，代码看起来更整洁。不过要注意，reactive 不能直接赋值整个对象，否则会失去响应性，这点不如 ref 直观。

## 答案 3：技术深度解析

### 1. 实现原理对比

#### ref 实现原理

ref 内部通过一个包装对象实现响应式，核心源码逻辑如下：



```
// ref 函数的简化实现

function ref(value) {

&#x20; // 创建一个包含 value 属性的对象

&#x20; const refObject = {

&#x20;   // 用 \_\_v\_isRef 标记这是一个 ref 对象，供 Vue 内部识别

&#x20;   \_\_v\_isRef: true,

&#x20;  &#x20;

&#x20;   // getter 函数，访问 .value 时触发

&#x20;   get value() {

&#x20;     // 收集依赖，当 value 被访问时，记录当前的副作用函数

&#x20;     track(refObject, 'get', 'value')

&#x20;     return value

&#x20;   },

&#x20;  &#x20;

&#x20;   // setter 函数，修改 .value 时触发

&#x20;   set value(newValue) {

&#x20;     value = newValue

&#x20;     // 触发更新，通知所有依赖该 ref 的副作用函数重新执行

&#x20;     trigger(refObject, 'set', 'value', newValue)

&#x20;   }

&#x20; }

&#x20; return refObject

}
```

#### reactive 实现原理

reactive 通过 ES6 的 Proxy 实现响应式，核心源码逻辑如下：



```
// reactive 函数的简化实现

function reactive(target) {

&#x20; // 创建 Proxy 对象，拦截目标对象的操作

&#x20; return new Proxy(target, {

&#x20;   // 拦截属性访问

&#x20;   get(target, key, receiver) {

&#x20;     const result = Reflect.get(target, key, receiver)

&#x20;     // 收集依赖

&#x20;     track(target, 'get', key)

&#x20;     // 如果属性值是对象，递归将其转为 reactive 对象

&#x20;     if (isObject(result)) {

&#x20;       return reactive(result)

&#x20;     }

&#x20;     return result

&#x20;   },

&#x20;  &#x20;

&#x20;   // 拦截属性设置

&#x20;   set(target, key, value, receiver) {

&#x20;     const oldValue = Reflect.get(target, key, receiver)

&#x20;     const result = Reflect.set(target, key, value, receiver)

&#x20;     // 只有当值发生变化时才触发更新

&#x20;     if (oldValue !== value) {

&#x20;       // 触发更新

&#x20;       trigger(target, 'set', key, value, oldValue)

&#x20;     }

&#x20;     return result

&#x20;   },

&#x20;  &#x20;

&#x20;   // 拦截属性删除

&#x20;   deleteProperty(target, key) {

&#x20;     const hadKey = hasOwn(target, key)

&#x20;     const result = Reflect.deleteProperty(target, key)

&#x20;     // 如果确实删除了属性，触发更新

&#x20;     if (hadKey && result) {

&#x20;       trigger(target, 'delete', key)

&#x20;     }

&#x20;     return result

&#x20;   }

&#x20; })

}
```

### 2. 关键区别对比



| 特性      | ref                   | reactive     |
| ------- | --------------------- | ------------ |
| 支持类型    | 基本类型、对象、数组            | 仅对象、数组       |
| 访问方式    | 需要通过 .value (脚本中)     | 直接访问属性       |
| 模板访问    | 自动解包，无需 .value        | 直接访问属性       |
| 重新赋值    | 可以直接赋值 (.value = ...) | 不能直接替换整个对象   |
| 响应式丢失风险 | 低                     | 高（直接赋值整个对象时） |
| 适用场景    | 简单值、独立状态              | 复杂对象结构       |

### 3. 模板访问方式详解

#### ref 在模板中的访问

当在模板中使用 ref 定义的响应式变量时，Vue 会自动解包，无需使用 .value：



```
\<template>

&#x20; \<div>

&#x20;   \<!-- 直接使用变量名，无需 .value -->

&#x20;   \<p>{{ count }}\</p>

&#x20;   \<button @click="count++">增加\</button>

&#x20; \</div>

\</template>

\<script setup>

import { ref } from 'vue'

// 定义 ref 响应式变量

const count = ref(0)

\</script>
```

#### reactive 在模板中的访问

reactive 定义的响应式对象在模板中直接访问其属性：



```
\<template>

&#x20; \<div>

&#x20;   \<!-- 直接访问对象属性 -->

&#x20;   \<p>{{ user.name }}\</p>

&#x20;   \<p>{{ user.age }}\</p>

&#x20;   \<button @click="user.age++">增加年龄\</button>

&#x20; \</div>

\</template>

\<script setup>

import { reactive } from 'vue'

// 定义 reactive 响应式对象

const user = reactive({

&#x20; name: '张三',

&#x20; age: 30

})

\</script>
```

### 4. 特殊情况处理

#### ref 对象的解包规则

当 ref 作为 reactive 对象的属性时，会自动解包：



```
const count = ref(0)

const obj = reactive({ count })

// 无需 .value 即可访问

console.log(obj.count) // 0

// 修改时也无需 .value

obj.count = 1

console.log(count.value) // 1
```

#### 避免 reactive 响应式丢失

直接替换 reactive 对象会导致响应式丢失：



```
const user = reactive({ name: '张三' })

// 错误做法：这样会丢失响应性

user = { name: '李四' }

// 正确做法：修改属性而不是替换整个对象

user.name = '李四'

// 或者使用 Object.assign

Object.assign(user, { name: '李四' })
```

### 5. 最佳实践建议



1.  **基本类型数据**：优先使用 ref（如数字、字符串、布尔值）

2.  **对象 / 数组**：

*   简单对象且需要频繁整体替换时，使用 ref

*   复杂对象且主要修改属性时，使用 reactive

1.  **组合使用**：在大型应用中，可以组合使用两者



```
const form = reactive({

&#x20; name: ref(''),

&#x20; age: ref(0),

&#x20; address: reactive({

&#x20;   city: '',

&#x20;   street: ''

&#x20; })

})
```



1.  **使用 toRefs 转换**：当需要解构 reactive 对象时，使用 toRefs 保持响应性



```
import { reactive, toRefs } from 'vue'

const user = reactive({

&#x20; name: '张三',

&#x20; age: 30

})

// 解构后仍保持响应性

const { name, age } = toRefs(user)
```

通过理解这些核心差异和使用场景，可以在 Vue 项目中更有效地使用 ref 和 reactive，构建可靠的响应式系统。

