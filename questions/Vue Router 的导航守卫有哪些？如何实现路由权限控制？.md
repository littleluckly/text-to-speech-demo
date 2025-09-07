# Vue Router 的导航守卫有哪些？如何实现路由权限控制？

## meta 元数据



```
{

&#x20; "id": "k9l0m1n2-o3p4-5678-qrst-9012345678hi",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue", "vue-router"]

}
```

## 答案 1：核心简洁的口语化回答

・导航守卫类型：包括全局守卫（beforeEach、beforeResolve、afterEach）、路由独享守卫（beforeEnter）、组件内守卫（beforeRouteEnter、beforeRouteUpdate、beforeRouteLeave）。

・全局守卫：作用于所有路由，beforeEach 在路由跳转前触发，可用于权限校验；afterEach 在跳转后触发，常用于页面标题修改。

・路由独享守卫：在单个路由配置中定义，仅作用于该路由，功能类似 beforeEach。

・组件内守卫：在组件内部定义，用于监听组件相关的路由变化。

・权限控制实现：在 beforeEach 中判断用户权限与路由所需权限，不满足时跳转至登录页或无权限页，结合路由元信息（meta）存储权限要求。

## 答案 2：口语化扩展回答

Vue Router 的导航守卫就像路由跳转过程中的 "关卡"，能在不同阶段拦截并处理跳转。全局守卫里，beforeEach 最常用，每次路由切换前都会触发，适合做全局的权限检查，比如判断用户有没有登录。beforeResolve 在所有组件内守卫和异步路由组件解析后触发，afterEach 则是在路由跳转完成后执行，一般用来改页面标题或者统计访问。

路由独享守卫是给单个路由配置的，直接写在路由规则里的 beforeEnter，作用和 beforeEach 类似，但只对当前路由生效，比如某个特殊页面需要单独验证权限时用。

组件内的守卫更贴近组件本身，比如 beforeRouteEnter 在进入组件对应的路由前触发，不过这时候组件还没创建，拿不到 this；beforeRouteUpdate 在组件被复用时触发，比如从 /user/1 跳到 /user/2；beforeRouteLeave 则是离开组件路由时触发，可用来提示用户保存未提交的内容。

实现权限控制时，通常先在路由的 meta 里定义需要的权限，比如 meta: {requiresAuth: true, role: 'admin'}。然后在全局 beforeEach 里，获取当前路由的 meta 信息，检查用户是否登录、角色是否匹配。如果没权限，就用 next ('/login') 跳转到登录页，或者 next ('/403') 到无权限页；有权限的话就用 next () 放行。这样就能在用户跳转前拦住不符合条件的请求，实现路由级别的权限管理。

## 答案 3：技术深度解析

### 1. 导航守卫的完整分类与使用场景

#### （1）全局守卫

作用于整个应用的所有路由，定义在路由实例上：



```
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({/\* 路由配置 \*/})

// 1. 全局前置守卫：路由跳转前触发

router.beforeEach((to, from, next) => {

&#x20; // to：目标路由对象

&#x20; // from：当前导航正要离开的路由

&#x20; // next：函数，决定是否继续导航

&#x20; console.log('全局前置守卫：即将从', from.path, '跳转到', to.path)

&#x20;&#x20;

&#x20; // 必须调用next()，否则路由会停滞

&#x20; // next()：放行

&#x20; // next(false)：取消导航

&#x20; // next('/login')：跳转到指定路由

&#x20; next()

})

// 2. 全局解析守卫：在所有组件内守卫和异步路由被解析后触发

router.beforeResolve((to, from, next) => {

&#x20; console.log('全局解析守卫：即将确认导航到', to.path)

&#x20; next()

})

// 3. 全局后置钩子：路由跳转完成后触发（无next参数）

router.afterEach((to, from) => {

&#x20; console.log('全局后置钩子：已从', from.path, '跳转到', to.path)

&#x20; // 常用于设置页面标题

&#x20; document.title = to.meta.title || '默认标题'

})
```

**使用场景**：



*   beforeEach：全局权限校验、登录状态检查

*   beforeResolve：等待异步操作完成后再确认导航

