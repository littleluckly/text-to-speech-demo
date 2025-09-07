# Vue 和 React 的生命周期钩子如何体现模板方法模式？请对比两者的设计差异。

## meta 元数据



```
{

&#x20; "id": "k2l3m4n5-o6p7-8901-nopq-23abcdef5678",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue", "react", "设计模式"]

}
```

## 答案 1：核心简洁的口语化回答

・两者均通过模板方法模式实现生命周期：框架定义固定执行流程（模板方法），允许开发者在特定节点（钩子）插入自定义逻辑

・Vue 的生命周期钩子（如 created、mounted）直接暴露给开发者，与框架内部流程强绑定

・React 类组件生命周期（如 componentDidMount）需重写父类方法，函数组件通过 Hooks 模拟生命周期阶段

・设计差异：Vue 钩子更直观（命名体现阶段），React 类组件钩子粒度更细（如区分 will/did 阶段）

・核心一致：框架控制执行顺序，开发者仅需关注特定阶段的逻辑实现

## 答案 2：口语化扩展回答

Vue 和 React 的生命周期钩子都是模板方法模式的典型应用。模板方法模式的核心是框架提前定义好一套流程模板，比如组件从创建到销毁的整个过程，然后在关键节点留出 "钩子"，让开发者可以插入自己的代码。

Vue 里的生命周期钩子很直接，像 created、mounted 这些，一看名字就知道是组件创建完成、挂载到 DOM 上的阶段。开发者只需要在组件里定义这些方法，Vue 会在对应的阶段自动调用，不用关心整体流程。

React 类组件的生命周期则是通过重写父类方法实现的，比如 componentDidMount，本质上是覆盖了 React.Component 里的同名方法。函数组件虽然没有类的概念，但 useEffect 也能模拟出类似的阶段，比如依赖为空数组时相当于 componentDidMount。

两者的设计思路不同，Vue 把钩子做得更简单直观，适合快速上手；React 类组件的钩子划分得更细，比如更新阶段会区分 shouldComponentUpdate、componentWillUpdate 等，给了开发者更多控制节点，但也更复杂一些。不过无论哪种，都是框架控制整体流程，开发者只需要关注特定阶段的逻辑。

## 答案 3：技术深度解析

### 模板方法模式与生命周期钩子的关联

模板方法模式是一种行为设计模式，其核心思想是**在父类中定义算法的骨架（模板方法），而将一些步骤延迟到子类中实现**。框架的生命周期钩子完美契合这一模式：



*   **框架核心流程**：对应模板方法，定义了组件从初始化到销毁的完整生命周期阶段（如初始化、挂载、更新、卸载）

*   **生命周期钩子**：对应可扩展的步骤，允许开发者在不修改框架核心逻辑的前提下，在特定阶段插入自定义代码

#### 模板方法模式的核心要素映射



| 模板方法模式要素   | 前端框架中的实现                                             |
| ---------- | ---------------------------------------------------- |
| 抽象父类       | Vue/React 的组件基类（如 Vue 的 Component、React 的 Component） |
| 模板方法       | 框架内部的生命周期调度函数（控制钩子执行顺序）                              |
| 基本方法（不可重写） | 框架内部的核心逻辑（如 DOM 渲染、diff 算法）                          |
| 钩子方法（可重写）  | 暴露给开发者的生命周期钩子（如 mounted、componentDidMount）           |

### Vue 生命周期钩子对模板方法模式的体现

Vue 的生命周期系统通过**预先定义的钩子函数**实现模板方法模式，核心特点是钩子与框架内部流程强耦合，命名直观且阶段划分明确。

#### 1. 核心生命周期流程（模板方法）

Vue 组件的完整生命周期可分为四个阶段，框架内部定义了固定的执行顺序：



