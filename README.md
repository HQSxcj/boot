# Boot - 云盘媒体管理工具

一站式云盘媒体管理解决方案，支持 115 网盘、123 云盘和 OpenList 集成。

## 功能

- **云盘整理** - 支持 115/123 网盘文件自动识别和整理
- **STRM 生成** - 自动生成串流文件，支持 Emby/Jellyfin
- **离线下载** - Telegram Bot 接收链接，自动转存
- **Emby 集成** - 缺集检测、媒体库刷新
- **WebDAV** - 挂载 STRM 目录供播放器访问

## 快速开始

```bash
docker run -d \
  --name boot \
  -p 18080:18080 \
  -v /your/data:/data \
  -v /your/strm:/data/strm \
  -e SECRETS_ENCRYPTION_KEY=your-32-char-key \
  boot:latest
```

## 端口

| 端口 | 用途 |
|------|------|
| 18080 | Web UI + API + WebDAV |

## 数据目录

```
/data/
├── secrets.db      # 敏感数据(加密)
├── appdata.db      # 配置数据
├── config.yml      # 应用配置
├── strm/           # STRM 文件输出
└── logs/           # 应用日志
    └── app.log
```

## 技术栈

- **前端**: React + TypeScript + Tailwind CSS + Vite
- **后端**: Flask + SQLAlchemy + Gunicorn
- **部署**: Nginx + Docker

## 开发

```bash
# 前端
npm install
npm run dev

# 后端
cd backend
pip install -r requirements.txt
python main.py
```

## License

MIT
