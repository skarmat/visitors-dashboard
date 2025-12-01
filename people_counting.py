import cv2
import numpy as np
from ultralytics import YOLO
from sort import Sort
import mediapipe as mp
import time
from datetime import datetime
import os

def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    hand_count = 0
    last_hand_time = 0
    hand_detected_prev_frame = False
    cooldown_period = 1

    # Initialize YOLO model
    model = YOLO('yolov8n.pt')

    # Initialize SORT tracker
    tracker = Sort()

    # Initialize video capture
    cap = cv2.VideoCapture(0)

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define counting line (horizontal line in the middle)
    line_y = frame_height // 2
    counting_line = [(0, line_y), (frame_width, line_y)]

    # Initialize counters
    count_in = 0
    count_out = 0
    tracked_objects = {}
    last_logged_count_in = 0  # Track last logged visitor count
    last_logged_hand_count = 0  # Track last logged IAO count

    # Add this function after the initial setup and before the main loop
    def is_hand_fully_opened(hand_landmarks):
        # Get fingertip landmarks (indices 4,8,12,16,20)
        fingertips = [hand_landmarks.landmark[i] for i in [4,8,12,16,20]]
        # Get middle palm landmark as reference
        palm = hand_landmarks.landmark[9]
        
        # Check if all fingertips are above the palm (indicating opened hand)
        fingers_opened = all(tip.y < palm.y for tip in fingertips[1:])  # excluding thumb
        
        # Check if fingers are spread apart horizontally
        fingertip_x = [tip.x for tip in fingertips]
        x_spread = max(fingertip_x) - min(fingertip_x)
        #print(f"Fingers opened: {fingers_opened}, X spread: {x_spread:.2f}")
        
        return fingers_opened and x_spread > 0.1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        # Detect people using YOLO
        results = model(frame, classes=0, verbose=False)  # class 0 is person

        # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results_hand = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Replace the hand detection block with this updated version
        if results_hand.multi_hand_landmarks:
            for hand_landmarks in results_hand.multi_hand_landmarks:
                # Check confidence score
                hand_confidence = results_hand.multi_handedness[0].classification[0].score
                
                if hand_confidence > 0.9 and is_hand_fully_opened(hand_landmarks):
                    # Draw landmarks only for valid hand detections
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    if not hand_detected_prev_frame and (current_time - last_hand_time) > cooldown_period:
                        hand_count += 1
                        last_hand_time = current_time
                    hand_detected_prev_frame = True
                else:
                    hand_detected_prev_frame = False
        else:
            hand_detected_prev_frame = False
        
        # Display the count
        # cv2.putText(frame, f'Unique hands detected: {hand_count}', (10, 60),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Extract detections
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                if conf > 0.4:  # Confidence threshold
                    detections.append([x1, y1, x2, y2, conf])

        # Update SORT tracker
        if len(detections) > 0:
            track_bbs_ids = tracker.update(np.array(detections))
        else:
            track_bbs_ids = np.empty((0, 5))

        # Draw counting line
        cv2.line(frame, counting_line[0], counting_line[1], (0, 255, 0), 2)

        # Process tracking results
        for track in track_bbs_ids:
            x1, y1, x2, y2, track_id = track
            center_y = (y1 + y2) // 2

            # Store object's position history
            if track_id not in tracked_objects:
                tracked_objects[track_id] = center_y
            else:
                previous_y = tracked_objects[track_id]
                # Check if object crossed the line
                if previous_y > line_y and center_y <= line_y:
                # if previous_y < line_y and center_y >= line_y:
                    count_in += 1
                # elif previous_y > line_y and center_y <= line_y:
                #     count_out += 1
                tracked_objects[track_id] = center_y

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {int(track_id)}", (int(x1), int(y1)-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.putText(frame, f"Visitor: {count_in}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"IAO: {hand_count}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        day = datetime.now().strftime("%Y%m%d")

        # Log Visitor event if count_in increased
        if count_in > last_logged_count_in:
            with open(f"visitors_{day}.txt", "a") as f:
                f.write(f"Visitor at {datetime.now().strftime('%H:%M:%S')}\n")
            last_logged_count_in = count_in

        # Log IAO event if hand_count increased
        if hand_count > last_logged_hand_count:
            with open(f"visitors_{day}.txt", "a") as f:
                f.write(f"IAO at {datetime.now().strftime('%H:%M:%S')}\n")
            last_logged_hand_count = hand_count

        cv2.imshow('People Counting', frame)

        # Check if it's past operating hours or quit is pressed
        now = datetime.now()
        if now.hour >= 18 or now.hour < 9:
            print("Outside operating hours (9 AM - 6 PM). Stopping program.")
            break
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quit command received. Stopping program.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return False

while True:
    now = datetime.now()
    current_hour = now.hour
    
    if 9 <= current_hour < 18:
        print(f"Starting program at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        if not main():
            time.sleep(60)
    else:
        wait_minutes = 2
        print(f"Outside operating hours. Next check in {wait_minutes} minutes. Current time: {now.strftime('%H:%M:%S')}")
        time.sleep(wait_minutes * 60)
