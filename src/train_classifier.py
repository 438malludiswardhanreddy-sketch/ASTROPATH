"""
ASTROPATH Training Module (train_classifier.py)
Train a pothole vs. plain road classifier using transfer learning with MobileNetV2
Improved version of main (1).py with better data pipeline and augmentation
"""

import os
import sys
import numpy as np
from glob import glob
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import cv2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import setup_logger, ensure_dir_exists, validate_training_data

logger = setup_logger(__name__)


class PotholeClassifierTrainer:
    """Train and evaluate pothole classification model"""
    
    def __init__(self, img_size=config.IMG_SIZE_CLASSIFIER):
        self.img_size = img_size
        self.model = None
        self.history = None
        logger.info(f"Initializing PotholeClassifierTrainer (img_size={img_size})")
    
    def load_images_from_directory(self, directory, label, max_samples=None):
        """Load images from directory with label"""
        images = []
        labels = []
        
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
        image_files = []
        
        for ext in extensions:
            image_files.extend(glob(os.path.join(directory, ext)))
        
        if max_samples:
            image_files = image_files[:max_samples]
        
        logger.info(f"Loading {len(image_files)} images from {directory} (label={label})")
        
        for img_path in image_files:
            try:
                img = cv2.imread(img_path)
                if img is None:
                    logger.warning(f"Failed to read: {img_path}")
                    continue
                
                # Resize image
                img = cv2.resize(img, (self.img_size, self.img_size))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                images.append(img)
                labels.append(label)
            except Exception as e:
                logger.warning(f"Error loading {img_path}: {e}")
        
        return np.array(images), np.array(labels)
    
    def prepare_data(self, pothole_dir, plain_dir, validation_split=0.2):
        """Prepare training and validation data"""
        logger.info("Preparing dataset...")
        
        # Load pothole images (label = 1)
        pothole_imgs, pothole_labels = self.load_images_from_directory(pothole_dir, 1)
        
        # Load plain road images (label = 0)
        plain_imgs, plain_labels = self.load_images_from_directory(plain_dir, 0)
        
        # Combine datasets
        all_images = np.concatenate([pothole_imgs, plain_imgs])
        all_labels = np.concatenate([pothole_labels, plain_labels])
        
        logger.info(f"Total samples: {len(all_images)} (Potholes: {np.sum(all_labels)}, Plain: {np.sum(all_labels == 0)})")
        
        # Split into train and validation
        X_train, X_val, y_train, y_val = train_test_split(
            all_images, all_labels,
            test_size=validation_split,
            random_state=42,
            stratify=all_labels
        )
        
        logger.info(f"Train: {len(X_train)} | Validation: {len(X_val)}")
        
        return (X_train, y_train), (X_val, y_val)
    
    def create_model(self, freeze_base=True):
        """Create model with MobileNetV2 transfer learning"""
        logger.info("Creating model with MobileNetV2 transfer learning...")
        
        # Load pre-trained MobileNetV2
        base_model = MobileNetV2(
            input_shape=(self.img_size, self.img_size, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model weights
        if freeze_base:
            base_model.trainable = False
            logger.info("Base model weights frozen")
        
        # Add custom layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(1, activation='sigmoid')(x)  # Binary classification
        
        # Create final model
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=config.LEARNING_RATE),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC()]
        )
        
        logger.info("Model compiled successfully")
        logger.info(f"Total parameters: {model.count_params()}")
        
        self.model = model
        return model
    
    def create_data_generators(self):
        """Create data augmentation generators"""
        logger.info("Creating data augmentation generators...")
        
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            shear_range=0.15,
            fill_mode='nearest'
        )
        
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        return train_datagen, val_datagen
    
    def train(self, X_train, y_train, X_val, y_val, epochs=config.EPOCHS, batch_size=config.BATCH_SIZE):
        """Train the model"""
        if self.model is None:
            logger.error("Model not created. Call create_model() first.")
            return
        
        logger.info(f"Starting training... (epochs={epochs}, batch_size={batch_size})")
        
        # Data generators
        train_datagen, val_datagen = self.create_data_generators()
        
        # Normalize training data
        X_train = X_train.astype(np.float32) / 255.0
        X_val = X_val.astype(np.float32) / 255.0
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                config.CLASSIFIER_MODEL,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            train_datagen.flow(X_train, y_train, batch_size=batch_size),
            validation_data=val_datagen.flow(X_val, y_val, batch_size=batch_size),
            epochs=epochs,
            callbacks=callbacks,
            verbose=1,
            steps_per_epoch=len(X_train) // batch_size
        )
        
        logger.info("Training completed!")
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test data"""
        if self.model is None:
            logger.error("Model not loaded")
            return
        
        X_test = X_test.astype(np.float32) / 255.0
        
        results = self.model.evaluate(X_test, y_test, verbose=0)
        logger.info(f"Test Loss: {results[0]:.4f}")
        logger.info(f"Test Accuracy: {results[1]:.4f}")
        logger.info(f"Test AUC: {results[2]:.4f}")
        
        return results
    
    def save_model(self, output_path=config.CLASSIFIER_MODEL):
        """Save trained model"""
        if self.model is None:
            logger.error("Model not trained")
            return
        
        ensure_dir_exists(os.path.dirname(output_path))
        self.model.save(output_path)
        logger.info(f"Model saved to: {output_path}")
    
    def convert_to_tflite(self, output_path=config.CLASSIFIER_TFLITE):
        """Convert model to TensorFlow Lite for Raspberry Pi deployment"""
        if self.model is None:
            logger.error("Model not trained")
            return
        
        logger.info(f"Converting model to TensorFlow Lite...")
        
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        tflite_model = converter.convert()
        
        ensure_dir_exists(os.path.dirname(output_path))
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        logger.info(f"TFLite model saved to: {output_path}")


def main():
    """Main training pipeline"""
    logger.info("="*60)
    logger.info("ASTROPATH Pothole Classifier Training")
    logger.info("="*60)
    
    # ✅ INTEGRATION: Show available training data locations
    logger.info(f"\n📁 Training Data Locations:")
    logger.info(f"   Your existing pothole images: {config.EXISTING_POTHOLE_IMAGES}")
    logger.info(f"   Pothole training path: {config.POTHOLE_DATA_PATH}")
    logger.info(f"   Plain road training path: {config.PLAIN_DATA_PATH}\n")
    
    # Validate training data exists
    if not validate_training_data():
        logger.error("Training data validation failed!")
        logger.info(f"\n✅ Your existing pothole images are located at:")
        logger.info(f"   {config.EXISTING_POTHOLE_IMAGES}")
        logger.info(f"\n💡 To use them for training, choose one option:")
        logger.info(f"   1. Copy images to: {config.POTHOLE_DATA_PATH}")
        logger.info(f"   2. Update config.py: POTHOLE_DATA_PATH = EXISTING_POTHOLE_IMAGES")
        logger.info(f"   3. Organize pothole & plain images for binary classification\n")
        return
    
    # Initialize trainer
    trainer = PotholeClassifierTrainer(img_size=config.IMG_SIZE_CLASSIFIER)
    
    # Prepare data
    (X_train, y_train), (X_val, y_val) = trainer.prepare_data(
        config.POTHOLE_DATA_PATH,
        config.PLAIN_DATA_PATH,
        validation_split=config.TRAIN_TEST_SPLIT
    )
    
    # Create model
    trainer.create_model(freeze_base=True)
    
    # Train model
    trainer.train(X_train, y_train, X_val, y_val, epochs=config.EPOCHS, batch_size=config.BATCH_SIZE)
    
    # Evaluate model
    trainer.evaluate(X_val, y_val)
    
    # Save model
    trainer.save_model()
    
    # Convert to TFLite for Raspberry Pi
    if config.PI_OPTIMIZE:
        trainer.convert_to_tflite()
    
    logger.info("Training pipeline completed successfully!")
    logger.info(f"Model saved to: {config.CLASSIFIER_MODEL}")
    if config.PI_OPTIMIZE:
        logger.info(f"TFLite model saved to: {config.CLASSIFIER_TFLITE}")


if __name__ == "__main__":
    main()
