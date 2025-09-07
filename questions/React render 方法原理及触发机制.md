# 说说 React render 方法的原理？在什么时候会被触发？

## meta 元数据



```
{

&#x20; "id": "e5f6a7b8-d9c0-1234-efgh-890123456789",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・render 方法是 React 组件将虚拟 DOM 转化为 JSX 的核心函数，返回用于描述 UI 的虚拟 DOM 树

・原理是根据组件的 props 和 state 生成虚拟 DOM，再通过协调算法（Reconciliation）与真实 DOM 对比更新

・触发时机：组件初始化挂载时；组件的 props 或 state 发生变化时；父组件重新 render 时

・纯组件（PureComponent）或使用 React.memo 的组件会浅比较 props/state，减少不必要的 render

・render 本身不操作 DOM，仅负责计算 UI 描述，实际 DOM 更新由 ReactDOM 完成

## 答案 2：口语化扩展回答

React 里的 render 方法，简单说就是根据组件当前的状态（state）和接收的参数（props），生成一份描述页面结构的虚拟 DOM。它就像个画师，根据拿到的 "剧本"（数据）画出 UI 的蓝图，然后 React 再根据这个蓝图去更新真实的页面。

平时开发中，组件第一次挂载到页面上时，肯定会触发 render。之后如果组件自己的 state 变了，比如用 setState 更新数据，也会触发。还有一种情况是父组件重新渲染了，即使子组件的 props 没变化，默认情况下子组件也会跟着 render，这时候可能就需要用 React.memo 来优化。

不过 render 只是生成虚拟 DOM，不会直接操作真实 DOM，这样能提高性能，因为操作真实 DOM 开销大。React 会把新生成的虚拟 DOM 和上一次的做对比，只更新有变化的部分，这个过程叫协调。另外，如果 render 里有不纯的操作，比如直接修改 state 或者调用 setState，就会导致无限循环，这是需要避免的。

## 答案 3：技术深度解析

### React render 方法的底层原理与触发机制

#### 1. render 方法的核心原理

React 的`render`方法是组件将内部状态转化为 UI 描述的关键环节，其核心作用是生成**虚拟 DOM（Virtual DOM）**，而非直接操作真实 DOM。

##### 1.1 虚拟 DOM 的生成过程

虚拟 DOM 是对真实 DOM 的轻量级 JavaScript 对象表示，`render`方法的本质是返回这样一个对象树：



```
// 组件render返回的JSX会被编译为React.createElement调用

class MyComponent extends React.Component {

&#x20; render() {

&#x20;   // JSX语法

&#x20;   return \<div className="container">Hello, {this.props.name}\</div>;

&#x20;  &#x20;

&#x20;   // 等价于JavaScript对象（虚拟DOM）

&#x20;   return React.createElement(

&#x20;     "div",          // 标签名

&#x20;     { className: "container" },  // 属性对象

&#x20;     "Hello, ", this.props.name   // 子节点

&#x20;   );

&#x20; }

}

// 生成的虚拟DOM结构（简化版）

{

&#x20; type: "div",

&#x20; props: {

&#x20;   className: "container",

&#x20;   children: \["Hello, ", "Alice"]

&#x20; },

&#x20; key: null,

&#x20; ref: null

}
```

##### 1.2 与真实 DOM 的关联

`render`方法本身不涉及任何 DOM 操作，它仅负责计算 UI 应该是什么样子。真实 DOM 的更新由 React 的**协调算法（Reconciliation）** 和**提交阶段（Commit Phase）** 完成：



1.  **协调阶段**：对比新旧虚拟 DOM 树，找出差异（Diffing）

2.  **提交阶段**：根据差异更新真实 DOM

这个分离设计带来两大优势：



*   减少真实 DOM 操作（昂贵操作）

*   支持跨平台渲染（虚拟 DOM 与平台无关）

#### 2. render 方法的触发机制

`render`方法的触发遵循严格的生命周期规则，主要分为初始化触发和更新触发两大类。

##### 2.1 初始化触发

当组件首次挂载到 DOM 时，`render`会被触发一次：



```
// 组件挂载流程

