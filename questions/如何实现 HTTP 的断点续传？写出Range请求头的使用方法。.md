# 如何实现 HTTP 的断点续传？写出 Range 请求头的使用方法。

## meta 元数据



```
{

&#x20; "id": "d3e4f5a6-b7c8-9012-dcba-34567890abcd",

&#x20; "type": "answer",

&#x20; "difficulty": "medium",

&#x20; "tags": \["http"]

}
```

## 答案 1：核心简洁的口语化回答

・实现 HTTP 断点续传需客户端用 Range 请求头指定需获取的字节范围，服务器返回 206 状态码及对应数据。

・Range 语法：`Range: bytes=start-end`，start 为起始字节（含），end 可选（缺省为文件末尾）。

・示例：`bytes=1000-`表示从 1000 字节开始到末尾；`bytes=500-1999`表示 500 到 1999 字节。

・服务器响应含 Content-Range 头，如`bytes 1000-2999/3000`，标识返回范围及总大小。

・需处理 416 状态码（范围无效），客户端记录已下载位置以便续传。

## 答案 2：口语化扩展回答

HTTP 断点续传的核心是让客户端和服务器配合，只传输没下载完的部分。具体来说，当文件下载中断后，客户端要记住已经下载到哪个字节了，下次请求时就用 Range 头告诉服务器从这个位置开始传。

Range 头的用法不难，格式是`bytes=start-end`，比如之前下到了 1000 字节，就写`bytes=1000-`，服务器收到后，就会从 1000 字节开始返回剩下的内容，同时响应状态码是 206，还会在 Content-Range 头里说明返回的范围和文件总大小，方便客户端拼接。

要是客户端指定的范围不对，比如超过了文件大小，服务器会返回 416 错误，这时候客户端可能就得重新下载了。另外，服务器得支持范围请求，会通过 Accept-Ranges: bytes 头告诉客户端可以用断点续传，不然就只能从头下了。实际开发中，客户端得做好记录已下载位置的工作，比如存在本地存储里，这样断网后再连就能接着传，不用浪费流量。

## 答案 3：技术深度解析

### 一、HTTP 断点续传的实现原理

HTTP 断点续传基于 HTTP/1.1 引入的范围请求（Range Requests）机制，允许客户端仅请求资源的部分字节，从而实现中断后继续传输。其核心流程如下：



1.  **客户端记录已下载位置**：当下载中断时，客户端保存已接收的字节数（如`10240`字节）。

2.  **客户端发送范围请求**：恢复下载时，通过`Range`请求头告知服务器需获取的字节范围（如从`10240`字节开始）。

3.  **服务器验证并响应**：服务器若支持范围请求（通过`Accept-Ranges: bytes`声明），则返回`206 Partial Content`状态码，响应体包含请求范围内的数据，并通过`Content-Range`头说明返回范围和总大小。

4.  **客户端拼接数据**：客户端将新接收的部分数据与已下载部分拼接，直至完成整个文件。

### 二、Range 请求头的使用方法

#### 1. 基本语法



```
Range: bytes=start-end
```



*   `start`：起始字节位置（必需，从 0 开始计数，包含该字节）。

*   `end`：结束字节位置（可选，包含该字节；若省略，默认到文件末尾）。

#### 2. 常见使用场景及示例



| 场景          | Range 请求头示例                     | 说明                          |
| ----------- | ------------------------------- | --------------------------- |
| 从指定位置到末尾    | `Range: bytes=10240-`           | 请求从 10240 字节开始至文件末尾的所有数据    |
| 固定范围的字节     | `Range: bytes=5120-10239`       | 请求 5120-10239 字节（共 5120 字节） |
| 多段不连续范围（少见） | `Range: bytes=0-499, 1000-1499` | 请求两段数据，服务器返回多部分响应           |

#### 3. 服务器响应格式



*   **成功响应（206 Partial Content）**：



```
HTTP/1.1 206 Partial Content

Accept-Ranges: bytes

Content-Range: bytes 10240-20479/30720  # 返回范围：10240-20479字节，总大小30720字节

Content-Length: 10240  # 本次返回的数据大小（20479-10240+1=10240）

Content-Type: application/octet-stream
```



*   **范围无效（416 Requested Range Not Satisfiable）**：



```
HTTP/1.1 416 Requested Range Not Satisfiable

Content-Range: bytes \*/30720  # 总大小30720字节，无有效范围
```

### 三、完整实现代码示例（客户端 + 服务器）

#### 1. 客户端实现（JavaScript，模拟断点续传）



