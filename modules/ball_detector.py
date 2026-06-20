# modules/ball_detector.py
import cv2
import numpy as np


def detect_balls(frame, table_mask=None):
    """
    Detects balls using color-segmentation (non-felt blobs) + contour
    shape analysis. No dataset/training required.

    Felt color is auto-sampled from the center of the frame each call,
    so this works regardless of table color (green, blue, red, etc.)
    instead of assuming green.

    Also removes duplicate detections where a smaller blob (often a
    glare/highlight spot) sits inside a larger real ball detection.
    """
    if table_mask is not None:
        frame = cv2.bitwise_and(frame, frame, mask=table_mask)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- Auto-detect felt color from a patch near the center of the frame ---
    h, w = hsv.shape[:2]
    cy, cx = h // 2, w // 2
    pad = 25
    sample = hsv[max(0, cy - pad):cy + pad, max(0, cx - pad):cx + pad]

    avg_hue = float(np.median(sample[:, :, 0]))
    avg_sat = float(np.median(sample[:, :, 1]))
    avg_val = float(np.median(sample[:, :, 2]))

    hue_margin = 15
    lower_hue = avg_hue - hue_margin
    upper_hue = avg_hue + hue_margin

    sat_floor = max(30, avg_sat - 70)
    val_floor = max(20, avg_val - 80)

    if lower_hue < 0 or upper_hue > 179:
        # Hue wraps around (e.g. red felt near hue 0/179) — combine two masks
        lower1 = np.array([0, sat_floor, val_floor])
        upper1 = np.array([min(179, upper_hue % 180), 255, 255])
        lower2 = np.array([max(0, lower_hue % 180), sat_floor, val_floor])
        upper2 = np.array([179, 255, 255])
        felt_mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
    else:
        lower_felt = np.array([lower_hue, sat_floor, val_floor])
        upper_felt = np.array([upper_hue, 255, 255])
        felt_mask = cv2.inRange(hsv, lower_felt, upper_felt)

    non_felt = cv2.bitwise_not(felt_mask)

    kernel = np.ones((3, 3), np.uint8)
    non_felt = cv2.morphologyEx(non_felt, cv2.MORPH_OPEN, kernel, iterations=1)
    non_felt = cv2.morphologyEx(non_felt, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(non_felt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    balls = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 40 or area > 9000:
            continue

        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if radius < 6 or radius > 75:
            continue

        circle_area = np.pi * (radius ** 2)
        roundness = area / circle_area
        if roundness < 0.55:
            continue

        balls.append({'x': float(x), 'y': float(y), 'radius': float(radius)})

    # Remove smaller detections that are mostly inside a bigger one —
    # these are almost always glare/highlight spots on the SAME ball,
    # not a second real ball.
    balls.sort(key=lambda b: b['radius'], reverse=True)
    filtered = []
    for b in balls:
        is_inside_bigger = False
        for kept in filtered:
            dx = b['x'] - kept['x']
            dy = b['y'] - kept['y']
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < kept['radius'] * 0.9:
                is_inside_bigger = True
                break
        if not is_inside_bigger:
            filtered.append(b)

    return filtered