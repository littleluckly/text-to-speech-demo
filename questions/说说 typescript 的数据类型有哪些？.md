# 说说 typescript 的数据类型有哪些？

## meta 元数据



```
{

&#x20; "id": "c3d4e5f6-a7b8-9012-cdef-34567890abcd",

&#x20; "type": "answer",

&#x20; "difficulty": "easy",

&#x20; "tags": \["typeScript"]

}
```

## 答案 1：核心简洁的口语化回答

・基础类型：number、string、boolean、null、undefined、symbol、bigint。

・引用类型：object（包含数组 array、函数 function、对象字面量等）。

・特殊类型：any（任意类型）、unknown（未知类型）、void（无返回值）、never（永不存在的值）。

・高级类型：联合类型（|）、交叉类型（&）、泛型（T）、枚举（enum）、接口（interface）。

## 答案 2：口语化扩展回答

TypeScript 的数据类型其实是在 JavaScript 基础上做了扩展，首先基础类型和 JS 差不多，像数字、字符串、布尔值这些都有，还有 null 和 undefined。不过 TS 里多了 bigint，用来处理特别大的整数，还有 symbol，能创建唯一的值。

引用类型里，对象、数组、函数这些都算，TS 会更严格地检查它们的结构。比如数组，你可以指定它里面元素的类型，像 number \[] 就表示全是数字的数组。

比较特殊的是 any 和 unknown，any 是可以随便赋值任何类型，用多了会失去 TS 类型检查的意义；unknown 也类似，但更安全，不能直接操作，得先确认类型。void 一般用在函数上，表示函数没有返回值。never 则更特殊，比如那些会抛出错误或者永远不会结束的函数，就用 never。

还有联合类型，就是一个变量可以是几种类型中的一种，用 | 隔开。交叉类型则是把多个类型合并成一个，用 & 连接。枚举 enum 能给一组数值起名字，让代码更易读。接口 interface 则可以定义对象的结构，规定对象应该有哪些属性和方法。

## 答案 3：技术深度解析

### 1. 基础数据类型

基础数据类型是 TypeScript 中最基本的类型，大多与 JavaScript 一致，但增加了类型检查。



*   **number**：表示所有数字，包括整数、浮点数、NaN 等。



```
let age: number = 25;

let height: number = 1.85;

let notANumber: number = NaN; // 合法，NaN属于number类型
```



*   **string**：表示文本数据，可用单引号、双引号或反引号包裹。



```
let name: string = "张三";

let message: string = \`我叫\${name}，今年\${age}岁\`; // 支持模板字符串
```



*   **boolean**：只有 true 和 false 两个值。



```
let isStudent: boolean = true;

let hasJob: boolean = false;
```



*   **null 和 undefined**：分别表示空值和未定义，默认情况下是所有类型的子类型。



```
let empty: null = null;

let uninitialized: undefined = undefined;

let temp: string = null; // 在非严格模式下合法
```



*   **symbol**：表示唯一且不可变的值，通过 Symbol () 创建。



```
let id1: symbol = Symbol("id");

let id2: symbol = Symbol("id");

console.log(id1 === id2); // 输出false，即使描述相同，symbol也不相等
```



*   **bigint**：用于表示大于 2^53 - 1 的整数，通过在数字后加 n 或使用 BigInt () 创建。



```
let bigNum1: bigint = 1234567890123456789012345678901234567890n;

let bigNum2: bigint = BigInt(1234567890);
```

### 2. 引用数据类型

引用类型的值存储的是指向数据的引用，TypeScript 对其有更严格的结构检查。



*   **object**：表示非原始类型的所有值，包括对象字面量、数组、函数等。



```
let person: object = { name: "张三", age: 25 };

let arr: object = \[1, 2, 3];

let func: object = () => {};
```



*   **array**：表示数组，可指定数组元素的类型，有两种写法。



```
let numbers: number\[] = \[1, 2, 3]; // 推荐写法

let strings: Array\<string> = \["a", "b", "c"]; // 泛型写法

let mixed: (number | string)\[] = \[1, "a", 2]; // 联合类型数组
```



