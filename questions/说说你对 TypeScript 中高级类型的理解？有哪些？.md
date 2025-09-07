# 说说你对 TypeScript 中高级类型的理解？有哪些？

## meta 元数据



```
{

&#x20; "id": "b3c4d5e6-f7g8-9012-bcde-34567890abcd",

&#x20; "type": "answer",

&#x20; "difficulty": "difficult",

&#x20; "tags": \["typeScript"]

}
```

## 答案 1：核心简洁的口语化回答

・TypeScript 高级类型是基于基础类型扩展的复杂类型工具，用于处理复杂的类型关系和转换，增强类型系统的灵活性。

・常见的高级类型包括：联合类型（|）、交叉类型（&）、类型别名（type）、泛型工具类型（Partial、Readonly 等）、条件类型（T extends U ? X : Y）、映射类型、索引类型、类型守卫等。

・它们能实现类型提取、转换、过滤等操作，解决复杂场景下的类型定义问题，提升代码的类型安全性和复用性。

## 答案 2：口语化扩展回答

TypeScript 的高级类型其实就是在基础类型之上，提供的更灵活、更复杂的类型处理方式。它们不像 number、string 这些基础类型那么简单，而是用来解决实际开发中更复杂的类型问题，比如处理不同类型的组合、转换已有类型、或者根据条件动态生成新类型。

比如联合类型，就是把几个类型组合起来，让一个变量可以是其中任意一种类型，像 “string | number” 就表示这个变量要么是字符串要么是数字。交叉类型则是把多个类型合并成一个，新类型会拥有所有类型的属性，适合需要组合多个接口的场景。

还有像 Partial 这种泛型工具类型特别实用，能把一个接口的所有属性都变成可选的，在更新数据的时候特别方便，不用每次都传全所有字段。条件类型就更灵活了，能根据一个条件来决定用哪个类型，比如判断一个类型是不是数组，如果是就提取它的元素类型，不是就保持原样。

这些高级类型让 TypeScript 的类型系统更强大，能应对各种复杂的业务场景，虽然看起来有点复杂，但学会了之后能大大提升代码的类型安全性，减少很多潜在的 bug。

## 答案 3：技术深度解析

### 1. 对 TypeScript 高级类型的理解

TypeScript 高级类型是构建在基础类型（如 number、string、boolean 等）和泛型之上的复杂类型系统扩展，它们提供了一套强大的类型操作工具，用于处理**类型之间的关系**、**类型转换**和**类型推导**，解决复杂业务场景下的类型定义问题。

高级类型的核心价值在于：



*   **增强类型表达能力**：能够描述更复杂的类型关系，如 “一个类型是另一个类型的子集”“类型 A 和类型 B 的交集” 等

*   **提升类型复用性**：通过类型转换和组合，减少重复的类型定义

*   **实现类型安全的复杂逻辑**：在编译阶段捕获更多潜在错误，确保类型一致性

*   **支持元编程**：允许基于已有类型动态生成新类型

### 2. 常见的高级类型及应用

#### （1）联合类型（Union Types）

联合类型表示一个值可以是多种类型中的一种，使用`|`分隔不同类型。

**语法**：`Type1 | Type2 | Type3`

**示例**：



```
// 基础联合类型

type StringOrNumber = string | number;

let value: StringOrNumber;

value = "hello"; // 合法

value = 42; // 合法

// value = true; // 错误：boolean不是联合类型的一部分

// 联合类型与类型守卫

type Square = { kind: "square"; size: number };

type Circle = { kind: "circle"; radius: number };

type Shape = Square | Circle;

function area(shape: Shape): number {

&#x20; // 使用类型守卫（discriminated union）判断具体类型

&#x20; if (shape.kind === "square") {

&#x20;   return shape.size \* shape.size; // 类型收窄为Square

&#x20; } else {

&#x20;   return Math.PI \* shape.radius \*\*2; // 类型收窄为Circle

&#x20; }

}
```

**应用场景**：



*   表示变量可能的多种类型（如 API 返回的不同数据结构）

*   处理互斥的选项或状态

*   实现有区分的联合（discriminated union），通过共同字段区分不同类型

#### （2）交叉类型（Intersection Types）

交叉类型将多个类型合并为一个类型，新类型拥有所有类型的属性和方法，使用`&`连接不同类型。

**语法**：`Type1 & Type2 & Type3`

**示例**：



```
// 接口交叉

interface Person {

&#x20; name: string;

&#x20; age: number;

}

interface Contact {

&#x20; phone: string;

&#x20; email: string;

}

// 交叉类型同时拥有Person和Contact的所有属性

type PersonWithContact = Person & Contact;

const person: PersonWithContact = {

&#x20; name: "张三",

&#x20; age: 25,

&#x20; phone: "123456789",

&#x20; email: "zhangsan@example.com"

};

// 函数交叉（较少见，用于合并函数类型）

type Add = (a: number, b: number) => number;

type Log = (message: string) => void;

type AddAndLog = Add & Log;

const func: AddAndLog = Object.assign(

&#x20; (a: number, b: number) => a + b,

&#x20; { (message: string) => console.log(message) }

);
```