ReactDOM.render(\<MyComponent />, document.getElementById('root'));

// 执行顺序：constructor → componentWillMount → render → componentDidMount
```

##### 2.2 更新时触发

以下情况会导致组件更新并触发`render`：



1.  **state 变化**



```
class Counter extends React.Component {

&#x20; state = { count: 0 };

&#x20;&#x20;

&#x20; handleClick = () => {

&#x20;   // 调用setState修改state，触发更新

&#x20;   this.setState({ count: this.state.count + 1 });

&#x20; };

&#x20;&#x20;

&#x20; render() {

&#x20;   return (

&#x20;     \<div>

&#x20;       \<p>Count: {this.state.count}\</p>

&#x20;       \<button onClick={this.handleClick}>Increment\</button>

&#x20;     \</div>

&#x20;   );

&#x20; }

}
```

> 注意：
>
> `setState`
>
> 是异步批量更新的，多次调用可能只触发一次
>
> `render`



1.  **props 变化**

    当父组件传递的`props`发生变化时，子组件会触发`render`：



```
// 父组件

class Parent extends React.Component {

&#x20; state = { name: "Alice" };

&#x20;&#x20;

&#x20; render() {

&#x20;   return \<Child name={this.state.name} />;

&#x20; }

}

// 子组件：当name props变化时会重新render

class Child extends React.Component {

&#x20; render() {

&#x20;   return \<div>Hello, {this.props.name}\</div>;

&#x20; }

}
```



1.  **父组件 render 触发**

    即使子组件的`props`没有变化，父组件`render`时也会默认触发子组件的`render`：



```
// 父组件render会导致子组件也render（即使props没变）

class Parent extends React.Component {

&#x20; state = { count: 0 };

&#x20;&#x20;

&#x20; render() {

&#x20;   return (

&#x20;     \<div>

&#x20;       \<Child name="固定值" /> {/\* 每次都会重新render \*/}

&#x20;     \</div>

&#x20;   );

&#x20; }

}
```



1.  **forceUpdate 强制触发**

    调用`forceUpdate`会跳过`shouldComponentUpdate`直接触发`render`：



```
class MyComponent extends React.Component {

&#x20; handleClick = () => {

&#x20;   // 强制更新，即使state和props没变

&#x20;   this.forceUpdate();

&#x20; };

&#x20;&#x20;

&#x20; render() { ... }

}
```

#### 3. 避免不必要的 render：优化机制

React 提供了多种机制来避免无效的`render`，提升性能：

##### 3.1 shouldComponentUpdate 生命周期

类组件可通过重写`shouldComponentUpdate`控制是否触发`render`：



```
class OptimizedComponent extends React.Component {

&#x20; // 自定义判断逻辑

&#x20; shouldComponentUpdate(nextProps, nextState) {

&#x20;   // 仅当name变化时才更新

&#x20;   if (this.props.name !== nextProps.name) {

&#x20;     return true; // 允许render

&#x20;   }

&#x20;   return false; // 阻止render

&#x20; }

&#x20;&#x20;

&#x20; render() { ... }

}
```

##### 3.2 PureComponent

`PureComponent`内置了浅比较逻辑，自动优化`shouldComponentUpdate`：



```
// PureComponent会浅比较props和state

class PureChild extends React.PureComponent {

&#x20; render() {

&#x20;   return \<div>{this.props.name}\</div>;

&#x20; }

}

// 使用场景：当props是简单类型或稳定的引用类型时
```

> 注意：浅比较对嵌套对象可能失效，此时需手动实现
>
> `shouldComponentUpdate`

##### 3.3 React.memo（函数组件）

`React.memo`是函数组件的性能优化方案，类似`PureComponent`：



```
// 对函数组件进行包装

const MemoizedComponent = React.memo(function MyComponent(props) {

&#x20; return \<div>{props.name}\</div>;

});

// 自定义比较函数（可选）

