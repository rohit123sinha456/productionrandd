import cv2
import numpy as np
import os
import shutil
def check_corrupation(filepath):
    img = cv2.imread(filepath)
    filesize = os.stat(filepath).st_size/(1024)
    image_median = np.median(img)
    # print(filepath,filesize,image_median)
    if(filesize < 400 and image_median > 110):
        return True
    else:
        return False

if __name__ == "__main__":
    for imgname in os.listdir("images"):
        if imgname[len(imgname)-3:] == "jpg" and check_corrupation(os.path.join('images',imgname)):
            shutil.move(os.path.join("images",imgname),os.path.join("gray",imgname))
            print(imgname)
            