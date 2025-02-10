import os
import cv2
import numpy as np

OUTPUT_DIR = os.path.abspath("../target")

FRAME_LAG = 1

def convert_frame_to_bw(frame_image):
    vid_gray = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
    thresh = 127
    vid_bw = cv2.threshold(vid_gray, thresh, 255, cv2.THRESH_BINARY)[1]

    return vid_bw


def process_frame(frame_image, frame_counter, last_image):
    """ Processes the provided video frame.
    
        frame_image - video frame
        frame_counter - frame number in the stream
    """
    # "subtract" prior frame from new frame
    if last_image is not None:
#        delta_frame = np.bitwise_xor(frame_image, last_image)
        delta_frame = frame_image - last_image
        output_filename = OUTPUT_DIR + ("/frame%d.jpg" % frame_counter)
        cv2.imwrite(output_filename, delta_frame)


def read_video_stream(path):
    """ Processes the provided video stream or file.
    
        path - path to video file
    """
    # validate arguments
    if path is None or len(path) == 0:
        print ("Input path is empty!")
        return
    if not os.path.exists(path):
        print (f"Input file does not exist: {path}")
        return

    # prepare output directory
    print (f"Setting up output directory: {OUTPUT_DIR}")
    if not os.path.exists(OUTPUT_DIR):
        print ("Creating output directory...")
        os.mkdir(OUTPUT_DIR)
        print ("Output directory created!")
    print ()

	# create OpenCV video capture object 
    video_capture = cv2.VideoCapture(path) 

    # process video, frame by frame
    frame_counter = 0
    success = True
    last_bw_frame = None
    while success: 
        success, frame_image = video_capture.read() 
        frame_counter += 1

        # process the video frame
        if success and (frame_counter % FRAME_LAG == 0):
            # convert frame to BW
            current_bw_frame = convert_frame_to_bw(frame_image)

            process_frame(current_bw_frame, frame_counter, last_bw_frame)
            last_bw_frame = current_bw_frame


if __name__ == '__main__': 
    read_video_stream("../samples/clip1.mov") 
