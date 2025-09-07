# CSRF 攻击的原理是什么？如何通过 Token 机制防御 CSRF 攻击？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ad",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["安全"]

}
```

## 答案 1：核心简洁的口语化回答

・CSRF 攻击即跨站请求伪造，攻击者诱导用户在已登录的目标网站上执行非本意的操作。

・原理是利用用户的登录状态，以用户名义发送恶意请求，浏览器会自动携带 Cookie 等认证信息。

・Token 机制防御：服务器生成唯一 Token 并关联用户，请求时需提交 Token，服务器验证 Token 有效性，不一致则拒绝请求。

## 答案 2：口语化扩展回答

CSRF 攻击简单说就是，坏人想让你在你已经登录的网站上帮他做坏事。比如你登录了银行网站，这时点了个恶意链接，这个链接可能就会以你的名义给坏人转账。这是因为浏览器在访问那个银行相关的请求时，会自动带上你登录银行的 Cookie，网站以为是你自己操作的，就执行了请求。

这种攻击能成，主要是因为网站信任用户的登录状态，却没验证这个请求是不是用户真的想发的。而 Token 机制就是来解决这个问题的。服务器会给每个用户生成一个唯一的 Token，存在服务器端，同时也会让前端拿到这个 Token。之后用户发请求的时候，不仅要带 Cookie，还得把这个 Token 也带上。服务器收到请求后，会对比请求里的 Token 和自己存的是不是一样，不一样就不认这个请求，这样坏人就算诱导你发请求，拿不到正确的 Token，攻击也就失败了。一般来说，Token 会放在表单里或者请求头里，而且每次请求可能还会更新 Token，更安全些。

## 答案 3：技术深度解析

### 一、CSRF 攻击的原理

CSRF（Cross-Site Request Forgery，跨站请求伪造）攻击，是指攻击者诱导已登录目标网站的用户，在该网站上执行非用户本意的操作的攻击方式。

其核心原理基于以下几点：



1.  用户已经登录了目标网站，并且在浏览器中保存了该网站的登录凭证（如 Cookie）。

2.  攻击者构造了一个恶意请求，该请求指向目标网站的某个功能接口（如转账、修改密码等）。

3.  攻击者通过各种方式（如诱导用户点击链接、加载包含恶意代码的图片等），使用户的浏览器发送这个恶意请求。

4.  由于用户已登录目标网站，浏览器会自动在请求中携带该网站的登录凭证，目标网站收到请求后，会误认为是用户本人发起的操作，从而执行该恶意请求。

例如，某银行网站有一个转账接口`http://bank.com/transfer?to=xxx&amount=xxx`，当用户登录银行网站后，攻击者构造一个链接`<img src="``http://bank.com/transfer?to=attacker&amount=1000``">`，并诱导用户访问包含该图片的页面。此时，用户的浏览器会自动向银行网站发送转账请求，且携带用户的登录 Cookie，银行网站验证登录凭证有效后，就会执行转账操作。

### 二、Token 机制防御 CSRF 攻击的实现

Token 机制是防御 CSRF 攻击的有效手段，其核心思想是在请求中加入一个服务器生成的、唯一的 Token，服务器通过验证 Token 的有效性来判断请求是否合法。

#### 1. Token 的生成与存储



*   当用户登录成功后，服务器为该用户生成一个随机的、唯一的 Token（通常是一个长字符串）。

*   服务器将 Token 与用户信息（如用户 ID）关联存储在服务器端（如 Session、Redis 等）。

*   服务器将 Token 返回给前端，前端可以将 Token 存储在 Cookie（非 HttpOnly，便于前端获取）、LocalStorage 或 SessionStorage 中。

示例代码（后端生成并存储 Token，以 Node.js + Express 为例）：



```
const express = require('express');

const session = require('express-session');

const crypto = require('crypto');

const app = express();

// 配置Session，用于存储用户相关信息及Token

app.use(session({

&#x20; secret: 'csrf-token-secret',

&#x20; resave: false,

&#x20; saveUninitialized: true,

&#x20; cookie: { secure: false } // 生产环境应设为true（仅HTTPS）

}));

// 登录接口，登录成功后生成Token

app.post('/login', (req, res) => {

&#x20; const { username, password } = req.body;

&#x20; // 假设验证用户名密码成功

&#x20; const userId = 'user123'; // 实际应从数据库获取

&#x20; req.session.userId = userId;

&#x20;&#x20;

&#x20; // 生成随机Token

&#x20; const csrfToken = crypto.randomBytes(32).toString('hex');

&#x20; // 将Token存储在Session中，与用户关联

&#x20; req.session.csrfToken = csrfToken;

&#x20;&#x20;

&#x20; res.json({

&#x20;   success: true,

&#x20;   csrfToken: csrfToken // 返回Token给前端

&#x20; });

});
```

