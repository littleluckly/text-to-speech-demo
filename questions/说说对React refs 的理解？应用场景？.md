# 说说对 React refs 的理解？应用场景？

## meta 元数据



```
{

&#x20; "id": "h1i2j3k4-l5m6-7890-opqr-1234567890uv",

&#x20; "type": "answer",

&#x20; "difficulty": "easy",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・React refs 是用于访问 DOM 节点或组件实例的特殊属性，允许直接与 DOM 或组件交互

・创建方式：函数组件用 useRef，类组件用 createRef 或回调 refs

・特性： refs 变化不会触发重渲染，避免通过 state 间接操作 DOM 的性能开销

・应用场景：获取表单元素值、控制媒体播放、操作 DOM 元素尺寸 / 位置、集成第三方 DOM 库

・注意：应避免过度使用 refs，优先通过 props 和 state 管理组件交互

## 答案 2：口语化扩展回答

React refs 就像是给 DOM 元素或组件打了个标记，让我们能直接访问到它们，有点类似原生 JS 里的 getElementById，但更符合 React 的组件化思想。在函数组件里，我们通常用 useRef 这个 Hook 来创建 refs，它会返回一个带 current 属性的对象，这个属性就指向我们要访问的 DOM 或组件实例。类组件里则可以用 createRef 或者回调函数的方式来创建。

使用 refs 的时候要注意，它并不会像 state 那样触发组件重渲染，这是它的一个重要特点。这意味着我们可以用它来存储一些不需要引起界面更新的数据，但最主要的用途还是操作 DOM。比如表单里的输入框，有时候需要直接获取用户输入的值，或者让输入框自动聚焦，这时候用 refs 就很方便。

另外，在处理一些媒体元素像视频、音频时，用 refs 可以直接调用它们的 play、pause 方法。还有当需要获取某个元素的尺寸或者位置时，比如实现滚动加载、拖拽功能，也会用到 refs 来获取 DOM 节点的信息。不过要记住，React 的理念是尽量通过 props 和 state 来管理组件交互，refs 应该作为一种补充手段，不要过度依赖，否则会让组件逻辑变得混乱，难以维护。

## 答案 3：技术深度解析

### 一、React refs 的核心概念

React refs 提供了一种绕过组件声明式 API，直接访问 DOM 节点或组件实例的方式。它打破了 React"数据驱动" 的常规流程，允许开发者进行**命令式操作**。

#### 1. refs 的本质

refs 本质上是一个容器对象，其结构为：



```
{

&#x20; current: null | DOMElement | ComponentInstance

}
```



*   `current`属性初始值为`null`

*   当 refs 与 DOM 元素关联时，`current`指向该 DOM 节点

*   当 refs 与类组件关联时，`current`指向该组件的实例

*   函数组件默认不支持 refs（无实例），需通过`forwardRef`包装

#### 2. 创建与使用方式

**（1）函数组件中使用 useRef**



```
import { useRef } from 'react';

function InputComponent() {

&#x20; // 创建refs对象

&#x20; const inputRef = useRef(null);

&#x20;&#x20;

&#x20; const handleFocus = () => {

&#x20;   // 访问DOM元素并调用方法

&#x20;   inputRef.current.focus();

&#x20; };

&#x20;&#x20;

&#x20; return (

&#x20;   \<div>

&#x20;     {/\* 关联DOM元素 \*/}

&#x20;     \<input type="text" ref={inputRef} />

&#x20;     \<button onClick={handleFocus}>聚焦输入框\</button>

&#x20;   \</div>

&#x20; );

}
```

**（2）类组件中使用 createRef**



```
import { createRef } from 'react';

class InputComponent extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   // 创建refs对象

&#x20;   this.inputRef = createRef(null);

&#x20; }

&#x20;&#x20;

&#x20; handleFocus = () => {

&#x20;   this.inputRef.current.focus();

&#x20; };

&#x20;&#x20;

&#x20; render() {

&#x20;   return (

&#x20;     \<div>

&#x20;       \<input type="text" ref={this.inputRef} />

&#x20;       \<button onClick={this.handleFocus}>聚焦输入框\</button>

&#x20;     \</div>

&#x20;   );