```
// Vue 组件生命周期核心流程（简化版）

class Component {

&#x20; // 模板方法：定义生命周期整体流程

&#x20; lifecycle() {

&#x20;   this.initState(); // 初始化状态（框架内部逻辑）

&#x20;   this.beforeCreate(); // 钩子：创建前

&#x20;   this.initInjections(); // 注入依赖（框架内部逻辑）

&#x20;   this.created(); // 钩子：创建完成

&#x20;   if (this.\$options.el) {

&#x20;     this.mount(); // 挂载流程

&#x20;   }

&#x20; }

&#x20; // 挂载阶段子流程

&#x20; mount() {

&#x20;   this.beforeMount(); // 钩子：挂载前

&#x20;   this.renderDOM(); // 渲染DOM（框架内部逻辑）

&#x20;   this.mounted(); // 钩子：挂载完成

&#x20; }

&#x20; // 更新阶段子流程

&#x20; update() {

&#x20;   this.beforeUpdate(); // 钩子：更新前

&#x20;   this.patchDOM(); // 更新DOM（框架内部逻辑）

&#x20;   this.updated(); // 钩子：更新完成

&#x20; }

&#x20; // 卸载阶段子流程

&#x20; unmount() {

&#x20;   this.beforeUnmount(); // 钩子：卸载前

&#x20;   this.removeDOM(); // 移除DOM（框架内部逻辑）

&#x20;   this.unmounted(); // 钩子：卸载完成

&#x20; }

&#x20; // 定义钩子方法（默认空实现，由开发者重写）

&#x20; beforeCreate() {}

&#x20; created() {}

&#x20; beforeMount() {}

&#x20; mounted() {}

&#x20; beforeUpdate() {}

&#x20; updated() {}

&#x20; beforeUnmount() {}

&#x20; unmounted() {}

}
```

#### 2. 开发者使用方式

开发者通过在组件选项中定义钩子函数，实现对特定阶段的扩展：



```
\<template>

&#x20; \<div>{{ message }}\</div>

\</template>

\<script>

export default {

&#x20; data() {

&#x20;   return { message: "Hello Vue" };

&#x20; },

&#x20; // 重写钩子方法，插入自定义逻辑

&#x20; created() {

&#x20;   console.log("组件创建完成，数据已初始化");

&#x20;   this.fetchData(); // 在创建阶段发起数据请求

&#x20; },

&#x20; mounted() {

&#x20;   console.log("组件已挂载到DOM");

&#x20;   this.initEventListeners(); // 在挂载后初始化事件监听

&#x20; },

&#x20; beforeUnmount() {

&#x20;   console.log("组件即将卸载");

&#x20;   this.cleanupEventListeners(); // 在卸载前清理资源

&#x20; },

&#x20; methods: {

&#x20;   fetchData() { /\* 数据请求逻辑 \*/ },

&#x20;   initEventListeners() { /\* 初始化事件 \*/ },

&#x20;   cleanupEventListeners() { /\* 清理事件 \*/ }

&#x20; }

};

\</script>
```

### React 生命周期钩子对模板方法模式的体现

React 类组件通过**重写父类方法**实现模板方法模式，函数组件则通过 Hooks 模拟生命周期阶段，核心特点是阶段划分更细，提供更多干预节点。

#### 1. 类组件的生命周期流程（模板方法）

React 类组件的生命周期由基类 `React.Component` 定义，核心流程如下：



```
// React 类组件生命周期核心流程（简化版）

class ReactComponent {

&#x20; // 模板方法：控制生命周期执行顺序

&#x20; performUpdate() {

&#x20;   // 1. 准备更新

&#x20;   if (this.shouldComponentUpdate(this.nextProps, this.nextState)) {

&#x20;     this.componentWillUpdate(this.nextProps, this.nextState); // 钩子：更新前

&#x20;     this.updateState(); // 更新状态（框架内部逻辑）

&#x20;     this.render(); // 渲染虚拟DOM（框架内部逻辑）

&#x20;     this.componentDidUpdate(this.prevProps, this.prevState); // 钩子：更新后

&#x20;   }

&#x20; }

&#x20; // 挂载流程

&#x20; mountComponent() {

&#x20;   this.componentWillMount(); // 钩子：挂载前（已废弃）

&#x20;   this.render(); // 首次渲染（框架内部逻辑）

&#x20;   this.componentDidMount(); // 钩子：挂载后

&#x20; }

&#x20; // 卸载流程

&#x20; unmountComponent() {

&#x20;   this.componentWillUnmount(); // 钩子：卸载前

&#x20;   this.removeComponent(); // 移除组件（框架内部逻辑）

&#x20; }

&#x20; // 定义钩子方法（默认空实现）

&#x20; componentWillMount() {} // 已废弃

&#x20; componentDidMount() {}

&#x20; shouldComponentUpdate() { return true; } // 可返回布尔值控制更新

&#x20; componentWillUpdate() {} // 已废弃

&#x20; componentDidUpdate() {}

&#x20; componentWillUnmount() {}

}
```

