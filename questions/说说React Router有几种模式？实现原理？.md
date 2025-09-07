# 说说 React Router 有几种模式？实现原理？

## meta 元数据



```
{

&#x20; "id": "g1h2i3j4-k5l6-7890-mnqr-1234567890st",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・React Router 主要有两种模式：**Hash 模式**和**History 模式**

・Hash 模式使用 URL 中的哈希（#）部分实现路由，如`http://example.com/#/home`，通过监听`hashchange`事件感知变化

・History 模式使用 HTML5 History API（`pushState`、`replaceState`）操作 URL，如`http://example.com/home`，通过监听`popstate`事件处理前进 / 后退

・Hash 模式无需后端配置，但 URL 包含 #；History 模式 URL 更美观，但需后端配合处理刷新请求，否则会 404

## 答案 2：口语化扩展回答

React Router 常用的有两种路由模式，分别是 Hash 模式和 History 模式，它们都是用来在单页应用中实现页面切换的，不用刷新整个页面。

Hash 模式很容易识别，就是 URL 里带个 #号，比如`http://test.com/#/user`，# 后面的部分就是哈希值。它的原理是通过监听浏览器的`hashchange`事件，当 #后面的内容变化时，就触发事件处理函数，然后根据新的哈希值渲染对应的组件。这种模式的好处是兼容性好，所有浏览器都支持，而且不需要后端做任何配置，因为 #后面的内容不会发送到服务器。不过缺点也明显，URL 里带个 #不够美观，而且有些场景下可能会有问题，比如 SEO 或者某些第三方工具处理。

History 模式用的是 HTML5 新增的 History API，URL 看起来就和普通网站一样，比如`http://test.com/user`。它通过`pushState`和`replaceState`这两个方法来改变 URL，不会触发页面刷新。不过这种模式需要监听`popstate`事件来处理用户的前进和后退操作。但它有个问题，就是当用户直接刷新页面或者从外部链接进入时，浏览器会真的去请求这个 URL，如果后端没有对应的路由配置，就会返回 404。所以用 History 模式必须让后端配合，把所有请求都转发到前端的入口页面，让前端来处理路由。

实际开发中，一般根据项目需求选择，比如对 URL 美观度要求高或者需要更好的 SEO，就用 History 模式，同时配置好后端；如果图简单或者兼容性要求高，就用 Hash 模式。

## 答案 3：技术深度解析

### 一、React Router 的两种核心模式

React Router 作为 React 生态中处理路由的核心库，主要提供两种路由模式，分别基于不同的浏览器 API 实现，适用于不同场景。

#### 1. Hash 模式（HashRouter）

**定义**：使用 URL 中的哈希（`#`）部分作为路由标识，哈希值的变化不会触发页面重新加载。

**URL 格式**：`http://example.com/#/path?query=1`



*   `#`后面的`/path?query=1`为哈希部分，不会被发送到服务器

#### 2. History 模式（BrowserRouter）

**定义**：基于 HTML5 History API 实现，使用标准的 URL 格式，通过 API 操作浏览器历史记录实现路由切换。

**URL 格式**：`http://example.com/path?query=1`



*   完整 URL 会被发送到服务器，需要后端配合处理

### 二、Hash 模式实现原理

#### 1. 核心 API 与事件

Hash 模式主要依赖浏览器的`location.hash`属性和`hashchange`事件：



```
// 哈希值操作

console.log(location.hash); // 获取当前哈希值（如"#/home"）

location.hash = "/about"; // 设置哈希值，会添加到历史记录
```



```
// 监听哈希变化事件

window.addEventListener("hashchange", (event) => {

&#x20; console.log("旧URL:", event.oldURL);

&#x20; console.log("新URL:", event.newURL);

&#x20; console.log("新哈希值:", location.hash);

&#x20; // 此处可执行路由匹配和组件更新逻辑

});
```

#### 2. React Router 中的 HashRouter 实现简化



