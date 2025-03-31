import cv2
import mediapipe as mp
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Function to count fingers with better thumb detection
def count_fingers(hand_landmarks, hand_label):
    finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
    thumb_tip = 4
    count = 0

    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    
    # Thumb detection based on hand side
    if hand_label == "Right":
        if hand_landmarks.landmark[thumb_tip].x > hand_landmarks.landmark[thumb_tip - 2].x:
            count += 1
    else:  
        if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 2].x:
            count += 1

    return count

# Start Video Capture
cap = cv2.VideoCapture(0)

operation = None
stage = "select_operation"
operand1 = None
operand2 = None
last_time = time.time()
result = None
delay = 3  # Reduced selection delay for better response

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    fingers = []
    hand_label = None

    if results.multi_hand_landmarks and results.multi_handedness:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            hand_label = results.multi_handedness[i].classification[0].label
            fingers.append(count_fingers(hand_landmarks, hand_label))

    current_time = time.time()

    # Step 1: Select Operation
    if stage == "select_operation":
        cv2.putText(frame, "Show Fingers to Select Operation:", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, "1-Add | 2-Sub | 3-Mul | 4-Div", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        if len(fingers) == 1 and current_time - last_time > delay:
            operation = fingers[0]
            if operation in [1, 2, 3, 4]:  
                stage = "select_operand1"
                last_time = time.time()

    # Step 2: Select First Operand
    elif stage == "select_operand1":
        cv2.putText(frame, "Show Fingers for First Number:", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        if len(fingers) == 1 and current_time - last_time > delay:
            operand1 = fingers[0]
            stage = "select_operand2"
            last_time = time.time()

    # Step 3: Select Second Operand
    elif stage == "select_operand2":
        cv2.putText(frame, "Show Fingers for Second Number:", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        if len(fingers) == 1 and current_time - last_time > delay:
            operand2 = fingers[0]
            stage = "display_result"
            last_time = time.time()

    # Step 4: Perform Calculation and Display
    elif stage == "display_result":
        op_text = ""
        if operation == 1:
            result = operand1 + operand2
            op_text = "+"
        elif operation == 2:
            result = operand1 - operand2
            op_text = "-"
        elif operation == 3:
            result = operand1 * operand2
            op_text = "x"
        elif operation == 4:
            result = operand1 / operand2 if operand2 != 0 else "Undefined"
            op_text = "/"

        # Display result
        cv2.putText(frame, f"{operand1} {op_text} {operand2} = {result}", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Hold result for 3 seconds
        if current_time - last_time > delay:
            stage = "select_operation"
            last_time = time.time()
            operation, operand1, operand2, result = None, None, None, None

    # Show video feed
    cv2.imshow("Hand Gesture Arithmetic", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


