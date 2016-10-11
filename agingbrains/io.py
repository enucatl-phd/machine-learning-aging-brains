import nibabel as nb
import apache_beam as beam

class _NibabelSource(beam.io.filebasedsource.FileBasedSource):

    def read_records(self, file_name, range_tracker):
        with self.open_file(file_name) as f:
            record = nb.load(file_name)
            yield record
