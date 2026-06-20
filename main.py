# main.py
from modules.frame_extractor import extract_frames
from modules.ball_detector import detect_balls
from modules.ball_tracker import BallTracker
from modules.shot_detector import ShotDetector
from modules.collision_detector import CollisionDetector
from modules.event_state_machine import ShotResultTracker
from modules.overlay import draw_overlay
import cv2

VIDEO_PATH = 'data/input_videos/standard_input.mp4'

tracker = BallTracker()
shot_detector = ShotDetector()
result_tracker = ShotResultTracker()
collision_detector = CollisionDetector(cooldown_frames=15, threshold_multiplier=1.15, min_age=3)

frame_index = 0
collision_counted_this_shot = False

cv2.namedWindow('Pool Shot Detector', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Pool Shot Detector', 480, 854)

for frame, fps in extract_frames(VIDEO_PATH):
    detections = detect_balls(frame)
    tracked_balls = tracker.update(detections)

    if frame_index < 5:
        debug_positions = {
            k: (round(v['x']), round(v['y']), round(v.get('radius', 0)))
            for k, v in tracked_balls.items()
        }
        print(f"  >>> Frame {frame_index} tracked_balls: {debug_positions}")

    shot_state = shot_detector.update(tracked_balls)
    collisions = collision_detector.update(tracked_balls, frame_index)

    # Reset the "already counted" flag whenever a new shot begins or we're idle
    if shot_state == 'SHOT_STARTED' or shot_state == 'IDLE':
        collision_counted_this_shot = False

    # Only let the FIRST collision of this shot count toward the verdict
    counted_collisions = []
    if len(collisions) > 0 and not collision_counted_this_shot:
        collision_counted_this_shot = True
        counted_collisions = collisions

    verdict = result_tracker.process_frame(shot_state, counted_collisions)

    print(f"Frame {frame_index} | {shot_state} | collisions: {collisions} | counted: {counted_collisions} | balls: {len(tracked_balls)} | score: {collision_detector.score}")

    frame = draw_overlay(frame, tracked_balls, verdict)
    cv2.imshow('Pool Shot Detector', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_index += 1

cv2.destroyAllWindows()
print("Shot-by-shot results:", result_tracker.results_log)
print("Total collisions/score:", collision_detector.score)