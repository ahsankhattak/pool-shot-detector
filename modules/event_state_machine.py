class ShotResultTracker:
    def __init__(self):
        self.collision_happened_this_shot = False
        self.results_log = []          # stores every shot's final verdict
 
    def process_frame(self, shot_state, collisions):
        """
        shot_state: 'SHOT_STARTED' / 'SHOT_ONGOING' / 'SHOT_ENDED' / 'IDLE' (from Module 4)
        collisions: list of colliding ball-id pairs this frame (from Module 5)
        """
        if shot_state == 'SHOT_STARTED':
            self.collision_happened_this_shot = False   # reset for the new shot
 
        if collisions:                                    # any collision marks this shot a hit
            self.collision_happened_this_shot = True
 
        if shot_state == 'SHOT_ENDED':
            verdict = 'POINT' if self.collision_happened_this_shot else 'NO POINT'
            self.results_log.append(verdict)
            return verdict
 
        return None   # no verdict yet -- shot still in progress
