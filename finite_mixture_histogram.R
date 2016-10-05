#!/usr/bin/env Rscript

library(argparse)
library(data.table)
library(mixtools)
library(ggplot2)

theme_set(theme_bw(base_size=12) + theme(
    legend.key.size=unit(1, 'lines'),
    text=element_text(face='plain', family='CM Roman'),
    legend.title=element_text(face='plain'),
    axis.line=element_line(color='black'),
    axis.title.y=element_text(vjust=0.1),
    axis.title.x=element_text(vjust=0.1),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    legend.key = element_blank(),
    panel.border = element_blank()
))

commandline_parser = ArgumentParser(
        description="fit histogram with two components")
commandline_parser$add_argument('-f', '--file',
            type='character', nargs='?', default='data/set_train_histogram.csv',
            help='file with the data.table')
args = commandline_parser$parse_args()

table = fread(args$f)[, voxels := voxels / sum(voxels)]

sigma = 100
print(table[, voxels])

finite.mixture = normalmixEM2comp(
    table[, voxels],
    lambda=1,
    mu=c(800, 1350),
    sigsqrd=c(sigma*sigma, sigma*sigma),
    verb=TRUE
    )

print(summary(finite.mixture))
plot(finite.mixture)
