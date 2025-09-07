# 说说 React diff 的原理是什么？

## meta 元数据



```
{

&#x20; "id": "c1d2e3f4-g5h6-7890-ijkl-1234567890mn",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react"]

}
```

## 答案 1：核心简洁的口语化回答

・React diff 采用分层比较策略，只比较同一层级的节点，不跨层级比较，降低复杂度

・节点类型不同时，直接销毁旧节点并创建新节点，不深入比较子节点

・节点类型相同时，通过 key 属性判断是否为同一节点，相同 key 则复用节点并更新属性

・列表 diff 通过 key 匹配，减少节点的增删改操作，优先移动已有节点而非重新创建

・整体以高效复用节点为目标，牺牲部分最优解换取性能提升，时间复杂度接近 O (n)

## 答案 2：口语化扩展回答

React diff 的核心思路是通过高效的比对算法，找出前后虚拟 DOM 的差异，再把这些差异更新到真实 DOM 上。它和传统的 diff 算法不一样，没有采用那种层层递归对比的方式，而是做了一些策略上的优化。

首先它是分层比较的，就是只看同一层级的节点，比如 div 下的子节点只和另一个 div 下的子节点比，不会去跨层级找节点比较，这样一下子就把复杂度降下来了。然后如果两个节点的类型不一样，比如一个是 div，一个是 p，那 React 就会直接把旧的 div 删掉，再新建一个 p，不会再去比较它们的子节点了，这样也省了不少事。

对于同一类型的节点，比如都是 div，就会比较它们的属性，更新变化的属性。如果是列表里的节点，就全靠 key 来识别了，有了 key，React 就知道哪个节点是新增的，哪个是删掉的，哪个是移动位置的，这样就能最大限度地复用已经存在的节点，不用重新创建，这对性能提升挺明显的。

不过这种策略也不是完美的，有时候为了效率会牺牲一些最优解，但整体来说，在实际开发中表现很好，能快速找出差异并更新 DOM。

## 答案 3：技术深度解析

### 一、React diff 的设计背景

React diff 是虚拟 DOM（Virtual DOM）比对的核心算法，其设计目标是**在保证性能可接受的前提下，快速找出前后两次虚拟 DOM 树的差异**，并将差异高效更新到真实 DOM。

传统的树形结构 diff 算法时间复杂度为 O (n³)（n 为节点数量），无法满足前端高频更新场景。React diff 通过三大策略将时间复杂度优化至 O (n)，使其能在实际项目中高效运行。

### 二、核心比对策略

#### 1. 分层比对（Tree Diff）

**原理**：只对虚拟 DOM 树中同一层级的节点进行比对，忽略跨层级的节点移动。



```
// 简化的层级比对逻辑

function diffTrees(oldTree, newTree) {

&#x20; // 只比较根节点层级

&#x20; if (oldTree.tag !== newTree.tag) {

&#x20;   // 根节点类型不同，直接替换整棵树

&#x20;   return { type: 'REPLACE', newNode: newTree };

&#x20; }

&#x20;&#x20;

&#x20; // 递归比对子节点（同一层级）

&#x20; const patch = diffChildren(oldTree.children, newTree.children);

&#x20;&#x20;

&#x20; return patch.length ? { type: 'PATCH', patches: patch } : null;

}
```

**特点**：



*   若节点跨层级移动（如从父节点移动到祖父节点），React 会先删除旧节点，再在新位置创建新节点，而非直接移动

*   这种策略基于前端开发中 "跨层级节点移动场景较少" 的经验假设

#### 2. 同类型节点比对（Component Diff）

**原理**：对于同一层级的节点，先通过节点类型（tagName 或组件类型）进行筛选。



```
function diffComponents(oldNode, newNode) {

&#x20; // 类型不同，直接替换

&#x20; if (oldNode.type !== newNode.type) {

&#x20;   return { type: 'REPLACE', newNode: newNode };

&#x20; }

&#x20;&#x20;

&#x20; // 类型相同，进一步比对属性和子节点

&#x20; const propsDiff = diffProps(oldNode.props, newNode.props);

&#x20; const childrenDiff = diffChildren(oldNode.children, newNode.children);

&#x20;&#x20;

&#x20; const patches = \[];

&#x20; if (propsDiff) patches.push(propsDiff);

&#x20; if (childrenDiff) patches.push(childrenDiff);

&#x20;&#x20;

&#x20; return patches.length ? { type: 'PATCH', patches } : null;

}
```