```
class HashRouter extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   // 初始化路由状态（从当前哈希值解析）

&#x20;   this.state = {

&#x20;     currentPath: this.getHashPath()

&#x20;   };

&#x20; }

&#x20; // 从哈希值中提取路径（去除#）

&#x20; getHashPath() {

&#x20;   const hash = window.location.hash;

&#x20;   // 处理空哈希或仅#的情况

&#x20;   return hash.startsWith("#") ? hash.slice(1) || "/" : "/";

&#x20; }

&#x20; // 处理哈希变化的回调

&#x20; handleHashChange = () => {

&#x20;   const newPath = this.getHashPath();

&#x20;   this.setState({ currentPath: newPath });

&#x20; };

&#x20; componentDidMount() {

&#x20;   // 初始化时如果没有哈希值，设置默认路径

&#x20;   if (!window.location.hash) {

&#x20;     window.location.hash = "/";

&#x20;   }

&#x20;   // 监听哈希变化事件

&#x20;   window.addEventListener("hashchange", this.handleHashChange);

&#x20; }

&#x20; componentWillUnmount() {

&#x20;   // 移除事件监听

&#x20;   window.removeEventListener("hashchange", this.handleHashChange);

&#x20; }

&#x20; render() {

&#x20;   // 通过Context向子组件传递当前路径和导航方法

&#x20;   return (

&#x20;     \<RouterContext.Provider

&#x20;       value={{

&#x20;         path: this.state.currentPath,

&#x20;         push: (path) => { window.location.hash = path; },

&#x20;         replace: (path) => {&#x20;

&#x20;           // 使用replaceState替换当前历史记录，避免回退到上一个哈希

&#x20;           window.location.replace(\`#\${path}\`);

&#x20;         }

&#x20;       }}

&#x20;     \>

&#x20;       {this.props.children}

&#x20;     \</RouterContext.Provider>

&#x20;   );

&#x20; }

}
```

#### 3. 关键特性



*   **无需后端配置**：哈希部分不会发送到服务器，刷新页面时服务器仅收到`#`前的 URL

*   **兼容性**：支持所有现代浏览器及 IE8+

*   **局限性**：


    *   URL 包含`#`，不够美观

    *   哈希值会被包含在锚点跳转中，可能与页面内锚点冲突

    *   部分第三方服务（如微信分享）可能忽略哈希部分

### 三、History 模式实现原理

#### 1. 核心 API 与事件

History 模式基于 HTML5 History API，主要使用以下方法和事件：



```
// 修改历史记录（不会触发页面刷新）

history.pushState({ state: "home" }, "首页", "/home"); // 添加新记录

history.replaceState({ state: "about" }, "关于", "/about"); // 替换当前记录

// 监听历史记录变化（仅对前进/后退有效）

window.addEventListener("popstate", (event) => {

&#x20; console.log("历史状态变化:", event.state);

&#x20; console.log("当前URL:", window.location.pathname);

&#x20; // 此处可执行路由匹配和组件更新逻辑

});
```

> 注意：
>
> `pushState`
>
> 和
>
> `replaceState`
>
> 不会触发
>
> `popstate`
>
> 事件，需手动处理路由更新

#### 2. React Router 中的 BrowserRouter 实现简化



```
class BrowserRouter extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   this.state = {

&#x20;     currentPath: window.location.pathname

&#x20;   };

&#x20; }

&#x20; // 处理路径变化

&#x20; handlePathChange = (path, replace = false) => {

&#x20;   if (replace) {

&#x20;     // 替换当前历史记录

&#x20;     history.replaceState({ path }, "", path);

&#x20;   } else {

&#x20;     // 添加新历史记录

&#x20;     history.pushState({ path }, "", path);

&#x20;   }

&#x20;   // 手动更新状态（因为pushState不会触发popstate）

&#x20;   this.setState({ currentPath: path });

&#x20; };

&#x20; // 处理popstate事件（前进/后退按钮）

&#x20; handlePopState = (event) => {

&#x20;   this.setState({ currentPath: window.location.pathname });

&#x20; };

&#x20; componentDidMount() {

&#x20;   window.addEventListener("popstate", this.handlePopState);

&#x20; }

&#x20; componentWillUnmount() {

&#x20;   window.removeEventListener("popstate", this.handlePopState);

&#x20; }

&#x20; render() {

&#x20;   return (

&#x20;     \<RouterContext.Provider

&#x20;       value={{

&#x20;         path: this.state.currentPath,

&#x20;         push: (path) => this.handlePathChange(path, false),

&#x20;         replace: (path) => this.handlePathChange(path, true)

&#x20;       }}

&#x20;     \>

&#x20;       {this.props.children}

&#x20;     \</RouterContext.Provider>

&#x20;   );

&#x20; }

}
```

