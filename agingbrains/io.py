import nibabel as nb
import numpy as np
import apache_beam as beam

class _Nifti1Source(beam.io.filebasedsource.FileBasedSource):

    def read_records(self, file_name, range_tracker):
        with self.open_file(file_name) as f:
            record = np.array((1, 1, 1))
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
