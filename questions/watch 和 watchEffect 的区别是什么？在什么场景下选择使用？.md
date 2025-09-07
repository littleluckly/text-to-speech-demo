# watch 和 watchEffect 的区别是什么？在什么场景下选择使用？

## meta 元数据



```
{

&#x20; "id": "g5h6i7j8-k9l0-1234-mnop-5678901234de",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["vue3"]

}
```

## 答案 1：核心简洁的口语化回答

・依赖指定：watch 需明确指定监听的响应式数据，watchEffect 自动追踪内部使用的响应式数据。

・执行时机：watch 默认懒执行（首次不触发），watchEffect 默认立即执行（首次会触发）。

・参数获取：watch 能获取新旧值，watchEffect 无法直接获取。

・使用场景：watch 适合监听特定数据变化并需新旧值对比的场景；watchEffect 适合依赖多个数据，且无需新旧值的场景。

## 答案 2：口语化扩展回答

watch 和 watchEffect 都是 Vue 中监听响应式数据变化的工具，但用法和特点不一样。

watch 需要明确告诉它要监听哪个数据，比如 watch (count, ...) 就只盯着 count 的变化。而且它默认在数据第一次加载时不执行，只有当监听的数据真的变了才会触发。另外，watch 的回调函数里能拿到变化前后的值，这在需要对比新旧状态的时候很有用，比如判断数据是否真的改变了再执行操作。

watchEffect 就简单多了，不用指定监听谁，它会自动追踪函数里用到的所有响应式数据。不过它有个特点，就是一创建就会执行一次，之后依赖的数据变了才会再执行。但它的回调里拿不到旧值，只能用当前的新值。

实际用的时候，如果只需要监听特定数据，还得知道变化前后的情况，比如表单验证时对比输入值是否符合要求，就用 watch。如果要监听多个数据，或者依赖关系比较复杂，比如数据变化后要同时更新多个关联状态，用 watchEffect 更方便，能少写不少代码。

## 答案 3：技术深度解析

### 1. 核心原理与实现差异

#### watch 的工作原理

watch 基于**显式依赖追踪**，需要手动指定监听源，其核心逻辑是：



1.  接收用户指定的监听源（可以是 ref、reactive 属性、getter 函数等）

2.  当监听源发生变化时，执行回调函数

3.  回调函数可获取变化前后的值

简化实现逻辑：



```
function watch(source, callback, options = {}) {

&#x20; // 解析监听源，获取其值

&#x20; const getSourceValue = () => /\* 从source中提取值 \*/;

&#x20;&#x20;

&#x20; // 初始化旧值

&#x20; let oldValue;

&#x20; // 是否懒执行（默认true）

&#x20; if (!options.immediate) {

&#x20;   oldValue = getSourceValue();

&#x20; }

&#x20;&#x20;

&#x20; // 追踪依赖变化

&#x20; effect(() => {

&#x20;   const newValue = getSourceValue();

&#x20;   // 依赖变化时执行回调

&#x20;   if (hasChanged(newValue, oldValue)) {

&#x20;     callback(newValue, oldValue);

&#x20;     oldValue = newValue;

&#x20;   }

&#x20; }, {&#x20;

&#x20;   lazy: options.immediate ? false : true&#x20;

&#x20; });

}
```

#### watchEffect 的工作原理

watchEffect 基于**隐式依赖追踪**，自动收集函数内部使用的响应式数据，核心逻辑是：



1.  立即执行一次用户提供的副作用函数

2.  追踪函数执行过程中访问的所有响应式数据

3.  当任何追踪的数据变化时，重新执行副作用函数

简化实现逻辑：



```
function watchEffect(effectFn, options = {}) {

&#x20; // 立即执行副作用函数并追踪依赖

&#x20; effect(effectFn, {

&#x20;   lazy: false, // 非懒执行，立即执行

&#x20;   scheduler: () => {

&#x20;     // 依赖变化时重新执行

&#x20;     effectFn();

&#x20;   }

&#x20; });

}
```

### 2. 关键区别对比



| 特性        | watch                             | watchEffect                   |
| --------- | --------------------------------- | ----------------------------- |
| **依赖指定**  | 需显式指定监听源                          | 自动追踪函数内使用的响应式数据               |
| **首次执行**  | 默认不执行（懒执行），可通过 immediate: true 开启 | 默认立即执行，可通过 flush: 'post' 调整时机 |
| **参数获取**  | 回调函数接收 (newValue, oldValue)       | 无参数，无法直接获取旧值                  |
| **停止监听**  | 调用返回的停止函数                         | 调用返回的停止函数                     |
| **清理副作用** | 在回调中返回清理函数                        | 在副作用函数中返回清理函数                 |
| **执行时机**  | 默认同步执行，可通过 flush 配置               | 默认同步执行，可通过 flush 配置           |

