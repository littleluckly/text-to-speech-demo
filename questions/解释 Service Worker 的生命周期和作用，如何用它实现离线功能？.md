# 解释 Service Worker 的生命周期和作用，如何用它实现离线功能？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ba",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["浏览器", "缓存"]

}
```

## 答案 1：核心简洁的口语化回答

・Service Worker 生命周期包括注册、安装、激活、运行 / 等待、销毁阶段。注册是让浏览器识别并安装；安装阶段缓存关键资源；激活阶段清理旧缓存；运行时拦截请求并管理缓存；不再使用时被销毁。

・作用：拦截网络请求、管理缓存、实现离线访问、推送通知、后台同步等，是 PWA 的核心技术。

・实现离线功能：注册 Service Worker 后，在安装阶段缓存静态资源；激活阶段处理缓存更新；拦截请求时，若网络可用则请求并更新缓存，若离线则返回缓存资源。

## 答案 2：口语化扩展回答

Service Worker 是运行在浏览器后台的独立脚本，生命周期比较清晰。首先得在页面里注册它，告诉浏览器 Service Worker 脚本的位置，浏览器会在后台悄悄下载并安装。安装的时候，我们可以指定要缓存的资源，比如 HTML、CSS、JS 这些静态文件，要是缓存成功，就说明安装完成了。

接下来是激活阶段，这时候可以清理之前版本的旧缓存，避免冲突，然后 Service Worker 就正式开始工作了。它能一直运行，即使页面关闭也可能保持活跃，直到被浏览器回收或者更新。

它的作用可不少，最核心的是能拦截网页发出的请求，决定是从缓存拿资源还是去服务器请求，这样就能实现离线功能。比如用户没网的时候，打开页面还能看到之前缓存的内容。另外，它还支持推送通知，就算页面没打开，也能给用户发消息，还有后台同步功能，等网络恢复了把离线时的操作同步到服务器。

用它实现离线功能，步骤大概是：先注册 Service Worker，安装时缓存好首屏需要的资源；激活时处理好缓存的版本管理；然后在拦截请求的阶段，判断如果有网络，就去请求新资源并更新缓存，如果没网，就直接返回之前缓存的资源，这样用户离线时也能正常访问页面了。

## 答案 3：技术深度解析

### 1. Service Worker 的生命周期

Service Worker 是运行在浏览器后台的**独立线程脚本**，与页面无关，其生命周期完全由浏览器控制，主要包括以下阶段：

#### 1.1 注册（Registration）



*   **触发时机**：通常在页面加载完成后，通过 JavaScript 代码主动注册。

*   **核心操作**：


    *   调用`navigator.serviceWorker.register(url, { scope })`指定 Service Worker 脚本路径和作用域（控制的页面范围）。

    *   浏览器下载脚本并进行解析，若脚本语法错误则注册失败。

*   **示例代码**：



```
if ('serviceWorker' in navigator) {

&#x20; window.addEventListener('load', () => {

&#x20;   navigator.serviceWorker.register('/sw.js', { scope: '/' })

&#x20;     .then(registration => {

&#x20;       console.log('Service Worker注册成功，作用域：', registration.scope);

&#x20;     })

&#x20;     .catch(err => {

&#x20;       console.log('Service Worker注册失败：', err);

&#x20;     });

&#x20; });

}
```

#### 1.2 安装（Install）



*   **触发时机**：注册成功后，浏览器首次执行 Service Worker 脚本时触发。

*   **核心操作**：


    *   通常用于缓存关键静态资源（如 HTML、CSS、JS、图片等），确保离线可用。

    *   通过`event.waitUntil(promise)`延长安装阶段，直至缓存完成；若 Promise reject 则安装失败。

*   **示例代码**：



```
// sw.js

const CACHE\_NAME = 'my-cache-v1';

const INITIAL\_CACHES = \[

&#x20; '/',

&#x20; '/index.html',

&#x20; '/styles.css',

&#x20; '/app.js',

&#x20; '/logo.png'

];

