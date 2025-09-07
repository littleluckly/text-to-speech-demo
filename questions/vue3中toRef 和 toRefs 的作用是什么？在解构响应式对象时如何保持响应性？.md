# vue3 中 toRef 和 toRefs 的作用是什么？在解构响应式对象时如何保持响应性？

## meta 元数据



```
{

&#x20; "id": "c4d5e6f7-a8b9-0123-4567-89abcdef0123",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue3"]

}
```

## 答案 1：核心简洁的口语化回答

・toRef：将响应式对象的单个属性转为 ref，保持与原对象的响应式关联

・toRefs：将响应式对象的所有属性转为 ref 组成的对象，每个属性都保持响应性

・解构响应式对象时，直接解构会丢失响应性，使用 toRefs 转换后再解构可保持响应性

・转换后的 ref 属性需通过.value 访问（脚本中），模板中可直接使用

・适用于需要拆分响应式对象但仍需保持数据联动的场景

## 答案 2：口语化扩展回答

toRef 和 toRefs 都是 Vue3 里用来处理响应式对象的工具。当我们有一个用 reactive 创建的响应式对象时，如果直接拿它的属性或者解构的话，会发现这些属性失去了响应性，改了之后页面不会更新，这就很麻烦。

toRef 就是解决单个属性的问题，比如有个 user 对象，想单独把 name 属性拿出来用，又不想失去响应性，就可以用 toRef (user, 'name')，这样得到的还是个响应式的 ref。而 toRefs 更方便，能把整个对象的所有属性都转成 ref，变成一个新对象，每个属性都是 ref 类型。

在解构的时候，直接用 const {name, age} = user 肯定不行，响应性就没了。这时候先用 toRefs 把 user 转一下，再解构，const {name, age} = toRefs (user)，这样得到的 name 和 age 都是 ref，改它们的值页面也会跟着变。不过要注意，在脚本里用的时候得加.value，模板里就不用了，和普通 ref 一样。这种方式在组件传参或者拆分复杂响应式对象的时候特别有用，能保持数据的联动性。

## 答案 3：技术深度解析

### 1. toRef 和 toRefs 的核心作用

#### toRef 的作用



*   将响应式对象的单个属性转换为 ref 对象

*   保持与原响应式对象的关联，修改转换后的 ref 会同步影响原对象

*   即使原属性不存在，也能创建一个不触发警告的 ref（值为 undefined）

#### toRefs 的作用



*   批量处理响应式对象的所有可枚举属性，转换为 ref 对象

*   返回一个新对象，其属性与原响应式对象的属性一一对应且均为 ref 类型

*   保持整体结构不变的同时，让每个属性都具备 ref 的特性

### 2. 实现原理对比

#### toRef 源码解析（简化版）



```
// toRef 函数的核心实现逻辑

function toRef(object, key) {

&#x20; // 创建一个ref对象

&#x20; const refObject = {

&#x20;   // 标记为ref类型

&#x20;   \_\_v\_isRef: true,

&#x20;   // 存储原始对象和属性名，保持关联

&#x20;   \_object: object,

&#x20;   \_key: key,

&#x20;  &#x20;

&#x20;   // getter：访问.value时获取原对象的属性值

&#x20;   get value() {

&#x20;     // 从原始对象中获取属性值

&#x20;     return this.\_object\[this.\_key]

&#x20;   },

&#x20;  &#x20;

&#x20;   // setter：修改.value时同步更新原对象

&#x20;   set value(newValue) {

&#x20;     // 更新原始对象的属性值

&#x20;     this.\_object\[this.\_key] = newValue

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; return refObject

}
```

#### toRefs 源码解析（简化版）



```
// toRefs 函数的核心实现逻辑

function toRefs(object) {

&#x20; // 创建一个空对象用于存储转换后的ref属性

&#x20; const ret = {}

&#x20;&#x20;

&#x20; // 遍历原对象的所有可枚举属性

&#x20; for (const key in object) {

&#x20;   // 对每个属性调用toRef进行转换

&#x20;   ret\[key] = toRef(object, key)

&#x20; }

&#x20;&#x20;

&#x20; return ret

}
```

### 3. 解构响应式对象的问题与解决方案

#### 直接解构的问题

当我们直接解构 reactive 创建的响应式对象时，会丢失响应性：



