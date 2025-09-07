# 说说 React 生命周期有哪些不同阶段？每个阶段对应的方法是？

## meta 元数据



```
{

&#x20; "id": "d3e4f5g6-h7i8-9012-jklm-34567890abcd",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react", "生命周期"]

}
```

## 答案 1：核心简洁的口语化回答

・初始化阶段：constructor 用于初始化状态和绑定方法。

・挂载阶段：componentWillMount（即将废弃）、render 渲染 DOM、componentDidMount 完成挂载后执行。

・更新阶段：shouldComponentUpdate 判断是否更新、componentWillUpdate（即将废弃）、render 重新渲染、componentDidUpdate 完成更新后执行。

・卸载阶段：componentWillUnmount 在组件卸载前清理资源。

・错误处理阶段：componentDidCatch 捕获子组件错误。

## 答案 2：口语化扩展回答

React 组件的生命周期就像一个事物从创建到消失的过程，分几个关键阶段。

初始化阶段主要是 constructor 方法，在这里可以给组件设置初始的 state，也能绑定事件处理函数的 this 指向，不过别在这里做数据请求之类的操作。

挂载阶段是组件第一次出现在页面上的过程。先执行 componentWillMount（现在不太推荐用了），接着是最重要的 render 方法，它负责返回要渲染的 JSX 结构，最后 componentDidMount 会在组件真正挂载到 DOM 后触发，像数据请求、订阅事件这些操作放在这里很合适，因为这时 DOM 已经准备好了。

更新阶段在组件的 props 或 state 变化时触发。shouldComponentUpdate 会先判断是否需要更新，返回 false 就能阻止不必要的渲染，提升性能。然后 componentWillUpdate（也不推荐了）和 render 先后执行，最后 componentDidUpdate 在更新完成后调用，这里可以根据前后的 props 或 state 差异做一些后续处理，比如更新 DOM。

当组件要被移除时，就到了卸载阶段，componentWillUnmount 会被调用，这里要做的是清理工作，比如取消定时器、移除事件监听，避免内存泄漏。

还有错误处理阶段，componentDidCatch 能捕获子组件抛出的错误，让父组件可以显示错误提示而不是整个崩溃。

## 答案 3：技术深度解析

### React 生命周期的阶段划分及对应方法

React 组件的生命周期是组件从创建到销毁的整个过程，不同版本的 React 对生命周期方法有一定调整，以下基于 React 16.3 + 版本（引入`getDerivedStateFromProps`和`getSnapshotBeforeUpdate`，废弃部分不安全方法）进行解析。

#### 一、初始化阶段（Initialization）

该阶段是组件实例创建的初始过程，主要在`constructor`中完成。

**核心方法：**`constructor(props)`



```
class MyComponent extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props); // 必须调用父类构造函数，否则无法使用this.props

&#x20;   // 初始化state

&#x20;   this.state = {

&#x20;     count: 0,

&#x20;     data: \[]

&#x20;   };

&#x20;   // 绑定事件处理函数的this指向

&#x20;   this.handleClick = this.handleClick.bind(this);

&#x20; }

&#x20;&#x20;

&#x20; handleClick() {

&#x20;   // 事件处理逻辑

&#x20; }

}
```

**作用**：



*   初始化组件的 state 对象。

*   为事件处理函数绑定 this 上下文。

*   不能在这里调用`setState`，也不应进行数据请求或订阅操作。

#### 二、挂载阶段（Mounting）

组件从创建到首次渲染到 DOM 中的过程，分为三个关键步骤。



1.  `static getDerivedStateFromProps(props, state)`



```
class MyComponent extends React.Component {

&#x20; static getDerivedStateFromProps(nextProps, prevState) {

&#x20;   // 根据新props更新state

&#x20;   if (nextProps.id !== prevState.id) {

&#x20;     return {

&#x20;       id: nextProps.id,

&#x20;       data: null // 重置数据，等待重新加载

&#x20;     };

&#x20;   }

&#x20;   // 不需要更新state时返回null

&#x20;   return null;

&#x20; }

}
```

