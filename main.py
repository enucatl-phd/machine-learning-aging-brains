import apache_beam as beam
import agingbrains
import agingbrains.io
import agingbrains.read_age
import agingbrains.voxel_fit


class AgingBrainOptions(beam.utils.options.PipelineOptions):

    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--train",
            dest="train",
            default="data/set_train/train_10[01].nii"
        )
        parser.add_argument(
            "--test",
            dest="test",
            default="data/set_test/test_1[01].nii"
        )
        parser.add_argument(
            "--ages",
            dest="ages",
            default="data/targets.csv"
        )
        parser.add_argument(
            "--output",
            dest="output",
            default="output/OUTPUT_FILE"
        )
        parser.add_argument(
            "--test_slice",
            dest="test_slice",
            action="store_true"
        )


if __name__ == "__main__":
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(AgingBrainOptions)
    datasets = p | "ReadTrainDataset" >> agingbrains.io.ReadNifti1(
        options.train,
        test_slice=options.test_slice)
    # thresholds = datasets | "GlobalThresholding" >> beam.Map(
        # agingbrains.segment.global_thresholding
    # )
    # frontal_thresholds = datasets | "FrontalThresholding" >> beam.Map(
        # agingbrains.segment.frontal_thresholding
    # )
    ages = p | "ReadTrainDatasetAge" >> agingbrains.read_age.ReadAge(
        options.ages, options.train)
    test_dataset = p | "ReadTestDataset" >> agingbrains.io.ReadNifti1(
        options.test,
        test_slice=options.test_slice)
    trained_voxels = ({"data": datasets, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.emit_voxels)
        | beam.GroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.filter_voxels_correlation)
        | beam.core.Map(agingbrains.voxel_fit.estimate_kernel_density)
    )
    test_voxels = test_dataset | beam.core.FlatMap(agingbrains.voxel_fit.emit_test_voxels)
    ({"train": trained_voxels, "test": test_voxels}
        | "CombineTestData" >> beam.CoGroupByKey()
        | "FilterRelevant" >> beam.core.Filter(
            agingbrains.voxel_fit.filter_test_voxels)
        | beam.core.FlatMap(agingbrains.voxel_fit.estimate_age)
        | "RecombineTestBrains" >> beam.core.GroupByKey()
        | beam.core.Map(agingbrains.voxel_fit.average_age)
        | beam.io.WriteToText(options.output)
    )
    p.run()
