# 说说对 React 中类组件和函数组件的理解？有什么区别？

## meta 元数据



```
{

&#x20; "id": "f5g6h7i8-j9k0-1234-lmno-567890abcdef",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・类组件是基于 ES6 类语法创建的组件，需要继承 React.Component，通过 this 访问 props 和 state。

・函数组件是用 JavaScript 函数定义的组件，接收 props 作为参数，返回 React 元素。

・类组件有完整的生命周期方法，函数组件需借助 Hooks 实现类似功能。

・类组件通过 this.setState 更新状态，函数组件用 useState 等 Hooks 管理状态。

・函数组件更简洁，性能更好，是 React 推荐的编写方式。

## 答案 2：口语化扩展回答

类组件和函数组件是 React 中两种定义组件的方式，各有特点。

类组件就像一个完整的 “对象”，需要用 class 关键字定义，还要继承 React.Component。它里面有 constructor 构造函数来初始化状态，用 this.state 存数据，更新状态得用 this.setState 方法。生命周期方法比如 componentDidMount、componentDidUpdate 这些也都直接写在类里面，方便在组件不同阶段做处理，比如数据请求、清理工作等。不过写起来代码量多一点，还要注意 this 的指向问题，经常需要绑定 this，不然容易出 bug。

函数组件就简单多了，就是一个普通的 JavaScript 函数，接收 props 参数，直接返回要渲染的内容。早期的函数组件只能做简单的展示，没法管理状态和使用生命周期，被叫做 “无状态组件”。但自从 React 推出 Hooks 后，函数组件也能通过 useState 管理状态，用 useEffect 处理副作用，完全能替代类组件的功能。而且它的代码更简洁，读起来一目了然，不用处理复杂的 this 问题，现在开发中基本都优先用函数组件了。

总的来说，函数组件更符合 React 的声明式编程思想，写法简单，还能通过 Hooks 灵活组合逻辑，而类组件虽然功能齐全，但相对繁琐，现在逐渐被函数组件取代。

## 答案 3：技术深度解析

### 类组件与函数组件的本质理解

#### 类组件（Class Components）

类组件是基于 ES6 类语法实现的组件，通过继承`React.Component`或`React.PureComponent`创建，具有面向对象的特性。它本质上是一个包含特定方法（如生命周期方法）的类实例，通过`this`关键字访问组件的属性和状态。



```
// 类组件基本结构

class ClassComponent extends React.Component {

&#x20; // 构造函数，初始化state和绑定方法

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   this.state = { count: 0 };

&#x20;   this.handleClick = this.handleClick.bind(this);

&#x20; }

&#x20; // 自定义方法

&#x20; handleClick() {

&#x20;   this.setState({ count: this.state.count + 1 });

&#x20; }

&#x20; // 生命周期方法

&#x20; componentDidMount() {

&#x20;   console.log('组件挂载完成');

&#x20; }

&#x20; // 渲染方法，返回React元素

&#x20; render() {

&#x20;   return (

&#x20;     \<div>

&#x20;       \<p>计数：{this.state.count}\</p>

&#x20;       \<button onClick={this.handleClick}>增加\</button>

&#x20;     \</div>

&#x20;   );

&#x20; }

}
```

#### 函数组件（Function Components）

函数组件是接收`props`作为参数并返回 React 元素的 JavaScript 函数。在 React 16.8 引入 Hooks 之前，函数组件仅能作为无状态组件使用；Hooks 出现后，函数组件拥有了状态管理和副作用处理能力，功能上可与类组件完全对等。



```
// 函数组件基本结构（使用Hooks）

function FunctionComponent(props) {

&#x20; // 使用useState管理状态

&#x20; const \[count, setCount] = React.useState(0);

&#x20; // 使用useEffect处理副作用（替代生命周期）

&#x20; React.useEffect(() => {

&#x20;   console.log('组件挂载完成');

&#x20;   return () => {

&#x20;     console.log('组件卸载前清理');

&#x20;   };

&#x20; }, \[]);

&#x20; // 自定义方法（无需绑定this）

&#x20; const handleClick = () => {

&#x20;   setCount(count + 1);

&#x20; };

&#x20; // 直接返回React元素

&#x20; return (

&#x20;   \<div>

&#x20;     \<p>计数：{count}\</p>

&#x20;     \<button onClick={handleClick}>增加\</button>

&#x20;   \</div>

&#x20; );

}
```

### 核心技术区别

#### 1. 定义与结构



| 特性      | 类组件                            | 函数组件               |
| ------- | ------------------------------ | ------------------ |
| 定义方式    | 基于 class 语法，继承 React.Component | 基于函数定义，接收 props 参数 |
| 渲染入口    | 必须实现 render () 方法              | 函数返回值即为渲染内容        |
| 代码量     | 结构繁琐，代码量多                      | 简洁紧凑，代码量少          |
| this 指向 | 存在 this，需处理绑定问题                | 无 this，避免上下文混淆     |

#### 2. 状态管理

**类组件状态管理**：



*   通过`this.state`存储状态，`this.setState`更新状态

*   `setState`是异步操作，可接收函数参数确保基于最新状态更新

*   状态对象通常是一个复杂对象，更新时需注意浅拷贝



```
// 类组件状态更新

this.setState({ count: this.state.count + 1 });

// 函数式更新（推荐，避免状态依赖问题）

this.setState(prevState => ({

&#x20; count: prevState.count + 1

}));
```

**函数组件状态管理**：



*   通过`useState` Hook 管理状态，返回`[state, setState]`数组

*   每个状态变量独立管理，无需合并对象

*   更新函数同样支持函数式更新，语义更清晰



```
// 函数组件状态更新

