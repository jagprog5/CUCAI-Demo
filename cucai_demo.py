"""
John Giorshev
2020-03-07

Demo for CUCAI presentation.
"""

import cv2
import numpy as np
import os

# const
MODE_NORMAL = 0
MODE_FRAME_DIFF = 1
MODE_MOTION = 2
MODE_COLORIZED = 3
HEAT_MAP = "HEATMAP"

# change as needed
FILE_NAMES = ["street.mp4","intersection_trimmed_lowres.mp4"]
MODE_DELAYS = [30, 20, 17, 10]
RESET_THRESHOLD = 400
FULL_SCREEN = True
CAMERA_DEFAULT = False
VID_START_INDEX = 0

def main():
    motion = None
    previous_frame = None
    mode = 0
    frame_count = 0
    camera_active = CAMERA_DEFAULT
    vid_index = VID_START_INDEX

    if FULL_SCREEN:
        cv2.namedWindow(HEAT_MAP, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(HEAT_MAP, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    if camera_active:
        print("Opening camera...")
    cap = cv2.VideoCapture(0 if camera_active else get_same_dir_path(FILE_NAMES[0]))
    handle_if_open_failed(cap, camera_active)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            if camera_active:
                print("Camera disconnected!")
                break
            else:
                if CAMERA_DEFAULT:
                    print("Video ended. Switching back to camera...")
                    camera_active = True
                    cap = cv2.VideoCapture(0)
                else:
                    print("Video ended. Restarting video...")
                    cap = cv2.VideoCapture(get_same_dir_path(FILE_NAMES[vid_index]))
                handle_if_open_failed(cap, camera_active)
                
                # reset vals
                previous_frame = None
                motion = None
                continue
        
        if camera_active:
            frame = cv2.flip(frame, 1) # flip horizontally. Make it like a mirror
        
        if previous_frame is not None:
            diff = highlight_difference(previous_frame, frame, 1)
            if motion is None:
                motion = np.zeros(diff.shape[:2], np.uint8)
            motion += diff
            
            if mode == MODE_NORMAL:
                cv2.imshow(HEAT_MAP, frame)
            elif mode == MODE_FRAME_DIFF:
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
                # periodically clear motion
                if frame_count > RESET_THRESHOLD:
                    frame_count = 0
                    motion = None

            char = cv2.waitKey(MODE_DELAYS[mode]) & 0xFF
            if char == ord(' '):
                mode += 1
                if mode >= 4:
                    mode = 0
            elif char == ord('m'):
                motion = None
            elif char == ord('t'):
                # toggle to/from video and camera feeds
                camera_active = not camera_active

                # reset vals
                motion = None
                previous_frame = None
                frame_count = 0

                cap = cv2.VideoCapture(0 if camera_active else get_same_dir_path(FILE_NAMES[vid_index]))
                handle_if_open_failed(cap, camera_active)
                continue
            elif char == ord('y') and not camera_active:
                # toggle to next video if already showing videos
                vid_index += 1
                if vid_index >= len(FILE_NAMES):
                    vid_index = 0
                
                # reset vals
                motion = None
                previous_frame = None
                frame_count = 0

                cap = cv2.VideoCapture(get_same_dir_path(FILE_NAMES[vid_index]))
                handle_if_open_failed(cap, camera_active)
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
    dir = os.path.dirname(os.path.realpath(__file__))
    return dir + "\\" + file

def handle_if_open_failed(cap, camera_active):
    if not cap.isOpened():
        if camera_active:
            print("Error opening camera device!")
        else:
            print("Error finding video file!")
        exit(1)

if __name__ == '__main__':
    main()