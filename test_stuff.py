import apache_beam as beam
import agingbrains
import agingbrains.io
import agingbrains.read_age
import agingbrains.voxel_fit
import numpy as np
from apache_beam import pvalue

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

def read_all_and_group():
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(AgingBrainOptions)
    datasets = p | "ReadTrainDataset" >> agingbrains.io.ReadNifti1(
        options.train,
        test_slice=options.test_slice)
    ages = p | "ReadTrainDatasetAge" >> agingbrains.read_age.ReadAge(
        options.ages, options.train)
    trained_voxels = ({"data": datasets, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | "SaveGroupedData" >> beam.io.WriteToText(options.output)
    )
    p.run()

def read_and_emit_voxels():
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(AgingBrainOptions)
    datasets = p | "ReadTrainDataset" >> agingbrains.io.ReadNifti1(
        options.train,
        test_slice=options.test_slice)
    ages = p | "ReadTrainDatasetAge" >> agingbrains.read_age.ReadAge(
        options.ages, options.train)
    trained_voxels = ({"data": datasets, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | "ProduceVoxels" >> beam.core.FlatMap(agingbrains.voxel_fit.emit_voxels)
        | beam.GroupByKey()
        | "SaveGroupedData" >> beam.io.WriteToText(options.output)
    )
    p.run()

def distance_from(data,base_point):
  yield (data[0],base_point[0]), np.linalg.norm(data[1] - base_point[1])

def filter_points(data, keylist):
  for k in keylist:
    if data[0] == k:
      yield pvalue.SideOutputValue('%d' % k, data)
      break

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
    keys = range(278)
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

def old_main():
    pipeline_options = beam.utils.options.PipelineOptions()
    p = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(AgingBrainOptions)
    datasets = p | "ReadTrainDataset" >> agingbrains.io.ReadNifti1(
        options.train,
        test_slice=options.test_slice)
    thresholds = datasets | "GlobalThresholding" >> beam.Map(
        agingbrains.segment.global_thresholding
    )
    frontal_thresholds = datasets | "FrontalThresholding" >> beam.Map(
        agingbrains.segment.frontal_thresholding
    )
    ages = p | "ReadTrainDatasetAge" >> agingbrains.read_age.ReadAge(
        options.ages, options.train)
    test_dataset = p | "ReadTestDataset" >> agingbrains.io.ReadNifti1(
        options.test,
        test_slice=options.test_slice)
    trained_voxels = ({"data": datasets, "age": ages}
        | "GroupWithAge" >> beam.CoGroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.emit_voxels)
        | beam.GroupByKey()
        | beam.core.FlatMap(agingbrains.voxel_fit.filter_empty)
        | beam.core.FlatMap(agingbrains.voxel_fit.fit_voxel)
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
