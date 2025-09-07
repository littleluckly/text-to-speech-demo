# 解释 Intersection Observer API 的作用，如何用它实现图片懒加载？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890b4",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["性能优化"]

}
```

## 答案 1：核心简洁的口语化回答

・Intersection Observer API 用于监听元素与视口或父元素的交叉状态（是否可见、可见比例），无需频繁触发滚动事件，性能更优。

・实现图片懒加载：将图片真实地址存放在`data-src`属性，用占位图作为`src`；通过该 API 监听图片元素，当元素进入视口时，将`data-src`的值赋给`src`，加载真实图片。

・优势：避免滚动事件的高频触发，减少浏览器性能消耗，提升页面流畅度。

## 答案 2：口语化扩展回答

Intersection Observer API 就像一个 “观察者”，能自动监测目标元素是否进入了视口，或者和某个父元素产生了交叉。以前要判断元素是否可见，得监听滚动事件，然后用一堆计算来判断位置，不仅代码麻烦，还容易因为频繁触发事件导致页面卡顿。而这个 API 能在后台异步监测，不会阻塞主线程，性能好很多。

用它实现图片懒加载很合适。原理就是先不给图片设置真实的`src`，而是存在`data-src`里，先用一张小的占位图或者空白图顶着。然后创建一个 Intersection Observer 实例，让它去盯着所有需要懒加载的图片。当图片滚动到视口内，也就是观察者发现图片和视口交叉了，就把`data-src`里的地址放到`src`里，图片就会自动加载了。加载完之后，还能把这个观察者给断开，避免不必要的监听，更省资源。这样一来，页面初始加载时不用一次性加载所有图片，尤其是长页面，能大大减少一开始的请求量，加快页面加载速度。

## 答案 3：技术深度解析

### 1. Intersection Observer API 的核心作用与原理

#### 1.1 定义与核心功能

Intersection Observer API 是浏览器提供的**异步监测元素交叉状态**的 API，用于判断目标元素是否可见（与视口或指定祖先元素产生交叉），以及可见区域的比例。其核心作用是替代传统的`scroll`/`resize`事件监听，解决频繁触发回调导致的性能问题。

#### 1.2 工作原理



*   **异步监测**：监测逻辑在浏览器主线程之外执行，不会阻塞页面渲染。

*   **交叉阈值**：可设置触发回调的可见比例阈值（如元素可见 50% 时触发）。

*   **自动处理**：无需手动计算元素位置（如`getBoundingClientRect()`），API 内部自动完成交叉状态判断。

#### 1.3 与传统滚动监听的对比



| 方案        | 传统`scroll`事件监听     | Intersection Observer API |
| --------- | ------------------ | ------------------------- |
| **性能**    | 高频触发（如每秒数十次），易导致卡顿 | 仅在交叉状态变化时触发，性能优异          |
| **代码复杂度** | 需手动计算元素位置和可见性      | 自动处理交叉判断，代码简洁             |
| **适用场景**  | 简单可见性判断（兼容性要求极高时）  | 复杂懒加载、无限滚动、曝光统计等          |

### 2. 利用 Intersection Observer API 实现图片懒加载

图片懒加载是指**仅当图片进入视口时才加载真实资源**，减少初始加载的请求数量和带宽消耗，提升页面加载速度。

#### 2.1 实现步骤

##### 步骤 1：HTML 结构准备



*   图片的真实地址存储在`data-src`（或自定义属性）中。

*   `src`属性使用占位图（如 1x1 像素的透明图），避免初始加载无效资源。

*   为懒加载图片添加统一类名（如`lazy-img`），便于批量选择。



```
\<!-- 懒加载图片示例 -->

\<img class="lazy-img"&#x20;

&#x20;    src="placeholder.png"  \<!-- 占位图 -->

&#x20;    data-src="real-image-1.jpg"  \<!-- 真实图片地址 -->

&#x20;    alt="示例图片">

\<img class="lazy-img"&#x20;

&#x20;    src="placeholder.png"&#x20;

&#x20;    data-src="real-image-2.jpg"&#x20;

