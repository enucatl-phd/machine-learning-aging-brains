import apache_beam as beam
import agingbrains as ab


class AgingBrainOptions(beam.utils.options.PipelineOptions):

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
    datasets = p | "ReadData" >> ab.io.ReadNifti1(
        options.input,
        test_slice=options.test_slice)
    thresholds = datasets | "GlobalThresholding" >> beam.Map(
        ab.segment.global_thresholding
    )
    frontal_thresholds = datasets | "FrontalThresholding" >> beam.Map(
        ab.segment.frontal_thresholding
    )
    ages = p | "ReadAge" >> ab.read_age.ReadAge(options.ages, options.input)
    voxels = ({"data": datasets, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | beam.core.FlatMap(ab.voxel_fit.emit_voxels)
        | beam.core.GroupByKey()
        | beam.core.FlatMap(ab.voxel_fit.filter_empty)
        | beam.core.Map(ab.voxel_fit.fit_voxel)
        | beam.io.WriteToText(options.output)
    )
    # merged = {
        # "global": thresholds,
        # "frontal": frontal_thresholds,
        # "age": ages,
    # } | beam.CoGroupByKey()
    # (
        # merged
        # | beam.Map(ab.io.groups2csv)
        # | beam.io.WriteToText(options.output)
    # )
    p.run()
