# 在react中组件间过渡动画如何实现？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890b0",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・可使用 React 官方推荐的 react-transition-group 库，通过 Transition、CSSTransition 等组件包裹目标元素，配合 CSS 实现动画。

・利用 CSS 的 transition 或 animation 属性，结合组件的显示 / 隐藏状态（如条件渲染的 state）触发动画。

・借助第三方动画库如 Framer Motion，通过组件化 API 快速实现复杂过渡效果，支持手势和物理动画。

・对于路由切换的过渡，可结合 react-router 与过渡库，在路由组件切换时添加动画。

・原生实现需监听组件挂载 / 卸载时机，通过添加 / 移除 CSS 类名触发动画，注意处理卸载前的动画完成时机。

## 答案 2：口语化扩展回答

在 React 里实现组件间的过渡动画，最常用的是借助专门的库，比如 react-transition-group，这是官方比较推荐的。它提供了像 CSSTransition 这样的组件，你只需要把要加动画的元素包起来，然后在 CSS 里定义进入和退出的动画样式就行。比如组件显示时，它会自动添加 enter、enter-active 这些类名，你对应写好过渡效果，就能实现淡入淡出、滑动这些动画了。

如果不想用库，也可以自己用 CSS 配合状态来做。比如用一个 state 控制组件显示与否，当状态变化时，先给组件加上 “进入” 的动画类，等动画结束后再真正隐藏或显示。不过这种方式得自己处理动画结束的事件，比如用 setTimeout 或者监听 transitionend 事件，不然可能出现组件还没完成动画就被卸载的情况。

对于路由之间的切换动画，通常会把路由组件用过渡库的组件包起来，比如 react-router 和 react-transition-group 结合使用，当路由变化时，让旧组件淡出，新组件淡入。另外，像 Framer Motion 这样的库功能更强大，写法也更简单，直接用它的 motion 组件，通过 props 指定动画属性，就能实现比较复杂的效果，比如拖拽、弹簧动画等，适合需要丰富交互的场景。不过如果只是简单的过渡，用 react-transition-group 配合 CSS 就足够了，性能也更好。

## 答案 3：技术深度解析

#### 1. 基于 react-transition-group 的实现（官方推荐）

react-transition-group 是 React 生态中处理过渡动画的主流库，它抽象了组件进入 / 退出的生命周期，提供了声明式的动画 API。

##### 1.1 核心组件介绍



*   **CSSTransition**：结合 CSS 实现过渡动画，是最常用的组件

*   **TransitionGroup**：管理多个过渡组件的容器

*   **SwitchTransition**：处理组件切换动画（如 tabs 切换）

##### 1.2 基础使用示例（淡入淡出效果）



```
import { CSSTransition } from 'react-transition-group';

import './FadeAnimation.css';

function FadeComponent({ isVisible }) {

&#x20; return (

&#x20;   \<CSSTransition

&#x20;     in={isVisible} // 控制组件显示/隐藏的状态

&#x20;     timeout={300} // 动画持续时间（毫秒）

&#x20;     classNames="fade" // CSS类名前缀

&#x20;     unmountOnExit // 动画结束后卸载组件

&#x20;   \>

&#x20;     \<div className="content">我是带过渡动画的组件\</div>

&#x20;   \</CSSTransition>

&#x20; );

}
```

对应的 CSS 样式：



```
/\* 初始状态（未进入） \*/

.fade-enter {

&#x20; opacity: 0;

}

/\* 进入过程中 \*/

.fade-enter-active {

&#x20; opacity: 1;

&#x20; transition: opacity 300ms ease-in;

}

/\* 退出开始时 \*/

.fade-exit {

&#x20; opacity: 1;

}

/\* 退出过程中 \*/

.fade-exit-active {

&#x20; opacity: 0;

&#x20; transition: opacity 300ms ease-out;

}

/\* 动画结束后保持的状态（可选） \*/

.fade-enter-done {

&#x20; opacity: 1;

}
```

**工作原理**：



*   CSSTransition 会根据`in`属性的变化，在不同阶段为子元素添加对应的类名

*   进入阶段：依次添加`fade-enter` → `fade-enter-active` → `fade-enter-done`

*   退出阶段：依次添加`fade-exit` → `fade-exit-active` → 卸载（如果设置 unmountOnExit）

*   动画时长由`timeout`控制，需与 CSS 中的 transition duration 保持一致

