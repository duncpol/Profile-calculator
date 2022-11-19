from PIL import Image
import numpy as np
import math


def calculate_pixel_length(data, actual_width):
    return actual_width / (len(data[0]))


def calculate_pixel_area(pixel_length):
    return pixel_length ** 2


def calculate_area(data, pixel_area):
    """Returns cross-sectional area of profile in mm^2"""

    active_pixels = 0
    for row in data:
        for val in row:
            if not val:
                active_pixels += 1

    area = active_pixels * pixel_area
    return area


def crop_image(data):
    """Crops all white background outside the profile"""

    print(f'Original image size: {data.shape} px')
    # crop white rows
    print("-----------cropping image...----------\n")
    row_num = 0
    row_num_orig = 0
    while row_num < data.shape[0]:
        # print(row, all(row), "\n")
        if all(data[row_num, :]):
            data = np.delete(data, row_num, axis=0)
            print(f"row {row_num_orig} deleted")
            row_num -= 1
        # print(f"row num {row_num+1}, rows in data: {data.shape[0]}")
        row_num += 1
        row_num_orig += 1

    # crop white columns
    col_num = 0
    col_num_orig = 0
    while col_num < data.shape[1]:
        # print(col, all(col), "\n")
        if all(data[:, col_num]):
            data = np.delete(data, col_num, axis=1)
            print(f"column {col_num_orig} deleted")
            col_num -= 1
        # print(f"col num {col_num+1}, cols in data: {data.shape[1]}")
        col_num += 1
        col_num_orig += 1

    print()
    print("-----------cropping ended-------------\n")
    print(f'Cropped image size: {data.shape} px\n')
    return data


def calculate_cog(data, profile_area, pixel_area):
    cog_x = 0
    cog_y = 0
    for y_coord, row in enumerate(data):
        for x_coord, pixel in enumerate(row):
            # print(f"x: {x_coord}, y: {y_coord}")
            if not pixel:  # if color is black, i.e. area within the profile
                pixel_moment_x = (pixel_area * x_coord + pixel_area * (x_coord + 1)) / 2  # average value
                cog_x += pixel_moment_x
                pixel_moment_y = (pixel_area * y_coord + pixel_area * (y_coord + 1)) / 2  # average value
                cog_y += pixel_moment_y

    cog_x /= profile_area
    cog_y /= profile_area
    cog = (cog_x, cog_y)
    return cog


def calculate_cog_mm(cog, pixel_length):
    """Calculates center of gravity in mm"""

    cog_x_mm = cog[0] * pixel_length
    cog_y_mm = cog[1] * pixel_length
    cog_mm = (cog_x_mm, cog_y_mm)
    return cog_mm


def add_cog_mark(data, cog):
    """Adds center of gravity crosshair mark into image"""

    image_cog = Image.fromarray(data)
    image_cog = image_cog.convert('RGB')
    data = np.array(image_cog)

    # add crosshair mark
    # print(data[math.floor(cog[1]), math.floor(cog[0])])
    fl_cog_y = math.floor(cog[1])
    fl_cog_x = math.floor(cog[0])

    # set scale of crosshair relative to image size
    if data.shape[1] > 45:
        cross_x = int(data.shape[1] / 15)
    else:
        cross_x = 2
    if data.shape[0] > 45:
        cross_y = int(data.shape[0] / 15)
    else:
        cross_y = 2

    data[fl_cog_y - cross_y:fl_cog_y + cross_y + 1, fl_cog_x] = [255, 0, 0]
    data[fl_cog_y, fl_cog_x - cross_x:fl_cog_x + cross_x + 1] = [255, 0, 0]

    if max(data.shape) > 3000:
        data[fl_cog_y - cross_y:fl_cog_y + cross_y + 1, fl_cog_x + 1] = [255, 0, 0]
        data[fl_cog_y + 1, fl_cog_x - cross_x:fl_cog_x + cross_x + 1] = [255, 0, 0]
        data[fl_cog_y - cross_y:fl_cog_y + cross_y + 1, fl_cog_x - 1] = [255, 0, 0]
        data[fl_cog_y - 1, fl_cog_x - cross_x:fl_cog_x + cross_x + 1] = [255, 0, 0]
        data[fl_cog_y - cross_y:fl_cog_y + cross_y + 1, fl_cog_x + 2] = [255, 0, 0]
        data[fl_cog_y + 2, fl_cog_x - cross_x:fl_cog_x + cross_x + 1] = [255, 0, 0]
        data[fl_cog_y - cross_y:fl_cog_y + cross_y + 1, fl_cog_x - 2] = [255, 0, 0]
        data[fl_cog_y - 2, fl_cog_x - cross_x:fl_cog_x + cross_x + 1] = [255, 0, 0]

    return data


def calculate_2nd_mom_of_area(data, pixel_area, cog, pixel_length):
    """Calculates second moment of area of profile in mm^4 around x and y axis
    returns a tuple Ix and Iy
    [SK: kvadratický moment prierezu]"""

    moa2_x = 0
    moa2_y = 0
    for y_coord, row in enumerate(data):
        for x_coord, pixel in enumerate(row):
            if not pixel:
                moa2_x += (1/12) * pixel_area ** 2 + pixel_area * \
                          ((y_coord - cog[1]) * pixel_length + pixel_length / 2) ** 2
                moa2_y += (1/12) * pixel_area ** 2 + pixel_area * \
                          ((x_coord - cog[0]) * pixel_length + pixel_length / 2) ** 2

    moa2_tuple = (moa2_x, moa2_y)
    return moa2_tuple


def calculate_section_modulus_bending(moa2_tuple, cog, pixel_length):
    secmod_b_x = moa2_tuple[0] / (cog[1] * pixel_length)
    secmod_b_y = moa2_tuple[1] / (cog[0] * pixel_length)
    secmod_tuple = (secmod_b_x, secmod_b_y)
    return secmod_tuple


def calculate_polar_moment_of_area(moa2_tuple):
    return sum(moa2_tuple)

