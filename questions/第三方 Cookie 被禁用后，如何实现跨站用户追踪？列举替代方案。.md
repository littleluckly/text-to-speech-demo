# 第三方 Cookie 被禁用后，如何实现跨站用户追踪？列举替代方案。

## meta 元数据



```
{

&#x20; "id": "c2d3e4f5-a6b7-8901-cdef-234567890abc",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["http"]

}
```

## 答案 1：核心简洁的口语化回答

・浏览器指纹：收集设备特征（如分辨率、字体）生成唯一标识，跨站识别用户。

・URL 参数传递：跳转时在 URL 中携带用户 ID，接收方解析关联用户行为。

・主域名共享 Cookie：同一主域名下的子站，通过主域名 Cookie 共享用户标识。

・账号关联：用户在多站用同一账号登录，服务端通过账号 ID 关联跨站行为。

・本地存储 + 跨域通信：用 localStorage 存标识，通过 postMessage 跨站传递。

## 答案 2：口语化扩展回答

第三方 Cookie 禁用后，跨站追踪得换些思路。浏览器指纹是常用的，就是收集设备的各种信息，像屏幕大小、装的字体，甚至 Canvas 渲染的细微差别，组合成一个独特的 “指纹”，不同网站通过这个指纹就能认出是同一个用户，不过指纹可能会变，比如换了浏览器设置就不准了。

URL 参数传递也简单，用户从 A 网站跳到 B 网站时，A 在链接里带上用户 ID，B 拿到后存在自己的存储里，这样就能关联起来，但用户要是删掉参数就没用了，而且得依赖用户主动跳转。

