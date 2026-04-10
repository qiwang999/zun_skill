"""配置常量：路径、URL、说话人标识"""

from pathlib import Path

# ── 路径 ──────────────────────────────────────────────

SKILL_DIR = Path.home() / ".codebuddy" / "skills" / "zun-persona"
RAW_DIR = SKILL_DIR / "references" / "raw_interviews"
INDEX_DIR = SKILL_DIR / "references" / "vector_index"
QUOTES_JSON = INDEX_DIR / "quotes.json"
CHROMA_DIR = INDEX_DIR / "chroma_db"

LOCAL_QUOTES = [
    SKILL_DIR / "references" / "quotes" / "creation.md",
    SKILL_DIR / "references" / "quotes" / "philosophy.md",
    SKILL_DIR / "references" / "quotes" / "life-stories.md",
]

# ── Embedding 模型 ───────────────────────────────────

EMBEDDING_MODEL = "intfloat/multilingual-e5-large"

# ── ZUN 的说话人标识变体 ─────────────────────────────

ZUN_NAMES = {
    "ZUN", "Z", "ZUN氏", "神主", "ZUN先生",
    "ZUN（以下，Z）", "ZUN(以下,Z)",
}

# ── 访谈源 ──────────────────────────────────────────

INTERVIEW_URLS = [
    ("garakuta-1", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E6%88%91%E4%B9%90%E5%A4%9A%E4%B8%9B%E5%BF%97/ZUN%E5%88%9B%E5%88%8A%E8%AE%BF%E8%B0%88"),
    ("gairai-2018autumn", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Autumn!/ZUN%E8%AE%BF%E8%B0%88"),
    ("gairai-2018spring", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Spring!/ZUN%E8%AE%BF%E8%B0%88"),
    ("gairai-2019autumn", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Autumn!/ZUN%E8%AE%BF%E8%B0%88"),
    ("gairai-2019spring", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Spring!/ZUN%E8%AE%BF%E8%B0%88"),
    ("gairai-2021spring", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2021_Spring!/%E6%95%B0%E5%AD%97%E8%AE%BF%E8%B0%88"),
    ("gairai-2024", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2024/ZUN%E8%AE%BF%E8%B0%88"),
    ("gairai-tenkuujo", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E5%A4%A9%E7%A9%BA%E7%92%8B%E8%AE%BF%E8%B0%88"),
    ("gairai-kishinjo", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E9%A3%8E%E7%A5%9E%E5%BD%95%E8%AE%BF%E8%B0%88"),
    ("gairai-konjuden", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E7%BB%80%E7%8F%A0%E4%BC%A0%E8%AE%BF%E8%B0%88"),
    ("gairai-shinpireku", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E6%B7%B1%E7%A7%98%E5%BD%95%E8%AE%BF%E8%B0%88"),
    ("gairai-ni-zun", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%E8%AE%BF%E8%B0%88"),
    ("gairai-ni-zun-akiyama", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E3%81%82%E3%81%8D%E3%82%84%E3%81%BE%E3%81%86%E3%81%AB"),
    ("gairai-ni-zun-umihara", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E6%B5%B7%E5%8E%9F%E6%B5%B7%E8%B1%9A"),
    ("gairai-san-books", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%8F%82/%E4%B9%A6%E7%B1%8D%E7%9A%84%E6%B5%81%E6%B4%BE"),
    ("th-fuujinroku", "https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E9%A3%8E%E7%A5%9E%E5%BD%95%E9%87%87%E8%AE%BF"),
    ("th-chireiden", "https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%9C%B0%E7%81%B5%E6%AE%BF%E9%87%87%E8%AE%BF"),
    ("th-shinreibyou", "https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E7%A5%9E%E7%81%B5%E5%BA%99%E9%87%87%E8%AE%BF"),
    ("th-kishinchou", "https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E8%BE%89%E9%92%88%E5%9F%8E%E9%87%87%E8%AE%BF"),
    ("th-yousei", "https://thbwiki.cc/ZUN/%E5%A6%96%E7%B2%BE%E5%A4%A7%E6%88%98%E4%BA%89%E9%87%87%E8%AE%BF"),
    ("pku", "https://thbwiki.cc/ZUN/%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E9%87%87%E8%AE%BF"),
    ("weplay", "https://thbwiki.cc/ZUN/WePlay%E9%87%87%E8%AE%BF"),
    ("ign", "https://thbwiki.cc/ZUN/IGN%E9%87%87%E8%AE%BF"),
    ("usgamer", "https://thbwiki.cc/ZUN/USgamer%E9%87%87%E8%AE%BF"),
    ("reitaisai16", "https://thbwiki.cc/ZUN/%E4%BE%8B%E5%A4%A7%E7%A5%AD16%E9%87%87%E8%AE%BF"),
    ("bougetsu", "https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%84%9A%E6%9C%88%E6%8A%84%E9%87%87%E8%AE%BF"),
    ("shujin-no-kotodama", "https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E4%B8%89%E6%9C%88%E7%B2%BE_%EF%BD%9E_Eastern_and_Little_Nature_Deity./%E7%A5%9E%E4%B8%BB%E7%9A%84%E8%A8%80%E7%81%B5"),
]

GITHUB_INTERVIEWS = [
    ("shiguren-interview", "https://raw.githubusercontent.com/Delsin-Yu/THBWiki-Markdown/main/sources/ZUN-%E4%B8%9C%E6%96%B9%E8%8C%A8%E6%AD%8C%E4%BB%99%E8%AE%BF%E8%B0%88.md"),
]

# ── 二轩目广播（2軒目から始まるラジオ）─────────────────

NIKENME_URL = "https://thbwiki.cc/2%E8%BB%92%E7%9B%AE%E3%81%8B%E3%82%89%E5%A7%8B%E3%81%BE%E3%82%8B%E3%83%A9%E3%82%B8%E3%82%AA/%E5%86%85%E5%AE%B9%E6%95%B4%E7%90%86"

# 二轩目广播中的其他说话人（非 ZUN），用于分割语录
NIKENME_OTHER_SPEAKERS = {
    "小此木", "小此木哲朗", "okonogi",
    "heppoko", "Mario", "beat Mario", "马里奥",
    "DAI", "海原海豚", "海原", "azmaya",
    "是空", "Maron", "豚", "にしかわ",
    "观众", "主持人",
}

# 二轩目广播解析的最小语录长度（广播内容较碎，适当降低阈值）
NIKENME_MIN_QUOTE_LEN = 8
