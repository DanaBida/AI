# Script to preprocess and prepare dataset for image analysis

"""
Preprocesses images: resize to 224x224, normalize with ImageNet stats.
"""


import os
from PIL import Image
from torchvision import transforms
from config import Config

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def preprocess_image(input_path, output_path):
	os.makedirs(os.path.dirname(output_path), exist_ok=True)
	img = Image.open(input_path).convert("RGB")
	transform = transforms.Compose([
		transforms.Resize((224, 224)),
		transforms.ToTensor(),
		transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
	])
	tensor = transform(img)
	# Save as tensor file (optional: save as image for inspection)
	# torch.save(tensor, output_path)
	# For demo, save as image
	img.save(output_path)

def preprocess_folder(input_dir, output_dir):
	for root, _, files in os.walk(input_dir):
		for file in files:
			if file.lower().endswith((".jpg", ".jpeg", ".png")):
				rel_dir = os.path.relpath(root, input_dir)
				out_dir = os.path.join(output_dir, rel_dir)
				os.makedirs(out_dir, exist_ok=True)
				preprocess_image(os.path.join(root, file), os.path.join(out_dir, file))

if __name__ == "__main__":
	input_dir = Config.RAW_DATA_DIR
	output_dir = Config.PROCESSED_DATA_DIR
	preprocess_folder(input_dir, output_dir)
