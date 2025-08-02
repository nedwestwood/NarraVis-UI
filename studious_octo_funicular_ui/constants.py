from pathlib import Path

# Toggle this flag to switch between local and S3 mode
USE_S3 = True  # Set to False for local development

# Color palette for labeling
PALETTE = {
    "HERO": "#ADD8E6",
    "VILLAIN": "#FF7F7F",
    "VICTIM": "#FFFFC5",
    "BENEFICIARY": "#90EE90",
    "default": "#808080",
    "event": "#CBC3E3",
}

# LOCAL PATHS
DATA_DIR = Path("./data/") if not USE_S3 else None
OUTPUT_DATA_DIR = DATA_DIR / "output/" if DATA_DIR else None
VIDEO_DATA_DIR = DATA_DIR / "videos/" if DATA_DIR else None

# S3 CONFIGURATION
S3_BUCKET = "narravis-ui-data"
S3_REGION = "eu-west-2"
S3_BASE_PREFIX = "data"  # base folder in the bucket

S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"
