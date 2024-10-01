import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def detect_number_plate(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    number_plate_contour = None
    max_area = 0

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)

        if len(approx) == 4 and area > max_area:
            number_plate_contour = approx
            max_area = area

    if number_plate_contour is not None:
        cv2.drawContours(img, [number_plate_contour], -1, (0, 255, 0), 3)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [number_plate_contour], 0, 255, -1)
        number_plate = cv2.bitwise_and(img, img, mask=mask)
        x, y, w, h = cv2.boundingRect(number_plate_contour)
        cropped_plate = img[y:y+h, x:x+w]
        cv2.imshow('Original Image', img)
        cv2.imshow('Number Plate', cropped_plate)
        cv2.imwrite('detected_number_plate.jpg', cropped_plate)
    
        number_plate_text = pytesseract.image_to_string(cropped_plate, config='--psm 8')
        print("Detected Number Plate Text:", number_plate_text.strip())

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return cropped_plate, number_plate_text.strip()
    else:
        print("Number plate not detected.")
        return None, None

image_path = 'img/car_img.jpg'
cropped_plate, number_plate_text = detect_number_plate(image_path)
