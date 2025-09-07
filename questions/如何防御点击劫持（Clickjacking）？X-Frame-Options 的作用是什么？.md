# 如何防御点击劫持（Clickjacking）？X-Frame-Options 的作用是什么？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890af",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["安全"]

}
```

## 答案 1：核心简洁的口语化回答

・防御点击劫持可采用设置 X-Frame-Options 响应头、使用 CSP 的 frame-ancestors 指令、添加防御性 JavaScript 代码等方法。

・X-Frame-Options 是 HTTP 响应头，用于控制网页是否允许被嵌入到 iframe 等框架中，以此阻止恶意网站通过嵌套框架诱导用户点击。

## 答案 2：口语化扩展回答

点击劫持是攻击者把目标网站放到自己的网页里，用透明的 iframe 盖住，再放个诱惑用户点击的按钮在上面，让用户以为点的是假按钮，实际点的是目标网站的关键按钮，比如付款、登录这些。

防御它的话，最常用的就是设置 X-Frame-Options 响应头，这个头能直接告诉浏览器，这个网页能不能被其他网站的 iframe 嵌进去。另外，内容安全策略 CSP 里的 frame-ancestors 指令也能管这个，规定哪些网站能嵌当前页面，比 X-Frame-Options 更灵活。还有就是用 JavaScript 判断自己是不是被嵌在别人的框架里，如果是就做点处理，比如跳转到自己的页面。

X-Frame-Options 的作用很直接，就是防嵌套。它有几个值，DENY 是完全不让嵌，SAMEORIGIN 只允许同域名的网页嵌，ALLOW-FROM uri 就只允许指定的网址嵌。这样一来，恶意网站就没法把目标网页藏在自己的 iframe 里搞小动作了，用户也就不会在不知情的情况下点到不该点的东西。

## 答案 3：技术深度解析

### 一、点击劫持（Clickjacking）的防御方法

点击劫持是一种视觉欺骗攻击，攻击者通过将目标网站嵌入到自己的网页中（通常使用 iframe），并设置 iframe 为透明，覆盖在诱导性内容上方，使用户在点击诱导内容时，实际点击的是目标网站上的敏感操作按钮（如支付、确认、删除等）。防御点击劫持需要从阻止网页被非法嵌套、检测嵌套环境等方面入手，常见方法如下：

#### 1. 使用 X-Frame-Options 响应头

这是最直接有效的防御手段，通过服务器设置该 HTTP 响应头，限制当前网页是否允许被嵌入到 iframe 或 frame 中。具体取值及作用见下文详细说明。

#### 2. 利用 Content-Security-Policy（CSP）的 frame-ancestors 指令

CSP 的`frame-ancestors`指令用于指定允许嵌入当前网页的父页面来源，功能上比 X-Frame-Options 更强大，支持多来源限制，且能与其他 CSP 指令协同工作。例如：



```
Content-Security-Policy: frame-ancestors 'self' https://trusted.example.com;
```

表示当前网页仅允许被同源页面或`https://trusted.example.com`域名下的页面嵌入。

#### 3. 防御性 JavaScript 代码（Frame Busting）

通过 JavaScript 检测当前网页是否被嵌入到其他框架中，若发现被非法嵌套，则采取跳转、隐藏内容等措施。示例代码：



```
// 检测是否被嵌入到iframe中

if (top !== self) {

&#x20; // 若不是同源页面，跳转到自身顶层页面

&#x20; if (top.location.hostname !== self.location.hostname) {

&#x20;   top.location.href = self.location.href;

&#x20; }

&#x20; // 或隐藏页面内容

&#x20; // document.body.style.display = 'none';

}
```

但这种方法存在被绕过的可能（如攻击者禁用 JavaScript），通常作为辅助防御手段。

#### 4. 其他辅助措施



*   对于敏感操作（如支付、修改密码），增加二次确认步骤（如输入验证码、密码），降低误操作风险。

