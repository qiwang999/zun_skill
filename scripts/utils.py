"""工具类：语录构造、HTML 清洗"""

import hashlib
import re


class QuoteFactory:
    """语录记录工厂：构造纯回答和提问-回答对"""

    @staticmethod
    def make_quote(text: str, source: str, quote_type: str = "interview_answer") -> dict:
        """构造一条语录记录"""
        return {
            "id": hashlib.md5(text.encode()).hexdigest()[:12],
            "text": text,
            "source": source,
            "type": quote_type,
        }

    @staticmethod
    def make_qa_pair(question: str, answer: str, source: str) -> dict:
        """构造一条提问-回答对记录

        question: 提问者的原话（非 ZUN 说的）
        answer: ZUN 的回答
        """
        qa_text = f"{question} → {answer}"
        return {
            "id": hashlib.md5(qa_text.encode()).hexdigest()[:12],
            "question": question,
            "answer": answer,
            "text": answer,  # 兼容：text 字段存答案，用于 zun_quotes collection
            "source": source,
            "type": "qa_pair",
        }


# 模块级便捷实例，供旧代码兼容
_factory = QuoteFactory()
make_quote = _factory.make_quote
make_qa_pair = _factory.make_qa_pair


class HtmlCleaner:
    """HTML 清洗工具：提取正文、去除标签"""

    @staticmethod
    def extract_mw_body(content: str) -> str:
        """提取 mw-parser-output 内容，避免导航栏干扰"""
        mw_match = re.search(
            r'<div class="mw-parser-output">(.*?)<div class="printfooter"',
            content, re.DOTALL,
        )
        return mw_match.group(1) if mw_match else content

    @staticmethod
    def clean_html(html: str) -> str:
        """清理 HTML 标签，保留换行符用于段落分割"""
        text = re.sub(r'<br\s*/?>', '\n', html)
        text = re.sub(r'</p>', '\n', text)
        text = re.sub(r'</div>', '\n', text)
        text = re.sub(r'</li>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'[^\S\n]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


# 模块级便捷实例
_cleaner = HtmlCleaner()
extract_mw_body = _cleaner.extract_mw_body
clean_html = _cleaner.clean_html