```
import { reactive } from 'vue'

const user = reactive({

&#x20; name: '张三',

&#x20; age: 30

})

// 直接解构会丢失响应性

const { name, age } = user

// 修改不会触发界面更新

name = '李四' // 错误：普通变量赋值，不会影响原响应式对象
```

**原因**：reactive 通过 Proxy 实现响应式，直接解构会获取属性的原始值（非 Proxy 包装），导致失去响应式关联。

#### 使用 toRefs 保持响应性



```
import { reactive, toRefs } from 'vue'

const user = reactive({

&#x20; name: '张三',

&#x20; age: 30

})

// 使用toRefs转换后再解构

const { name, age } = toRefs(user)

// 正确：通过ref的.value修改，会同步更新原对象并触发界面更新

name.value = '李四'

age.value = 31
```

**原理**：toRefs 将每个属性转换为 ref，解构后得到的是 ref 对象，通过.value 修改时会触发原响应式对象的更新。

### 4. 实际应用场景

#### 场景 1：组件拆分与传参



```
\<!-- 父组件 -->

\<template>

&#x20; \<UserInfo :name="name" :age="age" />

\</template>

\<script setup>

import { reactive, toRefs } from 'vue'

import UserInfo from './UserInfo.vue'

const user = reactive({

&#x20; name: '张三',

&#x20; age: 30,

&#x20; address: '北京市'

})

// 只传递需要的属性，保持响应性

const { name, age } = toRefs(user)

\</script>
```



```
\<!-- 子组件 UserInfo.vue -->

\<script setup>

import { defineProps } from 'vue'

// 接收ref类型的props，保持响应性

const props = defineProps({

&#x20; name: String,

&#x20; age: Number

})

// 在子组件中使用时也需要通过.value访问

console.log(props.name.value) // 张三

\</script>
```

#### 场景 2：组合式函数返回响应式对象



```
// useUser.js 组合式函数

import { reactive, toRefs } from 'vue'

export function useUser() {

&#x20; const state = reactive({

&#x20;   user: null,

&#x20;   loading: false,

&#x20;   error: null

&#x20; })

&#x20;&#x20;

&#x20; // 模拟获取用户数据

&#x20; const fetchUser = async (id) => {

&#x20;   state.loading = true

&#x20;   try {

&#x20;     state.user = await api.getUser(id)

&#x20;     state.error = null

&#x20;   } catch (err) {

&#x20;     state.error = err.message

&#x20;   } finally {

&#x20;     state.loading = false

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 返回响应式属性和方法，使用toRefs保持响应性

&#x20; return {

&#x20;   ...toRefs(state),

&#x20;   fetchUser

&#x20; }

}
```



```
\<!-- 在组件中使用 -->

\<script setup>

import { useUser } from './useUser.js'

// 解构后仍保持响应性

const { user, loading, error, fetchUser } = useUser()

// 调用方法

fetchUser(1)

\</script>
```

### 5. 注意事项与最佳实践



1.  **toRefs 只对响应式对象有效**

    对普通对象使用 toRefs 不会产生响应式效果，因为没有 Proxy 支持：



```
const obj = { name: '张三' }

const refs = toRefs(obj)

// 修改不会触发任何响应式更新

refs.name.value = '李四'
```



1.  **处理可选属性**

    对于可能不存在的属性，使用 toRef 更安全：



```
const user = reactive({})

// 即使address不存在，也能安全创建ref

const addressRef = toRef(user, 'address')
```



1.  **与 ref 的配合使用**

    可以将 toRefs 与 ref 组合使用，灵活管理响应式状态：



```
import { ref, reactive, toRefs } from 'vue'

const count = ref(0)

const user = reactive({ name: '张三' })

// 组合多个响应式数据源

const state = {

&#x20; count,

&#x20; ...toRefs(user)

}
```



1.  **避免过度使用**

    并非所有场景都需要使用 toRefs，只有当需要解构响应式对象且保持响应性时才使用，否则会增加不必要的复杂性。

通过合理使用 toRef 和 toRefs，我们可以在保持响应性的同时，更灵活地操作和传递响应式数据，这在 Vue3 的组合式 API 开发模式中尤为重要。它们解决了响应式对象解构时的响应性丢失问题，让代码组织更加灵活。

