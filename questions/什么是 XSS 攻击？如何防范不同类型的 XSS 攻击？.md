# 什么是 XSS 攻击？如何防范不同类型的 XSS 攻击？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ac",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["安全"]

}
```

## 答案 1：核心简洁的口语化回答

・XSS 攻击是跨站脚本攻击，指攻击者注入恶意脚本到网页，让用户浏览时执行。

・主要分存储型、反射型、DOM 型三类，存储型存服务器，反射型经 URL 传递，DOM 型基于页面 DOM 操作。

・防范需输入过滤、输出编码，使用 CSP，设置 Cookie 的 HttpOnly 属性，避免危险 API。

## 答案 2：口语化扩展回答

XSS 攻击简单说就是坏人往网页里塞了恶意的脚本代码，当我们打开网页时，这些代码就会偷偷执行，可能会盗取我们的账号密码、 cookies 这些重要信息，甚至还能冒充我们做一些操作。

从类型来看，存储型的就比较隐蔽，它会把恶意脚本存在服务器里，比如在论坛发个带恶意代码的帖子，别人一打开这个帖子就中招了；反射型的则是通过 URL 传递，比如点了个含恶意代码的链接，服务器把代码反射到页面上执行；DOM 型是在客户端处理数据时搞的鬼，不用经过服务器，直接在浏览器里就触发了。

防范的时候，输入的时候得把那些可能有问题的字符过滤掉，输出到页面上也要进行编码，让恶意代码变成普通文本。还有那个 CSP 机制挺有用的，能限制网页加载哪些资源和脚本。另外，给 Cookie 加上 HttpOnly 属性，能防止脚本盗取。平时写代码也得注意，别用 eval 之类的危险函数，减少被攻击的机会。不同类型的攻击防范思路差不多，但要结合具体场景，比如存储型要重点做好服务器端的过滤存储，反射型要注意处理 URL 传来的数据。

## 答案 3：技术深度解析

### 一、XSS 攻击的定义

XSS（Cross-Site Scripting）攻击，即跨站脚本攻击，是一种常见的 Web 安全漏洞。攻击者通过在网页中注入恶意的客户端脚本（通常是 JavaScript），当用户访问该网页时，恶意脚本会在用户的浏览器中执行，从而达到窃取用户信息、篡改网页内容、冒充用户进行操作等恶意目的。

### 二、不同类型 XSS 攻击的原理及工作流程



1.  存储型 XSS

*   原理：攻击者将恶意脚本提交到目标网站的服务器数据库中，当其他用户访问包含该恶意脚本的页面时，服务器将恶意脚本从数据库中取出并返回给用户浏览器，恶意脚本在用户浏览器中执行。

*   工作流程：


    ```mermaid
    graph LR
    A[攻击者提交含恶意脚本的数据] --> B[服务器将数据存储到数据库]
    B --> C[用户请求包含该数据的页面]
    C --> D[服务器从数据库取出数据并返回给用户浏览器]
    D --> E[恶意脚本在用户浏览器执行]
    ```

1.  反射型 XSS

*   原理：攻击者构造带有恶意脚本的 URL，当用户点击该 URL 时，服务器将 URL 中的恶意脚本作为响应的一部分反射给用户浏览器，恶意脚本执行。

*   工作流程：


    ```mermaid
    graph LR
    A[攻击者构造含恶意脚本的URL] --> B[用户点击该URL]
    B --> C[服务器解析URL，将恶意脚本反射到响应中]
    C --> D[恶意脚本在用户浏览器执行]
    ```

1.  DOM 型 XSS

*   原理：基于文档对象模型（DOM）的漏洞，攻击者注入的恶意脚本不会经过服务器处理，而是通过客户端的 JavaScript 代码对 DOM 进行操作时执行。

*   工作流程：


    ```mermaid
    graph LR
    A[攻击者构造含恶意脚本的数据] --> B[数据被传递到客户端JavaScript]
    B --> C[JavaScript代码处理数据时，恶意脚本被执行]
    ```

### 三、防范不同类型 XSS 攻击的技术方案



1.  输入验证与过滤

    对用户输入的数据进行严格验证，过滤掉可能包含恶意脚本的内容。可以使用正则表达式或专门的库来实现。

    示例代码（使用正则表达式过滤危险标签和属性）：



```
function sanitizeInput(input) {

&#x20; // 过滤\<script>标签

&#x20; let sanitized = input.replace(/\<script.\*?>.\*?<\\/script>/gi, '');

&#x20; // 过滤on事件属性，如onclick、onload等

&#x20; sanitized = sanitized.replace(/on\w+=".\*?"/gi, '');

&#x20; return sanitized;

}

