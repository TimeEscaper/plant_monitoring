import cv2
# See https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/

def is_image_blurred(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    return fm < 95.0
