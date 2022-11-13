import sys
from PIL import Image
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import profile_calculations


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # super(MainWindow, self).__init__()
        self.initialize_ui()
        self.img_filename = ""

    def initialize_ui(self):
        """
        Initialize the window and display its contents to the screen.
        """
        loadUi("GUI2.ui", self)
        self.setWindowTitle('Profile calculator')
        self.browse.clicked.connect(self.browse_files)
        self.calculate.clicked.connect(self.calculate_props)
        self.filename.setText('Press Browse button to load an image')
        self.show()

    def browse_files(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', '', 'Image files (*.png *.jpg *.jpeg *.bmp)')
        self.filename.setText(file_name[0])
        self.img_filename = file_name[0]
        if file_name[0] != "":
            print("Image file name was set")

    def calculate_props(self):
        try:
            image = Image.open(self.img_filename)
        except AttributeError:
            print("Invalid image file!")
            return None

        print("Calculation started...")
        image = image.convert('1')
        actual_width = float(self.width_input.text())

        # convert image to numpy array
        data = np.asarray(image)

        # crop image
        data = profile_calculations.crop_image(data)

        # convert cropped image to numpy array
        image = Image.fromarray(data)

        image.save('profile_mod.png')

        pixel_length = profile_calculations.calculate_pixel_length(data, actual_width)
        pixel_area = profile_calculations.calculate_pixel_area(pixel_length)

        profile_area = profile_calculations.calculate_area(data, pixel_area)
        self.area_result.setText(str(profile_area))

        # calculate center of gravity
        cog = profile_calculations.calculate_cog(data, profile_area, pixel_area)
        self.cog_px_result.setText("x=" + str(cog[0]) + ", y=" + str(cog[1]))

        # calculate center of gravity in mm
        cog_mm = profile_calculations.calculate_cog_mm(cog, pixel_length)
        self.cog_mm_result.setText("x=" + str(cog_mm[0]) + ", y=" + str(cog_mm[1]))

        moa2_tuple = profile_calculations.calculate_2nd_mom_of_area(data, pixel_area, cog, pixel_length)
        self.moa2_result.setText("Ix=" + str(moa2_tuple[0]) + ", Iy=" + str(moa2_tuple[1]))

        secmod_tuple = profile_calculations.calculate_section_modulus_bending(moa2_tuple, cog, pixel_length)
        self.secmod_result.setText("Wx=" + str(secmod_tuple[0]) + ", Wy=" + str(secmod_tuple[1]))

        data_cog = profile_calculations.add_cog_mark(data, cog)
        image_cog = Image.fromarray(data_cog)
        image_cog.save('profile_COG.png')

        pixmap = QPixmap('profile_COG.png')
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        print("Calculation ended.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
