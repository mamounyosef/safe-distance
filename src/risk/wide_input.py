"""The 16:9 model input (256 x 448, shapes kept): the frame preparation and the patch V-JEPA 2 needs for it.

WHY: the current input squashes the 1280 x 720 dashcam frame into a square (things look 1.8x narrower). Here the
frame keeps its shape: shrunk to 455 x 256, then 448 x 256 cut out of the middle (only ~3 px off each side), so both
sides are whole multiples of V-JEPA 2's 16 x 16-pixel patches (28 x 16 patches per frame).

THE PATCH: V-JEPA 2 tells each token where it is with rotary position encoding (RoPE): every token gets 3 numbers,
(time slot, row, column), worked out from its place in the token list. V-JEPA 2's code assumes a SQUARE grid
(16 x 16 patches, from config.crop_size = 256), so for a 16-row x 28-column grid it would hand out wrong rows and
columns. patch_positions() makes every attention layer (encoder AND predictor) use the real grid instead. Nothing
else in the model depends on the picture's shape (the patch embedding is a convolution: it works on any size).

Checked on the CPU by scripts/check_wide_input.py (with grid 16 x 16 the patched code gives exactly the original
outputs; with 16 x 28 every token gets the right (time, row, column)).
"""

from __future__ import annotations

import numpy as np

# ---- CONFIG ----
WIDE_H, WIDE_W = 256, 448                            # model input: 16 x 28 patches of 16 x 16 pixels
PATCH = 16                                           # V-JEPA 2's patch size (pixels)
MEAN = np.array([0.485, 0.456, 0.406], np.float32)  # ImageNet colour mean / spread: what V-JEPA 2 was pretrained on
STD = np.array([0.229, 0.224, 0.225], np.float32)
# ----------------


def wide_frame(frame, cv2_module=None) -> np.ndarray:
    """One original frame (any size, e.g. 1280 x 720, RGB uint8) -> 256 x 448 RGB uint8, shape kept.
    Shrink so the height is 256 (1280 x 720 -> 455 x 256), then cut 448 out of the middle of the width."""
    import cv2
    h, w = frame.shape[:2]
    new_w = int(round(w * WIDE_H / h))                               # 1280 x 256 / 720 = 455
    small = cv2.resize(frame, (new_w, WIDE_H), interpolation=cv2.INTER_AREA)   # INTER_AREA: best for shrinking
    x0 = (new_w - WIDE_W) // 2                                        # (455 - 448) / 2 = 3 px off the left
    return small[:, x0:x0 + WIDE_W]


def normalise(frames_uint8):
    """B x T x 256 x 448 x 3 uint8 (torch, any device) -> B x T x 3 x 256 x 448 float: scale to 0..1, then ImageNet
    normalise. The same last steps as V-JEPA 2's own processor, without its resize / square crop."""
    import torch
    x = frames_uint8.float() / 255.0
    mean = torch.tensor(MEAN, device=x.device)
    std = torch.tensor(STD, device=x.device)
    x = (x - mean) / std
    return x.permute(0, 1, 4, 2, 3).contiguous()                     # colour channel before height / width


def _position_ids(self, x, masks=None):
    """Replacement for VJEPA2RopeAttention.get_position_ids that knows the grid is grid_h rows x grid_w columns.

    Tokens are numbered time slot by time slot, row by row, left to right. So token number id is at:
        time slot = id // (rows x columns)      row = (id within its slot) // columns      column = what is left
    V-JEPA 2's original does the same with rows = columns = 16; here they come from the real picture.
    """
    import torch
    if masks is not None:                                            # the predictor passes the tokens' numbers
        ids = masks.unsqueeze(1).repeat(1, self.num_attention_heads, 1)
    else:                                                            # the encoder: tokens 0, 1, 2, ... in order
        ids = torch.arange(x.size(1), device=x.device)
    grid_h = getattr(self, "grid_h", self.grid_size)                 # a layer never patched keeps the square grid
    grid_w = getattr(self, "grid_w", self.grid_size)
    per_slot = grid_h * grid_w                                       # tokens per time slot (16 x 28 = 448)
    slot = ids // per_slot
    within = ids - per_slot * slot                                   # number inside its time slot
    row = within // grid_w
    col = within - grid_w * row
    return slot, row, col


def patch_positions(model, height: int, width: int) -> int:
    """Make every V-JEPA 2 attention layer in `model` (encoder and predictor) use a height/16 x width/16 grid.
    Returns how many layers were patched (BADAS-Open: 24 encoder + 12 predictor = 36).

    The replacement goes on the attention CLASS once (not as a separate bound method on each of the 36 layers):
    torch.compile handles a plain class method well, while per-object methods crashed it (segmentation fault on
    Modal). Each layer only stores its own grid size (two whole numbers)."""
    n = 0
    for m in model.modules():
        if type(m).__name__ == "VJEPA2RopeAttention":
            m.grid_h, m.grid_w = height // PATCH, width // PATCH
            type(m).get_position_ids = _position_ids              # same function for every layer
            n += 1
    return n
