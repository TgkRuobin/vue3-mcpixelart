# MCPixelArt - Minecraft 像素画/地图画、雕塑和红石音乐在线制作与分享平台

** 存档声明
🚨 2026/06/20 线上项目发布了彻底重构后的版本

该仓库（旧版）已停止维护与更新。我使用了全新的架构对项目进行了**彻底重构**，并移至了新仓库（目前闭源）。

**MCPixelArt** 是一个专注于 Minecraft 像素画/地图画、雕塑和红石音乐创作的在线平台。用户可以通过我们的工具轻松设计和分享自己的作品，无论是像素画、雕塑还是复杂的红石音乐，都能在这里找到灵感和工具。

This project is a platform dedicated to the online creation and sharing of Minecraft pixel art, sculptures, and redstone music, encompassing a complete frontend and backend.

## 项目简介

- **项目名称**: MCPixelArt  
- **项目类型**: 第三方 Minecraft 创作工具平台  
- **在线地址**: [https://mcpixelart.com](https://mcpixelart.com)  
- **B站主页**: [https://space.bilibili.com/1019826327](https://space.bilibili.com/1019826327)  

## 主要功能

1. **像素画/地图画制作**  
   - 提供直观的像素画转换页面，自定义大小和方块选择，可制作立体地图画，支持抖动算法。  
   - 生成 Minecraft 像素画/地图画投影，方便导入游戏。
   - 手动搭建功能方便基岩版/网易版/不用投影mod的玩家搭建

2. **雕塑设计**  
   - .obj文件转换为雕塑，支持在线预览和下载投影。

3. **红石音乐创作**  
   - 提供midi音乐转换。
   - 生成投影文件或手动搭建。
   - 3种音高调整方案，可拆分和查看音轨。

4. **作品分享与社区**  
   - 用户可以将自己的作品上传到平台，与其他玩家分享。  
   - 您可预览和下载其他用户分享的作品，或者为好的作品点赞！ 

## 操作教程

我准备了详细的教学视频，欢迎访问 B站主页观看: 
- [我的Bilibili主页](https://space.bilibili.com/1019826327)

## 项目启动

```sh
# 后端项目启动
cd backend
sh build.sh
sh run.sh

# 前端项目启动
cd ../
pnpm i
pnpm dev

# 投影文件会生成在 .env 的 STATIC_FOLDER 中
```

## 技术栈

- **[前端](./FRONT-END.md)**: Vue3, Vite, Tone.js, Three.js
- **[后端](./BACK-END.md)**: Python, Nginx
- **数据库**: Mysql

## 开发中遇到的问题和难点的解决思路

在[thought.md](thought.md)中做了详细记载

## 联系我

如果您有任何问题或合作意向，欢迎通过以下方式联系我：  
- **Email**: 19950083014@163.com  

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