**作用**：根据传入的 props 更新组件的 state，是一个静态方法，不能使用 this。适用于 state 依赖 props 变化的场景，如表单控件默认值随 props 更新。



1.  `render()`



```
class MyComponent extends React.Component {

&#x20; render() {

&#x20;   const { count } = this.state;

&#x20;   // 返回JSX元素，描述组件的UI结构

&#x20;   return (

&#x20;     \<div>

&#x20;       \<p>当前计数：{count}\</p>

&#x20;       \<button onClick={this.handleIncrement}>增加\</button>

&#x20;     \</div>

&#x20;   );

&#x20; }

}
```

**作用**：



*   是生命周期中唯一必须实现的方法。

*   返回需要渲染的 React 元素（JSX），或 null（不渲染内容）。

*   应保持纯函数特性，不修改 state，不执行副作用操作。

1.  `componentDidMount()`



```
class MyComponent extends React.Component {

&#x20; componentDidMount() {

&#x20;   // 组件挂载后执行

&#x20;   this.fetchData(); // 发起数据请求

&#x20;   this.timer = setInterval(() => {

&#x20;     this.setState({ time: new Date().toLocaleTimeString() });

&#x20;   }, 1000);

&#x20;   // 绑定DOM事件

&#x20;   this.refs.myInput.addEventListener('focus', this.handleFocus);

&#x20; }

&#x20;&#x20;

&#x20; fetchData() {

&#x20;   // 数据请求逻辑

&#x20; }

}
```

**作用**：



*   组件首次渲染到 DOM 后立即调用。

*   可执行数据请求、订阅事件、设置定时器、操作 DOM 等副作用操作。

*   可以在这里调用`setState`，会触发额外的渲染，但不会导致用户可见的闪烁。

#### 三、更新阶段（Updating）

当组件的 props 或 state 发生变化时触发，是生命周期中最复杂的阶段。



1.  `static getDerivedStateFromProps(props, state)`

与挂载阶段的该方法功能相同，在更新阶段也会被调用，用于根据新 props 更新 state。



1.  `shouldComponentUpdate(nextProps, nextState)`



```
class MyComponent extends React.Component {

&#x20; shouldComponentUpdate(nextProps, nextState) {

&#x20;   // 比较props和state，决定是否更新

&#x20;   if (nextProps.id === this.props.id && nextState.count === this.state.count) {

&#x20;     return false; // 不更新

&#x20;   }

&#x20;   return true; // 更新

&#x20; }

}
```

**作用**：



*   决定组件是否需要重新渲染，返回布尔值。

*   默认返回 true，即每次 props 或 state 变化都重新渲染。

*   通过自定义比较逻辑返回 false，可避免不必要的渲染，优化性能（类似`React.memo`的类组件实现）。

1.  `render()`

与挂载阶段功能一致，重新渲染组件 UI。



1.  `getSnapshotBeforeUpdate(prevProps, prevState)`



```
class ScrollList extends React.Component {

&#x20; getSnapshotBeforeUpdate(prevProps, prevState) {

&#x20;   // 在DOM更新前获取滚动位置快照

&#x20;   if (prevProps.items.length !== this.props.items.length) {

&#x20;     const list = this.refs.list;

&#x20;     return list.scrollHeight - list.scrollTop;

&#x20;   }

&#x20;   return null;

&#x20; }

}
```

**作用**：



*   在 DOM 更新前被调用，可获取 DOM 更新前的状态快照（如滚动位置、元素尺寸）。

*   返回值会作为第三个参数传递给`componentDidUpdate`。

*   适用于需要在 DOM 更新前后同步某些状态的场景，如保持滚动位置。

1.  `componentDidUpdate(prevProps, prevState, snapshot)`



