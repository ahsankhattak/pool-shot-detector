# modules/collision_detector.py
import itertools
import math


class CollisionDetector:
    def __init__(self, cooldown_frames=15, threshold_multiplier=1.15, min_age=25):
        self.cooldown_timer = 0
        self.cooldown_frames = cooldown_frames
        self.threshold_multiplier = threshold_multiplier
        self.min_age = min_age   # NEW: ball must exist this many frames before it can collide
        self.score = 0

    def update(self, tracked_balls, frame_index):
        new_collisions = []

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return new_collisions

        # NEW: only consider balls that have proven themselves real (old enough)
        eligible_ids = [
            bid for bid, b in tracked_balls.items()
            if b.get('age', 0) >= self.min_age
        ]

        for id1, id2 in itertools.combinations(eligible_ids, 2):
            b1, b2 = tracked_balls[id1], tracked_balls[id2]

            dx = b1['x'] - b2['x']
            dy = b1['y'] - b2['y']
            distance = math.sqrt(dx * dx + dy * dy)

            d1 = b1.get('radius', 10) * 2
            d2 = b2.get('radius', 10) * 2
            avg_diameter = (d1 + d2) / 2
            collision_threshold = avg_diameter * self.threshold_multiplier

            if distance < collision_threshold:
                self.score += 1
                self.cooldown_timer = self.cooldown_frames
                new_collisions.append((id1, id2))
                print(f"💥 COLLISION DETECTED | Frame Index: {frame_index} | Current Score: {self.score}")
                break

        return new_collisions