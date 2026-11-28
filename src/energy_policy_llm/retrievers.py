"""Transparent stdlib BM25 retrieval baseline over frozen, exactly citable chunks."""
from dataclasses import dataclass
from collections import Counter
from math import log
import re
from .legal_chunker import LegalChunk

TOKEN = re.compile(r"17\.9\.\d+\.\d+|[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?", re.I)
def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN.findall(text)]

@dataclass(frozen=True)
class SearchHit:
    chunk: LegalChunk
    bm25_score: float
    rank: int

class BM25LegalRetriever:
    def __init__(self, chunks: list[LegalChunk], *, k1: float = 1.5, b: float = 0.75):
        if not chunks or not 0 < k1 or not 0 <= b <= 1:
            raise ValueError("Invalid BM25 corpus/parameters")
        self.chunks = tuple(chunks)
        self.k1, self.b = k1, b
        self.docs = [Counter(tokenize(c.exact_text)) for c in chunks]
        lengths = [sum(v.values()) for v in self.docs]
        self.avg_len = sum(lengths) / len(lengths)
        self.lengths = lengths
        self.df = Counter()
        for doc in self.docs:
            self.df.update(doc.keys())

    def search(self, query: str, k: int = 5, *, source_id: str | None = None) -> list[SearchHit]:
        if k < 1:
            raise ValueError("k must be positive")
        terms = set(tokenize(query))
        if not terms:
            return []
        n = len(self.docs)
        scored = []
        for chunk, doc, length in zip(self.chunks, self.docs, self.lengths):
            if source_id is not None and chunk.source_id != source_id:
                continue
            score = 0.0
            for term in terms:
                tf = doc.get(term, 0)
                if not tf:
                    continue
                idf = log(1 + (n - self.df[term] + .5) / (self.df[term] + .5))
                score += idf * tf * (self.k1 + 1) / (
                    tf + self.k1 * (1-self.b+self.b*length/self.avg_len))
            if score > 0:
                scored.append((score, chunk.chunk_id, chunk))
        scored.sort(key=lambda v: (-v[0], v[1]))
        return [SearchHit(chunk, score, rank)
                for rank, (score, _, chunk) in enumerate(scored[:k], 1)]
