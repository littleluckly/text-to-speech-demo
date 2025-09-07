# 微前端架构中，子应用如何通过 HTTP 头实现跨域通信？

## meta 元数据



```
{

&#x20; "id": "f1e2d3c4-b5a6-7890-fedc-0987654321ab",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["http"]

}
```

## 答案 1：核心简洁的口语化回答

・借助 CORS 机制，子应用服务器配置 Access-Control-Allow-Origin 指定允许的主应用域名。

・设置 Access-Control-Allow-Methods 声明允许的 HTTP 方法（如 GET、POST）。

・通过 Access-Control-Allow-Headers 允许自定义请求头（如子应用标识头）。

・如需携带凭据，配置 Access-Control-Allow-Credentials: true，且 Origin 不能为 \*。

・用 Access-Control-Expose-Headers 让前端获取自定义响应头。

## 答案 2：口语化扩展回答

在微前端里，子应用和主应用常不在一个域名下，跨域通信主要靠配置 HTTP 头来让浏览器允许这种跨域访问。首先得明确谁能访问，所以子应用服务器要设 Access-Control-Allow-Origin，指定主应用的域名，不能随便用 \*，尤其是需要传 Cookie 的时候。然后，得告诉浏览器允许哪些请求方法，比如主应用可能用 POST 发数据，这就得在 Access-Control-Allow-Methods 里加上。如果通信时需要带点自定义的信息，比如子应用的 ID，那 Access-Control-Allow-Headers 里就得包含这些自定义头，不然浏览器会拦下来。要是涉及到用户登录信息之类的凭据，得开 Access-Control-Allow-Credentials，同时 Origin 得写死具体域名。另外，子应用返回的一些自定义响应头，得通过 Access-Control-Expose-Headers 让主应用能拿到。实际开发中，还得处理浏览器先发的 OPTIONS 预检请求，确保服务器能正确响应，这样后续的实际请求才能顺利进行。

## 答案 3：技术深度解析

### 实现原理

微前端中子应用通过 HTTP 头实现跨域通信的底层逻辑是浏览器的跨域资源共享（CORS）机制。当主应用（或其他子应用）向不同域的子应用发起请求时，浏览器会先检查子应用服务器返回的 CORS 相关 HTTP 头，判断是否允许该跨域请求，允许则放行，否则拦截。

### 核心 HTTP 头及配置示例



1.  **Access-Control-Allow-Origin**

*   作用：指定允许跨域访问的源。

*   配置示例（Nginx）：



```
\# 只允许主应用https://main-app.com访问

add\_header Access-Control-Allow-Origin "https://main-app.com";
```



*   说明：生产环境中应指定具体域名，避免使用`*`；若需携带凭据，必须指定具体域名。

1.  **Access-Control-Allow-Methods**

*   作用：声明允许的 HTTP 请求方法。

*   配置示例（Apache）：



```
\# 允许GET、POST、OPTIONS方法

Header set Access-Control-Allow-Methods "GET, POST, OPTIONS"
```



*   说明：需包含实际通信中使用的所有方法，OPTIONS 用于处理预检请求。

1.  **Access-Control-Allow-Headers**

*   作用：允许请求中携带的自定义头。

*   配置示例（Express）：



```
// 允许自定义头X-Micro-App-Id和Content-Type

app.use((req, res, next) => {

&#x20; res.setHeader('Access-Control-Allow-Headers', 'X-Micro-App-Id, Content-Type');

&#x20; next();

});
```



*   说明：主应用请求中携带的自定义头必须在此列出，否则请求会被拦截。

1.  **Access-Control-Allow-Credentials**

*   作用：允许跨域请求携带凭据（如 Cookie）。

*   配置示例（Koa）：



```
// 允许携带凭据

app.use(async (ctx, next) => {

&#x20; ctx.set('Access-Control-Allow-Credentials', 'true');

&#x20; await next();

});
```



*   说明：启用后，前端请求需设置`credentials: 'include'`（fetch）或`withCredentials: true`（Axios）。

1.  **Access-Control-Expose-Headers**

*   作用：允许前端获取的自定义响应头。

*   配置示例（Nginx）：



```
\# 允许前端获取X-Micro-App-Status头

add\_header Access-Control-Expose-Headers "X-Micro-App-Status";
```



