import time
import numpy as np
from PIL import Image
from multiprocessing import Pool


def edge_filter(fragment):
    img = fragment.astype(np.float32)
    p = np.pad(img, 1, mode='edge')
    gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
    gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
    mag = np.sqrt(gx ** 2 + gy ** 2)
    return np.clip(mag, 0, 255).astype(np.uint8)


def split_image(image, n):
    arr = np.array(image.convert('L'))
    return np.array_split(arr, n, axis=0)


def merge_image(fragments):
    return Image.fromarray(np.vstack(fragments))


if __name__ == '__main__':
    image_path = 'obraz1.jpg'
    n = 4

    image = Image.open(image_path)
    fragments = split_image(image, n)

    t = time.time()
    seq = [edge_filter(f) for f in fragments]
    print(f"Sekwencyjnie: {time.time() - t:.3f} s")

    t = time.time()
    with Pool(n) as p:
        results = p.map(edge_filter, fragments)
    print(f"Rownolegle (Pool({n})): {time.time() - t:.3f} s")

    merge_image(results).save(f'processed_{image_path}.png')