**应用场景**：



*   组合多个接口的属性（如合并用户信息和联系方式）

*   扩展已有类型（不修改原类型的情况下添加新属性）

*   实现混入（mixin）模式

#### （3）类型别名（Type Aliases）

类型别名用于给已有类型起一个新名字，使用`type`关键字定义，支持基础类型、联合类型、交叉类型等各种类型。

**语法**：`type AliasName = Type;`

**示例**：



```
// 基础类型别名

type UserID = string;

type Age = number;

// 联合类型别名

type Status = "pending" | "approved" | "rejected";

// 对象类型别名

type Point = {

&#x20; x: number;

&#x20; y: number;

};

// 泛型类型别名

type Container\<T> = {

&#x20; value: T;

&#x20; getValue: () => T;

};

const numContainer: Container\<number> = {

&#x20; value: 10,

&#x20; getValue() {

&#x20;   return this.value;

&#x20; }

};
```

**与接口的区别**：



*   类型别名不能被`extends`和`implements`，接口可以

*   类型别名不会创建新类型，只是已有类型的别名；接口会创建新类型

*   类型别名可以表示基本类型、联合类型等，接口只能表示对象类型

**应用场景**：



*   简化复杂类型的引用（如长联合类型）

*   为类型提供更语义化的名称

*   定义泛型类型模板

#### （4）泛型工具类型（Generic Utility Types）

TypeScript 内置了一系列泛型工具类型，用于常见的类型转换操作，这些工具类型位于`lib.es5.d.ts`中，可以直接使用。

**常用工具类型**：

1.\*\* Partial\*\*：将 T 的所有属性变为可选



```
interface User {

&#x20; id: number;

&#x20; name: string;

&#x20; age: number;

}

// { id?: number; name?: string; age?: number }

type PartialUser = Partial\<User>;

// 应用：更新用户信息时无需传全所有字段

function updateUser(user: User, changes: Partial\<User>): User {

&#x20; return { ...user, ...changes };

}
```

2.\*\* Readonly\*\*：将 T 的所有属性变为只读



```
type ReadonlyUser = Readonly\<User>;

const user: ReadonlyUser = { id: 1, name: "张三", age: 25 };

// user.name = "李四"; // 错误：只读属性不能修改
```

3.\*\* Pick\<T, K>\*\*：从 T 中挑选出属性 K（K 是 T 的属性键的子集）



```
// { name: string }

type UserName = Pick\<User, "name">;

// { id: number; age: number }

type UserIdAndAge = Pick\<User, "id" | "age">;
```

4.\*\* Omit\<T, K>\*\*：从 T 中排除属性 K



```
// { name: string; age: number }

type UserWithoutId = Omit\<User, "id">;
```

5.\*\* Exclude\<T, U>\*\*：从 T 中排除可以赋值给 U 的类型（用于联合类型）



```
// "b" | "c"（排除了与string字面量"a"匹配的类型）

type Excluded = Exclude<"a" | "b" | "c", "a">;
```

6.\*\* Extract\<T, U>\*\*：从 T 中提取可以赋值给 U 的类型（与 Exclude 相反）



```
// "a"（只保留与string字面量"a"匹配的类型）

type Extracted = Extract<"a" | "b" | "c", "a">;
```

7.\*\* ReturnType\*\*：获取函数 T 的返回值类型



```
type Func = () => { id: number; name: string };

// { id: number; name: string }

type FuncReturnType = ReturnType\<Func>;
```

**应用场景**：



*   快速转换已有类型（如创建可选属性版本的接口）

*   提取函数参数或返回值类型（实现类型安全的函数包装）

*   基于已有类型创建新的相关类型，减少重复定义

#### （5）条件类型（Conditional Types）

条件类型根据条件表达式判断类型关系，返回不同的类型，语法类似三元运算符。

**语法**：`T extends U ? X : Y`（如果 T 可赋值给 U，则返回 X，否则返回 Y）

**示例**：



```
// 基础条件类型

type IsString\<T> = T extends string ? true : false;

type A = IsString\<string>; // true

type B = IsString\<number>; // false

// 提取数组元素类型

type ElementType\<T> = T extends Array\<infer U> ? U : T;

type C = ElementType\<number\[]>; // number

type D = ElementType\<string>; // string

type E = ElementType\<boolean\[]>; // boolean

// 分布式条件类型（对联合类型生效）

type ToArray\<T> = T extends any ? T\[] : never;

type F = ToArray\<string | number>; // string\[] | number\[]
```

**关键特性**：

-\*\* 分布式条件类型 **：当 T 是联合类型时，条件类型会自动分发到每个成员**

**-** 类型推断（infer）\*\*：使用`infer`关键字在条件类型中推断类型变量

**应用场景**：



*   基于类型关系动态生成新类型

*   实现类型提取（如从函数中提取参数类型）

*   处理联合类型的每个成员

#### （6）映射类型（Mapped Types）

映射类型通过遍历已有类型的属性（key）创建新类型，语法类似对象字面量。