**处理逻辑**：



*   类型不同：直接销毁旧节点（触发 componentWillUnmount），创建新节点（触发 componentWillMount）

*   类型相同：


    *   比对并更新属性（如 className、style 等）

    *   递归比对子节点

#### 3. 列表节点比对（Element Diff）

**原理**：对于同一类型的列表节点，通过`key`属性建立节点的唯一标识，实现高效复用。

**核心步骤**：



1.  先遍历新列表，通过 key 查找旧列表中是否存在可复用节点

2.  对找到的可复用节点，计算其位置偏移量，判断是否需要移动

3.  处理新增节点和待删除节点



```
function diffList(oldList, newList) {

&#x20; const patches = \[];

&#x20; const oldKeyToIndex = createKeyToIndexMap(oldList); // { key: index }

&#x20;&#x20;

&#x20; // 第一遍：处理可复用节点和新增节点

&#x20; newList.forEach((newNode, newIndex) => {

&#x20;   const oldIndex = oldKeyToIndex.get(newNode.key);

&#x20;  &#x20;

&#x20;   if (oldIndex === undefined) {

&#x20;     // 新增节点

&#x20;     patches.push({

&#x20;       type: 'INSERT',

&#x20;       index: newIndex,

&#x20;       node: newNode

&#x20;     });

&#x20;   } else {

&#x20;     // 复用节点，检查是否需要移动

&#x20;     const oldNode = oldList\[oldIndex];

&#x20;     const nodeDiff = diffNodes(oldNode, newNode);

&#x20;     if (nodeDiff) {

&#x20;       patches.push({

&#x20;         type: 'PATCH',

&#x20;         index: newIndex,

&#x20;         patch: nodeDiff

&#x20;       });

&#x20;     }

&#x20;     // 记录位置信息用于后续移动判断

&#x20;     newNode.\_oldIndex = oldIndex;

&#x20;   }

&#x20; });

&#x20;&#x20;

&#x20; // 第二遍：处理需要删除的节点

&#x20; oldList.forEach((oldNode, oldIndex) => {

&#x20;   const isExistInNew = newList.some(

&#x20;     newNode => newNode.key === oldNode.key

&#x20;   );

&#x20;   if (!isExistInNew) {

&#x20;     patches.push({

&#x20;       type: 'REMOVE',

&#x20;       index: oldIndex

&#x20;     });

&#x20;   }

&#x20; });

&#x20;&#x20;

&#x20; // 第三遍：处理节点移动

&#x20; patches.push(...calculateMovements(newList));

&#x20;&#x20;

&#x20; return patches;

}
```

**key 的重要性**：



*   无 key 时，React 默认使用索引作为 key，在列表增删时会导致大量节点复用错误

*   稳定唯一的 key（如数据 ID）可确保节点正确复用，减少 DOM 操作

### 三、React diff 的局限性与优化

#### 1. 局限性



*   跨层级移动节点会导致额外的删除 / 创建操作

*   列表逆序排列时，可能产生较多移动操作（O (n) 复杂度）

*   对相同类型但结构差异大的节点，仍会深入比对子节点

#### 2. 实际开发中的优化建议



*   避免频繁跨层级操作 DOM，尽量通过 CSS 定位实现视觉上的层级变化

*   为列表项提供稳定唯一的 key（避免使用索引）

*   对于结构差异大的组件，可通过改变 key 强制重新渲染（如`key={JSON.stringify(data)}`）

*   结合`React.memo`、`useMemo`等 API 减少不必要的 diff 过程

### 四、React 18 中的 diff 优化

React 18 通过**并发渲染（Concurrent Rendering）** 进一步优化了 diff 过程：



*   支持 diff 过程的中断与恢复

*   优先处理用户交互相关的更新，延迟处理非紧急更新

*   通过`scheduler`包实现优先级调度，使 diff 过程更符合用户体验需求

### 总结

React diff 通过 "分层比对、类型筛选、key 标识" 三大策略，在时间复杂度和实际性能之间取得了平衡。其设计思想并非追求理论上的最优解，而是基于前端开发场景的特点，实现了工程上的高效方案。理解 React diff 原理，有助于写出更符合 React 性能优化理念的代码，避免常见的性能陷阱。

