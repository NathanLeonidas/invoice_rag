import cv2
import pytesseract
from pytesseract import Output

# Si besoin sous Windows
#pytesseract.pytesseract.tesseract_cmd = r'C:\Users\nlewy\AppData\Local\Programs\Tesseract-OCR'

# Charger l'image
image = cv2.imread('./receipt_00008.png')  # Remplace par le chemin vers ton image

# Effectuer l'OCR avec les données détaillées
data = pytesseract.image_to_data(image, output_type=Output.DICT)

# Afficher chaque mot détecté avec sa boîte
n_boxes = len(data['text'])
for i in range(n_boxes):
    if int(data['conf'][i]) > 60:  # Confiance > 60%
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        text = data['text'][i]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 1)

# Afficher l'image résultante
cv2.imshow('OCR avec bounding boxes', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
