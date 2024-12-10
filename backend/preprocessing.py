import tensorflow as tf
# from  keras.layers import Layer
def preprocess(file_path):
    byte_img=tf.io.read_file(file_path)
    img = tf.io.decode_jpeg(byte_img)
    img=tf.image.resize(img,(100,100))
    img = img/255.0 
    return img