# computed 属性的两种写法（函数式与对象式）有何不同？

## meta 元数据



```
{

&#x20; "id": "h6i7j8k9-l0m1-2345-nopq-6789012345ef",

&#x20; "type": "answer",

&#x20; "difficulty": "easy",

&#x20; "tags": \["vue"]

}
```

## 答案 1：核心简洁的口语化回答

・函数式：直接传入一个计算函数，只能读取值，不能手动修改，适用于纯计算场景。

・对象式：通过`get`方法定义读取逻辑，`set`方法定义修改逻辑，支持手动修改计算结果，适用于需要反向修改的场景。

・依赖追踪：两者都能自动追踪依赖的响应式数据，但函数式本质是对象式的`get`方法简化写法。

・使用限制：函数式无法设置缓存控制等高级配置，对象式可通过配置项扩展功能。

## 答案 2：口语化扩展回答

computed 属性的两种写法主要区别在是否能修改计算结果和使用场景上。

函数式写法很简单，就是把计算逻辑写成一个函数传进去，比如`computed(() => a + b)`。这种写法只能用来读取计算后的值，没办法手动修改，因为它内部只相当于定义了一个 getter。适合那些纯计算的场景，比如从现有数据里算出一个新值，而且不需要反过来修改这个计算结果。

对象式写法则更灵活，需要明确写出`get`和`set`两个方法。`get`方法和函数式里的计算函数作用一样，用来定义怎么算出结果；`set`方法则用来定义当手动修改计算属性时该做什么，比如`set(newValue) { a = newValue - b }`。这种写法适合需要修改计算属性的场景，比如表单里的双向绑定，用户输入修改了计算属性，这时候可以通过 set 方法反推回去更新依赖的数据。

另外，函数式其实是对象式的简化版，当只需要 getter 的时候用函数式更简洁，代码也更短。但如果有修改需求，就必须用对象式写法，这时候虽然代码长一点，但功能更完整。

## 答案 3：技术深度解析

### 1. 两种写法的基本定义与实现

#### 函数式写法

函数式写法是 computed 属性最常用的形式，本质是只提供了 getter 方法的简化写法：



```
import { ref, computed } from 'vue'

const a = ref(1)

const b = ref(2)

// 函数式写法：仅包含getter

const sum = computed(() => {

&#x20; return a.value + b.value

})

// 使用方式：直接访问.value

console.log(sum.value) // 3
```

**实现原理**：函数式写法会被 Vue 内部转换为包含 getter 方法的对象形式，等效于：



```
const sum = computed({

&#x20; get: () => a.value + b.value

})
```

#### 对象式写法

对象式写法允许同时定义 getter 和 setter 方法，支持对计算属性进行修改：



```
import { ref, computed } from 'vue'

const firstName = ref('张')

const lastName = ref('三')

// 对象式写法：包含get和set

const fullName = computed({

&#x20; // getter：计算并返回结果

&#x20; get: () => {

&#x20;   return \`\${firstName.value}\${lastName.value}\`

&#x20; },

&#x20; // setter：处理手动修改逻辑

&#x20; set: (newValue) => {

&#x20;   // 当fullName.value被修改时执行

&#x20;   const \[newFirst, newLast] = newValue.split(' ')

&#x20;   firstName.value = newFirst

&#x20;   lastName.value = newLast || ''

&#x20; }

})

// 读取

console.log(fullName.value) // "张三"

// 修改

fullName.value = '李四'

console.log(firstName.value) // "李"

console.log(lastName.value) // "四"
```

### 2. 核心差异对比



| 特性        | 函数式写法        | 对象式写法                 |
| --------- | ------------ | --------------------- |
| **语法结构**  | 接收一个函数作为参数   | 接收一个包含 get 和 set 的对象  |
| **可修改性**  | 只读（无法手动修改）   | 可读写（支持手动修改）           |
| **使用场景**  | 纯计算场景，无需反向修改 | 需要双向绑定或反向修改的场景        |
| **返回值控制** | 仅通过返回值控制     | 可通过 setter 主动控制依赖数据   |
| **配置扩展性** | 不支持额外配置      | 支持缓存控制等高级配置           |
| **内部实现**  | 仅包含 getter   | 可同时包含 getter 和 setter |

### 3. 底层实现机制

Vue3 中 computed 的核心实现基于`ComputedRefImpl`类，两种写法最终都会被转换为该类的实例：



```
// 简化的ComputedRefImpl实现

class ComputedRefImpl {

&#x20; constructor(getter, setter, isReadonly) {

&#x20;   this.\_getter = getter

&#x20;   this.\_setter = setter

&#x20;   this.\_isReadonly = isReadonly

&#x20;   // 创建副作用函数

&#x20;   this.effect = effect(getter, {

&#x20;     lazy: true, // 懒执行，首次访问才计算

&#x20;     scheduler: () => {

&#x20;       // 依赖变化时触发更新

&#x20;       trigger(this, 'set', 'value')

&#x20;     }

&#x20;   })

&#x20; }

&#x20; // 读取计算属性时调用

&#x20; get value() {

&#x20;   // 收集依赖

&#x20;   track(this, 'get', 'value')

&#x20;   // 执行getter并缓存结果

&#x20;   this.\_value = this.effect()

&#x20;   return this.\_value

&#x20; }

&#x20; // 修改计算属性时调用

&#x20; set value(newValue) {

&#x20;   if (this.\_isReadonly) {

&#x20;     console.warn('计算属性为只读，无法修改')

&#x20;     return

&#x20;   }

&#x20;   // 执行setter

&#x20;   this.\_setter(newValue)

&#x20; }

}
```



