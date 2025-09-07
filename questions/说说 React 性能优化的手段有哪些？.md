# 说说 React 性能优化的手段有哪些？

## meta 元数据



```
{

&#x20; "id": "e1f2g3h4-i5j6-7890-klmn-1234567890op",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react", "性能优化"]

}
```

## 答案 1：核心简洁的口语化回答

・减少不必要渲染：用 React.memo、PureComponent 缓存组件，useMemo/useCallback 缓存数据和函数

・优化状态管理：将状态下沉到需要的组件，避免冗余状态和频繁更新

・列表优化：使用唯一稳定的 key，长列表采用虚拟列表（如 react-window）

・代码分割：通过 React.lazy 和 Suspense 实现组件懒加载，减小初始包体积

・减少重排重绘：避免频繁操作 DOM，使用 CSS 动画替代 JS 动画，合理使用 useLayoutEffect

## 答案 2：口语化扩展回答

React 性能优化可以从多个维度入手。首先是减少不必要的组件渲染，很多时候组件会因为父组件更新而跟着重新渲染，这时候用 React.memo 包裹函数组件，或者类组件继承 PureComponent，就能通过浅比较 props 来避免这种情况。如果有传递函数或复杂计算结果给子组件，记得用 useCallback 和 useMemo 缓存，不然每次渲染都会生成新引用，导致子组件误更新。

状态管理也很关键，别把所有状态都放在顶层组件，比如一个表单的输入状态，完全可以放在表单组件内部，没必要让整个页面跟着更新。对于列表，尤其是长列表，一定要用数据本身的唯一 id 做 key，别用索引，否则增删数据时会导致大量 DOM 重建。如果列表特别长，比如几千条数据，用虚拟列表只渲染可视区域的内容，能显著提升性能。

代码体积方面，用 React.lazy 配合 Suspense 拆分组件，让首屏只加载必要的代码，其他组件等需要时再加载，能加快首屏渲染速度。另外，避免在渲染阶段做复杂计算，尽量把计算逻辑移到 useEffect 里，或者用 useMemo 缓存结果。还有，事件处理函数里别创建新函数，不然每次渲染都会触发子组件更新。最后，合理使用 React DevTools 的 Profiler 工具，能帮你定位具体的性能瓶颈。

## 答案 3：技术深度解析

### 一、渲染优化：减少不必要的重渲染

#### 1. 组件缓存机制

**（1）函数组件优化**



```
// React.memo 缓存组件（浅比较props）

const MemoizedComponent = React.memo(function MyComponent(props) {

&#x20; // 组件逻辑

&#x20; return \<div>{props.name}\</div>;

});

// 自定义比较函数（深比较场景）

const DeepCompareComponent = React.memo(

&#x20; MyComponent,

&#x20; (prevProps, nextProps) => {

&#x20;   // 自定义判断逻辑，返回true表示不更新

&#x20;   return prevProps.user.id === nextProps.user.id;

&#x20; }

);
```

**（2）类组件优化**



```
// PureComponent 内置浅比较

class MyPureComponent extends React.PureComponent {

&#x20; render() {

&#x20;   return \<div>{this.props.name}\</div>;

&#x20; }

}

// 自定义shouldComponentUpdate

class MyComponent extends React.Component {

&#x20; shouldComponentUpdate(nextProps, nextState) {

&#x20;   // 精确控制更新条件

&#x20;   return this.props.id !== nextProps.id || this.state.count !== nextState.count;

&#x20; }

}
```

#### 2. 引用类型优化



```
function ParentComponent() {

&#x20; const \[count, setCount] = useState(0);

&#x20; const user = { name: "John", age: 30 };

&#x20; // 缓存函数（避免每次渲染创建新函数）

&#x20; const handleClick = useCallback(() => {

&#x20;   console.log("点击事件");

&#x20; }, \[]); // 空依赖数组表示函数不会变化

&#x20; // 缓存计算结果（复杂计算场景）

&#x20; const filteredList = useMemo(() => {

&#x20;   return largeList.filter(item => item.score > 90);

&#x20; }, \[largeList]); // 依赖largeList变化时才重新计算

&#x20; return (

&#x20;   \<div>

&#x20;     \<ChildComponent onClick={handleClick} user={user} />

&#x20;     \<ListComponent data={filteredList} />

&#x20;   \</div>

&#x20; );

}
```

