import apache_beam as beam
import agingbrains
import agingbrains.io
import agingbrains.read_gender
import agingbrains.voxel_fit


class CorrelationOptions(beam.utils.options.PipelineOptions):

    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--input",
            dest="input",
            default="data/set_train/train_1*.nii"
        )
        parser.add_argument(
            "--genders",
            dest="genders",
            default="data/mlp3-targets.csv"
        )
        parser.add_argument(
            "--output",
            dest="output",
            default="output/GENDER_OUTPUT"
        )
        parser.add_argument(
            "--test_slice",
            dest="test_slice",
            action="store_true"
        )


if __name__ == "__main__":
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(CorrelationOptions)
    datasets = p | "ReadTrainDataset" >> agingbrains.io.ReadNifti1(
        options.input,
        test_slice=options.test_slice)
    genders = p | "ReadGenders" >> agingbrains.read_gender.ReadGender(
        options.genders, options.input)
    brain_correlation_map = ({"data": datasets, "gender": genders}
        | "GroupWithGender" >> beam.CoGroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.emit_voxels)
        | beam.GroupByKey()
        | beam.core.Map(agingbrains.voxel_fit.fisher_score)
        | beam.core.Map(agingbrains.io.save_correlation)
        | beam.io.WriteToText(
            options.output, 
            compression_type=beam.io.fileio.CompressionTypes.GZIP,
            file_name_suffix=".tgz")
    )
    p.run()