*   afterEach：页面标题设置、访问统计、滚动位置重置

#### （2）路由独享守卫

仅作用于单个路由，在路由配置中定义：



```
const routes = \[

&#x20; {

&#x20;   path: '/dashboard',

&#x20;   component: Dashboard,

&#x20;   // 路由独享守卫

&#x20;   beforeEnter: (to, from, next) => {

&#x20;     console.log('路由独享守卫：进入dashboard前触发')

&#x20;     // 可单独验证该路由的权限

&#x20;     if (hasDashboardAccess()) {

&#x20;       next()

&#x20;     } else {

&#x20;       next('/no-access')

&#x20;     }

&#x20;   }

&#x20; }

]
```

**使用场景**：



*   特殊路由的单独权限校验

*   该路由的前置处理逻辑（如数据预加载）

#### （3）组件内守卫

定义在路由组件内部，监听与该组件相关的路由变化：



```
\<script>

export default {

&#x20; // 1. 进入组件对应的路由前触发（组件实例未创建，无this）

&#x20; beforeRouteEnter(to, from, next) {

&#x20;   console.log('组件内守卫：进入组件前')

&#x20;   // 通过回调获取组件实例

&#x20;   next(vm => {

&#x20;     // vm 即组件实例

&#x20;     vm.initData()

&#x20;   })

&#x20; },

&#x20;&#x20;

&#x20; // 2. 路由参数变化但组件复用（如 /user/1 → /user/2）

&#x20; beforeRouteUpdate(to, from, next) {

&#x20;   console.log('组件内守卫：路由参数更新')

&#x20;   // 可通过this访问组件实例

&#x20;   this.userId = to.params.id

&#x20;   this.loadUserData()

&#x20;   next()

&#x20; },

&#x20;&#x20;

&#x20; // 3. 离开组件对应的路由时触发

&#x20; beforeRouteLeave(to, from, next) {

&#x20;   console.log('组件内守卫：离开组件前')

&#x20;   // 常用于确认未保存的修改

&#x20;   if (this.hasUnsavedChanges) {

&#x20;     if (confirm('是否放弃未保存的内容？')) {

&#x20;       next()

&#x20;     } else {

&#x20;       next(false) // 取消导航

&#x20;     }

&#x20;   } else {

&#x20;     next()

&#x20;   }

&#x20; }

}

\</script>
```

**使用场景**：



*   beforeRouteEnter：组件初始化数据加载（需在组件创建前准备数据）

*   beforeRouteUpdate：处理路由参数变化（避免组件重复创建）

*   beforeRouteLeave：防止用户误操作丢失数据

### 2. 导航守卫的执行顺序

完整的导航解析流程（以从 A 路由跳转到 B 路由为例）：



1.  触发 B 路由的`beforeRouteLeave`（如果 B 组件已加载）

2.  触发全局`beforeEach`守卫

3.  触发 A 路由的`beforeRouteUpdate`（如果 A 组件被复用）

4.  触发 A 路由的`beforeEnter`守卫

5.  解析 A 路由组件（如果是异步组件）

6.  触发 A 组件内的`beforeRouteEnter`

7.  触发全局`beforeResolve`守卫

8.  确认导航

9.  触发全局`afterEach`钩子

10. 执行`beforeRouteEnter`中传给`next`的回调（创建 A 组件实例）

### 3. 路由权限控制的实现方案

#### （1）基于路由元信息的权限设计

在路由配置中通过`meta`字段定义权限要求：



```
// 路由配置

const routes = \[

&#x20; {

&#x20;   path: '/',

&#x20;   component: Home,

&#x20;   meta: { title: '首页' } // 无需权限

&#x20; },

&#x20; {

&#x20;   path: '/profile',

&#x20;   component: Profile,

&#x20;   meta: {&#x20;

&#x20;     title: '个人中心',

&#x20;     requiresAuth: true // 需要登录

&#x20;   }

&#x20; },

&#x20; {

&#x20;   path: '/admin',

&#x20;   component: AdminPanel,

&#x20;   meta: {&#x20;

&#x20;     title: '管理员面板',

&#x20;     requiresAuth: true,

&#x20;     roles: \['admin'] // 仅管理员可访问

&#x20;   }

&#x20; },

&#x20; {

&#x20;   path: '/login',

&#x20;   component: Login

&#x20; },

&#x20; {

&#x20;   path: '/403',

&#x20;   component: Forbidden

&#x20; }

]
```

