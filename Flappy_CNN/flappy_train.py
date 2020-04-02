import os
import matplotlib.pyplot as plt
import numpy as np 
import tensorflow as tf
import training_params as params

# Add this code to avoid CNN error
physical_devices = tf.config.experimental.list_physical_devices('GPU')
assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
tf.config.experimental.set_memory_growth(physical_devices[0], True)

BATCH_SIZE = params.BATCH_SIZE
IMG_SHAPE = params.IMG_SHAPE
EPOCHS = params.EPOCHS

base_dir = r'D:\UNSW Year 3\tensorflow\Some-Easy-Training-Problem\FlappyBird\data'
train_dir = os.path.join(base_dir,'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')

train_flap_dir = os.path.join(train_dir, 'flap')
train_no_dir = os.path.join(train_dir, 'no')

validation_flap_dir = os.path.join(validation_dir, 'flap')
validation_no_dir = os.path.join(validation_dir, 'no')

test_flap_dir = os.path.join(test_dir, 'flap')
test_no_dir = os.path.join(test_dir, 'no')

print("There are {} items in train_flap_dir".format(len(os.listdir(train_flap_dir))))
print("There are {} items in validation_flap_dir".format(len(os.listdir(validation_flap_dir))))

print("There are {} items in train_no_dir".format(len(os.listdir(train_no_dir))))
print("There are {} items in validation_no_dir".format(len(os.listdir(validation_no_dir))))

image_gen_train = tf.keras.preprocessing.image.ImageDataGenerator(
    rotation_range = 30,
    rescale=1./255,
    fill_mode='nearest'
)

image_gen_val = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

train_data_gen = image_gen_train.flow_from_directory(
    batch_size=BATCH_SIZE,
    directory=train_dir,
    shuffle=True,
    target_size=(IMG_SHAPE,IMG_SHAPE),
    class_mode='binary'
)

val_data_gen = image_gen_val.flow_from_directory(
    batch_size=BATCH_SIZE,
    directory=validation_dir,
    shuffle=False,
    target_size=(IMG_SHAPE,IMG_SHAPE),
    class_mode='binary'
)

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(16, (3,3), padding='same',activation='relu', input_shape=(IMG_SHAPE,IMG_SHAPE,3)),
    tf.keras.layers.MaxPooling2D(2,2),

    tf.keras.layers.Conv2D(32 , (3,3), padding='same',activation='relu'),
    tf.keras.layers.MaxPool2D(2,2),

    tf.keras.layers.Conv2D(64, (3,3), padding='same',activation='relu'),
    tf.keras.layers.MaxPool2D(2,2),

    tf.keras.layers.Conv2D(128, (3,3), padding='same',activation='relu'),
    tf.keras.layers.MaxPool2D(2,2),

    tf.keras.layers.Flatten(),

    tf.keras.layers.Dense(64, activation='relu'),

    tf.keras.layers.Dense(1,activation='sigmoid')
])

model.compile(
    loss='binary_crossentropy',
    optimizer=tf.keras.optimizers.RMSprop(lr=1e-4),
    metrics=['accuracy']
)

total_train = len(os.listdir(train_flap_dir)) + len(os.listdir(train_no_dir))
total_val = len(os.listdir(validation_flap_dir)) + len(os.listdir(validation_no_dir))

history = model.fit(
    train_data_gen,
    steps_per_epoch=int(np.ceil(total_train / float(BATCH_SIZE))),
    epochs=EPOCHS,
    validation_data=val_data_gen,
    validation_steps=int(np.ceil(total_val / float(BATCH_SIZE))),
)

model_dir = './models'

tf.keras.models.save_model(model, model_dir)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(EPOCHS)
plt.figure(figsize=(8,8))
plt.subplot(1,2,1)
plt.plot(epochs_range,acc, label="Training Accuracy")
plt.plot(epochs_range,val_acc, label = 'Validation Accuracy')
plt.legend(loc='lower right')
plt.title("Training and Validation Accuracy")

plt.show()

