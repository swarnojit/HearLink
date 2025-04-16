import cv2

for i in range(5):  # Check first 5 camera indexes
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Camera found at index {i}")
        cap.release()
    else:
        print(f"❌ No camera at index {i}")
