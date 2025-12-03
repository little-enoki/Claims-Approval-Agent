import json
import pandas as pd

# ---------------------------
# Load Data
# ---------------------------
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

policies = load_json("data/insurance_policies.json")
reference_codes = load_json("data/reference_codes.json")
test_records = load_json("data/test_records.json")
validation_records = load_json("data/validation_records.json")

policy_map = {p["policy_id"]: p for p in policies}


# ---------------------------
# Required Functions
# ---------------------------

def summarize_patient_record(record):
    return {
        "patient_id": record["patient_id"],
        "age": record["age"],
        "gender": record["gender"],
        "diagnosis_codes": record["diagnosis_codes"],
        "procedure_code": record["procedure_code"],
        "preauth": record["preauth"],
        "policy_id": record["policy_id"],
    }


def summarize_policy_guideline(policy):
    return {
        "covered_procedure_codes": policy["covered_procedure_codes"],
        "covered_diagnosis_codes": policy["covered_diagnosis_codes"],
        "age_min": policy["age_min"],
        "age_max": policy["age_max"],
        "gender": policy["gender"],
        "requires_preauth": policy["requires_preauth"],
    }


def check_claim_coverage(patient, policy):
    results = {}

    # Step 1: Procedure code validation
    results["procedure_match"] = "Pass" if \
        patient["procedure_code"] in policy["covered_procedure_codes"] else "Fail"

    # Step 2: Diagnosis match
    results["diagnosis_match"] = "Pass" if \
        any(d in policy["covered_diagnosis_codes"] for d in patient["diagnosis_codes"]) else "Fail"

    # Step 3: Age check
    results["age_check"] = "Pass" if \
        policy["age_min"] <= patient["age"] <= policy["age_max"] else "Fail"

    # Step 4: Gender check
    results["gender_check"] = "Pass" if \
        (policy["gender"] == "Any" or policy["gender"] == patient["gender"]) else "Fail"

    # Step 5: Preauthorization check
    if policy["requires_preauth"]:
        results["preauth_check"] = "Pass" if patient["preauth"] else "Fail"
    else:
        results["preauth_check"] = "Pass"

    # Final decision
    final_decision = "Approve" if all(v == "Pass" for v in results.values()) \
                     else "Route for Review"

    results["Final Decision"] = final_decision
    return results


# ---------------------------
# Run agent on test records
# ---------------------------
def run_agent(records):
    results = []
    for record in records:
        patient = summarize_patient_record(record)
        policy = summarize_policy_guideline(policy_map[patient["policy_id"]])
        coverage_results = check_claim_coverage(patient, policy)
        results.append({**patient, **coverage_results})
    return pd.DataFrame(results)


df_results = run_agent(test_records)
df_results.to_excel("claim_approval_results.xlsx", index=False)

print("Saved: claim_approval_results.xlsx")
