from tkinter import filedialog
import tkinter as tk
import os
import sys
import subprocess


def install_dependencies(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


try:
    from PIL import Image
    import Imath
    import numpy as np
    import OpenEXR
except ImportError:
    packages = ['Imath', 'OpenEXR', 'Pillow']
    for pack in packages:
        install_dependencies(pack)
    from PIL import Image
    import Imath
    import numpy as np
    import OpenEXR


class ImageConverter():
    def __init__(self) -> None:
        pass


    def get_files(self):
        root = tk.Tk()
        root.withdraw() # Hide the main window
        file_paths = filedialog.askopenfilenames(
            title='Select files')
        return file_paths


    def get_exr_files(self):
        root = tk.Tk()
        root.withdraw() # Hide the main window
        file_paths = filedialog.askopenfilenames(
            title='Select EXR files',
            filetypes=[('EXR Files', '*.exr')])
        return file_paths


    def convert_exr_to_jpg(self, exr_path, remove_original=False):
        # Read the .exr file using OpenEXR
        file = OpenEXR.InputFile(exr_path)
        dw = file.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

        # Check available channel in the EXR file
        channels = file.header()['channels'].keys()
        required_channels = ['R', 'G', 'B']

        # Read the RGB channels
        rgb = []
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        for color in required_channels:
            if color in channels:
                channel_data = np.frombuffer(file.channel(color, pt), 
                                            dtype=np.float32)
            else:
                channel_data = np.zeros(size[0] * size[1], dtype=np.float32)
            rgb.append(channel_data)
        r, g, b = [im.reshape(size) for im in rgb]

        # Stack and normalize the image
        img = np.stack([r, g, b], axis=-1)
        img = np.clip(img * 255, 0, 255).astype(np.uint8)

        # Save the image as .jpg using PIL
        jpg_path = os.path.splitext(exr_path)[0] + '.jpg'
        img = Image.fromarray(img)
        img.save(jpg_path, 'JPEG')
        file.close()
        print(f'\t | {exr_path} has been converted.')

        if remove_original:
            os.remove(exr_path)
        return jpg_path
    
    
    def convert_tif_to_jpg(self, tif_path, remove_original=False):
        image = Image.open(tif_path)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        jpg_path = os.path.splitext(tif_path)[0] + '.jpg'
        image.save(jpg_path ,'JPEG')

        print(f'\t | {tif_path} has been converted.')
        if remove_original:
            os.remove(tif_path)
        return jpg_path


    def uninstall_dependencies(self):
        packages = ['Imath', 'OpenEXR', 'Pillow']
        for pack in packages:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'uninstall', '-y', pack])
        return packages


    def run(self, source_type='exr', remove_original=False):
        img_files = self.get_files()
        #exr_files = self.get_exr_files()
        if img_files:
            print(f'\n Converting images:')
            for file in img_files:
                if source_type == 'exr':
                    self.convert_exr_to_jpg(
                            file, remove_original=remove_original)
                elif source_type == 'tif':
                    self.convert_tif_to_jpg(
                            file, remove_original=remove_original)
            print('\n')
        self.uninstall_dependencies()


if __name__ == '__main__':
    cvtr = ImageConverter()
    cvtr.run(source_type='tif', remove_original=True)