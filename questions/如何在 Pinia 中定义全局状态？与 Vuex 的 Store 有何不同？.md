# 如何在 Pinia 中定义全局状态？与 Vuex 的 Store 有何不同？

## meta 元数据



```
{

&#x20; "id": "e2f3g4h5-i6j7-8901-klmn-234567890abc",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vuex", "vue"]

}
```

## 答案 1：核心简洁的口语化回答

・Pinia 中通过 `defineStore` 定义全局状态，指定唯一 ID 和状态对象（选项式）或函数（组合式）。

・与 Vuex 相比，Pinia 无 Mutations，直接在 Actions 中修改状态；取消 Modules，以多个 Store 替代。

・Pinia 原生支持 TypeScript，无需额外类型声明；Vuex 需手动维护类型，较繁琐。

・Pinia 简化了 API，合并了 Vuex 的 State、Getters、Actions，使用更直观；Vuex 结构更严格，区分度高。

・Pinia 支持插件扩展和服务器端渲染，兼容性更好，是 Vue3 推荐的状态管理方案。

## 答案 2：口语化扩展回答

在 Pinia 里定义全局状态很直接，用 `defineStore` 函数就行，给个唯一的 ID，然后通过对象或函数的方式写状态、计算属性和方法。比如选项式写法里，state 是个返回初始状态的函数，getters 定义计算属性，actions 写修改状态的逻辑，不用像 Vuex 那样非得用 mutations 改状态，在 actions 里直接改就行，省事多了。

和 Vuex 比，差别还挺明显的。Vuex 得区分 mutations 和 actions，mutations 只能同步改状态，异步操作放 actions 里，Pinia 把这些合并了，actions 里同步异步都能写，代码更简洁。另外 Vuex 用 modules 来拆分状态，Pinia 不用，直接创建多个 store 文件，用的时候导入就行，结构更清晰。

对 TypeScript 支持方面，Pinia 天生就友好，定义状态时能自动推断类型，用的时候有完整的提示。Vuex 就麻烦点，得自己写不少类型声明，不然类型就不对。而且 Pinia 是 Vue 官方推荐的，对 Vue3 的特性支持更好，比如 Composition API，用起来更顺手。

## 答案 3：技术深度解析

### 如何在 Pinia 中定义全局状态

Pinia 定义全局状态主要通过 `defineStore` 函数，支持两种写法：选项式 API 和组合式 API，以下是具体实现：

#### 1. 选项式 API 定义



```
// stores/counterStore.ts

import { defineStore } from 'pinia'

// 第一个参数是唯一ID（必须），用于在DevTools中标识store

export const useCounterStore = defineStore('counter', {

&#x20; // 状态：返回初始状态的函数（避免服务端渲染时的单例问题）

&#x20; state: () => ({

&#x20;   count: 0,

&#x20;   user: {

&#x20;     name: 'Guest',

&#x20;     isLogin: false

&#x20;   }

&#x20; }),

&#x20; // 计算属性：基于state派生状态，具有缓存特性

&#x20; getters: {

&#x20;   // 简单 getter

&#x20;   doubleCount: (state) => state.count \* 2,

&#x20;   // 依赖其他 getter 的 getter（使用 this 访问当前store实例）

&#x20;   welcomeMessage: (state) => {

&#x20;     return state.user.isLogin&#x20;

&#x20;       ? \`Welcome \${state.user.name}!\`&#x20;

&#x20;       : 'Please login'

&#x20;   },

&#x20;   // 带参数的 getter（返回函数）

&#x20;   getUserStatus: (state) => (isLogin: boolean) => {

&#x20;     return isLogin ? 'Online' : 'Offline'

&#x20;   }

&#x20; },

&#x20; // 方法：包含同步和异步操作，用于修改状态

&#x20; actions: {

&#x20;   // 同步修改

&#x20;   increment() {

&#x20;     // 直接修改state（无需像Vuex那样通过mutation）

&#x20;     this.count++

&#x20;   },

&#x20;   // 带参数的修改

&#x20;   setCount(value: number) {

&#x20;     this.count = value

&#x20;   },

&#x20;   // 异步操作（如API请求）

&#x20;   async fetchUserInfo(userId: string) {

&#x20;     try {

&#x20;       const response = await fetch(\`/api/users/\${userId}\`)

&#x20;       const data = await response.json()

&#x20;       // 直接更新状态

&#x20;       this.user = {

&#x20;         name: data.name,

&#x20;         isLogin: true

&#x20;       }

&#x20;     } catch (error) {

&#x20;       console.error('Failed to fetch user:', error)

&#x20;     }

&#x20;   }

&#x20; }

})
```