#### 2. 开发者使用方式（类组件）



```
class MyComponent extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   this.state = { data: null };

&#x20; }

&#x20; // 重写父类钩子方法

&#x20; componentDidMount() {

&#x20;   console.log("组件已挂载");

&#x20;   this.fetchData(); // 挂载后请求数据

&#x20; }

&#x20; // 重写更新控制钩子

&#x20; shouldComponentUpdate(nextProps, nextState) {

&#x20;   // 自定义更新逻辑，优化性能

&#x20;   return nextState.data !== this.state.data;

&#x20; }

&#x20; componentDidUpdate(prevProps) {

&#x20;   console.log("组件已更新");

&#x20;   // 当props变化时重新请求数据

&#x20;   if (prevProps.id !== this.props.id) {

&#x20;     this.fetchData();

&#x20;   }

&#x20; }

&#x20; componentWillUnmount() {

&#x20;   console.log("组件即将卸载");

&#x20;   this.cancelRequest(); // 清理未完成的请求

&#x20; }

&#x20; // 自定义方法

&#x20; fetchData() { /\* 数据请求逻辑 \*/ }

&#x20; cancelRequest() { /\* 取消请求逻辑 \*/ }

&#x20; render() {

&#x20;   return \<div>{this.state.data}\</div>;

&#x20; }

}
```

#### 3. 函数组件的生命周期模拟（Hooks）

React 函数组件没有类的继承关系，但通过 `useEffect` 等 Hooks 模拟了生命周期阶段，本质上仍是模板方法模式的体现：



```
function MyFunctionComponent({ id }) {

&#x20; const \[data, setData] = React.useState(null);

&#x20; // 模拟 componentDidMount 和 componentDidUpdate（依赖变化时执行）

&#x20; React.useEffect(() => {

&#x20;   console.log("组件挂载或id变化时执行");

&#x20;   const fetchData = async () => {

&#x20;     const result = await api.fetchData(id);

&#x20;     setData(result);

&#x20;   };

&#x20;   fetchData();

&#x20;   // 模拟 componentWillUnmount（清理函数）

&#x20;   return () => {

&#x20;     console.log("组件卸载或id变化前执行");

&#x20;     // 清理逻辑（如取消请求）

&#x20;   };

&#x20; }, \[id]); // 依赖数组：控制执行时机

&#x20; // 模拟 componentDidMount（仅执行一次）

&#x20; React.useEffect(() => {

&#x20;   console.log("组件首次挂载后执行");

&#x20;   return () => {

&#x20;     console.log("组件卸载时执行");

&#x20;   };

&#x20; }, \[]); // 空依赖数组：仅在挂载和卸载时执行

&#x20; return \<div>{data}\</div>;

}
```

### Vue 与 React 生命周期设计的核心差异



| 维度     | Vue 生命周期设计                          | React 类组件生命周期设计                        |
| ------ | ----------------------------------- | -------------------------------------- |
| 继承关系   | 隐式继承（组件选项自动关联基类）                    | 显式继承（extends React.Component）          |
| 钩子命名   | 直观反映阶段（如 mounted 表示已挂载）             | 包含动作前缀（will/did，如 componentWillMount）  |
| 阶段粒度   | 中等粒度（合并相似阶段，如 created 包含数据初始化完成）    | 细粒度（拆分 will/did 阶段，如更新前 / 后）           |
| 更新控制   | 无专门钩子，需通过 watch 或计算属性控制             | 提供 shouldComponentUpdate 钩子控制是否更新      |
| 废弃策略   | 较少废弃钩子（Vue3 仅调整部分钩子命名）              | 多次废弃钩子（如 componentWillMount 因副作用问题废弃）  |
| 函数组件支持 | Options API 和 Composition API 均原生支持 | 需通过 Hooks 模拟（useEffect 等）              |
| 错误处理   | 提供 errorCaptured 钩子捕获子组件错误          | 提供 componentDidCatch 钩子捕获错误（React 16+） |

