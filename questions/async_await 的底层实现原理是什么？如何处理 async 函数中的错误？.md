# async/await 的底层实现原理是什么？如何处理 async 函数中的错误？

## meta 元数据



```
{

&#x20; "id": "f6g7h8i9-j0k1-2345-lmno-6789012345pq",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["javascript"]

}
```

## 答案 1：核心简洁的口语化回答

・async/await 底层是基于 Promise 和生成器（Generator）实现的语法糖，让异步代码写法更接近同步

・async 函数执行后返回 Promise 对象，内部返回值会被自动包装为 resolved 状态的 Promise

・await 会暂停当前函数执行，等待后续 Promise 完成，其作用类似 Generator 中的 yield

・错误处理可通过 try/catch 块捕获，也可在 await 后的 Promise 后链式调用 .catch () 方法

・多个 await 语句按顺序执行，前一个完成才会执行下一个，若需并行可结合 Promise.all ()

## 答案 2：口语化扩展回答

async/await 其实是对 Promise 和生成器函数的封装，让异步代码写起来更自然。async 函数一执行就会返回一个 Promise，不管你 return 什么值，都会被自动变成 Promise 对象。就算函数里抛了错误，这个 Promise 也会变成 rejected 状态。

await 关键字得在 async 函数里用，它的作用就是等着后面的 Promise 有结果。在等的时候，函数会暂停，不会卡着整个程序，其他代码还能跑。这背后其实和生成器函数那种暂停、恢复的机制差不多，只是浏览器或 Node.js 帮我们自动处理了，不用像用 Generator 那样手动调用 next () 方法。

处理错误的话，最方便的就是用 try/catch 把 await 包裹起来，不管是 Promise 被 reject 了，还是代码里有同步错误，都能抓到。要是不想用 try/catch，也能在每个 await 后面加个 .catch ()，这样某个异步操作出错了，也不会影响后面的代码执行。不过要注意，多个 await 是一个接一个执行的，要是它们之间没依赖，最好用 Promise.all () 让它们并行跑，不然太浪费时间了。

## 答案 3：技术深度解析

### async/await 底层实现原理

#### 1. 基于 Promise 的封装机制

async/await 并非独立的异步机制，而是完全构建在 Promise 之上，所有 async 函数的返回值都会被强制转换为 Promise 对象：



```
// 示例1：返回基本类型值

async function returnBasicValue() {

&#x20; return 'hello async';

}

// 等价于

function returnBasicValue() {

&#x20; return Promise.resolve('hello async');

}

// 示例2：返回Promise对象

async function returnPromise() {

&#x20; return Promise.resolve('from promise');

}

// 等价于

function returnPromise() {

&#x20; return Promise.resolve('from promise');

}

// 示例3：抛出错误

async function throwError() {

&#x20; throw new Error('something wrong');

}

// 等价于

function throwError() {

&#x20; return Promise.reject(new Error('something wrong'));

}
```

这种封装使得 async 函数可以无缝融入 Promise 生态，支持 .then ()、.catch () 等方法链式调用。

#### 2. 生成器函数的暂停与恢复

async/await 的核心能力 —— 暂停执行与恢复，源自 Generator 函数的特性。以下通过对比展示其内在联系：

**Generator 实现异步流程**：



```
// 定义生成器函数

function\* asyncGenerator() {

&#x20; console.log('开始执行');

&#x20; // 暂停执行，等待Promise完成

&#x20; const result1 = yield fetchData1();&#x20;

&#x20; console.log('第一个请求结果:', result1);

&#x20;&#x20;

&#x20; // 继续暂停，等待下一个Promise

&#x20; const result2 = yield fetchData2(result1);

&#x20; console.log('第二个请求结果:', result2);

&#x20;&#x20;

&#x20; return '完成';

}

// 手动执行生成器

const gen = asyncGenerator();

// 启动生成器，执行到第一个yield

const firstYield = gen.next();&#x20;

// 当第一个Promise完成后，将结果传入并继续执行

firstYield.value.then(data1 => {

&#x20; const secondYield = gen.next(data1);

&#x20; // 处理第二个Promise

&#x20; secondYield.value.then(data2 => {

&#x20;   gen.next(data2);

&#x20; });

});
```

**async/await 与 Generator 的对应关系**：



*   async 函数 ≈ 自带自动执行器的 Generator 函数

*   await 关键字 ≈ Generator 中的 yield 关键字

*   JavaScript 引擎在后台自动完成了 Generator 的 next () 调用和 Promise 状态监听

