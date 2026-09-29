import cv2
import numpy as np
import torch
from pathlib import Path
from typing import Tuple, Dict, Any

class ImagePreprocessor:
    """
    Cadastral drone/satellite imagery preprocessor.
    Applies CLAHE contrast enhancement, edge-preserving smoothing,
    and tiling/normalization for deep learning segmentation.
    """
    def __init__(self, target_size: Tuple[int, int] = (512, 512)):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))

    def load_image(self, file_path: str) -> np.ndarray:
        """Load image as RGB numpy array."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found at {file_path}")
        img_bgr = cv2.imread(str(path))
        if img_bgr is None:
            raise ValueError(f"Unable to read image at {file_path}")
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    def enhance_contrast(self, img_rgb: np.ndarray) -> np.ndarray:
        """Apply CLAHE on the L-channel in LAB color space to enhance field boundary edges."""
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        enhanced_l = self.clahe.apply(l)
        merged = cv2.merge((enhanced_l, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

    def smooth_edges(self, img_rgb: np.ndarray) -> np.ndarray:
        """Apply bilateral filtering to remove crop noise while preserving parcel borders."""
        return cv2.bilateralFilter(img_rgb, d=7, sigmaColor=50, sigmaSpace=50)

    def preprocess(self, file_path: str) -> Dict[str, Any]:
        """
        Full preprocessing pipeline returning original image, enhanced image,
        and normalized PyTorch tensor.
        """
        raw_rgb = self.load_image(file_path)
        orig_h, orig_w = raw_rgb.shape[:2]

        # Enhance contrast & filter noise
        enhanced = self.enhance_contrast(raw_rgb)
        smoothed = self.smooth_edges(enhanced)

        # Pad or resize to multiple of 32 for U-Net architecture
        pad_h = (32 - (orig_h % 32)) % 32
        pad_w = (32 - (orig_w % 32)) % 32
        padded = cv2.copyMakeBorder(smoothed, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT)

        # Normalize to [0, 1] tensor (B, C, H, W)
        tensor = torch.from_numpy(padded).permute(2, 0, 1).float() / 255.0
        tensor = tensor.unsqueeze(0)  # Add batch dimension

        return {
            "raw_image": raw_rgb,
            "preprocessed_image": smoothed,
            "tensor": tensor,
            "original_dims": (orig_h, orig_w),
            "padded_dims": padded.shape[:2],
        }