### 3. 使用方式与示例

#### watch 的使用方式



1.  **监听单个 ref**



```
import { ref, watch } from 'vue'

const count = ref(0)

// 监听ref

watch(count, (newVal, oldVal) => {

&#x20; console.log(\`count从\${oldVal}变成了\${newVal}\`)

})

count.value++ // 触发回调：count从0变成了1
```



1.  **监听 reactive 对象属性**



```
import { reactive, watch } from 'vue'

const user = reactive({ name: '张三', age: 30 })

// 监听对象属性（需用getter函数）

watch(

&#x20; () => user.age,

&#x20; (newAge, oldAge) => {

&#x20;   console.log(\`年龄从\${oldAge}变成了\${newAge}\`)

&#x20; }

)

user.age = 31 // 触发回调：年龄从30变成了31
```



1.  **监听多个源**



```
watch(

&#x20; \[() => user.name, count], // 监听多个源

&#x20; (\[newName, newCount], \[oldName, oldCount]) => {

&#x20;   console.log(\`姓名变化: \${oldName} → \${newName}\`)

&#x20;   console.log(\`数量变化: \${oldCount} → \${newCount}\`)

&#x20; },

&#x20; { immediate: true } // 立即执行一次

)
```

#### watchEffect 的使用方式



1.  **基本用法**



```
import { ref, watchEffect } from 'vue'

const count = ref(0)

const message = ref('')

// 自动追踪count和message

const stop = watchEffect(() => {

&#x20; console.log(\`count: \${count.value}, message: \${message.value}\`)

})

// 首次执行输出：count: 0, message:&#x20;

count.value++ // 输出：count: 1, message:&#x20;

message.value = 'hello' // 输出：count: 1, message: hello

// 停止监听

stop()

count.value++ // 不再触发
```



1.  **清理副作用**



```
watchEffect(() => {

&#x20; const timer = setInterval(() => {

&#x20;   console.log(count.value)

&#x20; }, 1000)

&#x20;&#x20;

&#x20; // 返回清理函数，在下次执行前或停止时调用

&#x20; return () => clearInterval(timer)

})
```



1.  **调整执行时机**



```
// 组件更新后执行（适合操作DOM）

watchEffect(() => {

&#x20; // 操作DOM的逻辑

}, { flush: 'post' })
```

### 4. 适用场景分析

#### 优先使用 watch 的场景



1.  **需要对比新旧值的场景**

*   表单验证：判断用户输入的新值是否符合要求，可能需要与旧值对比

*   数据变更日志：记录数据从旧值到新值的变更过程



```
// 表单验证示例

watch(

&#x20; () => form.password,

&#x20; (newVal, oldVal) => {

&#x20;   if (newVal.length < 6 && newVal !== oldVal) {

&#x20;     error.value = '密码长度不能少于6位'

&#x20;   } else {

&#x20;     error.value = ''

&#x20;   }

&#x20; }

)
```



1.  **只需要在特定数据变化时执行**

*   按需加载数据：只有当筛选条件变化时才重新请求数据

*   特定状态触发动画：只有当显示状态变为 true 时才执行动画



```
// 按需加载数据示例

watch(

&#x20; () => filter.value,

&#x20; async (newFilter) => {

&#x20;   loading.value = true

&#x20;   data.value = await fetchData(newFilter)

&#x20;   loading.value = false

&#x20; }

)
```



1.  **需要延迟执行或防抖节流**

*   搜索输入：用户输入停止后再执行搜索请求



```
// 防抖示例

watch(

&#x20; () => searchQuery.value,

&#x20; debounce(async (query) => {

&#x20;   results.value = await searchApi(query)

&#x20; }, 500)

)
```

#### 优先使用 watchEffect 的场景



1.  **依赖多个数据的复杂逻辑**

*   联合查询：当多个筛选条件中的任何一个变化时，重新计算结果



```
// 联合查询示例

watchEffect(async () => {

&#x20; // 自动追踪keyword和category的变化

&#x20; results.value = await queryData(keyword.value, category.value)

})
```



1.  **需要立即执行的初始化逻辑**

*   数据初始化：组件加载时立即执行，并在依赖变化时更新



