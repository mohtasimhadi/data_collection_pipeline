import cv2
import matplotlib.pyplot as plt

def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return
    
    frame_count = 0
    frames = []
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        frames.append(frame)
        frame_count += 1
    cap.release()
    print(f"Frames extracted: {frame_count}")
    return frames

frames1 = extract_frames("2/18443010518B880E00_5501_color.h265")
frames2 = extract_frames("2/19443010517FFD1200_5500_color.h265")
plt.imshow(frames2[120])