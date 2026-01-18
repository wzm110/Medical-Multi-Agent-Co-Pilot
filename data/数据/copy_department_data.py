"""
科室数据复制工具
将选择的科室CSV文件复制到指定目录的input文件夹
"""

import os
import shutil
from pathlib import Path

def list_department_files():
    """列出所有科室CSV文件"""
    data_dir = Path("d:\\LangGraph\\data\\数据")
    
    csv_files = list(data_dir.glob("*.csv"))
    csv_files = [f for f in csv_files if f.name != "medical_chunks_v2.csv"]
    
    return sorted(csv_files, key=lambda x: x.name)

def extract_department_name(filename):
    """从CSV文件名提取科室名称"""
    return filename.replace(".csv", "")

def copy_department_data(department_csv_file, target_base_dir):
    """复制科室数据到目标目录"""
    
    department_name = extract_department_name(department_csv_file.name)
    
    target_dir = Path(target_base_dir) / department_name
    input_dir = target_dir / "input"
    
    print(f"\n选择的科室: {department_name}")
    print(f"源文件: {department_csv_file}")
    print(f"目标目录: {input_dir}")
    
    if not department_csv_file.exists():
        print(f"错误: 源文件不存在！")
        return False
    
    try:
        input_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = input_dir / department_csv_file.name
        
        shutil.copy2(department_csv_file, target_file)
        
        file_size = target_file.stat().st_size / 1024
        print(f"\n✓ 复制成功！")
        print(f"  目标文件: {target_file}")
        print(f"  文件大小: {file_size:.2f} KB")
        
        return True
    except Exception as e:
        print(f"\n✗ 复制失败: {e}")
        return False

def main():
    """主函数"""
    
    print("=" * 80)
    print("科室数据复制工具")
    print("=" * 80)
    
    csv_files = list_department_files()
    
    if not csv_files:
        print("\n错误: 未找到科室CSV文件！")
        print("请确保在 d:\\LangGraph\\data\\数据\\ 目录下有科室CSV文件。")
        return
    
    print(f"\n找到 {len(csv_files)} 个科室CSV文件:\n")
    
    for idx, csv_file in enumerate(csv_files, 1):
        file_size = csv_file.stat().st_size / 1024
        print(f"  {idx}. {csv_file.name} ({file_size:.2f} KB)")
    
    print("\n" + "=" * 80)
    
    while True:
        try:
            choice = input("\n请选择要复制的科室编号 (1-{}, 输入q退出): ".format(len(csv_files)))
            
            if choice.lower() == 'q':
                print("\n已退出。")
                return
            
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(csv_files):
                selected_file = csv_files[choice_num - 1]
                
                target_base_dir = "D:\\医学Graph\\知识图谱"
                
                success = copy_department_data(selected_file, target_base_dir)
                
                if success:
                    print("\n" + "=" * 80)
                    print("操作完成！")
                    print("=" * 80)
                break
            else:
                print(f"\n错误: 请输入1到{len(csv_files)}之间的数字！")
                
        except ValueError:
            print("\n错误: 请输入有效的数字！")
        except KeyboardInterrupt:
            print("\n\n已取消操作。")
            return

if __name__ == "__main__":
    main()