const \[count, setCount] = useState(0);

setCount(count + 1);

// 函数式更新

setCount(prev => prev + 1);
```

#### 3. 生命周期与副作用

**类组件生命周期**：



*   拥有完整的生命周期方法，如`componentDidMount`、`componentDidUpdate`、`componentWillUnmount`等

*   生命周期方法分散在类的不同方法中，逻辑关联性弱



```
// 类组件生命周期示例

componentDidMount() {

&#x20; // 组件挂载后执行（如数据请求）

&#x20; this.timer = setInterval(() => {}, 1000);

}

componentWillUnmount() {

&#x20; // 组件卸载前清理（如清除定时器）

&#x20; clearInterval(this.timer);

}
```

**函数组件副作用处理**：



*   通过`useEffect` Hook 统一处理副作用，替代类组件的多个生命周期方法

*   一个`useEffect`可对应类组件中`componentDidMount`、`componentDidUpdate`和`componentWillUnmount`的组合功能

*   可使用多个`useEffect`按逻辑拆分副作用，提高代码组织性



```
// 函数组件副作用示例（替代生命周期）

useEffect(() => {

&#x20; // 组件挂载后执行（对应componentDidMount）

&#x20; const timer = setInterval(() => {}, 1000);

&#x20;&#x20;

&#x20; // 组件更新或卸载前执行（对应componentWillUnmount）

&#x20; return () => {

&#x20;   clearInterval(timer);

&#x20; };

}, \[]); // 空依赖数组表示仅在挂载和卸载时执行
```

#### 4. 性能优化

**类组件性能优化**：



*   继承`React.PureComponent`实现浅比较，避免不必要的重渲染

*   重写`shouldComponentUpdate`方法实现自定义比较逻辑



```
// 类组件性能优化

class OptimizedClassComponent extends React.PureComponent {

&#x20; // PureComponent自动实现浅比较的shouldComponentUpdate

&#x20; render() {

&#x20;   return \<div>{this.props.value}\</div>;

&#x20; }

}
```

**函数组件性能优化**：



*   使用`React.memo`包装组件，实现类似`PureComponent`的浅比较

*   使用`useMemo`缓存计算结果，`useCallback`缓存函数引用，避免子组件不必要的重渲染



```
// 函数组件性能优化

const OptimizedFunctionComponent = React.memo(({ value }) => {

&#x20; return \<div>{value}\</div>;

});

// 使用useMemo缓存计算结果

const expensiveValue = useMemo(() => computeExpensiveValue(a, b), \[a, b]);
```

#### 5. 逻辑复用

**类组件逻辑复用**：



*   主要通过高阶组件（HOC）和 render props 模式实现

*   容易产生 “嵌套地狱”，代码结构复杂



```
// 类组件高阶组件示例

function withLogger(WrappedComponent) {

&#x20; return class extends React.Component {

&#x20;   componentDidMount() {

&#x20;     console.log('组件挂载');

&#x20;   }

&#x20;   render() {

&#x20;     return \<WrappedComponent {...this.props} />;

&#x20;   }

&#x20; };

}

// 使用高阶组件

class MyComponent extends React.Component { /\* ... \*/ }

const MyComponentWithLogger = withLogger(MyComponent);
```

**函数组件逻辑复用**：



*   通过自定义 Hooks 实现逻辑复用，代码更简洁

*   避免嵌套，逻辑组合更灵活



```
// 函数组件自定义Hook示例

function useLogger() {

&#x20; useEffect(() => {

&#x20;   console.log('组件挂载');

&#x20;   return () => console.log('组件卸载');

&#x20; }, \[]);

}

// 使用自定义Hook

function MyComponent() {

&#x20; useLogger(); // 直接调用Hook复用逻辑

&#x20; return \<div>...\</div>;

}
```

### 适用场景分析

#### 类组件适用场景：



*   维护老旧项目，已有大量类组件代码

*   需要使用某些仅类组件支持的特性（如`getSnapshotBeforeUpdate`的特定用法）

*   团队更熟悉面向对象编程范式

#### 函数组件适用场景：



*   新开发的项目，推荐优先使用

*   需要复用复杂逻辑的场景（通过自定义 Hooks）

*   追求代码简洁性和可读性的场景

*   性能要求较高的应用（函数组件内存占用更低，更新性能更好）

### 最佳实践与迁移策略



1.  **优先使用函数组件**：React 官方推荐使用函数组件和 Hooks，它们更符合 React 的设计理念，代码更简洁可维护。

2.  **类组件迁移步骤**：

*   用函数组件替换类组件结构

*   用`useState`替换`this.state`和`this.setState`

*   用`useEffect`替换生命周期方法

*   用`useCallback`和`useMemo`优化性能

*   用自定义 Hooks 提取复用逻辑

1.  **避免混合使用**：在同一组件中避免混合类组件和函数组件的思维模式，保持代码风格一致。

2.  **注意 Hooks 规则**：函数组件中使用 Hooks 需遵循调用规则（只在顶层调用、只在函数组件或自定义 Hooks 中调用）。

### 总结

类组件和函数组件的核心区别在于编程范式：类组件基于面向对象思想，通过继承和生命周期方法管理组件；函数组件基于函数式编程思想，通过 Hooks 实现状态管理和副作用处理。

随着 React 的发展，函数组件已成为主流，它在代码简洁性、逻辑复用、性能优化等方面都具有优势。虽然类组件并未被废弃，但在新开发中应优先选择函数组件，充分利用 Hooks 带来的便利。

理解两种组件类型的区别，不仅有助于在实际开发中做出合适选择，更能深入把握 React 从面向对象到函数式编程的演进思路，提升对 React 核心思想的理解。

