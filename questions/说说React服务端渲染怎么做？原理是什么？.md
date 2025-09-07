# 说说 React 服务端渲染怎么做？原理是什么？

## meta 元数据



```
{

&#x20; "id": "f1g2h3i4-j5k6-7890-lopq-1234567890rs",

&#x20; "type": "answer",

&#x20; "difficulty": "difficult",

&#x20; "tags": \["react", "SSR"]

}
```

## 答案 1：核心简洁的口语化回答

・服务端渲染（SSR）需搭建 Node 服务（如 Express），在服务端通过 ReactDOMServer 的 renderToString 或 renderToNodeStream 方法将组件转为 HTML 字符串

・客户端引入同一份组件代码，通过 ReactDOM.hydrate () 激活 HTML，绑定事件实现交互

・原理是服务端生成完整 HTML 响应，客户端复用 HTML 结构并补充交互能力，提升首屏加载速度和 SEO 表现

・需处理数据同步问题，确保服务端预取的数据能传递给客户端

・常见方案有 Next.js 等框架，简化 SSR 配置与实现流程

## 答案 2：口语化扩展回答

做 React 服务端渲染，首先得有个 Node 服务器，比如用 Express 搭建。核心是在服务端把 React 组件转换成 HTML 字符串，而不是像客户端渲染那样让浏览器去解析 JS 生成 DOM。具体来说，服务端会引入页面组件，用 ReactDOMServer 里的 renderToString 方法把组件渲染成 HTML，然后把这段 HTML 塞进一个模板里，作为响应返回给浏览器。

浏览器拿到这个 HTML 后，首屏内容能直接显示出来，不用等 JS 加载完，这就解决了首屏加载慢的问题。但这时候页面还不能交互，所以客户端还要加载同样的 React 代码，用 ReactDOM.hydrate () 方法去 "激活" 这个静态 HTML，给元素绑定事件监听器，让页面变得可交互。

这里有个关键是数据同步，服务端渲染前要先获取组件需要的数据，比如从接口拉取列表数据，渲染时把这些数据注入到 HTML 里，客户端初始化时再从 HTML 中读取这些数据，避免客户端重新请求导致的数据不一致。现在很多人用 Next.js 这类框架，它封装了 SSR 的复杂配置，能自动处理路由、数据预取这些事情，让开发更简单。总的来说，SSR 的核心就是 "服务端生成结构，客户端激活交互"，既保留了 React 的开发体验，又优化了首屏性能和 SEO。

## 答案 3：技术深度解析

### 一、服务端渲染（SSR）实现步骤

#### 1. 基础环境搭建



```
// 1. 安装核心依赖

// npm install react react-dom express

// 2. 简单的Express服务器（server.js）

const express = require('express');

const { renderToString } = require('react-dom/server');

const React = require('react');

const App = require('./src/App'); // 引入根组件

const path = require('path');

const app = express();

// 静态资源托管（客户端JS、CSS等）

app.use(express.static(path.join(\_\_dirname, 'build')));

// 处理所有路由请求

app.get('\*', (req, res) => {

&#x20; // 服务端渲染核心步骤

&#x20; const html = renderToString(React.createElement(App, { url: req.url }));

&#x20;&#x20;

&#x20; // 构建完整HTML响应

&#x20; const fullHtml = \`

&#x20;   \<!DOCTYPE html>

&#x20;   \<html>

&#x20;     \<head>

&#x20;       \<title>React SSR\</title>

&#x20;       \<link rel="stylesheet" href="/css/main.css">

&#x20;     \</head>

&#x20;     \<body>

&#x20;       \<div id="root">\${html}\</div>

&#x20;       \<!-- 客户端JS，用于激活交互 -->

&#x20;       \<script src="/client.bundle.js">\</script>

&#x20;     \</body>

&#x20;   \</html>

&#x20; \`;

&#x20;&#x20;

&#x20; res.send(fullHtml);

});

app.listen(3000, () => {

&#x20; console.log('SSR server running on port 3000');

});
```

#### 2. 客户端激活代码



```
// src/client.js

import React from 'react';

import { hydrate } from 'react-dom';

import App from './App';

// 用hydrate而非render，复用服务端生成的HTML

hydrate(

&#x20; \<App url={window.location.pathname} />,

&#x20; document.getElementById('root')

);
```

#### 3. 数据预取与同步



