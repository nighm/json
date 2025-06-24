@echo off
echo 开始执行JMeter命令...
echo.

src\tools\jmeter\bin\jmeter.bat -n -t src\tools\jmeter\api_cases\register_test.jmx -l test_result.jtl -e -o test_report -Jthread_count 5 -Jiterations 1 -Jdevice_csv_file=data\generated_devices\devices.csv

echo.
echo JMeter命令执行完成！
pause 