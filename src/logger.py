import logging
import os

os.makedirs("output", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(module)s | %(message)s',
    handlers=[
        logging.FileHandler("output/system_trace.log"), # persistent action log
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SunriseAMC")