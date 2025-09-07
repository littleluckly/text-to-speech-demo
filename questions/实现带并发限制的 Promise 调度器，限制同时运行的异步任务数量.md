# 实现带并发限制的 Promise 调度器，限制同时运行的异步任务数量。

## meta 元数据



```
{

&#x20; "id": "c9d0e1f2-a3b4-5678-cdef-90abcdef1234",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["javascript"]

}
```

## 答案 1：核心简洁的口语化回答

・并发限制的 Promise 调度器需控制同时运行的异步任务数量，超出限制的任务进入等待队列。

・核心思路：维护一个计数器记录当前运行的任务数，任务完成后从队列取新任务执行。

・实现要点：创建调度器类，提供添加任务的方法，内部管理等待队列，当任务完成（无论成功失败）时触发下一个任务。

・关键逻辑：新任务添加时，若当前运行数未达限制则立即执行，否则入队；任务结束后计数器减 1，并从队列取任务执行。

## 答案 2：口语化扩展回答

带并发限制的 Promise 调度器主要解决同时运行的异步任务过多的问题，比如限制最多 3 个任务同时执行，其他任务得排队等着。

实现时，首先得有个计数器，记录当前正在跑的任务有多少个。然后需要一个队列，用来存那些暂时不能执行的任务。当添加新任务时，先看看当前运行的任务数有没有达到限制。如果没到，就直接执行这个任务，同时把计数器加 1；如果到了，就把任务放到队列里等着。

每个任务执行完之后（不管是成功还是失败），都要把计数器减 1，然后检查队列里有没有等待的任务，如果有，就从队列里拿出一个来执行，同时更新计数器。这样就能保证始终只有指定数量的任务在同时运行。

实际用的时候，只要创建调度器实例并指定并发数，然后通过 add 方法添加任务就行，添加的任务会自动按规则执行，最后能通过 Promise 获取所有任务的执行结果。

## 答案 3：技术深度解析

### 需求分析与核心思路

在实际开发中，当需要处理大量异步任务（如并发请求接口）时，无限制的并发可能导致系统资源耗尽或触发服务器限流。带并发限制的 Promise 调度器可控制同时执行的任务数量，既保证执行效率，又避免资源过载。

**核心需求**：



*   限制同时运行的异步任务数量（如最多同时运行 3 个）

*   超出限制的任务进入等待队列，待有任务完成后按顺序执行

*   支持获取所有任务的执行结果（成功 / 失败）

*   提供添加任务和启动调度的接口

**实现思路**：



1.  维护一个计数器（`runningCount`），记录当前正在执行的任务数量

2.  维护一个等待队列（`taskQueue`），存储暂时无法执行的任务

3.  当添加任务时，若当前运行数未达限制则立即执行，否则入队

4.  每个任务完成后（无论成功 / 失败），触发后续逻辑：

*   计数器减 1

*   从等待队列中取出一个任务执行（若有）

*   重复上述过程直至队列清空

### 完整实现代码



