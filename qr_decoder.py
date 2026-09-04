import io
import struct
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

SCALE_FACTOR = 4
ANCHOR_SIZE = 16
QUIET_ZONE = 2
ANCHOR_BLOCK = ANCHOR_SIZE + QUIET_ZONE


def decode_3marker_grid(grid_image_path, output_image_path="restored.png"): #restored.png is restored image name
  img_bgr = cv2.imread(grid_image_path)
  if img_bgr is None:
    print(f"Error: Could not open or find image at '{grid_image_path}'.")
    return

  gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
  
  _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
  contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  target_marker_px = ANCHOR_SIZE * SCALE_FACTOR
  candidate_corners = []

  for cnt in contours:
    approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
    if len(approx) == 4:
      x, y, w, h = cv2.boundingRect(approx)
      if abs(w - target_marker_px) < 30 and abs(h - target_marker_px) < 30:
        candidate_corners.append([x + w / 2, y + h / 2])

  if len(candidate_corners) < 3:
    print(f"Error: Could not find all 3 alignment markers (found {len(candidate_corners)}).")
    return

  pts = np.array(candidate_corners[:3], dtype=np.float32)
  
  sums = pts.sum(axis=1)
  tl = pts[np.argmin(sums)]
  
  diffs = np.diff(pts, axis=1)
  tr = pts[np.argmin(diffs)]
  bl = pts[np.argmax(diffs)]

  # Estimate Bottom-Right corner
  br = tr + (bl - tl)

  grid_width_px = int(np.linalg.norm(tr - tl))
  estimated_grid_pixel_size = grid_width_px + (ANCHOR_BLOCK * SCALE_FACTOR)
  
  # Precise anchor center mapping offsets (Anchor starts at block start, center is +8 units in)
  offset_px = 8 * SCALE_FACTOR            # Center of the 16x16 anchor relative to its block start
  edge_offset_px = (ANCHOR_BLOCK - 8) * SCALE_FACTOR  # Distance from grid edge to anchor center
  
  src_pts = np.float32([tl, tr, bl, br])
  dest_pts = np.float32([
      [offset_px, offset_px],
      [estimated_grid_pixel_size - edge_offset_px, offset_px],
      [offset_px, estimated_grid_pixel_size - edge_offset_px],
      [estimated_grid_pixel_size - edge_offset_px, estimated_grid_pixel_size - edge_offset_px]
  ])
  
  matrix = cv2.getPerspectiveTransform(src_pts, dest_pts)
  warped = cv2.warpPerspective(gray, matrix, (estimated_grid_pixel_size, estimated_grid_pixel_size))

  grid_size = estimated_grid_pixel_size // SCALE_FACTOR
  binary_chars = []

  for y in range(grid_size):
    for x in range(grid_size):
      in_tl = (y < ANCHOR_BLOCK and x < ANCHOR_BLOCK)
      in_tr = (y < ANCHOR_BLOCK and x >= grid_size - ANCHOR_BLOCK)
      in_bl = (y >= grid_size - ANCHOR_BLOCK and x < ANCHOR_BLOCK)

      if in_tl or in_tr or in_bl:
        continue

      px_val = warped[int(y * SCALE_FACTOR), int(x * SCALE_FACTOR)]
      binary_chars.append("1" if px_val < 128 else "0")

  binary_str = "".join(binary_chars)

  byte_array = bytearray()
  for i in range(0, len(binary_str), 8):
    chunk = binary_str[i:i+8]
    if len(chunk) == 8:
      byte_array.append(int(chunk, 2))

  if byte_array[0:4] != b"IMG1":
    print("Error: Invalid format or corrupted perspective warp!")
    return

  img_length = struct.unpack(">I", bytes(byte_array[4:8]))[0]
  image_bytes = bytes(byte_array[8 : 8 + img_length])

  restored_img = Image.open(io.BytesIO(image_bytes))
  restored_img.save(output_image_path)
  print(f"Success! Image decoded and saved as '{output_image_path}'")


if __name__ == "__main__":
  file_path = Path("pix_qr.png")
  if file_path.is_file():
    grid_path = file_path
  else:
    grid_path = input("Enter QR-style grid image path to decode: ").strip()

  decode_3marker_grid(grid_path)