self.addEventListener('install', (event) => {

&#x20; // 等待所有资源缓存完成后再完成安装

&#x20; event.waitUntil(

&#x20;   caches.open(CACHE\_NAME)

&#x20;     .then(cache => cache.addAll(INITIAL\_CACHES)) // 缓存初始资源

&#x20;     .then(() => self.skipWaiting()) // 强制激活新SW（跳过等待状态）

&#x20; );

});
```

#### 1.3 等待（Waiting）



*   **触发时机**：若存在已激活的旧版本 Service Worker，新 SW 安装成功后进入等待状态。

*   **状态转换**：


    *   旧 SW 控制的所有页面关闭后，新 SW 自动激活。

    *   可通过`self.skipWaiting()`强制新 SW 立即激活（需在 install 事件中调用）。

#### 1.4 激活（Activate）



*   **触发时机**：新 SW 进入激活状态（旧 SW 被替换或首次安装）。

*   **核心操作**：


    *   清理旧版本缓存（避免缓存膨胀和版本冲突）。

    *   通过`self.clients.claim()`让新 SW 立即控制所有打开的页面（否则需刷新页面才生效）。

*   **示例代码**：



```
self.addEventListener('activate', (event) => {

&#x20; event.waitUntil(

&#x20;   // 删除旧版本缓存

&#x20;   caches.keys().then(cacheNames => {

&#x20;     return Promise.all(

&#x20;       cacheNames.filter(name => name !== CACHE\_NAME)

&#x20;         .map(name => caches.delete(name))

&#x20;     );

&#x20;   }).then(() => self.clients.claim()) // 立即控制所有页面

&#x20; );

});
```

#### 1.5 运行 / 拦截（Fetch）



*   **触发时机**：激活后，SW 开始监听页面发出的`fetch`请求（在其作用域内）。

*   **核心操作**：


    *   通过`fetch`事件拦截请求，自定义响应策略（如从缓存返回、请求网络并更新缓存等）。

    *   是实现离线功能、缓存优先加载的核心阶段。

*   **示例代码**：



```
self.addEventListener('fetch', (event) => {

&#x20; // 拦截请求并返回缓存或网络资源

&#x20; event.respondWith(

&#x20;   caches.match(event.request) // 先查询缓存

&#x20;     .then(cachedResponse => {

&#x20;       // 缓存命中则返回缓存，同时后台更新缓存

&#x20;       const fetchPromise = fetch(event.request).then(networkResponse => {

&#x20;         caches.open(CACHE\_NAME).then(cache => {

&#x20;           cache.put(event.request, networkResponse.clone()); // 更新缓存

&#x20;         });

&#x20;         return networkResponse;

&#x20;       });

&#x20;       // 缓存未命中则返回网络请求结果

&#x20;       return cachedResponse || fetchPromise;

&#x20;     })

&#x20; );

});
```

#### 1.6 销毁（Terminate）



*   **触发时机**：Service Worker 长期闲置（通常 30 秒内无活动）或被新版本 SW 替换时。

*   **特点**：销毁后不会主动重启，需等待页面再次请求或事件触发（如推送通知）。

### 2. Service Worker 的核心作用

#### 2.1 离线资源访问



*   拦截网络请求，在离线时返回缓存的静态资源，确保页面在无网络环境下可访问。

#### 2.2 缓存策略自定义



*   支持多种缓存策略（如缓存优先、网络优先、后台更新等），灵活控制资源加载方式。

#### 2.3 推送通知（Push Notifications）



*   即使页面关闭，也能通过服务器推送消息触发通知，提升用户粘性（需配合 Push API）。

#### 2.4 后台同步（Background Sync）



*   缓存用户离线时的操作（如表单提交），待网络恢复后自动同步到服务器。

#### 2.5 流量与性能优化



*   减少重复网络请求，通过缓存加速资源加载，降低服务器压力。

### 3. 利用 Service Worker 实现离线功能的完整流程

以 “离线访问静态网站” 为例，实现步骤如下：

#### 3.1 准备静态资源与页面



*   创建基础 HTML、CSS、JS 文件（如`index.html`、`styles.css`、`app.js`）。

*   确保资源路径与 Service Worker 缓存路径一致。

#### 3.2 编写 Service Worker 脚本（sw.js）



```
// 1. 定义缓存名称（含版本号，便于更新）

