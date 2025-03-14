import os
import re
import time
import fitz
import requests
from pathlib import Path
import argparse
import hashlib
from PIL import Image
import pytesseract
from typing import Optional, Tuple, List

class PaperProcessor:
    def __init__(self, api_key: str, root_dir: str, detail_level: str = "full"):
        self.api_key = api_key
        self.root_dir = Path(root_dir)
        self.detail_level = detail_level
        self.cache_dir = self.root_dir / ".paper_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # 初始化术语词典
        self.term_dict = {
            "SOP": "标准操作程序 (Standard Operating Procedure)",
            "LLM": "大语言模型 (Large Language Model)",
            "ICL": "上下文学习 (In-Context Learning)",
            "SFT": "监督微调 (Supervised Fine-Tuning)"
        }
        
        # 加载已处理文件记录
        self.processed_record_file = self.cache_dir / "processed_files.txt"
        self._load_processed_records()

    def _load_cache(self, pdf_path: Path) -> Optional[Tuple[str, str, str, str]]:
        """加载缓存"""
        file_hash = hashlib.md5(pdf_path.read_bytes()).hexdigest()
        cache_file = self.cache_dir / f"{file_hash}.cache"
        
        if cache_file.exists():
            cached_content = cache_file.read_text(encoding="utf-8").split("\n---\n")
            if len(cached_content) == 4:
                return cached_content[0], cached_content[1], cached_content[2], cached_content[3]
        return None

    def _save_cache(self, pdf_path: Path, text: str, summary: str, folder_name: str, figures: str):
        """保存缓存"""
        file_hash = hashlib.md5(pdf_path.read_bytes()).hexdigest()
        cache_file = self.cache_dir / f"{file_hash}.cache"
        cache_file.write_text(f"{text}\n---\n{summary}\n---\n{folder_name}\n---\n{figures}", encoding="utf-8")

    def extract_content(self, pdf_path: Path) -> Tuple[str, str]:
        """提取文本和图表信息"""
        text = self._extract_text(pdf_path)
        figures = self._extract_figures(pdf_path)
        return text, figures

    def _extract_text(self, pdf_path: Path) -> str:
        """提取格式化文本"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text("text").replace("\ufb01", "fi")
            return self._replace_terms(text[:100000])
        except Exception as e:
            raise RuntimeError(f"文本提取失败: {str(e)}")

    def _replace_terms(self, text: str) -> str:
        """替换专业术语为中文解释"""
        for term, explanation in self.term_dict.items():
            text = re.sub(r'\b' + term + r'\b', explanation, text)
        return text

    def _extract_figures(self, pdf_path: Path) -> str:
        """提取并识别图表信息"""
        figure_text = []
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # OCR识别
                    text = pytesseract.image_to_string(image, lang='eng+chi_sim')
                    if text.strip():
                        figure_text.append(f"图 {page_num+1}.{img_index+1}:\n{text}")
                    
                    # 保存原始图片
                    img_dir = self.cache_dir / "figures"
                    img_dir.mkdir(exist_ok=True)
                    image.save(img_dir / f"page{page_num}_fig{img_index}.png")
                    
            return "\n\n".join(figure_text)
        except Exception as e:
            print(f"图表识别警告: {str(e)}")
            return ""

    def generate_summary(self, text: str, figures: str, retry: int = 3) -> Tuple[str, str]:
        """生成增强版论文总结"""
        system_prompt = """作为资深科研助理，请用中文生成结构化论文总结，要求包含以下内容：

