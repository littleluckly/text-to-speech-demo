# 解释浏览器的同源策略，如何通过 CORS 机制实现跨域资源共享？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890bc",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["浏览器"]

}
```

## 答案 1：核心简洁的口语化回答

・同源策略是浏览器的安全机制，要求两个 URL 的协议、域名、端口完全一致（即同源）才能相互访问资源，否则限制跨域交互（如读取 Cookie、发送 AJAX 请求）。

・CORS（跨域资源共享）通过服务器设置响应头实现跨域，核心是`Access-Control-Allow-Origin`指定允许的源。

・简单请求直接发送并验证响应头；复杂请求先发送 OPTIONS 预检请求，确认服务器允许后再发送实际请求，确保安全性。

## 答案 2：口语化扩展回答

浏览器的同源策略就像一道安全门禁，目的是防止不同网站随意窃取数据。判断 “同源” 要看协议（比如 http 和 https 不一样）、域名（比如[a.com](https://a.com)和[b.com](https://b.com)不一样）、端口（比如 80 和 8080 不一样），三个都相同才算同源。不同源的话，浏览器会限制它们之间的互动，比如用 AJAX 不能直接请求数据，也不能读取对方的 Cookie。

但实际开发中经常需要跨域获取资源，这时候 CORS 机制就派上用场了。它其实是服务器端的配置，通过在响应里加特定的头信息，告诉浏览器 “允许某个域名的请求访问我”。

比如前端从[www.abc.com](https://www.abc.com)请求[www.xyz.com](https://www.xyz.com)的资源，只要[xyz.com](https://xyz.com)的服务器在响应头里加上`Access-Control-Allow-Origin: ``https://www.abc.com`，浏览器就会放行。如果是复杂请求（比如用 PUT 方法，或者带自定义头），浏览器会先发一个 OPTIONS “预检” 请求，问问服务器是否允许这种操作，服务器同意后，才会发送真正的请求数据，这样既满足了跨域需求，又保证了安全。

## 答案 3：技术深度解析

### 1. 浏览器的同源策略（Same-Origin Policy）

#### 1.1 定义与核心作用

同源策略是浏览器最核心的安全机制之一，由 Netscape 在 1995 年提出，用于限制**不同源的文档或脚本**对当前文档资源的访问。其核心目的是防止恶意网站通过脚本窃取用户敏感数据（如 Cookie、LocalStorage）或执行未授权操作（如伪造请求）。

#### 1.2 “同源” 的判定标准

两个 URL 必须同时满足以下三个条件才被视为 “同源”：



*   **协议（Protocol）相同**：如均为`http`或`https`（`http://a.com`与`https://a.com`不同源）。

*   **域名（Domain）相同**：如均为`example.com`（`a.example.com`与`b.example.com`不同源，因子域名不同）。

*   **端口（Port）相同**：如均为 80（默认端口可省略，`http://a.com:8080`与`http://a.com`不同源）。



| 示例 URL                               | 与`http://example.com:80/index.html`是否同源 | 原因                  |
| ------------------------------------ | --------------------------------------- | ------------------- |
| `http://example.com:80/about.html`   | 是                                       | 协议、域名、端口完全一致        |
| `https://example.com/index.html`     | 否                                       | 协议不同（https vs http） |
| `http://api.example.com/index.html`  | 否                                       | 域名不同（子域名差异）         |
| `http://example.com:8080/index.html` | 否                                       | 端口不同（8080 vs 80）    |

#### 1.3 限制范围

同源策略主要限制跨域的以下交互：



*   **DOM 访问**：无法通过`iframe`或`window.open`访问不同源页面的 DOM。

*   **数据读取**：禁止读取不同源的 Cookie、LocalStorage、SessionStorage。

*   **网络请求**：限制 XMLHttpRequest/Fetch 发送跨域请求（默认被拦截）。

*   **脚本执行**：禁止加载不同源的脚本并执行（除非设置特定头）。

### 2. CORS（跨域资源共享）机制

CORS（Cross-Origin Resource Sharing）是 W3C 标准定义的跨域解决方案，通过**服务器设置响应头**告知浏览器允许特定源的跨域请求，本质是浏览器与服务器的 “安全协商机制”。

#### 2.1 核心原理



1.  浏览器检测到跨域请求时，自动在请求头中添加`Origin`字段（标识请求来源）。

2.  服务器在响应头中返回`Access-Control-Allow-Origin`等字段，声明允许的源。

3.  浏览器验证响应头：若允许当前源，则放行请求；否则拦截并报错。

#### 2.2 简单请求与复杂请求

CORS 将跨域请求分为两类，处理流程不同：

##### （1）简单请求

同时满足以下条件的请求为简单请求，可直接发送：



*   **HTTP 方法**：限于 GET、POST、HEAD。

*   **请求头**：仅包含浏览器默认头（如`Accept`、`Content-Type`），且`Content-Type`只能是`application/x-www-form-urlencoded`、`multipart/form-data`、`text/plain`。

**处理流程**：



1.  前端发送请求，自动添加`Origin`头：



```
GET /data HTTP/1.1

Origin: https://frontend.com  # 请求来源

Host: backend.com
```



1.  服务器响应时添加 CORS 头：



