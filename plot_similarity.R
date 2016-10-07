#!/usr/bin/env Rscript

library(argparse)
library(data.table)
library(ggplot2)

commandline_parser = ArgumentParser(
        description="")
commandline_parser$add_argument(
    '-f',
    '--file',
    type='character',
    nargs='?',
    default='data/similarity.csv',
    help='file with the voxel fractions'
    )
args = commandline_parser$parse_args()

table = fread(args$f)
molten = melt(table, measure.vars=c("ssim3", "ssim5"))

plot = ggplot(molten, aes(x=abs(age1 - age2), y=mse, colour=variable)) +
    geom_point()
print(plot)

width = 7
factor = 0.618
height = width * factor
invisible(readLines("stdin", n=1))
