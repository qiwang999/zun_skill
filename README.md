<div align="center">

# ZUN Persona Skill

> *"我今后也会继续慢悠悠地制作游戏。可能会制作，也可能不会制作，在这里说过的话也可能会变，也请大家欣赏我这种优哉游哉的生活方式"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

**[English](README_EN.md)** · **[日本語](README_JA.md)**

<br>

以《东方Project》唯一创作者 ZUN（太田顺也）的第一人称视角，回应关于弹幕、创作、酒与幻想乡的话题。说实话，做这个也没什么复杂的理由——有趣嘛（笑）。

<br>

大量访谈回答与提问，用双向量索引存着 | 两阶段检索：先匹配提问→取关联回答，再直接搜回答→合并去重 | 不是复读语录，是用他的方式看问题——（笑）

[效果示例](#效果示例) · [查询流程](#查询流程) · [安装](#安装) · [他蒸馏了什么](#他蒸馏了什么) · [数据来源](#数据来源) · [新增访谈数据](#新增访谈数据) · [诚实边界](#诚实边界)

</div>

---

## 效果示例

```
用户      ❯ 你怎么评价灵梦？

ZUN       ❯ 灵梦嘛……怎么说呢，我最有感情的角色还是她（笑）。
            硬要说的话，灵梦才是坏家伙吧（笑）。基本上不管三七二十一直接打倒敌人，
            是好事还是坏事就另当别论了。我想尽可能放低她的立场，给她一种在别的
            作品里见不到的世俗气息。与其说是什么超凡脱俗的主人公，不如说是把缺点
            全都暴露出来——但我觉得这样反而能提高角色的魅力。

用户      ❯ 你为什么一个人做游戏？

ZUN       ❯ 一个人做更轻松嘛（笑）。和请教别人比起来自己尝试更轻松，
            也更有趣。互相争执很麻烦，我总是会让着别人，那还不如自己做算了。

用户      ❯ 弹幕对你来说意味着什么？

ZUN       ❯ 弹幕就像格斗游戏的必杀技，是角色的一部分。一旦给弹幕起了名，
            子弹本身就产生了意义。弹幕像烟花——危险但美丽的话，就算危险也想靠近。
            最终目的还是让弹幕变得有趣（笑）。
```

不是简单的语录复读。ZUN 会用 **「有趣即正义」「坦诚自嘲」「细节堆叠」** 这些认知框架来回应——不是复读语录，是用他的方式看你的问题。

---

## 查询流程

用户提问后，系统按以下顺序检索相关语录：

```
  用户输入
  「你为什么一个人做游戏？」
       │
       ▼
  ┌─────────────────────────────────┐
  │  Step 1 · SKILL.md 内联语录       │
  │  核心语录直接引用，不需要额外检索   │
  └──────────────┬──────────────────┘
                 │ 不够？
                 ▼
  ┌─────────────────────────────────────────────────────┐
  │              Step 2 · 双向量语义检索                   │
  │                                                       │
  │   ┌──────────────────┐   ┌──────────────────┐        │
  │   │  提问集合          │   │  回答集合          │        │
  │   │  zun_questions   │   │  zun_quotes      │        │
  │   │                  │   │                  │        │
  │   │  语义搜索相似提问  │   │  直接语义搜索回答  │        │
  │   │      │           │   │      │           │        │
  │   │      ▼           │   │      ▼           │        │
  │   │  命中：           │   │  命中：           │        │
  │   │  「不玩自己做      │   │  「为什么我不玩    │        │
  │   │   的游戏吗？」    │   │   社交游戏」      │        │
  │   │      │           │   │                  │        │
  │   │      ▼           │   │                  │        │
  │   │  answer_id ──────┼───┼──→ 取出关联回答   │        │
  │   └──────────────────┘   └──────────────────┘        │
  │              │                │                        │
  │              └───────┬────────┘                        │
  │                      ▼                                 │
  │          合并 · 去重 · 按相似度排序                      │
  │      question_match 优先（有完整问答上下文）              │
  └──────────────────────┬────────────────────────────────┘
                         │ 相似度 < 0.7 或无覆盖？
                         ▼
  ┌─────────────────────────────────┐
  │  Step 3 · 网络检索               │
  │  ZUN {关键词} 発言 訪談           │
  │  优先：我楽多叢誌 > THBWiki      │
  └──────────────┬──────────────────┘
                 │ 找不到？
                 ▼
  「这个嘛……不太记得了（笑）」
```

### 为什么是两阶段？

访谈里有大量问答对话——问「为什么做弹幕游戏？」→ ZUN 答「……」。如果只存回答去检索，就像只看到弹幕轨迹却不知道符卡的名字，上下文就丢了。

两阶段检索让提问本身也成为检索入口：用户问「你为什么一个人做游戏」→ 匹配到「不玩自己做的游戏吗？」→ 取出 ZUN 的完整回答。有上下文的回答，比孤立的语录有用得多——大概吧（笑）。

### 模块结构

| 模块 | 类 | 职责 |
|------|------|------|
| `utils.py` | `QuoteFactory` | 语录与问答对的构造 |
| `utils.py` | `HtmlCleaner` | HTML 清洗、正文提取 |
| `parsers.py` | `InterviewParser` | 7 种格式解析器 + QA 对提取 + 自动调度 |
| `crawler.py` | `InterviewCrawler` | 网页抓取、缓存、多源爬取 |
| `indexer.py` | `VectorIndexer` | 去重、分类、记录构建、embedding 生成、ChromaDB 写入 |
| `searcher.py` | `QuoteSearcher` | 两阶段语义检索（提问匹配 + 回答匹配） |

---

## 安装

```bash
git clone https://github.com/qiwang999/zun_skill.git
cd zun_skill
pip install -r requirements.txt

# 向量索引已预构建，直接用就行
# 要是觉得不对劲，可以强制重建：
# python3 scripts/cli.py --rebuild
```

触发关键词：`ZUN`、`神主`、`东方`、`弹幕`、`幻想乡`、`太田顺也`、`上海爱丽丝幻乐团`

---

## 他蒸馏了什么

ZUN 不是理论家，是用直觉和具体画面讲道理的创作者。硬要说他的思维方式的话——

| 心智模型 | 一句话 |
|---------|--------|
| **有趣即正义** | 不做某事因为"太麻烦了"，做某事因为"有趣"——唯一的判断标准 |
| **（笑）的节奏** | 说认真的事 → 补一个自嘲 →（笑），对自己说的话保持轻松的距离感。不是在讲笑话，是一种距离感 |
| **坦诚直率** | 不美化过去，不避讳失败。Comike 落选、学分勉强毕业——这些都不藏着 |
| **细节堆叠** | 不说抽象感悟，堆具体的画面："每次都是用手指按着纽扣电池玩的" |
| **弹幕中心论** | 所有话题最终都会拉回弹幕和射击游戏——最终目的还是让弹幕变得有趣 |
| **被遗忘之物的守护者** | FM音源、旧式射击游戏、长野的民间传统——不是故意捡起，单纯只是喜欢 |

核心语录内化于 SKILL.md，更多问答通过双向量语义检索实时查找。

---

## 数据来源

所有语录来自 ZUN 先生的公开访谈——也没什么特别的，就是到处搜集来的（笑）。

| 来源 | 类型 | 数量 | 链接 |
|------|------|------|------|
| THBWiki 访谈页面 | 一手资料（HTML） | 26 篇 | [thbwiki.cc](https://thbwiki.cc) |
| 東方我楽多叢誌 ZUN 创刊访谈 | 一手资料（HTML） | ~5万字 | [访谈页面](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E6%88%91%E4%B9%90%E5%A4%9A%E4%B8%9B%E5%BF%97/ZUN%E5%88%9B%E5%88%8A%E8%AE%BF%E8%B0%88) |
| 二轩目广播 | 酒会广播内容整理（HTML） | 91 回 | [内容整理](https://thbwiki.cc/2%E8%BB%92%E7%9B%AE%E3%81%8B%E3%82%89%E5%A7%8B%E3%81%BE%E3%82%8B%E3%83%A9%E3%82%B8%E3%82%AA/%E5%86%85%E5%AE%B9%E6%95%B4%E7%90%86) |
| THBWiki-Markdown 茨歌仙访谈 | 一手资料（Markdown） | 1 篇 | [GitHub](https://github.com/Delsin-Yu/THBWiki-Markdown) |
| 本地手动整理语录 | 策展 | 3 个文件 | `references/quotes/` |

### 详细访谈清单

`scripts/config.py` 中 `INTERVIEW_URLS` 和 `GITHUB_INTERVIEWS` 配置的完整访谈列表。**欢迎大家继续补充新的访谈来源！**

| ID | 来源 | 说明 | 链接 |
|----|------|------|------|
| garakuta-1 | 東方我楽多叢誌 | ZUN 创刊访谈 | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E6%88%91%E4%B9%90%E5%A4%9A%E4%B8%9B%E5%BF%97/ZUN%E5%88%9B%E5%88%8A%E8%AE%BF%E8%B0%88) |
| gairai-2018autumn | 東方外來韋編 2018 Autumn! | ZUN 访谈 | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Autumn!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2018spring | 東方外來韋編 2018 Spring! | ZUN 访谈 | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Spring!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2019autumn | 東方外來韋編 2019 Autumn! | ZUN 访谈 | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Autumn!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2019spring | 東方外來韋編 2019 Spring! | ZUN 访谈 | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Spring!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2021spring | 東方外來韋編 2021 Spring! | 数字访谈 | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2021_Spring!/%E6%95%B0%E5%AD%97%E8%AE%BF%E8%B0%88) |
| gairai-2024 | 東方外來韋編 2024 | ZUN 访谈 | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2024/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-tenkuujo | 東方外來韋編 肆/天空璋访谈 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E5%A4%A9%E7%A9%BA%E7%92%8B%E8%AE%BF%E8%B0%88) |
| gairai-kishinjo | 東方外來韋編 肆/风神录访谈 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E9%A3%8E%E7%A5%9E%E5%BD%95%E8%AE%BF%E8%B0%88) |
| gairai-konjuden | 東方外來韋編 壱/绀珠传访谈 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E7%BB%80%E7%8F%A0%E4%BC%A0%E8%AE%BF%E8%B0%88) |
| gairai-shinpireku | 東方外來韋編 壱/深秘录访谈 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E6%B7%B1%E7%A7%98%E5%BD%95%E8%AE%BF%E8%B0%88) |
| gairai-ni-zun | 東方外來韋編 弐/ZUN 访谈 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-ni-zun-akiyama | 東方外來韋編 弐/ZUN×秋山 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E3%81%82%E3%81%8D%E3%82%84%E3%81%BE%E3%81%86%E3%81%AB) |
| gairai-ni-zun-umihara | 東方外來韋編 弐/ZUN×海原 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E6%B5%B7%E5%8E%9F%E6%B5%B7%E8%B1%9A) |
| gairai-san-books | 東方外來韋編 参/书籍的流派 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%8F%82/%E4%B9%A6%E7%B1%8D%E7%9A%84%E6%B5%81%E6%B4%BE) |
| th-fuujinroku | ZUN/东方风神录采访 | | [查看](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E9%A3%8E%E7%A5%9E%E5%BD%95%E9%87%87%E8%AE%BF) |
| th-chireiden | ZUN/东方地灵殿采访 | | [查看](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%9C%B0%E7%81%B5%E6%AE%BF%E9%87%87%E8%AE%BF) |
| th-shinreibyou | ZUN/东方神灵庙采访 | | [查看](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E7%A5%9E%E7%81%B5%E5%BA%99%E9%87%87%E8%AE%BF) |
| th-kishinchou | ZUN/东方辉针城采访 | | [查看](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E8%BE%89%E9%92%88%E5%9F%8E%E9%87%87%E8%AE%BF) |
| th-yousei | ZUN/妖精大战争采访 | | [查看](https://thbwiki.cc/ZUN/%E5%A6%96%E7%B2%BE%E5%A4%A7%E6%88%98%E4%BA%89%E9%87%87%E8%AE%BF) |
| pku | ZUN/北京大学采访 | | [查看](https://thbwiki.cc/ZUN/%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E9%87%87%E8%AE%BF) |
| weplay | ZUN/WePlay采访 | | [查看](https://thbwiki.cc/ZUN/WePlay%E9%87%87%E8%AE%BF) |
| ign | ZUN/IGN采访 | | [查看](https://thbwiki.cc/ZUN/IGN%E9%87%87%E8%AE%BF) |
| usgamer | ZUN/USgamer采访 | | [查看](https://thbwiki.cc/ZUN/USgamer%E9%87%87%E8%AE%BF) |
| reitaisai16 | ZUN/例大祭16采访 | | [查看](https://thbwiki.cc/ZUN/%E4%BE%8B%E5%A4%A7%E7%A5%AD16%E9%87%87%E8%AE%BF) |
| bougetsu | ZUN/东方儚月抄采访 | | [查看](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%84%9A%E6%9C%88%E6%8A%84%E9%87%87%E8%AE%BF) |
| shujin-no-kotodama | 东方三月精 神主的言灵 | | [查看](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E4%B8%89%E6%9C%88%E7%B2%BE_%EF%BD%9E_Eastern_and_Little_Nature_Deity./%E7%A5%9E%E4%B8%BB%E7%9A%84%E8%A8%80%E7%81%B5) |
| shiguren-interview | 茨歌仙访谈 | GitHub Markdown 源 | [查看](https://github.com/Delsin-Yu/THBWiki-Markdown) |
| nikenme-radio | 二轩目广播 | 91回广播内容整理 | [查看](https://thbwiki.cc/2%E8%BB%92%E7%9B%AE%E3%81%8B%E3%82%89%E5%A7%8B%E3%81%BE%E3%82%8B%E3%83%A9%E3%82%B8%E3%82%AA/%E5%86%85%E5%AE%B9%E6%95%B4%E7%90%86) |

---

## 新增访谈数据

支持三种方式新增 ZUN 先生的访谈数据：

### 方式一：添加本地语录文件（最简单）

将语录整理为 Markdown 格式，放入 `references/quotes/`：

```markdown
- "语录原文内容1"
- "语录原文内容2"
- "语录原文内容3"
```

`InterviewParser.parse_local_quotes()` 会自动解析。

### 方式二：添加 THBWiki / 其他网页访谈

编辑 `scripts/config.py`，在 `INTERVIEW_URLS` 列表中新增条目：

```python
INTERVIEW_URLS = [
    # ... 已有条目 ...
    ("my-new-interview", "https://thbwiki.cc/你的访谈页面URL"),
]
```

`InterviewParser` 会自动尝试 7 种 HTML 解析器，用第一个返回非空结果的——总之试试看嘛（笑）。

### 方式三：添加 Markdown 格式访谈

编辑 `scripts/config.py`，在 `GITHUB_INTERVIEWS` 列表中新增条目：

```python
GITHUB_INTERVIEWS = [
    # ... 已有条目 ...
    ("my-md-interview", "https://raw.githubusercontent.com/.../interview.md"),
]
```

Markdown 解析支持 `**ZUN**：回答` 和 `ZUN\n: 回答` 两种格式。

### 重建索引

添加新数据后，重建索引：

```bash
python3 scripts/cli.py --rebuild
```

### 添加自定义解析器

如果新访谈的 HTML 结构不在已有 7 种解析器覆盖范围内，在 `InterviewParser` 类中新增方法，并加入 `ALL_PARSERS_HTML` 列表：

```python
class InterviewParser:
    # ...
    
    def parse_my_custom_format(self, content: str, source_id: str) -> list:
        """自定义格式的解析器"""
        quotes = []
        # ... 解析逻辑 ...
        return quotes

    ALL_PARSERS_HTML = [
        "parse_thbwiki_table",
        # ... 已有解析器 ...
        "parse_my_custom_format",  # 添加到末尾
    ]
```

---

## 诚实边界

说实话，不把局限性讲清楚的 Skill 不值得信任——大概吧（笑）。

**能做的：**
- 以 ZUN 的第一人称风格回应关于东方、弹幕、创作、酒等话题
- 从真实访谈回答与提问的双向量索引中语义检索相关原话
- 如实呈现他的坦诚自嘲和随性表达

**做不到的：**

| 维度 | 说明 |
|------|------|
| 替代本人 | ZUN 的真实想法和私人生活无法复制 |
| 最新情报 | 新作发布、最新访谈等需要网络检索补充 |
| 角色设定 | 对东方世界观不做确定性的设定解释——"不太好说""这种感觉吧" |
| 日文原文 | 语录来源均为中文翻译，非日文原文 |

---

## 仓库结构

```
zun-persona/
├── SKILL.md                          # ZUN 人格核心文件（激活时加载）
├── README.md                         # 本文件（中文）
├── README_EN.md                      # English README
├── README_JA.md                      # 日本語 README
├── requirements.txt                  # Python 依赖
├── .gitignore
├── scripts/
│   ├── cli.py                        # CLI 入口（构建/检索/统计）
│   ├── config.py                     # 配置常量（路径、URL、说话人标识）
│   ├── utils.py                      # QuoteFactory + HtmlCleaner
│   ├── parsers.py                    # InterviewParser（7种格式解析器）
│   ├── crawler.py                    # InterviewCrawler（访谈采集，带缓存）
│   ├── indexer.py                    # VectorIndexer（双向量索引构建）
│   └── searcher.py                   # QuoteSearcher（两阶段语义检索）
└── references/
    ├── works.md                      # 作品年表
    ├── life.md                       # 生平时间线
    ├── quotes/                       # 语录切片（向量索引源文件）
    │   ├── creation.md               # 创作相关
    │   ├── philosophy.md             # 人生观与东方哲学
    │   └── life-stories.md           # 生平故事片段
    ├── raw_interviews/               # 爬取的原始访谈缓存
    │   └── SOURCES.md                # 访谈文件与原始出处链接索引
    └── vector_index/                 # 向量索引数据（预构建，可直接使用）
        ├── quotes.json               # 全部语录 JSON（~500KB）
        └── chroma_db/                # ChromaDB 向量索引（zun_questions + zun_quotes）
```

---

## 命令参考

```bash
# 构建索引
python3 scripts/cli.py

# 强制重建
python3 scripts/cli.py --rebuild

# 查看统计
python3 scripts/cli.py --stats

# 人类可读检索
python3 scripts/cli.py --query "你对灵梦有什么看法"

# JSON 检索（供程序调用）
python3 scripts/cli.py --search "灵梦" 5
```

---

## 关于 ZUN

ZUN（太田顺也，1977—），长野县出身，上海爱丽丝幻乐团的唯一成员。《东方Project》系列的唯一创作者——程序、编剧、美术、音乐全由一人完成，持续近三十年。以独立开发和宽松的二次创作政策闻名，创造了同人文化的奇迹。喜欢啤酒，讨厌麻烦的事，做游戏的理由只有一个——有趣。

---

## 许可证

MIT — 随便用，随便改，随便造。

---

<div align="center">

**语录** 告诉你他说过什么。<br>
**ZUN Persona Skill** 帮你用他的方式看问题。<br><br>
*最终目的，还是为了让弹幕变得有趣。*

<br>

MIT License © [qiwang999](https://github.com/qiwang999)

</div>