**语法**：



```
type MappedType\<T> = {

&#x20; \[P in keyof T]: Type;

};
```

**示例**：



```
interface User {

&#x20; id: number;

&#x20; name: string;

&#x20; age: number;

}

// 将所有属性变为可选（类似Partial的实现）

type MyPartial\<T> = {

&#x20; \[P in keyof T]?: T\[P];

};

type PartialUser = MyPartial\<User>;

// 将所有属性变为只读

type MyReadonly\<T> = {

&#x20; readonly \[P in keyof T]: T\[P];

};

type ReadonlyUser = MyReadonly\<User>;

// 转换属性类型（如将所有属性变为string）

type Stringify\<T> = {

&#x20; \[P in keyof T]: string;

};

type StringifiedUser = Stringify\<User>; // { id: string; name: string; age: string }

// 添加前缀

type Prefix\<T, P extends string> = {

&#x20; \[K in keyof T as \`\${P}\${Capitalize\<string & K>}\`]: T\[K];

};

type PrefixedUser = Prefix\<User, "user">; // { userId: number; userName: string; userAge: number }
```

**应用场景**：



*   批量转换类型的属性（如添加只读修饰符、改变属性类型）

*   基于已有类型创建变体类型（如可选版、只读版）

*   实现自定义的类型工具（类似内置的 Partial、Readonly）

#### （7）索引类型（Index Types）

索引类型用于处理对象的属性和属性值类型，结合`keyof`和`T[K]`操作符使用。

**关键操作符**：



*   `keyof T`：获取 T 的所有属性键组成的联合类型

*   `T[K]`：获取 T 中属性 K 的类型（索引访问类型）

**示例**：



```
interface User {

&#x20; id: number;

&#x20; name: string;

&#x20; age: number;

}

// "id" | "name" | "age"

type UserKeys = keyof User;

// number（User\["id"]的类型）

type IdType = User\["id"];

// string | number（User\["name" | "age"]的类型）

type NameOrAgeType = User\["name" | "age"];

// 泛型函数：安全获取对象属性

function getProperty\<T, K extends keyof T>(obj: T, key: K): T\[K] {

&#x20; return obj\[key];

}

const user: User = { id: 1, name: "张三", age: 25 };

const userName = getProperty(user, "name"); // string类型

const userId = getProperty(user, "id"); // number类型

// const invalid = getProperty(user, "invalid"); // 错误：不存在的属性
```

**应用场景**：



*   实现类型安全的属性访问函数

*   获取对象属性的键或值的类型

*   处理动态属性名的场景

#### （8）类型守卫（Type Guards）

类型守卫是一种运行时检查，用于缩小类型范围（类型收窄），确保在特定分支中变量具有特定类型。

**常见类型守卫**：



1.  `typeof`类型守卫：检查基本类型



```
function print(value: string | number) {

&#x20; if (typeof value === "string") {

&#x20;   console.log(value.toUpperCase()); // 类型收窄为string

&#x20; } else {

&#x20;   console.log(value.toFixed(2)); // 类型收窄为number

&#x20; }

}
```



1.  `instanceof`类型守卫：检查对象实例



```
class Dog {

&#x20; bark() { console.log("Woof!"); }

}

class Cat {

&#x20; meow() { console.log("Meow!"); }

}

function makeSound(animal: Dog | Cat) {

&#x20; if (animal instanceof Dog) {

&#x20;   animal.bark(); // 类型收窄为Dog

&#x20; } else {

&#x20;   animal.meow(); // 类型收窄为Cat

&#x20; }

}
```



1.  自定义类型守卫：使用`is`关键字



```
interface Bird {

&#x20; fly: () => void;

}

interface Fish {

&#x20; swim: () => void;

}

// 自定义类型守卫：判断是否为Bird

function isBird(animal: Bird | Fish): animal is Bird {

&#x20; return "fly" in animal;

}

function move(animal: Bird | Fish) {

&#x20; if (isBird(animal)) {

&#x20;   animal.fly(); // 类型收窄为Bird

&#x20; } else {

&#x20;   animal.swim(); // 类型收窄为Fish

&#x20; }

}
```

**应用场景**：



*   在联合类型中安全访问特定类型的属性或方法

*   减少类型断言的使用，提高代码安全性

*   处理复杂的类型区分逻辑

### 3. 高级类型的组合使用

在实际开发中，高级类型通常会组合使用，解决更复杂的类型问题。

**示例：实现一个高级的 API 响应处理类型**



```
// 基础API响应类型

type ApiResponse\<T> = {

&#x20; code: number;

&#x20; message: string;

&#x20; data: T;

};

// 成功响应（code=200）

type SuccessResponse\<T> = ApiResponse\<T> & { code: 200 };

// 错误响应（code!==200）

type ErrorResponse = ApiResponse\<never> & { code: Exclude\<number, 200> };

// API响应联合类型

type Response\<T> = SuccessResponse\<T> | ErrorResponse;

// 提取响应数据类型的条件类型

type ExtractData\</doubaocanvas>
```

