---
id: 1
type: choice
difficulty: easy
tags: [vue, lifecycle]
---

## **题目：** Vue 2.x 生命周期有哪些？分别做了什么？

## **✅ 精简答案：** beforeCreate → created → beforeMount → mounted → beforeUpdate → updated → beforeDestroy → destroyed

**📘 详细解析：**

- beforeCreate：实例刚初始化，data、methods 均不可用。
- created：实例创建完成，可访问/修改数据，但 DOM 未生成；适合发异步请求。
- beforeMount：模板已编译为 render 函数，即将首次渲染真实 DOM。
- mounted：真实 DOM 已插入页面，可安全操作 $refs；适合初始化第三方库。
- beforeUpdate：响应式数据变化后、虚拟 DOM 重新渲染之前触发，可再次改数据。
- updated：虚拟 DOM 重新渲染并打补丁完成；此阶段改数据易引发循环更新。
- beforeDestroy：实例销毁前，可清理定时器、解绑全局事件。
- destroyed：实例已销毁，只剩空 DOM；所有绑定、监听、子实例均被移除。

---

id: 2
type: choice
difficulty: medium
tags: [vue, reactivity]

---

## **题目：** Vue2 与 Vue3 的响应式原理有何不同？

## **✅ 精简答案：** Vue2 用 Object.defineProperty；Vue3 用 Proxy。

**📘 详细解析：**

- Vue2：遍历 data 中所有属性，通过 Object.defineProperty 重写 getter / setter 完成依赖收集与发布订阅。
- 缺陷：无法监听新增/删除属性、数组索引/长度变化。
- Vue3：改用 Proxy，可一次性代理整个对象，支持 13 种拦截；配合 Reflect 实现深度观测；性能更好，且能捕获动态属性增删和数组变化。

---

id: 3
type: choice
difficulty: medium
tags: [vue, version]

---

## **题目：** Vue3 相对于 Vue2 的主要区别是什么？

## **✅ 精简答案：** TS 重写、Composition API、Proxy 响应式、编译优化、多根节点、生命周期调整、打包瘦身等。

**📘 详细解析：**

- 源码全部用 TypeScript 重写。
- 新增 Composition API（setup），逻辑复用更灵活；Options API 仍可用。
- 响应式系统升级为 Proxy，解决数组与动态属性的监听问题。
- 编译阶段标记并提升所有静态节点，diff 时只对比动态节点，性能提升。
- 移除不常用 API（filter、inline-template）；Tree-shaking 更彻底，包更小。
- 生命周期：setup 合并 beforeCreate & created；新增 onBeforeUnmount、onUnmounted 等。
- template 支持多个根标签。
- Vuex 改为 createStore，Router 需使用 useRouter / useRoute。

---

id: 4
type: short
difficulty: easy
tags: [vue, mvvm]

---

## **题目：** 简述 MVVM 的理解。

## **✅ 精简答案：** Model-View-ViewModel，数据(Model)与视图(View)通过 ViewModel 双向绑定。

**📘 详细解析：**  
Model 负责数据，View 负责 UI，ViewModel 作为桥梁：

- 自动把 Model 数据渲染到 View；
- 监听 View 的用户输入并更新 Model。  
  开发者只需关注数据逻辑，无需手动操作 DOM。

---

id: 5
type: choice
difficulty: medium
tags: [vue, array]

---

## **题目：** Vue2 如何检测数组的变化？

## **✅ 精简答案：** 重写数组 7 个原型方法（push/pop/shift/unshift/splice/sort/reverse）。

**📘 详细解析：**  
Vue 把 data 中的数组隐式原型指向自定义的拦截器，方法调用时先执行原生逻辑，再触发依赖通知。若数组元素为引用类型，继续递归侦测。通过这种方式捕获变更并驱动视图更新。

---

id: 6
type: short
difficulty: easy
tags: [vue, v-model]

---

## **题目：** v-model 双向绑定的原理？

