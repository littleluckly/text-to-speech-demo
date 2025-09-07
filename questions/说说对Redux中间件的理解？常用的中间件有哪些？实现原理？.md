# 说说对Redux中间件的理解？常用的中间件有哪些？实现原理？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890b1",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・Redux 中间件是介于 action 被派发和 reducer 处理之间的扩展机制，用于处理异步操作、日志记录等副作用。

・常用中间件有 redux-thunk（处理异步 action）、redux-saga（复杂异步流程管理）、redux-logger（打印 action 和 state 变化日志）。

・实现原理基于函数柯里化和洋葱模型，通过串联多个中间件函数，对 dispatch 方法进行增强，依次处理 action 后再传递给 reducer。

・中间件能在不修改原有 redux 核心逻辑的前提下，扩展功能，使代码更具可维护性。

・其本质是对 dispatch 的包装，每个中间件负责特定功能，可按需组合使用。

## 答案 2：口语化扩展回答

Redux 中间件其实就是 Redux 提供的一个扩展点，作用在 action 发送到 reducer 的过程中。平时我们用 Redux，action 都是直接传给 reducer 的，但如果有异步操作，比如发请求获取数据，这时候就需要中间件来帮忙处理了，不然同步的 action 没法直接处理异步逻辑。

常用的中间件里，redux-thunk 应该是最基础的，它允许 action 返回一个函数而不是普通对象，这个函数里可以写异步代码，等异步操作完成后再派发真正的 action。对于更复杂的异步场景，比如需要取消请求、处理竞态问题，redux-saga 就更合适，它用 generator 函数来管理异步流程，逻辑更清晰，也方便测试。而 redux-logger 主要是开发时用的，能打印出每次派发的 action、之前的 state 和之后的 state，调试的时候特别有用。

从原理上来说，中间件其实是对 dispatch 方法做了一层包装。原来的 dispatch 只能发普通 action，经过中间件处理后，dispatch 就有了新的能力，比如能处理函数类型的 action。多个中间件一起用的时候，会像洋葱一样一层层处理 action，每个中间件做完自己的事再传给下一个，最后才到 reducer。这样的设计特别灵活，我们可以根据需求组合不同的中间件，不用改 Redux 本身的代码。

## 答案 3：技术深度解析

#### 1. Redux 中间件的本质与作用

Redux 中间件是 Redux 架构中处理**副作用（Side Effects）** 的核心机制，其本质是**对 dispatch 方法的增强**，在 action 被派发后、到达 reducer 之前拦截并处理 action。

**核心作用**：



*   处理异步操作（如 API 请求）

*   日志记录与调试

*   错误捕获

*   路由跳转与状态同步

*   对 action 进行转换或过滤

在 Redux 工作流中，中间件位于 action 派发和 reducer 处理之间：



```
dispatch(action) → \[中间件处理] → reducer → state更新
```

#### 2. 常用中间件及应用场景

##### 2.1 redux-thunk

**功能**：允许 action 创建器返回函数（而非普通对象），从而在函数内部实现异步逻辑。

**使用示例**：



```
// 安装：npm install redux-thunk

import { createStore, applyMiddleware } from 'redux';

import thunk from 'redux-thunk';

import rootReducer from './reducers';

const store = createStore(rootReducer, applyMiddleware(thunk));

// 异步action创建器

const fetchUser = (userId) => {

&#x20; // 返回函数，接收dispatch和getState作为参数

&#x20; return (dispatch, getState) => {

&#x20;   dispatch({ type: 'USER\_FETCH\_STARTED' });

&#x20;   fetch(\`/api/users/\${userId}\`)

&#x20;     .then(response => response.json())

&#x20;     .then(user => {

&#x20;       dispatch({ type: 'USER\_FETCH\_SUCCEEDED', payload: user });

&#x20;     })

&#x20;     .catch(error => {

&#x20;       dispatch({ type: 'USER\_FETCH\_FAILED', payload: error });

&#x20;     });

&#x20; };

};

// 派发异步action

store.dispatch(fetchUser(123));
```

