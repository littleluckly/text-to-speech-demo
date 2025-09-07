# 在 React 中如何通过组合模式设计可嵌套的菜单组件？请对比 Props 与 Context 的实现差异。

## meta 元数据



```
{

&#x20; "id": "a7b8c9d0-e1f2-3456-ghij-789abcdef012",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["react", "设计模式"]

}
```

## 答案 1：核心简洁的口语化回答

・用组合模式设计嵌套菜单时，需定义统一接口的菜单组件（如 Menu、MenuItem、SubMenu），允许互相嵌套

・父组件通过 children 属性接收子菜单，形成树状结构，统一处理点击、选中状态

・Props 实现：通过逐层传递状态（如 activeKey、onSelect）控制子组件，层级深时代码冗余

・Context 实现：用 Context.Provider 共享状态，子组件通过 useContext 获取，避免 Props 透传

・差异：Props 适合层级浅的菜单，逻辑直观；Context 适合深层嵌套，减少代码冗余但增加复杂度

## 答案 2：口语化扩展回答

在 React 中用组合模式设计嵌套菜单，核心是让不同层级的菜单组件能像搭积木一样组合。比如设计 Menu（容器）、MenuItem（菜单项）、SubMenu（子菜单容器）这几个组件，它们都能互相嵌套 ——SubMenu 里可以放 MenuItem，也能再放 SubMenu，形成多级菜单。父组件通过 children 属性接收子元素，这样就能灵活组合出复杂结构。

用 Props 实现时，父菜单的状态（比如当前选中项、点击事件）要一层一层往下传。比如 Menu 的 activeKey 要传给 SubMenu，SubMenu 再传给它的 MenuItem，层级多了就会很繁琐，每次新增层级都要手动传递。

而用 Context 的话，只需在最外层 Menu 提供一个 Context.Provider，把共享状态放进去。不管子组件嵌套多深，只要通过 useContext 就能直接拿到状态，不用手动透传 Props。不过这种方式也有缺点，状态变更时所有消费 Context 的组件都会重新渲染，简单菜单用 Props 更直观，复杂深层菜单用 Context 更合适。

## 答案 3：技术深度解析

### 基于组合模式的嵌套菜单组件设计

组合模式要求**将对象组合成树状结构，并以统一方式处理单个对象和组合对象**。在 React 中，可通过以下组件结构实现嵌套菜单：

#### 1. 组件设计方案

核心组件包括：



*   `Menu`：最外层容器，管理全局状态（如选中项、模式）

*   `MenuItem`：叶子节点，代表可点击的菜单项

*   `SubMenu`：容器节点，可包含 MenuItem 或其他 SubMenu，支持展开 / 折叠



```
// 组合模式的菜单组件结构示例

\<Menu mode="vertical" defaultActiveKey="1">

&#x20; \<MenuItem key="1">首页\</MenuItem>

&#x20; \<SubMenu title="产品中心" key="2">

&#x20;   \<MenuItem key="2-1">产品列表\</MenuItem>

&#x20;   \<SubMenu title="详情" key="2-2">

&#x20;     \<MenuItem key="2-2-1">规格参数\</MenuItem>

&#x20;     \<MenuItem key="2-2-2">用户评价\</MenuItem>

&#x20;   \</SubMenu>

&#x20; \</SubMenu>

&#x20; \<MenuItem key="3">关于我们\</MenuItem>

\</Menu>
```

#### 2. 基础组件实现（框架代码）



```
// 类型定义（TS）

type MenuMode = 'horizontal' | 'vertical';

type MenuProps = {

&#x20; mode?: MenuMode;

&#x20; defaultActiveKey?: string;

&#x20; onSelect?: (key: string) => void;

&#x20; children: React.ReactNode;

};

type MenuItemProps = {

&#x20; key: string;

&#x20; children: React.ReactNode;

&#x20; onClick?: () => void;

};

type SubMenuProps = {

&#x20; key: string;

&#x20; title: string;

&#x20; children: React.ReactNode;

};

// 基础组件实现（无状态管理）

const Menu = ({ mode, children }: MenuProps) => (

&#x20; \<ul className={\`menu menu-\${mode}\`}>{children}\</ul>

);

const MenuItem = ({ key, children, onClick }: MenuItemProps) => (

&#x20; \<li key={key} className="menu-item" onClick={onClick}>

&#x20;   {children}

&#x20; \</li>

);

const SubMenu = ({ key, title, children }: SubMenuProps) => (

&#x20; \<li key={key} className="submenu">

&#x20;   \<div className="submenu-title">{title}\</div>

&#x20;   \<ul className="submenu-children">{children}\</ul>

&#x20; \</li>

);
```

### Props 实现方式

