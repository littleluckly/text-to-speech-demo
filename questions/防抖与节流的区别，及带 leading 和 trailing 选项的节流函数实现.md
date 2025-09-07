# 防抖与节流的区别，及带 leading 和 trailing 选项的节流函数实现

## meta 元数据



```
{

&#x20; "id": "d5e6f7g8-h9i0-1234-jklm-6789012345op",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["javascript"]

}
```

## 答案 1：核心简洁的口语化回答

・防抖：触发事件后，延迟 n 秒执行函数，若 n 秒内再次触发则重新计时，最终只执行最后一次。

・节流：触发事件后立即执行函数，之后 n 秒内再次触发不执行，n 秒后恢复，保证固定频率执行。

・实现带选项的节流：用时间戳或定时器判断，leading 控制是否立即执行，trailing 控制是否延迟执行，需处理两者同时为 true 时的冲突。

## 答案 2：口语化扩展回答

防抖和节流都是为了限制函数的执行频率，优化性能，但它们的处理方式不一样。防抖就像坐电梯，电梯门开始计时，只要有人进来就重新等 3 秒，直到没人进来才关门运行，最后只执行一次。比如搜索框输入时，等用户停笔了再发请求，避免输入过程中频繁请求。

节流则像水滴，每隔固定时间滴一次，不管中间有多少水积累，频率是固定的。比如滚动页面时，每隔 200 毫秒才计算一次位置，不会因为滚动得快就频繁触发，既保证了响应性，又不会太消耗资源。

要实现带 leading 和 trailing 的节流函数，leading 设为 true 的话，第一次触发就马上执行；trailing 设为 true 的话，结束后会再执行一次。不过两者不能同时都生效，否则可能在间隔结束时多执行一次。实现时用个定时器，记录上次执行时间，每次触发时判断是否过了间隔时间，再根据选项决定是立即执行还是延迟执行。

## 答案 3：技术深度解析

### 防抖与节流的核心区别

#### 1. 执行时机与频率控制



| 特性    | 防抖（Debounce）        | 节流（Throttle）         |
| ----- | ------------------- | -------------------- |
| 核心思想  | 触发后延迟执行，重复触发则重置计时   | 固定时间间隔内只执行一次，保证频率    |
| 执行次数  | 最后一次触发后延迟执行 1 次     | 间隔时间内无论触发多少次都只执行 1 次 |
| 适用场景  | 搜索输入、窗口 resize 最终计算 | 滚动加载、鼠标移动绘图          |
| 时间线示例 | 触发→等待→重置→等待→执行      | 执行→等待→执行→等待→执行       |

**可视化示例**：



*   防抖：`触发---等待---触发---等待---执行`

*   节流：`执行---等待---执行---等待---执行`

#### 2. 代码行为对比



```
// 防抖示例

function debounce(fn, delay) {

&#x20; let timer;

&#x20; return function(...args) {

&#x20;   clearTimeout(timer); // 重置定时器

&#x20;   timer = setTimeout(() => {

&#x20;     fn.apply(this, args);

&#x20;   }, delay);

&#x20; };

}

// 节流示例（时间戳版）

function throttleBasic(fn, interval) {

&#x20; let lastTime = 0;

&#x20; return function(...args) {

&#x20;   const now = Date.now();

&#x20;   if (now - lastTime >= interval) { // 间隔达标

&#x20;     fn.apply(this, args);

&#x20;     lastTime = now;

&#x20;   }

&#x20; };

}
```

### 带 leading 和 trailing 选项的节流函数实现

#### 1. 需求分析



*   `leading`：是否在时间间隔开始时执行（默认 true）

*   `trailing`：是否在时间间隔结束时执行（默认 false）

*   冲突处理：当 `leading` 和 `trailing` 同时为 true 时，需避免间隔结束时多执行一次

#### 2. 实现思路



1.  用 `lastTime` 记录上次执行时间

2.  用 `timer` 管理延迟执行的定时器

3.  触发时计算当前时间与 `lastTime` 的差值：

*   若差值 ≥ 间隔时间：执行函数（leading 逻辑）

*   若差值 < 间隔时间：设置定时器在剩余时间后执行（trailing 逻辑）

1.  清除定时器避免重复执行

#### 3. 完整实现代码