1. **核心贡献**（3-5个创新点）
2. **方法细节**（算法伪代码+数学公式）
3. **实验结果**（量化指标对比）
4. **图表分析**（关键图表说明）
5. **应用价值**
"""
        # 将文本分成多个块进行处理，每块最大25000字符
        max_chunk_size = 25000
        text_chunks = self._split_text_into_chunks(text, max_chunk_size)
        print(f"文本已分割为 {len(text_chunks)} 个块进行处理")
        
        # 顺序处理每个文本块
        summaries = []
        for i, chunk in enumerate(text_chunks):
            print(f"处理文本块 {i+1}/{len(text_chunks)}...")
            
            # 为每个块添加上下文信息
            chunk_content = f"论文内容(第{i+1}部分，共{len(text_chunks)}部分)：\n{chunk}"
            if i == len(text_chunks) - 1 and figures:  # 只在最后一个块添加图表信息
                chunk_content += f"\n\n图表信息：\n{figures}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk_content}
            ]

            # 尝试API请求
            chunk_summary = self._make_api_request(messages, retry)
            if chunk_summary:
                summaries.append(chunk_summary)
                print(f"文本块 {i+1}/{len(text_chunks)} 处理完成")
            else:
                print(f"警告：第{i+1}块处理失败")
        
        # 如果所有块都处理失败，返回空结果
        if not summaries:
            return "", "API请求失败"
        
        # 合并所有块的摘要
        combined_summary = "\n\n".join(summaries)
        
        # 提取文件夹名称
        folder_match = re.search(r'文件夹名称：(.+)', combined_summary)
        folder_name = re.sub(r'[\\/:*?"<>|]', '', folder_match.group(1).strip()) if folder_match else "未命名论文"
        summary = re.sub(r'文件夹名称：.+', '', combined_summary).strip()
        
        return summary, folder_name
    
    def _split_text_into_chunks(self, text: str, max_size: int) -> List[str]:
        """将文本分割成多个块"""
        # 如果文本小于最大块大小，直接返回
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        # 按段落分割文本
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            # 如果当前段落加上当前块超过最大大小，保存当前块并开始新块
            if len(current_chunk) + len(para) + 2 > max_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = para
            else:
                # 否则，将段落添加到当前块
                if current_chunk:
                    current_chunk += '\n\n' + para
                else:
                    current_chunk = para
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def _make_api_request(self, messages: List[dict], retry: int = 3) -> str:
        """发送API请求并处理响应"""
        for attempt in range(retry):
            try:
                print(f"API请求尝试 {attempt+1}/{retry}...")
                response = requests.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "deepseek-reasoner",
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 3000
                    },
                    timeout=120  # 增加超时时间到120秒
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                
                elif response.status_code == 429:
                    sleep_time = 2 ** attempt
                    print(f"速率限制，等待 {sleep_time}s 后重试...")
                    time.sleep(sleep_time)
                
                else:
                    print(f"API错误: {response.status_code} - {response.text}")
                    if attempt < retry - 1:
                        sleep_time = 5 + 2 ** attempt
                        print(f"等待 {sleep_time}s 后重试...")
                        time.sleep(sleep_time)
                    else:
                        raise RuntimeError(f"API错误: {response.status_code} - {response.text}")

            except (requests.exceptions.RequestException, KeyError) as e:
                print(f"请求异常: {str(e)}")
                if attempt < retry - 1:
                    sleep_time = 5 + 2 ** attempt
                    print(f"等待 {sleep_time}s 后重试...")
                    time.sleep(sleep_time)
                else:
                    print(f"最终失败: {str(e)}")
                    return ""

        return ""

    def process_paper(self, pdf_path: Path):
        """处理单篇论文"""
        try:
            # 检查是否已处理过
            file_hash = hashlib.md5(pdf_path.read_bytes()).hexdigest()
            if file_hash in self.processed_files:
                print(f"跳过已处理文件: {pdf_path.name}")
                return
                
            print(f"\n处理中: {pdf_path.name}")
            
            # 检查缓存
            if cached := self._load_cache(pdf_path):
                text, summary, folder_name, figures = cached
                print("从缓存加载...")
            else:
                text, figures = self.extract_content(pdf_path)
                summary, folder_name = self.generate_summary(text, figures)
                self._save_cache(pdf_path, text, summary, folder_name, figures)

            # 创建目标目录
            target_dir = pdf_path.parent / folder_name
            suffix = 1
            while target_dir.exists():
                target_dir = pdf_path.parent / f"{folder_name}_{suffix}"
                suffix += 1
            target_dir.mkdir(exist_ok=True)

            # 移动并保存文件
            new_pdf = target_dir / pdf_path.name
            pdf_path.rename(new_pdf)
            
            # 保存增强版总结
            md_content = self._format_summary(summary, figures)
            (target_dir / f"{pdf_path.stem}_详细总结.md").write_text(md_content, encoding="utf-8")
            
            # 记录已处理文件
            self._mark_as_processed(file_hash)
            
            print(f"已保存到：{target_dir}")
        except Exception as e:
            print(f"处理失败 [{pdf_path.name}]: {str(e)}")

    def _format_summary(self, summary: str, figures: str) -> str:
        """格式化最终输出"""
        content = []
        if figures:
            content.append("## 图表分析\n" + figures.replace("图 ", "### 图 "))
        
        content.insert(0, summary)  # 保持总结在前
        
        return "\n\n---\n\n".join(content)

    def _load_processed_records(self):
        """加载已处理文件记录"""
        if self.processed_record_file.exists():
            with open(self.processed_record_file, 'r') as f:
                self.processed_files = set(line.strip() for line in f if line.strip())
            print(f"已加载 {len(self.processed_files)} 个已处理文件记录")
        else:
            self.processed_files = set()
    
    def _mark_as_processed(self, file_hash: str):
        """标记文件为已处理"""
        self.processed_files.add(file_hash)
        with open(self.processed_record_file, 'a') as f:
            f.write(f"{file_hash}\n")

    def run(self):
        """顺序处理所有PDF"""
        # 收集所有PDF文件路径
        pdf_files = list(self.root_dir.glob("**/*.pdf"))
        print(f"发现 {len(pdf_files)} 个PDF文件")
        
        # 顺序处理每个PDF文件
        for pdf_path in pdf_files:
            try:
                self.process_paper(pdf_path)
                # 每处理完一个文件后等待一段时间，避免API限制
                time.sleep(2)
            except Exception as e:
                print(f"处理失败 [{pdf_path.name}]: {str(e)}")
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="论文自动处理系统",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--api_key",
        required=True,
        help="DeepSeek API密钥"
    )
    parser.add_argument(
        "--root_dir",
        required=True,
        help="PDF根目录路径"
    )
    parser.add_argument(
        "--detail",
        choices=["minimal", "standard", "full"],
        default="full",
        help="总结详细程度"
    )
    
    args = parser.parse_args()
    
    processor = PaperProcessor(
        api_key=args.api_key,
        root_dir=args.root_dir,
        detail_level=args.detail
    )
    processor.run()