const MemoizedComponent = React.memo(MyComponent, (prevProps, nextProps) => {

&#x20; // 返回true表示props无变化，不触发更新

&#x20; return prevProps.name === nextProps.name;

});
```

#### 4. 底层源码解析：render 触发的工作流

以下是 React 源码中与`render`触发相关的核心流程（简化版）：



```
// React组件更新入口（简化逻辑）

function scheduleUpdateOnFiber(fiber) {

&#x20; // 1. 标记需要更新的 fiber 节点

&#x20; markUpdateLaneFromFiberToRoot(fiber);

&#x20;&#x20;

&#x20; // 2. 调度更新任务（优先级队列）

&#x20; ensureRootIsScheduled(root);

}

// 协调阶段（Reconciliation）

function performUnitOfWork(unitOfWork) {

&#x20; // 创建新的虚拟DOM（对应render方法）

&#x20; const nextChildren = workInProgress.pendingProps.children;

&#x20;&#x20;

&#x20; // 对比新旧虚拟DOM（Diff算法）

&#x20; reconcileChildren(

&#x20;   workInProgress,

&#x20;   current.child,

&#x20;   nextChildren

&#x20; );

&#x20;&#x20;

&#x20; // 继续处理下一个节点

&#x20; return workInProgress.child;

}

// 提交阶段（更新真实DOM）

function commitRoot(root) {

&#x20; const finishedWork = root.finishedWork;

&#x20;&#x20;

&#x20; // 3. 执行真实DOM操作

&#x20; commitMutationEffects(finishedWork);

&#x20;&#x20;

&#x20; // 4. 触发componentDidMount/componentDidUpdate

&#x20; commitLayoutEffects(finishedWork);

}
```

工作流程说明：



1.  当`setState`或`props`变化时，React 会标记对应组件为 "待更新"

2.  调度器根据优先级安排更新任务

3.  进入协调阶段，调用`render`生成新虚拟 DOM，对比差异

4.  提交阶段，根据差异更新真实 DOM

5.  触发后续生命周期方法（如`componentDidUpdate`）

#### 5. 常见问题与解决方案

##### 5.1 不必要的 render 导致性能问题

**现象**：组件频繁渲染，导致页面卡顿

**解决方案**：



*   使用`React.memo`/`PureComponent`减少无效更新

*   避免在`render`中创建新函数 / 对象（破坏引用相等性）



```
// 错误示例：每次render创建新函数，导致子组件更新

render() {

&#x20; return \<Child onClick={() => {}} />;

}

// 正确示例：函数引用稳定

handleClick = () => {};

render() {

&#x20; return \<Child onClick={this.handleClick} />;

}
```

##### 5.2 render 中的副作用

**问题**：在`render`中调用`setState`或 API 请求，导致无限循环

**原理**：`render`应该是纯函数，不应产生副作用

**解决方案**：将副作用移至`componentDidMount`/`useEffect`

##### 5.3 异步 setState 对 render 的影响



```
// 异步更新：多次setState合并，只触发一次render

this.setState({ count: this.state.count + 1 });

this.setState({ count: this.state.count + 1 });

// 最终count只加1，render触发一次

// 函数式更新：确保基于前一次状态计算

this.setState(prevState => ({ count: prevState.count + 1 }));

this.setState(prevState => ({ count: prevState.count + 1 }));

// 最终count加2，render触发一次
```

#### 6. 演进与未来趋势

随着 React 18 的发布，`render`机制也在不断优化：



1.  **并发渲染（Concurrent Rendering）**

    允许`render`过程被中断、暂停和恢复，优先处理高优先级任务（如用户输入）

2.  **自动批处理（Automatic Batching）**

    更智能地合并多个更新，进一步减少`render`次数：



```
// React 18中，这两个setState只会触发一次render

fetchData().then(() => {

&#x20; setCount(c => c + 1);

&#x20; setFlag(f => !f);

});
```



1.  **服务器组件（Server Components）**

    服务器端`render`生成的组件不包含状态和交互逻辑，进一步优化客户端性能

理解`render`方法的原理和触发机制，是编写高性能 React 应用的基础。合理运用 React 提供的优化手段，能有效减少不必要的渲染，提升应用响应速度。

