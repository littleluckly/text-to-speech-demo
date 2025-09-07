# react 中 state 和 props 有什么区别？

## meta 元数据



```
{

&#x20; "id": "e4f5g6h7-i8j9-0123-klmn-4567890abcde",

&#x20; "type": "answer",

&#x20; "difficulty": "easy",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・来源不同：state 是组件内部自己管理的数据，由组件自身初始化和修改；props 是从父组件传递过来的数据，组件自身无法修改。

・可变性不同：state 是可变的，通过 setState 方法更新；props 是只读的，不能在子组件中直接修改。

・作用范围不同：state 仅在当前组件内部生效；props 用于组件之间的数据传递，从父到子单向流动。

・使用场景不同：state 用于管理组件内部的动态状态；props 用于组件间通信和传递静态或动态数据。

## 答案 2：口语化扩展回答

state 和 props 都是 React 里用来管理数据的，但它们的角色和用法差别挺大。

state 就像是组件自己的 “私房钱”，是组件内部独有的数据，只能自己说了算。比如一个计数器组件，记录当前计数的那个数字就适合用 state，组件可以自己决定什么时候加一、什么时候清零，通过 setState 方法就能轻松更新。而且这些数据只有组件自己知道，外面拿不到也改不了，完全是内部事务。

props 则像是父组件给子组件的 “零花钱”，是从外面传进来的，子组件只能看不能改。比如父组件想让子组件显示不同的文本，就把文本内容通过 props 传给子组件，子组件收到后照着显示就行。如果子组件觉得这个数据不合适，也不能自己直接改，只能告诉父组件，让父组件重新传一个新值过来。

简单说，state 管内部变化，props 管外部传递，两者配合着用，就能让组件既灵活又可控。比如一个表单组件，输入框里的内容用 state 管理，而表单的提示文字、初始值这些可以通过 props 从外面传进来，这样组件既可以自己处理用户输入，又能被外部灵活配置。

## 答案 3：技术深度解析

### state 与 props 的本质差异

在 React 组件模型中，state 和 props 是管理数据的两种核心机制，它们的本质差异体现在**数据所有权**和**生命周期管理**上。



| 特性    | state                  | props     |
| ----- | ---------------------- | --------- |
| 数据来源  | 组件内部初始化                | 父组件传递     |
| 可修改性  | 组件自身可修改                | 只读，不可修改   |
| 数据流向  | 内部封闭                   | 父→子单向流动   |
| 初始化位置 | 组件构造函数或 useState       | 父组件调用时指定  |
| 变化触发  | setState/useState 更新函数 | 父组件重新渲染   |
| 作用域   | 仅限当前组件                 | 可沿组件树向下传递 |

### 技术实现细节对比

#### 1. 初始化方式

**state 初始化（类组件）**：



```
class Counter extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   // 初始化state

&#x20;   this.state = {

&#x20;     count: props.initialCount || 0 // 可基于props初始化

&#x20;   };

&#x20; }

}
```

**state 初始化（函数组件）**：



```
function Counter({ initialCount = 0 }) {

&#x20; // 数组解构获取状态和更新函数

&#x20; const \[count, setCount] = React.useState(initialCount);

&#x20; return \<div>{count}\</div>;

}
```

**props 接收方式**：



```
// 类组件接收props

class Greeting extends React.Component {

&#x20; render() {

&#x20;   return \<h1>Hello, {this.props.name}\</h1>;

&#x20; }

}

// 函数组件接收props（解构方式更简洁）

function Greeting({ name }) {

&#x20; return \<h1>Hello, {name}\</h1>;

}
```

#### 2. 数据更新机制

**state 更新（类组件）**：



```
class Counter extends React.Component {

&#x20; increment() {

&#x20;   // 正确：使用函数式更新确保基于最新状态

&#x20;   this.setState(prevState => ({

&#x20;     count: prevState.count + 1

&#x20;   }));

&#x20;  &#x20;

&#x20;   // 错误：直接修改state不会触发重新渲染

&#x20;   // this.state.count += 1;

&#x20; }

}
```

**state 更新（函数组件）**：



```
function Counter() {

&#x20; const \[count, setCount] = React.useState(0);

&#x20;&#x20;

&#x20; const increment = () => {

&#x20;   // 函数式更新适用于依赖先前状态的场景

&#x20;   setCount(prev => prev + 1);

&#x20; };

&#x20;&#x20;

&#x20; return \<button onClick={increment}>{count}\</button>;

}
```

**props 更新机制**：



```
// 父组件重新渲染时传递新的props