#### 关键差异点解析



1.  **继承与钩子关联方式**：

*   Vue 组件通过选项对象定义钩子，框架内部自动将其与基类方法关联，开发者无需关注继承关系

*   React 类组件必须显式继承 `React.Component` 并重写父类方法，钩子与基类方法直接绑定

1.  **更新控制机制**：

*   Vue 不提供专门的更新控制钩子，默认通过响应式系统自动判断是否更新，开发者可通过 `watch` 或 `computed` 优化

*   React 提供 `shouldComponentUpdate` 钩子，允许开发者手动控制是否执行更新，是性能优化的重要手段

1.  **函数组件适配**：

*   Vue 3 的 Composition API 中，`onMounted` 等钩子函数与 Options API 生命周期一一对应，保持设计一致性

*   React 函数组件完全抛弃类的概念，通过 `useEffect` 等 Hooks 灵活组合生命周期逻辑，更符合函数式编程思想

1.  **错误处理设计**：

*   Vue 的 `errorCaptured` 钩子主要用于捕获子组件错误，偏向于组件树内的错误处理

*   React 的 `componentDidCatch` 钩子（以及后来的 Error Boundary）更强调全局错误边界的概念，可捕获整个子树的错误

### 模板方法模式在两者设计中的共同价值

尽管存在设计差异，Vue 和 React 的生命周期钩子均通过模板方法模式实现了以下价值：



1.  **框架主导流程稳定性**：核心生命周期流程由框架控制，确保组件行为的一致性和可预测性

2.  **开发者聚焦业务逻辑**：无需关心组件初始化、渲染、更新的底层实现，只需关注特定阶段的业务需求

3.  **扩展点标准化**：提供统一的扩展接口，使组件逻辑模块化、可复用（如通过 mixins 或自定义 Hooks 封装通用生命周期逻辑）

4.  **版本迭代兼容性**：框架升级时可通过钩子适配底层变化，减少对开发者代码的影响（如 React 用 getDerivedStateFromProps 替代 componentWillReceiveProps）

### 演进趋势与最佳实践



1.  **Vue 的演进**：

*   Vue 3 保留了 Options API 的生命周期钩子，同时在 Composition API 中提供了 `onMounted` 等函数式钩子

*   调整部分钩子命名（如 `beforeUnmount` 替代 `beforeDestroy`），使语义更准确

*   增强错误处理能力，通过 `onErrorCaptured` 钩子提供更细粒度的错误捕获

1.  **React 的演进**：

*   逐步废弃可能导致副作用的生命周期（如 `componentWillMount`），推荐使用 `componentDidMount` 处理副作用

*   函数组件 + Hooks 成为主流，`useEffect` 统一了挂载、更新、卸载阶段的逻辑处理

*   引入并发渲染机制，生命周期钩子的执行时机可能被中断或重启（需注意副作用的幂等性）

1.  **最佳实践**：

*   初始化操作（如数据请求、事件监听）应放在挂载完成阶段（Vue 的 mounted、React 的 componentDidMount 或 useEffect 空依赖）

*   清理操作（如移除事件监听、取消请求）必须放在卸载前阶段，避免内存泄漏

*   性能优化：Vue 中合理使用 `watch` 的深度监听，React 中正确实现 `shouldComponentUpdate` 或使用 `React.memo`

### 总结

Vue 和 React 的生命周期钩子均是模板方法模式的经典实践：框架定义组件生命周期的整体流程（模板方法），通过钩子函数开放扩展点（可重写的步骤），使开发者能够在不修改框架核心逻辑的前提下定制组件行为。

两者的设计差异主要体现在钩子的粒度、命名方式和与框架的关联方式上：Vue 更注重直观性和简洁性，React 类组件则提供更细的控制粒度（函数组件通过 Hooks 实现更灵活的组合）。理解这些差异有助于开发者根据框架特性编写更符合最佳实践的代码，同时深入掌握模板方法模式在前端框架中的应用思想。

