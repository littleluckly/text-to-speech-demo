# React 中如何通过自定义 Hook 实现观察者模式？举例说明组件间通信场景。

## meta 元数据



```
{

&#x20; "id": "c4d5e6f7-g8h9-0123-efgh-4567890abcd1",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react", "设计模式"]

}
```

## 答案 1：核心简洁的口语化回答

・自定义 Hook 实现观察者模式需封装：事件存储、订阅方法、发布方法、取消订阅方法

・用 useRef 存储事件回调列表（避免刷新丢失），useEffect 处理订阅清理

・组件间通信场景：兄弟组件状态同步（如表单与预览区）、跨层级通知（如导航栏与内容区）

・核心是通过共享的事件中心，让组件按需订阅 / 发布事件，解耦通信逻辑

・优势：减少 props 传递层级，灵活处理动态组件间的交互

## 答案 2：口语化扩展回答

在 React 里用自定义 Hook 实现观察者模式，关键是把观察者的核心功能封装成可复用的 Hook。一般会用 useRef 来存事件列表，因为它不会随着组件刷新而重置，能稳定保存所有订阅的回调。然后提供订阅、发布、取消订阅这几个方法，让组件可以按需使用。

比如做一个事件总线的 Hook，叫 useEventBus。组件需要通信时，只要引入这个 Hook，就能通过发布事件和订阅事件来传递信息。像兄弟组件之间，比如一个筛选组件和一个列表组件，筛选条件变了，筛选组件发布一个事件，列表组件订阅这个事件，收到后就重新加载数据，不用通过父组件转发 props，这样代码更简洁。

还有跨多层级的情况，比如顶部导航栏的主题切换按钮，点击后要通知深层嵌套的内容组件换样式。这时候用这种方式，导航栏发布主题变更事件，内容组件订阅后更新自身样式，比用 Context 或者 Redux 简单不少，尤其是组件结构比较动态的时候，更灵活。不过要注意在组件卸载时取消订阅，避免内存泄漏，这一步可以在 useEffect 的清理函数里做。

## 答案 3：技术深度解析

### 自定义 Hook 实现观察者模式的技术原理

React 中通过自定义 Hook 实现观察者模式，核心是利用 **Hook 的状态管理能力** 结合 **闭包存储事件订阅列表**，封装观察者模式的核心方法（订阅、发布、取消订阅），并通过 React 的生命周期机制处理订阅的清理，避免内存泄漏。

#### 核心实现步骤：



1.  **事件存储容器**：使用 `useRef` 存储事件与订阅者的映射关系（键为事件名，值为回调函数数组），利用其持久化特性保证状态不随组件渲染丢失。

2.  **订阅机制**：提供 `on` 方法，将回调函数注册到对应事件的订阅列表中。

3.  **发布机制**：提供 `emit` 方法，触发指定事件的所有订阅回调，并传递参数。

4.  **取消订阅**：提供 `off` 方法，从订阅列表中移除指定回调，避免无效执行。

5.  **自动清理**：在 `useEffect` 的清理函数中处理组件卸载时的订阅取消，防止内存泄漏。

### 完整实现代码：useEventBus 自定义 Hook



```
import { useRef, useEffect } from 'react';

/\*\*

&#x20;\* 实现观察者模式的自定义 Hook

&#x20;\* 提供事件订阅、发布、取消订阅功能

&#x20;\* @returns {Object} 包含 on, emit, off 方法的事件总线对象

&#x20;\*/

function useEventBus() {

&#x20; // 用 ref 存储事件映射表：{ eventName: \[callback1, callback2, ...] }

&#x20; // 为什么用 ref？因为 ref 的 current 属性不会触发组件重渲染，且值会被持久化

&#x20; const eventsRef = useRef({});

&#x20; // 订阅事件

&#x20; const on = (eventName, callback) => {

&#x20;   // 如果事件名不存在，初始化一个空数组

&#x20;   if (!eventsRef.current\[eventName]) {

&#x20;     eventsRef.current\[eventName] = \[];

&#x20;   }

&#x20;   // 将回调添加到事件列表（去重处理，避免重复订阅）

&#x20;   const callbacks = eventsRef.current\[eventName];

&#x20;   if (!callbacks.includes(callback)) {

&#x20;     callbacks.push(callback);

&#x20;   }

&#x20; };

&#x20; // 发布事件

&#x20; const emit = (eventName, ...args) => {

&#x20;   // 获取该事件的所有订阅回调

&#x20;   const callbacks = eventsRef.current\[eventName] || \[];

&#x20;   // 复制一份回调列表再执行，防止执行中修改原数组导致异常

&#x20;   \[...callbacks].forEach(callback => {

&#x20;     // 执行回调并传递参数

&#x20;     callback(...args);

&#x20;   });

&#x20; };

&#x20; // 取消订阅

&#x20; const off = (eventName, callback) => {

&#x20;   const callbacks = eventsRef.current\[eventName];

&#x20;   if (callbacks) {

&#x20;     // 过滤掉要移除的回调

&#x20;     eventsRef.current\[eventName] = callbacks.filter(cb => cb !== callback);

&#x20;     // 如果事件列表为空，可删除该事件键节省内存

&#x20;     if (eventsRef.current\[eventName].length === 0) {

&#x20;       delete eventsRef.current\[eventName];

&#x20;     }

&#x20;   }

&#x20; };

&#x20; // 组件卸载时自动清理所有订阅（可选，根据场景决定）

&#x20; useEffect(() => {

&#x20;   return () => {

&#x20;     // 清空所有事件订阅

&#x20;     eventsRef.current = {};

&#x20;   };

&#x20; }, \[]);

&#x20; return { on, emit, off };

}

export default useEventBus;
```

