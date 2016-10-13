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
            "--output",
            dest="output",
            nargs="*",
            default="output/OUTPUT_FILE"
        )


if __name__ == "__main__":
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(AgingBrainOptions)
    datasets = p | "Read" >> ab.io.ReadNifti1(options.input)
    thresholds = datasets | "GlobalThresholding" >> beam.Map(
        ab.segment.global_thresholding
    )
    thresholds | beam.io.WriteToText(options.output)
    p.run()
