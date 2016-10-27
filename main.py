import apache_beam as beam
import agingbrains as ab


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
    datasets = p | "ReadTrainDataset" >> ab.io.ReadNifti1(
        options.train,
        test_slice=options.test_slice)
    thresholds = datasets | "GlobalThresholding" >> beam.Map(
        ab.segment.global_thresholding
    )
    frontal_thresholds = datasets | "FrontalThresholding" >> beam.Map(
        ab.segment.frontal_thresholding
    )
    ages = p | "ReadTrainDatasetAge" >> ab.read_age.ReadAge(
        options.ages, options.train)
    test_dataset = p | "ReadTestDataset" >> ab.io.ReadNifti1(
        options.test,
        test_slice=options.test_slice) trained_voxels = ({"data": datasets, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | beam.core.FlatMap(ab.voxel_fit.emit_voxels)
        | beam.GroupByKey()
        | beam.core.FlatMap(ab.voxel_fit.filter_empty)
        | beam.core.FlatMap(ab.voxel_fit.fit_voxel)
        | beam.core.Map(ab.voxel_fit.estimate_kernel_density)
    )
    test_voxels = test_dataset | beam.core.FlatMap(ab.voxel_fit.emit_test_voxels)
    ({"train": trained_voxels, "test": test_voxels}
        | "CombineTestData" >> beam.CoGroupByKey()
        | "FilterRelevant" >> beam.core.Filter(
            ab.voxel_fit.filter_test_voxels)
        | beam.core.FlatMap(ab.voxel_fit.estimate_age)
        | "RecombineTestBrains" >> beam.core.GroupByKey()
    )
    p.run()