&#x20; }

}
```

**（3）回调 refs**



```
function CallbackRefComponent() {

&#x20; let inputRef = null;

&#x20;&#x20;

&#x20; // 定义回调函数

&#x20; const setInputRef = (element) => {

&#x20;   inputRef = element; // 直接存储DOM引用

&#x20; };

&#x20;&#x20;

&#x20; const handleFocus = () => {

&#x20;   if (inputRef) inputRef.focus();

&#x20; };

&#x20;&#x20;

&#x20; return (

&#x20;   \<div>

&#x20;     \<input type="text" ref={setInputRef} />

&#x20;     \<button onClick={handleFocus}>聚焦输入框\</button>

&#x20;   \</div>

&#x20; );

}
```

**（4）转发 refs 到函数组件（forwardRef）**



```
import { forwardRef } from 'react';

// 使用forwardRef包装函数组件

const CustomInput = forwardRef((props, ref) => (

&#x20; \<input type="text" ref={ref} {...props} />

));

// 使用包装后的组件

function ParentComponent() {

&#x20; const inputRef = useRef(null);

&#x20;&#x20;

&#x20; return \<CustomInput ref={inputRef} placeholder="请输入" />;

}
```

### 二、refs 的关键特性



1.  **不触发重渲染**：

*   refs 的变化不会导致组件重新渲染

*   与 state 的核心区别：state 更新会触发渲染，refs 仅用于访问

1.  **更新时机**：

*   refs 在组件挂载后被赋值（`current`变为有效）

*   在组件卸载后被重置为`null`

*   在`useEffect`或`componentDidMount`/`componentDidUpdate`中可安全访问

1.  **不可变性**：

*   `useRef`返回的 refs 对象在组件生命周期内保持不变（同一个引用）

*   修改`current`属性不会触发任何 React 生命周期方法

### 三、实际应用场景

#### 1. 表单控制

**获取输入值**：



```
function FormComponent() {

&#x20; const usernameRef = useRef(null);

&#x20; const passwordRef = useRef(null);

&#x20;&#x20;

&#x20; const handleSubmit = (e) => {

&#x20;   e.preventDefault();

&#x20;   // 直接获取输入值

&#x20;   const data = {

&#x20;     username: usernameRef.current.value,

&#x20;     password: passwordRef.current.value

&#x20;   };

&#x20;   console.log('表单数据:', data);

&#x20; };

&#x20;&#x20;

&#x20; return (

&#x20;   \<form onSubmit={handleSubmit}>

&#x20;     \<input type="text" ref={usernameRef} />

&#x20;     \<input type="password" ref={passwordRef} />

&#x20;     \<button type="submit">提交\</button>

&#x20;   \</form>

&#x20; );

}
```

**表单验证聚焦**：



```
function ValidationForm() {

&#x20; const inputsRef = useRef({});

&#x20;&#x20;

&#x20; const validate = () => {

&#x20;   let isValid = true;

&#x20;   // 验证所有输入框

&#x20;   Object.values(inputsRef.current).forEach(input => {

&#x20;     if (!input.value) {

&#x20;       input.focus(); // 聚焦到第一个无效输入

&#x20;       isValid = false;

&#x20;     }

&#x20;   });

&#x20;   return isValid;

&#x20; };

&#x20;&#x20;

&#x20; return (

&#x20;   \<form>

&#x20;     \<input&#x20;

&#x20;       name="username"&#x20;

&#x20;       ref={el => inputsRef.current.username = el}&#x20;

&#x20;     />

&#x20;     \<input&#x20;

&#x20;       name="email"&#x20;

&#x20;       ref={el => inputsRef.current.email = el}&#x20;

&#x20;     />

&#x20;     \<button onClick={validate}>验证\</button>

&#x20;   \</form>

&#x20; );

}
```

#### 2. 媒体元素控制



```
function VideoPlayer() {

&#x20; const videoRef = useRef(null);

&#x20;&#x20;

&#x20; const handlePlay = () => {

&#x20;   videoRef.current.play(); // 调用视频播放方法

&#x20; };

&#x20;&#x20;

&#x20; const handlePause = () => {

&#x20;   videoRef.current.pause(); // 调用视频暂停方法

&#x20; };

&#x20;&#x20;

&#x20; return (

&#x20;   \<div>

&#x20;     \<video&#x20;

&#x20;       ref={videoRef}&#x20;

&#x20;       src="/example.mp4"&#x20;

&#x20;       width="640"

&#x20;     />

&#x20;     \<button onClick={handlePlay}>播放\</button>

&#x20;     \<button onClick={handlePause}>暂停\</button>

&#x20;   \</div>

&#x20; );

}
```

#### 3. DOM 尺寸与位置获取



```
function ResizeComponent() {

&#x20; const containerRef = useRef(null);

&#x20; const \[size, setSize] = useState({ width: 0, height: 0 });

&#x20;&#x20;

&#x20; useEffect(() => {

&#x20;   // 获取元素尺寸

&#x20;   const updateSize = () => {

&#x20;     const { offsetWidth, offsetHeight } = containerRef.current;

&#x20;     setSize({ width: offsetWidth, height: offsetHeight });

&#x20;   };

&#x20;  &#x20;

&#x20;   updateSize(); // 初始获取

&#x20;   window.addEventListener('resize', updateSize); // 监听窗口变化

&#x20;  &#x20;

&#x20;   return () => {

&#x20;     window.removeEventListener('resize', updateSize);

&#x20;   };

&#x20; }, \[]);

&#x20;&#x20;

&#x20; return (

&#x20;   \<div ref={containerRef}>

&#x20;     \<p>宽度: {size.width}px\</p>

&#x20;     \<p>高度: {size.height}px\</p>

&#x20;   \</div>

&#x20; );

}
```

#### 4. 第三方 DOM 库集成

许多 UI 库（如 Chart.js、Mapbox）需要直接操作 DOM 元素，refs 是最佳选择：



```
import { useEffect, useRef } from 'react';

