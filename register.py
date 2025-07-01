import cv2
import os

name = input("Enter your name: ").strip()
folder = "registered_faces"
os.makedirs(folder, exist_ok=True)

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imshow("Captured", frame)
    cv2.imwrite(f"{folder}/{name}.jpg", frame)
    print(f"{name}.jpg saved in {folder}")
cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()
