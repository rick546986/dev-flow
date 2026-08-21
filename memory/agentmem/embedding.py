"""versioned embedding(§24)。

**observation 不得只有裸 vector。** 每一筆 embedding 一律連帶記下四件:

    provider / model / dimension / version

換 embedding model 最惡劣的失敗模式是**靜默**:舊 vector 還在表裡,維度或語意空間
已經換了,cosine similarity 全部趨近 0 —— retrieval 看起來「找不到」,而不是
「索引該重建了」。所以本檔提供的不是「一個 embedding 函式」,是:

    mismatch 偵測 → 明確回報 → re-index(migration)

**預設 provider 的誠實聲明**:`hashing / bow-sha256` 是**不需要任何外部相依**的
token-hashing bag-of-words 向量,它提供的是「詞面重疊的向量化」,**不是語意相似度**。
它的用途是讓 vector 通道在沒有 embedding 服務的環境裡也有一個確定性的成員參與
RRF fusion(而且測試結果可重現)。要真語意,註冊外部 provider:

    embedding.register_provider(MyProvider())   # 見 Provider 協定

vector 只住 local SQLite,**不進 Git**(§5)。
"""
import hashlib
import math
import struct

from . import textnorm

DEFAULT_DIM = 256


class Provider:
    """embedding provider 協定。實作四個屬性 + 一個方法即可註冊。"""

    name = "abstract"
    model = "abstract"
    dim = 0
    version = "0"

    def embed(self, text):
        raise NotImplementedError


class HashingProvider(Provider):
    """token-hashing bag-of-words(stdlib only、deterministic)。

    刻意用 textnorm.tokens() 當切詞來源 —— 這樣中文與 code symbol 在 vector 通道
    也不會被 strip;若這裡自己重寫一套 ASCII 切詞,就會出現「lexical 通道查得到、
    vector 通道查不到」的不對稱。
    """

    name = "hashing"
    model = "bow-sha256"
    version = "1"

    def __init__(self, dim=DEFAULT_DIM):
        self.dim = dim

    def embed(self, text):
        vector = [0.0] * self.dim
        toks = textnorm.tokens(text or "")
        if not toks:
            return vector
        for token in toks:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector))
        if norm:
            vector = [v / norm for v in vector]
        return vector


_PROVIDERS = {}


def register_provider(provider):
    _PROVIDERS[provider.name] = provider
    return provider


register_provider(HashingProvider())


def get_provider(name=None):
    if name is None:
        return _PROVIDERS["hashing"]
    if name not in _PROVIDERS:
        raise ValueError(
            "未註冊的 embedding provider:{0!r}(已註冊:{1})".format(
                name, sorted(_PROVIDERS)))
    return _PROVIDERS[name]


def pack(vector):
    return struct.pack("<%df" % len(vector), *vector)


def unpack(blob, dim):
    if len(blob) != dim * 4:
        raise ValueError(
            "vector 位元組長度 {0} 與宣告維度 {1} 不符 —— 這正是換 model 沒 re-index "
            "的徵象,不得當成 0 相似度略過".format(len(blob), dim))
    return list(struct.unpack("<%df" % dim, blob))


def cosine(a, b):
    if len(a) != len(b):
        raise ValueError("維度不同的兩個向量不可比較({0} vs {1})".format(
            len(a), len(b)))
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)


class Embedder:
    """把 provider 綁到一個 store 上,負責 index / mismatch / re-index。"""

    def __init__(self, provider=None):
        self.provider = provider or get_provider()

    @property
    def signature(self):
        return {"provider": self.provider.name, "model": self.provider.model,
                "dim": self.provider.dim, "version": self.provider.version}

    def embed_item(self, store, uid, text):
        vector = self.provider.embed(text)
        store.put_embedding(uid, self.provider.name, self.provider.model,
                            self.provider.dim, self.provider.version,
                            pack(vector))
        return vector

    def mismatch_report(self, store):
        """回報向量通道健康:簽章不符、缺列、孤兒,三個數字都必填。

        「無需 re-index」只在 mismatched==0 **且** missing==0 時成立。
        既有向量簽章正確但有 item 沒向量,仍然是不完整的索引。
        """
        sig = (self.provider.name, self.provider.model,
               self.provider.version, self.provider.dim)
        mismatched = store.embedding_mismatch(*sig)
        missing = store.embedding_missing(*sig)
        orphaned = store.embedding_orphaned(*sig)
        needs = bool(mismatched or missing)
        return {"mismatched": mismatched, "missing": missing,
                "orphaned": orphaned, "signature": self.signature,
                "action": ("re-index 需要:跑 dev-setup 或 `memory reindex`"
                           if needs else "無需 re-index")}

    def reindex(self, store, force=False):
        """對缺 embedding(或 signature 不符)的 item 重算。回傳處理筆數。"""
        if force:
            store.drop_mismatched_embeddings(
                self.provider.name, self.provider.model, self.provider.version,
                self.provider.dim)
        else:
            dropped = store.drop_mismatched_embeddings(
                self.provider.name, self.provider.model, self.provider.version,
                self.provider.dim)
            del dropped
        rows = store.conn.execute(
            "SELECT i.item_uid, i.title, i.text FROM items i"
            " LEFT JOIN embeddings e ON e.item_uid = i.item_uid"
            " WHERE i.project_id = ? AND e.item_uid IS NULL",
            (store.project_id,)).fetchall()
        for row in rows:
            self.embed_item(store, row["item_uid"],
                            " ".join([row["title"] or "", row["text"] or ""]))
        store.set_meta("embedding_provider", self.provider.name)
        store.set_meta("embedding_model", self.provider.model)
        store.set_meta("embedding_dimension", self.provider.dim)
        store.set_meta("embedding_version", self.provider.version)
        return len(rows)

    def search(self, store, query_text, limit=20):
        """cosine 檢索;維度不符的列一律**跳過並記錄**,不當成 0 分默默混進結果。"""
        target = self.provider.embed(query_text)
        if not any(target):
            return [], 0
        skipped = 0
        scored = []
        for row in store.conn.execute(
                "SELECT item_uid, dim, vector FROM embeddings"
                " WHERE provider=? AND model=? AND version=?",
                (self.provider.name, self.provider.model,
                 self.provider.version)):
            try:
                vector = unpack(row["vector"], row["dim"])
            except ValueError:
                skipped += 1
                continue
            if len(vector) != len(target):
                skipped += 1
                continue
            scored.append((cosine(target, vector), row["item_uid"]))
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [(uid, score) for score, uid in scored[:limit] if score > 0], skipped
