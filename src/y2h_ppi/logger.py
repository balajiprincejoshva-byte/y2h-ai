import logging
import sys
from pathlib import Path

def setup_logger(name: str = "y2h_ppi", log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """Set up structured logging to both console and log file."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        # Console Handler
        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setLevel(level)
        c_format = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
        
        # File Handler
        f_handler = logging.FileHandler(log_path / "y2h_ppi.log", encoding="utf-8")
        f_handler.setLevel(level)
        f_format = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
        
    return logger

logger = setup_logger()
