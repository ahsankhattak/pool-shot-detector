import cv2
def extract_frames(video_path):
    """
    Opens the video file and yields one frame at a time.
    'frame' = a single image (numpy array) representing one moment in time.
    """
    cap = cv2.VideoCapture(video_path)          # opens the video file
    fps = cap.get(cv2.CAP_PROP_FPS)              # frames per second of the video
 
    while cap.isOpened():
        ret, frame = cap.read()                  # ret=False means video ended
        if not ret:
                        break
        yield frame, fps                          # send this frame onward to Module 2
 
    cap.release()                                 

