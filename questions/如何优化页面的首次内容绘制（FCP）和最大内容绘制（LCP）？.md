# 如何优化页面的首次内容绘制（FCP）和最大内容绘制（LCP）？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890b2",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["性能优化"]

}
```

## 答案 1：核心简洁的口语化回答

・优化 FCP 需优先加载关键资源，内联首屏 CSS，异步加载非必要脚本，减少关键资源体积。

・提升 LCP 要优化最大内容元素（如图片、文本块），采用懒加载非首屏资源，使用 CDN 加速，压缩图片并选择合适格式。

・减少 DOM 层级和复杂样式，避免阻塞渲染的 CSS/JS，利用浏览器缓存降低重复加载耗时。

## 答案 2：口语化扩展回答

首次内容绘制（FCP）反映页面首次出现内容的速度，最大内容绘制（LCP）则关注页面中最大元素的加载完成时间，两者都是衡量用户体验的重要指标。

优化 FCP 的关键是让浏览器尽快渲染出首屏内容。可以把首屏必需的 CSS 直接嵌在 HTML 里，不用等外部文件下载，非关键的 JS 和 CSS 晚点加载，别挡住渲染。同时压缩 HTML、CSS 这些资源，让它们传输更快，还能通过减少 DOM 嵌套层数，让浏览器解析起来更轻松。

对于 LCP，首先要明确页面里的最大元素是什么，通常是主图或大段文本。图片的话，用压缩后的格式比如 WebP，设置合适尺寸避免缩放，还能通过 CDN 加速传输。如果是文本，确保字体加载不阻塞，可使用字体预加载。另外，非首屏的资源用懒加载，别抢占带宽，服务器开启缓存也能让重复访问时加载更快。

## 答案 3：技术深度解析

### 1. 首次内容绘制（FCP）的优化策略

首次内容绘制（FCP）衡量页面从开始加载到首次出现任何内容（文本、图片、SVG 等）的时间，其核心优化方向是**减少关键资源加载时间**和**加速渲染启动**。

#### 1.1 优化关键资源加载



*   **识别并优先加载关键资源**：


    *   关键资源指首屏渲染必需的 HTML、CSS 和少量 JS（如导航交互逻辑），可通过 Chrome DevTools 的**Performance 面板**分析确定。

    *   内联关键 CSS 到`<style>`标签，避免额外 HTTP 请求：



```
\<head>

&#x20; \<style>

&#x20;   /\* 仅包含首屏必需样式，如导航、标题、主图容器 \*/

&#x20;   .header { width: 100%; height: 60px; }

&#x20;   .hero-image { max-width: 100%; }

&#x20; \</style>

\</head>
```



*   **异步加载非关键资源**：


    *   非首屏 CSS（如页脚样式、弹窗样式）使用`media="print"`标记为非阻塞资源，加载完成后切换生效：



```
\<link rel="stylesheet" href="non-critical.css" media="print" onload="this.media='all'">
```



*   非关键 JS（如统计脚本、广告脚本）使用`async`或`defer`属性，避免阻塞 DOM 解析：



```
\<script src="analytics.js" async>\</script> \<!-- 下载完成后立即执行 -->

\<script src="ads.js" defer>\</script> \<!-- DOM解析完成后执行 -->
```



*   **减小关键资源体积**：


    *   压缩 HTML/CSS/JS：使用 Gzip 或 Brotli 压缩（Brotli 压缩率通常比 Gzip 高 15%-20%）。

    *   移除冗余代码：通过**PurgeCSS**清理未使用的 CSS，通过 Webpack 的 Tree-shaking 删除 JS 死代码。

#### 1.2 加速渲染启动



*   **减少 DOM 解析时间**：


    *   简化 HTML 结构，避免嵌套层级过深（建议不超过 6 层），减少无意义的包裹元素（如空`<div>`）。

    *   延迟加载非首屏内容：通过`<template>`标签暂存非首屏 DOM，在首屏渲染完成后动态插入。

*   **避免渲染阻塞**：


    *   将 JS 脚本放在`</body>`前，或使用`async`/`defer`，防止 JS 下载 / 执行阻塞 DOM 解析。

    *   避免在`<head>`中使用`document.write()`，其会阻断 HTML 解析并可能导致资源重新请求。

### 2. 最大内容绘制（LCP）的优化策略

最大内容绘制（LCP）衡量页面从开始加载到最大内容元素（通常是主图、大段文本或视频）完全渲染的时间，优化核心是**加速最大内容元素的加载与渲染**。

#### 2.1 优化最大内容元素（图片场景）



*   **选择高效图片格式**：


    *   优先使用 WebP 或 AVIF 格式，相比 JPEG/PNG 压缩率提升 25%-50%，且支持透明和动画：



```
\<picture>

