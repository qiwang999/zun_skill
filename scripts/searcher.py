"""语义检索器：两阶段策略

1. 先搜 zun_questions：用户问题 → 找相似提问 → 取对应回答
2. 再搜 zun_quotes：用户问题 → 直接匹配回答
3. 合并去重，按相似度排序

这样当用户问"你为什么做弹幕游戏"时，能找到访谈中"为什么做弹幕游戏？→ ZUN: ..."
这种有明确问答关系的上下文，回答效果更好。
"""

from config import CHROMA_DIR, EMBEDDING_MODEL


class QuoteSearcher:
    """语录语义检索器：两阶段策略（提问匹配 + 回答匹配）"""

    def __init__(self, chroma_dir=None, embedding_model_name=None):
        self.chroma_dir = chroma_dir or CHROMA_DIR
        self.embedding_model_name = embedding_model_name or EMBEDDING_MODEL
        self._chroma_client = None
        self._embedding_model = None

    # ── 懒加载属性 ──────────────────────────────────────

    @property
    def chroma_client(self):
        """懒加载 ChromaDB 客户端"""
        if self._chroma_client is None:
            import chromadb
            self._chroma_client = chromadb.PersistentClient(path=str(self.chroma_dir))
        return self._chroma_client

    @property
    def embedding_model(self):
        """懒加载 Embedding 模型"""
        if self._embedding_model is None:
            from fastembed import TextEmbedding
            self._embedding_model = TextEmbedding(self.embedding_model_name)
        return self._embedding_model

    # ── Embedding 生成 ─────────────────────────────────

    def embed_query(self, query: str) -> list:
        """将查询文本转为 embedding 向量"""
        return list(self.embedding_model.embed([query]))[0].tolist()

    # ── 阶段1：搜索提问 ────────────────────────────────

    def search_questions(self, query_embedding: list, n_results: int) -> dict:
        """搜索 zun_questions，返回 {answer_id: {similarity, question_text}}"""
        result_map = {}
        try:
            questions_col = self.chroma_client.get_collection("zun_questions")
            count = questions_col.count()
            if count == 0:
                return result_map

            q_results = questions_col.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, count)
            )

            if not q_results["distances"][0]:
                return result_map

            for doc, dist, meta in zip(
                q_results["documents"][0],
                q_results["distances"][0],
                q_results["metadatas"][0]
            ):
                sim = round(1 - dist, 3)
                aid = meta["answer_id"]
                result_map[aid] = {"similarity": sim, "question_text": doc}

        except Exception as e:
            print(f"  [warning] question search failed: {e}")

        return result_map

    # ── 获取关联回答 ───────────────────────────────────

    def fetch_answers_by_ids(self, answer_ids: list, question_sim_map: dict) -> dict:
        """根据 answer_id 批量获取回答，组装 question_match 结果"""
        results = {}
        if not answer_ids:
            return results

        try:
            quotes_col = self.chroma_client.get_collection("zun_quotes")
            ans_data = quotes_col.get(ids=answer_ids, include=["documents", "metadatas"])

            for aid, doc, meta in zip(
                ans_data["ids"],
                ans_data["documents"],
                ans_data["metadatas"]
            ):
                if aid in question_sim_map:
                    sim_info = question_sim_map[aid]
                    results[aid] = {
                        "text": doc,
                        "similarity": sim_info["similarity"],
                        "source": meta["source"],
                        "match_type": "question_match",
                        "matched_question": sim_info["question_text"],
                    }
        except Exception as e:
            print(f"  [warning] fetch answers failed: {e}")

        return results

    # ── 阶段2：搜索回答 ────────────────────────────────

    def search_answers(self, query_embedding: list, n_results: int, existing_ids: set) -> dict:
        """搜索 zun_quotes，返回不在 existing_ids 中的回答"""
        results = {}
        try:
            quotes_col = self.chroma_client.get_collection("zun_quotes")
            count = quotes_col.count()
            if count == 0:
                return results

            # 多搜一些，因为部分可能已被 question_match 覆盖
            fetch_n = min(n_results * 2, count)
            a_results = quotes_col.query(
                query_embeddings=[query_embedding],
                n_results=fetch_n
            )

            for doc, dist, meta, rid in zip(
                a_results["documents"][0],
                a_results["distances"][0],
                a_results["metadatas"][0],
                a_results["ids"][0]
            ):
                sim = round(1 - dist, 3)
                if rid not in existing_ids or sim > (existing_ids[rid] if isinstance(existing_ids, dict) else 0):
                    results[rid] = {
                        "text": doc,
                        "similarity": sim,
                        "source": meta["source"],
                        "match_type": "answer_match",
                    }

        except Exception as e:
            print(f"  [warning] answer search failed: {e}")

        return results

    # ── 主入口：两阶段检索 ──────────────────────────────

    def search(self, query: str, n_results: int = 5) -> list:
        """两阶段语义检索

        返回格式: [{"text": ..., "similarity": ..., "source": ..., "match_type": ...}, ...]
        match_type: "question_match" | "answer_match"
        """
        query_embedding = self.embed_query(query)
        results = {}  # id → result dict, 用于去重

        # 阶段1：搜索 zun_questions → 取对应回答
        question_sim_map = self.search_questions(query_embedding, n_results)
        if question_sim_map:
            answer_ids = list(question_sim_map.keys())
            question_results = self.fetch_answers_by_ids(answer_ids, question_sim_map)
            results.update(question_results)

        # 阶段2：搜索 zun_quotes
        # 传入已有结果的 id→similarity 映射，用于覆盖判断
        existing_sim = {rid: r["similarity"] for rid, r in results.items()}
        answer_results = self.search_answers(query_embedding, n_results, existing_sim)
        for rid, r in answer_results.items():
            if rid not in results or r["similarity"] > results[rid]["similarity"]:
                results[rid] = r

        # 按相似度排序，取 top n
        return sorted(results.values(), key=lambda x: -x["similarity"])[:n_results]


# ── 模块级便捷函数（向后兼容）──────────────────────────────

_searcher = QuoteSearcher()

def search(query: str, n_results: int = 5) -> list:
    """向后兼容的模块级入口"""
    return _searcher.search(query, n_results)
