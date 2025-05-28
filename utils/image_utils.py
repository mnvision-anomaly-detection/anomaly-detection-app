import numpy as np
import random
from PIL import Image

def crop_largest_rectangle(img: Image.Image) -> Image.Image:
    gray = img.convert('L')
    np_img = np.array(gray)
    mask = (np_img > 20) & (np_img < 230)
    coords = np.argwhere(mask)
    if coords.size == 0: return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    return img.crop((x0, y0, x1, y1))

def process_single_image(img: Image.Image, target_size=(128, 128)) -> np.ndarray:
    img = crop_largest_rectangle(img.convert('RGB'))
    angle = random.uniform(-10, 10)
    img = img.rotate(angle,Image.BICUBIC, expand=True)
    img = crop_largest_rectangle(img)
    img = img.resize(target_size, Image.BICUBIC)
    return np.array(img) / 255.0