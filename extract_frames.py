import cv2

def extract_frames_from_video(input_file, output_folder):
    cap = cv2.VideoCapture(input_file)
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite(f"{output_folder}/frame_{frame_count:04d}.png", frame)
        frame_count += 1

    cap.release()
