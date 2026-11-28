"""Execute Policy IR → Compiler v2 on synthetic test configurations, no PyPSA solve."""
import json
from dataclasses import asdict
from energy_policy_llm.model_profile import synthetic_profile
from energy_policy_llm.policy_ir import PolicyIR, LegalType, MetricV2
from energy_policy_llm.compiler_v2 import compile_policy

def main():
    ir = PolicyIR(
        annotation_id="SYNTHETIC_NM2030_RPS", source_sha256="a"*64,
        provision="SYNTHETIC_17.9.571.8(C)", legal_type=LegalType.TARGET,
        metric=MetricV2.RENEWABLE_RETAIL_SALES, entity_id="distribution_cooperative",
        year=2030, target_fraction=0.50, evidence_verified=True,
        human_adjudicated=False)
    cases = {
        "strict_minimal": compile_policy(ir, synthetic_profile()),
        "explicit_generation_proxy": compile_policy(ir, synthetic_profile(), allow_proxy=True),
        "complete_synthetic_data_unadjudicated": compile_policy(ir, synthetic_profile(full=True)),
    }
    print(json.dumps({"experiment_type": "synthetic_compiler_only", "source_text_verified": False,
                      "human_gold_count": 0, "llm_predictions": 0, "pypsa_solved": False,
                      "results": {name: asdict(result) for name, result in cases.items()}}, indent=2))
    assert cases["strict_minimal"].status == "ABSTAIN"
    assert cases["explicit_generation_proxy"].status == "SCENARIO_PROXY"
    assert cases["complete_synthetic_data_unadjudicated"].status == "ABSTAIN"
if __name__ == "__main__":
    main()
