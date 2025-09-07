# 什么是 JWT（JSON Web Token）？它的认证流程和安全隐患是什么？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890b3",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["安全"]

}
```

## 答案 1：核心简洁的口语化回答

・JWT 是一种基于 JSON 的轻量级令牌，用于在客户端和服务器间安全传递用户身份信息。

・认证流程：用户登录后，服务器生成包含用户信息的 JWT 返回客户端，客户端后续请求携带 JWT，服务器验证其有效性即可确认身份。

・安全隐患包括：令牌无法主动撤销、有效期内被盗用风险高、签名密钥泄露会导致伪造、payload 信息易被解析等。

## 答案 2：口语化扩展回答

JWT 就像一个加密的数字身份证，里面包含了用户的基本信息（比如用户 ID、权限），由服务器生成后发给客户端。客户端每次访问服务器时带上这个 “身份证”，服务器不用查数据库，直接验证 “身份证” 的真实性就能确认用户身份，很适合前后端分离或多服务器的场景。

认证时，用户先输入账号密码登录，服务器验证通过后，会把用户的非敏感信息打包进 JWT，用密钥签名后发给客户端。客户端可以把它存在 localStorage 或 Cookie 里，下次发请求时，放在请求头的 Authorization 里传给服务器。服务器收到后，先检查签名对不对，再看有没有过期，都没问题就认可这个用户。

不过 JWT 也有缺点。一旦发出去，服务器没法主动收回，要是被别人偷走了，在有效期内就能冒充用户；签名用的密钥要是泄露了，坏人就能伪造 JWT；而且它里面的信息只是用 Base64 编码，不是加密，很容易被解开看到内容，所以绝对不能放密码之类的敏感信息。另外，有效期设得太长不安全，设得太短又得频繁登录，需要好好权衡。

## 答案 3：技术深度解析

### 一、JWT（JSON Web Token）的定义

JWT（JSON Web Token）是一种开放标准（RFC 7519），它定义了一种紧凑且自包含的方式，用于在多方之间以 JSON 对象安全传递信息。这些信息之所以可信，是因为它们经过了数字签名。

JWT 由三部分组成，用点（.）分隔，分别是：



*   **Header（头部）**：通常包含两部分信息，一是令牌类型（即 “JWT”），二是使用的签名算法（如 HMAC SHA256 或 RSA）。例如：`{"alg":"HS256","typ":"JWT"}`，这部分会经过 Base64Url 编码形成 JWT 的第一部分。

*   **Payload（载荷）**：包含声明（Claims），即需要传递的数据。声明分为三种类型：注册声明（如 iss 发行人、exp 过期时间、sub 主题等，是预定义的但可选）、公共声明（可以自定义但需避免冲突）、私有声明（是发行方和接收方共同定义的声明）。例如：`{"sub":"1234567890","name":"John Doe","admin":true}`，这部分也会经过 Base64Url 编码形成 JWT 的第二部分。

*   **Signature（签名）**：是对前两部分的签名，用于验证消息在传递过程中没有被篡改，同时也能确保发送者的身份。签名的生成需要编码后的 Header、编码后的 Payload、一个密钥以及 Header 中指定的签名算法。例如，使用 HMAC SHA256 算法的签名生成公式为：`HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)`。

一个完整的 JWT 示例：`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

### 二、JWT 的认证流程

JWT 的认证流程主要分为以下几个步骤，下面结合代码示例进行详细说明：



1.  **用户登录**：用户通过客户端（如网页、APP）向服务器发送包含用户名和密码的登录请求。

2.  **服务器验证并生成 JWT**：

    示例代码（使用 Node.js 的 jsonwebtoken 库生成 JWT）：



```
const jwt = require('jsonwebtoken');

// 假设用户登录信息验证成功，获取到用户数据

const user = {

&#x20; id: '123456',

&#x20; username: 'john\_doe',

&#x20; role: 'user'

};

// 定义JWT的Payload

const payload = {

&#x20; sub: user.id, // 主题，通常为用户ID

&#x20; name: user.username,

&#x20; role: user.role,

&#x20; exp: Math.floor(Date.now() / 1000) + 3600 // 过期时间，这里设置为1小时后

};

// 签名密钥，需要妥善保管，不能泄露

const secretKey = 'your-very-secret-key';

// 生成JWT

const token = jwt.sign(payload, secretKey, { algorithm: 'HS256' });

// 将生成的JWT返回给客户端

console.log('生成的JWT:', token);
```



*   服务器接收并验证用户提交的登录信息。如果验证失败，返回错误信息；如果验证成功，服务器会生成 JWT。

*   生成 JWT 时，服务器需要定义 Payload 中的信息（如用户 ID、过期时间等），选择合适的签名算法，并使用密钥对 Header 和 Payload 进行签名。

1.  **客户端存储 JWT**：客户端收到服务器返回的 JWT 后，将其存储在合适的位置。常见的存储方式有：

*   localStorage：优点是易于访问，缺点是存在 XSS 攻击风险。

*   Cookie：可以设置 HttpOnly、Secure 等属性，降低 XSS 风险，但可能存在 CSRF 风险。

*   移动端 APP 的本地存储：如 Android 的 SharedPreferences、iOS 的 NSUserDefaults。

