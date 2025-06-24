# LINE Bot 專案

這是一個基於 FastAPI 的 LINE Bot 專案，包含兩個 LINE Bot：TY Scrap Bot 和 THS Bot，用於處理不同的業務需求。

## 功能特色

### TY Scrap Bot
- **機器監控查詢**: 提供有加入此 LINE Bot 的使用者查詢影像
- **互動式選單**: 透過 LINE 的 Flex Message 提供日期、時間、影像清單的互動介面，最後回傳使用者查詢的特定影像
- **即時影像檢視**: 隨時查看最新的生產影像

### THS Bot 
- **多專案通知**: 支援多個專案的訊息發送
- **雙重通知**: 同時發送 LINE 群組訊息和 NTFY 通知
- **圖片支援**: 可附加圖片到通知訊息中

## 專案架構

```
LINE_Bot/
├── main.py                 
├── requirements.txt        
├── Dockerfile             
├── docker-compose.yml    
├── config/                
│   ├── config.yaml       
│   └── logging.yaml      
├── routers/               
│   ├── ths_bot.py        
│   └── ty_scrap.py        
├── handlers/              
│   └── ty_scrap_handler.py 
├── utils/                
│   ├── factory.py         
│   ├── fetch_url.py      
│   └── notification.py    
└── tests/                 
    ├── test_ths_bot.py    
    ├── test_ty_scrap.py   
    └── utils.py          
```

## 技術棧

- **後端框架**: FastAPI
- **LINE Bot SDK**: line-bot-sdk v3.11.0
- **網頁爬蟲**: BeautifulSoup4
- **通知服務**: NTFY
- **日誌系統**: Logstash
- **容器化**: Docker & Docker Compose
- **測試框架**: pytest
- **速率限制**: slowapi

## 環境需求

- Python 3.12+
- Docker & Docker Compose
- LINE Bot Channel (需要 Channel Access Token 和 Channel Secret)

## 安裝與設定

### 1. 環境變數設定

建立 `.env` 檔案並設定以下環境變數：

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

## API 端點

### TY Scrap Bot Webhook
- **POST** `/webhooks/ty_scrap/line` - LINE Bot webhook 端點

### THS Bot Webhook
- **POST** `/webhooks/pushbot/line` - LINE Bot webhook 端點

### 通知端點
- **POST** `/webhooks/pushbot/notify/ty_scrap` 
- **POST** `/webhooks/pushbot/notify/ty_system_scrap` 
- **POST** `/webhooks/pushbot/notify/water_spray` 
- **POST** `/webhooks/pushbot/notify/spark_detection`
- **POST** `/webhooks/pushbot/notify/dust_detection_150` 
- **POST** `/webhooks/pushbot/notify/pose_detection` 

## Bot 使用方式

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
  "message": "系統異常通知訊息",
  "image_path": "20241023_10/test.png"
}
```

#### 圖片通知
```json
{
  "message": "系統異常通知訊息",
  "image_filename": "test.png"
}
```

#### 文字通知
```json
{
  "message": "系統異常通知訊息"
}
```

## 測試

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

## 監控與日誌

- **日誌系統**: 使用 Logstash 進行日誌收集和分析，紀錄於Elasticsearch
- **速率限制**: 所有 API 端點都有速率限制保護
- **錯誤處理**: 完整的錯誤處理和日誌記錄

## 安全性

- **簽名驗證**: 所有 LINE webhook 都經過簽名驗證
- **速率限制**: 防止 API 濫用
- **環境變數**: 敏感資訊使用環境變數管理

## 部署

### 生產環境部署

1. 設定生產環境變數
2. 使用 Docker Compose 部署
3. 設定反向代理 (如 Nginx)
4. 配置 SSL 憑證
5. 設定監控和警報


**注意**: 此專案為東和鋼鐵公司內部專案，部分重要資訊已移除，僅供參閱。