#### 3. 自动执行器的工作原理

async 函数的便捷性很大程度上来自于内置的自动执行器，其核心逻辑可简化为以下伪代码：



```
// async函数自动执行器伪代码

function asyncExecutor(generatorFunc) {

&#x20; // 创建生成器实例

&#x20; const generator = generatorFunc();

&#x20;&#x20;

&#x20; // 递归处理生成器的暂停与恢复

&#x20; function process(result) {

&#x20;   // 如果生成器已完成，返回最终结果

&#x20;   if (result.done) {

&#x20;     return Promise.resolve(result.value);

&#x20;   }

&#x20;  &#x20;

&#x20;   // 处理当前yield的Promise

&#x20;   return Promise.resolve(result.value)

&#x20;     .then(data => {

&#x20;       // 当Promise成功时，将结果传入并继续执行生成器

&#x20;       return process(generator.next(data));

&#x20;     })

&#x20;     .catch(error => {

&#x20;       // 当Promise失败时，向生成器抛出错误

&#x20;       return process(generator.throw(error));

&#x20;     });

&#x20; }

&#x20;&#x20;

&#x20; // 启动执行器

&#x20; return process(generator.next());

}

// 使用示例

const asyncFunction = async () => {

&#x20; const data1 = await fetchData1();

&#x20; const data2 = await fetchData2(data1);

&#x20; return data2;

};

// 等价于

const generatorFunction = function\* () {

&#x20; const data1 = yield fetchData1();

&#x20; const data2 = yield fetchData2(data1);

&#x20; return data2;

};

const wrappedFunction = () => asyncExecutor(generatorFunction);
```

这个自动执行器实现了 Promise 状态与生成器执行状态的自动同步，无需手动干预。

### async 函数中的错误处理机制

#### 1. try/catch 块捕获所有错误

try/catch 是处理 async 函数错误最常用的方式，能够捕获以下类型的错误：



*   await 表达式中被 reject 的 Promise

*   函数内部的同步错误

*   其他函数调用抛出的错误



```
async function comprehensiveErrorHandling() {

&#x20; try {

&#x20;   // 捕获被reject的Promise

&#x20;   const invalidData = await Promise.reject(new Error('数据请求失败'));

&#x20;  &#x20;

&#x20;   // 以下代码不会执行，因为上面已经出错

&#x20;   const syncError = 1 / undefined; // 同步错误示例

&#x20;  &#x20;

&#x20;   // 调用可能抛出错误的函数

&#x20;   validateData(invalidData);

&#x20; } catch (error) {

&#x20;   // 所有错误都会被捕获到这里

&#x20;   console.error('捕获到错误:', error.message);

&#x20;   // 可以根据错误类型进行不同处理

&#x20;   if (error.message.includes('数据请求')) {

&#x20;     console.log('尝试使用缓存数据');

&#x20;   } else {

&#x20;     console.log('执行默认错误处理');

&#x20;   }

&#x20; }

}

comprehensiveErrorHandling();
```

#### 2. 单个 await 表达式的 .catch () 处理

在 await 后直接链式调用 .catch () 可以单独处理当前异步操作的错误，不影响后续代码执行：



```
async function individualErrorHandling() {

&#x20; // 处理单个异步操作的错误

&#x20; const userData = await fetchUserData()

&#x20;   .catch(error => {

&#x20;     console.error('获取用户数据失败:', error.message);

&#x20;     return { id: 'guest', name: '游客' }; // 返回默认值

&#x20;   });

&#x20;&#x20;

&#x20; // 即使上面出错，这里仍会继续执行

&#x20; console.log('当前用户:', userData.name);

&#x20;&#x20;

&#x20; // 另一个异步操作，使用不同的错误处理

&#x20; const products = await fetchProducts()

&#x20;   .catch(error => {

&#x20;     console.error('获取产品列表失败:', error.message);

&#x20;     throw new Error('无法加载产品，请稍后重试'); // 重新抛出错误

&#x20;   });

&#x20;&#x20;

&#x20; return { userData, products };

}

// 调用时仍需处理可能被重新抛出的错误

individualErrorHandling()

&#x20; .catch(error => {

&#x20;   console.error('操作最终失败:', error.message);

&#x20; });
```

#### 3. 并行异步操作的错误处理

使用 Promise.all () 处理并行操作时，任何一个 Promise 被 reject 都会导致整体失败，需特殊处理：