&#x20; \<source srcset="hero.avif" type="image/avif">

&#x20; \<source srcset="hero.webp" type="image/webp">

&#x20; \<img src="hero.jpg" alt="主图"> \<!-- 降级方案 -->

\</picture>
```



*   **控制图片尺寸与加载**：


    *   提前设置图片尺寸（`width`/`height`属性），避免布局偏移（CLS）导致的二次渲染：



```
\<img src="hero.jpg" width="800" height="400" alt="主图"> \<!-- 明确尺寸 -->
```



*   使用`srcset`和`sizes`属性提供响应式图片，避免加载过大尺寸的图片：



```
\<img&#x20;

&#x20; srcset="hero-small.jpg 400w, hero-large.jpg 800w"

&#x20; sizes="(max-width: 600px) 400px, 800px"

&#x20; src="hero-large.jpg"&#x20;

&#x20; alt="主图"

\>
```



*   预加载 LCP 图片：对确定的 LCP 图片使用`rel="preload"`提前加载：



```
\<link rel="preload" as="image" href="hero.jpg" fetchpriority="high">
```

（`fetchpriority="high"`可提升资源优先级，优先于其他非关键资源）

#### 2.2 优化最大内容元素（文本场景）



*   **加速字体加载**：


    *   内联关键字体（如标题字体）的 WOFF2 格式到 CSS，减少字体请求：



```
@font-face {

&#x20; font-family: 'TitleFont';

&#x20; src: url('title-font.woff2') format('woff2');

&#x20; font-display: swap; /\* 字体加载期间使用系统字体替代 \*/

}
```



*   使用`font-display: swap`确保文本优先显示（即使字体未加载完成），避免 “无文本闪烁”。

<!---->

*   **优化文本渲染**：


    *   避免文本被动态插入（如通过 JS 添加文本内容），确保 HTML 解析时直接包含文本。

    *   减少文本容器的嵌套层级，降低浏览器计算文本布局的时间。

#### 2.3 通用加载优化



*   **使用 CDN 加速资源传输**：


    *   将静态资源（图片、CSS、JS）部署到 CDN，利用边缘节点减少用户与服务器的物理距离，降低网络延迟。

    *   配置 CDN 的缓存策略（如`Cache-Control: max-age=31536000`），减少重复请求。

*   **启用 HTTP/2 或 HTTP/3**：


    *   HTTP/2 的多路复用可并行加载多个资源，减少 TCP 连接建立成本；HTTP/3 基于 QUIC 协议，进一步降低延迟。

*   **懒加载非首屏资源**：


    *   对非首屏图片和视频使用`loading="lazy"`属性，延迟加载直到用户滚动到可视区域：



```
\<img src="below-fold.jpg" loading="lazy" alt="非首屏图片">
```

### 3. 共同优化策略

#### 3.1 服务器层面优化



*   **启用压缩与缓存**：


    *   配置服务器的 Gzip/Brotli 压缩（如 Nginx 的`gzip on;`和`brotli on;`）。

    *   设置合理的缓存头（`Cache-Control`、`ETag`），对静态资源长期缓存，对 HTML 设置短期缓存或不缓存。

*   **减少 TTFB（首字节时间）**：


    *   使用服务器端缓存（如 Redis）减少动态内容生成时间。

    *   采用边缘计算（如 Cloudflare Workers）在边缘节点处理部分请求，降低回源频率。

#### 3.2 监控与迭代



*   **使用性能监控工具**：


    *   通过**Chrome Lighthouse**定期审计 FCP 和 LCP 指标。

    *   接入**Web Vitals** API 实时监控用户真实体验：



```
import { getFCP, getLCP } from 'web-vitals';

getFCP(metric => console.log('FCP:', metric.value));

getLCP(metric => console.log('LCP:', metric.value));
```



*   **持续迭代优化**：


    *   针对监控数据中的慢加载资源，分析原因（如体积过大、请求次数多）并优化。

    *   A/B 测试不同优化方案（如不同图片格式、不同缓存策略），选择最优解。

### 4. 总结

FCP 和 LCP 的优化核心是**减少关键资源加载时间**和**加速核心内容渲染**。FCP 优化需聚焦首屏关键资源的优先级和体积，LCP 优化则需针对性提升最大内容元素的加载效率。通过资源压缩、异步加载、CDN 加速、服务器优化等手段，结合持续的性能监控与迭代，可显著提升这两个指标，改善用户的页面加载体验。