#### （2）全局权限校验实现

在`beforeEach`中统一处理权限逻辑：



```
// 全局权限控制

router.beforeEach((to, from, next) => {

&#x20; // 1. 获取用户信息（实际项目中从登录状态/Store中获取）

&#x20; const user = {

&#x20;   isLogin: localStorage.getItem('token') !== null, // 是否登录

&#x20;   roles: JSON.parse(localStorage.getItem('roles') || '\[]') // 用户角色

&#x20; }

&#x20;&#x20;

&#x20; // 2. 检查目标路由是否需要登录

&#x20; if (to.meta.requiresAuth) {

&#x20;   // 3. 未登录：跳转到登录页，并记录目标地址（方便登录后跳转回来）

&#x20;   if (!user.isLogin) {

&#x20;     next({&#x20;

&#x20;       path: '/login',

&#x20;       query: { redirect: to.fullPath } // 存储目标路径

&#x20;     })

&#x20;     return

&#x20;   }

&#x20;  &#x20;

&#x20;   // 4. 已登录但需要角色权限

&#x20;   if (to.meta.roles && to.meta.roles.length > 0) {

&#x20;     // 检查用户角色是否包含所需角色

&#x20;     const hasPermission = to.meta.roles.some(role =>&#x20;

&#x20;       user.roles.includes(role)

&#x20;     )

&#x20;    &#x20;

&#x20;     if (hasPermission) {

&#x20;       next() // 有权限，放行

&#x20;     } else {

&#x20;       next('/403') // 无权限，跳转到403页

&#x20;     }

&#x20;     return

&#x20;   }

&#x20; }

&#x20;&#x20;

&#x20; // 5. 无需权限或已通过权限校验，正常放行

&#x20; next()

})
```

#### （3）登录后跳转回原目标页

在登录组件中处理跳转逻辑：



```
\<!-- Login.vue -->

\<template>

&#x20; \<div>

&#x20;   \<form @submit.prevent="handleLogin">

&#x20;     \<!-- 登录表单 -->

&#x20;   \</form>

&#x20; \</div>

\</template>

\<script setup>

import { useRoute, useRouter } from 'vue-router'

const route = useRoute()

const router = useRouter()

const handleLogin = async () => {

&#x20; // 登录逻辑...

&#x20; const loginSuccess = await api.login(username, password)

&#x20;&#x20;

&#x20; if (loginSuccess) {

&#x20;   // 获取登录前的目标路径（默认跳转到首页）

&#x20;   const redirect = route.query.redirect || '/'

&#x20;   // 跳转到目标路径

&#x20;   router.push(redirect)

&#x20; }

}

\</script>
```

#### （4）动态路由权限控制

对于权限差异较大的系统，可动态生成路由表：



```
// 动态生成路由

const generateRoutes = (userRoles) => {

&#x20; // 基础路由（所有用户可见）

&#x20; const basicRoutes = \[

&#x20;   { path: '/', component: Home },

&#x20;   { path: '/login', component: Login }

&#x20; ]

&#x20;&#x20;

&#x20; // 权限路由（根据角色动态添加）

&#x20; const authRoutes = \[]

&#x20;&#x20;

&#x20; // 管理员路由

&#x20; if (userRoles.includes('admin')) {

&#x20;   authRoutes.push({

&#x20;     path: '/admin',

&#x20;     component: AdminPanel

&#x20;   })

&#x20; }

&#x20;&#x20;

&#x20; // 普通用户路由

&#x20; if (userRoles.includes('user')) {

&#x20;   authRoutes.push({

&#x20;     path: '/profile',

&#x20;     component: Profile

&#x20;   })

&#x20; }

&#x20;&#x20;

&#x20; // 合并路由并添加404页面

&#x20; return \[...basicRoutes, ...authRoutes, {

&#x20;   path: '/:pathMatch(.\*)\*',

&#x20;   component: NotFound

&#x20; }]

}

// 在登录后动态添加路由

const handleLogin = async () => {

&#x20; const { roles } = await api.login(/\* ... \*/)

&#x20; const accessibleRoutes = generateRoutes(roles)

&#x20;&#x20;

&#x20; // 动态添加路由

&#x20; accessibleRoutes.forEach(route => {

&#x20;   router.addRoute(route)

&#x20; })

&#x20;&#x20;

&#x20; // 跳转到目标页

&#x20; router.push(redirect)

}
```

