# 如何通过 Cache-Control 头实现资源的长期缓存？写出配置示例。

## meta 元数据



```
{

&#x20; "id": "d9e0f1a2-b3c4-5678-f123-90abcdef1234",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["http"]

}
```

## 答案 1：核心简洁的口语化回答

・对静态资源（图片、CSS、JS 等）设置 Cache-Control: public, max-age=31536000，实现 1 年长期缓存。

・配合资源指纹（文件名加哈希），如 style.8f3d7.css，内容更新时哈希变化，触发重新请求。

・服务器配置需确保缓存头正确生效，避免与 no-cache 等指令冲突。

・兼容旧浏览器可附加 Expires 头，但优先级低于 Cache-Control。

## 答案 2：口语化扩展回答

要用 Cache-Control 头实现资源长期缓存，主要是给那些不常变动的静态资源设置足够长的缓存时间。比如图片、字体文件，还有稳定的 CSS 和 JS，这些资源一整年可能都变不了几次，就可以把 max-age 设为 31536000 秒，也就是一年。这样浏览器在一年内都会直接从本地缓存拿，不用再向服务器请求，能大大减少服务器压力。

不过光设时间还不够，得给资源文件名加个哈希值，像把 logo.png 改成 logo.2a3b4c.png。这样一旦资源内容有变动，哈希也会跟着变，浏览器就会把它当成新文件，重新下载，不会用旧的缓存。另外，服务器配置的时候要注意用 public 指令，让代理服务器也能缓存这些资源，同时别加 no-cache 之类的冲突指令，不然长期缓存就失效了。对于一些老浏览器，还可以加个 Expires 头作为补充，但主要还是看 Cache-Control。

## 答案 3：技术深度解析

### 一、实现资源长期缓存的核心原理

通过`Cache-Control`头设置合理的缓存策略，让浏览器和代理服务器在指定时间内直接使用本地缓存的资源，无需向服务器发起请求。关键在于：



*   **长期缓存时长**：使用`max-age`指令指定资源的缓存有效期（单位：秒），对静态资源建议设置为 1 年（31536000 秒）。

*   **资源更新机制**：通过资源指纹（如文件名哈希）确保内容更新时，浏览器能识别为新资源并重新请求。

*   **缓存范围控制**：使用`public`指令允许代理服务器缓存，扩大缓存范围。

### 二、Cache-Control 头的关键指令



| 指令          | 作用                | 长期缓存场景是否必选 |
| ----------- | ----------------- | ---------- |
| `public`    | 允许客户端和代理服务器缓存     | 是（提升缓存利用率） |
| `max-age`   | 指定缓存有效期（秒）        | 是（核心指令）    |
| `immutable` | 声明资源不会变化，避免不必要的验证 | 否（推荐，优化体验） |

### 三、不同服务器的配置示例

#### 1. Nginx 配置



```
\# 匹配静态资源文件（图片、CSS、JS、字体等）

location \~\* \\.(jpg|jpeg|png|gif|ico|css|js|woff2|woff|ttf)\$ {

&#x20; \# 设置Cache-Control头：公开缓存，有效期1年

&#x20; add\_header Cache-Control "public, max-age=31536000, immutable";

&#x20;&#x20;

&#x20; \# 兼容HTTP/1.0的Expires头（1年后过期）

&#x20; expires 31536000s;

&#x20;&#x20;

&#x20; \# 关闭ETag（资源指纹已确保更新，减少服务器计算开销）

&#x20; etag off;

&#x20;&#x20;

&#x20; \# 关闭Last-Modified（同理，依赖资源指纹更新）

&#x20; if\_modified\_since off;

}
```



*   注释：`~*`表示不区分大小写匹配文件后缀；`immutable`告诉浏览器资源不会变，无需在缓存期内发起验证请求。

#### 2. Apache 配置



