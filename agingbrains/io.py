import nibabel as nb
import numpy as np
import apache_beam as beam
import StringIO
import csv


class _Nifti1Source(beam.io.filebasedsource.FileBasedSource):

    def __init__(self, file_pattern, min_bundle_size):
        super(_Nifti1Source, self).__init__(
            file_pattern=file_pattern,
            min_bundle_size=min_bundle_size,
            splittable=False)

    def read_records(self, file_name, range_tracker):
        with self.open_file(file_name) as f:
            hdr_fh = nb.fileholders.FileHolder(fileobj=f)
            img_fh = nb.fileholders.FileHolder(fileobj=f)
            file_map = {"image": img_fh}
            header = nb.Nifti1Image.header_class.from_fileobj(f)
            data = header.data_from_fileobj(f)[
                # 107-2:107+2,
                # 76-2:76+2,
                # 100-2:100+2
                ..., 0
            ]
            yield (file_name, data)


class ReadNifti1(beam.transforms.PTransform):

    def __init__(self, file_pattern=None, min_bundle_size=0):
        super(ReadNifti1, self).__init__()
        self._file_pattern = file_pattern
        self._min_bundle_size = min_bundle_size

    def apply(self, pcoll):
        return pcoll.pipeline | beam.io.Read(
            _Nifti1Source(
                file_pattern=self._file_pattern,
                min_bundle_size=self._min_bundle_size))


def groups2csv((name, dictionary)):
    l = (
        [name] +
        dictionary["age"] +
        list(dictionary["global"][0]) +
        list(dictionary["frontal"][0])
    )
    line = StringIO.StringIO()
    writer = csv.writer(line, lineterminator="")
    writer.writerow(l)
    return line.getvalue()
