# 说说你在 React 项目是如何捕获错误的？

## meta 元数据



```
{

&#x20; "id": "r3e4a5c6-t7e8-7890-errr-1234567890ab",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・使用 React 内置的 Error Boundary 组件捕获渲染阶段的 JS 错误，防止应用崩溃

・借助 try/catch 语句处理事件处理函数等非渲染阶段的同步错误

・对异步操作（如 API 请求），通过.catch () 或 try/catch（配合 async/await）捕获错误

・利用 window.onerror 和 window.addEventListener ('unhandledrejection') 捕获全局未处理错误

・结合 Sentry 等监控工具，收集并分析生产环境中的错误信息

## 答案 2：口语化扩展回答

在 React 项目里捕获错误得分场景来处理。最常用的是 Error Boundary，这是 React 官方提供的组件，能把渲染时出的错兜住，不会让整个应用白屏，还能显示友好的错误提示。不过要注意，它管不了事件处理里的错，也管不了异步代码和服务端渲染的错。

对于事件处理函数里的错误，比如按钮点击触发的逻辑，就得用 try/catch 来抓，因为这些代码不在 React 的渲染流程里。异步操作像调接口，用 fetch 或者 axios 的话，一般会在.then 后面加.catch，要是用 async/await 写法，就把 await 那句包在 try 里，后面跟 catch。

全局层面也不能漏，window.onerror 可以抓一些 JS 运行时错误，unhandledrejection 事件能处理没被捕获的 Promise 错误，比如忘了写.catch 的异步操作。实际开发中，还会集成 Sentry 这类工具，自动收集错误信息，包括调用栈、用户操作路径这些，方便排查问题。另外，开发环境用 ESLint 提前发现代码问题，也是减少错误的好办法。

## 答案 3：技术深度解析

### React 项目错误捕获体系

在 React 应用中，错误可能发生在不同阶段和场景，需要建立多层次的错误捕获体系。完整的错误处理策略应覆盖：渲染阶段错误、事件处理错误、异步操作错误、全局未捕获错误等场景。

### 1. 渲染阶段错误捕获：Error Boundary

#### 原理与实现

Error Boundary 是 React 16 引入的特殊组件，利用了 React 组件生命周期方法`componentDidCatch`（类组件）或`static getDerivedStateFromError`来捕获子组件树中的渲染错误。



```
// 基础Error Boundary实现

