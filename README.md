# 种子盒截图脚本

此脚本为个人使用，用于帮助用户在 Linux 系统（主要为 Debian 系）中批量从视频文件中生成高质量的随机 PNG 截图，并可选进行无损压缩。截图会自动上传到PiXhost图床，并且返回直接连接和BBCode。

许多种子因截图链接失效或质量欠佳需要重新截图上传。使用此脚本可以方便快速重新截图，完成转种。

### 特性简介

- **无损压缩工具**：采用 `oxipng` 替代 `OptiPNG`，支持多核多线程，加速压缩过程。 `OptiPNG` 虽然优秀，但不支持多核，`oxipng` 则更适合盒子的压缩需求。脚本提供 `oxipng` 的一键安装和卸载功能（仅支持 x86_64 架构）。
- **自动化与高效**：支持批量截图、自动上传图床，便于转种。

### 效果预览：
  
![6bd7fc0ef09271c612d1931c566901a6.png](https://ice.frostsky.com/2024/11/12/6bd7fc0ef09271c612d1931c566901a6.png)
---

## 一、功能

1. **随机截图生成**：使用 `ffmpeg` 从视频生成随机无损 PNG 截图。
2. **无损压缩**：通过 `oxipng` 压缩截图（可选）。
3. **自动上传图床**：在图片处理完成后会自动上传到PiXhost图床。
4. **多线程压缩**：默认开启多线程加速压缩，可在低性能盒子上选择关闭。
5. **`oxipng` 自动安装/卸载**：支持 `x86_64` 架构的 Linux 系统一键安装 `oxipng`，`ARM` 架构暂不支持。

---

## 二、环境要求

- **操作系统**：Linux（主要为 Debian 系，其他系统未测试）。
- **测试环境**：netcup rs1000 G9.5（Debian 11）、甲骨文 Oracle ARM（Ubuntu 22.04）
- **依赖工具**：
  - `ffmpeg`：用于截图。
  - `oxipng`（可选）：用于 PNG 图片无损压缩。
  - `Python 3.x`：脚本基于 Python 3.x 开发。

---

## 三、安装依赖

在使用脚本之前，请确保系统已安装以下工具：

- **安装 `ffmpeg`**：
  
  ```bash
  sudo apt-get update
  sudo apt-get install ffmpeg
  ```

- **安装 `oxipng`（可选，一键安装仅适用 x86_64 架构）**：

  使用此脚本一键安装 `oxipng`：

  ```bash
  python3 script.py oxipng
  ```

  若使用 `ARM` 架构（如 `aarch64`），脚本会提示不支持自动安装。

---

## 四、使用方法

### (1) 截图和压缩

运行以下命令从视频中生成指定数量的随机无损 PNG 截图，保存在 `screenshots` 文件夹，并自动上传到图床：

```bash
python3 script.py 视频文件 截图数量 [压缩质量] [-t]
```

- **视频文件**：视频文件的路径。
- **截图数量**：生成截图数量（正整数）。
- **压缩质量**（可选）：指定图片的压缩质量，范围 1 到 6。数字越大压缩效果越好，但时间更长。
- **-t**（可选）：关闭多线程，适合低性能盒子。

#### 示例

1. 最基本用法，生成 5 张随机截图，不指定压缩质量：
   ```bash
   python3 script.py /path/to/video.mp4 5
   ```

2. 生成 10 张随机截图，压缩质量为 3：
   ```bash
   python3 script.py /path/to/video.mp4 10 3
   ```

3. 生成 5 张截图，使用单线程压缩：
   ```bash
   python3 script.py /path/to/video.mp4 5 4 -t
   ```

4. 生成 5 张截图，不指定压缩质量，使用单线程：
   ```bash
   python3 script.py /path/to/video.mp4 5 -t
   ```

---

### (2) `oxipng` 的安装与卸载

- **安装 `oxipng`**：

  若使用的是 `x86_64` 架构的 Linux 系统，运行以下命令安装 `oxipng`：

  ```bash
  python3 script.py oxipng
  ```

  `ARM` 架构暂不支持自动安装。

- **卸载 `oxipng`**：

  运行以下命令卸载 `oxipng`：

  ```bash
  python3 script.py unoxipng
  ```

---

## 注意事项

1. **`ffmpeg` 必须预先安装**：脚本依赖 `ffmpeg` 截图，未安装将导致错误。
2. **`oxipng` 压缩为可选项**：如未安装 `oxipng`，截图功能仍可正常运行。需要时可通过 `python3 script.py oxipng` 安装。
3. **截图数量限制**：如截图数量超过 50，脚本会给出警告并询问用户是否继续操作。

----

## 后续更新计划
1. 自动上传图床功能可关闭，关闭后将打包截图文件夹为压缩包
2. 支持更多图床
3. 修复PiXhost图床服务器号的错误获取
