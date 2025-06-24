#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV文件顺序分片工具
将大型CSV文件按顺序分配到多个小文件中，确保数据不重复且完整
"""

import pandas as pd
import os
import sys
from pathlib import Path

def split_csv_sequentially(input_file, output_dir, parts=50, chunk_size=2000):
    """
    顺序拆分CSV文件，确保数据不重复且完整
    
    Args:
        input_file (str): 输入CSV文件路径
        output_dir (str): 输出目录
        parts (int): 分片数量
        chunk_size (int): 每个分片的数据量
    """
    print(f"🔧 开始顺序拆分CSV文件...")
    print(f"   输入文件: {input_file}")
    print(f"   输出目录: {output_dir}")
    print(f"   分片数量: {parts}")
    print(f"   每片大小: {chunk_size}")
    
    # 读取原始CSV文件
    try:
        df = pd.read_csv(input_file)
        total_rows = len(df)
        print(f"✅ 成功读取CSV文件，总行数: {total_rows}")
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {e}")
        return False
    
    # 验证数据完整性
    expected_total = parts * chunk_size
    if total_rows != expected_total:
        print(f"⚠️  警告: 数据量不匹配")
        print(f"   期望: {expected_total} 行")
        print(f"   实际: {total_rows} 行")
        print(f"   将调整分片策略...")
        
        # 重新计算分片大小
        chunk_size = total_rows // parts
        remainder = total_rows % parts
        print(f"   调整后每片大小: {chunk_size}")
        print(f"   剩余数据: {remainder} 行")
    else:
        # 数据量匹配，计算remainder
        remainder = total_rows % parts
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 顺序分配数据到各个分片
    start_idx = 0
    total_allocated = 0
    
    for i in range(parts):
        # 计算当前分片的结束索引
        if i < remainder:
            # 前remainder个分片多分配1行
            end_idx = start_idx + chunk_size + 1
        else:
            end_idx = start_idx + chunk_size
        
        # 确保不超过总行数
        end_idx = min(end_idx, total_rows)
        
        # 提取当前分片的数据
        chunk_df = df.iloc[start_idx:end_idx]
        chunk_rows = len(chunk_df)
        
        if chunk_rows == 0:
            print(f"⚠️  分片 {i+1} 为空，跳过")
            continue
        
        # 生成输出文件名
        output_file = os.path.join(output_dir, f"part_{i+1:02d}_{chunk_rows}rows.csv")
        
        # 保存分片文件
        try:
            chunk_df.to_csv(output_file, index=False)
            total_allocated += chunk_rows
            print(f"✅ 分片 {i+1:02d}: {chunk_rows} 行 -> {output_file}")
        except Exception as e:
            print(f"❌ 保存分片 {i+1} 失败: {e}")
            return False
        
        # 更新起始索引
        start_idx = end_idx
        
        # 检查是否已分配完所有数据
        if start_idx >= total_rows:
            break
    
    # 验证分配结果
    print(f"\n📊 分配结果统计:")
    print(f"   原始数据: {total_rows} 行")
    print(f"   已分配: {total_allocated} 行")
    print(f"   分片数量: {parts}")
    
    if total_allocated == total_rows:
        print(f"✅ 数据分配完整，无重复")
    else:
        print(f"❌ 数据分配不完整")
        return False
    
    return True

def main():
    """主函数"""
    # 配置参数
    input_file = "src/tools/jmeter/bin/fresh_devices_100000.csv"
    output_dir = "src/tools/jmeter/bin/device_parts"
    parts = 50  # 50个分片
    chunk_size = 2000  # 每个分片2000条数据
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    # 执行拆分
    success = split_csv_sequentially(input_file, output_dir, parts, chunk_size)
    
    if success:
        print(f"\n🎉 CSV文件顺序拆分完成!")
        print(f"   输出目录: {output_dir}")
        print(f"   请检查分片文件确保数据完整性")
    else:
        print(f"\n❌ CSV文件拆分失败!")
        return False
    
    return True

if __name__ == "__main__":
    main() 