### 二、状态管理优化

#### 1. 状态局部化



```
// 反模式：过度集中的状态

function BadExample() {

&#x20; const \[user, setUser] = useState({});

&#x20; const \[todos, setTodos] = useState(\[]);

&#x20; const \[theme, setTheme] = useState("light");

&#x20; return (

&#x20;   \<div>

&#x20;     \<UserInfo user={user} />

&#x20;     \<TodoList todos={todos} />

&#x20;     \<ThemeSwitcher theme={theme} />

&#x20;   \</div>

&#x20; );

}

// 优化：状态分散管理

function GoodExample() {

&#x20; return (

&#x20;   \<div>

&#x20;     \<UserInfo /> {/\* 内部管理user状态 \*/}

&#x20;     \<TodoList /> {/\* 内部管理todos状态 \*/}

&#x20;     \<ThemeSwitcher /> {/\* 内部管理theme状态 \*/}

&#x20;   \</div>

&#x20; );

}
```

#### 2. 不可变数据更新



```
// 错误方式：直接修改原对象（不会触发更新）

const updateUser = () => {

&#x20; user.age = 20;

&#x20; setUser(user);

};

// 正确方式：创建新对象（使用扩展运算符或Immer库）

const updateUser = () => {

&#x20; setUser({

&#x20;   ...user,

&#x20;   age: 20

&#x20; });

};

// 使用Immer简化不可变更新

import { produce } from "immer";

const updateUser = () => {

&#x20; setUser(produce(draft => {

&#x20;   draft.age = 20; // 直接"修改"草稿对象

&#x20; }));

};
```

### 三、列表渲染优化

#### 1. 合理使用 key



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

#### 2. 虚拟列表实现



```
import { FixedSizeList as List } from "react-window";

// 长列表优化（只渲染可视区域内容）

function VirtualizedList({ data }) {

&#x20; const Row = ({ index, style }) => (

&#x20;   \<div style={style}>

&#x20;     {data\[index].name}

&#x20;   \</div>

&#x20; );

&#x20; return (

&#x20;   \<List

&#x20;     height={500} // 可视区域高度

&#x20;     width="100%"  // 可视区域宽度

&#x20;     itemCount={data.length} // 总条数

&#x20;     itemSize={50} // 每条高度

&#x20;   \>

&#x20;     {Row}

&#x20;   \</List>

&#x20; );

}
```

### 四、代码分割与懒加载

#### 1. 组件懒加载



```
// 动态导入组件

const LazyComponent = React.lazy(() => import("./LazyComponent"));

// 使用Suspense提供加载状态

function App() {

&#x20; return (

&#x20;   \<div>

&#x20;     \<Suspense fallback={\<div>Loading...\</div>}>

&#x20;       \<LazyComponent />

&#x20;     \</Suspense>

&#x20;   \</div>

&#x20; );

}
```

#### 2. 路由级别的代码分割



```
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import React, { Suspense, lazy } from "react";

// 按路由分割代码

const Home = lazy(() => import("./routes/Home"));

const About = lazy(() => import("./routes/About"));

function App() {

&#x20; return (

&#x20;   \<Router>

&#x20;     \<Suspense fallback={\<div>Loading...\</div>}>

&#x20;       \<Routes>

&#x20;         \<Route path="/" element={\<Home />} />

&#x20;         \<Route path="/about" element={\<About />} />

&#x20;       \</Routes>

&#x20;     \</Suspense>

&#x20;   \</Router>

&#x20; );

}
```

### 五、DOM 操作优化

#### 1. 减少重排重绘



```
// 避免频繁修改DOM样式

function BadExample() {

&#x20; const \[left, setLeft] = useState(0);

&#x20;&#x20;

&#x20; useEffect(() => {

&#x20;   const timer = setInterval(() => {

&#x20;     // 每次更新都会触发重排

&#x20;     setLeft(prev => prev + 1);

&#x20;   }, 16);

&#x20;   return () => clearInterval(timer);

&#x20; }, \[]);

&#x20;&#x20;

&#x20; return \<div style={{ left }} />;

}

// 使用CSS动画替代JS动画

function GoodExample() {

&#x20; const \[isMoving, setIsMoving] = useState(false);

&#x20;&#x20;

&#x20; return (

&#x20;   \<div&#x20;

&#x20;     className={\`box \${isMoving ? 'move' : ''}\`}

&#x20;     onClick={() => setIsMoving(true)}

&#x20;   />

&#x20; );

}

// CSS

// .box { transition: transform 0.3s; }

// .move { transform: translateX(100px); }
```

