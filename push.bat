@echo off
echo GitHub'da yeni repo olusturun: https://github.com/new
echo Repository name: destekadmin
echo.
set /p repo_url="GitHub repo URL'ini girin (ornek: https://github.com/username/destekadmin.git): "
echo.
git remote set-url origin %repo_url%
git push -u origin main
echo.
echo Yukleme tamamlandi!
pause