const CACHE\_NAME = 'static-cache-v2';

const OFFLINE\_URL = '/offline.html'; // 离线时的备用页面

// 2. 安装阶段：缓存关键资源和离线备用页

self.addEventListener('install', (event) => {

&#x20; event.waitUntil(

&#x20;   caches.open(CACHE\_NAME)

&#x20;     .then(cache => {

&#x20;       return cache.addAll(\[

&#x20;         '/',

&#x20;         '/index.html',

&#x20;         '/styles.css',

&#x20;         '/app.js',

&#x20;         '/logo.png',

&#x20;         OFFLINE\_URL // 缓存离线页面

&#x20;       ]);

&#x20;     })

&#x20;     .then(() => self.skipWaiting()) // 强制激活

&#x20; );

});

// 3. 激活阶段：清理旧缓存

self.addEventListener('activate', (event) => {

&#x20; event.waitUntil(

&#x20;   caches.keys().then(cacheNames => {

&#x20;     return Promise.all(

&#x20;       cacheNames.filter(name => name !== CACHE\_NAME)

&#x20;         .map(name => caches.delete(name))

&#x20;     );

&#x20;   }).then(() => self.clients.claim())

&#x20; );

});

// 4. 拦截请求：实现离线逻辑

self.addEventListener('fetch', (event) => {

&#x20; // 仅处理GET请求

&#x20; if (event.request.method !== 'GET') return;

&#x20; event.respondWith(

&#x20;   // 先尝试从网络获取

&#x20;   fetch(event.request)

&#x20;     .then(networkResponse => {

&#x20;       // 网络请求成功，更新缓存

&#x20;       caches.open(CACHE\_NAME).then(cache => {

&#x20;         cache.put(event.request, networkResponse.clone());

&#x20;       });

&#x20;       return networkResponse;

&#x20;     })

&#x20;     .catch(() => {

&#x20;       // 网络失败，返回缓存资源

&#x20;       return caches.match(event.request)

&#x20;         .then(cachedResponse => {

&#x20;           // 若缓存未命中，返回离线备用页

&#x20;           return cachedResponse || caches.match(OFFLINE\_URL);

&#x20;         });

&#x20;     })

&#x20; );

});
```

#### 3.3 注册 Service Worker 并测试离线功能



*   在页面中注册 SW（如`app.js`中添加注册代码）。

*   部署网站（需 HTTPS 环境或[localhost](https://localhost)），首次访问时触发 SW 安装和缓存。

*   在浏览器开发者工具（Application > Service Workers）中勾选 “Offline”，模拟离线环境，刷新页面验证是否能正常显示缓存内容。

#### 3.4 缓存更新策略



*   当资源更新时，修改`CACHE_NAME`（如从`v1`改为`v2`），触发新 SW 的安装。

*   新 SW 激活时，通过`activate`事件清理旧缓存，确保用户获取最新资源。

### 4. 注意事项与最佳实践



*   **HTTPS 依赖**：Service Worker 仅在 HTTPS 环境（或[localhost](https://localhost)）中运行，防止中间人攻击。

*   **作用域限制**：SW 只能控制与其脚本同源且在`scope`范围内的页面，避免越权拦截。

*   **缓存体积控制**：避免缓存过多资源导致磁盘占用过高，定期清理无用缓存。

*   **版本管理**：通过缓存名称添加版本号（如`v1`、`v2`），确保更新时能正确替换旧缓存。

*   **兼容性处理**：对不支持 Service Worker 的浏览器（如 IE），提供降级方案（直接访问网络）。

### 5. 总结

Service Worker 是实现离线功能和 PWA 的核心技术，其生命周期包括注册、安装、激活、运行和销毁阶段，每个阶段都有明确的职责（如安装时缓存资源、激活时清理旧缓存、运行时拦截请求）。通过自定义`fetch`事件的响应策略，可在离线时返回缓存资源，确保用户在无网络环境下仍能访问页面。实际应用中，需注意缓存版本管理、HTTPS 依赖和兼容性处理，结合业务需求设计合理的缓存策略，平衡离线可用性与资源新鲜度。Service Worker 不仅提升了离线体验，还能优化网络请求性能，是现代前端开发的重要工具。

