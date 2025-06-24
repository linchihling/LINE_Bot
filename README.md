# LINE Bot 專案

這是一個基於 FastAPI 的 LINE Bot 專案，主要用於東和鋼鐵公司的生產監控和通知系統。專案包含兩個主要的 LINE Bot 功能：TY Scrap Bot 和 THS Bot，用於處理不同的業務需求。

## 🚀 功能特色

### TY Scrap Bot
- **機器監控查詢**: 支援軋一、軋二機器的影像查詢
- **互動式選單**: 提供日期、時間、影像清單的選擇介面
- **即時影像檢視**: 可查看最新的生產影像
- **Flex Message 支援**: 使用 LINE 的 Flex Message 提供豐富的互動體驗

### THS Bot (Push Bot)
- **多專案通知**: 支援多個監控專案的通知推送
  - 鋼筋檢測 (ty_scrap)
  - 噴水檢測 (water_spray)
  - 火花檢測 (spark_detection)
  - 粉塵檢測 (dust_detection)
  - 姿勢檢測 (pose_detection)
- **雙重通知**: 同時發送 LINE 群組訊息和 NTFY 通知
- **圖片支援**: 可附加圖片到通知訊息中

## 🏗️ 專案架構

```
LINE_Bot/
├── main.py                 # FastAPI 應用程式入口
├── requirements.txt        # Python 依賴套件
├── Dockerfile             # Docker 映像檔配置
├── docker-compose.yml     # Docker Compose 配置
├── config/                # 配置檔案
│   ├── config.yaml        # 主要配置
│   └── logging.yaml       # 日誌配置
├── routers/               # API 路由
│   ├── ths_bot.py         # THS Bot 路由
│   └── ty_scrap.py        # TY Scrap Bot 路由
├── handlers/              # 業務邏輯處理器
│   └── ty_scrap_handler.py # TY Scrap Bot 處理器
├── utils/                 # 工具模組
│   ├── factory.py         # 工廠模式工具
│   ├── fetch_url.py       # URL 抓取工具
│   └── notification.py    # 通知工具
└── tests/                 # 測試檔案
    ├── test_ths_bot.py    # THS Bot 測試
    ├── test_ty_scrap.py   # TY Scrap Bot 測試
    └── utils.py           # 測試工具
```

## 🛠️ 技術棧

- **後端框架**: FastAPI
- **LINE Bot SDK**: line-bot-sdk v3.11.0
- **網頁爬蟲**: BeautifulSoup4
- **通知服務**: NTFY
- **日誌系統**: Logstash
- **容器化**: Docker & Docker Compose
- **測試框架**: pytest
- **速率限制**: slowapi

## 📋 環境需求

- Python 3.12+
- Docker & Docker Compose
- LINE Bot Channel (需要 Channel Access Token 和 Channel Secret)

## 🔧 安裝與設定

### 1. 環境變數設定

建立 `.env` 檔案並設定以下環境變數：

```env
# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN_TY_SCRAP=your_ty_scrap_access_token
LINE_CHANNEL_SECRET_TY_SCRAP=your_ty_scrap_channel_secret
WEBHOOKS_URL_TY_SCRAP=/webhooks/ty_scrap
GROUP_ID_TY_SCRAP=your_ty_scrap_group_id

LINE_CHANNEL_ACCESS_TOKEN_PUSHBOT=your_pushbot_access_token
LINE_CHANNEL_SECRET_PUSHBOT=your_pushbot_channel_secret
WEBHOOKS_URL_PUSHBOT=/webhooks/pushbot

# 群組 ID 設定
GROUP_ID_PUSHBOT_TY_SCRAP=your_ty_scrap_group_id
GROUP_ID_PUSHBOT_TY_WATER_SPRAY=your_water_spray_group_id
GROUP_ID_PUSHBOT_TY_SPARK_DETECTION=your_spark_detection_group_id
GROUP_ID_PUSHBOT_TY_DUST_DETECTION=your_dust_detection_group_id
GROUP_ID_PUSHBOT_TY_POSE_DETECTION=your_pose_detection_group_id

# NTFY 主題設定
NTFY_TY_SCRAP=your_ty_scrap_ntfy_topic
NTFY_TY_WATER_SPRAY=your_water_spray_ntfy_topic
NTFY_TY_SPARK_DETECTION=your_spark_detection_ntfy_topic
NTFY_TY_DUST_DETECTION=your_dust_detection_ntfy_topic
NTFY_TY_POSE_DETECTION=your_pose_detection_ntfy_topic

# Logstash 設定
LOGSTASH_INTERNAL_PASSWORD=your_logstash_password
```