class ErrorBoundary extends React.Component {

&#x20; constructor(props) {

&#x20;   super(props);

&#x20;   // 初始化状态，用于标记是否发生错误

&#x20;   this.state = { hasError: false, error: null, errorInfo: null };

&#x20; }

&#x20; // 静态方法，用于更新错误状态

&#x20; // 当子组件抛出错误时触发，返回的对象会更新组件状态

&#x20; static getDerivedStateFromError(error) {

&#x20;   return { hasError: true, error };

&#x20; }

&#x20; // 用于捕获错误并记录错误信息

&#x20; // 可以在这里发送错误日志到服务端

&#x20; componentDidCatch(error, errorInfo) {

&#x20;   this.setState({ errorInfo });

&#x20;   // 记录错误日志

&#x20;   console.error("Error caught by ErrorBoundary:", error, errorInfo);

&#x20;   // 实际项目中可以发送到错误监控服务

&#x20;   // logErrorToService(error, errorInfo, this.props.componentName);

&#x20; }

&#x20; // 重置错误状态的方法

&#x20; resetError = () => {

&#x20;   this.setState({ hasError: false, error: null, errorInfo: null });

&#x20; };

&#x20; render() {

&#x20;   // 如果发生错误，显示错误 fallback UI

&#x20;   if (this.state.hasError) {

&#x20;     // 可以自定义错误展示内容

&#x20;     return this.props.fallback || (

&#x20;       \<div className="error-boundary">

&#x20;         \<h2>Something went wrong.\</h2>

&#x20;         \<button onClick={this.resetError}>Try again\</button>

&#x20;         {/\* 开发环境可以显示详细错误信息 \*/}

&#x20;         {process.env.NODE\_ENV === 'development' && (

&#x20;           \<details style={{ whiteSpace: 'pre-wrap' }}>

&#x20;             {this.state.error && this.state.error.toString()}

&#x20;             \<br />

&#x20;             {this.state.errorInfo?.componentStack}

&#x20;           \</details>

&#x20;         )}

&#x20;       \</div>

&#x20;     );

&#x20;   }

&#x20;   // 没有错误时，正常渲染子组件

&#x20;   return this.props.children;

&#x20; }

}
```

#### 使用场景与限制



*   **适用场景**：捕获子组件树中的渲染错误、生命周期方法中的错误、子组件构造函数中的错误

*   **不适用场景**：


    *   自身组件的错误（只能捕获子组件错误）

    *   事件处理函数中的错误（不属于渲染流程）

    *   异步代码（如 setTimeout、Promise 回调）

    *   服务端渲染过程中的错误

#### 最佳实践



*   按功能模块 granular 部署 Error Boundary，而非全局一个

*   提供用户可操作的错误恢复机制（如重置按钮）

*   区分开发 / 生产环境的错误展示内容

*   结合错误监控服务记录错误详情

### 2. 事件处理与同步代码错误：try/catch

React 不会为事件处理函数中的错误提供特殊处理，需要使用原生 try/catch 语句。



```
class UserProfile extends React.Component {

&#x20; handleDelete = async (userId) => {

&#x20;   try {

&#x20;     // 同步操作

&#x20;     this.validateUserPermission();

&#x20;     // 异步操作

&#x20;     await userService.deleteUser(userId);

&#x20;     this.setState({ success: true });

&#x20;   } catch (error) {

&#x20;     // 处理错误

&#x20;     this.setState({ error: error.message });

&#x20;     // 记录错误日志

&#x20;     console.error("Failed to delete user:", error);

&#x20;   }

&#x20; };

&#x20; validateUserPermission = () => {

&#x20;   // 权限验证逻辑

&#x20;   if (!this.props.hasPermission) {

&#x20;     // 主动抛出错误

&#x20;     throw new Error("You don't have permission to delete users");

&#x20;   }

&#x20; };

&#x20; render() {

&#x20;   return (

&#x20;     \<div>

&#x20;       {this.state.error && \<div className="error">{this.state.error}\</div>}

&#x20;       \<button onClick={() => this.handleDelete(this.props.userId)}>

&#x20;         Delete User

&#x20;       \</button>

&#x20;     \</div>

&#x20;   );

&#x20; }

}
```

### 3. 异步操作错误处理

#### Promise 链式调用



```
fetchUserData(userId)

&#x20; .then(response => {

&#x20;   if (!response.ok) {

&#x20;     // 处理HTTP错误状态

&#x20;     throw new Error(\`HTTP error! status: \${response.status}\`);

&#x20;   }

&#x20;   return response.json();

&#x20; })

&#x20; .then(data => {

&#x20;   this.setState({ userData: data });

&#x20; })

&#x20; .catch(error => {

&#x20;   // 捕获整个调用链中的错误

&#x20;   this.setState({ error: error.message });

&#x20;   logErrorToService(error, 'fetchUserData');

&#x20; });
```

#### Async/Await 语法



```
const loadUserPosts = async () => {

&#x20; try {

&#x20;   this.setState({ loading: true });

&#x20;   const response = await fetch(\`/api/users/\${this.props.userId}/posts\`);

&#x20;  &#x20;

&#x20;   if (!response.ok) {

&#x20;     throw new Error(\`Failed to fetch posts: \${response.statusText}\`);

&#x20;   }

&#x20;  &#x20;

&#x20;   const posts = await response.json();

&#x20;   this.setState({ posts, loading: false });

&#x20; } catch (error) {

&#x20;   this.setState({&#x20;

&#x20;     error: 'Failed to load posts. Please try again later.',&#x20;

&#x20;     loading: false&#x20;

&#x20;   });

&#x20;   logErrorToService(error, 'loadUserPosts');

&#x20; }

};
```

### 4. 全局错误捕获

用于捕获应用中未被局部处理的错误，作为最后一道防线。

#### 全局 JS 错误



```
// 捕获同步和大部分异步错误

window.onerror = (message, source, lineno, colno, error) => {

&#x20; console.error("Global error caught:", message, error);

&#x20; // 发送到错误监控服务

&#x20; logErrorToService(error, 'window.onerror');

&#x20; // 返回true表示已处理，不会显示默认错误提示

&#x20; return true;

};
```

#### 未处理的 Promise 拒绝



```
// 捕获未处理的Promise拒绝

