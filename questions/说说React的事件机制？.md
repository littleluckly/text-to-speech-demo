# 说说 React 的事件机制？

## meta 元数据



```
{

&#x20; "id": "g6h7i8j9-k0l1-2345-mnop-67890abcdef0",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・React 的事件机制是基于原生事件的封装，采用事件委托（事件冒泡到 document 统一处理）。

・提供的是合成事件（SyntheticEvent），接口与原生事件类似，但有跨浏览器兼容性。

・事件处理函数中的 this 默认是 undefined，需通过 bind 或箭头函数绑定。

・合成事件与原生事件执行顺序不同，合成事件会在所有原生事件冒泡完成后执行。

・可通过 e.nativeEvent 获取原生事件对象，调用 e.preventDefault () 阻止默认行为。

## 答案 2：口语化扩展回答

React 的事件机制并不是直接使用浏览器的原生事件，而是自己做了一层封装。简单说，就是 React 会把所有的事件处理都委托到 document 这个顶层节点上，不管你在哪个元素上绑定事件，最终都会由 document 来统一处理，这样能减少事件监听器的数量，提高性能。

它提供的事件叫合成事件，用法和原生事件差不多，比如 onClick、onChange 这些，但名字用的是驼峰式。这种合成事件帮我们处理了不同浏览器之间的兼容性问题，不用自己写代码去适配各种浏览器了。

不过有几点要注意，比如事件处理函数里的 this，默认情况下是 undefined，所以得用 bind 方法或者箭头函数来绑定正确的 this 指向。另外，合成事件和原生事件的执行顺序不一样，原生事件的冒泡会先完成，然后才会执行 React 的合成事件处理函数。如果想在 React 里用原生事件的方法，可以通过事件对象的 nativeEvent 属性获取原生事件。

还有，阻止默认行为也和原生不太一样，在 React 里直接调用 e.preventDefault () 就行，不用像原生那样先调用 e.returnValue 了，这也是合成事件带来的便利。

## 答案 3：技术深度解析

### React 事件机制的核心原理

React 的事件机制是一套基于浏览器原生事件的**合成事件系统（SyntheticEvent）**，其设计目标是实现跨浏览器兼容性、优化事件处理性能，并提供统一的事件接口。

#### 1. 事件委托机制

React 采用**事件委托（Event Delegation）** 模式，将所有事件处理函数统一委托到文档根节点（document）上，而非直接绑定在具体的 DOM 元素上。

**工作流程**：



*   组件挂载时，React 会将事件处理函数注册到 document 上，并记录事件类型、对应的 DOM 元素和处理函数等信息。

*   当用户触发事件（如点击），事件会从目标元素向上冒泡至 document。

*   document 上的事件监听器捕获到事件后，React 会根据之前记录的信息，找到对应的组件和处理函数并执行。

**代码示例：事件委托的底层实现逻辑（简化版）**



```
// React内部维护的事件注册表

const eventRegistry = new Map();

// 注册事件到document

function registerEvent(domElement, eventType, handler) {

&#x20; // 生成唯一标识

&#x20; const key = \`\${eventType}-\${domElement.id}\`;

&#x20; eventRegistry.set(key, { domElement, handler });

&#x20;&#x20;

&#x20; // 委托到document（同类型事件只注册一次）

&#x20; if (!document\[\`\_\_react\_\${eventType}\`]) {

&#x20;   document.addEventListener(eventType, dispatchEvent);

&#x20;   document\[\`\_\_react\_\${eventType}\`] = true;

&#x20; }

}

// 事件分发函数

function dispatchEvent(nativeEvent) {

&#x20; const eventType = nativeEvent.type;

&#x20; // 遍历查找匹配的事件处理函数

&#x20; eventRegistry.forEach(({ domElement, handler }, key) => {

&#x20;   if (key.startsWith(eventType) && isEventTarget(domElement, nativeEvent.target)) {

&#x20;     // 创建合成事件并执行处理函数

&#x20;     const syntheticEvent = createSyntheticEvent(nativeEvent);

&#x20;     handler.call(null, syntheticEvent);

&#x20;   }

&#x20; });

}
```

#### 2. 合成事件（SyntheticEvent）

合成事件是 React 对原生事件的封装，具有以下特点：



*   **跨浏览器一致性**：屏蔽了不同浏览器原生事件的差异（如 IE 的`attachEvent`与标准的`addEventListener`）。

*   **与原生事件类似的接口**：提供`stopPropagation()`、`preventDefault()`等方法，用法与原生事件一致。

*   **事件池复用**：合成事件对象会被放入事件池复用，避免频繁创建和销毁对象（React 17 + 已移除事件池）。

**合成事件结构（简化版）**：



```
class SyntheticEvent {

&#x20; constructor(nativeEvent) {

&#x20;   this.nativeEvent = nativeEvent; // 原生事件对象

&#x20;   this.target = nativeEvent.target; // 事件目标元素

&#x20;   this.type = nativeEvent.type; // 事件类型

&#x20;   // 其他属性...

&#x20; }

&#x20; // 阻止合成事件冒泡

&#x20; stopPropagation() {

&#x20;   this.isPropagationStopped = true;

&#x20;   // 同时阻止原生事件冒泡

&#x20;   this.nativeEvent.stopPropagation();

&#x20; }

&#x20; // 阻止默认行为

&#x20; preventDefault() {

&#x20;   this.isDefaultPrevented = true;

&#x20;   this.nativeEvent.preventDefault();

&#x20; }

}
```

#### 3. 事件处理函数的 this 绑定

React 事件处理函数中的`this`默认是`undefined`（非严格模式下为`window`），需要显式绑定：

**常用绑定方式**：



```
// 1. 构造函数中bind（推荐，只执行一次）

