import os
import apache_beam as beam


class _AgeReader(beam.io.filebasedsource.FileBasedSource):

    def __init__(self, ages_file, file_pattern, min_bundle_size):
        super(_AgeReader, self).__init__(
            file_pattern=file_pattern,
            min_bundle_size=min_bundle_size,
            splittable=False)
        self._ages_file = ages_file

    def read_records(self, file_name, range_tracker):
        with self.open_file(self._ages_file) as f:
            basename = os.path.splitext(os.path.basename(file_name))[0]
            i = int(basename.split("_")[1]) - 1
            age = int(f.read().split()[i])
            yield (file_name, age)


class ReadAge(beam.transforms.PTransform):

    def __init__(self, ages_file, file_pattern=None, min_bundle_size=0):
        super(ReadAge, self).__init__()
        self._ages_file = ages_file
        self._file_pattern = file_pattern
        self._min_bundle_size = min_bundle_size

    def apply(self, pcoll):
        return pcoll.pipeline | beam.io.Read(
            _AgeReader(
                ages_file=self._ages_file,
                file_pattern=self._file_pattern,
                min_bundle_size=self._min_bundle_size))
