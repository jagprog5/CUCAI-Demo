"""
John Giorshev
2020-03-03

Demo for CUCAI presentation.
"""

import cv2
import numpy as np
import os

HEAT_MAP = "HEATMAP"
FILE_NAME = "street.mp4"
MODE_FRAME_DIFF = 0
MODE_MOTION = 1
MODE_COLORIZED = 2
RESET_THRESHOLD = 400
FULL_SCREEN = True

def main():
    motion = None
    previous_frame = None
    mode = 0
    frame_count = 0
    camera_active = True

    if FULL_SCREEN:
        cv2.namedWindow(HEAT_MAP, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(HEAT_MAP, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
        cv2.setWindowProperty(HEAT_MAP, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    print("Opening camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error opening camera!")
        exit(1)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            if camera_active:
                print("Camera disconnected!")
                break
            else:
                print("Video ended. Switching back to camera...")
                cap = cv2.VideoCapture(0)
                previous_frame = None
                motion = None
                camera_active = True
                continue
            
        
        # flip horizontally. Make it like a mirror
        if camera_active:
            frame = cv2.flip(frame, 1)
        
        if previous_frame is not None:
            diff = highlight_difference(previous_frame, frame, 1)
            if motion is None:
                motion = np.zeros(diff.shape[:2], np.uint8)
            motion += diff
            
            if mode == MODE_FRAME_DIFF:
                max = np.amax(diff)
                if max != 0:
                    cv2.imshow(HEAT_MAP, diff * 255)
            else:
                scaled_motion = get_scaled_motion(motion)
                if mode == MODE_MOTION:
                    cv2.imshow(HEAT_MAP, scaled_motion)
                elif mode == MODE_COLORIZED:
                    colorized_motion = create_colormap(scaled_motion, frame)
                    cv2.imshow(HEAT_MAP, colorized_motion)
            
            if camera_active:
                frame_count += 1
                if frame_count > RESET_THRESHOLD:
                    frame_count = 0
                    motion = None
                if frame_count % 50 == 0:
                    print(frame_count)

            char = cv2.waitKey(1) & 0xFF
            if char == ord(' '):
                mode += 1
                if mode >= 3:
                    mode = 0
            elif char == ord('m'):
                motion = None
            elif char == ord('t'):
                # toggle to/from video and camera feeds
                camera_active = not camera_active
                motion = None
                previous_frame = None
                frame_count = 0
                cap = cv2.VideoCapture(0 if camera_active else get_same_dir_path(FILE_NAME))
                continue
            elif char == ord('q') or char == 27: # 27 is esc
                break
        previous_frame = frame

    # always on exit
    cap.release()
    
# returns arr of type float64
def get_scaled_motion(motion):
    max = np.amax(motion)
    if max == 0:
        print("No motion accumulated yet!")
        return motion
    img = motion / max
    return img

def highlight_difference(img_input_1, img_input_2, color):
    img = cv2.absdiff(img_input_1, img_input_2)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 60, color, cv2.THRESH_BINARY)[1]
    return img

def create_colormap(scaled_motion, raw_frame):
    colored_motion = cv2.applyColorMap((scaled_motion * 255).astype(np.uint8), cv2.COLORMAP_JET)
    result_overlay = cv2.addWeighted(raw_frame, 0.5, colored_motion, 0.5, 0)
    return result_overlay

def get_same_dir_path(file):
    if not os.path.exists(file):
        print("Couldn't find video file!")
        exit(1)
        return None
    dir = os.path.dirname(os.path.realpath(__file__))
    return dir + "\\" + file

if __name__ == '__main__':
    main()