*   合理设计页面 UI，避免关键按钮的位置和大小容易被覆盖模仿。

### 二、X-Frame-Options 的作用与详细说明

#### 1. 核心作用

X-Frame-Options 是一个 HTTP 响应头，主要作用是**控制当前网页是否允许被其他网页通过**`<iframe>`**、**`<frame>`**、**`<embed>`**或**`<object>`**标签嵌入**，以此防止点击劫持攻击。当浏览器检测到目标网页设置了该头且不允许被当前页面嵌入时，会拒绝加载该网页或显示错误信息。

#### 2. 取值及含义



*   **DENY**：表示当前网页**绝对不允许被任何网页嵌入**，无论嵌入页面的域名是什么。

    示例响应头：`X-Frame-Options: DENY`

*   **SAMEORIGIN**：表示当前网页**只允许被同源网页嵌入**（即嵌入页面与当前网页的协议、域名、端口完全一致）。

    示例响应头：`X-Frame-Options: SAMEORIGIN`

*   **ALLOW-FROM uri**（已被废弃，不推荐使用）：表示当前网页**只允许被指定 URI 的网页嵌入**。由于不同浏览器对该值的支持差异较大（如 Chrome 不支持），目前已被 CSP 的`frame-ancestors`指令替代。

    示例响应头：`X-Frame-Options: ALLOW-FROM ``https://trusted.example.com`

#### 3. 配置方式

需在服务器端进行配置，不同服务器的配置方式如下：



*   **Nginx**：在`server`或`location`块中添加



```
add\_header X-Frame-Options SAMEORIGIN;
```



*   **Apache**：在`.htaccess`文件或虚拟主机配置中添加



```
Header always set X-Frame-Options "SAMEORIGIN"
```



*   **IIS**：在`web.config`文件中添加



```
\<configuration>

&#x20; \<system.webServer>

&#x20;   \<httpProtocol>

&#x20;     \<customHeaders>

&#x20;       \<add name="X-Frame-Options" value="SAMEORIGIN" />

&#x20;     \</customHeaders>

&#x20;   \</httpProtocol>

&#x20; \</system.webServer>

\</configuration>
```



*   **Node.js（Express）**：通过中间件设置



```
const express = require('express');

const app = express();

app.use((req, res, next) => {

&#x20; res.setHeader('X-Frame-Options', 'SAMEORIGIN');

&#x20; next();

});
```

#### 4. 局限性与替代方案



*   **局限性**：`X-Frame-Options`功能单一，仅能控制嵌入权限，且`ALLOW-FROM`取值兼容性差；无法同时允许多个不同来源的页面嵌入。

*   **替代方案**：如前文所述，CSP 的`frame-ancestors`指令是更现代、更灵活的替代方案，支持多来源限制（如同时允许`'self'`和`https://a.example.com`、`https://b.example.com`），且能与其他 CSP 规则协同防御多种攻击。例如：



```
Content-Security-Policy: frame-ancestors 'self' https://a.example.com https://b.example.com;
```

### 三、防御点击劫持的最佳实践



1.  **优先使用 CSP 的 frame-ancestors 指令**：因其功能更全面，兼容性（现代浏览器）更好，能满足复杂场景的需求。

2.  **辅以 X-Frame-Options**：为了兼容不支持 CSP 的旧浏览器，可同时设置 X-Frame-Options 作为降级方案（浏览器会优先遵循 CSP）。

3.  **结合 JavaScript 检测**：作为最后一道防线，尽管可能被绕过，但能增加攻击者的攻击成本。

4.  **针对敏感页面强化防御**：对于登录页、支付页、用户中心等敏感页面，应严格限制嵌入来源（如设置为`SAMEORIGIN`或`DENY`），普通页面可根据需求适当放宽。

通过多种防御手段的组合，能有效抵御点击劫持攻击，保护用户在网页上的操作安全。

