# 说说 Real DOM 和 Virtual DOM 的区别？优缺点？

## meta 元数据



```
{

&#x20; "id": "i1j2k3l4-m5n6-7890-pqrs-1234567890vw",

&#x20; "type": "answer",

&#x20; "difficulty": "easy",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

• **本质区别**：Real DOM 是浏览器中真实存在的 DOM 节点，是 HTML 元素的具体实现；Virtual DOM 是用 JavaScript 对象描述 DOM 结构的轻量级副本。

・**操作成本**：Real DOM 操作成本高，频繁操作会引发重排重绘；Virtual DOM 操作成本低，仅在 JS 层面处理。

・**更新方式**：Real DOM 直接更新，每次更新都会重新渲染；Virtual DOM 通过对比新旧对象计算差异，只更新变化部分。

・**Real DOM 优点**：浏览器原生支持，无需额外处理；缺点是性能开销大，频繁操作易卡顿。

・**Virtual DOM 优点**：减少不必要渲染，提升性能，跨平台兼容；缺点是存在额外计算成本和内存占用。

## 答案 2：口语化扩展回答

Real DOM 就是浏览器里实际存在的 DOM 节点，比如我们写的 div、p 标签，最终都会被浏览器解析成真实的 DOM 元素，它是页面渲染的基础。而 Virtual DOM 其实是个 JavaScript 对象，里面存着标签名、属性、子元素这些信息，相当于给真实 DOM 做了个 "快照"，但它只存在于 JS 内存里，不是真实的 DOM 节点。

从操作上来说，直接改 Real DOM 代价很高，因为浏览器每次修改都要重新计算布局、绘制页面，频繁操作的话页面很容易卡。而 Virtual DOM 因为是 JS 对象，修改起来很快，而且框架会先对比前后两个 Virtual DOM 的差异，只把变化的部分更新到真实 DOM 上，这样就能减少很多不必要的渲染。

不过 Real DOM 也不是全是缺点，它是浏览器原生支持的，不需要额外的处理步骤，简单的页面用起来很直接。而 Virtual DOM 虽然能优化性能，但对比差异需要消耗计算资源，对于特别简单的操作，可能反而不如直接操作 Real DOM 快。另外，Virtual DOM 的跨平台能力很有用，比如 React 用它既能渲染网页，又能开发手机应用，这是 Real DOM 做不到的。实际开发中，框架通常会用 Virtual DOM 来平衡开发效率和性能，但我们也得知道什么时候该用原生 DOM 操作更合适。

## 答案 3：技术深度解析

### 一、本质定义与结构差异

#### 1. Real DOM（真实 DOM）

Real DOM 是浏览器引擎解析 HTML 后生成的**树形结构对象**，是页面渲染和交互的基础。它直接对应页面中的元素，具有完整的 API 和属性。

**结构示例**：



```
\<div class="container">

&#x20; \<h1>Hello World\</h1>

&#x20; \<p>Real DOM Example\</p>

