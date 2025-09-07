# Promise 的三种状态是什么？如何实现 Promise.all、Promise.race 和 Promise.allSettled？

## meta 元数据



```
{

&#x20; "id": "f6a7b8c9-d0e1-2345-fghi-67890abcdef",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["javascript"]

}
```

## 答案 1：核心简洁的口语化回答

・Promise 有三种状态：pending（等待中）、fulfilled（已成功）、rejected（已失败）。

・状态只能从 pending 转为 fulfilled 或 rejected，且一旦改变就不可再变。

・Promise.all：接收 Promise 数组，全部成功则返回成功结果数组；有一个失败则立即返回该失败原因。

・Promise.race：接收 Promise 数组，返回第一个改变状态的 Promise 的结果（无论成功或失败）。

・Promise.allSettled：接收 Promise 数组，等待所有 Promise 完成（无论成功失败），返回包含每个 Promise 结果及状态的对象数组。

## 答案 2：口语化扩展回答

Promise 的三种状态很好理解，一开始都是 pending 状态，也就是还在等待结果。当异步操作成功完成，就会变成 fulfilled 状态，这时候会触发 then 里的成功回调；如果失败了，就变成 rejected 状态，触发 catch 里的失败回调，而且状态一旦确定就改不了了，这就是所谓的 “状态凝固”。

实现这几个方法时，思路各有不同。Promise.all 得等所有传入的 Promise 都成功才行，只要有一个失败，就会立刻把这个失败原因抛出来。比如多个请求都成功才能渲染页面，就适合用它，但要注意如果有一个失败会整体失败。

Promise.race 就像赛跑，谁先有结果（不管成功还是失败），就用谁的结果。比如设置请求超时时间，把请求和一个延时 reject 的 Promise 放在一起，谁先触发就按谁的来。

Promise.allSettled 则更全面，不管每个 Promise 是成功还是失败，都会等所有的都结束，然后返回每个的详细情况，包括状态和结果或原因。适合需要知道所有异步操作最终状态的场景，比如批量处理任务后统计成功和失败的数量。

## 答案 3：技术深度解析

### Promise 的三种状态详解

Promise 是 JavaScript 处理异步操作的标准方式，其核心特性是状态管理，包含三种互斥的状态：



1.  **pending（等待中）**

*   初始状态，既未成功也未失败

*   当异步操作正在执行时，Promise 处于此状态

*   可转换为 fulfilled 或 rejected 状态

1.  **fulfilled（已成功）**

*   异步操作成功完成时的状态

*   状态一旦变为 fulfilled 就不可再改变

*   会触发 Promise 对象的 then () 方法中的成功回调

1.  **rejected（已失败）**

*   异步操作失败时的状态

*   状态一旦变为 rejected 就不可再改变

*   会触发 Promise 对象的 then () 方法中的失败回调或 catch () 方法

**状态转换图示**：



```
pending → fulfilled（通过resolve()）

pending → rejected（通过reject()）
```

> 注意：Promise 状态具有不可逆性，一旦从 pending 转换为 fulfilled 或 rejected，就无法再变回原来的状态，也不能在 fulfilled 和 rejected 之间相互转换。

### Promise.all 的实现

Promise.all 接收一个可迭代对象（通常是 Promise 数组），返回一个新的 Promise。其特性为：



*   所有 Promise 都 fulfilled 时，新 Promise 才 fulfilled，结果为所有成功值组成的数组

*   只要有一个 Promise rejected，新 Promise 立即 rejected，结果为该失败原因

**实现代码**：



```
Promise.myAll = function(promises) {

&#x20; // 返回一个新的Promise

&#x20; return new Promise((resolve, reject) => {

&#x20;   // 验证输入是否为可迭代对象

&#x20;   if (!Array.isArray(promises)) {

&#x20;     return reject(new TypeError('Argument must be an array'));

&#x20;   }

&#x20;   const result = \[]; // 存储成功结果

&#x20;   let completedCount = 0; // 已完成的Promise数量

&#x20;   const totalCount = promises.length; // 总Promise数量

&#x20;   // 如果传入空数组，直接resolve

&#x20;   if (totalCount === 0) {

&#x20;     return resolve(result);

&#x20;   }

&#x20;   promises.forEach((promise, index) => {

&#x20;     // 确保处理的是Promise对象，非Promise值会被包装为已fulfilled的Promise

&#x20;     Promise.resolve(promise)

&#x20;       .then(value => {

&#x20;         // 存储当前Promise的成功结果，保持与输入数组相同的顺序

&#x20;         result\[index] = value;

&#x20;         completedCount++;

&#x20;         // 所有Promise都成功完成时，resolve结果数组

&#x20;         if (completedCount === totalCount) {

&#x20;           resolve(result);

&#x20;         }

&#x20;       })

&#x20;       .catch(reason => {

&#x20;         // 只要有一个失败，立即reject

&#x20;         reject(reason);

&#x20;       });

&#x20;   });

&#x20; });

};
```

**代码解析**：



*   使用 Promise.resolve () 处理非 Promise 值，确保统一处理方式

*   通过 index 维护结果顺序，与输入数组顺序一致

*   一旦有 Promise reject，立即调用 reject 并终止