class MyComponent extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   this.handleClick = this.handleClick.bind(this);

&#x20; }

&#x20;&#x20;

&#x20; handleClick() {

&#x20;   console.log(this.props); // 正确指向组件实例

&#x20; }

}

// 2. 箭头函数（每次渲染都会创建新函数）

class MyComponent extends React.Component {

&#x20; handleClick = () => {

&#x20;   console.log(this.props); // 箭头函数继承外层this

&#x20; }

}

// 3. 渲染时绑定（不推荐，每次渲染创建新函数）

render() {

&#x20; return \<button onClick={this.handleClick.bind(this)}>Click\</button>;

}
```

### 事件执行顺序与冒泡机制

React 合成事件与原生事件的执行顺序存在差异，主要体现在事件冒泡阶段：



1.  **原生事件捕获阶段**：从 document 向下传播到目标元素。

2.  **原生事件冒泡阶段**：从目标元素向上传播到 document。

3.  **React 合成事件处理**：在原生事件冒泡至 document 后执行。

**代码示例：执行顺序验证**



```
class EventOrder extends React.Component {

&#x20; componentDidMount() {

&#x20;   // 绑定原生事件

&#x20;   this.buttonRef.addEventListener('click', () => {

&#x20;     console.log('原生事件（冒泡）');

&#x20;   }, false); // false表示冒泡阶段

&#x20;  &#x20;

&#x20;   this.buttonRef.addEventListener('click', () => {

&#x20;     console.log('原生事件（捕获）');

&#x20;   }, true); // true表示捕获阶段

&#x20; }

&#x20;&#x20;

&#x20; handleClick = () => {

&#x20;   console.log('React合成事件');

&#x20; }

&#x20;&#x20;

&#x20; render() {

&#x20;   return (

&#x20;     \<button&#x20;

&#x20;       ref={ref => this.buttonRef = ref}

&#x20;       onClick={this.handleClick}

&#x20;     \>

&#x20;       点击测试

&#x20;     \</button>

&#x20;   );

&#x20; }

}

// 点击后输出顺序：

// 原生事件（捕获）

// 原生事件（冒泡）

// React合成事件
```

**阻止冒泡的注意事项**：



*   合成事件中调用`e.stopPropagation()`会同时阻止合成事件和原生事件的冒泡。

*   原生事件中阻止冒泡（`e.stopPropagation()`）会导致 React 合成事件无法触发（因为合成事件依赖冒泡到 document）。

### 与原生事件的主要区别



| 特性          | React 合成事件                                   | 浏览器原生事件            |
| ----------- | -------------------------------------------- | ------------------ |
| 事件名称        | 驼峰式（如 onClick）                               | 小写（如 onclick）      |
| 绑定方式        | JSX 属性（如`<button onClick={handler}>`）        | `addEventListener` |
| 事件处理函数 this | 默认 undefined，需显式绑定                           | 指向绑定事件的元素          |
| 事件对象        | SyntheticEvent 实例                            | Event 实例           |
| 事件委托        | 委托到 document（React 17 前）或 root 节点（React 17+） | 需手动实现              |
| 跨浏览器兼容      | 自动处理                                         | 需手动处理              |
| 事件池         | React 17 前存在，17 + 移除                         | 无                  |

### React 17 中的事件机制变化

React 17 对事件机制进行了重要调整，主要变化包括：



1.  **事件委托目标改变**：从 document 改为 React 根节点（即`ReactDOM.render`挂载的节点），解决了与其他库的事件冲突问题。

2.  **移除事件池**：合成事件对象不再被复用，避免了异步访问事件属性时的`null`问题。



```
// React 16及之前（事件池导致的问题）

handleClick = (e) => {

&#x20; setTimeout(() => {

&#x20;   console.log(e.target); // 输出null，因为事件对象已被回收

&#x20; }, 0);

};

// React 17+（无事件池）

handleClick = (e) => {

&#x20; setTimeout(() => {

&#x20;   console.log(e.target); // 正常输出目标元素

&#x20; }, 0);

};
```



1.  **更好的事件冒泡兼容性**：合成事件的冒泡行为与原生事件更加一致，便于与其他 DOM 库协同工作。

### 实际开发中的注意事项



1.  **避免混合使用合成事件与原生事件**：可能导致事件执行顺序混乱或冒泡被意外阻止。

2.  **正确获取事件目标**：合成事件的`e.target`可能与原生事件的`e.target`存在差异（如在表单元素中），必要时使用`e.nativeEvent.target`获取原生目标。

3.  **事件解绑**：对于通过`addEventListener`绑定的原生事件，需在`componentWillUnmount`中手动解绑，避免内存泄漏。



```
componentDidMount() {

&#x20; this.handler = () => console.log('原生事件');

&#x20; window.addEventListener('scroll', this.handler);

}

componentWillUnmount() {

&#x20; window.removeEventListener('scroll', this.handler); // 必须解绑

}
```



1.  **表单事件处理**：React 对表单事件进行了特殊处理（如`onChange`在输入时立即触发，而非原生的失焦后触发），提供更符合预期的用户体验。

### 总结

React 的事件机制通过合成事件和事件委托，在原生事件基础上构建了一套更统一、更易用的事件处理系统。其核心优势在于跨浏览器兼容性、性能优化和开发体验提升。

理解 React 事件机制的工作原理，尤其是合成事件与原生事件的区别、执行顺序和冒泡机制，有助于开发者避免常见的事件处理问题，编写更健壮的 React 应用。同时，关注 React 版本更新带来的事件机制变化（如 React 17 的调整），能更好地适应框架的发展。

