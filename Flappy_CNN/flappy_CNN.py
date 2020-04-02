import tensorflow as tf
import cv2
import numpy as np 
import random
from collections import deque
import wrapped_flappy_CNN as wfc

# Add this code to avoid CNN error
physical_devices = tf.config.experimental.list_physical_devices('GPU')
assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
tf.config.experimental.set_memory_growth(physical_devices[0], True)

def main():
    flappy = wfc.Wrapped_Flappy_CNN()
    model_dir = './models'
    model = tf.keras.models.load_model(model_dir)
    screen = flappy.get_screen()

    frames_per_flap = 5
    i = 0
    screen = flappy.get_screen()
    while True:
        predicted_action = model.predict(screen)

        if predicted_action < 0.5:
            i += 1
            if i == frames_per_flap:
                action = 'f'
                i = 0
            else:
                action = 'n'
        else: action = 'n'

        screen = flappy.train_step(action)

if __name__ == "__main__":
    main()