##### 1.3 多组件切换动画（使用 TransitionGroup）



```
import { TransitionGroup, CSSTransition } from 'react-transition-group';

function TabContent({ activeTab, tabs }) {

&#x20; return (

&#x20;   \<TransitionGroup className="tab-container">

&#x20;     \<CSSTransition

&#x20;       key={activeTab} // 关键：不同key触发切换动画

&#x20;       timeout={300}

&#x20;       classNames="slide"

&#x20;       unmountOnExit

&#x20;     \>

&#x20;       \<div className="tab-content">

&#x20;         {tabs\[activeTab].content}

&#x20;       \</div>

&#x20;     \</CSSTransition>

&#x20;   \</TransitionGroup>

&#x20; );

}
```

#### 2. 路由切换动画实现

结合 react-router-dom 和 react-transition-group 实现页面切换动画：



```
import { BrowserRouter as Router, Route, Switch, useLocation } from 'react-router-dom';

import { TransitionGroup, CSSTransition } from 'react-transition-group';

function AnimatedRoutes() {

&#x20; const location = useLocation(); // 获取当前路由位置

&#x20; return (

&#x20;   \<TransitionGroup>

&#x20;     {/\* 关键：用location.key作为key，确保路由变化时触发动画 \*/}

&#x20;     \<CSSTransition

&#x20;       key={location.key}

&#x20;       timeout={500}

&#x20;       classNames="route"

&#x20;     \>

&#x20;       \<Switch location={location}>

&#x20;         \<Route path="/home" component={Home} />

&#x20;         \<Route path="/about" component={About} />

&#x20;         \<Route path="/contact" component={Contact} />

&#x20;       \</Switch>

&#x20;     \</CSSTransition>

&#x20;   \</TransitionGroup>

&#x20; );

}
```

路由动画 CSS：



```
.route-enter {

&#x20; transform: translateX(100%);

}

.route-enter-active {

&#x20; transform: translateX(0);

&#x20; transition: transform 500ms ease-in-out;

}

.route-exit {

&#x20; transform: translateX(0);

}

.route-exit-active {

&#x20; transform: translateX(-100%);

&#x20; transition: transform 500ms ease-in-out;

}
```

#### 3. 基于 Framer Motion 的高级动画实现

Framer Motion 是一个功能强大的动画库，提供了更简洁的 API 和更丰富的动画效果，适合复杂交互场景。

##### 3.1 基础组件过渡



```
import { motion } from 'framer-motion';

// 定义动画变体

const variants = {

&#x20; hidden: { opacity: 0, x: 0 },

&#x20; enter: { opacity: 1, x: 50 },

&#x20; exit: { opacity: 0, x: -50 }

};

function MotionComponent({ isVisible }) {

&#x20; return (

&#x20;   \<motion.div

&#x20;     variants={variants} // 动画变体定义

&#x20;     initial="hidden" // 初始状态

&#x20;     animate={isVisible ? "enter" : "exit"} // 动画目标状态

&#x20;     exit="exit" // 退出状态（配合AnimatePresence使用）

&#x20;     transition={{ duration: 0.3 }} // 过渡配置

&#x20;   \>

&#x20;     这是Framer Motion动画组件

&#x20;   \</motion.div>

&#x20; );

}
```

##### 3.2 组件切换动画（使用 AnimatePresence）



```
import { AnimatePresence, motion } from 'framer-motion';

function ToggleComponents({ isToggled }) {

&#x20; return (

&#x20;   \<AnimatePresence mode="wait">

&#x20;     {/\* 必须提供唯一key \*/}

&#x20;     {isToggled ? (

&#x20;       \<motion.div

&#x20;         key="componentA"

&#x20;         initial={{ opacity: 0 }}

&#x20;         animate={{ opacity: 1 }}

&#x20;         exit={{ opacity: 0 }}

&#x20;       \>

&#x20;         组件A

&#x20;       \</motion.div>

&#x20;     ) : (

&#x20;       \<motion.div

&#x20;         key="componentB"

&#x20;         initial={{ opacity: 0 }}

&#x20;         animate={{ opacity: 1 }}

&#x20;         exit={{ opacity: 0 }}

&#x20;       \>

&#x20;         组件B

&#x20;       \</motion.div>

&#x20;     )}

&#x20;   \</AnimatePresence>

&#x20; );

}
```

**Framer Motion 优势**：



