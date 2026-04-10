<div align="center">

# ZUN ペルソナスキル

> *「我今後もゆっくりとゲームを作り続けます。作るかもしれないし、作らないかもしれないし、ここで言ったことも変わるかもしれないけれど、私のこののんびりした生き方も楽しんでください」*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

**[中文](README.md)** · **[English](README_EN.md)**

<br>

東方Projectの唯一のクリエイター ZUN（太田順也）の一人称視点で、弾幕・創作・ビール・幻想郷についてすべてに答える。正直、これを作った複雑な理由なんてない——面白いから（笑）。

<br>

大量のインタビュー回答と質問のデュアルベクトルインデックス | 2段階検索：質問マッチ→関連回答、直接回答マッチ→統合・重複排除 | 語録を繰り返すのではなく、彼のやり方で考える

[デモ](#デモ) · [検索フロー](#検索フロー) · [インストール](#インストール) · [彼が蒸留したもの](#彼が蒸留したもの) · [データソース](#データソース) · [インタビューデータの追加](#インタビューデータの追加) · [正直な境界](#正直な境界)

</div>

---

## デモ

```
ユーザー    ❯ 霊夢についてどう思う？

ZUN         ❯ 霊夢か……どう言えばいいかな、一番愛着のあるキャラだな（笑）。
            強いて言えば、霊夢こそが悪党だろう（笑）。基本的に考えなしに敵を
            倒してしまう、それが良いことか悪いことかは別として。できるだけ彼女の
            立場を下げて、他の作品では見られない世俗的な雰囲気を持たせたかった。
            超凡脱俗な主人公というより、欠点をすべて曝け出している——でも、
            それが逆にキャラの魅力を高めると思う。

ユーザー    ❯ なぜ一人でゲームを作るの？

ZUN         ❯ 一人で作る方が楽だから（笑）。人に聞くより自分で試す方が楽で、
            面白い。他人と争うのは面倒くさい、いつも譲ってしまうから、
            いっそ自分でやった方がいい。

ユーザー    ❯ 弾幕にとって何を意味する？

ZUN         ❯ 弾幕は格闘ゲームの必殺技みたいなもの、キャラクターの一部だ。
            弾幕に名前をつければ、弾そのものに意味が生まれる。弾幕は花火みたい——
            危険なだけなら誰も見たくない。でも美しければ、危険でも近づきたい。
            結局の目的は、弾幕を面白くすることだ（笑）。
```

単なる語録の反復ではない。ZUN は **「面白い＝正義」「正直な自虐」「ディテールの積み重ね」** という認知フレームワークで応える——語録を繰り返すのではなく、彼の視点であなたの問題を見る。

---

## 検索フロー

ユーザーが質問すると、システムは次の順序で関連語録を検索する：

```
  ユーザー入力
  「なぜ一人でゲームを作るの？」
       │
       ▼
  ┌─────────────────────────────────┐
  │  Step 1 · SKILL.md インライン語録 │
  │  コア語録 — 追加検索不要           │
  └──────────────┬──────────────────┘
                 │ 足りない？
                 ▼
  ┌─────────────────────────────────────────────────────┐
  │              Step 2 · デュアルベクトル検索             │
  │                                                       │
  │   ┌──────────────────┐   ┌──────────────────┐        │
  │   │  質問コレクション   │   │  回答コレクション   │        │
  │   │  zun_questions   │   │  zun_quotes      │        │
  │   │                  │   │                  │        │
  │   │  類似質問を検索    │   │  回答を直接検索    │        │
  │   │      │           │   │      │           │        │
  │   │      ▼           │   │      ▼           │        │
  │   │  命中：           │   │  命中：           │        │
  │   │  「自分のゲーム     │   │  「なぜソーシャル   │        │
  │   │   遊ばないの？」   │   │   ゲームしない」   │        │
  │   │      │           │   │                  │        │
  │   │      ▼           │   │                  │        │
  │   │  answer_id ──────┼───┼──→ 関連回答を取得  │        │
  │   └──────────────────┘   └──────────────────┘        │
  │              │                │                        │
  │              └───────┬────────┘                        │
  │                      ▼                                 │
  │          統合 · 重複排除 · 類似度でランク付け            │
  │      question_match を優先（完全なコンテキストあり）      │
  └──────────────────────┬────────────────────────────────┘
                         │ 類似度 < 0.7 またはカバーなし？
                         ▼
  ┌─────────────────────────────────┐
  │  Step 3 · ウェブ検索              │
  │  ZUN {キーワード} 発言 訪談        │
  │  優先：我楽多叢誌 > THBWiki       │
  └──────────────┬──────────────────┘
                 │ 見つからない？
                 ▼
  「うーん……あんまり覚えてないな（笑）」
```

### なぜ2段階なのか？

インタビューにはQ&Aペアがたくさんある——「なぜ弾幕ゲームを作る？→ ZUN: ……」。回答だけをインデックスすると、スペルカードの名前を知らずに弾幕の軌跡だけを見ているようなもの——コンテキストが失われる。

2段階検索により、質問自体も検索の入り口になる：ユーザーが「なぜ一人でゲームを作るの？」と聞く → 「自分のゲーム遊ばないの？」にマッチ → ZUN の完全な回答を取得。コンテキストのある回答は、孤立した語録よりずっと有用——たぶんね（笑）。

### モジュール構成

| モジュール | クラス | 責務 |
|-----------|--------|------|
| `utils.py` | `QuoteFactory` | 語録とQAペアの構築 |
| `utils.py` | `HtmlCleaner` | HTMLクリーニング、テキスト抽出 |
| `parsers.py` | `InterviewParser` | 7形式パーサー + QAペア抽出 + 自動ディスパッチ |
| `crawler.py` | `InterviewCrawler` | キャッシュ付きウェブスクレイピング、マルチソース取得 |
| `indexer.py` | `VectorIndexer` | 重複排除、分類、レコード構築、embedding生成、ChromaDB書き込み |
| `searcher.py` | `QuoteSearcher` | 2段階セマンティック検索（質問マッチ + 回答マッチ） |

---

## インストール

```bash
git clone https://github.com/qiwang999/zun_skill.git
cd zun_skill
pip install -r requirements.txt

# ベクトルインデックスは事前構築済み — そのまま使える
# 何かおかしい場合は強制再構築：
# python3 scripts/cli.py --rebuild
```

トリガーキーワード：`ZUN`、`神主`、`東方`、`弾幕`、`幻想郷`、`太田順也`、`上海アリス幻楽団`

---

## 彼が蒸留したもの

ZUN は理論家ではなく、直感と具体的なイメージで語るクリエイターだ。彼の思考方式を無理に言うなら——

| メンタルモデル | 一言 |
|--------------|------|
| **面白い＝正義** | やらないのは「面倒くさい」、やるのは「面白い」——唯一の判断基準 |
| **（笑）のリズム** | 真面目なことを言う → 自虐を添える →（笑）、自分の言葉とのリラックスした距離感。冗談を言っているわけじゃない、距離感なんだ |
| **正直で率直** | 過去を美化しない、失敗を隠さない。コミケ落選、単位ギリギリ——全部隠さない |
| **ディテールの積み重ね** | 抽象的な感悟ではなく、具体的なイメージを積み上げる：「ボタン電池を指で押しながら遊んでた」 |
| **弾幕中心主義** | すべての話題は最終的に弾幕とシューティングゲームに戻る——究極の目的は弾幕を面白くすること |
| **忘れられしものの守護者** | FM音源、旧式シューティング、長野の民間伝承——わざと拾い上げたわけじゃない、単に好きなだけ |

コア語録は SKILL.md に内蔵、より多くのQ&Aはデュアルベクトルセマンティック検索でリアルタイムに検索可能。

---

## データソース

すべての語録は ZUN 先生の公開インタビューから——特別なことはない、あちこちから集めただけ（笑）。

| ソース | タイプ | 数量 | リンク |
|--------|--------|------|--------|
| THBWiki インタビューページ | 一次資料（HTML） | 26件 | [thbwiki.cc](https://thbwiki.cc) |
| 東方我楽多叢誌 ZUN 創刊インタビュー | 一次資料（HTML） | 約5万字 | [インタビューページ](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E6%88%91%E4%B9%90%E5%A4%9A%E4%B8%9B%E5%BF%97/ZUN%E5%88%9B%E5%88%8A%E8%AE%BF%E8%B0%88) |
| 二軒目ラジオ | 飲み会配信内容整理（HTML） | 91回 | [内容整理](https://thbwiki.cc/2%E8%BB%92%E7%9B%AE%E3%81%8B%E3%82%89%E5%A7%8B%E3%81%BE%E3%82%8B%E3%83%A9%E3%82%B8%E3%82%AA/%E5%86%85%E5%AE%B9%E6%95%B4%E7%90%86) |
| THBWiki-Markdown 三月精インタビュー | 一次資料（Markdown） | 1件 | [GitHub](https://github.com/Delsin-Yu/THBWiki-Markdown) |
| 手動整理の語録 | キュレーション | 3ファイル | `references/quotes/` |

### インタビュー全一覧

`scripts/config.py` の `INTERVIEW_URLS` と `GITHUB_INTERVIEWS` に設定されているインタビューの完全リスト。**新しいインタビューソースの追加を歓迎します！**

| ID | ソース | 説明 | リンク |
|----|--------|------|--------|
| garakuta-1 | 東方我楽多叢誌 | ZUN 創刊インタビュー | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E6%88%91%E4%B9%90%E5%A4%9A%E4%B8%9B%E5%BF%97/ZUN%E5%88%9B%E5%88%8A%E8%AE%BF%E8%B0%88) |
| gairai-2018autumn | 東方外來韋編 2018 Autumn! | ZUN インタビュー | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Autumn!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2018spring | 東方外來韋編 2018 Spring! | ZUN インタビュー | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Spring!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2019autumn | 東方外來韋編 2019 Autumn! | ZUN インタビュー | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Autumn!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2019spring | 東方外來韋編 2019 Spring! | ZUN インタビュー | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Spring!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2021spring | 東方外來韋編 2021 Spring! | デジタルインタビュー | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2021_Spring!/%E6%95%B0%E5%AD%97%E8%AE%BF%E8%B0%88) |
| gairai-2024 | 東方外來韋編 2024 | ZUN インタビュー | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2024/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-tenkuujo | 東方外來韋編 肆/天空璋インタビュー | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E5%A4%A9%E7%A9%BA%E7%92%8B%E8%AE%BF%E8%B0%88) |
| gairai-kishinjo | 東方外來韋編 肆/風神録インタビュー | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E9%A3%8E%E7%A5%9E%E5%BD%95%E8%AE%BF%E8%B0%88) |
| gairai-konjuden | 東方外來韋編 壱/紺珠伝インタビュー | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E7%BB%80%E7%8F%A0%E4%BC%A0%E8%AE%BF%E8%B0%88) |
| gairai-shinpireku | 東方外來韋編 壱/深秘録インタビュー | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E6%B7%B1%E7%A7%98%E5%BD%95%E8%AE%BF%E8%B0%88) |
| gairai-ni-zun | 東方外來韋編 弐/ZUN インタビュー | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-ni-zun-akiyama | 東方外來韋編 弐/ZUN×秋山 | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E3%81%82%E3%81%8D%E3%82%84%E3%81%BE%E3%81%86%E3%81%AB) |
| gairai-ni-zun-umihara | 東方外來韋編 弐/ZUN×海原 | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E6%B5%B7%E5%8E%9F%E6%B5%B7%E8%B1%9A) |
| gairai-san-books | 東方外來韋編 参/書籍の流派 | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%8F%82/%E4%B9%A6%E7%B1%8D%E7%9A%84%E6%B5%81%E6%B4%BE) |
| th-fuujinroku | ZUN/東方風神録インタビュー | | [表示](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E9%A3%8E%E7%A5%9E%E5%BD%95%E9%87%87%E8%A8%AA) |
| th-chireiden | ZUN/東方地霊殿インタビュー | | [表示](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%9C%B0%E7%81%B5%E6%AE%BF%E9%87%87%E8%A8%AA) |
| th-shinreibyou | ZUN/東方神霊廟インタビュー | | [表示](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E7%A5%9E%E7%81%B5%E5%BA%99%E9%87%87%E8%A8%AA) |
| th-kishinchou | ZUN/東方輝針城インタビュー | | [表示](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E8%BE%89%E9%87%88%E5%9F%8E%E9%87%87%E8%A8%AA) |
| th-yousei | ZUN/妖精大戦争インタビュー | | [表示](https://thbwiki.cc/ZUN/%E5%A6%96%E7%B2%BE%E5%A4%A7%E6%88%A6%E4%BA%89%E9%87%87%E8%A8%AA) |
| pku | ZUN/北京大学インタビュー | | [表示](https://thbwiki.cc/ZUN/%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E9%87%87%E8%A8%AA) |
| weplay | ZUN/WePlayインタビュー | | [表示](https://thbwiki.cc/ZUN/WePlay%E9%87%87%E8%A8%AA) |
| ign | ZUN/IGNインタビュー | | [表示](https://thbwiki.cc/ZUN/IGN%E9%87%87%E8%A8%AA) |
| usgamer | ZUN/USgamerインタビュー | | [表示](https://thbwiki.cc/ZUN/USgamer%E9%87%87%E8%A8%AA) |
| reitaisai16 | ZUN/例大祭16インタビュー | | [表示](https://thbwiki.cc/ZUN/%E4%BE%8B%E5%A4%A7%E7%A5%AD16%E9%87%87%E8%A8%AA) |
| bougetsu | ZUN/東方儚月抄インタビュー | | [表示](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%84%9A%E6%9C%88%E6%8A%84%E9%87%87%E8%A8%AA) |
| shujin-no-kotodama | 東方三月精 神主の言霊 | | [表示](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E4%B8%89%E6%9C%88%E7%B2%BE_%EF%BD%9E_Eastern_and_Little_Nature_Deity./%E7%A5%9E%E4%B8%BB%E7%9A%84%E8%A8%80%E7%81%B5) |
| shiguren-interview | 茨歌仙インタビュー | GitHub Markdown ソース | [表示](https://github.com/Delsin-Yu/THBWiki-Markdown) |
| nikenme-radio | 二軒目ラジオ | 91回の配信内容整理 | [表示](https://thbwiki.cc/2%E8%BB%92%E7%9B%AE%E3%81%8B%E3%82%89%E5%A7%8B%E3%81%BE%E3%82%8B%E3%83%A9%E3%82%B8%E3%82%AA/%E5%86%85%E5%AE%B9%E6%95%B4%E7%90%86) |

---

## インタビューデータの追加

ZUN 先生のインタビューデータを追加する3つの方法：

### 方法1：ローカル語録ファイルの追加（最も簡単）

語録を Markdown 形式で整理し、`references/quotes/` ディレクトリに配置する：

```markdown
- "語録原文1"
- "語録原文2"
- "語録原文3"
```

`InterviewParser.parse_local_quotes()` がよしなに処理する。

### 方法2：THBWiki / その他のウェブインタビューの追加

`scripts/config.py` を編集し、`INTERVIEW_URLS` リストにエントリを追加する：

```python
INTERVIEW_URLS = [
    # ... 既存のエントリ ...
    ("my-new-interview", "https://thbwiki.cc/あなたのインタビューページURL"),
]
```

`InterviewParser` は7種類のHTMLパーサーを自動的に試行する——とりあえずやってみよう（笑）。

### 方法3：Markdown形式のインタビューの追加

`scripts/config.py` を編集し、`GITHUB_INTERVIEWS` リストにエントリを追加する：

```python
GITHUB_INTERVIEWS = [
    # ... 既存のエントリ ...
    ("my-md-interview", "https://raw.githubusercontent.com/.../interview.md"),
]
```

Markdownパーサーは `**ZUN**：回答` と `ZUN\n: 回答` の2つの形式をサポートしている。

### インデックスの再構築

新しいデータを追加した後、インデックスを再構築する：

```bash
python3 scripts/cli.py --rebuild
```

### カスタムパーサーの追加

新しいインタビューのHTML構造が既存の7種類のパーサーでカバーされていない場合、`InterviewParser` クラスにメソッドを追加し、`ALL_PARSERS_HTML` リストに追加する：

```python
class InterviewParser:
    # ...
    
    def parse_my_custom_format(self, content: str, source_id: str) -> list:
        """カスタム形式のパーサー"""
        quotes = []
        # ... 解析ロジック ...
        return quotes

    ALL_PARSERS_HTML = [
        "parse_thbwiki_table",
        # ... 既存のパーサー ...
        "parse_my_custom_format",  # 末尾に追加
    ]
```

---

## 正直な境界

正直、限界を教えてくれないスキルは信頼に値しない——たぶんね（笑）。

**このスキルにできること：**
- ZUN の一人称スタイルで東方・弾幕・創作・ビール等の話題に回答
- 実際のインタビュー回答と質問のデュアルベクトルインデックスからセマンティック検索
- 彼の正直な自虐とカジュアルな表現を忠実に再現

**できないこと：**

| 次元 | 説明 |
|------|------|
| 本人に代わること | ZUN の本当の考えや私生活は再現できない |
| 最新情報 | 新作や最新インタビューはウェブ検索が必要 |
| 設定の権威 | 東方の世界観について確定的な解説はしない——「微妙だね」「そんな感じかな」 |
| 日本語原文 | 全語録は中国語訳であり、日本語原文ではない |

---

## リポジトリ構造

```
zun-persona/
├── SKILL.md                          # ZUN ペルソナコアファイル（起動時にロード）
├── README.md                         # 中国語 README
├── README_EN.md                      # 英語 README
├── README_JA.md                      # 本ファイル（日本語）
├── requirements.txt                  # Python 依存関係
├── .gitignore
├── scripts/
│   ├── cli.py                        # CLI エントリポイント（構築/検索/統計）
│   ├── config.py                     # 設定定数（パス、URL、話者ID）
│   ├── utils.py                      # QuoteFactory + HtmlCleaner
│   ├── parsers.py                    # InterviewParser（7形式パーサー）
│   ├── crawler.py                    # InterviewCrawler（キャッシュ付きスクレイピング）
│   ├── indexer.py                    # VectorIndexer（デュアルベクトルインデックス構築）
│   └── searcher.py                   # QuoteSearcher（2段階セマンティック検索）
└── references/
    ├── works.md                      # 作品年表
    ├── life.md                       # 生平タイムライン
    ├── quotes/                       # 語録ファイル（ベクトルインデックスソース）
    │   ├── creation.md               # 創作関連
    │   ├── philosophy.md             # 人生観と東方哲学
    │   └── life-stories.md           # 生平ストーリー断片
    ├── raw_interviews/               # 生インタビューキャッシュ
    │   └── SOURCES.md                # インタビューファイルと原文リンクの索引
    └── vector_index/                 # ベクトルインデックスデータ（事前構築済み）
        ├── quotes.json               # 全語録JSON（約500KB）
        └── chroma_db/                # ChromaDBベクトルインデックス（zun_questions + zun_quotes）
```

---

## コマンドリファレンス

```bash
# インデックス構築
python3 scripts/cli.py

# 強制再構築
python3 scripts/cli.py --rebuild

# 統計表示
python3 scripts/cli.py --stats

# 読みやすい検索
python3 scripts/cli.py --query "霊夢についてどう思う"

# JSON検索（プログラム用）
python3 scripts/cli.py --search "霊夢" 5
```

---

## ZUN について

ZUN（太田順也、1977年—）、長野県出身、上海アリス幻楽団の唯一のメンバー。『東方Project』シリーズの唯一のクリエイター——プログラム、シナリオ、グラフィック、音楽をすべて一人で手がけ、三十年近く続けている。インディーズ開発と緩い二次創作ポリシーで知られ、同人文化の奇跡を生み出した。ビールが好きで、面倒なことは嫌い。ゲームを作る理由はただ一つ——面白いから。

---

## ライセンス

MIT — 自由に使って、改造して、なんでもどうぞ。

---

<div align="center">

**語録** は彼が何を言ったかを教える。<br>
**ZUN ペルソナスキル** は彼の視点で物事を見る手助けをする。<br><br>
*結局のところ、弾幕を面白くするためなんだ。*

<br>

MIT License © [qiwang999](https://github.com/qiwang999)

</div>
