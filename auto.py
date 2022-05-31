import sys
import os
import glob
import numpy as np
import cv2
from PIL import Image
import imageio
import matplotlib.pyplot as plt

# ---------------------------- CONFIGURATION ----------------------------

time_for_one_frame_gif = 0.15 # How long a frame lasts in the final gif. Default is 0.15
time_for_one_frame_vid = 0.18 # How long a frame lasts in the final gif. Default is 0.15

# ---------------- DO NOT TOUCH ANYTHING UNDER THIS LINE ----------------

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
# dropped_folder = 'C:\\Users\\adrie\\Desktop\\projets\\Nimslo_Animator\\test'
print(dropped_folder)

dest_folder_gifs = f'{dropped_folder}/gifs'
dest_folder_vids = f'{dropped_folder}/vids'

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

    frames = [aligned0, aligned1, aligned2, aligned3, aligned2, aligned1]

    imageio.mimsave(f'{dest_folder_gifs}/{i}.gif', frames, duration=time_for_one_frame_gif)
    imageio.mimsave(f'{dest_folder_vids}/{i}.mp4', frames*10, fps=1/time_for_one_frame_vid)

    # Smooth vid :
    # ffmpeg -i 72.mp4 -crf 10 -vf "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" output72.mp4
