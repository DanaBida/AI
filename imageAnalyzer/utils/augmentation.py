# Data augmentation utilities for image analysis

"""
Augmentation pipeline: RandomResizedCrop, HorizontalFlip, ±10° rotation, ColorJitter, blur, RandomErasing
"""

import torchvision.transforms as T

def get_augmentation_pipeline():
	return T.Compose([
		T.RandomResizedCrop(224, scale=(0.8, 1.0)),
		T.RandomHorizontalFlip(),
		T.RandomRotation(10),
		T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
		T.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
		T.ToTensor(),
		T.RandomErasing(p=0.25, scale=(0.02, 0.2)),
	])
