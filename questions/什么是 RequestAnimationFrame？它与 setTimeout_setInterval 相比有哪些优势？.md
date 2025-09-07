# 什么是 RequestAnimationFrame？它与 setTimeout/setInterval 相比有哪些优势？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890b5",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["浏览器","性能优化"]

}
```

## 答案 1：核心简洁的口语化回答

・RequestAnimationFrame 是浏览器提供的用于定时执行动画的 API，它能让回调函数与浏览器的刷新频率同步（通常 60 次 / 秒）。

・相比 setTimeout/setInterval，优势在于：执行时机与浏览器渲染周期匹配，避免卡顿；浏览器后台标签页时会自动降低执行频率，节省性能；无需手动计算延迟时间，动画更流畅。

## 答案 2：口语化扩展回答

RequestAnimationFrame 简单说就是专门为动画设计的定时器，它的作用是让动画代码跟着浏览器的刷新节奏走。浏览器每秒大概刷新 60 次，这个 API 就会保证动画回调在每次刷新前执行，让动画看起来更顺滑。

而 setTimeout 和 setInterval 是通用的定时器，它们靠设定延迟时间（比如 16ms）来模拟动画间隔，但实际执行时间并不准。因为浏览器可能在处理其他任务，导致定时器回调延迟执行，动画就容易出现卡顿或跳帧。而且这两个定时器在页面不可见时（比如切到其他标签页）还会继续跑，白白消耗性能。

RequestAnimationFrame 就聪明多了，它会自动适配浏览器的刷新频率，不用手动算延迟。页面隐藏时，它还会暂停执行，省资源。做动画的时候用它，不仅动画更流畅，还能减少不必要的性能浪费，尤其适合复杂动画场景。

## 答案 3：技术深度解析

### 1. RequestAnimationFrame 的定义与工作原理

#### 1.1 核心定义

RequestAnimationFrame（简称 RAF）是浏览器提供的**专门用于动画渲染的 API**，它允许开发者注册一个回调函数，该函数会在浏览器下一次重绘之前执行。其设计目标是让动画与浏览器的渲染周期保持同步，从而实现更流畅的视觉效果。

#### 1.2 工作流程



*   **注册回调**：通过`requestAnimationFrame(callback)`注册动画回调函数，浏览器会返回一个唯一标识符（ID），用于后续取消回调。

*   **执行时机**：回调函数会在浏览器**重绘前**被调用，执行时机与浏览器的刷新周期（通常为 60Hz，即约 16.7ms / 帧）保持一致。

*   **自动适配**：若浏览器刷新频率发生变化（如从 60Hz 降为 30Hz），RAF 会自动调整回调执行间隔，确保动画速度与视觉刷新匹配。

示例代码：



```
// 定义动画回调

function animate(timestamp) {

&#x20; // timestamp：当前时间戳（毫秒），用于计算动画进度

&#x20; console.log('动画执行，时间戳：', timestamp);

&#x20; // 继续注册下一帧动画

&#x20; requestAnimationFrame(animate);

}

// 启动动画

requestAnimationFrame(animate);
```

### 2. 与 setTimeout/setInterval 的核心差异与优势

#### 2.1 执行时机与渲染同步性



*   **setTimeout/setInterval**：


    *   依赖手动设置延迟时间（如`setTimeout(fn, 16)`），但实际执行时间受主线程繁忙程度影响（如 JavaScript 执行、布局计算等），可能滞后于预期时间。

    *   回调执行与浏览器渲染周期无直接关联，可能导致 “掉帧”（如回调在两次重绘之间执行，导致某帧被跳过）。

*   **RequestAnimationFrame**：


    *   回调执行时机与浏览器重绘周期严格同步，确保每帧只执行一次回调，避免过度绘制。

    *   浏览器会根据当前渲染条件（如页面可见性、硬件性能）动态调整执行频率，例如：


        *   页面处于后台标签页时，RAF 会暂停或降低频率（如降至 1Hz），减少性能消耗。

        *   硬件性能不足时，自动降低帧率（如从 60fps 降至 30fps），避免卡顿。

#### 2.2 性能与资源利用率



*   **setTimeout/setInterval**：


    *   即使页面不可见（如用户切换标签），仍会按设定频率执行回调，浪费 CPU 和电池资源。

    *   若延迟时间设置不合理（如小于 16ms），会导致回调执行次数超过浏览器渲染能力，引发 “过度绘制”，增加主线程负担。

*   **RequestAnimationFrame**：


    *   页面不可见时自动暂停，显著降低后台资源消耗（尤其对移动设备的续航友好）。

    *   回调执行次数与浏览器渲染能力匹配，避免无效计算，减少主线程阻塞风险。

#### 2.3 动画精度与流畅度



*   **setTimeout/setInterval**：


    *   动画进度依赖手动计算时间差（如记录上一次执行时间，计算与当前时间的差值），易因延迟波动导致动画速度不均匀。

    *   示例：



```
let lastTime = 0;