```
HTTP/1.1 200 OK

Access-Control-Allow-Origin: https://frontend.com  # 允许的源（\*表示允许所有源）

Content-Type: application/json
```



1.  浏览器验证`Access-Control-Allow-Origin`：若包含请求源，则放行响应数据；否则报错。

##### （2）复杂请求

不符合简单请求条件的为复杂请求（如使用 PUT/DELETE 方法、带自定义头、`Content-Type: application/json`），需先发送 “预检请求”。

**处理流程**：



1.  **预检请求（OPTIONS）**：浏览器先发送 OPTIONS 请求，询问服务器是否允许跨域：



```
OPTIONS /data HTTP/1.1

Origin: https://frontend.com

Access-Control-Request-Method: PUT  # 告知服务器实际请求方法

Access-Control-Request-Headers: X-Custom-Header  # 告知服务器自定义头

Host: backend.com
```



1.  **服务器响应预检请求**，声明允许的方法、头、缓存时间：



```
HTTP/1.1 204 No Content

Access-Control-Allow-Origin: https://frontend.com

Access-Control-Allow-Methods: PUT, GET, POST  # 允许的方法

Access-Control-Allow-Headers: X-Custom-Header  # 允许的自定义头

Access-Control-Max-Age: 86400  # 预检结果缓存24小时（避免重复预检）
```



1.  浏览器验证预检响应：若通过，发送实际请求；否则拦截。

2.  **实际请求与响应**：流程同简单请求，服务器需再次返回`Access-Control-Allow-Origin`。

#### 2.3 关键 CORS 响应头



| 响应头                                | 作用                                                 |
| ---------------------------------- | -------------------------------------------------- |
| `Access-Control-Allow-Origin`      | 指定允许的跨域源（如`https://a.com`，`*`表示允许所有源，不能与带凭证请求同时使用） |
| `Access-Control-Allow-Methods`     | 预检请求中声明允许的 HTTP 方法（如`GET, POST, PUT`）              |
| `Access-Control-Allow-Headers`     | 预检请求中声明允许的自定义请求头                                   |
| `Access-Control-Allow-Credentials` | 设为`true`时，允许跨域请求携带凭证（Cookie、Authorization 头）       |
| `Access-Control-Expose-Headers`    | 允许客户端访问的响应头（默认仅`Cache-Control`等 6 个头可访问）           |
| `Access-Control-Max-Age`           | 预检请求结果的缓存时间（秒），减少预检次数                              |

#### 2.4 带凭证的跨域请求

当请求需要携带 Cookie 或 Authorization 头时，需满足：



1.  前端请求中设置`credentials: include`：



```
fetch('https://backend.com/data', {

&#x20; credentials: 'include'  // 携带凭证

});
```



1.  服务器响应头需同时设置：



```
Access-Control-Allow-Origin: https://frontend.com  # 不能为\*

Access-Control-Allow-Credentials: true  # 允许凭证
```

### 3. 实际应用示例

#### 3.1 服务器配置（Node.js/Express）



```
const express = require('express');

const app = express();

// 全局CORS中间件

app.use((req, res, next) => {

&#x20; // 允许的源（生产环境应指定具体域名，而非\*）

&#x20; res.setHeader('Access-Control-Allow-Origin', 'https://frontend.com');

&#x20; // 允许携带凭证

&#x20; res.setHeader('Access-Control-Allow-Credentials', 'true');

&#x20; // 允许的方法

&#x20; res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');

&#x20; // 允许的自定义头

&#x20; res.setHeader('Access-Control-Allow-Headers', 'X-Custom-Header, Content-Type');

&#x20; // 预检缓存时间

&#x20; res.setHeader('Access-Control-Max-Age', '86400');

&#x20;&#x20;

&#x20; // 处理预检请求

&#x20; if (req.method === 'OPTIONS') {

&#x20;   return res.sendStatus(204); // 预检成功

&#x20; }

&#x20; next();

});

// 跨域接口示例

app.get('/data', (req, res) => {

&#x20; res.json({ message: '跨域数据响应' });

});

app.listen(3000);
```

#### 3.2 前端请求示例



```
// 简单请求（GET）

fetch('https://backend.com/data')

&#x20; .then(response => response.json())

&#x20; .then(data => console.log(data));

// 复杂请求（带自定义头的POST）

fetch('https://backend.com/submit', {

&#x20; method: 'POST',

&#x20; headers: {

&#x20;   'Content-Type': 'application/json',

&#x20;   'X-Custom-Header': 'value'  // 自定义头，触发预检

&#x20; },

&#x20; body: JSON.stringify({ name: 'test' })

})

.then(response => response.json())

.then(data => console.log(data));
```

### 4. 总结

同源策略是浏览器的基础安全防线，通过限制跨域交互保护用户数据；CORS 则是在安全前提下实现跨域资源共享的标准方案，通过服务器响应头与浏览器协商，区分简单请求和复杂请求（含预检机制），兼顾灵活性与安全性。实际开发中，需根据请求类型正确配置服务器 CORS 头，并注意带凭证请求的特殊处理，避免因配置不当导致跨域失败。理解两者的工作原理，是解决前端跨域问题的核心。