### 2. 使用 Docker Compose 啟動

```bash
# 建置並啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f linebot
```

### 3. 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動應用程式
uvicorn main:app --host 0.0.0.0 --port 6000 --reload
```

## 📡 API 端點

### TY Scrap Bot Webhook
- **POST** `/webhooks/ty_scrap/line` - LINE Bot webhook 端點

### THS Bot Webhook
- **POST** `/webhooks/pushbot/line` - LINE Bot webhook 端點

### 通知端點
- **POST** `/webhooks/pushbot/notify/ty_scrap` - 鋼筋檢測通知
- **POST** `/webhooks/pushbot/notify/ty_system_scrap` - 系統鋼筋檢測通知
- **POST** `/webhooks/pushbot/notify/water_spray` - 噴水檢測通知
- **POST** `/webhooks/pushbot/notify/spark_detection` - 火花檢測通知
- **POST** `/webhooks/pushbot/notify/dust_detection_150` - 粉塵檢測通知
- **POST** `/webhooks/pushbot/notify/pose_detection` - 姿勢檢測通知

## 🤖 Bot 使用方式

### TY Scrap Bot 指令

1. **查詢機器影像**: 輸入 `(軋一)` 或 `(軋二)`
2. **選擇日期**: 從日期選單中選擇
3. **選擇時間**: 從時間選單中選擇
4. **查看影像**: 從影像清單中選擇
5. **查看最新影像**: 輸入 `(軋一)最新` 或 `(軋二)最新`

### 通知格式

#### 鋼筋檢測通知
```json
{
  "rolling_line": "1",
  "message": "檢測到異常",
  "image_path": "20241023_10/test.png"
}
```

#### 圖片通知
```json
{
  "message": "檢測到異常",
  "image_filename": "test.png"
}
```

#### 文字通知
```json
{
  "message": "系統通知訊息"
}
```

## 🧪 測試

執行測試：

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_ths_bot.py
pytest tests/test_ty_scrap.py

# 生成 HTML 測試報告
pytest --html=report.html
```

## 📊 監控與日誌

- **日誌系統**: 使用 Logstash 進行日誌收集和分析
- **速率限制**: 所有 API 端點都有速率限制保護
- **錯誤處理**: 完整的錯誤處理和日誌記錄

## 🔒 安全性

- **簽名驗證**: 所有 LINE webhook 都經過簽名驗證
- **速率限制**: 防止 API 濫用
- **環境變數**: 敏感資訊使用環境變數管理

## 🚀 部署

### 生產環境部署

1. 設定生產環境變數
2. 使用 Docker Compose 部署
3. 設定反向代理 (如 Nginx)
4. 配置 SSL 憑證
5. 設定監控和警報

### 健康檢查

應用程式會在以下端點提供健康檢查：
- `GET /docs` - API 文件
- `GET /openapi.json` - OpenAPI 規格

## 🤝 貢獻

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

此專案為東和鋼鐵公司內部專案，請遵循公司相關政策。

## 📞 支援

如有問題或需要支援，請聯繫開發團隊或建立 Issue。

---

**注意**: 請確保在部署前正確設定所有環境變數，並測試所有功能。