## **✅ 精简答案：** 语法糖，等于 :value + @input（或对应事件）。

**📘 详细解析：**

- 普通 input：`:value` 绑定数据，`@input` 事件把 $event.target.value 写回数据。
- 组件：通过 model 选项自定义 prop 与 event；例如 checkbox 用 :checked + @change。

---

id: 7
type: long
difficulty: hard
tags: [vue, diff]

---

## **题目：** 描述 Vue2 与 Vue3 渲染器 diff 算法的核心思想。

**✅ 精简答案：**

- Vue2：双端比较 + key；O(n)。
- Vue3：静态提升 + 动态位运算标记 + 最长递增子序列；更快。

---

**📘 详细解析：**

- Vue2：同层比较，新旧 children 两端向中间遍历，借助 key 复用节点，减少移动次数。
- Vue3：
  1. 编译阶段把静态节点提升，diff 只需对比动态节点。
  2. 运行时利用位运算快速判断 VNode 类型。
  3. 多子节点 diff 采用“最长递增子序列”算法（动态规划）最小化 DOM 移动，复杂度仍保持 O(n)。

---

id: 8
type: multi
difficulty: medium
tags: [vue, communication]

---

## **题目：** 列举 Vue 中父子、兄弟、跨级组件的通信方式及其原理。

**✅ 精简答案：**

- 父子：props / $emit / $parent / $children / ref / provide-inject
- 兄弟：EventBus / Vuex
- 跨级：Vuex / $attrs + $listeners / provide-inject

---

**📘 详细解析：**

- props 向下传递，$emit 向上触发事件。
- $parent / $children 直接访问实例，强耦合，不推荐。
- ref 获取子组件实例或 DOM。
- provide / inject 实现祖先向后代注入，响应式需传对象。
- EventBus = new Vue()，利用 $on/$emit 任意通信，简单场景可用。
- Vuex 全局单一状态树，适合大型应用。

---

id: 9
type: choice
difficulty: easy
tags: [vue, router]

---

## **题目：** Vue 路由 hash 与 history 模式的实现原理？

**✅ 精简答案：**

- hash：监听 location.hash + onhashchange 事件。
- history：基于 HTML5 history.pushState / replaceState + popstate 事件。

---

**📘 详细解析：**

- hash 模式利用 URL 中 # 后面的变化，不触发服务端请求，兼容性好。
- history 模式 URL 更干净，需要服务端配置 404 回退到 index.html，否则刷新 404。

---

id: 10
type: choice
difficulty: easy
tags: [vue, directive]

---

## **题目：** v-if 与 v-show 的区别？

## **✅ 精简答案：** v-if 真正增删 DOM；v-show 仅切换 display。

**📘 详细解析：**

- v-if=false 时节点被移除，条件为真时重新创建并插入，切换成本大；适合不常切换场景。
- v-show=false 时添加 style="display:none"，节点仍在 DOM，适合频繁显示/隐藏。

---

id: 11
type: choice
difficulty: medium
tags: [vue, keep-alive]

---

## **题目：** keep-alive 的常用属性及实现原理？

## **✅ 精简答案：** include/exclude 条件缓存；内部使用 LRU 缓存策略；提供 activated/deactivated 生命周期。

**📘 详细解析：**

- include/exclude 可用字符串、正则或数组匹配组件 name 决定缓存与否。
- 缓存对象按最近最少使用淘汰，避免内存泄漏。
- 被包裹组件切换时不会销毁，而是触发 activated / deactivated，适合 Tab 页、列表详情返回等场景。

---

id: 12
type: short
difficulty: medium
tags: [vue, nextTick]

---

## **题目：** nextTick 的作用与实现原理？

## **✅ 精简答案：** 在下次 DOM 更新循环结束后执行回调；内部按优先级使用 Promise → MutationObserver → setImmediate → setTimeout。