### 4. 权限控制的高级场景

#### （1）细粒度按钮权限

结合路由权限，在组件内控制按钮显示：



```
\<template>

&#x20; \<div>

&#x20;   \<button v-if="hasEditPermission">编辑\</button>

&#x20;   \<button v-if="hasDeletePermission">删除\</button>

&#x20; \</div>

\</template>

\<script setup>

import { useStore } from 'pinia'

const store = useStore()

const userRoles = store.state.user.roles

// 判断是否有编辑权限

const hasEditPermission = userRoles.includes('admin') || userRoles.includes('editor')

// 判断是否有删除权限

const hasDeletePermission = userRoles.includes('admin')

\</script>
```

#### （2）权限动态更新

用户权限变化后（如角色变更），重新加载路由：



```
// 权限更新函数

const updatePermissions = async (newRoles) => {

&#x20; // 更新用户角色

&#x20; localStorage.setItem('roles', JSON.stringify(newRoles))

&#x20;&#x20;

&#x20; // 移除现有路由

&#x20; router.getRoutes().forEach(route => {

&#x20;   router.removeRoute(route.name)

&#x20; })

&#x20;&#x20;

&#x20; // 重新添加路由

&#x20; const newRoutes = generateRoutes(newRoles)

&#x20; newRoutes.forEach(route => {

&#x20;   router.addRoute(route)

&#x20; })

&#x20;&#x20;

&#x20; // 刷新当前页面

&#x20; router.go(0)

}
```

### 5. 导航守卫的常见问题与解决方案

#### （1）next () 调用问题

**问题**：忘记调用 next () 导致路由卡死，或多次调用 next () 导致错误。

**解决方案**：确保在所有分支都调用且只调用一次 next ()：



```
// 正确示例

router.beforeEach((to, from, next) => {

&#x20; if (condition) {

&#x20;   next()

&#x20; } else {

&#x20;   next('/login')

&#x20; }

&#x20; // 不要在条件外再次调用next()

})
```

#### （2）无限重定向问题

**问题**：权限校验逻辑错误导致路由在 A 和 B 之间无限跳转。

**解决方案**：添加条件判断避免循环：



```
// 错误示例：未登录用户访问/login会再次被重定向到/login

router.beforeEach((to, from, next) => {

&#x20; if (!isLogin && to.meta.requiresAuth) {

&#x20;   next('/login') // 当to是/login时会导致循环

&#x20; }

})

// 正确示例：排除登录页

router.beforeEach((to, from, next) => {

&#x20; if (!isLogin && to.meta.requiresAuth && to.path !== '/login') {

&#x20;   next('/login') // 只有目标不是登录页时才跳转

&#x20; } else {

&#x20;   next()

&#x20; }

})
```

#### （3）异步权限校验

**问题**：权限校验是异步操作，next () 在异步完成前已调用。

**解决方案**：在异步回调中调用 next ()：



```
router.beforeEach(async (to, from, next) => {

&#x20; // 异步获取权限

&#x20; const hasPermission = await checkPermission(to.path)

&#x20;&#x20;

&#x20; if (hasPermission) {

&#x20;   next()

&#x20; } else {

&#x20;   next('/403')

&#x20; }

})
```

Vue Router 的导航守卫提供了灵活的路由拦截机制，其中全局前置守卫（beforeEach）是实现路由权限控制的核心工具。通过结合路由元信息存储权限要求，在导航守卫中校验用户权限，并根据结果决定放行或跳转，可构建安全可靠的权限控制体系。对于复杂应用，还可结合动态路由生成和组件内权限判断，实现更细粒度的权限管理。

