import sys
import os
import glob
import numpy as np
import cv2
from PIL import Image
import imageio
import matplotlib.pyplot as plt
import subprocess
import tifffile as tiff
from skimage.transform import resize
import shutil

# ---------------------------- CONFIGURATION ----------------------------

time_for_one_frame_gif = 0.15 # How long a frame lasts in the final gif. Default is 0.15
time_for_one_frame_vid = 0.18 # How long a frame lasts in the final gif. Default is 0.15

# ---------------- DO NOT TOUCH ANYTHING UNDER THIS LINE ----------------

def find_begin(profile):
    for i, val in enumerate(profile):
        if val != 0:
            return i+1

def find_end(profile):
    profile = np.flip(profile)
    dist_to_end = find_begin(profile)
    return len(profile) - dist_to_end

def match_images_cv(img1, img2):

    # Convert images to grayscale
    im1_gray = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

    # Find size of image1
    sz = img1.shape

    # Define the motion model
    warp_mode = cv2.MOTION_TRANSLATION 

    # Define 2x3 or 3x3 matrices and initialize the matrix to identity
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
        warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Specify the number of iterations.
    number_of_iterations = 200

    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = 1e-10;

    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

    # Run the ECC algorithm. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria, inputMask=None, gaussFiltSize=7)

    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        # Use warpPerspective for Homography
        im2_aligned = cv2.warpPerspective (img2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else :
        # Use warpAffine for Translation, Euclidean and Affine
        im2_aligned = cv2.warpAffine(img2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);

    return im2_aligned

# Get the folder that the user has dropped on the script
dropped_folder = sys.argv[1]
# dropped_folder = 'C:\\Users\\Adrien\\Desktop\\test Nimslo'
print(dropped_folder)

dest_folder_gifs = f'{dropped_folder}/gifs_auto'
dest_folder_vids = f'{dropped_folder}/vids_auto'

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

    aligned0 = imgs[0]
    print('Aligning 1/3')
    aligned1 = match_images_cv(aligned0, imgs[1])
    print('Aligning 2/3')
    aligned2 = match_images_cv(aligned1, imgs[2])
    print('Aligning 3/3')
    aligned3 = match_images_cv(aligned2, imgs[3])

    hor0 = np.average(aligned0[:,:,0], axis=0)
    hor1 = np.average(aligned1[:,:,0], axis=0)
    hor2 = np.average(aligned2[:,:,0], axis=0)
    hor3 = np.average(aligned3[:,:,0], axis=0)
    ver0 = np.average(aligned0[:,:,0], axis=1)
    ver1 = np.average(aligned1[:,:,0], axis=1)
    ver2 = np.average(aligned2[:,:,0], axis=1)
    ver3 = np.average(aligned3[:,:,0], axis=1)

    b0 = find_begin(hor0)
    e0 = find_end(hor0)
    b1 = find_begin(hor1)
    e1 = find_end(hor1)
    b2 = find_begin(hor2)
    e2 = find_end(hor2)
    b3 = find_begin(hor3)
    e3 = find_end(hor3)

    h0 = find_begin(ver0)
    l0 = find_end(ver0)
    h1 = find_begin(ver1)
    l1 = find_end(ver1)
    h2 = find_begin(ver2)
    l2 = find_end(ver2)
    h3 = find_begin(ver3)
    l3 = find_end(ver3)

    begin = max(b0, b1, b2, b3)
    end = min(e0, e1, e2, e3)
    high = max(h0, h1, h2, h3)
    low = min(l0, l1, l2, l3)

    aligned0 = aligned0[high:low, begin:end, :]
    aligned1 = aligned1[high:low, begin:end, :]
    aligned2 = aligned2[high:low, begin:end, :]
    aligned3 = aligned3[high:low, begin:end, :]

    height, width, depth = aligned0.shape
    aligned0 = resize(aligned0, (int(height/16) * 16, int(width/16) * 16, depth))
    aligned1 = resize(aligned1, (int(height/16) * 16, int(width/16) * 16, depth))
    aligned2 = resize(aligned2, (int(height/16) * 16, int(width/16) * 16, depth))
    aligned3 = resize(aligned3, (int(height/16) * 16, int(width/16) * 16, depth))

    frames = [aligned0, aligned1, aligned2, aligned3, aligned2, aligned1]

    gif_dest = f'{dest_folder_gifs}/{int(i/4)}.gif'
    vid_dest = f'{dest_folder_vids}/{int(i/4)}.mp4'
    smoothed_vid_dest = f'{dest_folder_vids}/{int(i/4)}-smooth.mp4'

    imageio.mimsave(gif_dest, frames, duration=time_for_one_frame_gif)
    imageio.mimsave(vid_dest, frames*5, fps=1/time_for_one_frame_vid)

    # Smooth vid :
    subprocess.Popen(['ffmpeg', '-i', vid_dest, '-crf', '10', '-vf', 'minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1', smoothed_vid_dest])
    # # ffmpeg -i 72.mp4 -crf 10 -vf "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" output72.mp4