**📘 详细解析：**  
Vue 的 DOM 更新是异步的。多次数据变更合并成一次渲染，nextTick 把回调推入微任务队列，确保拿到更新后的 DOM；常用于操作更新后的视图。

---

id: 13
type: long
difficulty: hard
tags: [vue, ssr]

---

## **题目：** Vue SSR 的实现原理及优缺点？

## **✅ 精简答案：** 服务端执行渲染生成 HTML 字符串返回客户端；优点 SEO、首屏快，缺点开发限制、服务器负载高。

**📘 详细解析：**

- 流程：Node 运行 Vue → 创建实例 → 渲染为字符串 → 客户端激活 (hydrate)。
- 仅 beforeCreate/created 在服务端执行，其他钩子无。
- 需打包两份 bundle(server & client)，外部库要兼容无 DOM。
- 服务器需处理大量 CPU 渲染，需做缓存和负载均衡。

---

id: 14
type: short
difficulty: easy
tags: [vue, data]

---

## **题目：** 为什么组件的 data 必须是一个函数？

## **✅ 精简答案：** 保证每个组件实例拥有独立数据，避免引用共享导致状态污染。

**📘 详细解析：**  
组件复用时返回同一构造函数，若 data 为对象，则所有实例共享同一份引用；使用函数每次返回新对象，确保数据隔离。

---

id: 15
type: long
difficulty: hard
tags: [vue, computed]

---

## **题目：** Vue computed 的实现原理？

## **✅ 精简答案：** 每个计算属性创建 lazy Watcher，依赖收集后缓存值，通过 dirty 标记实现按需重计算。

**📘 详细解析：**

- 初始化时遍历 computed 属性，生成带有 lazy=true 的 Watcher，保存 value 与 dirty。
- 首次读取时若 dirty 为 true 则求值并缓存，随后 dirty=false。
- 依赖项变化时仅把 dirty 置 true，等到下次读取或组件重新渲染时再计算。
- 既收集计算属性的 Watcher，也收集渲染 Watcher，确保视图同步。

---

id: 16
type: long
difficulty: hard
tags: [vue, compiler]

---

## **题目：** Vue Compiler 的实现流程？

## **✅ 精简答案：** parse → optimize → generate，最终产出 render 函数。

**📘 详细解析：**

- parse：将 template 模板解析成 AST（抽象语法树）。
- optimize：遍历 AST，标记静态节点与静态根，减少 diff 时的比对范围。
- generate：将优化后的 AST 拼接成 render 函数字符串，再通过 new Function 转为可执行函数，用于生成 VNode。

---

id: 17
type: long
difficulty: hard
tags: [vue, comparison]

---

## **题目：** Vue 与 React、Angular 的主要区别？

**✅ 精简答案：**

- Vue vs React：Vue 模板 + 响应式，React JSX + setState；Vue 官方维护路由/状态，React 社区生态大。
- Vue vs Angular：Vue 轻量、学习曲线低；Angular 全家桶 + TypeScript + 强约束。

---

**📘 详细解析：**

- Vue 与 React 都采用虚拟 DOM，核心理念相近。Vue 提供双向绑定、指令系统，React 坚持单向数据流。
- Vue 官方维护 vue-router、vuex；React 交给社区 (react-router, redux, mobx)。
- Angular 采用双向绑定 + 依赖注入 + RxJS，体积大，适合大型团队；Vue 更灵活渐进。

---

id: 18
type: choice
difficulty: medium
tags: [vue, watch, computed]

---

## **题目：** watch 与 computed 的区别及使用场景？

## **✅ 精简答案：** computed 缓存且多对一，watch 无缓存且一对多，支持异步；用 computed 算值，用 watch 做副作用。

**📘 详细解析：**

- computed：依赖值不变直接返回缓存，必须有返回值；适合计算衍生值。
- watch：监听单一或多个数据源，可异步；可配置 deep/immediate；适合请求接口、复杂业务逻辑。
- 场景示例：
  - 价格 \* 数量 = 总价 → computed；
  - 监听 id 变化拉取详情 → watch。

