import os
import apache_beam as beam


class _GenderReader(beam.io.filebasedsource.FileBasedSource):

    def __init__(self, genders_file, file_pattern, min_bundle_size):
        super(_GenderReader, self).__init__(
            file_pattern=file_pattern,
            min_bundle_size=min_bundle_size,
            splittable=False)
        self._genders_file = genders_file

    def read_records(self, file_name, range_tracker):
        with self.open_file(self._genders_file) as f:
            basename = os.path.splitext(os.path.basename(file_name))[0]
            i = int(basename.split("_")[1]) - 1
            gender = int(f.read().split()[i].split(",")[0])
            yield (file_name, gender)


class ReadGender(beam.transforms.PTransform):

    def __init__(self, genders_file, file_pattern=None, min_bundle_size=0):
        super(ReadGender, self).__init__()
        self._genders_file = genders_file
        self._file_pattern = file_pattern
        self._min_bundle_size = min_bundle_size

    def apply(self, pcoll):
        return pcoll.pipeline | beam.io.Read(
            _GenderReader(
                genders_file=self._genders_file,
                file_pattern=self._file_pattern,
                min_bundle_size=self._min_bundle_size))
