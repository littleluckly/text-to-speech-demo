---
id: 1
type: choice
difficulty: easy
tags: [vue, lifecycle]
---

## **题目：** Vue 2.x 生命周期有哪些？分别做了什么？

## **✅ 精简答案：** beforeCreate → created → beforeMount → mounted → beforeUpdate → updated → beforeDestroy → destroyed

**📘 详细解析：**

```javascript
function sayhello() {
  console.log("hello world!");
}
```

- beforeCreate：实例刚初始化，data、methods 均不可用。
- created：实例创建完成，可访问/修改数据，但 DOM 未生成；适合发异步请求。
- beforeMount：模板已编译为 render 函数，即将首次渲染真实 DOM。
- mounted：真实 DOM 已插入页面，可安全操作 $refs；适合初始化第三方库。
- beforeUpdate：响应式数据变化后、虚拟 DOM 重新渲染之前触发，可再次改数据。
- updated：虚拟 DOM 重新渲染并打补丁完成；此阶段改数据易引发循环更新。
- beforeDestroy：实例销毁前，可清理定时器、解绑全局事件。
- destroyed：实例已销毁，只剩空 DOM；所有绑定、监听、子实例均被移除。

```javascript
function sayhello() {
  console.log("hello");
}
```

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