```
\# 启用mod\_expires和mod\_headers模块

\<IfModule mod\_expires.c>

&#x20; ExpiresActive On

&#x20;&#x20;

&#x20; \# 图片资源缓存1年

&#x20; \<FilesMatch "\\.(jpg|jpeg|png|gif|ico)\$">

&#x20;   Header set Cache-Control "public, max-age=31536000, immutable"

&#x20;   ExpiresDefault "access plus 1 year"

&#x20; \</FilesMatch>

&#x20;&#x20;

&#x20; \# CSS和JS缓存1年

&#x20; \<FilesMatch "\\.(css|js)\$">

&#x20;   Header set Cache-Control "public, max-age=31536000, immutable"

&#x20;   ExpiresDefault "access plus 1 year"

&#x20; \</FilesMatch>

&#x20;&#x20;

&#x20; \# 字体文件缓存1年

&#x20; \<FilesMatch "\\.(woff2|woff|ttf)\$">

&#x20;   Header set Cache-Control "public, max-age=31536000, immutable"

&#x20;   ExpiresDefault "access plus 1 year"

&#x20; \</FilesMatch>

\</IfModule>
```



*   注释：`ExpiresDefault`用于兼容不支持`max-age`的旧浏览器，优先级低于`Cache-Control`。

#### 3. Node.js（Express 框架）配置



```
const express = require('express');

const app = express();

const path = require('path');

// 配置静态资源目录（如public文件夹）

app.use('/static', express.static(path.join(\_\_dirname, 'public'), {

&#x20; // 缓存选项

&#x20; maxAge: '31536000s', // 等价于max-age=31536000

&#x20; setHeaders: (res, path) => {

&#x20;   // 对静态资源设置完整的Cache-Control头

&#x20;   res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');

&#x20;  &#x20;

&#x20;   // 对不同类型的文件可单独调整（可选）

&#x20;   if (path.endsWith('.html')) {

&#x20;     // HTML通常不建议长期缓存，此处仅为示例

&#x20;     res.setHeader('Cache-Control', 'public, max-age=86400'); // 1天

&#x20;   }

&#x20; }

}));

app.listen(3000, () => {

&#x20; console.log('服务器运行在端口3000');

});
```



*   注释：`express.static`的`maxAge`选项会自动添加`Cache-Control: max-age=xxx`，但需通过`setHeaders`补充`public`和`immutable`。

### 四、资源指纹的实现（确保更新生效）

资源指纹是长期缓存的关键补充，当资源内容变化时，文件名哈希自动更新，浏览器会视为新资源并重新请求。

#### Webpack 配置示例



```
// webpack.config.js

module.exports = {

&#x20; output: {

&#x20;   // 对JS文件添加内容哈希（8位）

&#x20;   filename: 'js/\[name].\[contenthash:8].js',

&#x20;   // 对图片等资源添加哈希

&#x20;   assetModuleFilename: 'assets/\[name].\[hash:8]\[ext]'

&#x20; },

&#x20; module: {

&#x20;   rules: \[

&#x20;     {

&#x20;       test: /\\.(png|jpg|jpeg|gif)\$/i,

&#x20;       type: 'asset/resource' // 输出为单独文件

&#x20;     }

&#x20;   ]

&#x20; }

};
```



*   构建后生成的文件示例：`js/main.8f3d7a2b.js`、`assets/logo.1c2d3e4f.png`。

*   原理：`contenthash`基于文件内容计算，内容不变则哈希不变，确保缓存有效；内容变化则哈希变化，触发重新下载。

### 五、注意事项



1.  **避免缓存动态资源**：HTML 页面、API 接口等动态内容不应设置长期缓存，建议使用`no-cache`（需验证）或短期`max-age`。

2.  **缓存清理机制**：若资源需紧急更新（如修复 bug），可通过修改资源指纹强制失效，或在 URL 后添加版本参数（如`style.css?v=2`）。

3.  **浏览器兼容性**：`immutable`指令在 IE 中不支持，但不影响基本缓存功能；`max-age`在所有现代浏览器和 IE9 + 中支持。

4.  **HTTPS 环境**：长期缓存的资源建议通过 HTTPS 传输，避免中间人攻击篡改缓存内容。

### 总结

通过`Cache-Control: public, max-age=31536000`可实现静态资源的 1 年长期缓存，配合资源指纹确保内容更新时能被正确获取。不同服务器的配置需注意指令的完整性和兼容性，同时区分静态与动态资源的缓存策略，平衡性能与准确性。

