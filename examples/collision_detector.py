from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
                help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]



COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))


NUM_DIODES = 22
# load our model from disk
print("loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])


def vid_stream():
    # start video
    # show FPS counter for debug
    print("starting video...")
    stream = VideoStream(src=0).start()
    time.sleep(2.0)
    fps = FPS().start()
    while (True):
        # max width of 600 pixel for video in
        f = stream.read()
        f = imutils.resize(f, width=600)

        (h, w) = f.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(f, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass blob to nn
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (probability) of nn:s prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections (unlikely)
            if confidence > args["confidence"]:
                # extract the index of the class label
                # (x, y)-coordinates of the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # # draw the prediction on the streams cur_frame
                # label = "{}: {:.2f}%".format(CLASSES[idx],
                #                              confidence * 100)
                # cv2.rectangle(f, (startX, startY), (endX, endY),
                #               COLORS[idx], 2)
                # y = startY - 15 if startY - 15 > 15 else startY + 15
                # cv2.putText(f, label, (startX, y),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
            # idx = class_label
            # 2 = bicycle
            # 6 = bus
            # 7 = car
            # 14 = motorbike
            # 15 = person

            # how wide is classified object
            obj_width = endX - startX
            obj_height = endY - startY

            #Car
            if idx == 2 or idx == 6 or idx == 7 or idx == 14:
                # draw the prediction on the streams cur_frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                                             confidence * 100)
                cv2.rectangle(f, (startX, startY), (endX, endY),
                              COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(f, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)


                if obj_width >= 1/3 * w:
                    relay_pos(startX, endX, w)
                    cv2.putText(f, 'WARNING!!!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        # show the output frame
        cv2.imshow("Output Frame", f)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # update the FPS counter
        fps.update()

    # q
    # do a bit of cleanup
    cv2.destroyAllWindows()
    stream.stop()


def relay_pos(startX, endX, w):
    w/NUM_DIODES



def img_classify(img):
    while (True):
        # max width of 400 pixel for video stream
        f = cv2.imread(img)
        f = imutils.resize(f, width=400)

        (h, w) = f.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(f, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass blob to nn
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                                             confidence * 100)
                cv2.rectangle(f, (startX, startY), (endX, endY),
                              COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(f, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)


        # show the output frame
        cv2.imshow("Output Frame", f)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()


# video stream - webcam
vid_stream()
# img = 'test_images/test3.jpg'
# img_classify(img)

# img = 'test_images/test1.jpg'
# img_classify(img)