#### 3. 关键特性



*   **URL 美观**：使用标准 URL 格式，无`#`符号

*   **功能丰富**：可通过`state`参数存储额外路由信息

*   **局限性**：


    *   依赖 HTML5 API，不支持 IE9 及以下浏览器

    *   刷新页面时会真实请求服务器，需后端配置支持

    *   可能存在跨域限制

#### 4. 后端配置示例（避免 404 错误）

**Nginx 配置**：



```
server {

&#x20; listen 80;

&#x20; server\_name example.com;

&#x20; root /path/to/your/app;

&#x20; \# 所有请求都转发到index.html

&#x20; location / {

&#x20;   try\_files \$uri \$uri/ /index.html;

&#x20; }

}
```

**Node.js（Express）配置**：



```
const express = require('express');

const app = express();

const path = require('path');

// 静态资源托管

app.use(express.static(path.join(\_\_dirname, 'build')));

// 所有路由请求都返回index.html

app.get('\*', (req, res) => {

&#x20; res.sendFile(path.join(\_\_dirname, 'build', 'index.html'));

});

app.listen(3000);
```

### 四、两种模式的路由匹配原理

无论哪种模式，React Router 的核心路由匹配逻辑是一致的，主要通过以下组件实现：



1.  **Route 组件**：定义路径与组件的映射关系



```
\<Route path="/home" element={\<Home />} />
```



1.  **匹配算法**：

*   基于`path-to-regexp`库将路由路径转换为正则表达式

*   用转换后的正则匹配当前路径（Hash 模式取哈希部分，History 模式取`pathname`）

*   匹配成功则渲染对应的组件

1.  **嵌套路由实现**：

*   路由路径支持嵌套（如`/user`和`/user/profile`）

*   父组件通过`<Outlet />`渲染匹配的子路由组件



```
// 简化的Route匹配逻辑

function Route({ path, element, children }) {

&#x20; const { currentPath } = useContext(RouterContext);

&#x20; // 将路径转换为正则表达式

&#x20; const regex = pathToRegexp(path, \[], { end: false });

&#x20; // 检查当前路径是否匹配

&#x20; const isMatch = regex.test(currentPath);

&#x20;&#x20;

&#x20; if (isMatch) {

&#x20;   // 匹配成功，渲染对应的组件

&#x20;   return element;

&#x20; }

&#x20;&#x20;

&#x20; // 处理嵌套路由

&#x20; if (children) {

&#x20;   return children;

&#x20; }

&#x20;&#x20;

&#x20; return null;

}
```

### 五、模式选择建议



1.  **选择 Hash 模式的场景**：

*   快速开发原型，不想配置后端

*   需要支持 IE8 及以下浏览器

*   部署环境无法修改后端配置（如静态托管服务）

1.  **选择 History 模式的场景**：

*   对 URL 美观度要求高

*   需要更好的 SEO 支持（部分搜索引擎对哈希 URL 处理不佳）

*   需要使用路由状态（`state`）传递数据

*   项目有后端配合支持

1.  **其他路由模式**：

*   **MemoryRouter**：不依赖浏览器 URL，使用内存存储路由状态，适用于测试和非浏览器环境（如 React Native）

*   **StaticRouter**：服务端渲染专用，基于传入的`location`参数处理路由，不依赖浏览器 API

### 总结

React Router 的两种核心模式（Hash 和 History）分别基于浏览器的哈希机制和 HTML5 History API 实现，核心差异在于 URL 格式和对后端的依赖。Hash 模式简单易用但 URL 包含`#`，History 模式 URL 美观但需要后端配置。

理解两种模式的实现原理，有助于开发者根据项目需求选择合适的路由模式，并解决实际开发中遇到的路由问题（如 404 错误、刷新异常等）。在现代前端开发中，History 模式因更好的用户体验和 SEO 支持而被广泛采用，配合后端配置可实现理想的路由效果。

