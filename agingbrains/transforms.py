import apache_beam as beam
from apache_beam import pvalue
import numpy as np

class BuildArrayFn(beam.CombineFn):
    """Better to use the core beam.transforms.combiners.ToDict."""
    def create_accumulator(self):
        return {}

    def add_input(self, data_dict, input):
        data_dict[input[0]] = input[1]
        return data_dict

    def merge_accumulators(self, accumulators):
        new_acc = []
        for acc in accumulators:
            new_acc += acc.items()
        return dict(new_acc)

    def extract_output(self, data_dict):
        return data_dict

def filter_points(data, keylist):
  for k in keylist:
    if data[0] == k:
      yield pvalue.SideOutputValue('%d' % k, data)
      break

def distance_from(data,base_point):
  yield (data[0],base_point[0]), np.linalg.norm(data[1] - base_point[1])