### 组件间通信场景举例

#### 场景 1：兄弟组件通信（表单筛选与列表展示）

需求：左侧筛选表单组件与右侧列表组件为兄弟关系，筛选条件变化时，列表需自动刷新数据。



```
// 筛选组件 FilterPanel.jsx

import { useState } from 'react';

import useEventBus from './useEventBus';

function FilterPanel() {

&#x20; const \[filters, setFilters] = useState({ keyword: '', category: '' });

&#x20; const { emit } = useEventBus();

&#x20; // 筛选条件变化时发布事件

&#x20; const handleFilterChange = (newFilters) => {

&#x20;   setFilters(newFilters);

&#x20;   // 发布 'filterChange' 事件，传递最新筛选条件

&#x20;   emit('filterChange', newFilters);

&#x20; };

&#x20; return (

&#x20;   \<div className="filter-panel">

&#x20;     \<input

&#x20;       placeholder="搜索关键词"

&#x20;       value={filters.keyword}

&#x20;       onChange={(e) => handleFilterChange({ ...filters, keyword: e.target.value })}

&#x20;     />

&#x20;     \<select

&#x20;       value={filters.category}

&#x20;       onChange={(e) => handleFilterChange({ ...filters, category: e.target.value })}

&#x20;     \>

&#x20;       \<option value="">全部分类\</option>

&#x20;       \<option value="react">React\</option>

&#x20;       \<option value="vue">Vue\</option>

&#x20;     \</select>

&#x20;   \</div>

&#x20; );

}

// 列表组件 DataList.jsx

import { useState, useEffect } from 'react';

import useEventBus from './useEventBus';

function DataList() {

&#x20; const \[data, setData] = useState(\[]);

&#x20; const \[loading, setLoading] = useState(false);

&#x20; const { on, off } = useEventBus();

&#x20; // 订阅筛选事件，更新数据

&#x20; useEffect(() => {

&#x20;   // 定义事件回调

&#x20;   const handleFilterChange = async (filters) => {

&#x20;     setLoading(true);

&#x20;     // 模拟接口请求

&#x20;     const response = await fetch(\`/api/data?keyword=\${filters.keyword}\&category=\${filters.category}\`);

&#x20;     const result = await response.json();

&#x20;     setData(result);

&#x20;     setLoading(false);

&#x20;   };

&#x20;   // 订阅事件

&#x20;   on('filterChange', handleFilterChange);

&#x20;   // 组件卸载时取消订阅

&#x20;   return () => {

&#x20;     off('filterChange', handleFilterChange);

&#x20;   };

&#x20; }, \[on, off]);

&#x20; if (loading) return \<div>加载中...\</div>;

&#x20; return (

&#x20;   \<ul className="data-list">

&#x20;     {data.map(item => (

&#x20;       \<li key={item.id}>{item.title}\</li>

&#x20;     ))}

&#x20;   \</ul>

&#x20; );

}

// 父组件 Page.jsx

function Page() {

&#x20; return (

&#x20;   \<div className="page">

&#x20;     \<FilterPanel />

&#x20;     \<DataList />

&#x20;   \</div>

&#x20; );

}
```

#### 场景 2：跨层级组件通信（全局通知系统）

需求：深层嵌套的操作组件触发成功提示，顶层的通知组件需显示提示信息。