#### 2. 组合式 API 定义



```
// stores/todoStore.ts

import { defineStore } from 'pinia'

import { ref, computed, watch } from 'vue'

export const useTodoStore = defineStore('todo', () => {

&#x20; // 状态：使用ref定义响应式变量

&#x20; const todos = ref\<string\[]>(\[])

&#x20; const isLoading = ref(false)

&#x20; // 计算属性：使用computed

&#x20; const pendingCount = computed(() => {

&#x20;   return todos.value.length

&#x20; })

&#x20; // 方法：普通函数（同步/异步均可）

&#x20; const addTodo = (text: string) => {

&#x20;   todos.value.push(text)

&#x20; }

&#x20; const removeTodo = (index: number) => {

&#x20;   todos.value.splice(index, 1)

&#x20; }

&#x20; // 异步方法

&#x20; const fetchTodos = async () => {

&#x20;   isLoading.value = true

&#x20;   try {

&#x20;     const response = await fetch('/api/todos')

&#x20;     const data = await response.json()

&#x20;     todos.value = data

&#x20;   } catch (error) {

&#x20;     console.error('Failed to fetch todos:', error)

&#x20;   } finally {

&#x20;     isLoading.value = false

&#x20;   }

&#x20; }

&#x20; // 可以使用watch监听状态变化

&#x20; watch(todos, (newTodos) => {

&#x20;   console.log('Todos updated:', newTodos)

&#x20; })

&#x20; // 必须返回需要暴露的状态、计算属性和方法

&#x20; return {

&#x20;   todos,

&#x20;   isLoading,

&#x20;   pendingCount,

&#x20;   addTodo,

&#x20;   removeTodo,

&#x20;   fetchTodos

&#x20; }

})
```

#### 3. 使用全局状态



```
\<!-- 组件中使用 -->

\<template>

&#x20; \<div>

&#x20;   \<p>Count: {{ counterStore.count }}\</p>

&#x20;   \<button @click="counterStore.increment">Increment\</button>

&#x20; \</div>

\</template>

\<script setup lang="ts">

import { useCounterStore } from '@/stores/counterStore'

// 获取store实例（全局唯一）

const counterStore = useCounterStore()

// 也可以解构（需使用storeToRefs保持响应性）

import { storeToRefs } from 'pinia'

const { count, user } = storeToRefs(counterStore)

\</script>
```

### Pinia 与 Vuex 的核心差异



| 特性                | Pinia                             | Vuex 3.x/4.x                               |
| ----------------- | --------------------------------- | ------------------------------------------ |
| **状态修改方式**        | 直接在 actions 中修改 state，无 mutations | 必须通过 mutations 修改 state（同步）                |
| **模块化设计**         | 无 modules，通过多个 store 实现模块化        | 通过 modules 拆分状态，支持嵌套 modules               |
| **TypeScript 支持** | 原生支持，自动类型推断，无需额外声明                | 需要手动定义类型，配置复杂                              |
| **API 简洁性**       | 简化的 API，合并 state/getters/actions  | 区分 state/mutations/actions/getters/modules |
| **DevTools 支持**   | 完全支持，包括时间旅行和状态跟踪                  | 支持，但 Pinia 对 Vue3 适配更好                     |
| **热模块替换**         | 支持，无需重新加载页面                       | 支持，但配置更复杂                                  |
| **插件系统**          | 更灵活的插件系统，易于扩展                     | 插件系统相对固定                                   |
| **服务端渲染**         | 原生支持，适配性更好                        | 支持，但需要额外配置                                 |

