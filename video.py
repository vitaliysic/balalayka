import cv2
cap = cv2.VideoCapture('v.mp4')
# The device number might be 0 or 1 depending on the device and the webcam
# cap.open(0, cv2.CAP_DSHOW)
while(True):
    ret, frame = cap.read()
    if ret:
        cv2.imshow("frame", frame)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()