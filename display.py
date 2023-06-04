import numpy as np
import cv2
class display:
    def __init__(self, image):
        self.image = image

    def display_content(self, name, content,x, y):
        if 'angle' in name:
            cv2.putText(self.image, f'{name}: {content:.0f} degress', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2, cv2.LINE_AA)
        else:
            cv2.putText(self.image, f'{name}: {content}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2, cv2.LINE_AA)

    def draw_axis(self):
        if isinstance(self.image, np.ndarray):
            image_height, image_width, _ = self.image.shape
            cv2.line(self.image, (image_width // 2, 0), (image_width // 2, image_height), (255, 0, 0), 2)  # vertical line
            cv2.line(self.image, (0, image_height // 2), (image_width, image_height // 2), (255, 0, 0), 2)  # horizontal line
        else:
            raise ValueError("Invalid image input. Please provide a valid numpy array.")