```
// 数据初始化示例

watchEffect(() => {

&#x20; // 首次执行时加载初始数据

&#x20; // 当userId变化时重新加载

&#x20; if (userId.value) {

&#x20;   loadUserInfo(userId.value)

&#x20; }

})
```



1.  **需要清理副作用的场景**

*   事件监听：添加事件监听后，需要在依赖变化或组件卸载时移除



```
// 事件监听示例

watchEffect(() => {

&#x20; const handleScroll = () => {

&#x20;   // 处理滚动事件

&#x20; }

&#x20; window.addEventListener('scroll', handleScroll)

&#x20;&#x20;

&#x20; // 清理函数：移除事件监听

&#x20; return () => window.removeEventListener('scroll', handleScroll)

})
```

### 5. 高级特性与最佳实践

#### 停止监听

两种方法都返回一个停止函数，用于手动停止监听：



```
// 停止watch

const stopWatch = watch(count, () => {})

stopWatch()

// 停止watchEffect

const stopEffect = watchEffect(() => {})

stopEffect()
```

#### 清理副作用

在需要处理异步操作时，清理函数可以避免竞态条件：



```
// watch的清理函数

watch(searchQuery, async (query, oldQuery, onCleanup) => {

&#x20; const abortController = new AbortController()

&#x20;&#x20;

&#x20; // 注册清理函数

&#x20; onCleanup(() => {

&#x20;   abortController.abort() // 取消上一次请求

&#x20; })

&#x20;&#x20;

&#x20; const result = await fetch(\`/search?query=\${query}\`, {

&#x20;   signal: abortController.signal

&#x20; })

})

// watchEffect的清理函数

watchEffect(() => {

&#x20; const abortController = new AbortController()

&#x20;&#x20;

&#x20; fetch(\`/search?query=\${searchQuery.value}\`, {

&#x20;   signal: abortController.signal

&#x20; })

&#x20;&#x20;

&#x20; // 返回清理函数

&#x20; return () => abortController.abort()

})
```

#### 执行时机控制

通过`flush`选项控制回调执行时机：



*   `flush: 'sync'`：同步执行（默认）

*   `flush: 'pre'`：组件更新前执行

*   `flush: 'post'`：组件更新后执行（适合操作 DOM）



```
// 操作DOM的场景

watchEffect(() => {

&#x20; // 确保在DOM更新后执行

&#x20; const rect = el.value.getBoundingClientRect()

&#x20; // 基于DOM位置的操作

}, { flush: 'post' })
```

### 6. 常见问题与解决方案

#### 问题 1：watch 不触发

**可能原因**：



*   监听的是 reactive 对象的属性但未使用 getter 函数

*   直接修改了数组的索引或长度

**解决方案**：



```
// 正确监听reactive对象属性

watch(

&#x20; () => obj.prop, // 使用getter函数

&#x20; () => {}

)

// 正确监听数组变化

watch(

&#x20; () => arr.length,

&#x20; () => {}

)

// 或使用数组方法修改

arr.value.push(newItem)
```

#### 问题 2：watchEffect 触发过于频繁

**可能原因**：



*   依赖了不必要的响应式数据

*   副作用函数中修改了被追踪的响应式数据

**解决方案**：



```
// 只依赖必要数据

watchEffect(() => {

&#x20; // 只使用必要的响应式属性

&#x20; const { prop1 } = obj.value

&#x20; doSomething(prop1)

})

// 避免在副作用中修改依赖

watchEffect(() => {

&#x20; // 错误：会导致无限循环

&#x20; // count.value++

&#x20;&#x20;

&#x20; // 正确：使用条件判断

&#x20; if (count.value < 10) {

&#x20;   // 安全操作

&#x20; }

})
```

#### 问题 3：无法获取正确的旧值

**可能原因**：



*   监听的是复杂对象，新旧值指向同一引用

**解决方案**：



```
// 监听对象的序列化值（适用于简单对象）

watch(

&#x20; () => JSON.stringify(obj),

&#x20; (newStr, oldStr) => {

&#x20;   const newObj = JSON.parse(newStr)

&#x20;   const oldObj = JSON.parse(oldStr)

&#x20;   // 对比新旧对象

&#x20; }

)

// 或监听特定属性

watch(

&#x20; () => \[obj.prop1, obj.prop2],

&#x20; (\[new1, new2], \[old1, old2]) => {}

)
```

通过理解 watch 和 watchEffect 的核心区别和适用场景，可以在 Vue3 项目中更合理地选择监听方式，写出更清晰、高效的响应式逻辑。两者相辅相成，根据具体需求灵活运用能极大提升开发效率。

