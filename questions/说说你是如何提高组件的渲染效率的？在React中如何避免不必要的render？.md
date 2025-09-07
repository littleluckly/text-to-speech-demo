# 说说你是如何提高组件的渲染效率的？在 React 中如何避免不必要的 render？

## meta 元数据



```
{

&#x20; "id": "f9g8h7i6-j5k4-3210-lmno-0987654321fe",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react", "性能优化"]

}
```

## 答案 1：核心简洁的口语化回答

・使用 React.memo 缓存函数组件，避免 Props 未变时重渲染

・类组件用 shouldComponentUpdate 判断是否需要更新，或直接继承 PureComponent

・优化状态管理，将状态下沉到需要的组件，避免顶层状态频繁变化

・使用 useMemo 缓存计算结果、useCallback 缓存函数，防止子组件因引用变化重渲染

・列表渲染添加稳定 key，避免 DOM 节点不必要重建

## 答案 2：口语化扩展回答

在实际开发中，提高组件渲染效率主要从避免不必要的重渲染入手。首先，对于纯展示型的函数组件，用 React.memo 包裹一下很管用，它会浅比较 Props，没变就不重新渲染。类组件的话，要么自己写 shouldComponentUpdate 方法判断状态和属性变化，要么直接用 PureComponent，它内部已经实现了浅比较。

然后要注意状态的设计，别把所有状态都放顶层组件，比如一个表单组件的状态，就没必要让整个页面都跟着重新渲染。还有传递给子组件的函数，每次父组件渲染都会新建，子组件就算用了 React.memo 也会重新渲染，这时候用 useCallback 把函数缓存起来就好。如果有复杂计算，用 useMemo 缓存结果，避免每次渲染都重新计算。

另外，列表渲染时 key 很重要，别用索引当 key，数据增删时会导致 DOM 错乱和额外渲染，最好用每条数据唯一的 id。这些方法配合着用，能解决大部分渲染效率问题，特别是在列表多、组件嵌套深的页面里，效果很明显。

## 答案 3：技术深度解析

### 一、核心优化原理

React 的渲染过程分为**协调（Reconciliation）** 和**提交（Commit）** 两个阶段。优化渲染效率的核心是减少协调阶段的工作量，即避免对未发生变化的组件进行虚拟 DOM 对比。

### 二、具体实现方案

#### 1. 组件缓存机制

**（1）函数组件：React.memo**



```
// React.memo接收组件和自定义比较函数

const MemoizedComponent = React.memo(

&#x20; function MyComponent(props) {

&#x20;   // 组件逻辑

&#x20;   return \<div>{props.name}\</div>;

&#x20; },

&#x20; // 可选的自定义比较函数（返回true则不重渲染）

&#x20; (prevProps, nextProps) => {

&#x20;   // 这里可以实现深比较逻辑

&#x20;   return prevProps.name === nextProps.name;

&#x20; }

);
```

> 原理：React.memo 会缓存组件的渲染结果，当 Props 变化时才重新渲染。默认进行浅比较，复杂对象需自定义比较函数。

**（2）类组件：shouldComponentUpdate 与 PureComponent**



```
// 自定义shouldComponentUpdate

class MyComponent extends React.Component {

&#x20; shouldComponentUpdate(nextProps, nextState) {

&#x20;   // 精确控制更新条件

&#x20;   if (this.props.id !== nextProps.id) {

&#x20;     return true; // 需要更新

&#x20;   }

&#x20;   return false; // 不需要更新

&#x20; }

&#x20;&#x20;

&#x20; render() {

&#x20;   return \<div>{this.props.name}\</div>;

&#x20; }

}

// PureComponent内置浅比较

class MyPureComponent extends React.PureComponent {

&#x20; render() {

&#x20;   return \<div>{this.props.name}\</div>;

&#x20; }

}
```

> 注意：PureComponent 的浅比较可能对引用类型失效（如对象属性变化但引用不变时不会更新）

#### 2. 引用类型优化

**（1）函数缓存：useCallback**



```
function ParentComponent() {

&#x20; // 缓存函数，避免每次渲染创建新函数

&#x20; const handleClick = useCallback((id) => {

&#x20;   console.log('点击了', id);

&#x20; }, \[]); // 空依赖数组表示函数不会变化

&#x20;&#x20;

&#x20; return \<ChildComponent onClick={handleClick} />;

}
```

