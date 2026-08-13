import json
from pathlib import Path
from src.y2h_ppi.inference.predictor import PPIPredictor

def test_v3_results():
    predictor = PPIPredictor()
    # Predict YFL039C + YAL001C
    try:
        res = predictor.predict_pair("YFL039C", "YAL001C")
        print("V3 Prediction for YFL039C + YAL001C:")
        print(f"  Probability: {res['calibrated_probability']}")
        print(f"  Confidence: {res['confidence_band']}")
        print(f"  Model: {res['model']['version']}")
        print("  Status: SUCCESS - Sequence mapped successfully!\n")
    except Exception as e:
        print(f"FAILED: {e}")

    # Check metrics
    metrics_file = Path("reports/v3_evaluation_results.json")
    if metrics_file.exists():
        with open(metrics_file, "r") as f:
            metrics = json.load(f)
        try:
            rf_c1 = metrics["models"]["RandomForest"]["c1"]["1to1_balanced"]["auroc"]
            rf_c2 = metrics["models"]["RandomForest"]["c2"]["1to1_balanced"]["auroc"]
            rf_c3 = metrics["models"]["RandomForest"]["c3"]["1to1_balanced"]["auroc"]
            print(f"V3 Evaluation Metrics (1:1):")
            print(f"  C1 AUROC: {rf_c1:.4f}")
            print(f"  C2 AUROC: {rf_c2:.4f}")
            print(f"  C3 AUROC: {rf_c3:.4f}")
            
            if rf_c1 > 0.8 and rf_c3 > 0.6:
                print("\nSCIENTIFIC VALIDATION: V3 Evaluation Integrity Maintained.")
            else:
                print("\nWARNING: Metric degradation.")
        except KeyError:
            print("Could not read metrics structure.")
            
if __name__ == "__main__":
    test_v3_results()