**适用场景**：简单异步逻辑、需要访问 state 的异步操作。

##### 2.2 redux-saga

**功能**：基于 Generator 函数实现复杂异步流程管理，支持取消请求、竞态处理、防抖节流等高级特性。

**使用示例**：



```
// 安装：npm install redux-saga

import { createStore, applyMiddleware } from 'redux';

import createSagaMiddleware from 'redux-saga';

import { takeEvery, call, put } from 'redux-saga/effects';

// Saga工作流

function\* fetchUserSaga(action) {

&#x20; try {

&#x20;   yield put({ type: 'USER\_FETCH\_STARTED' });

&#x20;   // 调用异步函数

&#x20;   const user = yield call(fetch, \`/api/users/\${action.payload.userId}\`);

&#x20;   const data = yield call(\[user, 'json']);

&#x20;   // 派发成功action

&#x20;   yield put({ type: 'USER\_FETCH\_SUCCEEDED', payload: data });

&#x20; } catch (error) {

&#x20;   // 派发失败action

&#x20;   yield put({ type: 'USER\_FETCH\_FAILED', payload: error });

&#x20; }

}

// 监听action

function\* rootSaga() {

&#x20; yield takeEvery('USER\_FETCH\_REQUESTED', fetchUserSaga);

}

// 创建saga中间件

const sagaMiddleware = createSagaMiddleware();

const store = createStore(rootReducer, applyMiddleware(sagaMiddleware));

// 启动saga

sagaMiddleware.run(rootSaga);

// 触发异步流程

store.dispatch({ type: 'USER\_FETCH\_REQUESTED', payload: { userId: 123 } });
```

**适用场景**：复杂异步流程、需要取消 / 重试的请求、定时任务等。

##### 2.3 redux-logger

**功能**：在开发环境中打印 action 日志，包括 action 内容、执行前后的 state 状态。

**使用示例**：



```
// 安装：npm install redux-logger

import { createStore, applyMiddleware } from 'redux';

import logger from 'redux-logger';

import rootReducer from './reducers';

// 注意：logger应放在最后一个中间件

const store = createStore(

&#x20; rootReducer,

&#x20; applyMiddleware(thunk, logger)

);
```

**输出示例**：



```
action USER\_FETCH\_SUCCEEDED @ 16:23:45.123

prev state { loading: true, user: null }

action     { type: 'USER\_FETCH\_SUCCEEDED', payload: { id: 123, name: 'John' } }

next state { loading: false, user: { id: 123, name: 'John' } }
```

**适用场景**：开发调试、跟踪状态变化。

##### 2.4 其他常用中间件



*   **redux-promise**：支持 action 返回 Promise 对象

*   **redux-observable**：基于 RxJS 处理异步流

*   **redux-devtools-extension**：配合 Redux DevTools 进行调试

#### 3. 中间件实现原理

Redux 中间件基于**函数柯里化（Currying）** 和**洋葱模型（Onion Model）** 实现，核心是对 dispatch 方法的多层包装。

##### 3.1 中间件的函数结构

标准 Redux 中间件的函数结构为：



```
const middleware = store => next => action => {

&#x20; // 中间件逻辑

&#x20; return next(action);

};
```



*   第一层（store）：接收 Redux store 对象（包含 dispatch 和 getState）

*   第二层（next）：接收下一个中间件的 dispatch 方法

*   第三层（action）：接收当前派发的 action

##### 3.2 applyMiddleware 的工作原理

applyMiddleware 用于组合多个中间件，其简化实现如下：



