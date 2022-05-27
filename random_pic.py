from randimage import get_random_image
import matplotlib
import random

################################################################################
# Script for generation of random pictures
# https://github.com/nareto/randimage
################################################################################

def generateImage():
    img_size = (256,256)
    img = get_random_image(img_size)  #returns numpy array
    #show_array(img) #shows the image
    image_name = str(random.randrange(100000000000000))
    image_name = image_name + ".png"
    matplotlib.image.imsave(image_name, img)

    return image_name