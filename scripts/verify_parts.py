#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分片数据验证脚本
验证分片文件的唯一性和完整性
"""

import pandas as pd
import os
import glob

def verify_parts():
    """验证分片数据的唯一性和完整性"""
    parts_dir = "src/tools/jmeter/bin/device_parts"
    
    # 获取所有分片文件
    part_files = glob.glob(os.path.join(parts_dir, "part_*.csv"))
    part_files.sort()
    
    print(f"🔍 开始验证分片数据...")
    print(f"   分片目录: {parts_dir}")
    print(f"   分片数量: {len(part_files)}")
    
    # 读取所有分片数据
    all_sns = set()
    all_macs = set()
    total_rows = 0
    
    for i, file_path in enumerate(part_files, 1):
        try:
            df = pd.read_csv(file_path)
            rows = len(df)
            total_rows += rows
            
            # 检查序列号唯一性
            sns = set(df['device_serial_number'])
            macs = set(df['mac'])
            
            # 检查与之前分片的重复
            sn_duplicates = all_sns & sns
            mac_duplicates = all_macs & macs
            
            if sn_duplicates:
                print(f"❌ 分片 {i}: 发现重复序列号 {len(sn_duplicates)} 个")
            if mac_duplicates:
                print(f"❌ 分片 {i}: 发现重复MAC地址 {len(mac_duplicates)} 个")
            
            # 添加到总集合
            all_sns.update(sns)
            all_macs.update(macs)
            
            print(f"✅ 分片 {i:02d}: {rows} 行, SN唯一: {len(sns)}, MAC唯一: {len(macs)}")
            
        except Exception as e:
            print(f"❌ 读取分片 {i} 失败: {e}")
            return False
    
    # 最终验证
    print(f"\n📊 最终验证结果:")
    print(f"   总行数: {total_rows}")
    print(f"   唯一序列号: {len(all_sns)}")
    print(f"   唯一MAC地址: {len(all_macs)}")
    
    if total_rows == 100000 and len(all_sns) == 100000 and len(all_macs) == 100000:
        print(f"✅ 验证通过：数据完整且唯一")
        return True
    else:
        print(f"❌ 验证失败：数据不完整或存在重复")
        return False

if __name__ == "__main__":
    verify_parts() 