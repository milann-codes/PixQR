import math
import struct
from PIL import Image, ImageOps
import numpy as np

SCALE_FACTOR = 4
BORDER_SIZE = 30
ANCHOR_SIZE = 16  # 16x16 grid units
QUIET_ZONE = 2    # White buffer around the anchor
ANCHOR_BLOCK = ANCHOR_SIZE + QUIET_ZONE  # 18 units total


def create_qr_anchor():
  """Generates a QR-style concentric finder pattern (Nested squares)."""
  anchor = np.zeros((ANCHOR_SIZE, ANCHOR_SIZE), dtype=np.uint8)  # Outer black
  anchor[3:13, 3:13] = 1  # Middle white ring
  anchor[6:10, 6:10] = 0  # Center black box
  return anchor


def encode_3marker_grid(image_path, output_path="pix_qr.png"): #pix_qr.png is the name of qr image
  with open(image_path, "rb") as f:
    image_bytes = f.read()

  magic = b"IMG1"
  length_header = struct.pack(">I", len(image_bytes))
  full_payload = magic + length_header + image_bytes
  
  binary_str = "".join(format(byte, "08b") for byte in full_payload)
  total_bits = len(binary_str)

  three_anchors_area = 3 * (ANCHOR_SIZE * ANCHOR_SIZE)
  grid_size = max(ANCHOR_BLOCK * 2 + 8, math.ceil(math.sqrt(total_bits + three_anchors_area)))
  
  grid = np.ones((grid_size, grid_size), dtype=np.uint8)
  qr_anchor = create_qr_anchor()

  def place_anchor(start_y, start_x):
    # White quiet zone
    grid[start_y:start_y + ANCHOR_BLOCK, start_x:start_x + ANCHOR_BLOCK] = 1
    # Concentric QR-style anchor positioned inside the quiet zone block
    grid[start_y:start_y + ANCHOR_SIZE, start_x:start_x + ANCHOR_SIZE] = qr_anchor

  # Place 3 QR-style anchors (Top-Left, Top-Right, Bottom-Left)
  place_anchor(0, 0)
  place_anchor(0, grid_size - ANCHOR_BLOCK)
  place_anchor(grid_size - ANCHOR_BLOCK, 0)

  bit_idx = 0
  for y in range(grid_size):
    for x in range(grid_size):
      in_tl = (y < ANCHOR_BLOCK and x < ANCHOR_BLOCK)
      in_tr = (y < ANCHOR_BLOCK and x >= grid_size - ANCHOR_BLOCK)
      in_bl = (y >= grid_size - ANCHOR_BLOCK and x < ANCHOR_BLOCK)

      if in_tl or in_tr or in_bl:
        continue
      
      if bit_idx < len(binary_str):
        grid[y, x] = 0 if binary_str[bit_idx] == "1" else 1
        bit_idx += 1
      else:
        grid[y, x] = 1

  img = Image.fromarray(grid * 255, mode="L")
  img_scaled = img.resize((grid_size * SCALE_FACTOR, grid_size * SCALE_FACTOR), Image.NEAREST)
  img_final = ImageOps.expand(img_scaled, border=BORDER_SIZE, fill="white")
  
  img_final.save(output_path)
  print(f"Success! QR-style 3-marker grid saved to '{output_path}' (Grid Size: {grid_size}x{grid_size})")


if __name__ == "__main__":
  source_path = input("Enter source image path to encode: ").strip()
  encode_3marker_grid(source_path)