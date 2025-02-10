import os
import cv2
import pytesseract
import difflib

OUTPUT_DIR = os.path.abspath("../target")

FRAME_LIMIT = 5

def preprocess_image(frame_image):
    # convert to grayscale
    image_gray = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
    thresh = 0
    image_threshold = cv2.threshold(image_gray, thresh, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]

    return image_threshold

def process_frame(frame_image, frame_counter):
    """ Processes the provided video frame.
    
        frame_image - video frame
        frame_counter - frame number in the stream
    """
    # convert frame to BW
    bw_image = preprocess_image(frame_image)

    # Specify structure shape and kernel size. 
    # Kernel size increases or decreases the area 
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect 
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 18))

    # Applying dilation on the threshold image
    result_image = bw_image
    dilation = cv2.dilate(result_image, rect_kernel, iterations = 1)

    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, 
                                                    cv2.CHAIN_APPROX_NONE)

    all_text = ""
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
#        print (f"X={x}  Y={y}  w={w}  {h}")

        cropped = result_image[y:y + h, x:x + w]
        text = pytesseract.image_to_string(cropped)
#        all_text += text.strip().replace("\n", " ").strip() + " "
        all_text += text.strip() + "\n"

        result_image = cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # build the output filename
    output_filename = OUTPUT_DIR + ("/frame%d.jpg" % frame_counter)

    # display text
    print ("=========================================================")
    print (f"===    FRAME # {frame_counter}   /   {output_filename}")
    print ()
#    print (all_text)
    print ()

    # save the file
    cv2.imwrite(output_filename, result_image)

    return all_text

def compare_frame_text(last, this):
    differ = difflib.Differ()
    diff = differ.compare(last.splitlines(keepends=True), this.splitlines(keepends=True))

    #diff = difflib.ndiff(last, this)
    
    return ''.join(diff)

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
    last_frame_text = None
    while success: 
        success, frame_image = video_capture.read() 
        frame_counter += 1

        # process the video frame
        this_frame_text = None
        if success:
            this_frame_text = process_frame(frame_image, frame_counter)

        # compare last frame to this frame
        if last_frame_text is not None and this_frame_text is not None:
            print ("Differences:")
            diff_text = compare_frame_text(last_frame_text, this_frame_text)
            print (diff_text)
        last_frame_text = this_frame_text
    
        if frame_counter >= FRAME_LIMIT:
            break


if __name__ == '__main__': 
    read_video_stream("../samples/clip1.mov") 