function animate() {

&#x20; const now = Date.now();

&#x20; const deltaTime = now - lastTime; // 手动计算时间差

&#x20; updateAnimation(deltaTime); // 根据时间差更新动画

&#x20; lastTime = now;

&#x20; setTimeout(animate, 16);

}
```



*   **RequestAnimationFrame**：


    *   回调函数接收一个高精度时间戳（`timestamp`），表示当前帧的开始时间，可直接用于计算动画进度，无需手动记录时间。

    *   示例：



```
let start\_time;

function animate(timestamp) {

&#x20; if (!start\_time) start\_time = timestamp;

&#x20; const progress = timestamp - start\_time; // 自动获取精确时间差

&#x20; updateAnimation(progress); // 基于精确进度更新动画

&#x20; requestAnimationFrame(animate);

}
```



*   时间戳由浏览器内核提供，精度可达微秒级，确保动画速度稳定。

#### 2.4 取消机制



*   **setTimeout/setInterval**：通过`clearTimeout`或`clearInterval`取消，需保存定时器 ID。

*   **RequestAnimationFrame**：通过`cancelAnimationFrame(id)`取消，用法类似，但更贴合动画场景的生命周期管理。

示例（取消动画）：



```
// RAF取消示例

const animationId = requestAnimationFrame(animate);

// 取消动画

cancelAnimationFrame(animationId);

// setTimeout取消示例

const timerId = setTimeout(animate, 16);

clearTimeout(timerId);
```

### 3. 适用场景对比



| 场景                       | 推荐 API                | 原因分析              |
| ------------------------ | --------------------- | ----------------- |
| 复杂动画（如 DOM 动画、Canvas 动画） | RequestAnimationFrame | 与渲染周期同步，流畅度高，性能友好 |
| 简单定时任务（如 3 秒后提示）         | setTimeout            | 无需与渲染同步，用法更简单     |
| 周期性非动画任务（如数据轮询）          | setInterval           | 任务执行与渲染无关，需固定间隔执行 |
| 页面可见性相关动画                | RequestAnimationFrame | 自动适配页面可见状态，节省资源   |

### 4. 兼容性与降级方案

RAF 兼容所有现代浏览器（Chrome 10+、Firefox 4+、Edge 12+、Safari 6+），对于 IE9 及以下版本，可使用 setTimeout 实现降级：



```
// 兼容IE的RAF封装

if (!window.requestAnimationFrame) {

&#x20; window.requestAnimationFrame = function(callback) {

&#x20;   const currTime = Date.now();

&#x20;   // 计算距离下一帧的延迟（约16ms）

&#x20;   const delay = Math.max(0, 16 - (currTime - lastTime));

&#x20;   const id = setTimeout(() => {

&#x20;     callback(currTime + delay);

&#x20;   }, delay);

&#x20;   lastTime = currTime + delay;

&#x20;   return id;

&#x20; };

&#x20; window.cancelAnimationFrame = function(id) {

&#x20;   clearTimeout(id);

&#x20; };

}
```

### 5. 总结

RequestAnimationFrame 是专为动画设计的 API，其核心优势在于与浏览器渲染周期的深度协同：通过同步执行时机、动态适配频率、优化资源利用，解决了 setTimeout/setInterval 在动画场景中的卡顿、性能浪费等问题。对于需要流畅视觉效果的动画（如 DOM 过渡、Canvas 游戏、数据可视化），RAF 是首选方案；而对于非动画类定时任务，setTimeout/setInterval 仍更简洁实用。理解三者的差异，能帮助开发者在不同场景下做出最优技术选择，平衡性能与开发效率。