```
function applyMiddleware(...middlewares) {

&#x20; return (createStore) => (reducer, preloadedState) => {

&#x20;   // 创建原始store

&#x20;   const store = createStore(reducer, preloadedState);

&#x20;   let dispatch = store.dispatch;

&#x20;  &#x20;

&#x20;   // 中间件API

&#x20;   const middlewareAPI = {

&#x20;     getState: store.getState,

&#x20;     dispatch: (action) => dispatch(action) // 动态绑定最新dispatch

&#x20;   };

&#x20;  &#x20;

&#x20;   // 第一层柯里化：传入middlewareAPI

&#x20;   const chain = middlewares.map(middleware => middleware(middlewareAPI));

&#x20;  &#x20;

&#x20;   // 组合中间件，增强dispatch

&#x20;   dispatch = compose(...chain)(store.dispatch);

&#x20;  &#x20;

&#x20;   // 返回增强后的store

&#x20;   return { ...store, dispatch };

&#x20; };

}

// 组合函数：将中间件串联成一个函数

function compose(...funcs) {

&#x20; if (funcs.length === 0) return arg => arg;

&#x20; if (funcs.length === 1) return funcs\[0];

&#x20; return funcs.reduce((a, b) => (...args) => a(b(...args)));

}
```

##### 3.3 洋葱模型执行流程

当多个中间件组合使用时，执行流程类似洋葱：



1.  action 先进入第一个中间件

2.  完成处理后通过 next (action) 传递给下一个中间件

3.  依次经过所有中间件后到达原始 dispatch

4.  reducer 处理完成后，执行结果反向经过所有中间件

**示例**：当使用 logger 和 thunk 中间件时：



```
dispatch(action)

→ logger中间件（接收action）

→ thunk中间件（处理异步逻辑）

→ 原始dispatch

→ reducer处理

→ 返回结果

→ thunk中间件

→ logger中间件（打印日志）

→ 完成
```

##### 3.4 自定义中间件示例

**日志中间件实现**：



```
const loggerMiddleware = store => next => action => {

&#x20; console.log('prev state:', store.getState());

&#x20; console.log('action:', action);

&#x20;&#x20;

&#x20; // 调用下一个中间件

&#x20; const result = next(action);

&#x20;&#x20;

&#x20; console.log('next state:', store.getState());

&#x20; return result;

};
```

**异步中间件（简化版 thunk）实现**：



```
const thunkMiddleware = store => next => action => {

&#x20; // 如果action是函数，执行它并传入dispatch和getState

&#x20; if (typeof action === 'function') {

&#x20;   return action(store.dispatch, store.getState);

&#x20; }

&#x20; // 否则直接传递给下一个中间件

&#x20; return next(action);

};
```

#### 4. 中间件的最佳实践



*   **按功能分层**：将不同功能的中间件分类（如日志类、异步类）

*   **控制中间件顺序**：


    *   日志类中间件通常放在最后（能捕获所有 action）

    *   异步类中间件（如 thunk、saga）放在靠前位置

*   **生产环境优化**：移除开发环境中间件（如 logger）

*   **避免过度使用**：简单场景可直接使用 Redux Toolkit 的 createAsyncThunk

*   **中间件职责单一**：每个中间件只处理一类任务

#### 5. 与 Redux Toolkit 的结合

Redux Toolkit（RTK）已内置常用中间件，简化了中间件配置：



```
import { configureStore } from '@reduxjs/toolkit';

import rootReducer from './reducers';

import createSagaMiddleware from 'redux-saga';

const sagaMiddleware = createSagaMiddleware();

// RTK默认包含redux-thunk，可通过middleware配置扩展

const store = configureStore({

&#x20; reducer: rootReducer,

&#x20; middleware: (getDefaultMiddleware) =>&#x20;

&#x20;   getDefaultMiddleware().concat(sagaMiddleware, logger)

});

sagaMiddleware.run(rootSaga);
```

#### 6. 总结

Redux 中间件是 Redux 生态中处理副作用的关键机制，通过对 dispatch 的增强，实现了在不修改核心逻辑的前提下扩展 Redux 功能。常用的 redux-thunk、redux-saga 和 redux-logger 分别解决了不同场景下的问题，其实现原理基于函数柯里化和洋葱模型，通过多层函数包装实现对 action 的拦截与处理。

理解中间件的工作原理，不仅有助于更好地使用 Redux，还能帮助开发者设计更灵活的组件架构。在实际开发中，应根据项目复杂度选择合适的中间件，并遵循职责单一、顺序合理的原则进行配置，以充分发挥 Redux 中间件的优势。