function Parent() {

&#x20; const \[name, setName] = React.useState("Alice");

&#x20;&#x20;

&#x20; return (

&#x20;   \<div>

&#x20;     \<button onClick={() => setName("Bob")}>Change Name\</button>

&#x20;     \<Greeting name={name} /> {/\* 点击按钮后Greeting会收到新的name \*/}

&#x20;   \</div>

&#x20; );

}
```

#### 3. 数据传递与作用域

**props 的单向数据流示例**：



```
// 祖父组件

function Grandparent() {

&#x20; const \[theme, setTheme] = React.useState("light");

&#x20; return \<Parent theme={theme} onThemeChange={setTheme} />;

}

// 父组件：仅传递props，不修改

function Parent({ theme, onThemeChange }) {

&#x20; return \<Child theme={theme} onThemeChange={onThemeChange} />;

}

// 子组件：通过回调修改上游state

function Child({ theme, onThemeChange }) {

&#x20; return (

&#x20;   \<button onClick={() => onThemeChange(theme === "light" ? "dark" : "light")}>

&#x20;     Current theme: {theme}

&#x20;   \</button>

&#x20; );

}
```

**state 的封闭性示例**：



```
function UserProfile() {

&#x20; // 此state完全由UserProfile控制，子组件无法直接访问

&#x20; const \[user, setUser] = React.useState({ name: "", age: 0 });

&#x20;&#x20;

&#x20; const fetchUser = async () => {

&#x20;   const data = await api.getUser();

&#x20;   setUser(data); // 仅内部可更新

&#x20; };

&#x20;&#x20;

&#x20; return \<ProfileDisplay user={user} />; // 需通过props传递给子组件

}
```

### 适用场景分析

#### 适合使用 state 的场景：



*   组件内部的动态状态（如表单输入值、弹窗显示 / 隐藏）

*   用户交互产生的临时状态（如鼠标悬停效果、滚动位置）

*   需要随时间变化的数据（如计时器、动画状态）

*   尚未同步到服务器的本地修改（如草稿内容）

#### 适合使用 props 的场景：



*   组件间的数据传递（父组件向子组件传递配置）

*   组件的初始配置（如默认值、主题样式）

*   回调函数传递（子组件向父组件反馈事件）

*   静态数据展示（如列表项内容、标题文本）

### 常见误区与最佳实践



1.  **直接修改 state**：



```
// 错误做法

const \[user, setUser] = useState({ name: "Tom" });

user.name = "Jerry"; // 直接修改不会触发渲染

setUser(user); // 无效，引用未变

// 正确做法

setUser(prev => ({ ...prev, name: "Jerry" })); // 创建新对象
```



1.  **试图修改 props**：



```
function Child({ value }) {

&#x20; // 错误：props是只读的

&#x20; const handleClick = () => {

&#x20;   value = "new value"; // 无效操作

&#x20; };

&#x20;&#x20;

&#x20; return \<button onClick={handleClick}>Click\</button>;

}
```



1.  **过度使用 state**：

*   可从 props 计算得出的数据无需存入 state

*   可通过 useMemo 缓存的派生数据无需存入 state



```
// 优化前：冗余state

function UserInfo({ user }) {

&#x20; const \[fullName, setFullName] = useState("");

&#x20;&#x20;

&#x20; useEffect(() => {

&#x20;   setFullName(\`\${user.firstName} \${user.lastName}\`);

&#x20; }, \[user]);

}

// 优化后：直接计算

function UserInfo({ user }) {

&#x20; const fullName = \`\${user.firstName} \${user.lastName}\`;

&#x20; // 复杂计算可使用useMemo缓存

&#x20; // const fullName = useMemo(() => \`\${user.firstName} \${user.lastName}\`, \[user]);

}
```



1.  **props 透传问题**：

    当 props 需要经过多层组件传递时，可使用 Context API 避免 "props drilling"（props 钻取）：



```
// 创建上下文

const ThemeContext = React.createContext("light");

// 顶层提供值

function App() {

&#x20; return (

&#x20;   \<ThemeContext.Provider value="dark">

&#x20;     \<ComponentA />

&#x20;   \</ThemeContext.Provider>

&#x20; );

}

// 深层组件直接使用（无需通过props传递）

function ComponentC() {

&#x20; const theme = React.useContext(ThemeContext);

&#x20; return \<div theme={theme} />;

}
```

### 总结

state 和 props 共同构成了 React 组件的数据管理体系：**state 管理组件的内部状态变化，props 负责组件间的外部通信**。理解两者的差异关键在于把握 "数据所有权"—state 属于组件自身，而 props 是外部赋予的。

在实际开发中，应遵循 "单一数据源" 原则：同一数据不应同时由 state 和 props 管理。当需要跨多个组件共享状态时，可使用 Context API 或 Redux 等状态管理库，它们本质上是对 state 和 props 机制的扩展，而非替代。

掌握 state 和 props 的使用边界，是编写可维护 React 组件的基础，也是理解 React 单向数据流思想的核心。

