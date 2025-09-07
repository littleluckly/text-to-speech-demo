# 解释 Vue3 的组合式 API（Composition API）与选项式 API（Options API）的区别及适用场景。

## meta 元数据



```
{

&#x20; "id": "vue3-composition-vs-options-api",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue3"]

}
```

## 答案 1：核心简洁的口语化回答

・组织逻辑方式不同：组合式 API 按功能组织代码，选项式 API 按 data、methods 等选项分类

・逻辑复用方式不同：组合式用自定义钩子函数复用，选项式依赖 mixins 易冲突

・代码可读性差异：组合式在复杂组件中逻辑更集中，选项式随组件变大易分散

・类型支持不同：组合式对 TypeScript 更友好，选项式类型推断较弱

・适用场景不同：组合式适合大型复杂应用，选项式适合简单组件和快速开发

## 答案 2：口语化扩展回答

组合式 API 和选项式 API 最大的区别在于代码怎么摆。选项式 API 得把数据放 data 里，方法放 methods 里，就算是相关的逻辑也得分开写，组件复杂了找起来就费劲。组合式 API 就不一样，可以把一个功能相关的变量、方法都放一起，比如表单处理的逻辑全写在一块，看起来特别清楚。

复用逻辑的时候，组合式用自定义钩子特别方便，比如把请求数据的逻辑写成一个 useFetch 函数，哪里要用直接导入就行，还能清楚知道来源。选项式用 mixins 的话，容易出现名字冲突，而且不知道哪个数据来自哪个 mixin。

简单的组件用选项式写起来更快，不用考虑怎么组织结构。但要是做大型项目，组合式 API 的优势就很明显了，多人协作时代码结构更清晰，后期维护也轻松。另外用 TypeScript 的话，组合式能获得更好的类型提示，减少错误。

## 答案 3：技术深度解析

### 1. 核心设计理念差异

选项式 API（Options API）采用**面向对象的设计思路**，将组件的功能拆分为固定的选项（如 data、methods、computed 等），强制开发者按照选项类型组织代码。

组合式 API（Composition API）则基于**函数式编程思想**，允许开发者按照业务逻辑功能组织代码，将相关的状态和方法封装在一个函数作用域中。

这种设计理念的差异直接导致了两者在代码组织方式上的根本不同。

### 2. 代码组织方式对比

#### 选项式 API 代码结构



```
\<template>

&#x20; \<div>

&#x20;   \<p>用户名: {{ username }}\</p>

&#x20;   \<p>余额: {{ balance }}\</p>

&#x20;   \<button @click="fetchUser">加载用户\</button>

&#x20;   \<button @click="recharge">充值\</button>

&#x20; \</div>

\</template>

\<script>

export default {

&#x20; // 数据选项

&#x20; data() {

&#x20;   return {

&#x20;     username: '',

&#x20;     balance: 0,

&#x20;     loading: false

&#x20;   }

&#x20; },

&#x20; // 方法选项

&#x20; methods: {

&#x20;   async fetchUser() {

&#x20;     this.loading = true;

&#x20;     const res = await fetch('/api/user');

&#x20;     const data = await res.json();

&#x20;     this.username = data.name;

&#x20;     this.balance = data.balance;

&#x20;     this.loading = false;

&#x20;   },

&#x20;   recharge() {

&#x20;     this.balance += 100;

&#x20;   }

&#x20; },

&#x20; // 生命周期选项

&#x20; mounted() {

&#x20;   this.fetchUser();

&#x20; }

}

\</script>
```

可以看到，用户相关的逻辑被拆分到 data、methods 和 mounted 三个不同的选项中，随着组件复杂度增加，这种分散会更加明显。

#### 组合式 API 代码结构



```
\<template>

&#x20; \<div>

&#x20;   \<p>用户名: {{ username }}\</p>

&#x20;   \<p>余额: {{ balance }}\</p>

&#x20;   \<button @click="fetchUser">加载用户\</button>

&#x20;   \<button @click="recharge">充值\</button>

&#x20; \</div>

\</template>

\<script setup>

import { ref, onMounted } from 'vue';

// 用户相关逻辑集中在一起

const username = ref('');

const balance = ref(0);

const loading = ref(false);

async function fetchUser() {

&#x20; loading.value = true;

&#x20; const res = await fetch('/api/user');

&#x20; const data = await res.json();

&#x20; username.value = data.name;

&#x20; balance.value = data.balance;

&#x20; loading.value = false;

}

function recharge() {

&#x20; balance.value += 100;

}

onMounted(fetchUser);

\</script>
```

用户相关的状态和方法被组织在同一个逻辑块中，形成一个内聚的功能单元，便于理解和维护。

### 3. 逻辑复用机制对比

#### 选项式 API 的逻辑复用：Mixins



```
// user-mixin.js

export default {

&#x20; data() {

&#x20;   return {

&#x20;     username: '',

&#x20;     balance: 0

&#x20;   }

&#x20; },

&#x20; methods: {

&#x20;   fetchUser() {

&#x20;     // 实现逻辑

&#x20;   }

&#x20; }

}

// 组件中使用

import userMixin from './user-mixin.js';

export default {

&#x20; mixins: \[userMixin],

&#x20; data() {

&#x20;   return {

&#x20;     // 可能与mixin中的属性冲突

&#x20;     loading: false

&#x20;   }

&#x20; }

}
```

