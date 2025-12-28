# 🔐 Google Maps API 安全设置指南

## 步骤 1: 获取 Google Maps API 密钥

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用以下 API：
   - Maps JavaScript API
   - Geocoding API
   - Places API
4. 转到"凭证" > "创建凭证" > "API 密钥"
5. 复制你的 API 密钥

## 步骤 2: 配置本地环境

1. 在项目根目录复制 `.env.example` 为 `.env.local`
   ```bash
   cp .env.example .env.local
   ```

2. 编辑 `.env.local` 文件，将 API 密钥添加到：
   ```
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   ```

## 步骤 3: 验证配置

启动开发服务器：
```bash
npm run dev
```

访问 `http://localhost:3000`，地图应该正常加载。

## 步骤 4: 上传到 GitHub 前的检查清单

- ✅ `.env.local` 已添加到 `.gitignore`
- ✅ `.env.example` 已提交（不包含真实密钥）
- ✅ 从未提交 `.env.local` 文件
- ✅ 验证 Git 配置：
  ```bash
  git status
  ```
  确保 `.env.local` 没有出现在列表中

## 步骤 5: 安全发布到 GitHub

```bash
git add .
git commit -m "Add Google Maps API integration with secure env configuration"
git push origin main
```

## 步骤 6: 部署到生产环境 (Vercel/Netlify)

### Vercel:
1. 连接你的 GitHub 仓库
2. 在 "Environment Variables" 中添加：
   ```
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_production_api_key
   ```
3. 部署

### Netlify:
1. 连接你的 GitHub 仓库
2. 在 "Build & deploy" > "Environment" 中添加：
   ```
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_production_api_key
   ```
3. 部署

## ⚠️ 安全最佳实践

1. **永远不要提交 `.env.local`**
   - 确保 `.gitignore` 包含 `.env.local`
   
2. **限制 API 密钥权限**
   - 在 Google Cloud Console 中设置 HTTP Referrer 限制
   - 只允许你的网站域名访问
   - 设置使用配额和告警

3. **定期轮换密钥**
   - 每季度生成新的 API 密钥
   - 删除旧的未使用的密钥

4. **监控 API 使用**
   - 在 Google Cloud Console 中检查使用统计
   - 设置成本告警

## 故障排除

### 地图不显示
- 检查 `.env.local` 文件是否存在
- 验证 API 密钥是否正确
- 检查浏览器控制台是否有错误信息

### API 限流或配额超出
- 在 Google Cloud Console 中检查使用情况
- 增加配额限制
- 考虑启用缓存策略

---

更多信息: [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
