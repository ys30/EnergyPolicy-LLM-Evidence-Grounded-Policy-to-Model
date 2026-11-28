"""RRF fusion of BM25 and optional *real* semantic embeddings; no fake embeddings.

An injected callable supports either an externally selected encoder or, optionally,
sentence-transformers via SentenceTransformerEncoder. Model IDs must be preserved.
"""
from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Callable, Sequence
from .legal_chunker import LegalChunk
from .retrievers import BM25LegalRetriever

Vector = Sequence[float]
EmbeddingFunction = Callable[[list[str]], Sequence[Vector]]

def cosine(a: Vector, b: Vector) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("Embedding dimension mismatch or empty embedding")
    if not all(isfinite(float(x)) for x in (*a, *b)):
        raise ValueError("Nonfinite embedding value")
    norm_a=sqrt(sum(x*x for x in a))
    norm_b=sqrt(sum(x*x for x in b))
    return sum(x*y for x,y in zip(a,b))/(norm_a*norm_b) if norm_a and norm_b else 0.0

class SentenceTransformerEncoder:
    """Optional local semantic model; not instantiated in lightweight CI."""
    def __init__(self, model_id: str):
        if not model_id:
            raise ValueError("Pin a semantic encoder ID")
        from sentence_transformers import SentenceTransformer
        self.model_id=model_id
        self.model=SentenceTransformer(model_id)
    def __call__(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True,
                                 show_progress_bar=False).tolist()

@dataclass(frozen=True)
class HybridHit:
    chunk: LegalChunk
    rrf_score: float
    rank: int
    channels: tuple[str, ...]

class HybridRetriever:
    def __init__(self, chunks: list[LegalChunk], *, encoder: EmbeddingFunction | None = None,
                 encoder_id: str | None = None, rrf_k: int = 60):
        if not chunks or rrf_k < 1:
            raise ValueError("Chunks and positive RRF k required")
        if encoder is not None and not encoder_id:
            raise ValueError("Record exact embedding encoder ID")
        if encoder is None and encoder_id:
            raise ValueError("Encoder ID without embedding function")
        self.chunks=tuple(chunks)
        self.bm25=BM25LegalRetriever(chunks)
        self.encoder=encoder
        self.encoder_id=encoder_id
        self.rrf_k=rrf_k
        self.vectors=None
        if encoder is not None:
            self.vectors=self._encode([c.exact_text for c in chunks])

    def _encode(self,texts: list[str]) -> list[tuple[float,...]]:
        vectors=[tuple(float(x) for x in v) for v in self.encoder(texts)]
        if len(vectors)!=len(texts) or not vectors or not vectors[0]:
            raise ValueError("Embedding output cardinality/dimension invalid")
        dim=len(vectors[0])
        if any(len(v)!=dim or not all(isfinite(x) for x in v) for v in vectors):
            raise ValueError("Embedding dimension or finiteness invalid")
        return vectors

    def semantic_search(self, query: str, k: int = 5, *, source_id: str | None = None) -> list[HybridHit]:
        """Embedding-only baseline, with the same corpus and model as RRF."""
        if self.encoder is None:
            raise ValueError("Real semantic encoder is not configured")
        if k < 1:
            raise ValueError("k must be positive")
        if not query.strip():
            return []
        qv=self._encode([query])[0]
        scored=[]
        for chunk,vector in zip(self.chunks,self.vectors):
            if source_id is not None and chunk.source_id != source_id:
                continue
            score=cosine(qv,vector)
            if score > 0:
                scored.append((score,chunk.chunk_id,chunk))
        scored.sort(key=lambda row:(-row[0],row[1]))
        return [HybridHit(chunk, score, rank, ("EMBEDDING",))
                for rank,(score,_,chunk) in enumerate(scored[:k],1)]

    def search(self, query: str, k: int = 5, *, source_id: str | None = None) -> list[HybridHit]:
        if k < 1:
            raise ValueError("k must be positive")
        candidates={c.chunk_id:c for c in self.chunks if source_id is None or c.source_id==source_id}
        if not candidates or not query.strip():
            return []
        # Fixed candidate pool for auditability; no implicit cross-source retrieval.
        pool=min(len(self.chunks), max(20, k*5))
        lexical=[h.chunk.chunk_id for h in self.bm25.search(query, pool, source_id=source_id)]
        semantic=[]
        if self.encoder is not None:
            qv=self._encode([query])[0]
            scored=[(cosine(qv,vector),c.chunk_id)
                    for c,vector in zip(self.chunks,self.vectors) if c.chunk_id in candidates]
            scored.sort(key=lambda pair:(-pair[0],pair[1]))
            semantic=[name for value,name in scored[:pool] if value>0]
        scores={}
        channels={}
        for channel, ids in (("BM25",lexical),("EMBEDDING",semantic)):
            for rank,cid in enumerate(ids,1):
                scores[cid]=scores.get(cid,0)+1/(self.rrf_k+rank)
                channels.setdefault(cid,[]).append(channel)
        ranked=sorted(scores,key=lambda cid:(-scores[cid],cid))
        return [HybridHit(candidates[cid],scores[cid],rank,tuple(channels[cid]))
                for rank,cid in enumerate(ranked[:k],1)]
