"""QR decoding service powered by OpenCV."""
import cv2

class QRReader:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def decode(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("The selected file could not be opened as an image.")
        decoded, points, _ = self.detector.detectAndDecode(image)
        if not decoded:
            raise ValueError("No readable QR code was detected in this image.")
        return decoded