import Chart from 'chart.js/auto';

function ChartComponent() {

&#x20; const canvasRef = useRef(null);

&#x20; const chartRef = useRef(null); // 存储图表实例

&#x20;&#x20;

&#x20; useEffect(() => {

&#x20;   // 初始化图表

&#x20;   chartRef.current = new Chart(canvasRef.current, {

&#x20;     type: 'bar',

&#x20;     data: { labels: \['A', 'B', 'C'], datasets: \[{ data: \[10, 20, 30] }] }

&#x20;   });

&#x20;  &#x20;

&#x20;   return () => {

&#x20;     // 清理图表实例

&#x20;     chartRef.current.destroy();

&#x20;   };

&#x20; }, \[]);

&#x20;&#x20;

&#x20; return \<canvas ref={canvasRef} />;

}
```

#### 5. 滚动控制



```
function ScrollableList() {

&#x20; const listRef = useRef(null);

&#x20;&#x20;

&#x20; const scrollToBottom = () => {

&#x20;   // 滚动到列表底部

&#x20;   listRef.current.scrollTop = listRef.current.scrollHeight;

&#x20; };

&#x20;&#x20;

&#x20; return (

&#x20;   \<div>

&#x20;     \<div&#x20;

&#x20;       ref={listRef}&#x20;

&#x20;       style={{ height: '300px', overflow: 'auto' }}

&#x20;     \>

&#x20;       {/\* 长列表内容 \*/}

&#x20;     \</div>

&#x20;     \<button onClick={scrollToBottom}>滚动到底部\</button>

&#x20;   \</div>

&#x20; );

}
```

### 四、使用 refs 的注意事项



1.  **优先数据驱动**：

*   大多数情况下，应使用 state 和 props 管理组件交互

*   例如：表单控制优先使用受控组件（通过 state 管理值），而非 refs

1.  **避免过度使用**：

*   滥用 refs 会导致组件逻辑难以维护

*   复杂交互应考虑封装为自定义 Hook 或组件

1.  **函数组件的限制**：

*   不能直接给函数组件添加 refs（无实例）

*   需通过`forwardRef`转发，或使用包装组件

1.  **SSR 注意事项**：

*   服务端渲染时，DOM 尚未存在，refs 会为`null`

*   需在`useEffect`或`componentDidMount`中访问，避免报错

1.  **性能考量**：

*   频繁通过 refs 操作 DOM 可能导致性能问题

*   复杂 DOM 操作应合并或使用`requestAnimationFrame`

### 总结

React refs 是一种特殊的机制，允许开发者直接访问 DOM 元素或组件实例，适用于那些无法通过声明式 API 实现的命令式操作。其核心价值在于填补了 "数据驱动" 模式的空白，解决了表单控制、媒体操作、DOM 尺寸获取等实际开发需求。

使用 refs 时，应遵循 "最小必要" 原则：优先使用 state 和 props 管理组件交互，仅在必要时引入 refs。合理使用 refs 可以简化代码实现，但过度依赖会降低组件的可维护性和可测试性。理解 refs 的工作原理和应用场景，有助于开发者在 React 项目中做出更合理的技术选择。