#### 2. 合理使用 ref



```
// 避免通过state控制DOM属性

function GoodExample() {

&#x20; const inputRef = useRef(null);

&#x20;&#x20;

&#x20; const focusInput = () => {

&#x20;   // 直接操作DOM，不触发重渲染

&#x20;   inputRef.current.focus();

&#x20; };

&#x20;&#x20;

&#x20; return (

&#x20;   \<div>

&#x20;     \<input ref={inputRef} />

&#x20;     \<button onClick={focusInput}>聚焦输入框\</button>

&#x20;   \</div>

&#x20; );

}
```

### 六、高级优化策略

#### 1. 使用 React.memo 结合 Context 优化



```
// 拆分Context，避免不必要的更新

const UserContext = React.createContext();

const ThemeContext = React.createContext();

// 只依赖ThemeContext的组件不会因UserContext变化而更新

function ThemeComponent() {

&#x20; const theme = useContext(ThemeContext);

&#x20; return \<div style={{ color: theme.color }} />;

}

// 缓存组件

const MemoizedThemeComponent = React.memo(ThemeComponent);
```

#### 2. 使用 web workers 处理计算密集型任务



```
// 将复杂计算移到worker中，避免阻塞主线程

function DataProcessor() {

&#x20; const \[result, setResult] = useState(null);

&#x20;&#x20;

&#x20; useEffect(() => {

&#x20;   // 创建worker

&#x20;   const worker = new Worker("./data-worker.js");

&#x20;  &#x20;

&#x20;   // 发送数据给worker

&#x20;   worker.postMessage(largeDataset);

&#x20;  &#x20;

&#x20;   // 接收计算结果

&#x20;   worker.onmessage = (e) => {

&#x20;     setResult(e.data);

&#x20;   };

&#x20;  &#x20;

&#x20;   return () => worker.terminate();

&#x20; }, \[largeDataset]);

&#x20;&#x20;

&#x20; return \<ResultDisplay data={result} />;

}

// data-worker.js

self.onmessage = (e) => {

&#x20; // 复杂计算逻辑

&#x20; const result = heavyCalculation(e.data);

&#x20; // 发送结果回主线程

&#x20; self.postMessage(result);

};
```

#### 3. 性能监控与分析



```
import { Profiler } from "react";

// 性能监控回调

function onRenderCallback(

&#x20; id, // 组件ID

&#x20; phase, // "mount" 或 "update"

&#x20; actualDuration, // 实际耗时

&#x20; baseDuration, // 基准耗时

&#x20; startTime, // 开始时间

&#x20; commitTime, // 提交时间

&#x20; interactions // 交互信息

) {

&#x20; console.log(\`组件\${id}\${phase}耗时: \${actualDuration}ms\`);

}

// 监控目标组件

function App() {

&#x20; return (

&#x20;   \<Profiler id="MainApp" onRender={onRenderCallback}>

&#x20;     \<ComplexComponent />

&#x20;   \</Profiler>

&#x20; );

}
```

### 总结

React 性能优化是一个系统性工程，需要结合具体场景选择合适的优化策略：



1.  **渲染层**：通过组件缓存、引用类型优化减少不必要的重渲染

2.  **状态层**：合理设计状态结构，避免状态冗余和过度集中

3.  **列表层**：使用虚拟列表处理长列表，确保 key 的稳定性

4.  **代码层**：通过代码分割减小初始加载体积，实现按需加载

5.  **DOM 层**：减少重排重绘，合理使用直接 DOM 操作

实际开发中，应先通过 Profiler 工具定位性能瓶颈，再针对性优化，避免过早优化和过度优化。React 18 引入的并发渲染机制进一步提升了应用在复杂场景下的响应性能，结合新特性（如自动批处理）可获得更好的优化效果。

