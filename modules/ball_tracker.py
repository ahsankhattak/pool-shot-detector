# modules/ball_tracker.py
from scipy.spatial.distance import cdist
import numpy as np


class BallTracker:
    def __init__(self, max_match_distance=40, miss_limit=8):
        self.tracked_balls = {}
        self.next_id = 0
        self.max_match_distance = max_match_distance
        self.miss_limit = miss_limit

    def update(self, detections):
        if not self.tracked_balls:
            for d in detections:
                self._add_new_ball(d)
            return self._get_active_balls()

        prev_points = np.array([[b['x'], b['y']] for b in self.tracked_balls.values()])
        prev_ids = list(self.tracked_balls.keys())
        new_points = np.array([[d['x'], d['y']] for d in detections]) if detections else np.empty((0, 2))

        matched_new = set()
        matched_old = set()

        if len(new_points) > 0:
            distances = cdist(prev_points, new_points)
            for i, row in enumerate(distances):
                j = np.argmin(row)
                if row[j] < self.max_match_distance and j not in matched_new:
                    old = self.tracked_balls[prev_ids[i]]
                    new_x, new_y = detections[j]['x'], detections[j]['y']
                    old['vx'] = new_x - old['x']
                    old['vy'] = new_y - old['y']
                    old['x'], old['y'] = new_x, new_y
                    old['radius'] = detections[j].get('radius', old.get('radius', 10))
                    old['misses'] = 0
                    old['age'] = old.get('age', 0) + 1   # NEW: ball survived another frame
                    matched_new.add(j)
                    matched_old.add(prev_ids[i])

        for pid in prev_ids:
            if pid not in matched_old:
                self.tracked_balls[pid]['misses'] = self.tracked_balls[pid].get('misses', 0) + 1

        self.tracked_balls = {
            k: v for k, v in self.tracked_balls.items()
            if v.get('misses', 0) < self.miss_limit
        }

        for j, d in enumerate(detections):
            if j not in matched_new:
                self._add_new_ball(d)

        return self._get_active_balls()

    def _add_new_ball(self, d):
        self.tracked_balls[self.next_id] = {
            'x': d['x'], 'y': d['y'],
            'vx': 0, 'vy': 0,
            'radius': d.get('radius', 10),
            'misses': 0,
            'age': 0,   # NEW: starts at 0, increments each frame it survives
        }
        self.next_id += 1

    def _get_active_balls(self):
        return self.tracked_balls