import pandas as pd
from pathlib import Path

def split_data_by_department():
    """按科室将数据分离成不同的CSV文件"""
    
    data_dir = Path("d:\\LangGraph\\data")
    input_file = data_dir / "数据/medical_chunks_v2.csv"
    output_dir = data_dir / "数据"
    
    print("读取原始数据文件...")
    df = pd.read_csv(input_file)
    print(f"总数据块数: {len(df)}")
    
    print("\n科室分布:")
    print(df['department'].value_counts())
    
    print("\n开始按科室分离数据...")
    
    for department in df['department'].unique():
        if pd.isna(department):
            continue
            
        department_data = df[df['department'] == department]
        
        filename = f"{department}.csv"
        output_file = output_dir / filename
        
        # 移除chunk_id列（如果存在）
        if 'chunk_id' in department_data.columns:
            department_data = department_data.drop('chunk_id', axis=1)
        department_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"  生成文件: {filename} ({len(department_data)} 个数据块)")
    
    print("\n数据分离完成！")
    print(f"\n生成的文件列表:")
    
    for department in df['department'].unique():
        if pd.isna(department):
            continue
        filename = f"{department}.csv"
        output_file = output_dir / filename
        if output_file.exists():
            file_size = output_file.stat().st_size / 1024
            print(f"  - {filename} ({file_size:.2f} KB)")

if __name__ == "__main__":
    split_data_by_department()