```
class Scheduler {

&#x20; /\*\*

&#x20;  \* 创建带并发限制的Promise调度器

&#x20;  \* @param {number} concurrency - 最大并发数，必须为正整数

&#x20;  \*/

&#x20; constructor(concurrency) {

&#x20;   if (typeof concurrency !== 'number' || concurrency < 1 || !Number.isInteger(concurrency)) {

&#x20;     throw new Error('并发数必须是正整数');

&#x20;   }

&#x20;   this.concurrency = concurrency; // 最大并发数

&#x20;   this.runningCount = 0; // 当前运行的任务数

&#x20;   this.taskQueue = \[]; // 等待执行的任务队列

&#x20;   this.results = \[]; // 存储所有任务的结果

&#x20;   this.allTasksCompleted = false; // 是否所有任务都已完成

&#x20;   this.resolveAll = null; // 用于标记所有任务完成的Promise resolver

&#x20; }

&#x20; /\*\*

&#x20;  \* 添加任务到调度器

&#x20;  \* @param {Function} task - 返回Promise的函数，代表异步任务

&#x20;  \* @returns {Promise} 该任务的执行结果Promise

&#x20;  \*/

&#x20; add(task) {

&#x20;   // 验证任务格式：必须是返回Promise的函数

&#x20;   if (typeof task !== 'function') {

&#x20;     throw new Error('任务必须是返回Promise的函数');

&#x20;   }

&#x20;   return new Promise((resolve, reject) => {

&#x20;     // 将任务和其resolve/reject包装后加入队列

&#x20;     this.taskQueue.push({

&#x20;       task,

&#x20;       resolve,

&#x20;       reject

&#x20;     });

&#x20;     // 尝试执行任务（首次添加时触发）

&#x20;     this.runNext();

&#x20;   });

&#x20; }

&#x20; /\*\*

&#x20;  \* 尝试执行下一个任务

&#x20;  \*/

&#x20; runNext() {

&#x20;   // 如果已达最大并发数，或没有等待任务，则退出

&#x20;   if (this.runningCount >= this.concurrency || this.taskQueue.length === 0) {

&#x20;     return;

&#x20;   }

&#x20;   // 从队列头部取出一个任务

&#x20;   const { task, resolve, reject } = this.taskQueue.shift();

&#x20;   this.runningCount++; // 增加运行计数器

&#x20;   // 执行任务

&#x20;   Promise.resolve()

&#x20;     .then(() => task()) // 执行异步任务

&#x20;     .then(result => {

&#x20;       resolve(result); // 解析当前任务的Promise

&#x20;       this.results.push({ status: 'fulfilled', value: result });

&#x20;       return result;

&#x20;     })

&#x20;     .catch(error => {

&#x20;       reject(error); // 拒绝当前任务的Promise

&#x20;       this.results.push({ status: 'rejected', reason: error });

&#x20;       return error;

&#x20;     })

&#x20;     .finally(() => {

&#x20;       this.runningCount--; // 减少运行计数器

&#x20;       // 递归执行下一个任务

&#x20;       this.runNext();

&#x20;       // 检查是否所有任务都已完成

&#x20;       if (this.runningCount === 0 && this.taskQueue.length === 0) {

&#x20;         this.allTasksCompleted = true;

&#x20;         if (this.resolveAll) {

&#x20;           this.resolveAll(this.results);

&#x20;         }

&#x20;       }

&#x20;     });

&#x20; }

&#x20; /\*\*

&#x20;  \* 等待所有任务完成

&#x20;  \* @returns {Promise} 所有任务完成后的结果数组

&#x20;  \*/

&#x20; waitAll() {

&#x20;   // 如果所有任务已完成，直接返回结果

&#x20;   if (this.allTasksCompleted) {

&#x20;     return Promise.resolve(this.results);

&#x20;   }

&#x20;   // 否则返回一个Promise，等待所有任务完成

&#x20;   return new Promise(resolve => {

&#x20;     this.resolveAll = resolve;

&#x20;   });

&#x20; }

}
```

### 代码解析

#### 1. 类结构设计



*   **核心属性**：


    *   `concurrency`：最大并发数，通过构造函数初始化

    *   `runningCount`：实时跟踪当前运行的任务数量

    *   `taskQueue`：存储等待执行的任务（包含任务函数和其 resolve/reject）

    *   `results`：收集所有任务的执行结果（成功 / 失败）

    *   `resolveAll`：用于实现`waitAll`方法的 Promise resolver

*   **核心方法**：


    *   `constructor`：初始化并发数和内部状态

    *   `add`：添加任务到队列并尝试执行

    *   `runNext`：从队列取任务执行（核心调度逻辑）

    *   `waitAll`：返回等待所有任务完成的 Promise

#### 2. 任务调度流程



1.  **任务添加阶段**：

*   调用`add`方法时，任务被包装成包含 resolve/reject 的对象

*   任务被加入`taskQueue`等待执行

*   立即调用`runNext`尝试执行任务

1.  **任务执行阶段**：

*   `runNext`检查当前运行数是否小于并发限制

*   若可执行，则从队列取任务，`runningCount`加 1

