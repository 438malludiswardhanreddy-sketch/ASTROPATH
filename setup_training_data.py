"""
ASTROPATH Training Data Setup Helper
Integrate your existing pothole images for training
"""

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from src.utils import setup_logger

logger = setup_logger(__name__)


def show_menu():
    """Display setup menu"""
    print("\n" + "="*60)
    print("🖼️  ASTROPATH Training Data Setup")
    print("="*60)
    print("\nChoose how to integrate your pothole images:\n")
    print("1. ✅ Copy images from Image Annotation to training folder")
    print("2. 🔗 Use images directly from Image Annotation folder")
    print("3. 📋 Show current configuration")
    print("4. ❌ Exit\n")
    
    return input("Enter choice (1-4): ").strip()


def option_1_copy_images():
    """Copy existing images to training structure"""
    print("\n📂 Option 1: Copy Images to Training Folder")
    print("-" * 50)
    
    existing_images = config.EXISTING_POTHOLE_IMAGES
    pothole_dest = config.POTHOLE_DATA_PATH
    
    if not os.path.exists(existing_images):
        logger.error(f"❌ Source images not found: {existing_images}")
        return
    
    # Create destination directory
    os.makedirs(pothole_dest, exist_ok=True)
    
    # Get list of images
    image_files = [f for f in os.listdir(existing_images) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    logger.info(f"Found {len(image_files)} pothole images")
    print(f"\n📋 Sample images: {image_files[:5]}")
    
    if len(image_files) == 0:
        logger.error("❌ No images found!")
        return
    
    # Confirm copy
    confirm = input(f"\n✅ Copy {len(image_files)} images to {pothole_dest}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Copy images
    copied = 0
    for img in image_files:
        try:
            src = os.path.join(existing_images, img)
            dst = os.path.join(pothole_dest, img)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                copied += 1
        except Exception as e:
            logger.warning(f"Failed to copy {img}: {e}")
    
    logger.info(f"✅ Copied {copied} images to {pothole_dest}")
    print(f"\n✅ Done! Pothole images ready for training.")
    print(f"📍 Location: {pothole_dest}")
    print(f"📊 Count: {len(os.listdir(pothole_dest))} images")


def option_2_direct_use():
    """Update config to use images directly"""
    print("\n🔗 Option 2: Use Images Directly")
    print("-" * 50)
    
    existing_images = config.EXISTING_POTHOLE_IMAGES
    
    if not os.path.exists(existing_images):
        logger.error(f"❌ Images not found: {existing_images}")
        return
    
    image_count = len([f for f in os.listdir(existing_images) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    logger.info(f"Found {image_count} images at: {existing_images}")
    print(f"\n📝 To use these images directly for training:")
    print(f"\nEdit config.py line ~32 and uncomment:")
    print(f"   # POTHOLE_DATA_PATH = EXISTING_POTHOLE_IMAGES")
    print(f"\nThen run:")
    print(f"   python main.py → Select: 1. Train Pothole Classifier")
    print(f"\n✅ Your {image_count} pothole images will be used!")


def option_3_show_config():
    """Display current configuration"""
    print("\n📋 Current Configuration")
    print("-" * 50)
    
    print(f"\n📍 Existing Images Location:")
    print(f"   {config.EXISTING_POTHOLE_IMAGES}")
    print(f"   Status: {'✅ EXISTS' if os.path.exists(config.EXISTING_POTHOLE_IMAGES) else '❌ NOT FOUND'}")
    
    if os.path.exists(config.EXISTING_POTHOLE_IMAGES):
        count = len(os.listdir(config.EXISTING_POTHOLE_IMAGES))
        print(f"   Images: {count} files found")
    
    print(f"\n📂 Training Data Paths:")
    print(f"   Pothole: {config.POTHOLE_DATA_PATH}")
    print(f"   Status: {'✅ EXISTS' if os.path.exists(config.POTHOLE_DATA_PATH) else '❌ NOT FOUND'}")
    if os.path.exists(config.POTHOLE_DATA_PATH):
        count = len(os.listdir(config.POTHOLE_DATA_PATH))
        print(f"   Images: {count} files")
    
    print(f"\n   Plain: {config.PLAIN_DATA_PATH}")
    print(f"   Status: {'✅ EXISTS' if os.path.exists(config.PLAIN_DATA_PATH) else '❌ NOT FOUND'}")
    if os.path.exists(config.PLAIN_DATA_PATH):
        count = len(os.listdir(config.PLAIN_DATA_PATH))
        print(f"   Images: {count} files")


def main():
    """Main menu loop"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            option_1_copy_images()
        elif choice == '2':
            option_2_direct_use()
        elif choice == '3':
            option_3_show_config()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
