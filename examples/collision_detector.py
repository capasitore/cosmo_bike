from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2


# example run args
# -p model/model_deploy.prototxt.txt -m model/model_deploy.caffemodel -w 600 -d True

IDX_CONFIG_ALL = [2,6,7,14,15]
IDX_CONFIG_VEHICLES = [2,6,7,14]

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
                help="minimum probability to filter out unreliable detections")
ap.add_argument("-w", "--width", type=int, default=600,
                help="max width of screen to grab")
ap.add_argument("-d", "--debug", type=bool, default=False,
                help="show the screen being grabbed, imshow")
ap.add_argument("-i", "--idxconfig", type=str, default='IDX_CONFIG_ALL',
                help="choose the IDX_CONFIG to use IDX_CONFIG_ALL for vehicles + person or IDX_CONFIG_VEHICLES for only vehicles")

args = vars(ap.parse_args())

if args["idxconfig"] == 'IDX_CONFIG_ALL':
    IDX_CONFIG = IDX_CONFIG_ALL
else:
    IDX_CONFIG = IDX_CONFIG_VEHICLES

NUM_DIODES = 22

# initialize the list of class labels MobileNet SSD was trained on
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# opencv color space BGR - bounding box colors for debugging
COLORS = {2: (255,255,0),  # bicycle - lightblue
                 6: (0,128,255),  # orange - bus
                 7: (0,0,255),  # red - car
                 14: (0,255,255),  # yellow - motorbike
                 15: (0,255,0)  # green' - person
                 }



# idx = class_label
            # 2 = bicycle
            # 6 = bus
            # 7 = car
            # 14 = motorbike
            # 15 = person


# load  model from file
print("loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])


def vid_stream():
    # start video
    print("starting video...")
    stream = VideoStream(src=0).start()
    # give time to grab a frame
    time.sleep(2.0)
    fps = FPS().start()
    while (True):
        # max width of 600 pixel for video in
        f = stream.read()
        f = imutils.resize(f, width=args["width"])

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

                # draw_prediction(confidence, endX, endY, f, idx, startX, startY)

            # how wide is classified object
            obj_width = endX - startX
            obj_height = endY - startY

            #if classified object is interesting
            # if idx == 2 or idx == 6 or idx == 7 or idx == 14 or idx==15:
            if idx in IDX_CONFIG:
                # draw the prediction on the streams cur_frame
                draw_prediction(confidence, endX, endY, f, idx, startX, startY)

                if obj_width >= 1/4 * w:
                    activate_diodes(startX, endX, w, idx)
                    draw_warning(f)

        # show the output frame
        if args["debug"]:
            cv2.imshow("Output Frame", f)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # update the FPS counter
        fps.update()
        fps.stop()
        # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    stream.stop()


def draw_warning(f):
    # draws warning on cv screen
    cv2.putText(f, 'WARNING!!!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)


def draw_prediction(confidence, endX, endY, f, idx, startX, startY):
    # draw the prediction on the streams cur_frame
    label = "{}: {:.2f}%".format(CLASSES[idx],
                                 confidence * 100)
    cv2.rectangle(f, (startX, startY), (endX, endY),
                  COLORS[idx], 2)
    y = startY - 15 if startY - 15 > 15 else startY + 15
    cv2.putText(f, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)


def get_color_for_class(idx):
    # Define colors which will be used by the example.  Each color is an unsigned
    # 32-bit value where the lower 24 bits define the red, green, blue data (each
    # being 8 bits long).
    # DOT_COLORS = [0x200000,  # red
    #               0x201000,  # orange
    #               0x202000,  # yellow
    #               0x002000,  # green
    #               0x002020,  # lightblue #
    #               0x000020,  # blue
    #               0x100010,  # purple
    #               0x200010]  # pink

    # 2 = bicycle
    # 6 = bus
    # 7 = car
    # 14 = motorbike
    # 15 = person
    color_id_dict = {2: '0x002020', #bicycle - lightblue
     6: '0x201000', #orange - bus
     7: '0x200000', #red - car
     14:'0x202000', #yellow - motorbike
     15: '0x002000' # green' - person
     }

    return color_id_dict[idx]


def activate_diodes(startX, endX, w, idx):
    #     pass 22 tuples,
    # (id, color(32 byte rgb))



    # Brightness 0-255
    brightness = 255

    width_per_diode = w/NUM_DIODES
    start_id = startX/width_per_diode
    end_id = endX/width_per_diode
    # get the diodes as tuples (i, value on/off)
    color_diode_ls = []
    color = get_color_for_class(idx)
    off_color = '0x000000' #black

    for i in range(1,NUM_DIODES + 1):
        # which diodes to activate
        if(i> start_id and i < end_id):
            color_diode_i = color
        else:
            color_diode_i =  off_color
        color_diode_ls.append(color_diode_i)
    # print(color_diode_ls)

    #TODO send tuple_ls to diode



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
            # extract the confidence (probability) of nn:s prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections (unlikely)
            if confidence > args["confidence"]:
                # extract the index of the class label
                # (x, y)-coordinates of the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw_prediction(confidence, endX, endY, f, idx, startX, startY)

            # how wide is classified object
            obj_width = endX - startX
            obj_height = endY - startY

            # if classified object is interesting
            # if idx == 2 or idx == 6 or idx == 7 or idx == 14 or idx==15:
            if idx in IDX_CONFIG:
                # draw the prediction on the streams cur_frame
                draw_prediction(confidence, endX, endY, f, idx, startX, startY)
                # activate_diodes(startX, endX, w, idx)

                if obj_width >= 1 / 4 * w:
                    activate_diodes(startX, endX, w, idx)
                    draw_warning(f)

        # show the output frame
        cv2.imshow("Output Frame", f)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()



vid_stream()
# img = '/Users/andreas/Documents/HackBike/test_images/test1.jpg'
# img_classify(img)