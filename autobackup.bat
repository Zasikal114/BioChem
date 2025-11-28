@echo off
echo 开始自动备份...

cd /d "C:\Users\lenovo\Desktop\jython"

git add .
git commit -m "自动备份: %date% %time%"
git push

echo 备份完成!
timeout 5