import cv2

cam = cv2.VideoCapture(0)

while True:
    ret, image = cam.read()
    cv2.imshow('Image-Test', image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
        
cam.release()
cv2.destroyAllWindows()