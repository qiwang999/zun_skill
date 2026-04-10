"""语录解析器：从不同格式的访谈源中提取 ZUN 语录（含提问-回答对）

所有解析逻辑封装在 InterviewParser 类中，支持：
- 本地纯语录文件
- THBWiki 表格/dt-dd/通用表格/段落/叙述体/纯文本
- Markdown 格式访谈
- 二轩目广播
"""

import re

from config import ZUN_NAMES, LOCAL_QUOTES, NIKENME_MIN_QUOTE_LEN
from utils import QuoteFactory, HtmlCleaner


class InterviewParser:
    """访谈解析器：从各种格式提取 ZUN 语录和提问-回答对"""

    def __init__(self):
        self.factory = QuoteFactory()
        self.cleaner = HtmlCleaner()

    # ── 本地语录 ────────────────────────────────────────

    def parse_local_quotes(self) -> list:
        """从已有的 quotes/ 文件解析语录（纯语录，无对话上下文）"""
        quotes = []
        for filepath in LOCAL_QUOTES:
            if not filepath.exists():
                continue
            content = filepath.read_text(encoding="utf-8")
            source = filepath.stem
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith('- "') or line.startswith('- \u201c'):
                    text = line[3:].strip()
                    if text.endswith('\u201d') or text.endswith('"'):
                        text = text[:-1]
                    if len(text) > 5:
                        quotes.append(self.factory.make_quote(text, f"local-{source}", "quote"))
        return quotes

    # ── THBWiki 表格格式 ─────────────────────────────────

    def parse_thbwiki_table(self, content: str, source_id: str) -> list:
        """解析 THBWiki 表格格式的访谈

        支持三种表格结构：
        1. <tr class="tt-content"> + <td class="tt-char"> + <td class="tt-zh">
        2. 同上，但说话人缩写为 "Z" 或 "ZUN（以下，Z）"
        3. <tr> + <td class="tt-char tt-type-dialogue"> 结构
        """
        quotes = []
        all_rows = self._extract_thbwiki_table_rows(content)
        self._extract_qa_from_rows(all_rows, source_id, quotes, merge_consecutive=False)
        return quotes

    def _extract_thbwiki_table_rows(self, content: str) -> list:
        """从 THBWiki 表格中提取行数据"""
        all_rows = []
        seen_texts = set()

        def _add_row(speaker, is_zun, text):
            text = text.strip()
            if len(text) > 5 and text not in seen_texts:
                seen_texts.add(text)
                all_rows.append({"speaker": speaker, "is_zun": is_zun, "text": text})

        # 方法1: tt-content 行（最常见格式）
        tr_pattern = re.compile(r'<tr[^>]*class="tt-content"[^>]*>(.*?)</tr>', re.DOTALL)
        for tr_match in tr_pattern.finditer(content):
            tr_html = tr_match.group(1)
            char_pattern = re.compile(r'<td[^>]*class="tt-char[^"]*"[^>]*>(.*?)</td>', re.DOTALL)
            char_matches = char_pattern.findall(tr_html)
            speaker = self.cleaner.clean_html(char_matches[0]).strip() if char_matches else ""
            is_zun = any(self.cleaner.clean_html(cm).strip() in ZUN_NAMES for cm in char_matches)
            zh_pattern = re.compile(r'<td[^>]*class="tt-zh"[^>]*>(.*?)</td>', re.DOTALL)
            zh_match = zh_pattern.search(tr_html)
            if zh_match:
                zh_text = self.cleaner.clean_html(zh_match.group(1))
                _add_row(speaker, is_zun, zh_text)

        # 方法2: tt-type-dialogue div 格式（如 shujin-no-kotodama）
        # 格式：<div class="tt-char tt-type-dialogue">说话人</div><div class="tt-zh tt-type-dialogue">内容</div>
        dialogue_divs = re.findall(
            r'<div[^>]*class="tt-char\s+tt-type-dialogue"[^>]*>(.*?)</div>\s*'
            r'<div[^>]*class="tt-zh\s+tt-type-dialogue"[^>]*>(.*?)</div>',
            content, re.DOTALL
        )
        for char_html, zh_html in dialogue_divs:
            speaker = self.cleaner.clean_html(char_html).strip()
            is_zun = speaker in ZUN_NAMES or speaker == "ZUN"
            zh_text = self.cleaner.clean_html(zh_html)
            _add_row(speaker, is_zun, zh_text)

        return all_rows

    # ── THBWiki 表格 + tt-narrator 格式 ────────────────────

    def parse_thbwiki_narrator(self, content: str, source_id: str) -> list:
        """解析 THBWiki 表格格式，同时提取 tt-narrator 行中 ZUN 的发言

        适用于 gairai-shinpireku 等页面：ZUN 的发言在 tt-narrator 行中，
        而非 tt-char 行（因为 ZUN 不是被采访者，而是以旁白/叙述者身份出现）
        """
        quotes = []
        # 先提取标准 tt-content 行
        all_rows = self._extract_thbwiki_table_rows(content)

        # 再提取 tt-narrator 行中的 ZUN 发言
        narrator_rows = self._extract_narrator_rows(content)
        all_rows.extend(narrator_rows)

        self._extract_qa_from_rows(all_rows, source_id, quotes, merge_consecutive=False)
        return quotes

    def _extract_narrator_rows(self, content: str) -> list:
        """从 tt-narrator 行中提取 ZUN 发言

        tt-narrator 格式：<tr class="tt-narrator"><td class="tt-char">ZUN</td><td class="tt-zh">内容</td></tr>
        """
        rows = []
        narrator_pattern = re.compile(r'<tr[^>]*class="tt-narrator"[^>]*>(.*?)</tr>', re.DOTALL)
        for tr_match in narrator_pattern.finditer(content):
            tr_html = tr_match.group(1)
            char_pattern = re.compile(r'<td[^>]*class="tt-char[^"]*"[^>]*>(.*?)</td>', re.DOTALL)
            char_matches = char_pattern.findall(tr_html)
            speaker = self.cleaner.clean_html(char_matches[0]).strip() if char_matches else ""
            is_zun = any(self.cleaner.clean_html(cm).strip() in ZUN_NAMES for cm in char_matches)
            zh_pattern = re.compile(r'<td[^>]*class="tt-zh"[^>]*>(.*?)</td>', re.DOTALL)
            zh_match = zh_pattern.search(tr_html)
            if zh_match and is_zun:
                zh_text = self.cleaner.clean_html(zh_match.group(1))
                if len(zh_text.strip()) > 5:
                    rows.append({"speaker": speaker, "is_zun": is_zun, "text": zh_text.strip()})
        return rows

    # ── THBWiki dt/dd 格式 ──────────────────────────────

    def parse_thbwiki_dtdd(self, content: str, source_id: str) -> list:
        """解析 THBWiki <dl>/<dt>/<dd> 格式的访谈

        同时提取 h2/h3 标题作为话题上下文（用于没有明确提问者的段落）
        """
        quotes = []
        body = self.cleaner.extract_mw_body(content)

        # 先提取标题作为话题分隔
        headlines = list(re.finditer(
            r'<h[23][^>]*>\s*<span[^>]*class="mw-headline"[^>]*>(.*?)</span>', body, re.DOTALL
        ))

        # 建立 位置→标题 的映射
        topic_map = {}
        for hl in headlines:
            topic_text = self.cleaner.clean_html(hl.group(1)).strip()
            if topic_text and len(topic_text) > 2:
                topic_map[hl.start()] = topic_text

        # 排序位置，用于二分查找
        sorted_positions = sorted(topic_map.keys())

        def _find_topic(pos):
            """找到 pos 之前最近的标题"""
            if not sorted_positions:
                return None
            # 简单线性查找（标题数量少，性能没问题）
            best = None
            for p in sorted_positions:
                if p <= pos:
                    best = topic_map[p]
                else:
                    break
            return best

        # 提取 dt/dd 对
        dt_dd_pattern = re.compile(r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>', re.DOTALL)
        rows = []
        for m in dt_dd_pattern.finditer(body):
            dt_html, dd_html = m.group(1), m.group(2)
            speaker = self.cleaner.clean_html(dt_html).strip()
            text = self.cleaner.clean_html(dd_html)
            is_zun = speaker in ZUN_NAMES
            if len(text) > 5:
                # 找到这个 dt/dd 之前最近的标题作为话题
                topic = _find_topic(m.start())
                rows.append({
                    "speaker": speaker,
                    "is_zun": is_zun,
                    "text": text,
                    "topic": topic,  # 额外字段，后续使用
                })

        # 不合并连续行——每条 dt/dd 天然是一条独立发言
        # 用话题作为"提问"组成 QA pair
        for row in rows:
            if row["is_zun"]:
                answer = re.sub(r'\s+', ' ', row["text"]).strip()
                if len(answer) < 10:
                    continue
                topic = row.get("topic")
                if topic and not topic.startswith("STAGE") and len(topic) > 3:
                    quotes.append(self.factory.make_qa_pair(
                        f"关于{topic}", answer, source_id
                    ))
                else:
                    quotes.append(self.factory.make_quote(answer, source_id))
            elif row["speaker"] and row["text"]:
                # 非 ZUN 发言，跳过（但可以保留给未来的提问者提取）
                pass

        return quotes

    # ── 通用表格格式 ────────────────────────────────────

    def parse_generic_table(self, content: str, source_id: str) -> list:
        """解析通用表格格式的访谈（无 tt-content/tt-char class）"""
        quotes = []
        body = self.cleaner.extract_mw_body(content)
        rows = self._extract_generic_table_rows(body)
        self._extract_qa_from_rows(rows, source_id, quotes)
        return quotes

    def _extract_generic_table_rows(self, body: str) -> list:
        """从通用表格中提取行数据"""
        rows = []
        tables = re.findall(r'<table[^>]*>(.*?)</table>', body, re.DOTALL)
        for table_html in tables:
            trs = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
            for row in trs:
                cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL)
                if len(cells) < 2:
                    continue
                speaker = self.cleaner.clean_html(cells[0]).strip()
                zh_text = self.cleaner.clean_html(cells[-1])
                if len(zh_text) > 5:
                    rows.append({"speaker": speaker, "is_zun": speaker in ZUN_NAMES, "text": zh_text})
        return rows

    # ── <p>ZUN：xxx</p> 段落格式 ────────────────────────

    def parse_p_zun_format(self, content: str, source_id: str) -> list:
        """解析 <p>ZUN：xxx</p> 段落格式的访谈"""
        quotes = []
        body = self.cleaner.extract_mw_body(content)
        rows = self._extract_p_zun_rows(body)
        self._extract_qa_from_rows(rows, source_id, quotes)
        return quotes

    def _extract_p_zun_rows(self, body: str) -> list:
        """从 <p> 段落中提取行数据"""
        p_tags = re.findall(r'<p>(.*?)</p>', body, re.DOTALL)
        ZUN_PREFIX = re.compile(r'^(ZUN|Z|ZUN氏|神主|ZUN先生)[：:]\s*')
        OTHER_SPEAKER = re.compile(
            r'^(——|―|博之|记者|采访者|问[：:]|Q[：:]|EDITOR|小此木|海原|azmaya)'
        )
        rows = []
        current_speaker = None
        current_texts = []

        def _flush():
            nonlocal current_speaker, current_texts
            if current_speaker and current_texts:
                text = " ".join(current_texts).strip()
                if len(text) > 5:
                    rows.append({
                        "speaker": current_speaker,
                        "is_zun": current_speaker in ZUN_NAMES or current_speaker == "ZUN",
                        "text": text,
                    })
            current_speaker = None
            current_texts = []

        for p_html in p_tags:
            p_text = self.cleaner.clean_html(p_html).strip()
            if not p_text:
                continue
            zun_match = ZUN_PREFIX.match(p_text)
            other_match = OTHER_SPEAKER.match(p_text)
            if zun_match:
                _flush()
                current_speaker = "ZUN"
                after = ZUN_PREFIX.sub('', p_text)
                current_texts = [after] if after else []
            elif other_match:
                _flush()
                speaker_name = other_match.group(1)
                after = OTHER_SPEAKER.sub('', p_text)
                current_speaker = speaker_name
                current_texts = [after] if after else []
            elif current_speaker:
                current_texts.append(p_text)

        _flush()
        return rows

    # ── 叙述体引号格式 ──────────────────────────────────

    def parse_narrative_quotes(self, content: str, source_id: str) -> list:
        """解析叙述体文章中 ZUN 的原话（引号内），无明确提问者，只产出纯回答"""
        quotes = []
        body = self.cleaner.extract_mw_body(content)
        text = self.cleaner.clean_html(body)
        seen = set()

        def _add_if_new(q, min_len=10):
            if len(q) > min_len and q not in seen:
                seen.add(q)
                quotes.append(self.factory.make_quote(q, source_id))

        # 模式1：ZUN...说...「xxx」
        for q in re.findall(
            r'(?:ZUN|神主|太田)[^。]*?(?:说道|说|所说|谈到|表示|提到|讲述)[^「]*?「([^」]+)」', text
        ):
            _add_if_new(q)

        # 模式2：ZUN：「xxx」
        for q in re.findall(r'(?:ZUN|神主)[：:]\s*「([^」]+)」', text):
            _add_if_new(q)

        # 模式3：中文引号 "xxx"
        for q in re.findall(
            r'(?:ZUN|神主)[^""*]*?(?:说道|说|所说|谈到|讲述)[^""]*?\u201c([^\u201d]+)\u201d', text
        ):
            _add_if_new(q)

        # 模式4：独立引号（前后50字内有 ZUN/神主/太田 标记）
        for q in re.findall(r'「([^」]{20,})」', text):
            idx = text.find(q)
            if idx >= 0:
                before = text[max(0, idx - 50):idx]
                if any(kw in before for kw in ('ZUN', '神主', '太田')):
                    _add_if_new(q)

        # 模式5：独立中文引号
        for q in re.findall(r'\u201c([^\u201d]{20,})\u201d', text):
            idx = text.find(q)
            if idx >= 0:
                before = text[max(0, idx - 50):idx]
                if any(kw in before for kw in ('ZUN', '神主', '太田')):
                    _add_if_new(q)

        return quotes

    # ── 纯文本格式（fallback）────────────────────────────

    def parse_plain_zun_text(self, content: str, source_id: str) -> list:
        """解析纯文本中的 ZUN 发言（fallback）"""
        text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = self.cleaner.extract_mw_body(text)
        text = self.cleaner.clean_html(text)

        rows = self._extract_plain_text_rows(text)
        quotes = []
        self._extract_qa_from_rows(rows, source_id, quotes)
        return quotes

    def _extract_plain_text_rows(self, text: str) -> list:
        """从纯文本中提取行数据"""
        lines = text.split('\n')
        ZUN_PREFIX_RE = re.compile(
            r'^(ZUN[：:]|Z[：:]|神主[：:]|ZUN氏[：:]|ZUN先生[：:]|ZUN\s)'
        )
        ZUN_STANDALONE = {"ZUN", "Z", "神主"}
        OTHER_SPEAKER_RE = re.compile(
            r'^(博之|──|―|——|记者|采访者|问[：:]|Q[：:]|EDITOR|小此木|海原|海[：:]|azmaya)'
        )
        rows = []
        current_speaker = None
        current_texts = []

        def _flush():
            nonlocal current_speaker, current_texts
            if current_speaker and current_texts:
                text_joined = " ".join(current_texts).strip()
                if len(text_joined) > 5:
                    rows.append({
                        "speaker": current_speaker,
                        "is_zun": current_speaker in ZUN_NAMES or current_speaker == "ZUN",
                        "text": text_joined,
                    })
            current_speaker = None
            current_texts = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                _flush()
                continue
            zun_match = ZUN_PREFIX_RE.match(stripped)
            is_zun_standalone = stripped in ZUN_STANDALONE
            other_match = OTHER_SPEAKER_RE.match(stripped)
            if zun_match:
                _flush()
                current_speaker = "ZUN"
                after = stripped[zun_match.end():]
                current_texts = [after] if after else []
            elif is_zun_standalone:
                _flush()
                current_speaker = "ZUN"
            elif other_match:
                _flush()
                current_speaker = other_match.group(1)
                after = OTHER_SPEAKER_RE.sub('', stripped)
                current_texts = [after] if after else []
            elif current_speaker:
                if OTHER_SPEAKER_RE.match(stripped):
                    _flush()
                else:
                    current_texts.append(stripped)

        _flush()
        return rows

    # ── Markdown 格式 ────────────────────────────────────

    def parse_markdown_interview(self, content: str, source_id: str) -> list:
        """解析 Markdown 格式的访谈

        支持格式：
        - **ZUN**：回答
        - **提问者**：提问
        - ZUN\\n: 回答（MediaWiki 列表格式）
        - ——\\n: 提问
        """
        rows = self._extract_markdown_rows(content)
        quotes = []
        self._extract_qa_from_rows(rows, source_id, quotes, merge_consecutive=False)
        return quotes

    def _extract_markdown_rows(self, content: str) -> list:
        """从 Markdown 格式中提取行数据"""
        lines = content.split("\n")
        rows = []
        current_speaker = None
        current_text = []

        # 其他说话人（非 ZUN）
        OTHER_MD_SPEAKERS = re.compile(
            r'^(azmaya|——|博之|记者|采访者|问[：:]|Q[：:]|EDITOR|小此木|海原|azmaya|编辑|取材)'
        )

        def _flush():
            nonlocal current_speaker, current_text
            if current_speaker and current_text:
                text = " ".join(current_text).strip()
                text = re.sub(r'\s+', ' ', text)
                if len(text) > 5:
                    rows.append({"speaker": current_speaker, "is_zun": current_speaker == "ZUN", "text": text})
            current_speaker = None
            current_text = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # 格式1: **ZUN**：xxx 或 **提问者**：xxx
            bold_speaker_match = re.match(r'^\*\*(.+?)\*\*[：:]\s*(.*)', stripped)
            if bold_speaker_match:
                _flush()
                current_speaker = bold_speaker_match.group(1).strip()
                after = bold_speaker_match.group(2).strip()
                current_text = [after] if after else []
                continue

            # 格式2: ZUN\n: xxx（MediaWiki 列表格式）
            # 也支持其他说话人如 azmaya, ——
            if stripped in ("ZUN", "——", "azmaya"):
                _flush()
                current_speaker = stripped
                continue

            # 列表回答行: : xxx
            if stripped.startswith(": ") and current_speaker:
                answer = stripped[2:].strip()
                if answer:
                    current_text.append(answer)
                continue

            # 其他 ** 开头的说话人
            if stripped.startswith("**") and current_speaker:
                _flush()
                continue

            # 空行分隔
            if not stripped and current_speaker and current_text:
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith(": ") and next_line != "ZUN" and not next_line.startswith("**"):
                        _flush()
                continue

            if current_speaker and stripped and not stripped.startswith(": "):
                if OTHER_MD_SPEAKERS.match(stripped):
                    _flush()
                    current_speaker = stripped
                else:
                    current_text.append(stripped)

        _flush()
        return rows

    # ── 二轩目广播格式 ──────────────────────────────────

    def parse_nikenme_radio(self, content: str, source_id: str) -> list:
        """解析二轩目广播（2軒目から始まるラジオ）内容整理页面

        页面结构：每个 <h2> 是一回广播。
        主要格式：<dl>/<dt>/<dd> 对话列表
        辅助格式：<p> 段落中的叙述性概括和引号
        """
        quotes = []
        min_len = NIKENME_MIN_QUOTE_LEN
        seen_texts = set()

        def _add_quote(text: str, src: str):
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > min_len and text not in seen_texts:
                seen_texts.add(text)
                quotes.append(self.factory.make_quote(text, src))

        headlines = list(re.finditer(
            r'<span[^>]*class="mw-headline"[^>]*id="([^"]*)"[^>]*>([^<]*)</span>', content
        ))

        for i, hl in enumerate(headlines):
            section_title = re.sub(r'<[^>]+>', '', hl.group(2)).strip()
            if section_title == '注释':
                continue

            ep_match = re.search(r'第(\d+)回', section_title)
            ep_num = ep_match.group(1) if ep_match else ''
            ep_source = f"{source_id}-{ep_num}" if ep_num else source_id

            start = hl.end()
            end = headlines[i + 1].start() if i + 1 < len(headlines) else len(content)
            section_html = content[start:end]

            # 方法1: 解析 <dl>/<dt>/<dd> 对话列表
            rows = self._extract_nikenme_dialogue_rows(section_html, min_len)
            self._extract_qa_from_rows(rows, ep_source, quotes, min_len=min_len)

            # 方法2: 解析 <p> 中的叙述性内容（补充引号）
            paragraphs = re.findall(r'<p>(.*?)</p>', section_html, re.DOTALL)
            for p_html in paragraphs:
                p_text = self.cleaner.clean_html(p_html).strip()
                if not p_text:
                    continue
                for q in re.findall(r'\u201c([^\u201d]{10,})\u201d', p_text):
                    _add_quote(q, ep_source)
                for q in re.findall(r'\u300c([^\u300d]{10,})\u300d', p_text):
                    _add_quote(q, ep_source)

        return quotes

    def _extract_nikenme_dialogue_rows(self, section_html: str, min_len: int) -> list:
        """从二轩目广播 <dl>/<dt>/<dd> 中提取行数据"""
        dialogue_pairs = re.findall(
            r'<dt[^>]*>(.*?)</dt>\s*<dd>(.*?)</dd>', section_html, re.DOTALL
        )
        rows = []
        current_speaker = None
        current_texts = []

        def _flush():
            nonlocal current_speaker, current_texts
            if current_speaker and current_texts:
                text = " ".join(current_texts)
                is_zun = current_speaker in ZUN_NAMES
                if len(text) > min_len:
                    rows.append({"speaker": current_speaker, "is_zun": is_zun, "text": text})
            current_speaker = None
            current_texts = []

        for dt_html, dd_html in dialogue_pairs:
            speaker = self.cleaner.clean_html(dt_html).strip()
            text = self.cleaner.clean_html(dd_html).strip()
            is_zun = speaker in ZUN_NAMES

            if is_zun:
                if current_speaker and current_speaker not in ZUN_NAMES:
                    _flush()
                elif current_speaker in ZUN_NAMES:
                    pass  # 连续 ZUN 发言，合并
                else:
                    _flush()
                current_speaker = speaker
                if text:
                    current_texts.append(text)
            else:
                _flush()
                current_speaker = speaker
                if text:
                    current_texts = [text]
                else:
                    current_texts = []

        _flush()
        return rows

    # ── 通用 QApair 提取 ────────────────────────────────

    def _extract_qa_from_rows(self, rows: list, source_id: str, quotes: list, min_len: int = 10, merge_consecutive: bool = True):
        """从有序行列表中提取提问-回答对和纯回答

        rows: [{"speaker": str, "is_zun": bool, "text": str}, ...]
        逻辑：
        - 如果 ZUN 前面有非 ZUN 发言，组成 QApair
        - 连续多行非 ZUN → 合并为一个提问
        - 连续多行 ZUN → 合并为一个回答
        - 孤立 ZUN（前面无提问）→ 纯回答

        merge_consecutive: True → 合并连续同一说话人（适用于段落格式）;
                           False → 每行独立（适用于表格格式，每行天然是一条独立发言）
        """
        # 按需合并连续同一说话人的行
        merged = self._merge_consecutive_rows(rows) if merge_consecutive else rows

        # 从合并后的行中提取 QApair 和纯回答
        i = 0
        while i < len(merged):
            row = merged[i]
            if row["is_zun"]:
                answer = re.sub(r'\s+', ' ', row["text"]).strip()
                if len(answer) < min_len:
                    i += 1
                    continue

                # 检查前面是否有非 ZUN 发言（提问）
                question = None
                if i > 0 and not merged[i - 1]["is_zun"]:
                    q_text = re.sub(r'\s+', ' ', merged[i - 1]["text"]).strip()
                    if len(q_text) > 3:
                        question = q_text

                if question:
                    quotes.append(self.factory.make_qa_pair(question, answer, source_id))
                else:
                    quotes.append(self.factory.make_quote(answer, source_id))
            i += 1

    @staticmethod
    def _merge_consecutive_rows(rows: list) -> list:
        """合并连续同一说话人的行"""
        merged = []
        for row in rows:
            if merged and merged[-1]["is_zun"] == row["is_zun"]:
                merged[-1]["text"] += " " + row["text"]
            else:
                merged.append({
                    "speaker": row["speaker"],
                    "is_zun": row["is_zun"],
                    "text": row["text"],
                })
        return merged

    # ── 解析器调度 ──────────────────────────────────────
    # 每个数据源对应唯一解析器，通过 config.INTERVIEW_URLS 中的 parser_name 字段指定
    # 不再使用 auto 模式，避免误匹配


# ── 模块级便捷实例 ──────────────────────────────────────

_parser = InterviewParser()

# 向后兼容：模块级函数
parse_local_quotes = _parser.parse_local_quotes
parse_thbwiki_table = _parser.parse_thbwiki_table
parse_thbwiki_dtdd = _parser.parse_thbwiki_dtdd
parse_generic_table = _parser.parse_generic_table
parse_p_zun_format = _parser.parse_p_zun_format
parse_narrative_quotes = _parser.parse_narrative_quotes
parse_plain_zun_text = _parser.parse_plain_zun_text
parse_markdown_interview = _parser.parse_markdown_interview
parse_nikenme_radio = _parser.parse_nikenme_radio