```
class ResumeDownloader {

&#x20; constructor(fileUrl, savePath) {

&#x20;   this.fileUrl = fileUrl; // 下载地址

&#x20;   this.savePath = savePath; // 本地保存路径

&#x20;   this.downloadedSize = 0; // 已下载字节数（从本地存储读取）

&#x20;   this.chunkSize = 1024 \* 1024; // 每次请求的块大小（1MB）

&#x20;   this.xhr = null; // XMLHttpRequest实例

&#x20; }

&#x20; // 初始化：从本地读取已下载进度

&#x20; async init() {

&#x20;   try {

&#x20;     // 实际项目中可从IndexedDB或文件系统读取

&#x20;     const savedProgress = localStorage.getItem(\`progress\_\${this.fileUrl}\`);

&#x20;     this.downloadedSize = savedProgress ? parseInt(savedProgress, 10) : 0;

&#x20;     console.log(\`已下载\${this.downloadedSize}字节，准备续传\`);

&#x20;   } catch (e) {

&#x20;     console.error("初始化进度失败：", e);

&#x20;   }

&#x20; }

&#x20; // 开始/恢复下载

&#x20; start() {

&#x20;   this.xhr = new XMLHttpRequest();

&#x20;   this.xhr.open("GET", this.fileUrl, true);

&#x20;   // 设置Range请求头：从已下载位置开始

&#x20;   this.xhr.setRequestHeader("Range", \`bytes=\${this.downloadedSize}-\`);

&#x20;   // 监听进度事件（可选，用于显示下载进度）

&#x20;   this.xhr.addEventListener("progress", (e) => {

&#x20;     if (e.lengthComputable) {

&#x20;       const totalReceived = this.downloadedSize + e.loaded;

&#x20;       const totalSize = this.downloadedSize + e.total;

&#x20;       const progress = Math.round((totalReceived / totalSize) \* 100);

&#x20;       console.log(\`下载进度：\${progress}%\`);

&#x20;     }

&#x20;   });

&#x20;   // 下载成功（206或200）

&#x20;   this.xhr.addEventListener("load", async (e) => {

&#x20;     if (this.xhr.status === 206 || this.xhr.status === 200) {

&#x20;       // 200表示服务器不支持范围请求，需完整下载

&#x20;       const isFullDownload = this.xhr.status === 200;

&#x20;       if (isFullDownload) {

&#x20;         this.downloadedSize = 0; // 重置进度，视为全新下载

&#x20;       }

&#x20;       // 获取响应数据（Blob类型）

&#x20;       const blob = await this.xhr.response;

&#x20;       // 拼接数据（实际项目中写入文件系统）

&#x20;       await this.appendToFile(blob);

&#x20;       // 更新已下载大小

&#x20;       const contentRange = this.xhr.getResponseHeader("Content-Range");

&#x20;       if (contentRange) {

&#x20;         // 解析Content-Range：bytes 10240-20479/30720

&#x20;         const totalSize = parseInt(contentRange.split("/")\[1], 10);

&#x20;         this.downloadedSize = totalSize;

&#x20;         localStorage.setItem(\`progress\_\${this.fileUrl}\`, this.downloadedSize);

&#x20;         console.log("下载完成");

&#x20;       }

&#x20;     } else if (this.xhr.status === 416) {

&#x20;       // 范围无效，说明已下载完整文件

&#x20;       console.log("文件已完整下载");

&#x20;     }

&#x20;   });

&#x20;   // 下载中断（如网络错误）

&#x20;   this.xhr.addEventListener("abort", () => {

&#x20;     console.log("下载中断，已保存进度");

&#x20;   });

&#x20;   // 发送请求，指定响应类型为Blob

&#x20;   this.xhr.responseType = "blob";

&#x20;   this.xhr.send();

&#x20; }

&#x20; // 暂停下载

&#x20; pause() {

&#x20;   if (this.xhr) {

&#x20;     this.xhr.abort();

&#x20;   }

&#x20; }

&#x20; // 将新数据追加到本地文件（模拟实现）

&#x20; async appendToFile(blob) {

&#x20;   // 实际项目中使用File System Access API或后端存储

&#x20;   console.log(\`追加\${blob.size}字节到\${this.savePath}\`);

&#x20;   // 示例：将Blob转换为ArrayBuffer，模拟写入文件

&#x20;   const arrayBuffer = await blob.arrayBuffer();

&#x20;   // 此处省略实际写入逻辑...

&#x20; }

}

// 使用示例

(async () => {

&#x20; const downloader = new ResumeDownloader(

&#x20;   "https://example.com/large-file.zip",

&#x20;   "/local/large-file.zip"

&#x20; );

&#x20; await downloader.init();

&#x20; downloader.start();

&#x20; // 模拟3秒后暂停（测试断点）

&#x20; setTimeout(() => {

&#x20;   downloader.pause();

&#x20;   // 5秒后恢复下载

&#x20;   setTimeout(() => {

&#x20;     downloader.start();

&#x20;   }, 5000);

&#x20; }, 3000);

})();
```