// 使用示例

const userInput = '\<script>alert("XSS")\</script>\<button onclick="bad()">点击\</button>';

const safeInput = sanitizeInput(userInput);

console.log(safeInput); // 输出：\<button>点击\</button>
```



1.  输出编码

    将从服务器或用户输入中获取的数据，在输出到 HTML 页面时进行编码，将特殊字符转换为对应的实体编码，使恶意脚本无法执行。

    示例代码（HTML 编码函数）：



```
function htmlEncode(str) {

&#x20; if (!str) return '';

&#x20; // 创建一个div元素用于编码

&#x20; const div = document.createElement('div');

&#x20; // 将字符串作为文本节点添加到div中，自动进行编码

&#x20; div.textContent = str;

&#x20; // 返回编码后的字符串

&#x20; return div.innerHTML;

}

// 使用示例

const maliciousScript = '\<script>alert("XSS")\</script>';

const encodedScript = htmlEncode(maliciousScript);

// 输出到页面时，恶意脚本会被当作普通文本显示

document.getElementById('content').innerHTML = encodedScript;
```



1.  内容安全策略（CSP）

    通过设置 HTTP 响应头中的 Content-Security-Policy，限制网页可以加载和执行的资源，如脚本、样式表、图片等，从而防止恶意脚本的执行。

    示例（在服务器端设置 CSP 头）：



```
// 只允许加载同源的脚本和样式表，以及指定域名的图片

Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' https://example.com
```

上述设置表示：默认只允许加载同源资源；脚本只能加载同源的；样式表只能加载同源的；图片可以加载同源的和[https://example.com](https://example.com)域名下的。



1.  设置 Cookie 的 HttpOnly 属性

    将 Cookie 设置为 HttpOnly，使 JavaScript 无法访问 Cookie，防止攻击者通过 XSS 攻击窃取 Cookie。

    示例（在服务器端设置 Cookie）：



```
// 设置sessionId这个Cookie为HttpOnly

Set-Cookie: sessionId=123456; HttpOnly; Secure; SameSite=Strict
```

其中，HttpOnly 表示该 Cookie 只能通过 HTTP 协议访问，JavaScript 无法获取；Secure 表示该 Cookie 只能在 HTTPS 连接中传输；SameSite=Strict 表示该 Cookie 只在同源请求中发送，减少跨站请求伪造的风险。



1.  避免使用危险的 API

    尽量避免使用 eval ()、innerHTML 等可能执行恶意脚本的 API，改用更安全的替代方法，如 textContent。

    示例代码：



```
// 不安全的方式：使用innerHTML可能执行恶意脚本

const userInput = '\<script>alert("XSS")\</script>';

document.getElementById('content').innerHTML = userInput; // 会执行恶意脚本

// 安全的方式：使用textContent，只会当作文本显示

document.getElementById('content').textContent = userInput; // 不会执行恶意脚本
```

### 四、局限性及解决方案



1.  输入过滤的局限性：攻击者可能会通过各种变形的方式绕过过滤，如使用大小写混合、特殊字符编码等。

    解决方案：结合多种过滤规则，并定期更新过滤规则以应对新的攻击方式。

2.  输出编码的局限性：不同的上下文（如 HTML 标签内、属性值、JavaScript 代码中）需要不同的编码方式，如果编码方式不正确，可能无法有效防范 XSS 攻击。

    解决方案：根据数据输出的上下文选择合适的编码方式，例如在 JavaScript 中使用 JSON 编码。

3.  CSP 的局限性：部分旧浏览器不支持 CSP，且过于严格的 CSP 规则可能会影响网页的正常功能。

    解决方案：渐进式地部署 CSP，先使用 report-only 模式监控可能的问题，再逐步调整 CSP 规则。

### 五、演进思路及未来趋势

随着 Web 技术的发展，XSS 攻击的手段也在不断变化，防范技术也在持续演进。未来可能会有更多基于人工智能和机器学习的方法来检测和防范 XSS 攻击，通过分析用户行为和代码模式，自动识别潜在的恶意脚本。同时，浏览器和 Web 标准也会不断加强安全机制，如进一步完善 CSP、引入更严格的同源策略等，从底层减少 XSS 攻击的可能性。此外，开发人员的安全意识也将越来越重要，通过规范开发流程和加强安全培训，从源头降低 XSS 漏洞的产生。