---

id: 19
type: multi
difficulty: easy
tags: [vue, modifiers]

---

## **题目：** 列举常用 Vue 修饰符。

**✅ 精简答案：**

- 事件：.stop .prevent .capture .self .once .passive
- 按键：.enter .tab .esc .space .up .down …
- 表单：.lazy .number .trim

---

**📘 详细解析：**

- 事件修饰符简化 DOM 事件处理；
- 按键修饰符支持键盘、鼠标、系统键；
- 表单修饰符控制 v-model 行为，如 .lazy 在 change 而非 input 时同步。

---

id: 20
type: long
difficulty: hard
tags: [vue, performance]

---

## **题目：** Vue 项目性能优化手段？

## **✅ 精简答案：** 编码阶段 + 打包阶段 + 用户体验，多管齐下。

**📘 详细解析：**

- 编码：减少 data 量，v-if/v-show 区分使用，v-for 加 key，路由懒加载，keep-alive，防抖节流，动态导入第三方库，图片懒加载，长列表虚拟滚动。
- 打包：Tree-shaking、Scope Hoisting、CDN 外链、多线程构建、splitChunks、压缩 Gzip、source-map 关闭生产。
- 用户体验：骨架屏、PWA、预渲染、SSR、缓存策略。

---

id: 21
type: long
difficulty: medium
tags: [vue, spa, first-screen]

---

## **题目：** SPA 如何优化首屏加载速度？

## **✅ 精简答案：** CDN、缓存、懒加载、预渲染、压缩、http2、骨架屏。

**📘 详细解析：**

- 请求：第三方库 CDN，减少主包体积。
- 缓存：强缓存 + 文件指纹；服务端开启 gzip。
- 协议：HTTP2 多路复用。
- 代码：路由懒加载、动态组件、Tree-shaking、按需引入 UI 库。
- 渲染：预渲染 / SSR、骨架屏、PWA。
- 资源：图片懒加载、svg 图标、压缩。

---

id: 22
type: choice
difficulty: easy
tags: [vue, key]

---

## **题目：** Key 在列表渲染中的作用？

## **✅ 精简答案：** 为节点提供唯一标识，提升 diff 效率，避免就地复用导致状态错乱。

**📘 详细解析：**  
diff 算法同级比对时，通过 key 判断节点是否可复用，减少 DOM 移动与销毁；无 key 时按顺序就地复用，可能造成表单错位、过渡失效等问题。

---

id: 23
type: choice
difficulty: easy
tags: [vue, component]

---

## **题目：** 组件写 name 选项的好处？

## **✅ 精简答案：** 递归调用、keep-alive 缓存、跨级通信、调试工具显示。

**📘 详细解析：**

- name 用于自身递归组件 <my-folder>。
- keep-alive 的 include/exclude 按 name 匹配。
- $parent.$children 遍历时可通过 name 精准定位。
- vue-devtools 组件树名称即 name。

---

id: 24
type: short
difficulty: easy
tags: [vue, ref]

---

## **题目：** ref 的作用？

## **✅ 精简答案：** 注册 DOM 或组件引用，方便父级直接访问。

**📘 详细解析：**

- 在普通元素上 ref 获取原生 DOM；
- 在组件上 ref 获取组件实例，可直接调用内部方法或访问 data。

---

id: 25
type: choice
difficulty: easy
tags: [vue, lifecycle, http]

---

## **题目：** 接口请求一般放在哪个生命周期？为什么？

## **✅ 精简答案：** created；此时数据已初始化，SSR 兼容，避免闪屏。

**📘 详细解析：**

- created 中 props/data 已可用，能立即发请求，减少首屏等待；
- SSR 只执行 beforeCreate/created，保证同构代码一致；
- mounted 请求可能因 DOM 已渲染出现数据闪烁。
