"""Fail-closed semantic checker. Never silently converts RECs/retail sales to dispatch generation."""
from dataclasses import dataclass
from .schema import Metric, PolicyTarget


@dataclass(frozen=True)
class CompileDecision:
    status: str
    mode: str
    fraction: float | None
    justification: str
    legal_equivalence: bool


def compile_generation_share(target: PolicyTarget, allow_proxy: bool = False) -> CompileDecision:
    if target.legal_review != "clause_verified":
        if not allow_proxy:
            return CompileDecision("ABSTAIN", "strict", None, "Legal clause and covered entity have not been independently verified.", False)
    if target.metric == Metric.GENERATION_SHARE and target.legal_review == "clause_verified":
        return CompileDecision("COMPILED", "strict", target.fraction, "Explicit, reviewed generation-share metric.", True)
    if target.metric in (Metric.RETAIL_SALES_SHARE, Metric.CLEAN_RETAIL_SALES_SHARE):
        if allow_proxy and target.metric == Metric.RETAIL_SALES_SHARE:
            return CompileDecision("PROXY_ONLY", "illustrative", target.fraction,
                "Generation-share toy proxy is NOT a legal compliance constraint: retail sales, imports, certificates, eligible resources and periods differ.", False)
        return CompileDecision("ABSTAIN", "strict", None,
            "Cannot map retail-sales-based renewable/clean-energy requirement to generation share; eligible resources and compliance accounting are undefined.", False)
    return CompileDecision("ABSTAIN", "strict", None, "Unsupported target metric.", False)
