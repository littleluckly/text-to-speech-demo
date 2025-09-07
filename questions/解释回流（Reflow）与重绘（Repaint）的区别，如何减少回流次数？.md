# 解释回流（Reflow）与重绘（Repaint）的区别，如何减少回流次数？

## meta 元数据



```
{

&#x20; "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ad",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["浏览器", "性能优化"]

}
```

## 答案 1：核心简洁的口语化回答

・回流是元素几何属性（位置、尺寸）改变时，浏览器重新计算布局的过程；重绘是元素样式（颜色、阴影）改变但几何属性不变时，重新绘制元素的过程。

・回流一定会引发重绘，重绘不一定引发回流。

・减少回流可通过批量操作 DOM、使用文档片段、避免频繁读取布局属性、利用 CSS 触发合成层等方式。

## 答案 2：口语化扩展回答

回流和重绘都是浏览器渲染过程中的步骤，但影响范围和代价不同。回流涉及元素的位置、大小等几何信息的改变，比如调整元素的宽高、改变窗口尺寸，这时候浏览器需要重新计算整个页面的布局，过程比较耗时。而重绘只是元素的视觉样式变化，像修改颜色、背景图，元素的位置和大小没变，不需要重新计算布局，所以代价相对小一些。

不过要注意，回流发生时必然会导致重绘，因为布局变了元素的显示肯定会变；但重绘时却不一定会引发回流，比如只是把文字颜色改成红色，就不会触发回流。

在实际开发中，频繁的回流会让页面变卡，所以要想办法减少。比如要修改多个 DOM 样式时，先把元素隐藏起来再操作，或者用文档片段一次性插入；还有就是别频繁读取 offsetTop 这类会触发回流的属性，能批量读就别分开读；另外，用 transform 做动画比直接改 top、left 要好，因为它不会触发回流。

## 答案 3：技术深度解析

### 1. 回流与重绘的本质区别

#### 1.1 回流（Reflow）

回流是浏览器在渲染过程中，由于元素的几何属性发生改变，需要重新计算元素的位置和尺寸，并更新渲染树中相关节点的布局信息的过程。这一过程会从根节点开始，递归计算所有受影响元素的几何属性，最终生成新的布局。

#### 1.2 重绘（Repaint）

重绘是当元素的视觉样式发生改变（如颜色、背景、边框样式等），但几何属性未变时，浏览器重新绘制元素的过程。此时不需要重新计算布局，只需根据新的样式信息，在原有位置上重新绘制元素。

#### 1.3 核心差异对比



| 对比维度 | 回流（Reflow）          | 重绘（Repaint）     |
| ---- | ------------------- | --------------- |
| 触发原因 | 元素几何属性改变（位置、尺寸、布局等） | 元素视觉样式改变但几何属性不变 |
| 计算成本 | 高（需重新计算布局）          | 低（无需重新计算布局）     |
| 关联性  | 回流一定会引发重绘           | 重绘不一定引发回流       |
| 影响范围 | 可能影响多个元素（甚至整个页面）    | 通常只影响单个元素       |

### 2. 常见触发回流的操作

以下操作会改变元素的几何属性，从而触发回流：



*   调整元素的宽高（width、height）、边距（margin）、内边距（padding）

*   改变元素的位置（top、left、right、bottom、float、position 等）

*   增减 DOM 元素（添加、删除节点）

*   改变窗口大小

*   改变字体大小或行高

*   激活 CSS 伪类（如:hover）

*   计算 offsetTop、offsetLeft、offsetWidth、offsetHeight 等布局属性（浏览器为获取准确值会强制刷新队列，触发回流）

### 3. 减少回流次数的技术方案

#### 3.1 批量操作 DOM

避免频繁地对 DOM 进行单个修改，而是先将 DOM 从文档流中移除，批量修改后再重新插入。



```
// 不佳方式：多次修改DOM，触发多次回流

const list = document.getElementById('list');

for (let i = 0; i < 10; i++) {

&#x20; const item = document.createElement('li');

&#x20; item.textContent = \`Item \${i}\`;

&#x20; list.appendChild(item); // 每次添加都会触发回流

}

// 优化方式：使用文档片段批量操作，只触发一次回流

const list = document.getElementById('list');

const fragment = document.createDocumentFragment(); // 文档片段不在DOM树中，操作不会触发回流

for (let i = 0; i < 10; i++) {

&#x20; const item = document.createElement('li');

&#x20; item.textContent = \`Item \${i}\`;

&#x20; fragment.appendChild(item);

}

list.appendChild(fragment); // 仅此时触发一次回流
```

#### 3.2 缓存布局属性读取

避免频繁读取会触发回流的布局属性，可先一次性读取并缓存，再进行后续操作。



```
// 不佳方式：多次读取布局属性，触发多次回流

const box = document.getElementById('box');

box.style.width = '100px';

const width = box.offsetWidth; // 触发回流

box.style.height = width + 'px'; // 再次触发回流

box.style.marginTop = (width / 2) + 'px'; // 又一次触发回流

// 优化方式：缓存布局属性，减少回流

const box = document.getElementById('box');

box.style.width = '100px';

const width = box.offsetWidth; // 触发一次回流

// 后续使用缓存的值，不再次读取布局属性

box.style.height = width + 'px';

box.style.marginTop = (width / 2) + 'px'; // 仅在修改样式时可能触发一次回流（若多个样式同时修改，浏览器可能合并）
```

#### 3.3 利用 CSS 触发合成层

使用 CSS 的`transform`、`opacity`等属性进行动画或样式修改，这些属性只会触发合成阶段，而不会引发回流或重绘。



```
/\* 不佳方式：修改top属性会触发回流 \*/

.box {

&#x20; position: absolute;

&#x20; top: 0;

&#x20; transition: top 0.3s;

}

.box:hover {

&#x20; top: 100px; /\* 触发回流 \*/

}

/\* 优化方式：使用transform，仅触发合成，不引发回流 \*/

.box {

&#x20; position: absolute;

&#x20; transform: translateY(0);

&#x20; transition: transform 0.3s;

}

.box:hover {

&#x20; transform: translateY(100px); /\* 仅触发合成，性能更优 \*/

}
```

#### 3.4 隐藏元素后进行操作

先将元素设置为`display: none`，此时元素脱离文档流，操作不会触发回流，完成后再恢复显示。



```
const box = document.getElementById('box');

box.style.display = 'none'; // 元素隐藏，脱离文档流

// 进行多次DOM修改，不会触发回流

box.style.width = '200px';

box.style.height = '300px';

box.style.backgroundColor = 'red';

box.style.display = 'block'; // 恢复显示，仅触发一次回流
```

#### 3.5 使用虚拟 DOM

虚拟 DOM 通过在内存中构建虚拟的 DOM 树，先对比前后的差异，再将差异批量更新到真实 DOM，从而减少真实 DOM 的操作次数，降低回流频率。这也是 React、Vue 等框架优化性能的重要手段之一。

### 4. 总结

回流和重绘是影响浏览器渲染性能的关键因素，回流的计算成本远高于重绘。在开发中，应尽量减少回流次数，可通过批量操作 DOM、缓存布局属性、利用 CSS 合成层等方式优化。合理运用这些技术手段，能显著提升页面的流畅度和响应速度，改善用户体验。