window.addEventListener('unhandledrejection', (event) => {

&#x20; console.error("Unhandled promise rejection:", event.reason);

&#x20; // 发送到错误监控服务

&#x20; logErrorToService(event.reason, 'unhandledrejection');

&#x20; // 阻止默认处理（如浏览器控制台显示错误）

&#x20; event.preventDefault();

});
```

#### React 18 中的全局错误处理

React 18 提供了`reportError`方法，可用于向 React 错误边界报告错误：



```
import { reportError } from 'react-dom';

// 在任何地方捕获到错误但无法处理时

try {

&#x20; // 某些可能出错的操作

} catch (error) {

&#x20; // 报告给React，会触发最近的Error Boundary

&#x20; reportError(error);

&#x20; // 可以同时进行其他处理

&#x20; showUserFriendlyMessage();

}
```

### 5. 错误监控与上报

在生产环境中，需要将错误信息收集并上报到监控系统（如 Sentry、Datadog 等）。



```
// 错误上报工具函数示例

const logErrorToService = async (error, context) => {

&#x20; if (process.env.NODE\_ENV !== 'production') {

&#x20;   return; // 开发环境不发送

&#x20; }

&#x20;&#x20;

&#x20; try {

&#x20;   // 收集错误详情

&#x20;   const errorData = {

&#x20;     message: error.message,

&#x20;     stack: error.stack,

&#x20;     context: context, // 错误发生的上下文信息

&#x20;     user: {

&#x20;       id: getUserID(), // 当前用户ID

&#x20;       username: getUsername()

&#x20;     },

&#x20;     url: window.location.href,

&#x20;     userAgent: navigator.userAgent,

&#x20;     timestamp: new Date().toISOString()

&#x20;   };

&#x20;  &#x20;

&#x20;   // 发送到错误监控服务

&#x20;   await fetch('/api/log-error', {

&#x20;     method: 'POST',

&#x20;     headers: { 'Content-Type': 'application/json' },

&#x20;     body: JSON.stringify(errorData),

&#x20;     // 确保错误日志请求不会影响主要用户体验

&#x20;     keepalive: true

&#x20;   });

&#x20; } catch (reportError) {

&#x20;   console.error("Failed to report error:", reportError);

&#x20; }

};
```

### 6. 特殊场景处理

#### 第三方组件错误

对于可能不稳定的第三方组件，使用 Error Boundary 隔离：



```
\<ErrorBoundary fallback={\<AlternativeUI />} componentName="ThirdPartyChart">

&#x20; \<ThirdPartyChart data={chartData} />

\</ErrorBoundary>
```

#### 服务器端渲染 (SSR) 错误

在 Next.js 等 SSR 框架中，使用`getServerSideProps`的错误处理：



```
export async function getServerSideProps(context) {

&#x20; try {

&#x20;   const data = await fetchSomeData(context.params.id);

&#x20;   return { props: { data } };

&#x20; } catch (error) {

&#x20;   // 记录服务器端错误

&#x20;   console.error("SSR error:", error);

&#x20;   // 返回错误页面

&#x20;   return {

&#x20;     notFound: true, // 或返回错误页面组件

&#x20;     // 或 { props: { error: error.message } }

&#x20;   };

&#x20; }

}
```

### 错误处理最佳实践



1.  **分层防御**：结合局部处理（try/catch）、组件级处理（Error Boundary）和全局处理

2.  **用户体验优先**：提供清晰的错误提示和恢复操作，避免技术术语

3.  **开发 / 生产环境区分**：开发环境显示详细错误信息，生产环境显示友好提示

4.  **错误上下文**：记录错误发生时的用户操作、设备信息、网络状态等上下文

5.  **避免错误隐藏**：不要空 catch 块，至少记录错误日志

6.  **监控与告警**：建立错误监控系统，设置关键错误告警机制

7.  **错误恢复机制**：尽可能提供错误恢复选项，减少用户操作中断

通过建立完善的错误捕获体系，可以显著提升应用的稳定性和用户体验，同时为开发团队提供及时的错误反馈，加速问题解决。

