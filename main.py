import sys
import os
import glob
import numpy as np
import cv2
from PIL import Image
import imageio

# ---------------------------- CONFIGURATION ----------------------------

time_for_one_frame = 0.15 # How long a frame lasts in the final gif. Default is 0.15

# ---------------- DO NOT TOUCH ANYTHING UNDER THIS LINE ----------------
last_point = None

def select_point(event, x, y, flags, param):
    global last_point
    if event == cv2.EVENT_LBUTTONDOWN:
        last_point = (x, y)

# Get the folder that the user has dropped on the script
dropped_folder = sys.argv[1]
# dropped_folder = 'C:\\Users\\Adrien\\Desktop\\Code\\Nimslo_Gif_Maker\\00056355'
print(dropped_folder)

dest_folder = f'{dropped_folder}/gifs'
if not os.path.exists(dest_folder):
        print('Creating gifs folder.')
        os.mkdir(dest_folder)
else:
    print('The gifs folder already exists.')

# Iterate over all images with tiff-like extension in the folder
grabbed_files = glob.glob(f'{dropped_folder}/*.tif')
grabbed_files += glob.glob(f'{dropped_folder}/*.tiff')
grabbed_files += glob.glob(f'{dropped_folder}/*.jpg')
grabbed_files += glob.glob(f'{dropped_folder}/*.jpeg')

# Modulo to prevent overshooting
for i in range(0, len(grabbed_files) - len(grabbed_files)%4, 4):
    imgs = []
    for k in range(4):
        imgs.append(np.array(Image.open(grabbed_files[i+k])))

    names = []
    for k in range(4):
        names.append(os.path.basename(grabbed_files[i+k]))

    print(f'Working on images {names[0]}, {names[1]}, {names[2]} and {names[3]}.')

    points = []
    xs = []
    ys = []
    for k, img in enumerate(imgs):
        last_point = None
        name = names[k]
        cv2.imshow(name, img)
        cv2.setMouseCallback(name, select_point)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        points.append(last_point)
        x, y = last_point
        xs.append(x)
        ys.append(y)
        print(f'{x=}, {y=}')

    frames = []
    height_of_one_frame, width_of_one_frame, depth = imgs[0].shape
    width = min(xs) + width_of_one_frame - max(xs)
    height = min(ys) + height_of_one_frame - max(ys)
    x_align = min(xs)
    y_align = min(ys)

    for k in range(4):
        frame = np.zeros((height, width))
        frame = imgs[k][ys[k] - y_align:ys[k] - y_align+height, xs[k] - x_align:xs[k] - x_align+width]
        frames.append(frame)
    
    frame1 = frames[1]
    frame2 = frames[2]
    frames.append(frame2)
    frames.append(frame1)
    
    # for k, frame in enumerate(frames):
    #     tiff.imwrite(f'frame_{i+k}.tiff', frame)

    imageio.mimsave(f'{dest_folder}/{i}.gif', frames, duration=time_for_one_frame)