通过 Props 传递状态和回调，适合层级较浅的菜单结构。

#### 1. 实现代码



```
// Props版本Menu组件（带状态管理）

const PropsMenu = ({ mode, defaultActiveKey, onSelect, children }: MenuProps) => {

&#x20; const \[activeKey, setActiveKey] = useState(defaultActiveKey || '');

&#x20; // 处理选中逻辑

&#x20; const handleSelect = (key: string) => {

&#x20;   setActiveKey(key);

&#x20;   onSelect?.(key);

&#x20; };

&#x20; // 递归处理子元素，传递props

&#x20; const renderChildren = (children: React.ReactNode) => {

&#x20;   return React.Children.map(children, (child) => {

&#x20;     if (!React.isValidElement(child)) return child;

&#x20;     // 对MenuItem和SubMenu传递必要的props

&#x20;     if (child.type === PropsMenuItem || child.type === PropsSubMenu) {

&#x20;       return React.cloneElement(child, {

&#x20;         activeKey,

&#x20;         onSelect: handleSelect,

&#x20;         // 传递mode等其他必要属性

&#x20;         mode,

&#x20;       });

&#x20;     }

&#x20;     return child;

&#x20;   });

&#x20; };

&#x20; return (

&#x20;   \<ul className={\`menu menu-\${mode}\`}>

&#x20;     {renderChildren(children)}

&#x20;   \</ul>

&#x20; );

};

// Props版本MenuItem

const PropsMenuItem = ({ key, children, activeKey, onSelect }: MenuItemProps & { activeKey?: string; onSelect: (key: string) => void }) => {

&#x20; const isActive = activeKey === key;

&#x20; return (

&#x20;   \<li&#x20;

&#x20;     key={key}&#x20;

&#x20;     className={\`menu-item \${isActive ? 'active' : ''}\`}

&#x20;     onClick={() => onSelect(key)}

&#x20;   \>

&#x20;     {children}

&#x20;   \</li>

&#x20; );

};

// Props版本SubMenu（需继续传递props给子元素）

const PropsSubMenu = ({ key, title, children, activeKey, onSelect, mode }: SubMenuProps & { activeKey?: string; onSelect: (key: string) => void; mode: MenuMode }) => {

&#x20; const \[expanded, setExpanded] = useState(false);

&#x20; // 递归传递props给子元素

&#x20; const renderChildren = (children: React.ReactNode) => {

&#x20;   return React.Children.map(children, (child) => {

&#x20;     if (!React.isValidElement(child)) return child;

&#x20;     return React.cloneElement(child, {

&#x20;       activeKey,

&#x20;       onSelect,

&#x20;       mode,

&#x20;     });

&#x20;   });

&#x20; };

&#x20; return (

&#x20;   \<li key={key} className="submenu">

&#x20;     \<div&#x20;

&#x20;       className="submenu-title"

&#x20;       onClick={() => setExpanded(!expanded)}

&#x20;     \>

&#x20;       {title}

&#x20;       \<span className={\`arrow \${expanded ? 'expanded' : ''}\`} />

&#x20;     \</div>

&#x20;     {expanded && (

&#x20;       \<ul className="submenu-children">

&#x20;         {renderChildren(children)}

&#x20;       \</ul>

&#x20;     )}

&#x20;   \</li>

&#x20; );

};
```

#### 2. 核心特点



*   **显式传递**：所有状态（`activeKey`）和方法（`onSelect`）通过 Props 逐层传递

*   **递归处理**：`renderChildren`函数负责克隆子元素并注入 Props

*   **层级限制**：层级过深时（如 5 级以上菜单），会出现 "Props 透传地狱"

*   **性能优势**：状态变更时，仅接收 Props 的组件会重新渲染，避免不必要的更新

### Context 实现方式

通过 Context 共享状态，适合深层嵌套的复杂菜单。

#### 1. 实现代码