#### 1. 状态修改机制差异

**Vuex 的严格模式**：



```
// Vuex 中必须通过 mutation 修改状态

const store = new Vuex.Store({

&#x20; state: { count: 0 },

&#x20; mutations: {

&#x20;   increment(state) {

&#x20;     state.count++ // 只能在这里修改

&#x20;   }

&#x20; },

&#x20; actions: {

&#x20;   increment(context) {

&#x20;     context.commit('increment') // 必须提交mutation

&#x20;   }

&#x20; }

})
```

**Pinia 的简化模式**：



```
// Pinia 直接在 actions 中修改

const useStore = defineStore('counter', {

&#x20; state: () => ({ count: 0 }),

&#x20; actions: {

&#x20;   increment() {

&#x20;     this.count++ // 直接修改，无需mutation

&#x20;   }

&#x20; }

})
```

#### 2. 模块化实现差异

**Vuex 的 modules**：



```
// Vuex 需嵌套 modules

const userModule = {

&#x20; state: () => ({ name: 'Guest' }),

&#x20; mutations: { /\* ... \*/ }

}

const store = new Vuex.Store({

&#x20; modules: {

&#x20;   user: userModule,

&#x20;   // 支持嵌套

&#x20;   cart: {

&#x20;     namespaced: true,

&#x20;     modules: { items: { /\* ... \*/ } }

&#x20;   }

&#x20; }

})

// 使用时需指定模块路径

store.commit('user/setName', 'John')
```

**Pinia 的多 store 模式**：



```
// Pinia 直接创建多个 store 文件

// stores/user.ts

export const useUserStore = defineStore('user', { /\* ... \*/ })

// stores/cart.ts

export const useCartStore = defineStore('cart', { /\* ... \*/ })

// 使用时直接导入对应 store

import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
```

#### 3. TypeScript 支持差异

**Vuex 的类型声明（繁琐）**：



```
// Vuex 需要手动定义大量类型

import { Store } from 'vuex'

interface State {

&#x20; count: number

}

declare module '@vue/runtime-core' {

&#x20; interface ComponentCustomProperties {

&#x20;   \$store: Store\<State>

&#x20; }

}

// 还需为 mutations/actions 单独定义类型
```

**Pinia 的类型支持（自动）**：



```
// Pinia 自动推断类型

const useCounterStore = defineStore('counter', {

&#x20; state: () => ({ count: 0 }),

&#x20; actions: {

&#x20;   increment() {

&#x20;     this.count++

&#x20;   }

&#x20; }

})

// 使用时自动获得类型提示

const store = useCounterStore()

store.count // 类型：number

store.increment() // 类型：() => void
```

### 底层原理对比



1.  **响应式实现**：

*   两者均基于 Vue 的响应式系统（Vue2 用 Object.defineProperty，Vue3 用 Proxy）。

*   Pinia 对 Vue3 的 Proxy 支持更彻底，状态更新性能略优于 Vuex。

1.  **Store 实例管理**：

*   Pinia 通过 `defineStore` 创建的 store 是单例模式，多次调用返回同一实例。

*   Vuex 通过 `new Store()` 创建单一实例，所有模块共享该实例。

1.  **依赖注入**：

*   两者均通过 Vue 的 provide/inject 机制在组件树中共享 store 实例。

*   Pinia 简化了注入过程，无需在根组件显式挂载。

### 选型建议



*   新项目（尤其是 Vue3 + TypeScript）：优先选择 **Pinia**，API 简洁，类型友好，官方推荐。

*   维护 Vue2 项目：继续使用 **Vuex 3.x**，无需迁移。

*   需兼容 Vue2 和 Vue3 的项目：可考虑 **Pinia**（支持 Vue2），减少技术栈切换成本。

*   复杂的嵌套模块场景：Pinia 的多 store 模式比 Vuex 的嵌套 modules 更易维护。

Pinia 可以看作是 Vuex 的下一代演进，解决了 Vuex 中的诸多痛点，同时保持了轻量和灵活的特性，已成为 Vue 生态中状态管理的首选方案。

