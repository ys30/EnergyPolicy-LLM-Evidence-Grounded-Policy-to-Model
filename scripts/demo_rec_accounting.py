"""Synthetic REC accounting demonstration; independent of PyPSA and legal validation."""
from dataclasses import asdict
import json
from energy_policy_llm.rec_accounting import Certificate, AnnualRetailSales, illustrative_annual_balance
from energy_policy_llm.pypsa_data_contract import SimulatedAnnualEnergy, illustrative_generation_share

def main():
    certificates = [
        Certificate("SYN-REC-A", "coop", 2030, 30.0, True, "coop", 2030),
        Certificate("SYN-REC-B", "coop", 2029, 15.0, True, "coop", 2030),
        Certificate("SYN-REC-C", "coop", 2030, 25.0, True),
    ]
    retail = AnnualRetailSales("coop", 2030, 100.0)
    ledger = illustrative_annual_balance(retail, certificates, .50)
    generation = SimulatedAnnualEnergy("coop", 2030, 100.0, 70.0)
    result = {
        "experiment": "SYNTHETIC_NONLEGAL_ACCOUNTING",
        "pypsa_solver_called": False,
        "llm_calls": 0,
        "gold_count": 0,
        "retail_rec_balance": asdict(ledger),
        "local_generation_share_proxy": illustrative_generation_share(generation),
        "warning": "A 70% renewable generation proxy does not imply compliance with a 50% REC/retail-sales requirement."
    }
    assert result["retail_rec_balance"]["illustrative_shortfall_mwh"] == 5.0
    assert result["local_generation_share_proxy"] == .7
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
