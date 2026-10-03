"""Watch a saved video with full navigation (seek bar, play/pause, frame steps).

RUN IT (from the repo root), with any saved pipeline video:

    .venv\\Scripts\\python.exe src\\ttc\\scripts\\view_video.py out\\pipeline\\Nexar_00286.mp4

Controls:
    seek bar (bottom)   click or drag anywhere on it to jump there
    SPACE               play / pause
    LEFT / RIGHT        one frame back / forward (pauses)
    A / D               one second back / forward
    Z / X               five seconds back / forward
    + / -               play faster / slower
    Q or ESC            quit
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

LEFT, RIGHT = 2424832, 2555904          # arrow key codes from cv2.waitKeyEx on Windows
WINDOW = "Video viewer: click/drag the bar, SPACE play/pause, arrows step, A/D 1 s, Z/X 5 s, +/- speed, Q quit"
BAR_H = 40                              # height of the seek bar under the video, pixels
MARGIN = 20                             # empty space left and right of the bar


def view(path: str, scale: float = 1.0) -> None:
    """Open the video at `path` in a window with a clickable seek bar."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 10.0
    # Keep every frame in memory, JPEG-compressed (about 0.2 MB each instead of
    # 4.5 MB), so jumps and steps are instant.
    frames = []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        frames.append(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])[1])
    if not frames:
        print(f"cannot read {path}")
        return
    n = len(frames)
    h, w = cv2.imdecode(frames[0], cv2.IMREAD_COLOR).shape[:2]
    state = {"pos": 0, "playing": True, "speed": 1.0, "dragging": False, "was_playing": False}

    def frame_at(x: int) -> int:
        """Frame number for a click at horizontal pixel x on the bar."""
        share = (x - MARGIN) / max(w - 2 * MARGIN, 1)
        return int(round(min(max(share, 0.0), 1.0) * (n - 1)))

    def on_mouse(event, x, y, flags, _):
        # Mouse positions arrive in picture coordinates, even if the window is resized.
        on_bar = y >= h
        if event == cv2.EVENT_LBUTTONDOWN and on_bar:
            state["dragging"], state["was_playing"] = True, state["playing"]
            state["playing"], state["pos"] = False, frame_at(x)
        elif event == cv2.EVENT_MOUSEMOVE and state["dragging"]:
            state["pos"] = frame_at(x)
        elif event == cv2.EVENT_LBUTTONUP and state["dragging"]:
            state["dragging"], state["playing"] = False, state["was_playing"]

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW, int(w * scale), int((h + BAR_H) * scale))
    cv2.setMouseCallback(WINDOW, on_mouse)
    while True:
        pos = state["pos"]
        img = cv2.imdecode(frames[pos], cv2.IMREAD_COLOR)
        # Seek bar: grey track, blue filled part up to the current frame, white knob.
        bar = np.full((BAR_H, w, 3), 30, np.uint8)
        x_now = MARGIN + int((w - 2 * MARGIN) * pos / max(n - 1, 1))
        cv2.rectangle(bar, (MARGIN, 14), (w - MARGIN, 26), (90, 90, 90), -1)
        cv2.rectangle(bar, (MARGIN, 14), (x_now, 26), (255, 140, 0), -1)
        cv2.circle(bar, (x_now, 20), 9, (255, 255, 255), -1)
        label = (f"{pos / fps:5.1f} s / {n / fps:.1f} s   frame {pos + 1}/{n}   speed x{state['speed']:g}"
                 + ("" if state["playing"] else "   PAUSED"))
        cv2.putText(img, label, (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, label, (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow(WINDOW, np.vstack([img, bar]))

        key = cv2.waitKeyEx(max(1, int(1000 / (fps * state["speed"]))) if state["playing"] else 20)
        if key in (ord("q"), 27) or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
            break
        if key == ord(" "):
            state["playing"] = not state["playing"]
            if state["playing"] and pos >= n - 1:   # at the end: start over
                state["pos"] = 0
        elif key == RIGHT:
            state["playing"], state["pos"] = False, min(pos + 1, n - 1)
        elif key == LEFT:
            state["playing"], state["pos"] = False, max(pos - 1, 0)
        elif key == ord("d"):
            state["pos"] = min(pos + int(fps), n - 1)
        elif key == ord("a"):
            state["pos"] = max(pos - int(fps), 0)
        elif key == ord("x"):
            state["pos"] = min(pos + int(5 * fps), n - 1)
        elif key == ord("z"):
            state["pos"] = max(pos - int(5 * fps), 0)
        elif key in (ord("+"), ord("=")):
            state["speed"] = min(state["speed"] * 2, 8)
        elif key == ord("-"):
            state["speed"] = max(state["speed"] / 2, 0.125)
        elif state["playing"] and not state["dragging"]:
            if pos + 1 < n:
                state["pos"] = pos + 1
            else:
                state["playing"] = False
    cv2.destroyWindow(WINDOW)


if __name__ == "__main__":
    view(sys.argv[1] if len(sys.argv) > 1 else "out/pipeline/Nexar_00286.mp4")
