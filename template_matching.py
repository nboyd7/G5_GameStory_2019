import cv2
from imutils.contours import sort_contours

import video_handler
import numpy
import imutils


commentator_stream_fp = ''

# https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
# return the resized image according to the scale
def scale_image(gray, w, h):
    # loop over the scales of the image

    for scale in numpy.linspace(0.1, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
        #r = gray.shape[1] / float(resized.shape[1])

        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < w or resized.shape[1] < h:
            break

        return resized

def draw_box(edged, maxLoc, w, h):
    clone = numpy.dstack([edged, edged, edged])
    cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                  (maxLoc[0] + w, maxLoc[1] + h), (0, 0, 255), 2)
    return clone


def match_template(stream_fp, frame_fp, frame_number):
    cap = video_handler.read_video(stream_fp)

    #read the video
    cap.set(1, frame_number - 1)
    #ret, frame = cap.read()

    # get template info
    template = cv2.imread(frame_fp, 0)
    w, h = template.shape[::-1]

    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        box_extraction(gray, '/frames')

        # display_score_frame(frame)
        resized = scale_image(gray, w, h)

        edged = cv2.Canny(resized, 50, 200)

        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(res)


        loc = numpy.where(res >= 0.7)
        for pt in zip(*loc[::-1]):
           cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 3)

        #cv2.imshow("Match Result", draw_box(edged, maxLoc, w, h))

        if ret == True:
            # Display the resulting frame
            cv2.imshow('Stream', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Break the loop
        else:
            break

    # When everything done, release the video capture object
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()

def box_extraction(gray, cropped_dir_path):
    img = gray

    (thresh, img_bin) = cv2.threshold(img, 128, 255,
                                      cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding the image

    img_bin = 255 - img_bin  # Invert the image
    cv2.imshow("Image bin", img_bin)

    # Defining a kernel length
    kernel_length = numpy.array(img).shape[1] // 40

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))

    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))

    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect verticle lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
    cv2.imshow("verticle_lines.jpg", verticle_lines_img)

    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
    cv2.imshow("horizontal_lines.jpg", horizontal_lines_img)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha


    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # For Debugging
    # Enable this line to see verticle and horizontal lines in the image which is used to find boxes
    cv2.imshow("img_final_bin.jpg", img_final_bin)

    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(
        img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort all the contours by top to bottom.
    #(contours, boundingBoxes) = sort_contours(contours, method="top-to-bottom")
    idx = 0

    #print(contours)

    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)

        # If the box height is greater then 20, widht is >80, then only save it as a box in "cropped/" folder.
        if (( w > 400 and w < 615) and (h >  200 and h < 300)):
            #print(w, h)
            idx += 1
            new_img = img[y:y + h, x:x + w]
            cv2.imshow('Box extraction', new_img)
            #cv2.imwrite(cropped_dir_path + str(idx) + '.png', new_img)
        #else:
         #   print("BAD: ", w, h)


if __name__ == '__main__':
    match_template('/Volumes/Other 1/2018-03-02_P11.mp4', 'frames/frame291121-2.jpg', 717691)