&#x20;    alt="示例图片">
```

##### 步骤 2：创建 Intersection Observer 实例



*   定义回调函数：当元素交叉状态变化时触发，处理图片加载逻辑。

*   配置选项：设置监测根元素（默认是视口）、触发阈值、根元素边距等。



```
// 回调函数：当元素可见性变化时执行

const handleIntersect = (entries, observer) => {

&#x20; entries.forEach(entry => {

&#x20;   // 元素进入视口（isIntersecting为true）

&#x20;   if (entry.isIntersecting) {

&#x20;     const img = entry.target; // 获取目标图片元素

&#x20;     // 加载真实图片

&#x20;     img.src = img.dataset.src;

&#x20;     // 图片加载完成后，停止监听该元素（避免重复触发）

&#x20;     observer.unobserve(img);

&#x20;   }

&#x20; });

};

// 配置选项

const options = {

&#x20; root: null, // 根元素为视口

&#x20; rootMargin: '0px 0px 200px 0px', // 提前200px开始加载（优化体验）

&#x20; threshold: 0.1 // 元素可见比例达到10%时触发

};

// 创建观察者实例

const imageObserver = new IntersectionObserver(handleIntersect, options);
```

##### 步骤 3：监听目标图片元素



*   选择所有需要懒加载的图片，通过`observe()`方法交由观察者监测。



```
// 获取所有懒加载图片

const lazyImages = document.querySelectorAll('.lazy-img');

// 逐个监听图片元素

lazyImages.forEach(img => {

&#x20; imageObserver.observe(img);

});
```

#### 2.2 高级优化与细节处理



*   **处理图片加载错误**：为图片添加`error`事件监听，加载失败时显示备用图片。



```
img.addEventListener('error', () => {

&#x20; img.src = 'fallback-image.jpg'; // 加载失败时显示备用图

});
```



*   **支持 WebP 等现代格式**：结合`picture`标签实现图片格式降级，提升加载性能。



```
\<picture>

&#x20; \<source data-srcset="image.webp" type="image/webp">

&#x20; \<img class="lazy-img" src="placeholder.png" data-src="image.jpg" alt="示例">

\</picture>
```

对应的 JS 处理需同时更新`source`的`srcset`：



```
if (entry.isIntersecting) {

&#x20; const picture = entry.target.closest('picture');

&#x20; if (picture) {

&#x20;   const source = picture.querySelector('source');

&#x20;   source.srcset = source.dataset.srcset; // 加载source的真实资源

&#x20; }

&#x20; const img = entry.target;

&#x20; img.src = img.dataset.src;

&#x20; observer.unobserve(img);

}
```



*   **清理观察者**：页面卸载或图片容器销毁时，调用`disconnect()`停止所有监听，避免内存泄漏。



```
// 组件卸载时

imageObserver.disconnect();
```

#### 2.3 兼容性处理

Intersection Observer API 兼容现代浏览器（Chrome 51+、Firefox 55+、Edge 15+），对于低版本浏览器（如 IE），可使用 polyfill（如`intersection-observer`）实现兼容。

安装 polyfill：



```
npm install intersection-observer
```

引入并使用：



```
import 'intersection-observer'; // 引入polyfill后即可正常使用API
```

### 3. Intersection Observer API 的其他应用场景



*   **无限滚动**：监听滚动容器底部元素，当元素可见时加载更多内容。

*   **曝光统计**：统计广告、文章等元素在视口中的曝光时长和次数。

*   **懒加载非图片资源**：如视频、iframe 等，仅在可见时加载。

*   **动态导航样式**：当页面滚动到特定区域时，修改导航栏样式（如背景透明度）。

### 4. 总结

Intersection Observer API 通过异步监测元素交叉状态，解决了传统滚动监听的性能问题，是前端性能优化的重要工具。利用它实现图片懒加载时，只需通过`data-*`属性存储真实资源地址，创建观察者监听图片元素，在元素进入视口时加载资源，不仅代码简洁，还能显著减少初始加载资源，提升页面性能。除图片懒加载外，该 API 还可应用于无限滚动、曝光统计等多种场景，是前端开发者必备的性能优化手段。