#### 2. 服务器实现（Node.js/Express，支持范围请求）



```
const express = require("express");

const fs = require("fs").promises;

const fsConstants = require("fs").constants;

const path = require("path");

const app = express();

const PORT = 3000;

const FILE\_PATH = path.join(\_\_dirname, "large-file.zip"); // 待下载的大文件

// 处理下载请求

app.get("/large-file.zip", async (req, res) => {

&#x20; try {

&#x20;   // 检查文件是否存在

&#x20;   await fs.access(FILE\_PATH, fsConstants.F\_OK);

&#x20;   // 获取文件信息（大小）

&#x20;   const stats = await fs.stat(FILE\_PATH);

&#x20;   const fileSize = stats.size;

&#x20;   // 声明支持范围请求

&#x20;   res.setHeader("Accept-Ranges", "bytes");

&#x20;   // 处理Range请求头

&#x20;   const range = req.headers.range;

&#x20;   if (range) {

&#x20;     // 解析Range：bytes=10240-

&#x20;     const parts = range.replace(/bytes=/, "").split("-");

&#x20;     const start = parseInt(parts\[0], 10);

&#x20;     const end = parts\[1] ? parseInt(parts\[1], 10) : fileSize - 1;

&#x20;     // 验证范围有效性

&#x20;     if (start >= fileSize || end >= fileSize || start > end) {

&#x20;       res.statusCode = 416;

&#x20;       res.setHeader("Content-Range", \`bytes \*/\${fileSize}\`);

&#x20;       return res.end();

&#x20;     }

&#x20;     // 设置响应头

&#x20;     res.statusCode = 206; // 部分内容

&#x20;     res.setHeader(

&#x20;       "Content-Range",

&#x20;       \`bytes \${start}-\${end}/\${fileSize}\`

&#x20;     );

&#x20;     res.setHeader("Content-Length", end - start + 1);

&#x20;     res.setHeader("Content-Type", "application/octet-stream");

&#x20;     // 创建文件读取流，从start到end

&#x20;     const fileStream = fs.createReadStream(FILE\_PATH, { start, end });

&#x20;     fileStream.pipe(res);

&#x20;   } else {

&#x20;     // 无Range头，返回完整文件

&#x20;     res.setHeader("Content-Length", fileSize);

&#x20;     res.setHeader("Content-Type", "application/octet-stream");

&#x20;     const fileStream = fs.createReadStream(FILE\_PATH);

&#x20;     fileStream.pipe(res);

&#x20;   }

&#x20; } catch (e) {

&#x20;   if (e.code === "ENOENT") {

&#x20;     res.status(404).send("文件不存在");

&#x20;   } else {

&#x20;     res.status(500).send("服务器错误");

&#x20;   }

&#x20; }

});

app.listen(PORT, () => {

&#x20; console.log(\`服务器运行在http://localhost:\${PORT}\`);

});
```

### 四、关键注意事项



1.  **服务器支持验证**：客户端发起范围请求前，可先发送`HEAD`请求检查服务器是否返回`Accept-Ranges: bytes`，确认支持断点续传。

2.  **数据一致性保障**：若文件在传输过程中被修改，需通过`If-Range`头验证文件完整性：



```
Range: bytes=10240-

If-Range: "5f8d02a8f12345"  # 基于文件的ETag值
```

服务器若发现文件已修改，会忽略`Range`头，返回完整文件（200 状态码）。



1.  **大文件分块策略**：客户端可将大文件分成多个固定大小的块（如 1MB / 块），并行请求不同块，加速下载（需控制并发数，避免服务器压力过大）。

2.  **兼容性处理**：部分老旧服务器不支持`Range`头，此时客户端需降级为完整下载，需做好容错处理。

### 五、应用场景与扩展

断点续传广泛应用于大文件下载（如安装包、视频）、断点上传（通过`Content-Range`实现）等场景。HTTP/2 和 HTTP/3 进一步优化了范围请求的效率，通过多路复用减少连接开销，提升续传体验。在实际开发中，可结合`Content-Disposition`头设置文件名（`attachment; filename="file.zip"`），优化用户下载体验。

