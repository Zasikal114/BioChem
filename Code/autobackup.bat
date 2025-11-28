@echo off
echo starting backup...

cd /d "C:\Users\lenovo\Desktop\jython"

git add .
git commit -m "auto backup %date% %time%"
git push

echo backup completed.
timeout 60