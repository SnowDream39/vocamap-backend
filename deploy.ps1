# deploy.ps1
Write-Host "🚀 正在命令服务器部署..." -ForegroundColor Cyan

# 你的服务器信息（请自行修改）
$serverUser = "root"
$serverHost = "8.209.210.116"
$remotePath = "/var/www/Vocabili-database"

ssh "$serverUser@$serverHost" "cd $remotePath; source /var/www/vocamap-backend/venv/bin/activate; git pull; /root/.local/share/pnpm/pm2 restart vocamap-api --update-env;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 部署完成！" -ForegroundColor Green
} else {
    Write-Host "❌ 部署失败，请检查 SCP 配置或网络。" -ForegroundColor Red
}
