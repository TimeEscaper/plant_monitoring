from abc import ABC

"""
Abstract class for all camera drivers.
"""
class AbstractCameraDriver(ABC):

    """
    :return True if RGB photos supported.
    """
    def is_rgb_supported(self):
        pass

    """
    :return True if depth images supported.
    """
    def is_depth_supported(self):
        pass

    """
    :return True if point clouds supported.
    """
    def is_point_cloud_supported(self):
        pass

    """
    Takes RGB image.
    :param file_name String representing file to save the image.
    :param image_size A tuple (width, height) with image size.
    :param focus_skip_count Number of first images to skip in order to allow camera to focus.
    :raise RuntimeError if RGB is not supported or in case of other errors.
    """
    def take_rgb_image(self, file_name, image_size, focus_skip_count=0):
        pass

    """
    Takes depth image.
    :param file_name String representing file to save the image.
    :param image_size A tuple (width, height) with image size.
    :raise RuntimeError if depth is not supported or in case of other errors.
    """
    def take_depth_image(self, file_name, image_size):
        pass

    """
    Takes point cloud.
    :param file_name String representing file to save the image.
    :raise RuntimeError if point cloud is not supported or in case of other errors.
    """
    def take_point_cloud(self, file_name):
        pass
