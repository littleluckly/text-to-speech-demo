# 说说 React JSX 转换成真实 DOM 过程？

## meta 元数据



```
{

&#x20; "id": "d1e2f3g4-h5i6-7890-jklm-1234567890no",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・JSX 经 Babel 编译为 React.createElement () 函数调用，生成虚拟 DOM 对象

・虚拟 DOM 是描述 DOM 结构的 JavaScript 对象，包含标签名、属性和子元素等信息

・React 通过协调（Reconciliation）算法对比新旧虚拟 DOM，找出差异

・最后通过 ReactDOM.render () 将差异部分转换为真实 DOM 并挂载到页面

## 答案 2：口语化扩展回答

JSX 转换成真实 DOM 的过程可以分成几个步骤。首先，我们写的 JSX 代码其实是一种语法糖，浏览器不能直接识别，所以需要用 Babel 这类工具把它编译成 React.createElement () 的函数调用。这个函数会生成一个 JavaScript 对象，也就是虚拟 DOM，它里面包含了标签名称、属性、子元素等描述 DOM 结构的信息。

接下来，React 会处理这个虚拟 DOM。如果是首次渲染，就直接根据虚拟 DOM 的结构来创建对应的真实 DOM 元素。如果是后续更新，React 会拿新生成的虚拟 DOM 和之前的旧虚拟 DOM 进行比较，这个比较过程用的是 React 的协调算法，能高效找出两者的差异。

找到差异后，React 不会直接全部替换旧的 DOM，而是只把有变化的部分转换成真实 DOM 并更新到页面上。最后通过 ReactDOM.render () 方法，把生成的真实 DOM 挂载到页面中指定的容器节点上，这样用户就能看到渲染后的内容了。整个过程通过虚拟 DOM 做中间层，减少了直接操作真实 DOM 的开销，提高了渲染效率。

## 答案 3：技术深度解析

### 一、JSX 的编译阶段

JSX 是 React 提供的语法糖，本身不能被 JavaScript 引擎直接解析，需要通过编译器（如 Babel）转换为合法的 JavaScript 代码。

**转换示例**：



```
// 原始JSX

\<div className="container">

&#x20; \<h1>Hello, React\</h1>

&#x20; \<p>JSX to DOM\</p>

\</div>
```

经 Babel 编译后：



```
// 编译后的代码

