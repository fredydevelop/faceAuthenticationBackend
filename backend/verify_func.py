import tensorflow as tf
from preprocessing import preprocess
import os
import numpy as np


def verify(model,detection_threshold,verification_threshold):
    results=[]

    for image in os.listdir(os.path.join('application_data','verification_images')):
        print(image)
        input_img = preprocess(os.path.join('application_data', 'input_image','input_image.jpg'))
        validation_img = preprocess(os.path.join('application_data', 'verification_images',image))
        result = model.predict(list(np.expand_dims([input_img,validation_img],axis=1)))

        results.append(result)


    detection= np.sum(np.array(results) > detection_threshold)
    #print(detection)
    verification= detection/len(os.listdir(os.path.join('application_data', 'verification_images')))
    #print(verification)
    #if verification == 0:
     #   raise ValueError("No verification images found in the specified directory.")
    verified = verification> verification_threshold

    return results,verified