# Script to download Kaggle datasets for property room classification

"""
Downloads Kaggle dataset for property room classification.
Requires Kaggle API credentials (kaggle.json).
"""


import os
import subprocess
from config import Config

def download_kaggle_dataset(dataset: str, download_path: str):
	"""Download a Kaggle dataset using the Kaggle CLI."""
	os.makedirs(download_path, exist_ok=True)
	cmd = [
		"kaggle", "datasets", "download", "-d", dataset, "-p", download_path, "--unzip"
	]
	subprocess.run(cmd, check=True)

if __name__ == "__main__":
	dataset = Config.KAGGLE_DATASET
	download_path = Config.RAW_DATA_DIR
	download_kaggle_dataset(dataset, download_path)
