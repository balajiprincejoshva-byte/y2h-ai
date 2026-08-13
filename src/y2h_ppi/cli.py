import sys
import argparse
from pathlib import Path
from y2h_ppi.logger import logger

def phase0():
    """Phase 0: Environment & Repository Setup Checkpoint."""
    logger.info("Running Phase 0 Checkpoint: Environment & Repository Setup")
    dirs = [
        "config", "data/raw", "data/interim", "data/processed",
        "src/y2h_ppi/data", "src/y2h_ppi/features", "src/y2h_ppi/splitting",
        "src/y2h_ppi/models", "src/y2h_ppi/evaluation", "src/y2h_ppi/explain",
        "src/y2h_ppi/inference", "src/y2h_ppi/network", "src/y2h_ppi/api",
        "frontend", "tests", "reports", "scripts", "logs"
    ]
    for d in dirs:
        p = Path(d)
        p.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory verified: {p.resolve()}")
    
    print("[OK] Phase 0 Checkpoint PASSED: Directory structure & CLI functional.")

def phase1():
    """Phase 1: Real Data Acquisition (BioGRID, UniProt/SGD, Negatome) & Manifest Logging."""
    logger.info("Executing Phase 1: Real Data Acquisition")
    from y2h_ppi.data.pipeline import run_phase1
    run_phase1()

def phase2():
    """Phase 2: Negative Sampling Strategy (Curated, Random 1:1, Imbalance 1:10 & 1:100)."""
    logger.info("Executing Phase 2: Negative Sampling Strategy")
    from y2h_ppi.data.negatives import run_phase2
    run_phase2()

def phase3():
    """Phase 3: Feature Engineering (Classical Descriptors & ESM-2 Embeddings)."""
    logger.info("Executing Phase 3: Feature Engineering")
    from y2h_ppi.features.pipeline import run_phase3
    run_phase3()

def phase4():
    """Phase 4: Model Training Pipeline (Baseline ML, MLP, Siamese Network)."""
    logger.info("Executing Phase 4: Model Training")
    from y2h_ppi.models.trainer import run_phase4
    run_phase4()

def phase5():
    """Phase 5: Rigorous Protein-Disjoint (C1/C2/C3) Evaluation & Auto-Reporting."""
    logger.info("Executing Phase 5: Rigorous Evaluation")
    from y2h_ppi.evaluation.pipeline import run_phase5
    run_phase5()

def phase6():
    """Phase 6: Explainability Pipeline (SHAP & Embedding Nearest-Neighbors)."""
    logger.info("Executing Phase 6: Explainability")
    from y2h_ppi.explain.pipeline import run_phase6
    run_phase6()

def phase7():
    """Phase 7: Inference Engine Verification."""
    logger.info("Executing Phase 7: Inference Engine Verification")
    from y2h_ppi.inference.predictor import run_phase7
    run_phase7()

def phase8():
    """Phase 8: Launch API and Streamlit Web Application."""
    logger.info("Executing Phase 8: Launch Services")
    print("API endpoint: uvicorn src.y2h_ppi.api.main:app --reload")
    print("Web UI: streamlit run frontend/app.py")

def phase9():
    """Phase 9: Run Full Pytest Suite, Generate Model Card & Limitations."""
    logger.info("Executing Phase 9: Testing & Documentation")
    from y2h_ppi.evaluation.report_generator import generate_docs
    generate_docs()

def main():
    parser = argparse.ArgumentParser(description="Y2H-AI: AI-Driven Computational Platform for Yeast PPI Prediction")
    parser.add_argument("command", choices=[
        "phase0", "phase1", "phase2", "phase3", "phase4", "phase5",
        "phase6", "phase7", "phase8", "phase9", "reproduce"
    ], help="Phase command to execute")
    
    args = parser.parse_args()
    
    if args.command == "phase0":
        phase0()
    elif args.command == "phase1":
        phase1()
    elif args.command == "phase2":
        phase2()
    elif args.command == "phase3":
        phase3()
    elif args.command == "phase4":
        phase4()
    elif args.command == "phase5":
        phase5()
    elif args.command == "phase6":
        phase6()
    elif args.command == "phase7":
        phase7()
    elif args.command == "phase8":
        phase8()
    elif args.command == "phase9":
        phase9()
    elif args.command == "reproduce":
        logger.info("Executing End-to-End Reproducible Pipeline")
        phase0()
        phase1()
        phase2()
        phase3()
        phase4()
        phase5()
        from y2h_ppi.evaluation.ablation_study import run_ablation_study
        run_ablation_study()
        phase6()
        phase7()
        phase9()
        print("[OK] Entire pipeline execution complete!")

if __name__ == "__main__":
    main()
