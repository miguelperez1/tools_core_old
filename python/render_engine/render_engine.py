import os
import random
import math
import cv2

def render(width, height, pos, frame):
    pixel_color = []

    # r = int((float(j) / float(width)) * 255)
    # g = int((float(i) / float(height)) * 255)
    # b = 255

    # r = int(abs(math.sin(pos[1] * .05)) * 255)
    # g = int(abs(math.sin(pos[0] * .05)) * 255)
    # b = int((float(frame) / 48.0) * 255)

    r = int(random.random() * 255)
    g = int(random.random() * 255)
    b = int(random.random() * 255)

    return r, g, b


def main():
    width, height = 1920, 1080

    frames = 48

    for frame in range(frames):
        file_path = r"F:\test\image.{0}.ppm".format(frame)

        if os.path.isfile(file_path):
            os.remove(file_path)

        f = open(file_path, 'w')

        f.write("P3\n{0} {1}\n255\n".format(width, height))

        for i in range(height):
            for j in range(width):
                pos = (i, j)
                pixel_color = render(width, height, pos, frame)

                f.write("{0} {1} {2}\n".format(pixel_color[0], pixel_color[1], pixel_color[2]))

        f.close()
        im = Image.open(file_path)
        im.save(file_path.replace("ppm", "jpg"))

        print("{} done".format(file_path))

    # os.startfile(file_path)


if __name__ == '__main__':
    main()