```
// 1. 组件定义数据获取方法

class Home extends React.Component {

&#x20; // 静态方法，用于服务端预取数据

&#x20; static async getInitialProps() {

&#x20;   const res = await fetch('https://api.example.com/data');

&#x20;   const data = await res.json();

&#x20;   return { data }; // 返回的数据会作为props传入组件

&#x20; }

&#x20; render() {

&#x20;   return \<div>{this.props.data.map(item => \<div key={item.id}>{item.name}\</div>)}\</div>;

&#x20; }

}

// 2. 服务端处理数据预取

app.get('\*', async (req, res) => {

&#x20; // 根据当前路由匹配组件

&#x20; const matchedComponent = matchRoute(req.url);

&#x20;&#x20;

&#x20; // 调用组件的getInitialProps获取数据

&#x20; const initialData = await matchedComponent.getInitialProps();

&#x20;&#x20;

&#x20; // 渲染组件时传入预取的数据

&#x20; const html = renderToString(

&#x20;   React.createElement(matchedComponent, { ...initialData, url: req.url })

&#x20; );

&#x20;&#x20;

&#x20; // 将数据注入HTML，供客户端使用

&#x20; const fullHtml = \`

&#x20;   \<!DOCTYPE html>

&#x20;   \<html>

&#x20;     \<head>

&#x20;       \<title>React SSR\</title>

&#x20;     \</head>

&#x20;     \<body>

&#x20;       \<div id="root">\${html}\</div>

&#x20;       \<!-- 数据注入窗口对象 -->

&#x20;       \<script>window.\_\_INITIAL\_DATA\_\_ = \${JSON.stringify(initialData)}\</script>

&#x20;       \<script src="/client.bundle.js">\</script>

&#x20;     \</body>

&#x20;   \</html>

&#x20; \`;

&#x20;&#x20;

&#x20; res.send(fullHtml);

});

// 3. 客户端使用预取数据

// src/client.js

hydrate(

&#x20; \<App&#x20;

&#x20;   url={window.location.pathname}

&#x20;   {...window.\_\_INITIAL\_DATA\_\_} // 接收服务端传递的数据

&#x20; />,

&#x20; document.getElementById('root')

);
```

#### 4. 构建配置（Webpack）

需要分别配置服务端和客户端的 Webpack 构建：



```
// 服务端Webpack配置（webpack.server.js）

module.exports = {

&#x20; target: 'node', // 目标环境为Node

&#x20; entry: './server.js',

&#x20; output: {

&#x20;   filename: 'server.bundle.js',

&#x20;   path: path.join(\_\_dirname, 'build')

&#x20; },

&#x20; // ...其他配置（Babel处理JSX等）

};

// 客户端Webpack配置（webpack.client.js）

module.exports = {

&#x20; target: 'web', // 目标环境为浏览器

&#x20; entry: './src/client.js',

&#x20; output: {

&#x20;   filename: 'client.bundle.js',

&#x20;   path: path.join(\_\_dirname, 'build/static')

&#x20; },

&#x20; // ...其他配置

};
```

### 二、SSR 核心原理

#### 1. 服务端渲染流程



1.  **请求处理**：客户端发送 HTTP 请求到 Node 服务器

2.  **数据预取**：服务器根据路由和组件需求，预先获取所需数据

3.  **组件渲染**：通过`renderToString`将 React 组件转换为 HTML 字符串

*   `renderToString()`：生成带 React 内部标记的 HTML，用于客户端 hydrate 识别

*   `renderToNodeStream()`：生成 HTML 流，适合大型应用，提升响应速度

1.  **HTML 组装**：将渲染后的 HTML、预取数据、客户端 JS 引用等组装成完整 HTML

2.  **响应发送**：将完整 HTML 返回给客户端，浏览器直接解析显示

#### 2. 客户端激活（Hydration）流程



1.  **HTML 解析**：浏览器接收 HTML 并快速渲染出首屏内容

2.  **JS 加载**：客户端加载 React 及业务 JS 代码

3.  **Hydrate 激活**：调用`hydrate()`方法：

*   复用已存在的 DOM 节点，避免重新创建

*   为 DOM 元素绑定事件监听器

*   建立虚拟 DOM 与真实 DOM 的映射关系

1.  **交互就绪**：激活完成后，页面具备完整交互能力

#### 3. 与客户端渲染（CSR）的核心区别



