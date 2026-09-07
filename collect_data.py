import os
# os.environ["MEDIAPIPE_GPU"] = "0"  
if "MEDIAPIPE_GPU" in os.environ:
    del os.environ["MEDIAPIPE_GPU"]

import cv2
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from geometry import extract_feature
from dataset_collector import DatasetCollector

latest_result = None
#async callback fn
def on_hand_landmarks_ready(result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_mp: int):
    global latest_result
    latest_result = result

def run_collector():
    #initialize dataset collector
    collector = DatasetCollector()

    #Gesture Mapping  and Keyboard input - labels
    GESTURE_NAMES = {0: 'Fist', 1: 'Open Palm', 2: 'Pinch', 3: 'Peace Sign'}
    KEY_MAP = {ord('0'): 0, ord('1'): 1, ord('2'): 2, ord('3'): 3}

    # set Hand Landmarker attributes
    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path='hand_landmarker.task',
            delegate=python.BaseOptions.Delegate.GPU
        ),
        # base_options=python.BaseOptions(model_asset_path='hand_landmarker.task'),
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=2,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        result_callback=on_hand_landmarks_ready
    )

    # set my landamrker and hand connections 
    HAND_CONNECTIONS = vision.HandLandmarksConnections.HAND_CONNECTIONS

    W, H = 640, 480

    # Attempt camera initiailization with 2 fallbacks (COMMENTED OUT)
    # for cam_index in range(3):
    #     # Initialize the landmarker using the context manager to automatically clear memory leaks
    #     # with vision.HandLandmarker.create_from_options(options) as landmarker:
    #     temp_cap = cv2.VideoCapture(cam_index)
    #     if temp_cap.isOpened():
    #         #successful hardware identification and reading
    #         ret, test_frame = temp_cap.read()
    #         if ret:
    #             print(f"Successfully connected to Camera Index: {cam_index}")
    #             cap = temp_cap
    #             break
    #         temp_cap.release()

    # Direct camera initialization at index 0
    cap = cv2.VideoCapture(0)

    #configure camera res
    try:
        if not cap.isOpened():
            raise RuntimeError("No functional camera detected on index 0")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

        with vision.HandLandmarker.create_from_options(options) as landmarker:
            print("\n=== DATASET COLLECTION RUNNING ===")
            print("Press '0' : Record Fist")
            print("Press '1' : Record Open Palm")
            print("Press '2' : Record Pinch")
            print("Press '3' : Record Peace Sign")
            print("Press 'q' : Quit Collector Mode\n")

            last_record_time = 0.0
            RECORD_INTERVAL = 0.1  # Record at most 1 frame every 100ms (10 samples/sec)
            last_timestamp_ms = 0

            # capture live video frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab video feed")
                    break

                # mirror
                frame = cv2.flip(frame, 1)

                # define ROI for 300x300 pixel box
                box_x1, box_y1 = 170, 90 
                box_x2, box_y2 = 470, 390
                cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (255, 0, 0), 2)
                cv2.putText(frame, "Place Hand here", (box_x1, box_y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                # convert to RGBA (4-channel) for macOS Metal compatibility
                rgba_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGBA, data=rgba_frame)

                timestamp_ms = int(time.time() * 1000)
                if timestamp_ms <= last_timestamp_ms:
                    timestamp_ms = last_timestamp_ms + 1
                last_timestamp_ms = timestamp_ms

                landmarker.detect_async(mp_image, timestamp_ms)

                active_landmarks = None

                # Process detected hand landmarks
                if latest_result and latest_result.hand_landmarks and len(latest_result.hand_landmarks) > 0:
                    active_landmarks = latest_result.hand_landmarks[0]

                    points = []
                    # Convert normalized coordinates (0.0 - 1.0) to pixel coordinates
                    for lm in active_landmarks:
                        px, py = int(lm.x * W), int(lm.y * H)
                        points.append((px, py))
                        cv2.circle(frame, (px, py), 5, (0, 255, 0), -1)

                    # Draw skeleton connection lines
                    for conn in HAND_CONNECTIONS:
                        start_pt = points[conn.start]
                        end_pt = points[conn.end]
                        cv2.line(frame, start_pt, end_pt, (0, 0, 255), 2)

                # Recorded counts
                cv2.putText(frame, "Recorded Samples:", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                y_offset = 55
                for key_code, name in GESTURE_NAMES.items():
                    count = collector.recorded_counts.get(key_code, 0)
                    text = f"Key [{key_code}] {name} : {count}"
                    cv2.putText(frame, text, (10, y_offset), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y_offset += 20

                # Render window
                cv2.imshow("Webcam Feed - Gesture Area", frame)

                # keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                # Save frame sample if '0', '1', '2', or '3' is pressed
                elif key in KEY_MAP:
                    current_time = time.time()
                    # Only record if the throttle cooldown has elapsed
                    if current_time - last_record_time >= RECORD_INTERVAL:
                        if active_landmarks:
                            label = KEY_MAP[key]
                            features = extract_feature(active_landmarks)
                            collector.save_sample(features, label)
                            last_record_time = current_time
                            print(f"[RECORDING] [{GESTURE_NAMES[label]}] Total: {collector.recorded_counts[label]}")
                        else:
                            print("No hand detected! Position hand inside camera view.")

    except Exception as e:
        print(f"An error occurred during video processing: {e}")

#release resources
    finally:
        if cap is not None and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        print("Collector Mode Exited cleanly.")

# Protect standalone execution
if __name__ == "__main__":
    run_collector()