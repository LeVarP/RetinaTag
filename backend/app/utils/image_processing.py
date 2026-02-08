"""
Image processing utilities for OCT B-Scan Labeler.
Handles 16-bit to 8-bit conversion with normalization and format conversion.
"""

from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from PIL import Image


def load_16bit_image(image_path: Path) -> np.ndarray:
    """
    Load a 16-bit image from disk as numpy array.

    Args:
        image_path: Path to 16-bit image file

    Returns:
        numpy array with 16-bit data

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image format is not supported
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        img = Image.open(image_path)
        # Convert to numpy array, preserving 16-bit depth
        img_array = np.array(img, dtype=np.uint16)
        return img_array
    except Exception as e:
        raise ValueError(f"Failed to load image {image_path}: {e}")


def normalize_percentile(
    img_array: np.ndarray,
    low_percentile: float = 1.0,
    high_percentile: float = 99.0
) -> np.ndarray:
    """
    Normalize image using percentile-based clipping.
    Robust to outliers (hot pixels, noise).

    Args:
        img_array: Input image array (any bit depth)
        low_percentile: Lower percentile for clipping (default: 1.0)
        high_percentile: Upper percentile for clipping (default: 99.0)

    Returns:
        Normalized 8-bit image array (0-255)
    """
    # Calculate percentile values
    p_low = np.percentile(img_array, low_percentile)
    p_high = np.percentile(img_array, high_percentile)

    # Avoid division by zero
    if p_high - p_low == 0:
        # Image is constant, return mid-gray
        return np.full(img_array.shape, 128, dtype=np.uint8)

    # Normalize to 0-255 range
    normalized = (img_array - p_low) / (p_high - p_low) * 255
    # Clip to valid range and convert to uint8
    normalized = np.clip(normalized, 0, 255).astype(np.uint8)

    return normalized


def normalize_fixed_window(
    img_array: np.ndarray,
    window_min: int = 0,
    window_max: int = 65535
) -> np.ndarray:
    """
    Normalize image using fixed intensity window.
    Useful when consistent windowing is needed across images.

    Args:
        img_array: Input image array (any bit depth)
        window_min: Minimum intensity value
        window_max: Maximum intensity value

    Returns:
        Normalized 8-bit image array (0-255)
    """
    if window_max - window_min == 0:
        return np.full(img_array.shape, 128, dtype=np.uint8)

    # Normalize to 0-255 range
    normalized = (img_array - window_min) / (window_max - window_min) * 255
    # Clip to valid range and convert to uint8
    normalized = np.clip(normalized, 0, 255).astype(np.uint8)

    return normalized


def convert_16bit_to_8bit(
    img_array: np.ndarray,
    method: str = "percentile",
    **kwargs
) -> np.ndarray:
    """
    Convert 16-bit image to 8-bit with specified normalization method.

    Args:
        img_array: Input 16-bit image array
        method: Normalization method ('percentile' or 'fixed_window')
        **kwargs: Additional arguments for normalization method
            For 'percentile': low_percentile, high_percentile
            For 'fixed_window': window_min, window_max

    Returns:
        Normalized 8-bit image array

    Raises:
        ValueError: If method is not supported
    """
    if method == "percentile":
        low = kwargs.get("low_percentile", 1.0)
        high = kwargs.get("high_percentile", 99.0)
        return normalize_percentile(img_array, low, high)
    elif method == "fixed_window":
        w_min = kwargs.get("window_min", 0)
        w_max = kwargs.get("window_max", 65535)
        return normalize_fixed_window(img_array, w_min, w_max)
    else:
        raise ValueError(f"Unsupported normalization method: {method}")


def save_preview_image(
    img_array: np.ndarray,
    output_path: Path,
    format: str = "webp",
    quality: int = 85
) -> None:
    """
    Save 8-bit image array to disk in specified format.

    Args:
        img_array: 8-bit image array
        output_path: Path where preview will be saved
        format: Output format ('webp', 'png', 'jpeg')
        quality: Quality for lossy formats (0-100, higher is better)

    Raises:
        ValueError: If format is not supported
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create PIL Image from array
    img = Image.fromarray(img_array, mode='L')  # 'L' mode for grayscale

    # Save with appropriate settings
    format_lower = format.lower()
    if format_lower == "webp":
        img.save(output_path, "WEBP", quality=quality, method=6)
    elif format_lower == "png":
        img.save(output_path, "PNG", optimize=True)
    elif format_lower in ("jpeg", "jpg"):
        img.save(output_path, "JPEG", quality=quality, optimize=True)
    else:
        raise ValueError(f"Unsupported output format: {format}")


def generate_preview(
    source_path: Path,
    output_path: Path,
    format: str = "webp",
    quality: int = 85,
    normalization_method: str = "percentile",
    **norm_kwargs
) -> Path:
    """
    Complete pipeline: load 16-bit image, normalize to 8-bit, save preview.

    Args:
        source_path: Path to source 16-bit image
        output_path: Path where preview will be saved
        format: Output format ('webp', 'png', 'jpeg')
        quality: Quality for lossy formats (0-100)
        normalization_method: 'percentile' or 'fixed_window'
        **norm_kwargs: Additional normalization parameters

    Returns:
        Path to generated preview file

    Raises:
        FileNotFoundError: If source image doesn't exist
        ValueError: If normalization or format is invalid
    """
    # Load 16-bit image
    img_16bit = load_16bit_image(source_path)

    # Convert to 8-bit
    img_8bit = convert_16bit_to_8bit(img_16bit, method=normalization_method, **norm_kwargs)

    # Save preview
    save_preview_image(img_8bit, output_path, format=format, quality=quality)

    return output_path


def get_image_info(image_path: Path) -> dict:
    """
    Get information about an image file.

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with image metadata (width, height, mode, format)

    Raises:
        FileNotFoundError: If image doesn't exist
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format,
            "size_bytes": image_path.stat().st_size,
        }