| 维度      | 客户端渲染（CSR）        | 服务端渲染（SSR）     |
| ------- | ----------------- | -------------- |
| HTML 来源 | 浏览器通过 JS 动态生成     | 服务器直接返回完整 HTML |
| 首屏时间    | 较长（需加载 JS 并执行）    | 较短（HTML 直接解析）  |
| 交互就绪时间  | 与首屏时间一致           | 需等待 JS 加载并激活后  |
| SEO 支持  | 差（爬虫可能无法执行 JS）    | 好（HTML 包含完整内容） |
| 服务器压力   | 小（仅提供静态资源）        | 大（需处理渲染和数据请求）  |
| 缓存策略    | 主要缓存 JS/CSS 等静态资源 | 可缓存渲染结果或部分组件   |

### 三、关键技术点与优化

#### 1. 数据同步机制



*   服务端预取的数据必须通过`window.__INITIAL_DATA__`等方式传递给客户端

*   客户端初始化时必须优先使用服务端数据，避免二次请求导致的数据不一致

*   复杂应用可使用 Redux/MobX 等状态管理库，服务端初始化 store 后序列化传递



```
// Redux数据同步示例

// 服务端

const store = createStore(reducer);

// 预取数据并更新store

await fetchAndDispatchData(store, req.url);

// 序列化store状态

const initialState = JSON.stringify(store.getState());

// 客户端

const initialState = window.\_\_INITIAL\_STATE\_\_;

const store = createStore(reducer, initialState); // 初始化客户端store
```

#### 2. 路由匹配



*   服务端和客户端必须使用同一路由配置（如 React Router）

*   服务端需根据`req.url`匹配对应的组件进行渲染



```
// 服务端路由匹配

import { matchPath, StaticRouter } from 'react-router-dom/server';

app.get('\*', (req, res) => {

&#x20; // 创建服务端路由上下文

&#x20; const context = {};

&#x20;&#x20;

&#x20; const html = renderToString(

&#x20;   \<StaticRouter location={req.url} context={context}>

&#x20;     \<App />

&#x20;   \</StaticRouter>

&#x20; );

&#x20;&#x20;

&#x20; // 处理重定向等路由动作

&#x20; if (context.url) {

&#x20;   return res.redirect(301, context.url);

&#x20; }

&#x20;&#x20;

&#x20; res.send(fullHtml);

});
```

#### 3. 性能优化策略



*   **组件拆分**：将频繁变化的组件与静态组件分离，静态部分可缓存

*   **流式渲染**：使用`renderToNodeStream`和`pipe`方法，边渲染边发送响应

*   **部分 hydration**：只激活页面中需要交互的部分，静态部分不进行 hydrate

*   **缓存机制**：


    *   缓存渲染结果（如对相同路由和数据的请求直接返回缓存的 HTML）

    *   缓存数据请求结果，减少重复接口调用

*   **代码分割**：服务端和客户端共享代码分割配置，避免冗余加载

#### 4. 常见问题及解决方案



*   **Hydration 不匹配**：服务端与客户端渲染结果不一致导致，需确保：


    *   两端使用相同的组件代码和数据

    *   避免在渲染阶段使用客户端特有 API（如`window`、`document`）

*   **性能开销大**：可采用：


    *   服务端渲染与客户端渲染混合使用（关键页面用 SSR）

    *   使用缓存减轻服务器压力

    *   采用边缘计算（如 Vercel、Netlify）分发渲染压力

*   **样式闪烁**：确保服务端正确引入 CSS，或使用 CSS-in-JS 的服务端渲染支持

### 四、主流框架与工具



1.  **Next.js**：React 官方推荐的 SSR 框架，提供：

*   基于文件系统的路由

*   `getServerSideProps`/`getStaticProps`等数据预取方法

*   自动代码分割和优化

*   支持静态生成（SSG）和增量静态再生（ISR）

1.  **Remix**：全栈 React 框架，特点：

*   嵌套路由设计，优化数据加载和渲染

*   基于 Fetch API 的加载状态管理

*   自动处理表单提交和重定向

1.  **Gatsby**：以静态生成（SSG）为主，也支持 SSR，适合内容型网站

### 总结

React 服务端渲染的核心是**服务端生成 HTML 结构，客户端激活交互能力**，通过这种方式平衡了首屏性能、SEO 友好性与 React 组件化开发体验。其实现需要解决数据同步、路由匹配、客户端激活等关键问题，而 Next.js 等框架大幅降低了 SSR 的实施难度。

在实际应用中，需根据项目特点（如首屏性能要求、SEO 重要性、服务器资源等）决定是否采用 SSR，或结合静态生成（SSG）等方案，构建最优的渲染策略。