#### 2. Token 的传递

前端在发起请求（如表单提交、AJAX 请求）时，需要将 Token 传递给服务器。常见的传递方式有：



*   作为表单字段，随表单数据一起提交。

*   作为请求头（如`X-CSRF-Token`）传递。

示例代码（前端传递 Token）：



```
\<!-- 作为表单字段 -->

\<form action="/transfer" method="post">

&#x20; \<input type="hidden" name="csrfToken" value="前端存储的Token">

&#x20; \<input type="text" name="to" placeholder="收款账户">

&#x20; \<input type="number" name="amount" placeholder="金额">

&#x20; \<button type="submit">转账\</button>

\</form>

\<script>

// 作为请求头（AJAX请求）

const csrfToken = localStorage.getItem('csrfToken'); // 从LocalStorage获取Token

fetch('/updatePassword', {

&#x20; method: 'POST',

&#x20; headers: {

&#x20;   'Content-Type': 'application/json',

&#x20;   'X-CSRF-Token': csrfToken // 设置请求头

&#x20; },

&#x20; body: JSON.stringify({ newPassword: 'new123' })

});

\</script>
```

#### 3. Token 的验证

服务器收到请求后，从请求中提取 Token，与服务器端存储的该用户对应的 Token 进行对比验证。如果一致，则认为请求合法，执行相应操作；如果不一致或 Token 不存在，则拒绝请求。

示例代码（后端验证 Token）：



```
// 转账接口，验证CSRF Token

app.post('/transfer', (req, res) => {

&#x20; const { csrfToken, to, amount } = req.body;

&#x20; const storedToken = req.session.csrfToken;

&#x20;&#x20;

&#x20; // 验证Token

&#x20; if (!csrfToken || csrfToken !== storedToken) {

&#x20;   return res.status(403).json({ success: false, message: 'CSRF Token验证失败' });

&#x20; }

&#x20;&#x20;

&#x20; // Token验证通过，执行转账操作（此处仅为示例）

&#x20; console.log(\`向\${to}转账\${amount}元\`);

&#x20; res.json({ success: true, message: '转账成功' });

});

// 更新密码接口，从请求头获取Token并验证

app.post('/updatePassword', (req, res) => {

&#x20; const csrfToken = req.headers\['x-csrf-token'];

&#x20; const storedToken = req.session.csrfToken;

&#x20;&#x20;

&#x20; if (!csrfToken || csrfToken !== storedToken) {

&#x20;   return res.status(403).json({ success: false, message: 'CSRF Token验证失败' });

&#x20; }

&#x20;&#x20;

&#x20; // 执行更新密码操作

&#x20; res.json({ success: true, message: '密码更新成功' });

});
```

#### 4. Token 的更新

为了提高安全性，Token 可以设置有效期，或者在每次使用后更新。每次更新后，旧 Token 失效，前端需要重新获取新 Token。

示例代码（Token 使用后更新）：



```
app.post('/transfer', (req, res) => {

&#x20; // ... 前面的Token验证逻辑 ...

&#x20;&#x20;

&#x20; // 验证通过后，生成新的Token

&#x20; const newCsrfToken = crypto.randomBytes(32).toString('hex');

&#x20; req.session.csrfToken = newCsrfToken;

&#x20; // 返回新Token给前端

&#x20; res.json({&#x20;

&#x20;   success: true,&#x20;

&#x20;   message: '转账成功',

&#x20;   newCsrfToken: newCsrfToken

&#x20; });

});
```

### 三、Token 机制防御 CSRF 的优势与注意事项



1.  优势：

*   能有效区分请求是否由用户主动发起，因为攻击者无法获取到服务器生成的、与用户关联的 Token。

*   实现相对简单，兼容性好，适用于各种类型的请求。

1.  注意事项：

*   Token 必须保持机密性，不能通过不安全的方式传递（如 URL 参数，可能会被泄露）。

*   服务器端需要妥善存储 Token，确保与用户正确关联，且能有效验证。

*   前端需要正确获取和传递 Token，避免因 Token 丢失或传递错误导致正常请求失败。

*   对于重要操作，除了 Token 验证外，还可以结合其他验证方式（如验证码、密码二次验证），进一步提高安全性。

