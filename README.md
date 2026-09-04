# PixQR

A custom Python utility for encoding raw image data into high-density 3-marker QR matrix images and reconstructing the original image from the decoded binary payload.

---

## Features

- **Custom Binary Header Protocol:** Encodes image byte streams with magic bytes (`IMG1`) and length headers for safe, deterministic decoding.
- **Concentric 3-Marker Alignment:** Generates custom QR-style finder patterns (Top-Left, Top-Right, Bottom-Left) surrounded by quiet zones for perspective tracking.
- **Computer Vision Extraction:** Utilizes OpenCV contour detection and perspective transformation matrices to align, deskew, and sample grid data.
- **Scalable Grid Size:** Dynamically calculates matrix bounds based on input image byte size.

---

## Tech Stack

- **Python 3.8+**
- **OpenCV (`opencv-python`):** Image processing, contour detection, and perspective transformation.
- **Pillow (`PIL`):** Image file read/write operations, scaling, and canvas padding.
- **NumPy:** High-performance matrix manipulation for bit placement.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/milann-codes/PixQR.git
   cd PixQR
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Encode an Image into a PixQR Matrix
Run the encoder script to convert any target image file into a generated matrix file (`pix_qr.png`):

```bash
python encoder.py
```
*Prompt:* Enter the path to your source image (e.g., `image.jpg`).

### 2. Decode a PixQR Matrix back to the Original Image
Run the decoder script on a generated matrix image to extract and reconstruct the original image file (`restored.png`):

```bash
python decoder.py
```
*Prompt:* Enter the path to your QR grid image (e.g., `pix_qr.png`).

---

