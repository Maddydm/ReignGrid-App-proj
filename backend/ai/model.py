import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from typing import Optional

class DoubleConv(nn.Module):
    """(Conv2D -> BatchNorm -> ReLU) * 2"""
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.net(x)

class UNet(nn.Module):
    """
    Lightweight U-Net architecture tailored for cadastral parcel boundary detection.
    Extracts spatial boundary features using encoder-decoder architecture with skip connections.
    """
    def __init__(self, in_channels: int = 3, out_channels: int = 1, base_features: int = 32):
        super().__init__()
        f = base_features
        # Encoder (Contracting Path)
        self.inc = DoubleConv(in_channels, f)
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(f, f * 2))
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(f * 2, f * 4))
        self.down3 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(f * 4, f * 8))

        # Decoder (Expanding Path)
        self.up1 = nn.ConvTranspose2d(f * 8, f * 4, kernel_size=2, stride=2)
        self.conv1 = DoubleConv(f * 8, f * 4)

        self.up2 = nn.ConvTranspose2d(f * 4, f * 2, kernel_size=2, stride=2)
        self.conv2 = DoubleConv(f * 4, f * 2)

        self.up3 = nn.ConvTranspose2d(f * 2, f, kernel_size=2, stride=2)
        self.conv3 = DoubleConv(f * 2, f)

        # Output boundary mask (1 channel probability)
        self.outc = nn.Sequential(
            nn.Conv2d(f, out_channels, kernel_size=1),
            nn.Sigmoid()
        )

        self._initialize_weights()

    def _initialize_weights(self):
        """Kaiming normal initialization for conv layers."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)

        x = self.up1(x4)
        # Handle shape differences if any
        if x.shape[2:] != x3.shape[2:]:
            x = F.interpolate(x, size=x3.shape[2:], mode='bilinear', align_corners=True)
        x = torch.cat([x3, x], dim=1)
        x = self.conv1(x)

        x = self.up2(x)
        if x.shape[2:] != x2.shape[2:]:
            x = F.interpolate(x, size=x2.shape[2:], mode='bilinear', align_corners=True)
        x = torch.cat([x2, x], dim=1)
        x = self.conv2(x)

        x = self.up3(x)
        if x.shape[2:] != x1.shape[2:]:
            x = F.interpolate(x, size=x1.shape[2:], mode='bilinear', align_corners=True)
        x = torch.cat([x1, x], dim=1)
        x = self.conv3(x)

        logits = self.outc(x)
        return logits

class BoundarySegmenter:
    """Wrapper that runs U-Net segmentation and boundary detection."""
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = UNet(in_channels=3, out_channels=1, base_features=24).to(self.device)
        self.model.eval()

    def predict_boundaries(self, tensor: torch.Tensor, original_dims: tuple, img_rgb: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Run inference on the image tensor and combine with edge cues to yield
        a high-fidelity boundary probability mask.
        """
        orig_h, orig_w = original_dims
        with torch.no_grad():
            tensor = tensor.to(self.device)
            # Run U-Net forward pass
            pred = self.model(tensor)
            pred_np = pred.squeeze().cpu().numpy()
            
            # Crop back to original dimensions
            pred_cropped = pred_np[:orig_h, :orig_w]

        # Combine with morphological gradient / Canny features for sharp cadastral delineations
        if img_rgb is not None:
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, threshold1=40, threshold2=120) / 255.0
            # Blend deep features with edge detection
            blended = 0.5 * pred_cropped + 0.5 * canny
            return np.clip(blended, 0.0, 1.0).astype(np.float32)

        return pred_cropped.astype(np.float32)