\</div>
```

对应的 Real DOM 结构（简化）：



```
{

&#x20; tagName: "DIV",

&#x20; attributes: { class: "container" },

&#x20; childNodes: \[

&#x20;   {

&#x20;     tagName: "H1",

&#x20;     childNodes: \[{ nodeType: 3, nodeValue: "Hello World" }]

&#x20;   },

&#x20;   {

&#x20;     tagName: "P",

&#x20;     childNodes: \[{ nodeType: 3, nodeValue: "Real DOM Example" }]

&#x20;   }

&#x20; ],

&#x20; // 大量原生方法和属性

&#x20; appendChild: function() {},

&#x20; removeChild: function() {},

&#x20; style: { ... },

&#x20; offsetWidth: 800,

&#x20; // ...其他数百个属性和方法

}
```

#### 2. Virtual DOM（虚拟 DOM）

Virtual DOM 是**用 JavaScript 对象模拟的 DOM 结构**，仅包含渲染所需的核心信息（标签名、属性、子节点等），不包含浏览器原生 API。

**结构示例**（React 元素）：



```
{

&#x20; \$\$typeof: Symbol(react.element),

&#x20; type: "div",

&#x20; props: {

&#x20;   className: "container",

&#x20;   children: \[

&#x20;     {

&#x20;       type: "h1",

&#x20;       props: { children: "Hello World" }

&#x20;     },

&#x20;     {

&#x20;       type: "p",

&#x20;       props: { children: "Virtual DOM Example" }

&#x20;     }

&#x20;   ]

&#x20; },

&#x20; key: null,

&#x20; ref: null

}
```

### 二、核心区别对比



| 维度            | Real DOM                                            | Virtual DOM                      |
| ------------- | --------------------------------------------------- | -------------------------------- |
| **存在形式**      | 浏览器内存中的 DOM 节点，与渲染引擎关联                              | JavaScript 对象，仅存在于 JS 内存中        |
| **API 复杂度**   | 提供数百个属性和方法（如`offsetHeight`、`getBoundingClientRect`） | 仅包含核心渲染信息（type、props、children 等） |
| **操作成本**      | 高（修改会触发重排重绘）                                        | 低（仅 JS 对象操作）                     |
| **更新方式**      | 直接更新，修改即反映到页面                                       | 先对比差异，再批量更新真实 DOM                |
| **跨平台性**      | 依赖浏览器环境，无法跨平台                                       | 与平台无关，可渲染到 Web、移动端等              |
| **内存占用**      | 高（包含大量冗余信息和方法）                                      | 低（仅保留必要信息）                       |
| **创建 / 销毁成本** | 高（涉及浏览器内部复杂处理）                                      | 低（普通 JS 对象创建）                    |

### 三、优缺点深度分析

#### 1. Real DOM 的优缺点

**优点**：



*   **原生支持**：浏览器直接解析和渲染，无需额外处理步骤

*   **实时性**：修改后立即反映到页面，适合简单场景

*   **完整 API**：提供丰富的 DOM 操作方法，满足复杂交互需求

*   **无性能损耗**：简单操作时，无虚拟 DOM 的比对开销

**缺点**：



*   **性能开销大**：


    *   每次修改可能触发重排（Reflow）和重绘（Repaint）

    *   重排会导致浏览器重新计算元素布局，耗时 expensive

*   **频繁操作卡顿**：多次连续修改会累积性能损耗

*   **开发效率低**：手动操作需处理兼容和优化，代码繁琐

*   **不可跨平台**：只能在浏览器环境中使用

#### 2. Virtual DOM 的优缺点

**优点**：



*   **性能优化**：


    *   通过 Diff 算法计算最小更新集，减少重排重绘

    *   批量处理 DOM 操作，降低性能损耗

*   **开发体验好**：


    *   声明式编程，无需手动操作 DOM

    *   框架自动处理优化，开发者专注业务逻辑

*   **跨平台能力**：


    *   同一套虚拟 DOM 可渲染到不同平台（如 React DOM、React Native）

*   **稳定性高**：


    *   避免手动操作 DOM 导致的错误

    *   统一的更新机制，减少兼容性问题

**缺点**：



*   **额外计算开销**：


    *   Diff 算法需要消耗 CPU 资源

    *   简单场景下性能可能不如直接操作真实 DOM

*   **内存占用**：


    *   需同时保存新旧两个虚拟 DOM 树，增加内存使用

*   **学习成本**：


    *   需理解框架的更新机制，否则可能写出低效代码

*   **非实时性**：


    *   更新需经过 Diff 和批量处理，存在微小延迟

### 四、Virtual DOM 的 Diff 算法原理

Virtual DOM 的性能优势依赖于高效的 Diff 算法，以 React 为例：



1.  **分层比对**：只比较同一层级的节点，不跨层级比对

2.  **类型判断**：节点类型不同则直接替换，不深入比对

3.  **列表优化**：通过`key`属性识别可复用节点，减少创建销毁操作

4.  **批量更新**：收集所有差异后，一次性更新到真实 DOM

**简化的 Diff 逻辑**：



```
function diff(oldVNode, newVNode) {

&#x20; const patches = \[];

&#x20;&#x20;

&#x20; // 节点类型不同，直接替换

&#x20; if (oldVNode.type !== newVNode.type) {

&#x20;   patches.push({ type: 'REPLACE', newVNode });

&#x20;   return patches;

&#x20; }

&#x20;&#x20;

&#x20; // 文本节点比对

&#x20; if (typeof newVNode === 'string') {

&#x20;   if (oldVNode !== newVNode) {

&#x20;     patches.push({ type: 'TEXT', content: newVNode });

&#x20;   }

&#x20;   return patches;

&#x20; }

&#x20;&#x20;

&#x20; // 属性比对

&#x20; const propsDiff = diffProps(oldVNode.props, newVNode.props);

&#x20; if (propsDiff.length) {

&#x20;   patches.push({ type: 'PROPS', props: propsDiff });

&#x20; }

&#x20;&#x20;

&#x20; // 递归比对子节点

&#x20; const childrenDiff = diffChildren(oldVNode.children, newVNode.children);

&#x20; patches.push(...childrenDiff);

&#x20;&#x20;

&#x20; return patches;

}

// 应用差异到真实DOM

function patch(el, patches) {

&#x20; patches.forEach(patch => {

&#x20;   switch (patch.type) {

&#x20;     case 'REPLACE':

&#x20;       el.parentNode.replaceChild(createElement(patch.newVNode), el);

&#x20;       break;

&#x20;     case 'PROPS':

&#x20;       applyProps(el, patch.props);

&#x20;       break;

&#x20;     // 处理其他类型差异...

&#x20;   }

&#x20; });

}
```

### 五、适用场景分析



1.  **优先使用 Real DOM 的场景**：

*   简单页面或单个 DOM 元素操作（如表单验证）

*   需要实时获取 DOM 信息（如元素尺寸、位置）

*   性能敏感的高频操作（如动画帧更新）

*   小型项目，不想引入框架开销

1.  **优先使用 Virtual DOM 的场景**：

*   复杂交互界面（如管理系统、电商平台）

*   频繁更新的列表（如数据表格、聊天记录）

*   跨平台开发（同时支持 Web 和移动端）

*   大型应用，需要统一状态管理和渲染逻辑

### 总结

Real DOM 是浏览器原生的 DOM 实现，直接与渲染引擎交互，适合简单场景但性能开销大；Virtual DOM 是 JS 对象模拟的 DOM，通过 Diff 算法优化更新，适合复杂应用且支持跨平台。

两者并非对立关系，Virtual DOM 最终仍需转换为 Real DOM 才能渲染页面。现代前端框架（如 React、Vue）通过 Virtual DOM 平衡了开发效率和性能，但在实际开发中，应根据场景选择合适的操作方式 —— 对于简单操作，直接使用 Real DOM 可能更高效；对于复杂应用，Virtual DOM 的优势则更为明显。

理解两者的区别和优缺点，有助于开发者在项目中做出合理的技术选择，避免陷入 "盲目依赖框架" 或 "过度优化原生" 的误区。

