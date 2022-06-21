import sys
import os
import glob
import numpy as np
import cv2
from PIL import Image
import imageio
import subprocess
import shutil

# ---------------------------- CONFIGURATION ----------------------------

time_for_one_frame_gif = 0.15 # How long a frame lasts in the final gif. Default is 0.15
time_for_one_frame_vid = 0.18 # How long a frame lasts in the final gif. Default is 0.15

# ---------------- DO NOT TOUCH ANYTHING UNDER THIS LINE ----------------
last_point = None

def select_point(event, x, y, flags, param):
    global last_point
    if event == cv2.EVENT_LBUTTONDOWN:
        last_point = (x, y)

# Get the folder that the user has dropped on the script
dropped_folder = sys.argv[1]
# dropped_folder = 'C:\\Users\\Adrien\\Desktop\\00067953'
print(dropped_folder)

dest_folder_gifs = f'{dropped_folder}/gifs_manual'
dest_folder_vids = f'{dropped_folder}/vids_manual'

if not os.path.exists(dest_folder_gifs):
        print('Creating gifs folder.')
        os.mkdir(dest_folder_gifs)
else:
    print('The gifs folder already exists.')

if not os.path.exists(dest_folder_vids):
        print('Creating vids folder.')
        os.mkdir(dest_folder_vids)
else:
    print('The vids folder already exists.')

shutil.copy("./180.bat", dest_folder_gifs)
shutil.copy("./CW.bat", dest_folder_gifs)
shutil.copy("./CCW.bat", dest_folder_gifs)

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

        imgbgr = np.zeros(img.shape, dtype=img.dtype)
        imgbgr[:,:,0] = img[:,:,2]
        imgbgr[:,:,1] = img[:,:,1]
        imgbgr[:,:,2] = img[:,:,0]

        last_point = None
        name = names[k]
        cv2.imshow(name, imgbgr)
        cv2.setMouseCallback(name, select_point)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        points.append(last_point)
        x, y = last_point
        xs.append(x)
        ys.append(y)
        print(f'x={x}, y={y}')

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
    
    gif_dest = f'{dest_folder_gifs}/{i}.gif'
    vid_dest = f'{dest_folder_vids}/{i}.mp4'
    smoothed_vid_dest = f'{dest_folder_vids}/{i}-smooth.mp4'

    imageio.mimsave(gif_dest, frames, duration=time_for_one_frame_gif)
    imageio.mimsave(vid_dest, frames*5, fps=1/time_for_one_frame_vid)

    # Smooth vid :
    subprocess.Popen(['ffmpeg', '-i', vid_dest, '-crf', '10', '-vf', 'minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1', smoothed_vid_dest])
