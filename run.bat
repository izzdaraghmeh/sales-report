@echo off
echo تشغيل نظام تقرير قسم المبيعات...
echo.
echo تأكد من تثبيت Python أولاً
echo.
pause
echo تثبيت المتطلبات...
pip install -r requirements.txt
echo.
echo تشغيل التطبيق...
echo.
echo سيتم فتح التطبيق على: http://localhost:5000
echo.
python app.py
pause

