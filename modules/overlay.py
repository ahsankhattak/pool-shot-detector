import cv2
 
def draw_overlay(frame, tracked_balls, verdict_text=None):
    for ball in tracked_balls.values():
        center = (int(ball['x']), int(ball['y']))
        cv2.circle(frame, center, int(ball.get('radius', 10)), (0, 255, 0), 2)
 
    if verdict_text:
        cv2.putText(frame, verdict_text, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    return frame
