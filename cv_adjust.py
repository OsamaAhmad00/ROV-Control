# The core of this file is not written by me.

import cv2
import numpy as np


def nothing(x):
    pass


def x(cnt):
    global frame
    cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
    x, y, w, h = cv2.boundingRect(cnt)
    # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
    # cv2.circle(frame, (int(x+w/2), int (y+h/2)), 5, (255, 255, 255), -1)
    cv2.line(frame, (int(x + (w / 2)), y), (int(x + (w / 2)), y + h), (0, 128, 255), 1)
    return int(x + w / 2), int(y + h / 2)


def angle(contours):
    rect = cv2.minAreaRect(contours)
    (x, y), (w, h), ang = rect
    if ang < -45:
        ang = 90 + ang
    if w < h and ang > 0:
        ang = (90 - ang) * -1
    if w > h and ang < 0:
        ang = 90 + ang
    ang = int(ang)
    return ang


class CVAdjust:

    def __init__(self, camera_id=0):

        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise ValueError('There is no camera with this id.')

        cv2.namedWindow("K")
        cv2.createTrackbar("Min.Cont", "K", 500, 1000, nothing)  # the largest contour detected
        cv2.createTrackbar("Max.Cont", "K", 5000, 10000, nothing)  # the smallest contour detected

        cv2.createTrackbar("Min.dist", "K", 75, 200, nothing)  # the minimun distance in pixels
        cv2.createTrackbar("Max.dist", "K", 120, 500, nothing)  # the maximum distance in pixels

        cv2.createTrackbar("Angle", "K", 5, 15, nothing)  # min and max angle
        cv2.createTrackbar("Error", "K", 15, 100, nothing)  # min and max error

    def process_and_get_value(self):
        _, frame = self.cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blueline = cv2.inRange(hsv, (94, 80, 2), (126, 255, 255))
        kernel = np.ones((3, 3), np.uint8)
        blueline = cv2.erode(blueline, kernel, iterations=1)
        blueline = cv2.dilate(blueline, kernel, iterations=1)
        blueline = cv2.morphologyEx(blueline, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
        contours, _ = cv2.findContours(blueline, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        minArea = cv2.getTrackbarPos("Min.Cont", "K")
        maxArea = cv2.getTrackbarPos("Max.Cont", "K")
        cntsSorted = list(filter(lambda x: cv2.contourArea(x) > minArea and cv2.contourArea(x) < maxArea, contours))
        cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

        # center=(320,240)
        # setpoint=320
        # centerline1= (320,0)
        # centerline2= (320, 640)

        center = (int(frame.shape[1] / 2), int(frame.shape[0] / 2))
        setpoint = int(frame.shape[1] / 2)
        centerline1 = (int(frame.shape[1] / 2), 0)
        centerline2 = (int(frame.shape[1] / 2), int(frame.shape[1]))
        # print(frame.shape[0],frame.shape[1])
        # print(center)
        cv2.line(frame, centerline1, centerline2, (0, 255, 255), 3)
        cv2.circle(frame, center, 9, (0, 200, 200), -1)

        if len(cntsSorted) >= 2:
            largest_contour = cntsSorted[0]
            second_largest_contour = cntsSorted[1]
            (x1, y1) = x(largest_contour)
            (x2, y2) = x(second_largest_contour)
            xx = int((x1 + x2) / 2)
            yy = int((y1 + y2) / 2)

            cv2.line(frame, (xx, 0), (xx, frame.shape[1]), (0, 255, 255), 3)
            cv2.circle(frame, (int(xx), int(yy)), 9, (0, 200, 200), -1)

            error = int(xx - setpoint)  # is the distance between the center line and the line between two blue lines

            # cv2.putText(frame,"Error : "+str(error),(10, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "Error : " + str(error),
                        (int(frame.shape[0] / 480 * 10), int(frame.shape[1] / 640 * 460)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            ang = angle(largest_contour)  # is the angle of the largest contour and the vertical

            # cv2.putText(frame,"Angle : "+str(ang),(10,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
            cv2.putText(frame, "Angle : " + str(ang),
                        ((int(frame.shape[0] / 480 * 10), int(frame.shape[1] / 640 * 40))),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.line(frame, (x1, y1), (x2, y2), (150, 40, 255), 1)

            dist = x2 - x1  # is the distance between the two blue lines in pixels
            if dist < 0:
                dist = dist * -1

            # cv2.putText(frame,"Dist : "+str(dist),(450,460),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255),2)
            cv2.putText(frame, "Dist : " + str(dist),
                        (int(frame.shape[0] / 480 * 450), int(frame.shape[1] / 640 * 460)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

            if error < 0:  # elkreza
                cv2.line(frame, (xx, yy), (setpoint, yy), (255 + error, 255 + error, 255 + error), 2)
                # cv2.line(frame, (320, yy), (320, 240),(255+error,255+error,255+error),2)
                cv2.line(frame, (int(frame.shape[1] / 2), yy), (int(frame.shape[1] / 2), int(frame.shape[0] / 2)),
                         (255 + error, 255 + error, 255 + error), 2)

            else:
                cv2.line(frame, (xx, yy), (setpoint, yy), (255 - error, 255 - error, 255 - error), 2)
                # cv2.line(frame, (320, yy), (320, 240),(255-error,255-error,255-error),2)
                cv2.line(frame, (int(frame.shape[1] / 2), yy), (int(frame.shape[1] / 2), int(frame.shape[0] / 2)),
                         (255 - error, 255 - error, 255 - error), 2)

            # first compare the distance between the two lines with pixels
            # then the angle
            # then the distance between the center line and the line between the two blue lines

            mindist = cv2.getTrackbarPos("Min.dist", "K")  # taken from the trackbar
            maxdist = cv2.getTrackbarPos("Max.dist", "K")  # taken from the trackbar
            angle0 = cv2.getTrackbarPos("Angle", "K")  # taken from the trackbar
            error0 = cv2.getTrackbarPos("Error", "K")  # taken from the trackbar

            cv2.imshow("only blue", blueline)
            cv2.imshow("FINAL", frame)

            if dist > maxdist:
                print("up")  # to send letter j
                return 'j'
            if mindist > dist > 0:
                print("down")  # to send letter l
                return 'l'
            if mindist < dist < maxdist:
                if ang > angle0:
                    print("!<<<<")  # to send letter #
                    return '#'
                if ang < - angle0:
                    print(">>>>!")  # to send letter $
                    return '$'
                if - angle0 < ang < angle0:
                    if error0 < error:
                        print("left")  # to send letter s
                        return 's'
                    if error < - error0:
                        print("right")  # to send letter v
                        return 'v'
                    if - error0 < error < error0:
                        print("K")  # to send letter @
                        return '@'

    def __del__(self):
        cv2.destroyAllWindows()
        self.cap.release()

