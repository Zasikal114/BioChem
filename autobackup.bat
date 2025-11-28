@echo off
echo starting backup...

cd /d "C:\Users\lenovo\Desktop\jython"

git add .
git commit -m "自动备份: %date% %time%"
git push

echo backup completed.
timeout 5