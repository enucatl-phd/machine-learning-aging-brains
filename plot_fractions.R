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
    default='data/voxel_fractions.rds',
    help='file with the ages'
    )

args = commandline_parser$parse_args()

table = readRDS(args$f)
molten = melt(table, measure.vars=c("empty", "csf", "gm", "wm"))[variable != "empty"]

plot = ggplot(molten, aes(x=age, y=value, color=variable)) +
    geom_point()
print(plot)

invisible(readLines("stdin", n=1))
