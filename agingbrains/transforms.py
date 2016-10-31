import apache_beam as beam
from apache_beam import pvalue
import numpy as np


def filter_points(data, keylist):
  for k in keylist:
    if data[0] == k:
      yield pvalue.SideOutputValue('%d' % k, data)
      break

def distance_from(data,base_point):
  yield (data[0],base_point[0]), np.linalg.norm(data[1] - base_point[1])
