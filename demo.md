## 简介

这是第一段内容。

## React 声明周期

这是 React 生命周期的介绍。

## MOUNTING

这是挂载阶段的详细说明。

componentWillMount 会在 render 之前调用（在此调用 setState，是不会触发 re-render 的，而是会进行 state 的合并。因此此时的 this.state 不是最新的，在 render 中才可以获取更新后的 this.state。）
componentDidMount 会在 render 之后调用

---

这是第二个音频，通过分割线分割的方式
