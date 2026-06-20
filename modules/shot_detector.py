# modules/shot_detector.py

SPEED_THRESHOLD = 1.5
STOP_FRAMES_REQUIRED = 10


class ShotDetector:
    def __init__(self):
        self.shot_active = False
        self.still_frame_count = 0
        self.cue_ball_id = None

    def update(self, tracked_balls):
        if not tracked_balls:
            return 'IDLE'

        # Identify the cue ball as the largest, most consistently tracked ball
        # (radius tends to be biggest/closest to camera and stays stable)
        if self.cue_ball_id is None or self.cue_ball_id not in tracked_balls:
            self.cue_ball_id = max(tracked_balls, key=lambda k: tracked_balls[k].get('radius', 0))

        cue = tracked_balls.get(self.cue_ball_id)
        if cue is None:
            return 'SHOT_ONGOING' if self.shot_active else 'IDLE'

        speed = (cue['vx']**2 + cue['vy']**2) ** 0.5
        moving = speed > SPEED_THRESHOLD

        if not self.shot_active and moving:
            self.shot_active = True
            self.still_frame_count = 0
            return 'SHOT_STARTED'

        if self.shot_active and not moving:
            self.still_frame_count += 1
            if self.still_frame_count >= STOP_FRAMES_REQUIRED:
                self.shot_active = False
                return 'SHOT_ENDED'
        else:
            self.still_frame_count = 0

        return 'SHOT_ONGOING' if self.shot_active else 'IDLE'