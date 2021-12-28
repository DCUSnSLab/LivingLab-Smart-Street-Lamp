import cv2
import time

prev_time = 0
FPS = 10

video = cv2.VideoCapture("./TownCentreXVID.mp4")
fps = video.get(cv2.CAP_PROP_FPS)

print("fps :", fps)


while True:
    ret, frame = video.read()

    current_time = time.time() - prev_time

    if (ret is True) and (current_time > 1. / FPS):
        start_time = time.time()
        prev_time = time.time()

        cv2.imshow('VideoCapture', frame)
        end_time = time.time()

        #print("fps :",int(1./(end_time - start_time)))

        if cv2.waitKey(1) > 0:
            break