*   支持物理动画（弹簧效果等）

*   内置手势识别（拖拽、缩放等）

*   更简洁的动画控制 API

*   支持动画序列和并行动画

#### 4. 原生实现方式（不依赖第三方库）

在不使用动画库的情况下，可通过监听组件生命周期和 CSS 过渡事件实现动画：



```
import { useState, useRef, useEffect } from 'react';

import './NativeAnimation.css';

function NativeAnimationComponent({ isVisible }) {

&#x20; const \[isAnimating, setIsAnimating] = useState(false);

&#x20; const containerRef = useRef(null);

&#x20; useEffect(() => {

&#x20;   const container = containerRef.current;

&#x20;  &#x20;

&#x20;   if (isVisible) {

&#x20;     // 显示组件时触发进入动画

&#x20;     setIsAnimating(true);

&#x20;     container.classList.remove('exit');

&#x20;     container.classList.add('enter');

&#x20;   } else {

&#x20;     // 隐藏组件时触发退出动画

&#x20;     container.classList.remove('enter');

&#x20;     container.classList.add('exit');

&#x20;    &#x20;

&#x20;     // 监听动画结束事件，动画完成后卸载

&#x20;     const handleTransitionEnd = () => {

&#x20;       setIsAnimating(false);

&#x20;       container.removeEventListener('transitionend', handleTransitionEnd);

&#x20;     };

&#x20;    &#x20;

&#x20;     container.addEventListener('transitionend', handleTransitionEnd);

&#x20;   }

&#x20; }, \[isVisible]);

&#x20; // 动画未开始且不显示时，不渲染组件

&#x20; if (!isVisible && !isAnimating) return null;

&#x20; return (

&#x20;   \<div&#x20;

&#x20;     ref={containerRef}

&#x20;     className="native-container"

&#x20;   \>

&#x20;     原生实现的过渡动画

&#x20;   \</div>

&#x20; );

}
```

对应的 CSS：



```
.native-container {

&#x20; transition: all 0.3s ease;

}

.native-container.enter {

&#x20; opacity: 1;

&#x20; transform: translateY(0);

}

.native-container.exit {

&#x20; opacity: 0;

&#x20; transform: translateY(20px);

}

/\* 初始状态 \*/

.native-container:not(.enter):not(.exit) {

&#x20; opacity: 0;

&#x20; transform: translateY(20px);

}
```

**原生实现关键点**：



*   需手动管理动画状态（isAnimating）

*   必须监听 transitionend 事件确保动画完成后再卸载

*   需处理初始状态与动画状态的衔接

#### 5. 不同实现方式的对比与选择



| 实现方式                   | 优点                 | 缺点               | 适用场景             |
| ---------------------- | ------------------ | ---------------- | ---------------- |
| react-transition-group | 轻量、官方推荐、与 CSS 结合好  | 功能相对基础、需要写较多 CSS | 简单过渡动画、性能要求高的场景  |
| Framer Motion          | 功能强大、API 简洁、支持复杂动画 | 包体积较大（约 100KB+）  | 复杂交互动画、手势控制、原型开发 |
| 原生实现                   | 无依赖、体积最小           | 需手动处理生命周期、代码繁琐   | 简单场景、对依赖有严格限制    |

#### 6. 性能优化建议



*   避免对大量元素同时应用动画，可使用 requestAnimationFrame 分批处理

*   优先使用 transform 和 opacity 属性动画，这两个属性不会触发重排（reflow）

*   对频繁切换的动画组件，考虑使用`will-change: transform`提示浏览器优化

*   复杂动画场景可使用`shouldComponentUpdate`或 React.memo 避免不必要的重渲染

*   移动端动画尽量控制在 100ms 以内，提升交互响应感

#### 7. 总结

React 中实现组件过渡动画的核心是**管理组件显示 / 隐藏的中间状态**，通过在状态切换过程中应用 CSS 过渡或动画效果实现平滑过渡。实际开发中，推荐根据项目需求选择合适的方案：



*   简单过渡动画首选 react-transition-group，平衡了易用性和性能

*   复杂交互动画或原型开发推荐 Framer Motion，提升开发效率

*   对包体积有严格限制的场景可考虑原生实现，但需注意处理好动画生命周期

无论选择哪种方式，都应关注动画的性能和用户体验，避免过度动画导致的页面卡顿或干扰用户操作。

