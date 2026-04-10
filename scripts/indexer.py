"""向量索引构建器：ChromaDB + fastembed

双 collection 架构：
- zun_questions: 对提问做向量索引，metadata 中存储 answer_id
- zun_quotes: 对回答做向量索引

检索时先搜 zun_questions 找相似提问→取对应回答，再搜 zun_quotes 直接匹配→合并去重。
"""

import json

from config import INDEX_DIR, QUOTES_JSON, CHROMA_DIR, EMBEDDING_MODEL


class VectorIndexer:
    """向量索引构建器：去重 → 分类 → 保存 JSON → 生成 embedding → 写入 ChromaDB"""

    def __init__(self, chroma_dir=None, quotes_json=None, embedding_model_name=None):
        self.chroma_dir = chroma_dir or CHROMA_DIR
        self.quotes_json = quotes_json or QUOTES_JSON
        self.embedding_model_name = embedding_model_name or EMBEDDING_MODEL

    # ── 去重 ──────────────────────────────────────────

    @staticmethod
    def deduplicate(quotes: list) -> list:
        """按 text 字段去重"""
        seen = set()
        unique = []
        for q in quotes:
            key = q.get("text", "")
            if key not in seen:
                seen.add(key)
                unique.append(q)
        return unique

    # ── 分类 ──────────────────────────────────────────

    @staticmethod
    def classify_quotes(unique_quotes: list):
        """将语录分为 qa_pair 和纯回答两类"""
        qa_pairs = [q for q in unique_quotes if q["type"] == "qa_pair"]
        pure_quotes = [q for q in unique_quotes if q["type"] != "qa_pair"]
        return qa_pairs, pure_quotes

    # ── 保存 JSON ──────────────────────────────────────

    def save_quotes_json(self, unique_quotes: list):
        """保存去重后的语录到 JSON"""
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.quotes_json, "w", encoding="utf-8") as f:
            json.dump(unique_quotes, f, ensure_ascii=False, indent=2)

    # ── 记录构建 ──────────────────────────────────────

    @staticmethod
    def build_answer_records(qa_pairs: list, pure_quotes: list):
        """构建回答记录列表

        返回 (all_answers, answer_id_map)
        - all_answers: 所有回答的统一列表（qa_pair 的 answer + pure_quote 的 text）
        - answer_id_map: qa_pair.id → answer 记录 id 的映射
        """
        all_answers = []
        answer_id_map = {}

        for q in qa_pairs:
            answer_id = f"ans-{q['id']}"
            answer_id_map[q['id']] = answer_id
            all_answers.append({
                "id": answer_id,
                "text": q["answer"],
                "source": q["source"],
                "type": "qa_answer",
            })

        for q in pure_quotes:
            all_answers.append({
                "id": q["id"],
                "text": q["text"],
                "source": q["source"],
                "type": q["type"],
            })

        return all_answers, answer_id_map

    @staticmethod
    def build_question_records(qa_pairs: list, answer_id_map: dict) -> list:
        """构建提问记录列表，每条记录包含 answer_id 用于关联回答"""
        question_data = []
        for q in qa_pairs:
            question_data.append({
                "id": f"q-{q['id']}",
                "text": q["question"],
                "answer_id": answer_id_map[q['id']],
                "source": q["source"],
            })
        return question_data

    # ── Embedding 生成 ─────────────────────────────────

    @staticmethod
    def generate_embeddings(texts: list, model) -> list:
        """为文本列表生成 embedding 向量"""
        return list(model.embed(texts))

    # ── ChromaDB 写入 ─────────────────────────────────

    @staticmethod
    def add_to_collection(collection, ids, texts, embeddings, metas, batch_size=5000, label=""):
        """分批写入 ChromaDB collection"""
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            collection.add(
                ids=ids[i:end],
                documents=texts[i:end],
                embeddings=[emb.tolist() for emb in embeddings[i:end]],
                metadatas=metas[i:end]
            )
            if label:
                print(f"  [{label}] Added {end}/{len(ids)}")

    @staticmethod
    def reset_chroma(chroma_client):
        """清除旧 collection"""
        for name in ["zun_quotes", "zun_questions"]:
            try:
                chroma_client.delete_collection(name)
            except Exception:
                pass

    # ── 主入口 ──────────────────────────────────────

    def build(self, quotes: list):
        """去重 → 分类 → 保存 JSON → 生成 embedding → 写入 ChromaDB（双 collection）"""
        import chromadb
        from fastembed import TextEmbedding

        # 1. 去重
        unique_quotes = self.deduplicate(quotes)
        print(f"\nBuilding vector index for {len(unique_quotes)} unique quotes...")

        # 2. 分类
        qa_pairs, pure_quotes = self.classify_quotes(unique_quotes)
        print(f"  QA pairs: {len(qa_pairs)}")
        print(f"  Pure quotes: {len(pure_quotes)}")

        # 3. 保存 JSON
        self.save_quotes_json(unique_quotes)

        # 4. 构建记录
        all_answers, answer_id_map = self.build_answer_records(qa_pairs, pure_quotes)
        question_data = self.build_question_records(qa_pairs, answer_id_map)

        # 5. 生成 embedding
        print(f"  Loading model: {self.embedding_model_name}...")
        embedding_model = TextEmbedding(self.embedding_model_name)

        print(f"  Generating embeddings for {len(all_answers)} answers...")
        answer_embeddings = self.generate_embeddings(
            [a["text"] for a in all_answers], embedding_model
        )
        print(f"  Embedding dim: {len(answer_embeddings[0])}")

        print(f"  Generating embeddings for {len(question_data)} questions...")
        question_embeddings = self.generate_embeddings(
            [qd["text"] for qd in question_data], embedding_model
        )

        # 6. 写入 ChromaDB
        chroma_client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.reset_chroma(chroma_client)

        quotes_collection = chroma_client.create_collection(
            name="zun_quotes",
            metadata={"hnsw:space": "cosine"}
        )
        self.add_to_collection(
            quotes_collection,
            ids=[a["id"] for a in all_answers],
            texts=[a["text"] for a in all_answers],
            embeddings=answer_embeddings,
            metas=[{"source": a["source"], "type": a["type"]} for a in all_answers],
            label="zun_quotes",
        )

        questions_collection = chroma_client.create_collection(
            name="zun_questions",
            metadata={"hnsw:space": "cosine"}
        )
        self.add_to_collection(
            questions_collection,
            ids=[qd["id"] for qd in question_data],
            texts=[qd["text"] for qd in question_data],
            embeddings=question_embeddings,
            metas=[{"source": qd["source"], "answer_id": qd["answer_id"]} for qd in question_data],
            label="zun_questions",
        )

        print(f"\n  Done: {quotes_collection.count()} answers, {questions_collection.count()} questions indexed")
        return quotes_collection, questions_collection


# ── 模块级便捷函数（向后兼容）──────────────────────────────

_indexer = VectorIndexer()

def build_vector_index(quotes: list):
    """向后兼容的模块级入口"""
    return _indexer.build(quotes)