*   **函数式写法**：会创建`isReadonly: true`的实例，`_setter`为 undefined

*   **对象式写法**：会创建`isReadonly: false`的实例，`_setter`为用户定义的函数

### 4. 缓存机制与依赖追踪

两种写法都共享 computed 的核心特性：**缓存机制**和**依赖追踪**

#### 缓存机制

computed 属性会缓存计算结果，只有当依赖的响应式数据变化时才会重新计算：



```
const count = ref(0)

// 函数式computed

const double = computed(() => {

&#x20; console.log('重新计算')

&#x20; return count.value \* 2

})

console.log(double.value) // 输出"重新计算"和0

console.log(double.value) // 直接输出0（使用缓存，不重新计算）

count.value = 1

console.log(double.value) // 输出"重新计算"和2（依赖变化，重新计算）
```

#### 依赖追踪

computed 会自动追踪内部使用的响应式数据，仅当这些数据变化时才更新：



```
const a = ref(1)

const b = ref(2)

const c = ref(3)

// 仅追踪a和b的变化

const sum = computed(() => a.value + b.value)

console.log(sum.value) // 3

c.value = 4 // 不影响sum，无更新

a.value = 2 // 影响sum，重新计算

console.log(sum.value) // 4
```

### 5. 适用场景深度分析

#### 函数式写法适用场景



1.  **纯展示型计算**



```
// 计算商品总价

const price = ref(100)

const quantity = ref(2)

const total = computed(() => price.value \* quantity.value)
```



*   从多个数据中派生展示值，无需修改

1.  **数据格式化**



```
// 格式化日期

const date = ref(new Date())

const formattedDate = computed(() => {

&#x20; return date.value.toLocaleDateString('zh-CN')

})
```



*   对原始数据进行格式化处理后展示

1.  **筛选与转换**



```
// 筛选偶数

const numbers = ref(\[1, 2, 3, 4, 5])

const evenNumbers = computed(() => {

&#x20; return numbers.value.filter(n => n % 2 === 0)

})
```



*   对列表数据进行筛选或转换

#### 对象式写法适用场景



1.  **双向绑定场景**



```
// 表单中的全名双向绑定

const user = reactive({

&#x20; firstName: '张',

&#x20; lastName: '三'

})

const fullName = computed({

&#x20; get: () => \`\${user.firstName}\${user.lastName}\`,

&#x20; set: (value) => {

&#x20;   const \[first, last] = value.split(' ')

&#x20;   user.firstName = first

&#x20;   user.lastName = last || ''

&#x20; }

})
```

模板中可直接双向绑定：



```
\<input v-model="fullName" />
```



*   表单中需要双向绑定计算属性

1.  **复杂状态转换**



```
// 百分比与小数的双向转换

const rate = ref(0.15)

const percentage = computed({

&#x20; get: () => Math.round(rate.value \* 100),

&#x20; set: (value) => {

&#x20;   rate.value = Math.min(Math.max(value / 100, 0), 1) // 限制在0-1之间

&#x20; }

})
```



*   需要将计算结果反向转换为原始数据

1.  **多源数据聚合**



```
// 地址聚合与拆分

const address = reactive({

&#x20; province: '',

&#x20; city: '',

&#x20; district: ''

})

const fullAddress = computed({

&#x20; get: () => {

&#x20;   return \`\${address.province}\${address.city}\${address.district}\`

&#x20; },

&#x20; set: (value) => {

&#x20;   // 复杂的地址解析逻辑

&#x20;   const \[province, city, district] = parseAddress(value)

&#x20;   address.province = province

&#x20;   address.city = city

&#x20;   address.district = district

&#x20; }

})
```



*   聚合多个数据源，并支持反向拆分

### 6. 性能考量与最佳实践



1.  **避免在 computed 中执行 heavy 操作**

    计算函数应保持轻量，复杂计算会影响性能：



```
// 不推荐：复杂计算

const complexResult = computed(() => {

&#x20; // 耗时操作

&#x20; for (let i = 0; i < 1000000; i++) {

&#x20;   // ...

&#x20; }

})
```



1.  **合理利用缓存**

    对于相同输入始终返回相同结果的计算，适合用 computed 缓存：



```
// 推荐：结果可缓存的计算

const filteredList = computed(() => {

&#x20; return list.value.filter(item => item.status === activeStatus.value)

})
```



1.  **避免在 getter 中修改响应式数据**

    这会导致无限循环和性能问题：



```
// 不推荐：在getter中修改数据

const count = ref(0)

const increment = computed({

&#x20; get: () => {

&#x20;   count.value++ // 错误：会触发无限更新

&#x20;   return count.value

&#x20; },

&#x20; set: () => {}

})
```



1.  **明确区分可读写场景**

    不需要修改的计算属性应使用函数式写法，使意图更清晰：



```
// 推荐：纯计算用函数式

const readOnlyComputed = computed(() => a.value + b.value)

// 推荐：需要修改用对象式

const writableComputed = computed({

&#x20; get: () => {},

&#x20; set: () => {}

})
```

通过理解 computed 属性两种写法的差异和适用场景，可以在 Vue 项目中更合理地使用计算属性，既保证代码的简洁性，又能满足复杂的业务需求。函数式写法适合简单的纯计算场景，而对象式写法则为需要双向交互的场景提供了灵活的解决方案。