React.createElement(

&#x20; "div",  // 标签名或组件

&#x20; { className: "container" },  // 属性对象

&#x20; // 子元素（同样是createElement调用）

&#x20; React.createElement("h1", null, "Hello, React"),

&#x20; React.createElement("p", null, "JSX to DOM")

);
```

**编译规则**：



*   标签名：HTML 标签用字符串表示，自定义组件用标识符

*   属性：JSX 中的`className`对应 DOM 的`class`，`htmlFor`对应`for`（避免与 JavaScript 关键字冲突）

*   表达式：`{}`中的表达式会被直接嵌入

*   子元素：多个子元素作为后续参数传递

### 二、虚拟 DOM 的生成

React.createElement () 函数执行后返回的是**虚拟 DOM 对象（React Element）**，它是对真实 DOM 的轻量级描述。

**虚拟 DOM 结构示例**：



```
{

&#x20; \$\$typeof: Symbol(react.element),  // React元素标识

&#x20; type: "div",  // 元素类型

&#x20; key: null,    // 用于列表diff的标识

&#x20; ref: null,    // 用于访问真实DOM

&#x20; props: {      // 属性集合

&#x20;   className: "container",

&#x20;   children: \[  // 子元素数组

&#x20;     {

&#x20;       \$\$typeof: Symbol(react.element),

&#x20;       type: "h1",

&#x20;       props: { children: "Hello, React" },

&#x20;       // ...其他属性

&#x20;     },

&#x20;     {

&#x20;       \$\$typeof: Symbol(react.element),

&#x20;       type: "p",

&#x20;       props: { children: "JSX to DOM" },

&#x20;       // ...其他属性

&#x20;     }

&#x20;   ]

&#x20; },

&#x20; \_owner: null,  // 关联的组件实例

&#x20; // ...其他内部属性

}
```

**虚拟 DOM 的特点**：



*   纯 JavaScript 对象，操作成本远低于真实 DOM

*   包含完整的 DOM 结构描述信息

*   具有不可变性，更新时会创建新对象而非修改旧对象

### 三、协调（Reconciliation）过程

协调是 React 对比新旧虚拟 DOM 树、找出差异的过程，核心是`reconcileChildren`函数。

**协调算法要点**：



1.  **分层比较**：只比较同一层级的节点（如前文 React diff 原理所述）

2.  **类型判断**：

*   类型不同：直接标记为 "替换" 操作

*   类型相同：比较属性差异，递归处理子节点

1.  **列表处理**：通过`key`属性匹配可复用节点，减少 DOM 操作

**简化的协调逻辑**：



```
function reconcileChildren(oldVNode, newVNode) {

&#x20; const patches = \[];

&#x20;&#x20;

&#x20; if (newVNode === null) {

&#x20;   // 新节点不存在，标记删除

&#x20;   patches.push({ type: 'REMOVE', vnode: oldVNode });

&#x20;   return patches;

&#x20; }

&#x20;&#x20;

&#x20; if (typeof oldVNode !== typeof newVNode) {

&#x20;   // 类型不同，标记替换

&#x20;   patches.push({ type: 'REPLACE', oldVNode, newVNode });

&#x20;   return patches;

&#x20; }

&#x20;&#x20;

&#x20; if (typeof newVNode === 'string' || typeof newVNode === 'number') {

&#x20;   // 文本节点比较

&#x20;   if (oldVNode !== newVNode) {

&#x20;     patches.push({ type: 'TEXT', content: newVNode });

&#x20;   }

&#x20;   return patches;

&#x20; }

&#x20;&#x20;

&#x20; if (newVNode.type !== oldVNode.type) {

&#x20;   // 元素类型不同，标记替换

&#x20;   patches.push({ type: 'REPLACE', oldVNode, newVNode });

&#x20;   return patches;

&#x20; }

&#x20;&#x20;

&#x20; // 类型相同，比较属性

&#x20; const propsPatches = compareProps(oldVNode.props, newVNode.props);

&#x20; if (propsPatches.length) {

&#x20;   patches.push({ type: 'PROPS', props: propsPatches });

&#x20; }

&#x20;&#x20;

&#x20; // 递归处理子节点

&#x20; const childrenPatches = reconcileChildrenArray(

&#x20;   oldVNode.props.children,

&#x20;   newVNode.props.children

&#x20; );

&#x20; patches.push(...childrenPatches);

&#x20;&#x20;

&#x20; return patches;

}
```

### 四、真实 DOM 的生成与更新

协调过程产生的差异（patches）会被传递到**提交阶段（Commit）**，由 ReactDOM 负责将差异应用到真实 DOM。

#### 1. 首次渲染流程



*   调用`ReactDOM.render(vnode, container)`启动渲染

*   执行`mountComponent`方法，根据虚拟 DOM 创建真实 DOM：



```
function mountElement(vnode, container) {

&#x20; const { type, props } = vnode;

&#x20; // 创建真实DOM元素

&#x20; const el = document.createElement(type);

&#x20;&#x20;

&#x20; // 设置属性

&#x20; setProps(el, props);

&#x20;&#x20;

&#x20; // 处理子节点

&#x20; if (Array.isArray(props.children)) {

&#x20;   props.children.forEach(child => {

&#x20;     // 递归挂载子节点

&#x20;     mountElement(child, el);

&#x20;   });

&#x20; } else if (typeof props.children === 'string' || typeof props.children === 'number') {

&#x20;   // 文本节点

&#x20;   el.textContent = props.children;

&#x20; }

&#x20;&#x20;

&#x20; // 将元素添加到容器

&#x20; container.appendChild(el);

&#x20;&#x20;

&#x20; // 存储真实DOM引用（用于后续更新）

&#x20; vnode.el = el;

}
```

#### 2. 更新渲染流程



*   当组件状态变化时，重新生成虚拟 DOM

*   对比新旧虚拟 DOM 得到差异补丁

*   执行`updateComponent`方法，只更新有差异的部分：



```
function patch(el, patches) {

&#x20; patches.forEach(patch => {

&#x20;   switch (patch.type) {

&#x20;     case 'REPLACE':

&#x20;       // 替换节点

&#x20;       el.parentNode.replaceChild(createElement(patch.newVNode), el);

&#x20;       break;

&#x20;     case 'PROPS':

&#x20;       // 更新属性

&#x20;       patch.props.forEach(({ key, value }) => {

&#x20;         if (value === null) {

&#x20;           el.removeAttribute(key);

&#x20;         } else {

&#x20;           el.setAttribute(key, value);

&#x20;         }

&#x20;       });

&#x20;       break;

&#x20;     case 'TEXT':

&#x20;       // 更新文本

&#x20;       el.textContent = patch.content;

&#x20;       break;

&#x20;     case 'REMOVE':

&#x20;       // 删除节点

&#x20;       el.parentNode.removeChild(el);

&#x20;       break;

&#x20;     // 处理其他类型的补丁...

&#x20;   }

&#x20; });

}
```

### 五、关键优化点



1.  **批处理更新**：React 会将多次 DOM 更新合并为一次，减少重排重绘

2.  **事务机制**：确保 DOM 更新过程的原子性，避免中间状态暴露

3.  \*\* Fiber 架构 \*\*（React 16+）：

*   将渲染工作拆分为小单元，可中断、恢复

*   优先处理高优先级任务（如用户输入）

*   提高大型应用的响应性

### 总结

JSX 到真实 DOM 的转换过程是 React 的核心工作流，可概括为：



1.  语法转换：JSX → React.createElement () 调用

2.  虚拟 DOM 生成：createElement () → 虚拟 DOM 对象

3.  差异计算：新旧虚拟 DOM → 差异补丁

4.  DOM 操作：差异补丁 → 真实 DOM 更新

这一过程通过虚拟 DOM 作为中间层，结合高效的协调算法，大幅减少了直接操作真实 DOM 的性能开销，是 React 高性能的重要保障。理解这一流程有助于开发者写出更符合 React 渲染机制的代码，避免常见的性能问题。