*   所有 Promise 都 fulfilled 后，才调用 resolve 返回结果数组

### Promise.race 的实现

Promise.race 接收一个可迭代对象，返回一个新的 Promise。其特性为：



*   返回第一个改变状态的 Promise 的结果（无论 fulfilled 还是 rejected）

*   只关注第一个完成的 Promise，其他结果会被忽略

**实现代码**：



```
Promise.myRace = function(promises) {

&#x20; return new Promise((resolve, reject) => {

&#x20;   // 验证输入是否为数组

&#x20;   if (!Array.isArray(promises)) {

&#x20;     return reject(new TypeError('Argument must be an array'));

&#x20;   }

&#x20;   // 遍历所有Promise

&#x20;   promises.forEach(promise => {

&#x20;     // 第一个改变状态的Promise会触发resolve或reject

&#x20;     // 后续的Promise结果会被忽略

&#x20;     Promise.resolve(promise)

&#x20;       .then(value => {

&#x20;         resolve(value); // 第一个成功的结果

&#x20;       })

&#x20;       .catch(reason => {

&#x20;         reject(reason); // 第一个失败的原因

&#x20;       });

&#x20;   });

&#x20; });

};
```

**代码解析**：



*   不等待所有 Promise 完成，只响应第一个状态改变的 Promise

*   即使后续有其他 Promise 改变状态，也不会影响已返回的结果

*   常用于实现超时控制，例如：



```
// 超时控制示例

function withTimeout(promise, timeoutMs) {

&#x20; return Promise.myRace(\[

&#x20;   promise,

&#x20;   new Promise((\_, reject) => {

&#x20;     setTimeout(() => {

&#x20;       reject(new Error('Operation timed out'));

&#x20;     }, timeoutMs);

&#x20;   })

&#x20; ]);

}
```

### Promise.allSettled 的实现

Promise.allSettled 接收一个可迭代对象，返回一个新的 Promise。其特性为：



*   等待所有 Promise 都完成（无论 fulfilled 还是 rejected）

*   返回的 Promise 始终是 fulfilled 状态

*   结果是一个对象数组，每个对象包含对应 Promise 的状态和结果

每个结果对象的结构：



*   对于 fulfilled 的 Promise：`{ status: 'fulfilled', value: <成功值> }`

*   对于 rejected 的 Promise：`{ status: 'rejected', reason: <失败原因> }`

**实现代码**：



```
Promise.myAllSettled = function(promises) {

&#x20; return new Promise((resolve) => {

&#x20;   if (!Array.isArray(promises)) {

&#x20;     // 输入非数组时，返回包含错误的结果数组

&#x20;     return resolve(\[

&#x20;       {

&#x20;         status: 'rejected',

&#x20;         reason: new TypeError('Argument must be an array')

&#x20;       }

&#x20;     ]);

&#x20;   }

&#x20;   const results = \[];

&#x20;   let completedCount = 0;

&#x20;   const totalCount = promises.length;

&#x20;   if (totalCount === 0) {

&#x20;     return resolve(results);

&#x20;   }

&#x20;   promises.forEach((promise, index) => {

&#x20;     Promise.resolve(promise)

&#x20;       .then(value => {

&#x20;         // 记录成功状态和值

&#x20;         results\[index] = {

&#x20;           status: 'fulfilled',

&#x20;           value: value

&#x20;         };

&#x20;       })

&#x20;       .catch(reason => {

&#x20;         // 记录失败状态和原因

&#x20;         results\[index] = {

&#x20;           status: 'rejected',

&#x20;           reason: reason

&#x20;         };

&#x20;       })

&#x20;       .finally(() => {

&#x20;         completedCount++;

&#x20;         // 所有Promise都完成后，返回结果数组

&#x20;         if (completedCount === totalCount) {

&#x20;           resolve(results);

&#x20;         }

&#x20;       });

&#x20;   });

&#x20; });

};
```

**代码解析**：



*   使用 finally () 确保无论 Promise 成功或失败都计数

*   始终以 fulfilled 状态返回，不会 reject

*   结果数组与输入数组顺序一致，每个元素包含完整的状态信息

*   适合需要全面了解所有异步操作结果的场景，如：



```
// 批量操作结果统计示例

async function analyzeResults(tasks) {

&#x20; const results = await Promise.myAllSettled(tasks);

&#x20; const successCount = results.filter(r => r.status === 'fulfilled').length;

&#x20; const failureCount = results.length - successCount;

&#x20;&#x20;

&#x20; return { successCount, failureCount, details: results };

}
```

### 三种方法的对比与适用场景



| 方法                 | 特点                | 适用场景                    |
| ------------------ | ----------------- | ----------------------- |
| Promise.all        | 全部成功才成功，一个失败则整体失败 | 依赖多个并行异步操作的结果，所有操作都必须成功 |
| Promise.race       | 返回第一个完成的结果（无论成败）  | 超时控制、竞争条件处理             |
| Promise.allSettled | 等待所有完成，返回所有结果状态   | 需要知道所有操作的最终状态，如批量任务统计   |

理解这些方法的实现原理和特性，有助于在实际开发中正确选择合适的 Promise 组合方式，处理复杂的异步流程。

