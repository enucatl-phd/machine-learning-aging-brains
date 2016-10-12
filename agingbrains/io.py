import nibabel as nb
import numpy as np
import apache_beam as beam

class _Nifti1Source(beam.io.filebasedsource.FileBasedSource):

    def __init__(self, file_pattern, min_bundle_size):
        super(_Nifti1Source, self).__init__(
            file_pattern=file_pattern,
            min_bundle_size=min_bundle_size,
            splittable=False)

    def read_records(self, file_name, range_tracker):
        with self.open_file(file_name) as f:
            record = np.array((1, 1, 1))
            hdr_fh = nb.fileholders.FileHolder(fileobj=f)
            img_fh = nb.fileholders.FileHolder(fileobj=f)
            file_map = {"image": img_fh}
            header = nb.Nifti1Image.header_class.from_fileobj(f)
            hdr_copy = header.copy()
            data = nb.Nifti1Image.ImageArrayProxy(f, hdr_copy, mmap=False)
            img = nb.Nifti1Image(data, None, header, file_map=file_map)
            img._affine = header.get_best_affine()
            img._load_cache = {
                "header": hdr_copy,
                "affine": img._affine.copy(),
                "file_map": nb.fileholders.copy_file_map(file_map)
            }
            print(img.get_data()[..., 0])
            yield record

class ReadNifti1(beam.transforms.PTransform):

    def __init__(self, file_pattern=None, min_bundle_size=0):
        """TODO: Docstring for __init__.

        :file_pattern: TODO
        :min_bundle_size: TODO
        :returns: TODO

        """
        super(ReadNifti1, self).__init__()
        self._file_pattern = file_pattern
        self._min_bundle_size = min_bundle_size

    def apply(self, pcoll):
        return pcoll.pipeline | beam.io.Read(
            _Nifti1Source(
                file_pattern=self._file_pattern,
                min_bundle_size=self._min_bundle_size))