```
/\*\*

&#x20;\* 带 leading 和 trailing 选项的节流函数

&#x20;\* @param {Function} fn - 需要节流的函数

&#x20;\* @param {number} interval - 时间间隔（毫秒）

&#x20;\* @param {Object} options - 配置选项

&#x20;\* @param {boolean} \[options.leading=true] - 是否在间隔开始时执行

&#x20;\* @param {boolean} \[options.trailing=false] - 是否在间隔结束时执行

&#x20;\* @returns {Function} 节流后的函数

&#x20;\*/

function throttle(fn, interval, { leading = true, trailing = false } = {}) {

&#x20; // 记录上次执行时间

&#x20; let lastTime = 0;

&#x20; // 存储定时器ID

&#x20; let timer = null;

&#x20; // 实际执行的函数（绑定上下文和参数）

&#x20; const execute = function(...args) {

&#x20;   // 更新上次执行时间

&#x20;   lastTime = Date.now();

&#x20;   // 执行原函数

&#x20;   fn.apply(this, args);

&#x20; };

&#x20; // 节流处理函数

&#x20; const throttled = function(...args) {

&#x20;   const now = Date.now();

&#x20;   // 首次触发且不启用leading时，初始化lastTime

&#x20;   if (!lastTime && !leading) {

&#x20;     lastTime = now;

&#x20;   }

&#x20;   // 计算距离下次执行的剩余时间

&#x20;   const remainingTime = interval - (now - lastTime);

&#x20;   // 情况1：剩余时间 ≤ 0（已到执行时间点）

&#x20;   if (remainingTime <= 0) {

&#x20;     // 清除可能存在的定时器（避免trailing重复执行）

&#x20;     if (timer) {

&#x20;       clearTimeout(timer);

&#x20;       timer = null;

&#x20;     }

&#x20;     // 执行函数（leading逻辑）

&#x20;     execute.apply(this, args);

&#x20;   }

&#x20;   // 情况2：剩余时间 > 0 且未设置定时器（需要处理trailing）

&#x20;   else if (trailing && !timer) {

&#x20;     // 设置定时器，在剩余时间后执行（trailing逻辑）

&#x20;     timer = setTimeout(() => {

&#x20;       // 执行前清除定时器引用

&#x20;       timer = null;

&#x20;       // 执行函数（注意：这里用lastTime计算，避免多个定时器叠加）

&#x20;       execute.apply(this, args);

&#x20;     }, remainingTime);

&#x20;   }

&#x20; };

&#x20; // 提供取消方法（清除定时器）

&#x20; throttled.cancel = function() {

&#x20;   if (timer) {

&#x20;     clearTimeout(timer);

&#x20;     timer = null;

&#x20;     lastTime = 0; // 重置状态

&#x20;   }

&#x20; };

&#x20; return throttled;

}
```

#### 4. 关键逻辑解析



1.  **leading 执行逻辑**：

*   当 `now - lastTime ≥ interval` 时，立即执行函数

*   首次触发时，若 `leading=true`，则直接执行（`lastTime` 初始为 0）

1.  **trailing 执行逻辑**：

*   当剩余时间 > 0 且 `trailing=true` 时，设置定时器

*   定时器在剩余时间后执行，确保间隔结束时触发一次

1.  **冲突处理**：

*   当 `leading` 和 `trailing` 同时为 true 时：


    *   间隔开始时执行一次（leading）

    *   间隔结束时，若期间有触发，则执行一次（trailing）

    *   通过清除定时器避免重复执行

#### 5. 使用示例



```
// 测试函数

function log(message) {

&#x20; console.log(\`\[\${new Date().toLocaleTimeString()}] \${message}\`);

}

// 1. 默认配置（leading=true, trailing=false）

const throttleDefault = throttle(log, 1000);

// 连续触发时：立即执行，之后1秒内不执行，1秒后可再次执行

// 2. leading=false, trailing=true

const throttleTrailing = throttle(log, 1000, { leading: false, trailing: true });

// 连续触发时：首次不执行，停止触发1秒后执行，之后每1秒执行一次

// 3. leading=true, trailing=true

const throttleBoth = throttle(log, 1000, { leading: true, trailing: true });

// 连续触发时：立即执行，1秒后若有触发则再执行一次

// 模拟连续触发（每300ms触发一次）

let count = 0;

const interval = setInterval(() => {

&#x20; count++;

&#x20; throttleDefault(\`默认配置 \${count}\`);

&#x20; throttleTrailing(\` trailing配置 \${count}\`);

&#x20; throttleBoth(\` 双配置 \${count}\`);

&#x20;&#x20;

&#x20; if (count >= 5) {

&#x20;   clearInterval(interval);

&#x20; }

}, 300);
```

### 节流函数的应用场景与性能考量

#### 1. 典型应用场景



*   **滚动加载**：监听 `scroll` 事件，每隔 200ms 判断是否到达底部



```
window.addEventListener('scroll', throttle(checkLoadMore, 200));
```



*   **鼠标绘图**：监听 `mousemove` 事件，限制绘图频率



```
canvas.addEventListener('mousemove', throttle(drawPoint, 50));
```



*   **按钮点击防重复提交**：限制按钮点击频率



```
button.addEventListener('click', throttle(submitForm, 1000, { trailing: false }));
```

#### 2. 性能优化要点



*   **上下文绑定**：实现时需用 `apply` 保留原函数的 `this` 指向

*   **参数传递**：通过剩余参数 `...args` 确保原函数能接收所有参数

*   **资源释放**：提供 `cancel` 方法清除定时器，避免内存泄漏

*   **边界处理**：


    *   间隔时间为 0 时应直接执行原函数

    *   避免在短时间内创建大量定时器

### 总结

防抖与节流的核心区别在于执行时机：



*   防抖聚焦于 "最后一次触发后执行"，适合处理结束后的收尾操作

*   节流聚焦于 "固定频率执行"，适合处理过程中的连续操作

带 `leading` 和 `trailing` 选项的节流函数实现，通过时间戳计算和定时器控制，可灵活配置执行时机：



*   `leading: true` 确保操作开始时立即响应

*   `trailing: true` 确保操作结束后补充执行

*   需通过清除定时器避免重复执行，处理两者同时启用时的冲突

在实际开发中，应根据业务场景选择合适的频率控制策略，兼顾响应速度与性能消耗，提升用户体验。

