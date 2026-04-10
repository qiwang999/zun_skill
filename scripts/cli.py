#!/usr/bin/env python3
"""
ZUN 语录向量索引工具 — CLI 入口

用法：
  python build_vector_index.py                          # 构建索引
  python build_vector_index.py --rebuild                # 强制重建索引
  python build_vector_index.py --stats                  # 查看索引统计
  python build_vector_index.py --query "你对灵梦有什么看法"  # 人类可读检索
  python build_vector_index.py --search "灵梦" 5          # JSON 检索（供 Skill 调用）
"""

import json
import sys

# 将 scripts/ 目录加入 sys.path，支持直接运行
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CHROMA_DIR, QUOTES_JSON, EMBEDDING_MODEL
from parsers import InterviewParser
from crawler import InterviewCrawler
from indexer import VectorIndexer
from searcher import QuoteSearcher


def cmd_search(argv):
    """JSON 检索模式（供 Skill 调用）"""
    idx = argv.index("--search")
    if idx + 1 >= len(argv):
        print("Usage: python build_vector_index.py --search '查询内容' [n_results]", file=sys.stderr)
        sys.exit(1)
    query = argv[idx + 1]
    n_results = int(argv[idx + 2]) if idx + 2 < len(argv) else 5
    searcher = QuoteSearcher()
    results = searcher.search(query, n_results)
    print(json.dumps(results, ensure_ascii=False, indent=2))


def cmd_query(argv):
    """人类可读检索模式"""
    idx = argv.index("--query")
    if idx + 1 >= len(argv):
        print("Usage: python build_vector_index.py --query '你的问题'", file=sys.stderr)
        sys.exit(1)
    query = argv[idx + 1]
    searcher = QuoteSearcher()
    results = searcher.search(query, n_results=5)
    print(f"\n查询: {query}")
    print(f"{'='*60}")
    for i, r in enumerate(results):
        match_type = r.get('match_type', 'answer_match')
        type_label = "提问匹配" if match_type == "question_match" else "回答匹配"
        print(f"\n[{i+1}] 相似度: {r['similarity']:.3f} | 来源: {r['source']} | 匹配: {type_label}")
        if match_type == "question_match" and 'matched_question' in r:
            q_display = r['matched_question'][:100] + "..." if len(r['matched_question']) > 100 else r['matched_question']
            print(f"    提问: {q_display}")
        display = r['text'][:200] + "..." if len(r['text']) > 200 else r['text']
        print(f"    回答: {display}")


def cmd_stats():
    """查看索引统计"""
    if not CHROMA_DIR.exists():
        print("索引尚未构建")
        return
    import chromadb
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    print(f"索引统计:")
    print(f"  索引位置: {CHROMA_DIR}")

    # zun_quotes
    try:
        quotes_col = chroma_client.get_collection("zun_quotes")
        print(f"\n  zun_quotes (回答):")
        print(f"    总数: {quotes_col.count()}")
        all_data = quotes_col.get(include=["metadatas"])
        type_counts = {}
        source_counts = {}
        for meta in all_data["metadatas"]:
            t = meta.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
            src = meta["source"]
            source_counts[src] = source_counts.get(src, 0) + 1
        print(f"    按类型:")
        for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"      {t}: {count}")
        print(f"    按来源:")
        for src, count in sorted(source_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"      {src}: {count}")
    except Exception:
        print("  zun_quotes: 未找到")

    # zun_questions
    try:
        questions_col = chroma_client.get_collection("zun_questions")
        print(f"\n  zun_questions (提问):")
        print(f"    总数: {questions_col.count()}")
    except Exception:
        print("  zun_questions: 未找到")


def cmd_build(rebuild: bool):
    """构建向量索引"""
    print("=" * 60)
    print("ZUN 语录向量索引构建工具")
    print(f"Embedding 模型: {EMBEDDING_MODEL}")
    print("=" * 60)

    if CHROMA_DIR.exists() and not rebuild:
        import chromadb
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = chroma_client.get_collection("zun_quotes")
        print(f"\n索引已存在，包含 {collection.count()} 条语录")
        print("使用 --rebuild 强制重建")
        return

    parser = InterviewParser()
    crawler = InterviewCrawler()
    indexer = VectorIndexer()

    print("\n[1/3] 解析本地语录...")
    local_quotes = parser.parse_local_quotes()
    print(f"  {len(local_quotes)} 条")

    print("\n[2/3] 爬取访谈...")
    try:
        interview_quotes = crawler.fetch_all()
        print(f"  {len(interview_quotes)} 条")
    except Exception as e:
        print(f"  [warning] {e}")
        interview_quotes = []

    all_quotes = local_quotes + interview_quotes
    print(f"\n  总计: {len(all_quotes)} 条")

    if not all_quotes:
        print("没有语录可索引")
        return

    print("\n[3/3] 构建向量索引...")
    try:
        indexer.build(all_quotes)
    except Exception as e:
        print(f"  [error] {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n索引构建完成！")
    print(f"  索引位置: {CHROMA_DIR}")
    print(f"  语录数据: {QUOTES_JSON}")
    print(f"\n  测试检索:")
    print(f"  python {__file__} --query '你对灵梦有什么看法'")


def main():
    if "--search" in sys.argv:
        cmd_search(sys.argv)
    elif "--query" in sys.argv:
        cmd_query(sys.argv)
    elif "--stats" in sys.argv:
        cmd_stats()
    else:
        cmd_build(rebuild="--rebuild" in sys.argv)


if __name__ == "__main__":
    main()
