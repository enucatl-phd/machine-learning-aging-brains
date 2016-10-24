#!/usr/bin/env Rscript

library(argparse)
library(data.table)
library(ggplot2)
library(mixtools)

commandline_parser = ArgumentParser(
        description="")
commandline_parser$add_argument(
    '-f',
    '--file',
    type='character',
    nargs='?',
    default='../data/set_train_histogram.csv',
    help='file with the voxel fractions'
    )

args = commandline_parser$parse_args()

table = fread(args$f)
print(table)

n = 1e7
sampling = sample(
    x=table$bin,
    size=n,
    replace=TRUE,
    prob=table$voxels
    )

dt = data.table(intensity=sampling)
mix = normalmixEM(
    sampling,
    lambda=c(0.06, 0.72, 0.21),
    mu=c(269, 826, 1340),
    sigma=c(64, 261, 93)
    )
print(summary(mix))


plot = ggplot(dt, aes(x=intensity)) + geom_histogram(bins=600)

print(plot)
invisible(readLines("stdin", n=1))
