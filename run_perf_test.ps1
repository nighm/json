# 设置PowerShell输出编码为UTF-8，防止emoji和中文报错
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
python scripts/performance_stress_test_plan.py --phase baseline --test-type register 