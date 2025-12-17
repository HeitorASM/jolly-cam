import cv2
import numpy as np
import random
import time
import pygame
pygame.mixer.init()
hoho_sound = pygame.mixer.Sound("assets/ho-ho-ho-merry-christmas.mp3")
hoho_sound.set_volume(0.8)
muted = False
next_hoho_time = time.time() + random.randint(10, 30)
def overlay_png(background, overlay, x, y, w=None, h=None):
    bg_h, bg_w = background.shape[:2]

    if w and h:
        overlay = cv2.resize(overlay, (w, h), interpolation=cv2.INTER_AREA)

    h, w = overlay.shape[:2]

    if x < 0 or y < 0 or x + w > bg_w or y + h > bg_h:
        return background

    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            background[y:y+h, x:x+w, c] = (
                alpha * overlay[:, :, c] +
                (1 - alpha) * background[y:y+h, x:x+w, c]
            )
    else:
        background[y:y+h, x:x+w] = overlay

    return background

def rotate_image(img, angle):
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img

class Snow:
    def __init__(self, width, height, count=140):
        self.width = width
        self.height = height
        self.snowflakes = [
            [random.randint(0, width), random.randint(0, height), random.randint(1, 3)]
            for _ in range(count)
        ]

    def update_and_draw(self, frame):
        for flake in self.snowflakes:
            x, y, speed = flake
            cv2.circle(frame, (x, y), speed, (255, 255, 255), -1)
            flake[1] += speed

            if flake[1] > self.height:
                flake[0] = random.randint(0, self.width)
                flake[1] = 0
                flake[2] = random.randint(1, 3)

goro = cv2.imread("assets/goro.png", cv2.IMREAD_UNCHANGED)
corner = cv2.imread("assets/corner.png", cv2.IMREAD_UNCHANGED)
banner_top = cv2.imread("assets/banner_top.png", cv2.IMREAD_UNCHANGED)

corner_tr = rotate_image(corner, 90)
corner_br = rotate_image(corner, 180)
corner_bl = rotate_image(corner, 270)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
cap = cv2.VideoCapture(0)

ret, frame = cap.read()
cam_h, cam_w = frame.shape[:2]

snow = Snow(cam_w, cam_h)

window_name = "Jolly Cam"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

print("Teclas:")
print("  Q → sair")
print("  M → mutar / desmutar som")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    if not muted and time.time() >= next_hoho_time:
        hoho_sound.play()
        next_hoho_time = time.time() + random.randint(10, 30)

    banner_h = int(h * 0.18)
    frame = overlay_png(frame, banner_top, 0, 0, w, banner_h)

    corner_size = int(min(w, h) * 0.2)

    frame = overlay_png(frame, corner, 0, 0, corner_size, corner_size)
    frame = overlay_png(frame, corner_tr, w - corner_size, 0, corner_size, corner_size)
    frame = overlay_png(frame, corner_br, w - corner_size, h - corner_size, corner_size, corner_size)
    frame = overlay_png(frame, corner_bl, 0, h - corner_size, corner_size, corner_size)

    snow.update_and_draw(frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, fw, fh) in faces:
        goro_w = fw
        goro_h = int(goro_w * goro.shape[0] / goro.shape[1])
        goro_x = x
        goro_y = y - goro_h + int(fh * 0.15)

        frame = overlay_png(frame, goro, goro_x, goro_y, goro_w, goro_h)
    cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    elif key == ord("m"):
        muted = not muted
        if muted:
            pygame.mixer.stop()
            print("Som mutado")
        else:
            print("Som ativado")

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