*   执行任务函数并监听其 Promise 状态

1.  **任务完成阶段**：

*   任务成功：调用 resolve，记录成功结果

*   任务失败：调用 reject，记录失败原因

*   `finally`中`runningCount`减 1，递归调用`runNext`

*   若所有任务完成，触发`waitAll`的 resolve

### 使用示例



```
// 创建一个最大并发数为2的调度器

const scheduler = new Scheduler(2);

// 生成模拟异步任务的函数

function createTask(id, delay) {

&#x20; return () => new Promise(resolve => {

&#x20;   console.log(\`任务\${id}开始执行\`);

&#x20;   setTimeout(() => {

&#x20;     console.log(\`任务\${id}执行完成\`);

&#x20;     resolve(\`任务\${id}的结果\`);

&#x20;   }, delay);

&#x20; });

}

// 添加5个任务

scheduler.add(createTask(1, 1000));

scheduler.add(createTask(2, 500));

scheduler.add(createTask(3, 800));

scheduler.add(createTask(4, 1200));

scheduler.add(createTask(5, 300));

// 等待所有任务完成并输出结果

scheduler.waitAll().then(results => {

&#x20; console.log('所有任务完成，结果：');

&#x20; console.log(results);

});
```

**执行输出**：



```
任务1开始执行

任务2开始执行

任务2执行完成

任务3开始执行

任务1执行完成

任务4开始执行

任务3执行完成

任务5开始执行

任务5执行完成

任务4执行完成

所有任务完成，结果：

\[

&#x20; { status: 'fulfilled', value: '任务1的结果' },

&#x20; { status: 'fulfilled', value: '任务2的结果' },

&#x20; { status: 'fulfilled', value: '任务3的结果' },

&#x20; { status: 'fulfilled', value: '任务4的结果' },

&#x20; { status: 'fulfilled', value: '任务5的结果' }

]
```

### 进阶优化与扩展



1.  **支持动态调整并发数**：



```
setConcurrency(newConcurrency) {

&#x20; if (typeof newConcurrency !== 'number' || newConcurrency < 1 || !Number.isInteger(newConcurrency)) {

&#x20;   throw new Error('新并发数必须是正整数');

&#x20; }

&#x20; this.concurrency = newConcurrency;

&#x20; // 调整后尝试执行等待任务

&#x20; this.runNext();

}
```



1.  **添加任务取消功能**：



```
// 在add方法中返回取消函数

add(task) {

&#x20; let isCancelled = false;

&#x20; const cancel = () => {

&#x20;   isCancelled = true;

&#x20; };

&#x20; const promise = new Promise((resolve, reject) => {

&#x20;   this.taskQueue.push({

&#x20;     task,

&#x20;     resolve: (result) => !isCancelled && resolve(result),

&#x20;     reject: (error) => !isCancelled && reject(error),

&#x20;     isCancelled: () => isCancelled

&#x20;   });

&#x20;   this.runNext();

&#x20; });

&#x20; return { promise, cancel };

}

// 在runNext中检查任务是否已取消

runNext() {

&#x20; // 清理已取消的任务

&#x20; while (this.taskQueue.length > 0 && this.taskQueue\[0].isCancelled()) {

&#x20;   this.taskQueue.shift();

&#x20; }

&#x20; // ... 剩余逻辑不变

}
```



1.  **错误处理增强**：

*   支持全局错误监听

*   支持任务失败后是否继续执行后续任务的配置

### 实际应用场景



1.  **批量接口请求**：限制同时发起的 API 请求数量，避免触发服务器限流

2.  **文件上传 / 下载**：控制同时传输的文件数量，优化带宽利用

3.  **资源密集型任务**：如图片处理、数据计算等，避免 CPU / 内存占用过高

4.  **爬虫程序**：控制对目标网站的请求频率，防止被封禁 IP

带并发限制的 Promise 调度器是异步编程中的重要工具，通过合理控制并发量，既能保证执行效率，又能避免资源耗尽或触发限制，是处理批量异步任务的理想方案。