1.  **客户端携带 JWT 发起请求**：在后续的请求中，客户端需要将 JWT 携带在请求中，通常是放在 HTTP 请求头的 Authorization 字段中，格式为`Bearer <token>`。

    示例代码（前端使用 fetch API 携带 JWT 发起请求）：



```
// 从存储中获取JWT

const token = localStorage.getItem('jwtToken');

// 发起请求

fetch('https://api.example.com/data', {

&#x20; method: 'GET',

&#x20; headers: {

&#x20;   'Authorization': \`Bearer \${token}\`,

&#x20;   'Content-Type': 'application/json'

&#x20; }

})

.then(response => response.json())

.then(data => console.log('请求成功:', data))

.catch(error => console.error('请求失败:', error));
```



1.  **服务器验证 JWT**：

    示例代码（Node.js 验证 JWT）：



```
const jwt = require('jsonwebtoken');

const secretKey = 'your-very-secret-key';

// 从请求头中提取JWT

function getTokenFromHeader(req) {

&#x20; const authHeader = req.headers.authorization;

&#x20; if (authHeader && authHeader.startsWith('Bearer ')) {

&#x20;   return authHeader.split(' ')\[1];

&#x20; }

&#x20; return null;

}

// 验证JWT的中间件

function verifyToken(req, res, next) {

&#x20; const token = getTokenFromHeader(req);

&#x20;&#x20;

&#x20; if (!token) {

&#x20;   return res.status(401).json({ message: '未提供JWT' });

&#x20; }

&#x20;&#x20;

&#x20; try {

&#x20;   // 验证JWT

&#x20;   const decoded = jwt.verify(token, secretKey);

&#x20;   // 将解析后的用户信息添加到请求对象中，供后续处理使用

&#x20;   req.user = decoded;

&#x20;   next();

&#x20; } catch (error) {

&#x20;   if (error.name === 'TokenExpiredError') {

&#x20;     return res.status(401).json({ message: 'JWT已过期' });

&#x20;   }

&#x20;   return res.status(401).json({ message: 'JWT验证失败' });

&#x20; }

}

// 使用中间件验证请求

app.get('/protected-data', verifyToken, (req, res) => {

&#x20; // 可以使用req.user中的信息进行业务处理

&#x20; res.json({ message: '这是受保护的数据', user: req.user });

});
```



*   服务器从请求中提取 JWT。

*   服务器使用相同的签名算法和密钥对 JWT 进行验证。验证内容包括签名是否有效（防止 JWT 被篡改）、是否在有效期内等。

*   如果验证通过，服务器从 JWT 的 Payload 中获取用户信息，进行后续的业务处理；如果验证失败，返回 401 Unauthorized 等错误响应。

### 三、JWT 的安全隐患



1.  **无法主动撤销令牌**：JWT 一旦生成并发送给客户端，在其有效期内，服务器无法主动将其撤销。这意味着如果 JWT 被盗，攻击者可以在有效期内一直使用该令牌访问受保护的资源，直到令牌过期。与 Session 认证不同，Session 可以在服务器端直接销毁，从而立即终止用户的会话。

2.  **签名密钥泄露风险大**：JWT 的安全性完全依赖于签名密钥的保密性。如果签名密钥被泄露，攻击者就可以使用该密钥生成伪造的 JWT，从而冒充合法用户访问系统。因此，必须妥善保管签名密钥，避免将其硬编码在代码中，并且要定期更换密钥。

3.  **Payload 信息易被解析**：JWT 的 Header 和 Payload 部分只是使用 Base64Url 进行编码，而不是加密。这意味着任何人都可以通过 Base64Url 解码轻松获取其中的信息。因此，绝对不能在 Payload 中包含敏感信息，如用户密码、信用卡号等，否则会导致敏感信息泄露。

4.  **过期时间设置难题**：JWT 的过期时间（exp）设置需要在安全性和用户体验之间进行权衡。如果过期时间设置过长，JWT 被盗后，攻击者有更长的时间进行恶意操作；如果过期时间设置过短，用户需要频繁登录，会影响用户体验。

5.  **存储方式带来的安全风险**：

*   如果将 JWT 存储在 localStorage 中，容易受到 XSS（跨站脚本）攻击。攻击者可以通过注入恶意脚本获取 localStorage 中的 JWT，进而冒充用户进行操作。

*   如果将 JWT 存储在 Cookie 中，虽然可以通过设置 HttpOnly 属性防止 JavaScript 访问（从而降低 XSS 风险），但可能会面临 CSRF（跨站请求伪造）攻击的风险。

1.  **算法相关漏洞**：

*   有些 JWT 实现可能允许攻击者修改 Header 中的签名算法，例如将原本使用的 HMAC SHA256 算法改为 none（不进行签名）。如果服务器没有对算法进行严格验证，就可能接受未签名的 JWT，导致安全漏洞。

*   使用弱签名算法（如 HMAC-MD5）也会增加 JWT 被破解的风险，应该使用强签名算法（如 HMAC SHA256、RSA SHA256 等）。

1.  **重放攻击风险**：JWT 本身没有包含防止重放攻击的机制。攻击者可以截获有效的 JWT，并在其有效期内重复使用该 JWT 来访问资源。虽然可以通过设置较短的过期时间来降低这种风险，但在一些安全性要求极高的场景中，还需要结合其他措施（如使用一次性令牌、添加时间戳和随机数等）来防御重放攻击。

