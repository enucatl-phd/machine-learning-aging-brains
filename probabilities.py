import apache_beam as beam
import agingbrains
import agingbrains.io
import agingbrains.read_age
import agingbrains.voxel_fit


class ProbabilitiesOptions(beam.utils.options.PipelineOptions):

    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--train",
            dest="train",
            default="data/filtered_set_train/train_*.npy"
        )
        parser.add_argument(
            "--test",
            dest="test",
            default="data/filtered_set_test/test_*.npy"
        )
        parser.add_argument(
            "--ages",
            dest="ages",
            default="data/targets.csv"
        )
        parser.add_argument(
            "--output",
            dest="output",
            default="output/PREDICTION"
        )
        parser.add_argument(
            "--test_slice",
            dest="test_slice",
            action="store_true"
        )


if __name__ == "__main__":
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(ProbabilitiesOptions)
    train_dataset = p | "ReadTrainDataset" >> agingbrains.io.ReadNumpy(
        options.train,
        test_slice=options.test_slice)
    ages = p | "ReadAges" >> agingbrains.read_age.ReadAge(
        options.ages, options.train)
    trained_voxels = (
        {"data": train_dataset, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.emit_voxels)
        | "GroupTrainVoxels" >> beam.GroupByKey()
        | beam.core.Map(agingbrains.voxel_fit.estimate_kernel_density)
    )
    test_voxels = (
        p
        | "ReadTestDataset" >> agingbrains.io.ReadNumpy(
            options.test,
            test_slice=options.test_slice)
        | beam.core.FlatMap(agingbrains.voxel_fit.emit_test_voxels)
    )
    (
        {"train": trained_voxels, "test": test_voxels}
        | "GroupTrainWithTest" >> beam.CoGroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.estimate_age)
        | beam.core.Map(agingbrains.io.save_probabilities)
        | beam.io.WriteToText(options.output, file_name_suffix=".tgz")
    )
    p.run()