*   **function**：表示函数，可指定参数类型和返回值类型。



```
// 声明一个接收两个number参数，返回number的函数类型

let add: (a: number, b: number) => number = (x, y) => x + y;
```

### 3. 特殊数据类型



*   **any**：表示任意类型，变量声明为 any 后，TypeScript 会关闭对该变量的类型检查。



```
let value: any = "hello";

value = 123; // 合法

value = true; // 合法

value.toUpperCase(); // 即使value当前是number，也不会报错
```

> 注意：过度使用 any 会失去 TypeScript 的优势，应尽量避免。



*   **unknown**：与 any 类似，但更安全，不能直接对 unknown 类型的变量进行操作，需先确认类型。



```
let unknownValue: unknown = "hello";

// unknownValue.toUpperCase(); // 直接操作会报错

if (typeof unknownValue === "string") {

&#x20; unknownValue.toUpperCase(); // 类型确认后可操作

}
```



*   **void**：表示函数没有返回值（或返回 undefined）。



```
function logMessage(message: string): void {

&#x20; console.log(message);

&#x20; // 可省略return，或return undefined

}
```



*   **never**：表示永不存在的值的类型，如抛出错误的函数、无限循环的函数。



```
// 抛出错误的函数，永远不会有返回值

function throwError(message: string): never {

&#x20; throw new Error(message);

}

// 无限循环的函数，永远不会结束

function infiniteLoop(): never {

&#x20; while (true) {}

}
```

### 4. 高级数据类型



*   **联合类型（Union Types）**：表示变量可以是多种类型中的一种，用 | 分隔。



```
let data: string | number;

data = "hello"; // 合法

data = 123; // 合法

// data = true; // 不合法，boolean不在联合类型中

// 联合类型的类型守卫

function handleData(data: string | number) {

&#x20; if (typeof data === "string") {

&#x20;   console.log(data.length); // 类型收窄为string

&#x20; } else {

&#x20;   console.log(data.toFixed(2)); // 类型收窄为number

&#x20; }

}
```



*   **交叉类型（Intersection Types）**：表示将多个类型合并为一个，用 & 连接。



```
interface Person {

&#x20; name: string;

}

interface Contact {

&#x20; phone: string;

}

// 交叉类型同时拥有Person和Contact的属性

type PersonWithContact = Person & Contact;

let person: PersonWithContact = {

&#x20; name: "张三",

&#x20; phone: "123456789"

};
```



*   **泛型（Generics）**：允许在定义函数、接口或类时不指定具体类型，使用时再指定。



```
// 泛型函数，T是类型变量，代表传入的类型

function identity\<T>(arg: T): T {

&#x20; return arg;

}

let num: number = identity\<number>(123);

let str: string = identity\<string>("hello");

// 泛型接口

interface Container\<T> {

&#x20; value: T;

}

let numberContainer: Container\<number> = { value: 123 };
```



*   **枚举（Enum）**：用于定义命名的常量集合，默认从 0 开始编号，也可手动指定值。



```
// 数字枚举

enum Direction {

&#x20; Up, // 0

&#x20; Down, // 1

&#x20; Left, // 2

&#x20; Right // 3

}

console.log(Direction.Up); // 输出0

// 字符串枚举

enum Message {

&#x20; Success = "操作成功",

&#x20; Error = "操作失败"

}

console.log(Message.Success); // 输出"操作成功"
```



*   **接口（Interface）**：用于定义对象的结构，规定对象必须包含的属性和方法。



```
interface User {

&#x20; id: number;

&#x20; name: string;

&#x20; age?: number; // 可选属性

&#x20; readonly email: string; // 只读属性

&#x20; greet(): string; // 方法

}

let user: User = {

&#x20; id: 1,

&#x20; name: "张三",

&#x20; email: "zhangsan@example.com",

&#x20; greet() {

&#x20;   return \`Hello, I'm \${this.name}\`;

&#x20; }

};

// user.email = "new@example.com"; // 错误，只读属性不能修改
```