*   说明：默认情况下，浏览器仅暴露少量基础响应头，自定义头需在此声明才能被前端获取。

### 通信流程详解



1.  **主应用发起请求**



```
// 主应用向子应用发送请求示例

fetch('https://sub-app.com/api/data', {

&#x20; method: 'POST',

&#x20; headers: {

&#x20;   'Content-Type': 'application/json',

&#x20;   'X-Micro-App-Id': 'sub-app-1' // 自定义头，标识子应用

&#x20; },

&#x20; credentials: 'include' // 携带凭据

})

.then(response => response.json())

.then(data => console.log('获取子应用数据：', data));
```



*   这里设置`credentials: 'include'`是为了携带 Cookie 等凭据，与子应用服务器的`Access-Control-Allow-Credentials`配合使用。

1.  **浏览器发送预检请求（OPTIONS）**

    当请求为非简单请求（如使用 POST+JSON 格式、携带自定义头）时，浏览器会先发送 OPTIONS 预检请求，验证服务器是否允许跨域。

    子应用服务器需对 OPTIONS 请求做出响应：



```
// Express处理OPTIONS请求示例

app.options('\*', (req, res) => {

&#x20; res.setHeader('Access-Control-Allow-Origin', 'https://main-app.com');

&#x20; res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');

&#x20; res.setHeader('Access-Control-Allow-Headers', 'X-Micro-App-Id, Content-Type');

&#x20; res.setHeader('Access-Control-Allow-Credentials', 'true');

&#x20; res.sendStatus(204); // 预检请求成功，无响应体

});
```



*   预检请求成功后，浏览器才会发送实际的请求。

1.  **子应用服务器响应**

    子应用处理请求后，返回带 CORS 头的响应：



```
// 子应用处理请求并响应示例

app.post('/api/data', (req, res) => {

&#x20; // 处理业务逻辑，获取数据

&#x20; const data = { message: '子应用数据' };

&#x20;&#x20;

&#x20; // 设置CORS响应头

&#x20; res.setHeader('Access-Control-Allow-Origin', 'https://main-app.com');

&#x20; res.setHeader('Access-Control-Allow-Credentials', 'true');

&#x20; res.setHeader('X-Micro-App-Status', 'success'); // 自定义响应头

&#x20; res.setHeader('Access-Control-Expose-Headers', 'X-Micro-App-Status');

&#x20;&#x20;

&#x20; // 返回数据

&#x20; res.json(data);

});
```



1.  **主应用接收响应**

    浏览器验证子应用返回的 CORS 头无误后，将响应数据传递给主应用，主应用即可处理数据完成通信。

### 局限性及解决方案



1.  **局限性**

*   配置繁琐：需要精确配置多个 HTTP 头，容易遗漏或配置错误。

*   安全性风险：若配置不当（如滥用`*`），可能导致跨域攻击。

*   预检请求开销：非简单请求会多一次 OPTIONS 请求，增加通信延迟。

1.  **解决方案**

*   使用中间件：如 Express 的`cors`中间件，简化 CORS 配置。



```
const cors = require('cors');

// 配置允许的源、方法等

app.use(cors({

&#x20; origin: 'https://main-app.com',

&#x20; methods: \['GET', 'POST', 'OPTIONS'],

&#x20; allowedHeaders: \['X-Micro-App-Id', 'Content-Type'],

&#x20; credentials: true,

&#x20; exposedHeaders: \['X-Micro-App-Status']

}));
```



*   限制允许的源：通过动态校验`Origin`头，只允许白名单中的域名访问。

*   缓存预检请求：设置`Access-Control-Max-Age`头，缓存预检请求结果，减少重复请求。



```
\# 缓存预检请求结果1小时（3600秒）

add\_header Access-Control-Max-Age "3600";
```

### 演进思路及未来趋势

随着微前端架构的发展，跨域通信方案也在不断优化。未来可能会有更简洁、更安全的跨域机制出现，例如基于 HTTP/2 或 HTTP/3 的多路复用特性，减少跨域请求的开销；或者浏览器提供更精细化的跨域控制策略，平衡安全性和开发效率。同时，结合服务端代理等方式，可进一步简化跨域配置，提升微前端架构的稳定性和安全性。