```
class ScrollList extends React.Component {

&#x20; componentDidUpdate(prevProps, prevState, snapshot) {

&#x20;   // DOM更新后执行

&#x20;   if (snapshot !== null) {

&#x20;     // 使用快照恢复滚动位置

&#x20;     const list = this.refs.list;

&#x20;     list.scrollTop = list.scrollHeight - snapshot;

&#x20;   }

&#x20;   // 根据props变化重新请求数据

&#x20;   if (prevProps.id !== this.props.id) {

&#x20;     this.fetchData(this.props.id);

&#x20;   }

&#x20; }

}
```

**作用**：



*   组件更新完成后调用，首次渲染不会执行。

*   可根据前后 props 或 state 的差异执行相应操作（如数据请求）。

*   接收`getSnapshotBeforeUpdate`返回的快照值，用于后续处理。

*   可以在这里调用`setState`，但需注意设置条件避免无限循环。

#### 四、卸载阶段（Unmounting）

组件从 DOM 中移除并销毁的过程。

**核心方法：**`componentWillUnmount()`



```
class MyComponent extends React.Component {

&#x20; componentWillUnmount() {

&#x20;   // 清理资源

&#x20;   clearInterval(this.timer); // 清除定时器

&#x20;   this.socket.disconnect(); // 断开WebSocket连接

&#x20;   this.refs.myInput.removeEventListener('focus', this.handleFocus); // 移除事件监听

&#x20;   cancelAnimationFrame(this.animationId); // 取消动画帧

&#x20; }

}
```

**作用**：



*   组件卸载前调用，用于清理组件占用的资源。

*   必须在这里移除所有事件监听、定时器、订阅等，避免内存泄漏。

*   不能在这里调用`setState`，因为组件即将卸载，不会再重新渲染。

#### 五、错误处理阶段（Error Handling）

当子组件抛出错误时触发，用于捕获和处理错误。

**核心方法：**`componentDidCatch(error, info)`



```
class ErrorBoundary extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   this.state = { hasError: false };

&#x20; }

&#x20; componentDidCatch(error, info) {

&#x20;   // 捕获子组件错误

&#x20;   this.setState({ hasError: true });

&#x20;   // 记录错误日志

&#x20;   logErrorToService(error, info.componentStack);

&#x20; }

&#x20; render() {

&#x20;   if (this.state.hasError) {

&#x20;     // 显示错误提示UI

&#x20;     return \<h1>发生错误，请稍后再试。\</h1>;

&#x20;   }

&#x20;   // 正常渲染子组件

&#x20;   return this.props.children;

&#x20; }

}
```

**作用**：



*   捕获子组件树中抛出的 JavaScript 错误。

*   可以记录错误日志，展示友好的错误提示 UI，避免整个应用崩溃。

*   仅能捕获子组件的错误，不能捕获自身的错误。

### 生命周期方法的使用注意事项



1.  **废弃方法**：`componentWillMount`、`componentWillReceiveProps`、`componentWillUpdate`因可能导致潜在问题已被标记为不安全，建议使用`getDerivedStateFromProps`和`getSnapshotBeforeUpdate`替代。

2.  **性能优化**：合理使用`shouldComponentUpdate`或`React.PureComponent`（自动浅比较 props 和 state）减少不必要的渲染。

3.  **副作用管理**：数据请求、事件订阅等副作用应放在`componentDidMount`，清理工作放在`componentWillUnmount`，形成配对操作。

4.  **函数组件替代方案**：在函数组件中，可使用`useState`、`useEffect`等 Hooks 替代类组件的生命周期方法，`useEffect`能覆盖`componentDidMount`、`componentDidUpdate`和`componentWillUnmount`的功能。

理解 React 生命周期有助于更好地控制组件行为，优化应用性能，避免常见的内存泄漏等问题。在实际开发中，需根据具体场景选择合适的生命周期方法，并遵循最佳实践。