如果多个网站同属一个公司，比如都是[xxx.com](https://xxx.com)的子站，那就可以用主域名的 Cookie，子站都能读到，方便共享用户标识，不过这只限于同一主域名下的网站。

还有靠用户账号的，用户在不同网站用同一个邮箱登录，后台就能把这些行为绑在一起，准确性高，但只能追踪登录用户，匿名用户就没办法了。另外，也能结合本地存储和跨域通信，一个网站存了标识，其他网站通过脚本用 postMessage 获取，不过得处理好安全问题，防止信息泄露。

## 答案 3：技术深度解析

### 1. 浏览器指纹（Browser Fingerprinting）

#### 原理

通过采集浏览器和设备的多个独特特征，经过哈希计算生成唯一标识符，即使在不同网站，只要特征不变，标识符就可用于跨站追踪。

#### 实现代码（核心特征采集）



```
// 收集浏览器和设备的核心特征

function collectFingerprintFeatures() {

&#x20; const features = {};

&#x20;&#x20;

&#x20; // 1. 浏览器基础信息

&#x20; features.userAgent = navigator.userAgent; // 用户代理字符串，包含浏览器版本、内核等

&#x20; features.language = navigator.language; // 浏览器语言

&#x20; features.platform = navigator.platform; // 运行平台（如Win32、MacIntel）

&#x20;&#x20;

&#x20; // 2. 设备显示信息

&#x20; features.screenResolution = \`\${screen.width}x\${screen.height}\`; // 屏幕分辨率

&#x20; features.colorDepth = screen.colorDepth; // 颜色深度

&#x20;&#x20;

&#x20; // 3. 时区信息

&#x20; features.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone; // 时区（如Asia/Shanghai）

&#x20;&#x20;

&#x20; // 4. Canvas指纹（利用渲染差异）

&#x20; const canvas = document.createElement('canvas');

&#x20; const ctx = canvas.getContext('2d');

&#x20; ctx.fillStyle = '#f60';

&#x20; ctx.fillRect(0, 0, 100, 100);

&#x20; ctx.fillStyle = '#fff';

&#x20; ctx.font = '20px Arial';

&#x20; ctx.fillText('fingerprint', 10, 50);

&#x20; features.canvasFingerprint = canvas.toDataURL(); // Canvas渲染结果的Base64编码，不同设备可能不同

&#x20;&#x20;

&#x20; return features;

}

// 生成指纹（哈希处理特征）

async function generateFingerprint() {

&#x20; const features = collectFingerprintFeatures();

&#x20; // 将特征转换为字符串

&#x20; const featureStr = JSON.stringify(features);

&#x20; // 使用SHA-256哈希生成唯一标识（需引入crypto-js等库）

&#x20; const fingerprint = CryptoJS.SHA256(featureStr).toString();

&#x20; return fingerprint;

}

// 使用示例

generateFingerprint().then(fp => {

&#x20; console.log('用户指纹：', fp);

&#x20; // 将指纹发送到服务器，用于跨站关联

});
```

#### 优缺点



*   优点：无需用户授权，可追踪匿名用户。

*   缺点：特征可能随浏览器升级、设备设置改变而变化（稳定性约 90%）；隐私争议大，部分浏览器已开始限制（如 Firefox 的隐私保护模式会模糊指纹）。

### 2. URL 参数传递（Query String Tracking）

#### 原理

用户从网站 A 跳转至网站 B 时，A 在跳转 URL 中携带用户唯一标识（如`https://siteB.com?uid=123`），B 解析参数后存储，实现跨站关联。

#### 实现流程



1.  **网站 A 生成带标识的跳转链接**



```
// 网站A：用户点击跳转时，在URL中添加用户ID

function generateJumpUrl(targetUrl, userId) {

&#x20; const url = new URL(targetUrl);

&#x20; url.searchParams.set('uid', userId); // 添加用户标识参数

&#x20; return url.toString();

}

// 使用示例：生成跳转到网站B的链接

const jumpUrl = generateJumpUrl('https://siteB.com/page', 'user12345');

// 将链接插入页面，用户点击后跳转

document.getElementById('jumpLink').href = jumpUrl;
```



1.  **网站 B 解析并存储标识**



```
// 网站B：页面加载时解析URL参数

function getUserIdFromUrl() {

&#x20; const url = new URL(window.location.href);

&#x20; return url.searchParams.get('uid'); // 获取A传递的用户ID

}

// 存储用户ID到本地存储

const userId = getUserIdFromUrl();

if (userId) {

&#x20; localStorage.setItem('crossSiteUserId', userId); // 后续行为关联此ID

}
```

#### 优缺点



*   优点：实现简单，兼容性好，无浏览器限制。

*   缺点：标识暴露在 URL 中，易被用户删除或拦截；依赖用户主动跳转，无法追踪无跳转的跨站场景。

### 3. 主域名共享 Cookie（First-Party Cookie Sharing）

#### 原理

若多网站属于同一主域名（如`a.xxx.com`和`b.xxx.com`），可在主域名`xxx.com`下设置 Cookie，所有子域名均可访问，实现跨子站追踪。

#### 配置示例（Nginx）



```
\# 主域名xxx.com下设置Cookie，子域名可访问

location /set-shared-cookie {

&#x20; \# 设置Cookie，domain指定为主域名，path为/确保所有路径可访问

&#x20; add\_header Set-Cookie "crossUserId=user789; Domain=xxx.com; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax";

&#x20; return 200 "Cookie set";

}
```

#### 前端读取示例



```
// 子域名a.xxx.com和b.xxx.com均可读取主域名Cookie

function getSharedUserId() {

&#x20; const cookies = document.cookie.split('; ');

&#x20; for (const cookie of cookies) {

&#x20;   const \[name, value] = cookie.split('=');

&#x20;   if (name === 'crossUserId') {

&#x20;     return value; // 获取共享的用户ID

&#x20;   }

&#x20; }

&#x20; return null;

}
```

#### 优缺点



*   优点：基于第一方 Cookie，浏览器兼容性好，不易被拦截。

*   缺点：仅适用于同一主域名下的子站，无法跨主域名（如`xxx.com`与`yyy.com`）。

### 4. 账号关联（User Account Linking）

#### 原理

用户在多个网站使用同一账号（如邮箱、手机号）登录，服务端通过账号 ID 将不同网站的行为数据关联，实现跨站追踪。

#### 实现流程



1.  **多网站统一账号体系**：用户在网站 A 和 B 均使用`user@example.com`登录。

2.  **行为数据上报**：



```
// 网站A上报用户行为（包含账号ID）

function reportActionA(action) {

&#x20; fetch('https://track-server.com/report', {

&#x20;   method: 'POST',

&#x20;   headers: { 'Content-Type': 'application/json' },

&#x20;   body: JSON.stringify({

&#x20;     account: 'user@example.com', // 账号标识

&#x20;     site: 'siteA',

&#x20;     action: action,

&#x20;     time: new Date().toISOString()

&#x20;   })

&#x20; });

}

// 网站B上报用户行为（同一账号）

function reportActionB(action) {

&#x20; fetch('https://track-server.com/report', {

&#x20;   method: 'POST',

&#x20;   headers: { 'Content-Type': 'application/json' },

&#x20;   body: JSON.stringify({

&#x20;     account: 'user@example.com', // 同一账号标识

&#x20;     site: 'siteB',

&#x20;     action: action,

&#x20;     time: new Date().toISOString()

&#x20;   })

&#x20; });

}
```



1.  **服务端关联**：服务器根据`account`字段将`siteA`和`siteB`的行为数据合并，形成完整用户画像。

#### 优缺点



*   优点：准确性高，合规性好（基于用户主动登录）。

*   缺点：无法追踪匿名用户；依赖多站统一账号体系，实施成本高。

### 5. 本地存储 + 跨域通信（LocalStorage + postMessage）

#### 原理

网站 A 将用户标识存入`localStorage`，网站 B 通过嵌入与 A 同源的脚本，利用`postMessage`跨域获取标识，实现关联。

#### 实现代码



1.  **网站 A 存储标识并监听消息**



```
// 网站A：存储用户标识

localStorage.setItem('crossTrackerId', 'track123');

// 监听其他网站的消息请求

window.addEventListener('message', (event) => {

&#x20; // 验证消息来源（仅允许信任的域名）

&#x20; if (event.origin === 'https://siteB.com') {

&#x20;   if (event.data.type === 'requestTrackerId') {

&#x20;     // 向网站B返回用户标识

&#x20;     event.source.postMessage({

&#x20;       type: 'trackerId',

&#x20;       id: localStorage.getItem('crossTrackerId')

&#x20;     }, event.origin);

&#x20;   }

&#x20; }

}, false);
```



1.  **网站 B 嵌入 A 的脚本并请求标识**



```
\<!-- 网站B嵌入与网站A同源的脚本（如A的域名是https://siteA.com） -->

\<script src="https://siteA.com/cross-tracker.js">\</script>
```



```
// 网站B：通过脚本向网站A请求标识

function getTrackerIdFromA() {

&#x20; // 向网站A的域名发送消息请求

&#x20; window.parent.postMessage({ type: 'requestTrackerId' }, 'https://siteA.com');

&#x20;&#x20;

&#x20; // 监听A返回的消息

&#x20; window.addEventListener('message', (event) => {

&#x20;   if (event.origin === 'https://siteA.com' && event.data.type === 'trackerId') {

&#x20;     const trackerId = event.data.id;

&#x20;     localStorage.setItem('crossTrackerId', trackerId); // 存储标识用于后续追踪

&#x20;   }

&#x20; }, false);

}

// 页面加载时请求标识

getTrackerIdFromA();
```

#### 优缺点



*   优点：可跨主域名实现追踪，灵活性高。

*   缺点：依赖第三方脚本嵌入，存在安全风险（需严格验证`event.origin`）；部分浏览器限制跨域`postMessage`的频率或内容。

### 总结与趋势

第三方 Cookie 禁用后，跨站追踪需在合规前提下组合多种方案（如 “浏览器指纹 + URL 参数” 用于匿名用户，“账号关联” 用于登录用户）。未来，随着隐私法规（如 GDPR、CCPA）的严格化，追踪方案需更注重用户授权，浏览器也可能推出更严格的限制（如禁止 Canvas 指纹、强化 SameSite 策略），开发者需平衡追踪需求与用户隐私。