**缺点**：



*   命名冲突风险：组件和 mixin 中可能定义同名属性或方法

*   来源不清晰：模板中使用的属性无法直接判断来自哪个 mixin

*   依赖关系模糊：mixin 之间可能存在依赖，难以维护

#### 组合式 API 的逻辑复用：自定义 Hooks



```
// useUser.js

import { ref } from 'vue';

// 封装用户相关逻辑为自定义钩子

export function useUser() {

&#x20; const username = ref('');

&#x20; const balance = ref(0);

&#x20;&#x20;

&#x20; async function fetchUser() {

&#x20;   const res = await fetch('/api/user');

&#x20;   const data = await res.json();

&#x20;   username.value = data.name;

&#x20;   balance.value = data.balance;

&#x20; }

&#x20;&#x20;

&#x20; function recharge(amount) {

&#x20;   balance.value += amount;

&#x20; }

&#x20;&#x20;

&#x20; // 返回需要暴露的状态和方法

&#x20; return {

&#x20;   username,

&#x20;   balance,

&#x20;   fetchUser,

&#x20;   recharge

&#x20; }

}

// 组件中使用

\<script setup>

import { useUser } from './useUser.js';

// 清晰获取并使用逻辑单元

const { username, balance, fetchUser, recharge } = useUser();

\</script>
```

**优点**：



*   无命名冲突：通过变量解构方式引入，可重命名避免冲突

*   来源清晰：明确知道每个属性和方法的来源

*   依赖明确：钩子函数的参数和返回值清晰，依赖关系可见

### 4. 类型支持对比

Vue3 的组合式 API 从设计之初就考虑了 TypeScript 支持，而选项式 API 由于其动态特性，类型推断存在天然困难。

#### 组合式 API 的类型支持



```
import { ref, computed } from 'vue';

// 类型明确的响应式变量

const count = ref\<number>(0);

// 计算属性自动推断类型

const doubleCount = computed(() => count.value \* 2); // 类型为number

// 函数参数类型明确

function increment(step: number) {

&#x20; count.value += step;

}
```

#### 选项式 API 的类型支持



```
import { defineComponent } from 'vue';

export default defineComponent({

&#x20; data() {

&#x20;   return {

&#x20;     count: 0 // 需要手动指定类型或通过类型推断

&#x20;   }

&#x20; },

&#x20; methods: {

&#x20;   increment(step) { // step类型需要手动指定

&#x20;     this.count += step;

&#x20;   }

&#x20; }

})
```

组合式 API 通过函数参数和返回值的类型定义，能提供更完整的类型推断和检查，减少类型相关错误。

### 5. 适用场景分析

#### 选项式 API 适用场景：



1.  **简单组件开发**：对于功能单一、逻辑简单的组件，选项式 API 的代码结构更直观，开发速度更快。

2.  **快速原型开发**：在需要快速验证想法的场景下，选项式 API 的低样板代码特性可以加速开发过程。

3.  **小型项目**：团队规模小、项目复杂度低时，选项式 API 的学习成本低、上手快的优势明显。

4.  **Vue2 迁移项目**：从 Vue2 迁移到 Vue3 的项目，可以逐步过渡，保留选项式 API 减少迁移成本。

#### 组合式 API 适用场景：



1.  **大型复杂应用**：随着组件逻辑复杂度增加，组合式 API 的代码组织优势愈发明显。

2.  **逻辑复用频繁的场景**：当多个组件需要共享逻辑时，自定义钩子提供了清晰高效的复用方式。

3.  **多人协作项目**：结构化的代码组织方式使团队成员更容易理解和维护彼此的代码。

4.  **使用 TypeScript 的项目**：组合式 API 提供的良好类型支持能充分发挥 TypeScript 的优势。

5.  **需要长期维护的项目**：组合式 API 的代码结构更有利于后期维护和功能扩展。

### 6. 实际开发中的选择策略

在实际开发中，Vue3 允许两种 API 并存，可以根据具体情况灵活选择：



*   基础 UI 组件（如按钮、表单元素）：适合使用选项式 API，简单直观

*   业务逻辑组件（如订单处理、数据可视化）：适合使用组合式 API，便于逻辑组织

*   复杂页面组件：可混合使用，核心业务逻辑用组合式，简单交互用选项式

Vue3 的设计理念是 "渐进式框架"，两种 API 的并存正是这一理念的体现，开发者可以根据项目需求和团队情况逐步采用新特性。

### 7. 性能对比

在性能方面，两种 API 的运行时性能差异极小，主要区别在于：



*   组合式 API 通过按需导入减少了打包体积

*   组合式 API 的懒加载特性可以在大型应用中优化初始加载性能

*   选项式 API 的固定结构在某些场景下可能更利于 Vue 编译器优化

总体而言，性能差异不是选择 API 风格的主要考量因素，代码可维护性和开发效率更为重要。