```
async function parallelErrorHandling() {

&#x20; // 方法1：为每个Promise添加单独的错误处理

&#x20; const \[user, posts, comments] = await Promise.all(\[

&#x20;   fetchUser().catch(err => ({ error: err, fallback: '默认用户' })),

&#x20;   fetchPosts().catch(err => ({ error: err, fallback: \[] })),

&#x20;   fetchComments().catch(err => ({ error: err, fallback: \[] }))

&#x20; ]);

&#x20;&#x20;

&#x20; // 分别处理成功和失败的结果

&#x20; if (user.error) {

&#x20;   console.warn('用户数据获取失败，使用默认值');

&#x20; } else {

&#x20;   console.log('用户数据:', user);

&#x20; }

&#x20;&#x20;

&#x20; // 方法2：使用Promise.allSettled()获取所有结果状态

&#x20; const results = await Promise.allSettled(\[

&#x20;   fetchDataA(),

&#x20;   fetchDataB(),

&#x20;   fetchDataC()

&#x20; ]);

&#x20;&#x20;

&#x20; // 筛选成功和失败的结果

&#x20; const successfulResults = results

&#x20;   .filter(r => r.status === 'fulfilled')

&#x20;   .map(r => r.value);

&#x20;&#x20;

&#x20; const failedErrors = results

&#x20;   .filter(r => r.status === 'rejected')

&#x20;   .map(r => r.reason);

&#x20;&#x20;

&#x20; console.log('成功的结果:', successfulResults);

&#x20; console.log('失败的错误:', failedErrors);

}
```

#### 4. 错误处理最佳实践



1.  **明确错误边界**：



```
// 自定义错误类型

class NetworkError extends Error {

&#x20; constructor(message) {

&#x20;   super(message);

&#x20;   this.name = 'NetworkError';

&#x20; }

}

// 低层函数：抛出具体错误

async function fetchData(url) {

&#x20; try {

&#x20;   const response = await fetch(url);

&#x20;   if (!response.ok) {

&#x20;     throw new NetworkError(\`HTTP \${response.status} - \${url}\`);

&#x20;   }

&#x20;   return response.json();

&#x20; } catch (error) {

&#x20;   if (error.name !== 'NetworkError') {

&#x20;     // 包装成具体错误类型

&#x20;     throw new NetworkError(\`连接失败: \${error.message}\`);

&#x20;   }

&#x20;   throw error; // 已为具体错误，直接抛出

&#x20; }

}

// 高层函数：处理错误并恢复

async function loadData() {

&#x20; try {

&#x20;   return await fetchData('/api/data');

&#x20; } catch (error) {

&#x20;   if (error instanceof NetworkError) {

&#x20;     console.error('网络错误:', error.message);

&#x20;     return loadCachedData(); // 尝试恢复

&#x20;   }

&#x20;   // 未知错误，记录并重新抛出

&#x20;   logToService(error);

&#x20;   throw new Error('加载数据时发生未知错误');

&#x20; }

}
```



*   低层函数应抛出具体错误（使用自定义错误类型）

*   高层函数负责展示错误信息和恢复操作

1.  **避免静默失败**：

    永远不要使用空的 catch 块，至少应记录错误：



```
// 不推荐

try {

&#x20; await riskyOperation();

} catch (error) {

&#x20; // 空的catch块会隐藏错误，难以调试

}

// 推荐

try {

&#x20; await riskyOperation();

} catch (error) {

&#x20; console.error('操作失败:', error);

&#x20; // 或更完善的日志记录

&#x20; logError({

&#x20;   message: error.message,

&#x20;   stack: error.stack,

&#x20;   timestamp: new Date()

&#x20; });

&#x20; // 根据情况决定是否重新抛出

}
```



1.  **区分可恢复错误和致命错误**：

*   可恢复错误（如网络超时）：提供重试机制

*   致命错误（如权限不足）：通知用户并终止流程

### 总结

async/await 是 Promise 和 Generator 函数的语法糖，其底层实现依赖：



1.  Promise 进行异步操作管理和结果包装

2.  Generator 函数的暂停 / 恢复机制控制执行流程

3.  内置自动执行器处理状态同步和函数调度

错误处理的核心方式有两种：



*   try/catch 块：捕获所有类型错误，适合处理串行操作

*   .catch () 方法：单独处理特定异步操作错误，适合并行操作

在实际开发中，应结合自定义错误类型、明确错误边界和适当的恢复机制，构建健壮的异步错误处理体系。理解 async/await 的底层原理有助于更精准地控制异步流程和错误处理，写出更可靠的异步代码。