```
// 创建MenuContext

const MenuContext = React.createContext<{

&#x20; activeKey: string;

&#x20; onSelect: (key: string) => void;

&#x20; mode: MenuMode;

} | undefined>(undefined);

// Context版本Menu组件

const ContextMenu = ({ mode, defaultActiveKey, onSelect, children }: MenuProps) => {

&#x20; const \[activeKey, setActiveKey] = useState(defaultActiveKey || '');

&#x20; const handleSelect = (key: string) => {

&#x20;   setActiveKey(key);

&#x20;   onSelect?.(key);

&#x20; };

&#x20; // 提供Context值

&#x20; const value = {

&#x20;   activeKey,

&#x20;   onSelect: handleSelect,

&#x20;   mode: mode || 'horizontal',

&#x20; };

&#x20; return (

&#x20;   \<MenuContext.Provider value={value}>

&#x20;     \<ul className={\`menu menu-\${mode}\`}>{children}\</ul>

&#x20;   \</MenuContext.Provider>

&#x20; );

};

// Context版本MenuItem

const ContextMenuItem = ({ key, children }: MenuItemProps) => {

&#x20; // 直接从Context获取状态

&#x20; const context = useContext(MenuContext);

&#x20; if (!context) {

&#x20;   throw new Error('MenuItem must be used within a Menu');

&#x20; }

&#x20; const { activeKey, onSelect } = context;

&#x20; const isActive = activeKey === key;

&#x20; return (

&#x20;   \<li&#x20;

&#x20;     key={key}&#x20;

&#x20;     className={\`menu-item \${isActive ? 'active' : ''}\`}

&#x20;     onClick={() => onSelect(key)}

&#x20;   \>

&#x20;     {children}

&#x20;   \</li>

&#x20; );

};

// Context版本SubMenu

const ContextSubMenu = ({ key, title, children }: SubMenuProps) => {

&#x20; const context = useContext(MenuContext);

&#x20; if (!context) {

&#x20;   throw new Error('SubMenu must be used within a Menu');

&#x20; }

&#x20; const \[expanded, setExpanded] = useState(false);

&#x20; const { mode } = context;

&#x20; return (

&#x20;   \<li key={key} className="submenu">

&#x20;     \<div&#x20;

&#x20;       className="submenu-title"

&#x20;       onClick={() => setExpanded(!expanded)}

&#x20;     \>

&#x20;       {title}

&#x20;       \<span className={\`arrow \${expanded ? 'expanded' : ''}\`} />

&#x20;     \</div>

&#x20;     {expanded && (

&#x20;       \<ul className="submenu-children">

&#x20;         {children} {/\* 子元素可直接消费Context，无需手动传递 \*/}

&#x20;       \</ul>

&#x20;     )}

&#x20;   \</li>

&#x20; );

};
```

#### 2. 核心特点



*   **隐式共享**：状态通过`MenuContext.Provider`共享，子组件无需显式接收 Props

*   **深层访问**：无论嵌套多少层，`useContext`均可直接获取状态

*   **简化代码**：避免了`renderChildren`之类的递归传递逻辑

*   **性能考量**：Context 值变化时，所有消费组件会重新渲染（可通过拆分 Context 优化）

### Props 与 Context 实现的核心差异



| 维度    | Props 实现          | Context 实现        |
| ----- | ----------------- | ----------------- |
| 传递方式  | 显式逐层传递            | 隐式跨层级共享           |
| 代码复杂度 | 层级深时冗余（需递归传递）     | 代码简洁（无需手动透传）      |
| 学习成本  | 低（符合 React 基础理念）  | 中（需理解 Context 机制） |
| 性能表现  | 精准更新（仅传递链上组件重渲染）  | 可能过度更新（所有消费者重渲染）  |
| 调试难度  | 易（Props 传递链清晰可追踪） | 难（状态来源不直观）        |
| 适用场景  | 层级浅的菜单（≤3 级）      | 深层嵌套菜单（≥4 级）      |
| 灵活性   | 高（可针对性修改中间层传递）    | 低（共享状态统一变更）       |

### 优化建议与最佳实践



1.  **混合模式**：

*   外层用 Context 共享核心状态（`activeKey`、`mode`）

*   局部交互用 Props 传递（如 SubMenu 的`expanded`状态）

1.  **Context 拆分**：

    将频繁变化的状态（如`activeKey`）与稳定状态（如`mode`）拆分到不同 Context，减少重渲染：



```
const MenuStaticContext = createContext<{ mode: MenuMode }>({ mode: 'horizontal' });

const MenuDynamicContext = createContext<{ activeKey: string; onSelect: () => void }>(...);
```



1.  **性能优化**：

*   Props 传递时使用`React.memo`缓存组件

*   Context 消费时结合`useMemo`缓存计算结果

1.  **框架借鉴**：

*   Ant Design 的 Menu 组件采用 Context 实现深层嵌套

*   Material-UI 的 Menu 组件对简单场景使用 Props，复杂场景使用 Context

### 总结

在 React 中用组合模式设计嵌套菜单，核心是通过`Menu`、`MenuItem`、`SubMenu`的层级组合形成树状结构。Props 实现适合简单场景，逻辑直观但层级深时冗余；Context 实现适合复杂深层菜单，简化代码但需注意性能优化。

实际开发中，应根据菜单层级深度、状态变更频率选择合适的实现方式，或采用混合模式平衡开发效率与性能。理解两种方式的差异，有助于设计出既灵活又高效的组件系统。