**（2）计算结果缓存：useMemo**



```
function DataList({ data }) {

&#x20; // 缓存计算结果，data不变则不重新计算

&#x20; const processedData = useMemo(() => {

&#x20;   return data.filter(item => item.status === 'active')

&#x20;              .sort((a, b) => b.timestamp - a.timestamp);

&#x20; }, \[data]); // 依赖data变化时才重新计算

&#x20;&#x20;

&#x20; return (

&#x20;   \<ul>

&#x20;     {processedData.map(item => (

&#x20;       \<li key={item.id}>{item.name}\</li>

&#x20;     ))}

&#x20;   \</ul>

&#x20; );

}
```

#### 3. 状态管理优化

**（1）状态局部化**



```
// 反模式：状态过于集中

function BadExample() {

&#x20; const \[user, setUser] = useState({ name: '', age: 0 });

&#x20; const \[todos, setTodos] = useState(\[]);

&#x20;&#x20;

&#x20; return (

&#x20;   \<div>

&#x20;     \<UserInfo user={user} />

&#x20;     \<TodoList todos={todos} />

&#x20;   \</div>

&#x20; );

}

// 优化：状态分散到子组件

function GoodExample() {

&#x20; return (

&#x20;   \<div>

&#x20;     \<UserInfo /> {/\* 内部管理user状态 \*/}

&#x20;     \<TodoList /> {/\* 内部管理todos状态 \*/}

&#x20;   \</div>

&#x20; );

}
```

**（2）不可变数据更新**



```
// 错误方式：直接修改原对象（不会触发重新渲染）

const updateUser = () => {

&#x20; user.age = 20;

&#x20; setUser(user);

};

// 正确方式：创建新对象

const updateUser = () => {

&#x20; setUser({

&#x20;   ...user,

&#x20;   age: 20

&#x20; });

};
```

#### 4. 列表渲染优化



```
// 反模式：使用索引作为key

todos.map((todo, index) => (

&#x20; \<TodoItem key={index} todo={todo} />

));

// 正确方式：使用唯一ID

todos.map(todo => (

&#x20; \<TodoItem key={todo.id} todo={todo} />

));
```

> 原理：稳定的 key 能帮助 React 识别哪些元素未变化，避免不必要的 DOM 重建

### 三、高级优化策略



1.  **虚拟列表**：对于长列表（1000 + 项），使用 react-window 等库只渲染可视区域内的项

2.  **代码分割**：用 React.lazy 和 Suspense 拆分组件，减少初始渲染负载

3.  **状态提升权衡**：避免过度提升状态导致的频繁更新

4.  **使用 React Profiler API**：精确测量渲染性能瓶颈



```
import { Profiler } from 'react';

function onRenderCallback(

&#x20; id, // 发生提交的 Profiler 树的 “id”

&#x20; phase, // "mount" （第一次渲染） 或 "update" （重新渲染）

&#x20; actualDuration, // 本次更新 committed 花费的时间

&#x20; baseDuration, // 估计不使用 memoization 的情况下渲染整棵子树需要的时间

&#x20; startTime, // 本次更新中 React 开始渲染的时间

&#x20; commitTime, // 本次更新中 React committed 的时间

&#x20; interactions // 本次更新参与的 interactions 的集合

) {

&#x20; // 记录性能数据

&#x20; console.log(\`组件\${id}\${phase}耗时: \${actualDuration}\`);

}

// 使用Profiler包裹需要测量的组件

\<Profiler id="TodoList" onRender={onRenderCallback}>

&#x20; \<TodoList />

\</Profiler>
```

### 四、常见误区



1.  过度优化：简单组件的重渲染性能开销很小，没必要每个组件都加缓存

2.  浅比较陷阱：对嵌套对象使用 React.memo/PureComponent 可能导致更新失效

3.  依赖项缺失：useCallback/useMemo 忘记添加必要的依赖项，导致获取旧值

通过以上策略的组合使用，可以有效减少 React 应用中的不必要渲染，提升组件性能，特别是在大型应用和复杂 UI 场景下效果显著。

