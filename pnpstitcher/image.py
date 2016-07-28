from PIL import Image
from pnpstitcher.exception import StitcherError


class ImageCatalog(object):
    def __init__(self, filename_set):
        self.image_set = [
            Image.open(filename)
            for filename in filename_set]
        self.image_size = self.get_common_dimension()

    def get_common_dimension(self):
        """
        Get the common dimension.

        """
        base_size = self.image_set[0].size
        for image in self.image_set:
            if image.size != base_size:
                raise StitcherError(
                    ('Unmatched dimension. File: {},'
                     'expected dimension: {}').format(
                        image.fp.name, base_size))

        return base_size
