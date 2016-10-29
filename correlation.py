import apache_beam as beam
import agingbrains
import agingbrains.io
import agingbrains.read_age
import agingbrains.voxel_fit


class CorrelationOptions(beam.utils.options.PipelineOptions):

    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--input",
            dest="input",
            default="data/set_train/train_10[01].nii"
        )
        parser.add_argument(
            "--ages",
            dest="ages",
            default="data/targets.csv"
        )
        parser.add_argument(
            "--output",
            dest="output",
            default="output/CORRELATION_OUTPUT"
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
    ages = p | "ReadAges" >> agingbrains.read_age.ReadAge(
        options.ages, options.input)
    brain_correlation_map = ({"data": datasets, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.emit_voxels)
        | beam.GroupByKey()
        | beam.core.Map(agingbrains.voxel_fit.correlation)
        | beam.core.Map(agingbrains.io.save_correlation)
        | beam.io.WriteToText(options.output)
    )
    p.run()