```
// 操作组件 ActionButton.jsx（深层嵌套）

import useEventBus from './useEventBus';

function ActionButton() {

&#x20; const { emit } = useEventBus();

&#x20; const handleClick = async () => {

&#x20;   try {

&#x20;     await fetch('/api/action', { method: 'POST' });

&#x20;     // 发布成功通知事件

&#x20;     emit('showNotification', {

&#x20;       type: 'success',

&#x20;       message: '操作成功！'

&#x20;     });

&#x20;   } catch (error) {

&#x20;     emit('showNotification', {

&#x20;       type: 'error',

&#x20;       message: '操作失败，请重试'

&#x20;     });

&#x20;   }

&#x20; };

&#x20; return \<button onClick={handleClick}>执行操作\</button>;

}

// 通知组件 Notification.jsx（顶层组件）

import { useState, useEffect } from 'react';

import useEventBus from './useEventBus';

function Notification() {

&#x20; const \[notification, setNotification] = useState(null);

&#x20; const { on, off } = useEventBus();

&#x20; // 订阅通知事件

&#x20; useEffect(() => {

&#x20;   const handleShowNotification = (config) => {

&#x20;     // 显示通知

&#x20;     setNotification(config);

&#x20;     // 3秒后自动关闭

&#x20;     setTimeout(() => setNotification(null), 3000);

&#x20;   };

&#x20;   on('showNotification', handleShowNotification);

&#x20;   return () => {

&#x20;     off('showNotification', handleShowNotification);

&#x20;   };

&#x20; }, \[on, off]);

&#x20; if (!notification) return null;

&#x20; return (

&#x20;   \<div className={\`notification notification-\${notification.type}\`}>

&#x20;     {notification.message}

&#x20;   \</div>

&#x20; );

}

// 应用入口 App.jsx

function App() {

&#x20; return (

&#x20;   \<div className="app">

&#x20;     \<Notification />

&#x20;     \<div className="content">

&#x20;       {/\* 深层嵌套的组件树 \*/}

&#x20;       \<DeepNestedComponent />

&#x20;     \</div>

&#x20;   \</div>

&#x20; );

}

// 深层嵌套组件（示例结构）

function DeepNestedComponent() {

&#x20; return \<ActionButton />;

}
```

### 实现原理深度分析



1.  **事件存储机制**：

*   `eventsRef.current` 是一个对象，键为事件名称（如 'filterChange'），值为数组（存储该事件的所有订阅回调）

*   采用数组存储回调，支持一个事件被多个组件同时订阅

1.  **订阅与发布的联动**：

*   当 `emit` 被调用时，会遍历对应事件的回调数组并执行，实现 "一对多" 的通知机制

*   回调函数的参数通过 `...args` 传递，支持任意数量的参数传递

1.  **React 生命周期适配**：

*   在 `useEffect` 的清理函数中调用 `off`，确保组件卸载后不再接收事件，避免 "已卸载组件 setState" 的错误

*   对于需要动态订阅的场景（如根据 props 变化重新订阅），可在 `useEffect` 的依赖数组中添加相关变量

1.  **与 Context/Redux 的对比**：

*   优势：轻量灵活，适合非全局状态的临时通信，无需定义 action 和 reducer

*   劣势：不适合复杂状态管理，缺乏状态回溯能力，调试难度较高

### 注意事项与最佳实践



1.  **事件名规范**：使用唯一且语义化的事件名（如 'user:login'），避免命名冲突

2.  **防止重复订阅**：在 `on` 方法中添加去重逻辑（如示例中的 `!callbacks.includes(callback)`）

3.  **及时取消订阅**：所有订阅必须在组件卸载时取消，尤其对于频繁挂载 / 卸载的组件

4.  **避免过度使用**：全局事件总线可能导致组件关系模糊，复杂状态建议使用 Redux 等状态管理库

5.  **类型安全**：在 TypeScript 中可通过泛型定义事件类型，增强代码健壮性



```
// TypeScript 版本示例（简化）

import { useRef, useEffect } from 'react';

type EventMap = {

&#x20; filterChange: (filters: { keyword: string; category: string }) => void;

&#x20; showNotification: (config: { type: 'success' | 'error'; message: string }) => void;

};

function useEventBus() {

&#x20; const eventsRef = useRef<{ \[K in keyof EventMap]?: EventMap\[K]\[] }>({});

&#x20; const on = \<K extends keyof EventMap>(eventName: K, callback: EventMap\[K]) => {

&#x20;   if (!eventsRef.current\[eventName]) {

&#x20;     eventsRef.current\[eventName] = \[];

&#x20;   }

&#x20;   eventsRef.current\[eventName]!.push(callback);

&#x20; };

&#x20; // 其余方法实现类似，省略...

&#x20; return { on, emit, off };

}
```

通过上述实现，自定义 Hook 成功将观察者模式融入 React 生态，为组件间通信提供了一种轻量级解决方案，尤其适合处理跨层级、非父子关系的组件交互场景。

