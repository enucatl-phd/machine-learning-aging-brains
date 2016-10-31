import apache_beam as beam
import agingbrains
import agingbrains.io
import agingbrains.read_age
import agingbrains.voxel_fit
from agingbrains.transforms import filter_points, distance_from

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


def compute_distance_matrix():
    """This should be run locally with :local_af"""
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(AgingBrainOptions)
    datasets = p | "ReadTrainDataset" >> agingbrains.io.ReadNifti1(
        options.train,
        test_slice=options.test_slice)
    paired = ( datasets
      | beam.Map(
        lambda data: (
          int(data[0].split("/")[-1].split("_")[-1].split(".")[0])-1,
          data[1].flatten()
        )
      )
    )
    keys = range(99,149)
    pcoll_tuple = (
      paired
      | "Split Data" >> beam.FlatMap(filter_points,keylist=keys).with_outputs()
    )

    dist_mat = ( [ paired
        | "Distance From %d" %k >>beam.FlatMap(distance_from,base_point=beam.pvalue.AsSingleton(pcoll_tuple['%d'%k]))
        for k in keys ]
      ) | beam.Flatten()

    dist_mat | beam.io.WriteToText(options.output)
    p.run()

if __name__ == "__main__":
    compute_distance_matrix()
