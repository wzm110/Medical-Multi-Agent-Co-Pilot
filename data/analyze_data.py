"""
医学GraphRAG数据预处理系统 - 数据分析和可视化
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置数据路径
data_dir = Path("d:\\LangGraph\\data")
data_file = data_dir / "数据" / "medical_chunks_v2.csv"

# 读取数据
print("读取数据文件...")
df = pd.read_csv(data_file, encoding='utf-8-sig')

# 移除chunk_id列（如果存在）
if 'chunk_id' in df.columns:
    df = df.drop('chunk_id', axis=1)

print("=" * 100)
print("医学GraphRAG数据预处理 - 数据分析报告")
print("=" * 100)

# 1. 基本统计
print("\n【1. 基本统计信息】")
print(f"总数据块数: {len(df):,}")
print(f"总字符数: {df['char_count'].sum():,}")
print(f"平均块大小: {df['char_count'].mean():.1f} 字符")
print(f"中位数块大小: {df['char_count'].median():.1f} 字符")
print(f"最小块大小: {df['char_count'].min()} 字符")
print(f"最大块大小: {df['char_count'].max()} 字符")

# 2. 按科室统计
print("\n【2. 按科室统计】")
department_stats = df['department'].value_counts()
print(f"科室数: {len(department_stats)}")
for department, count in department_stats.items():
    percentage = count / len(df) * 100
    print(f"  {department}: {count:,} 块 ({percentage:.1f}%)")

# 3. 按系统分类统计
print("\n【3. 按系统分类统计】")
system_stats = df['system_category'].value_counts()
print(f"系统类别数: {len(system_stats)}")
for system, count in system_stats.items():
    percentage = count / len(df) * 100
    print(f"  {system}: {count:,} 块 ({percentage:.1f}%)")

# 4. 按内容类型统计
print("\n【4. 按内容类型统计】")
content_type_stats = df['content_type'].value_counts()
for content_type, count in content_type_stats.items():
    percentage = count / len(df) * 100
    print(f"  {content_type}: {count:,} 块 ({percentage:.1f}%)")

# 5. 按块类型统计
print("\n【5. 按块类型统计】")
chunk_type_stats = df['chunk_type'].value_counts()
for chunk_type, count in chunk_type_stats.items():
    percentage = count / len(df) * 100
    print(f"  {chunk_type}: {count:,} 块 ({percentage:.1f}%)")

# 6. 按层级统计
print("\n【6. 按层级统计】")
hierarchy_stats = df['hierarchy_level'].value_counts().sort_index()
for level, count in hierarchy_stats.items():
    percentage = count / len(df) * 100
    level_name = {1: "章节级", 2: "小节级", 3: "子小节级"}.get(level, f"层级{level}")
    print(f"  {level_name} (level={level}): {count:,} 块 ({percentage:.1f}%)")

# 7. 科室与内容类型交叉分析
print("\n【7. 科室与内容类型交叉分析（前5个科室）】")
cross_tab = pd.crosstab(df['department'], df['content_type'])
print(cross_tab.head(5))

# 8. 关键词分析
print("\n【8. 关键词分析】")
all_keywords = []
for keywords in df['keywords'].dropna():
    all_keywords.extend(keywords.split(','))

keyword_counter = Counter(all_keywords)
print(f"唯一关键词数: {len(keyword_counter):,}")
print(f"前20个高频关键词:")
for keyword, count in keyword_counter.most_common(20):
    print(f"  {keyword}: {count:,} 次")

# 9. 关键词分析增强
print("\n【9. 关键词分析增强】")
# 从关键词中提取疾病相关词汇（简单过滤）
disease_keywords = [kw for kw in all_keywords if any(d in kw for d in ['病', '症', '综合征', '炎', '癌', '瘤', '血症'])]
disease_counter = Counter(disease_keywords)
print(f"识别到的疾病相关关键词数: {len(set(disease_keywords)):,}")
print(f"前20个常见疾病相关关键词:")
for disease, count in disease_counter.most_common(20):
    print(f"  {disease}: {count:,} 次")

# 10. 数据质量评估
print("\n【10. 数据质量评估】")
print(f"有关键词的块: {df['keywords'].notna().sum():,} / {len(df):,} ({df['keywords'].notna().sum()/len(df)*100:.1f}%)")
print(f"有章节信息的块: {df['chapter'].notna().sum():,} / {len(df):,} ({df['chapter'].notna().sum()/len(df)*100:.1f}%)")
print(f"有小节信息的块: {df['section'].notna().sum():,} / {len(df):,} ({df['section'].notna().sum()/len(df)*100:.1f}%)")
print(f"有子小节信息的块: {df['subsection'].notna().sum():,} / {len(df):,} ({df['subsection'].notna().sum()/len(df)*100:.1f}%)")

# 11. 块大小分布
print("\n【11. 块大小分布】")
size_ranges = [
    (0, 200, "极小 (<200)"),
    (200, 400, "小 (200-400)"),
    (400, 600, "中小 (400-600)"),
    (600, 800, "中等 (600-800)"),
    (800, 1000, "中大 (800-1000)"),
    (1000, 1500, "大 (1000-1500)"),
    (1500, float('inf'), "极大 (>1500)")
]

for min_size, max_size, label in size_ranges:
    count = len(df[(df['char_count'] >= min_size) & (df['char_count'] < max_size)])
    percentage = count / len(df) * 100
    print(f"  {label}: {count:,} 块 ({percentage:.1f}%)")

# 12. 各科室的平均块大小
print("\n【12. 各科室的平均块大小】")
avg_size_by_dept = df.groupby('department')['char_count'].mean().sort_values(ascending=False)
for dept, avg_size in avg_size_by_dept.items():
    print(f"  {dept}: {avg_size:.1f} 字符")

# 13. 创建可视化
print("\n【13. 生成可视化图表】")

# 创建图表
fig = plt.figure(figsize=(24, 20))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 13.1 按科室统计
ax1 = fig.add_subplot(gs[0, 0])
department_stats.plot(kind='bar', ax=ax1, color='steelblue')
ax1.set_title('按科室统计', fontsize=14, fontweight='bold')
ax1.set_xlabel('科室', fontsize=12)
ax1.set_ylabel('数据块数', fontsize=12)
ax1.tick_params(axis='x', rotation=45)

# 13.2 按系统分类
ax2 = fig.add_subplot(gs[0, 1])
system_stats.plot(kind='bar', ax=ax2, color='skyblue')
ax2.set_title('按系统分类统计', fontsize=14, fontweight='bold')
ax2.set_xlabel('系统类别', fontsize=12)
ax2.set_ylabel('数据块数', fontsize=12)
ax2.tick_params(axis='x', rotation=45)

# 13.3 按内容类型
ax3 = fig.add_subplot(gs[0, 2])
content_type_stats.plot(kind='bar', ax=ax3, color='lightcoral')
ax3.set_title('按内容类型统计', fontsize=14, fontweight='bold')
ax3.set_xlabel('内容类型', fontsize=12)
ax3.set_ylabel('数据块数', fontsize=12)
ax3.tick_params(axis='x', rotation=45)

# 13.4 按块类型
ax4 = fig.add_subplot(gs[1, 0])
chunk_type_stats.plot(kind='bar', ax=ax4, color='lightgreen')
ax4.set_title('按块类型统计', fontsize=14, fontweight='bold')
ax4.set_xlabel('块类型', fontsize=12)
ax4.set_ylabel('数据块数', fontsize=12)
ax4.tick_params(axis='x', rotation=45)

# 13.5 按层级
ax5 = fig.add_subplot(gs[1, 1])
hierarchy_stats.plot(kind='bar', ax=ax5, color='orange')
ax5.set_title('按层级统计', fontsize=14, fontweight='bold')
ax5.set_xlabel('层级', fontsize=12)
ax5.set_ylabel('数据块数', fontsize=12)
level_labels = []
for i in hierarchy_stats.index:
    if i <= 3:
        label = ['章节级', '小节级', '子小节级'][i-1]
    else:
        label = f'层级{i}'
    level_labels.append(f"{i}\n({label})")
ax5.set_xticklabels(level_labels)

# 13.6 块大小分布
ax6 = fig.add_subplot(gs[1, 2])
ax6.hist(df['char_count'], bins=30, color='purple', alpha=0.7, edgecolor='black')
ax6.set_title('块大小分布', fontsize=14, fontweight='bold')
ax6.set_xlabel('字符数', fontsize=12)
ax6.set_ylabel('频数', fontsize=12)
ax6.axvline(df['char_count'].mean(), color='red', linestyle='--', linewidth=2, label=f'平均值: {df["char_count"].mean():.0f}')
ax6.legend()

# 13.7 科室与内容类型热力图（前5个科室）
ax7 = fig.add_subplot(gs[2, 0])
top5_depts = cross_tab.head(5)
sns.heatmap(top5_depts, annot=True, fmt='d', cmap='YlOrRd', ax=ax7)
ax7.set_title('科室与内容类型交叉分析（前5科室）', fontsize=14, fontweight='bold')

# 13.8 高频关键词（前15）
ax8 = fig.add_subplot(gs[2, 1])
top15_keywords = keyword_counter.most_common(15)
keywords_df = pd.DataFrame(top15_keywords, columns=['关键词', '频次'])
ax8.barh(keywords_df['关键词'], keywords_df['频次'], color='teal')
ax8.set_title('高频关键词（前15）', fontsize=14, fontweight='bold')
ax8.set_xlabel('频次', fontsize=12)
ax8.invert_yaxis()

# 13.9 各科室平均块大小
ax9 = fig.add_subplot(gs[2, 2])
avg_size_by_dept.plot(kind='bar', ax=ax9, color='brown')
ax9.set_title('各科室平均块大小', fontsize=14, fontweight='bold')
ax9.set_xlabel('科室', fontsize=12)
ax9.set_ylabel('平均字符数', fontsize=12)
ax9.tick_params(axis='x', rotation=45)

plt.savefig(data_dir / 'data_analysis.png', dpi=300, bbox_inches='tight')
print(f"  图表已保存到: {data_dir / 'data_analysis.png'}")

# 14. 生成详细报告
print("\n【14. 生成详细报告】")
report_file = data_dir / 'data_preprocessing_report.txt'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("医学GraphRAG数据预处理 - 详细报告\n")
    f.write("=" * 100 + "\n\n")
    
    f.write("【1. 数据概览】\n")
    f.write(f"总数据块数: {len(df):,}\n")
    f.write(f"总字符数: {df['char_count'].sum():,}\n")
    f.write(f"平均块大小: {df['char_count'].mean():.1f} 字符\n")
    f.write(f"中位数块大小: {df['char_count'].median():.1f} 字符\n\n")
    
    f.write("【2. 科室分类】\n")
    for department, count in department_stats.items():
        percentage = count / len(df) * 100
        f.write(f"  {department}: {count:,} 块 ({percentage:.1f}%)\n")
    f.write("\n")
    
    f.write("【3. 系统分类】\n")
    for system, count in system_stats.items():
        percentage = count / len(df) * 100
        f.write(f"  {system}: {count:,} 块 ({percentage:.1f}%)\n")
    f.write("\n")
    
    f.write("【4. 内容类型】\n")
    for content_type, count in content_type_stats.items():
        percentage = count / len(df) * 100
        f.write(f"  {content_type}: {count:,} 块 ({percentage:.1f}%)\n")
    f.write("\n")
    
    f.write("【5. 块类型】\n")
    for chunk_type, count in chunk_type_stats.items():
        percentage = count / len(df) * 100
        f.write(f"  {chunk_type}: {count:,} 块 ({percentage:.1f}%)\n")
    f.write("\n")
    
    f.write("【6. 层级分布】\n")
    for level, count in hierarchy_stats.items():
        percentage = count / len(df) * 100
        level_name = {1: "章节级", 2: "小节级", 3: "子小节级"}.get(level, f"层级{level}")
        f.write(f"  {level_name} (level={level}): {count:,} 块 ({percentage:.1f}%)\n")
    f.write("\n")
    
    f.write("【7. 高频关键词（前50）】\n")
    for keyword, count in keyword_counter.most_common(50):
        f.write(f"  {keyword}: {count:,} 次\n")
    f.write("\n")
    
    f.write("【8. 常见疾病（前50）】\n")
    for disease, count in disease_counter.most_common(50):
        f.write(f"  {disease}: {count:,} 块\n")
    f.write("\n")
    
    f.write("【9. 数据质量】\n")
    f.write(f"有关键词的块: {df['keywords'].notna().sum():,} / {len(df):,} ({df['keywords'].notna().sum()/len(df)*100:.1f}%)\n")
    f.write(f"有章节信息的块: {df['chapter'].notna().sum():,} / {len(df):,} ({df['chapter'].notna().sum()/len(df)*100:.1f}%)\n")
    f.write(f"有小节信息的块: {df['section'].notna().sum():,} / {len(df):,} ({df['section'].notna().sum()/len(df)*100:.1f}%)\n")
    f.write(f"有子小节信息的块: {df['subsection'].notna().sum():,} / {len(df):,} ({df['subsection'].notna().sum()/len(df)*100:.1f}%)\n")
    f.write("\n")
    
    f.write("【10. 块大小分布】\n")
    for min_size, max_size, label in size_ranges:
        count = len(df[(df['char_count'] >= min_size) & (df['char_count'] < max_size)])
        percentage = count / len(df) * 100
        f.write(f"  {label}: {count:,} 块 ({percentage:.1f}%)\n")
    f.write("\n")
    
    f.write("【11. 各科室平均块大小】\n")
    for dept, avg_size in avg_size_by_dept.items():
        f.write(f"  {dept}: {avg_size:.1f} 字符\n")
    f.write("\n")
    
    f.write("【12. 元数据字段说明】\n")
    f.write("  chunk_id: 数据块唯一标识符\n")
    f.write("  content: 数据块内容\n")
    f.write("  source_file: 来源文件路径\n")
    f.write("  chapter: 章节名称\n")
    f.write("  section: 小节名称\n")
    f.write("  subsection: 子小节名称\n")
    f.write("  department: 科室（如：呼吸内科、心血管内科）\n")
    f.write("  system_category: 系统分类（如：呼吸系统疾病）\n")
    f.write("  content_type: 内容类型（如：鉴别诊断、治疗指南）\n")

    f.write("  chunk_type: 块类型（如：概述、临床表现、诊断、治疗）\n")
    f.write("  hierarchy_level: 层级级别（1=章节级，2=小节级，3=子小节级）\n")
    f.write("  keywords: 关键词（逗号分隔）\n")
    f.write("  char_count: 字符数\n")
    f.write("  token_count: Token数（估算）\n")
    
    f.write("\n" + "=" * 100 + "\n")
    f.write("报告生成时间: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
    f.write("=" * 100 + "\n")

print(f"  详细报告已保存到: {report_file}")

print("\n" + "=" * 100)
print("数据分析完成！")
print("=" * 100)
