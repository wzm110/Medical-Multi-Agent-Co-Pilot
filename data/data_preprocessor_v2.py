"""
医学GraphRAG数据预处理系统 - 修复版V2
修复section/subsection提取问题，改进disease_name提取，添加科室分离
"""

import re
import csv
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib
import jieba
import jieba.analyse


@dataclass
class ChunkMetadata:
    """数据块元数据"""
    content: str
    source_file: str
    chapter: str
    section: str = ""
    subsection: str = ""
    department: str = ""
    system_category: str = ""
    content_type: str = ""
    chunk_type: str = ""
    hierarchy_level: int = 0
    parent_chunk: str = ""
    keywords: str = ""
    char_count: int = 0
    token_count: int = 0


class FixedMedicalDataPreprocessorV2:
    """修复的医学数据预处理器V2"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.chunks = []
        
        # 初始化jieba分词
        jieba.initialize()
        
        # 加载医学词典
        self._load_medical_dict()
        
        # 系统分类映射
        self.system_mapping = {
            "呼吸系统疾病": ["呼吸", "肺", "支气管", "哮喘", "肺炎", "肺栓塞", "气胸", "胸腔积液", "慢性阻塞性肺", "上呼吸道感染", "气管炎"],
            "心血管系统疾病": ["心血管", "心脏", "心力衰竭", "高血压", "冠心病", "心律失常", "心包", "心肌", "心绞痛", "心肌梗死", "心功能"],
            "消化系统疾病": ["消化", "胃肠", "肝", "胆", "胰腺", "腹", "呕吐", "腹泻", "黄疸", "溃疡", "肝硬化", "胃炎", "肠炎"],
            "泌尿系统疾病": ["泌尿", "肾", "尿", "膀胱", "前列腺", "肾炎", "肾衰竭", "尿路感染"],
            "血液和造血系统疾病": ["血液", "贫血", "出血", "凝血", "白血病", "淋巴瘤", "血小板", "紫癜"],
            "神经系统疾病": ["神经", "脑", "脊髓", "癫痫", "头痛", "眩晕", "晕厥", "意识障碍", "中风", "脑梗死", "脑出血", "瘫痪"],
            "内分泌系统及代谢性疾病": ["内分泌", "糖尿病", "甲状腺", "垂体", "肾上腺", "代谢", "痛风", "骨质疏松", "血糖"],
            "免疫性疾病": ["免疫", "风湿", "红斑狼疮", "类风湿", "血管炎", "关节炎", "变态反应"],
            "恶性肿瘤": ["肿瘤", "癌症", "癌", "肉瘤", "白血病", "淋巴瘤", "转移", "恶性肿瘤"],
            "传染病": ["感染", "病毒", "细菌", "结核", "肝炎", "流感", "脑膜炎", "败血症", "伤寒", "痢疾", "霍乱", "鼠疫"],
            "急诊医学": ["急诊", "危象", "休克", "中毒", "创伤", "衰竭", "危重", "抢救", "急救"]
        }
        
        # 科室映射
        self.department_mapping = {
            "呼吸系统疾病": "呼吸内科",
            "心血管系统疾病": "心血管内科",
            "消化系统疾病": "消化内科",
            "泌尿系统疾病": "肾内科",
            "血液和造血系统疾病": "血液科",
            "神经系统疾病": "神经内科",
            "内分泌系统及代谢性疾病": "内分泌科",
            "免疫性疾病": "风湿免疫科",
            "恶性肿瘤": "肿瘤科",
            "传染病": "感染科",
            "急诊医学": "急诊科"
        }
        
        # 内容类型映射
        self.content_type_mapping = {
            "内科疾病鉴别诊断学": "鉴别诊断",
            "内科治疗指南": "治疗指南",
            "临床药物治疗学": "药物治疗",
            "急诊内科学": "急诊处理",
            "病理学": "病理生理"
        }
        
        # 块类型映射
        self.chunk_type_keywords = {
            "概述": ["概述", "定义", "病因", "发病机制", "病理", "流行病学", "分类", "发展简史", "简史", "历史"],
            "临床表现": ["临床表现", "症状", "体征", "症状学", "临床特征", "临床病象", "临床特点", "症状表现"],
            "诊断": ["诊断", "诊断标准", "鉴别诊断", "检查", "化验", "实验室检查", "影像学", "X线", "CT", "MRI", "超声", "心电图", "脑电图"],
            "治疗": ["治疗", "治疗方案", "治疗原则", "药物", "手术", "治疗程序", "一般治疗", "药物治疗", "对症治疗", "抗病毒", "抗菌", "抗生素", "手术", "介入"],
            "预后": ["预后", "疗效", "随访", "观察", "转归", "疗效观察", "疗效标准"],
            "预防": ["预防", "护理", "康复", "保健", "预防措施", "护理要点"]
        }
        
        # 系统类别关键词（用于过滤）
        self.system_keywords = set()
        for system, keywords in self.system_mapping.items():
            self.system_keywords.update(keywords)
    
    def _load_medical_dict(self):
        """加载医学词典"""
        medical_terms = [
            # 常见疾病
            "急性上呼吸道感染", "急性气管-支气管炎", "肺炎", "慢性阻塞性肺疾病", "哮喘",
            "心力衰竭", "高血压", "冠心病", "心律失常", "心肌梗死",
            "消化性溃疡", "胃炎", "肝硬化", "胰腺炎", "肝炎",
            "肾炎", "肾衰竭", "尿路感染",
            "贫血", "白血病", "淋巴瘤",
            "癫痫", "脑梗死", "脑出血", "帕金森病",
            "糖尿病", "甲状腺功能亢进", "痛风",
            "系统性红斑狼疮", "类风湿关节炎",
            # 常见症状
            "发热", "咳嗽", "胸痛", "呼吸困难", "水肿", "腹痛", "呕吐", "腹泻", "黄疸",
            # 检查方法
            "血常规", "尿常规", "肝功能", "肾功能", "心电图", "X线", "CT", "MRI",
            # 药物类别
            "抗生素", "降压药", "降糖药", "利尿剂", "抗凝药"
        ]
        
        for term in medical_terms:
            jieba.add_word(term)
    
    def parse_latex_file(self, file_path: Path) -> List[Dict]:
        """
        解析LaTeX文件，提取章节结构
        关键修改：先提取结构，再清理内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"    读取文件失败: {e}")
            return []
        
        # 提取章节标题（在清理LaTeX之前）
        chapter_pattern = r'\\chapter\{([^}]+)\}'
        section_pattern = r'\\section\{([^}]+)\}'
        subsection_pattern = r'\\subsection\{([^}]+)\}'
        
        # 找到所有章节位置
        chapter_matches = list(re.finditer(chapter_pattern, content))
        
        if not chapter_matches:
            print(f"    未找到章节")
            return []
        
        # 构建结构树
        chapters = []
        for i, chap_match in enumerate(chapter_matches):
            chapter_name = chap_match.group(1).strip()
            chapter_start = chap_match.end()
            chapter_end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(content)
            chapter_content = content[chapter_start:chapter_end]
            
            # 先提取小节结构（在清理LaTeX之前）
            sections = self._extract_sections_from_raw(chapter_content)
            
            # 清理LaTeX标记
            chapter_content = self._clean_latex(chapter_content)
            
            chapters.append({
                'chapter': chapter_name,
                'content': chapter_content,
                'file': file_path.name,
                'sections': sections
            })
        
        return chapters
    
    def _extract_sections_from_raw(self, raw_content: str) -> List[Dict]:
        """
        从原始LaTeX内容中提取小节结构（在清理之前）
        """
        sections = []
        section_pattern = r'\\section\{([^}]+)\}'
        subsection_pattern = r'\\subsection\{([^}]+)\}'
        
        section_matches = list(re.finditer(section_pattern, raw_content))
        
        for i, sec_match in enumerate(section_matches):
            section_name = sec_match.group(1).strip()
            section_start = sec_match.end()
            section_end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(raw_content)
            section_content = raw_content[section_start:section_end]
            
            # 提取子小节（在清理之前）
            subsections = self._extract_subsections_from_raw(section_content)
            
            # 清理小节内容
            section_content = self._clean_latex(section_content)
            
            sections.append({
                'section': section_name,
                'content': section_content,
                'subsections': subsections
            })
        
        return sections
    
    def _extract_subsections_from_raw(self, raw_section_content: str) -> List[Dict]:
        """
        从原始LaTeX内容中提取子小节结构（在清理之前）
        """
        subsections = []
        subsection_pattern = r'\\subsection\{([^}]+)\}'
        
        subsection_matches = list(re.finditer(subsection_pattern, raw_section_content))
        
        for i, sub_match in enumerate(subsection_matches):
            subsection_name = sub_match.group(1).strip()
            subsection_start = sub_match.end()
            subsection_end = subsection_matches[i + 1].start() if i + 1 < len(subsection_matches) else len(raw_section_content)
            subsection_content = raw_section_content[subsection_start:subsection_end]
            
            # 清理子小节内容
            subsection_content = self._clean_latex(subsection_content)
            
            subsections.append({
                'subsection': subsection_name,
                'content': subsection_content
            })
        
        return subsections
    
    def _clean_latex(self, text: str) -> str:
        """
        清理LaTeX标记，保留纯文本
        """
        # 移除图片引用
        text = re.sub(r'\\includegraphics[^}]+\}', '', text)
        text = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', text, flags=re.DOTALL)
        
        # 移除表格
        text = re.sub(r'\\begin\{table\}.*?\\end\{table\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}', '', text, flags=re.DOTALL)
        
        # 移除引用
        text = re.sub(r'\\ref\{[^}]+\}', '', text)
        text = re.sub(r'\\cite\{[^}]+\}', '', text)
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\{[a-zA-Z0-9_\-]+\}', '', text)
        
        # 移除LaTeX命令但保留内容
        text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}\{([^}]*)\}', r'\1 \2', text)
        
        # 移除特殊符号
        text = re.sub(r'\\textasciitilde', '~', text)
        text = re.sub(r'\\textbackslash', '\\\\', text)
        text = re.sub(r'&', ' ', text)
        text = re.sub(r'\\%', '%', text)
        text = re.sub(r'\\$', '$', text)
        text = re.sub(r'\\#', '#', text)
        text = re.sub(r'\\_', '_', text)
        text = re.sub(r'\\~', '~', text)
        text = re.sub(r'\\^', '^', text)
        
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def classify_system(self, text: str, chapter_name: str = "") -> str:
        """
        根据文本内容分类系统
        """
        # 首先检查章节名称
        for system, keywords in self.system_mapping.items():
            for keyword in keywords:
                if keyword in chapter_name:
                    return system
        
        # 然后检查文本内容
        for system, keywords in self.system_mapping.items():
            for keyword in keywords:
                if keyword in text:
                    return system
        
        return "其他"
    
    def classify_department(self, system_category: str) -> str:
        """
        根据系统分类映射到科室
        """
        return self.department_mapping.get(system_category, "其他科室")
    
    def classify_content_type(self, source_dir: str) -> str:
        """
        根据源目录分类内容类型
        """
        for dir_name, content_type in self.content_type_mapping.items():
            if dir_name in source_dir:
                return content_type
        return "其他"
    
    def classify_chunk_type(self, section_name: str, content: str, chapter_name: str = "") -> str:
        """
        分类块类型
        """
        combined_text = (chapter_name + " " + section_name + " " + content[:500]).lower()
        
        for chunk_type, keywords in self.chunk_type_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return chunk_type
        
        if "治疗" in section_name or "方案" in section_name:
            return "治疗"
        elif "诊断" in section_name or "鉴别" in section_name:
            return "诊断"
        elif "症状" in section_name or "表现" in section_name:
            return "临床表现"
        elif "概述" in section_name or "定义" in section_name:
            return "概述"
        elif "预后" in section_name or "随访" in section_name:
            return "预后"
        elif "预防" in section_name or "护理" in section_name:
            return "预防"
        
        if "治疗" in content[:200] or "药物" in content[:200]:
            return "治疗"
        elif "诊断" in content[:200] or "检查" in content[:200]:
            return "诊断"
        elif "症状" in content[:200] or "体征" in content[:200]:
            return "临床表现"
        
        return "其他"
    
    def extract_disease_name(self, chapter_name: str, section_name: str, system_category: str) -> str:
        """
        提取疾病名称 - 改进版
        避免把系统类别当作疾病名称
        """
        # 系统类别关键词，需要过滤
        system_keywords = {"疾病", "系统", "治疗", "药物", "诊断", "概述", "原则", "方法", "指南", "学"}
        
        # 从章节名称中提取
        disease_patterns = [
            r'急性(.+炎)',
            r'慢性(.+炎)',
            r'(.+)炎',
            r'(.+)病',
            r'(.+)综合征',
            r'(.+)症',
            r'(.+)衰竭',
            r'(.+)梗死',
            r'(.+)出血',
            r'(.+)损伤',
        ]
        
        for pattern in disease_patterns:
            match = re.search(pattern, chapter_name)
            if match:
                disease = match.group(0)
                # 过滤掉系统类别关键词
                if disease not in system_keywords and disease != system_category:
                    # 进一步检查是否包含系统关键词
                    contains_system_keyword = any(keyword in disease for keyword in self.system_keywords)
                    if not contains_system_keyword:
                        return disease
        
        # 从小节名称中提取
        for pattern in disease_patterns:
            match = re.search(pattern, section_name)
            if match:
                disease = match.group(0)
                if disease not in system_keywords and disease != system_category:
                    contains_system_keyword = any(keyword in disease for keyword in self.system_keywords)
                    if not contains_system_keyword:
                        return disease
        
        return ""
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> str:
        """
        使用jieba提取关键词
        """
        if not text or len(text) < 10:
            return ""
        
        try:
            keywords = jieba.analyse.extract_tags(text, topK=max_keywords, withWeight=False)
            return ','.join(keywords)
        except:
            words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
            word_freq = defaultdict(int)
            
            for word in words:
                word_freq[word] += 1
            
            stop_words = {'的', '是', '在', '有', '和', '与', '或', '等', '可', '应', '需', '能', '会', '为', '而', '但', '因', '如', '及', '其', '这', '那', '此', '本', '该', '各', '某', '多', '少', '大', '小', '高', '低', '新', '老', '男', '女', '老', '幼', '急', '慢'}
            
            filtered_words = [(word, freq) for word, freq in word_freq.items() if word not in stop_words and freq > 1]
            filtered_words.sort(key=lambda x: x[1], reverse=True)
            
            keywords = [word for word, freq in filtered_words[:max_keywords]]
            return ','.join(keywords)
    
    def chunk_text(self, text: str, max_chars: int = 800) -> List[str]:
        """
        将文本分块，保持语义完整性
        """
        if not text or len(text) < 50:
            return []
        
        chunks = []
        sentences = re.split(r'[。！？；\n]', text)
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def process_directory(self, output_csv: str = "medical_chunks_v2.csv"):
        """
        处理整个数据目录
        """
        all_chunks = []
        chunk_counter = 0
        
        for subdir in self.data_dir.iterdir():
            if not subdir.is_dir() or subdir.name.startswith('.'):
                continue
            
            content_dir = subdir / "content"
            if not content_dir.exists():
                continue
            
            print(f"处理目录: {subdir.name}")
            
            content_type = self.classify_content_type(subdir.name)
            
            tex_files = sorted(content_dir.glob("*.tex"))
            for tex_file in tex_files:
                print(f"  处理文件: {tex_file.name}")
                
                chapters = self.parse_latex_file(tex_file)
                
                for chapter in chapters:
                    chapter_name = chapter['chapter']
                    system_category = self.classify_system(chapter['content'], chapter_name)
                    department = self.classify_department(system_category)
                    
                    # 处理章节内容（没有小节的情况）
                    if not chapter['sections']:
                        chapter_chunks = self.chunk_text(chapter['content'])
                        
                        for idx, chunk_text in enumerate(chapter_chunks):
                            chunk_counter += 1
                            
                            keywords = self.extract_keywords(chunk_text)
                            disease_name = self.extract_disease_name(chapter_name, "", system_category)
                            
                            metadata = ChunkMetadata(
                                content=chunk_text,
                                source_file=str(tex_file.relative_to(self.data_dir)),
                                chapter=chapter_name,
                                section="",
                                subsection="",
                                department=department,
                                system_category=system_category,
                                content_type=content_type,
                                chunk_type=self.classify_chunk_type(chapter_name, chunk_text, chapter_name),
                                hierarchy_level=1,
                                keywords=keywords,
                                char_count=len(chunk_text),
                                token_count=len(chunk_text) // 2
                            )
                            
                            all_chunks.append(asdict(metadata))
                    
                    # 处理小节
                    for section in chapter['sections']:
                        section_name = section['section']
                        
                        section_chunks = self.chunk_text(section['content'])
                        
                        for idx, chunk_text in enumerate(section_chunks):
                            chunk_counter += 1
                            
                            keywords = self.extract_keywords(chunk_text)
                            disease_name = self.extract_disease_name(chapter_name, section_name, system_category)
                            
                            metadata = ChunkMetadata(
                                content=chunk_text,
                                source_file=str(tex_file.relative_to(self.data_dir)),
                                chapter=chapter_name,
                                section=section_name,
                                subsection="",
                                department=department,
                                system_category=system_category,
                                content_type=content_type,
                                chunk_type=self.classify_chunk_type(section_name, chunk_text, chapter_name),
                                hierarchy_level=2,
                                keywords=keywords,
                                char_count=len(chunk_text),
                                token_count=len(chunk_text) // 2
                            )
                            
                            all_chunks.append(asdict(metadata))
                        
                        # 处理子小节
                        for subsection in section['subsections']:
                            subsection_name = subsection['subsection']
                            subsection_chunks = self.chunk_text(subsection['content'])
                            
                            for idx, chunk_text in enumerate(subsection_chunks):
                                chunk_counter += 1
                                
                                keywords = self.extract_keywords(chunk_text)
                                disease_name = self.extract_disease_name(chapter_name, subsection_name, system_category)
                                
                                metadata = ChunkMetadata(
                                    content=chunk_text,
                                    source_file=str(tex_file.relative_to(self.data_dir)),
                                    chapter=chapter_name,
                                    section=section_name,
                                    subsection=subsection_name,
                                    department=department,
                                    system_category=system_category,
                                    content_type=content_type,
                                    chunk_type=self.classify_chunk_type(subsection_name, chunk_text, chapter_name),
                                    hierarchy_level=3,
                                    keywords=keywords,
                                    char_count=len(chunk_text),
                                    token_count=len(chunk_text) // 2
                                )
                                
                                all_chunks.append(asdict(metadata))
        
        self._write_csv(all_chunks, output_csv)
        print(f"\n处理完成！共生成 {len(all_chunks)} 个数据块")
        print(f"CSV文件已保存到: {output_csv}")
        
        self._print_statistics(all_chunks)
    
    def _write_csv(self, chunks: List[Dict], output_csv: str):
        """将数据块写入CSV文件"""
        if not chunks:
            print("没有数据块可写入")
            return

        # 确保所有数据块都有相同的字段
        fieldnames = [
            'content', 'source_file', 'chapter', 'section', 'subsection',
            'department', 'system_category', 'content_type',
            'chunk_type', 'hierarchy_level', 'parent_chunk', 'keywords',
            'char_count', 'token_count'
        ]
        
        # 移除chunk_id字段（如果存在）
        for chunk in chunks:
            if 'chunk_id' in chunk:
                del chunk['chunk_id']
        
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(chunks)
    
    def _print_statistics(self, chunks: List[Dict]):
        """
        打印统计信息
        """
        print("\n=== 数据统计 ===")
        
        system_stats = defaultdict(int)
        for chunk in chunks:
            system_stats[chunk['system_category']] += 1
        
        print("\n按系统分类:")
        for system, count in sorted(system_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {system}: {count} 块")
        
        department_stats = defaultdict(int)
        for chunk in chunks:
            department_stats[chunk['department']] += 1
        
        print("\n按科室分类:")
        for department, count in sorted(department_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {department}: {count} 块")
        
        content_type_stats = defaultdict(int)
        for chunk in chunks:
            content_type_stats[chunk['content_type']] += 1
        
        print("\n按内容类型:")
        for content_type, count in sorted(content_type_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {content_type}: {count} 块")
        
        chunk_type_stats = defaultdict(int)
        for chunk in chunks:
            chunk_type_stats[chunk['chunk_type']] += 1
        
        print("\n按块类型:")
        for chunk_type, count in sorted(chunk_type_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {chunk_type}: {count} 块")
        
        section_count = sum(1 for chunk in chunks if chunk['section'])
        subsection_count = sum(1 for chunk in chunks if chunk['subsection'])
        print(f"\n有section信息的块: {section_count} / {len(chunks)} ({section_count/len(chunks)*100:.1f}%)")
        print(f"有subsection信息的块: {subsection_count} / {len(chunks)} ({subsection_count/len(chunks)*100:.1f}%)")
        
        char_counts = [chunk['char_count'] for chunk in chunks if chunk['char_count'] > 0]
        if char_counts:
            print(f"\n块大小统计:")
            print(f"  平均: {sum(char_counts)/len(char_counts):.1f} 字符")
            print(f"  最小: {min(char_counts)} 字符")
            print(f"  最大: {max(char_counts)} 字符")


def main():
    """主函数"""
    data_dir = r"d:\LangGraph\data"
    output_csv = r"d:\LangGraph\data\数据\medical_chunks_v2.csv"
    
    preprocessor = FixedMedicalDataPreprocessorV2(data_dir)
    preprocessor.process_directory(output_csv)


if __name__ == "__main__":
    main()
