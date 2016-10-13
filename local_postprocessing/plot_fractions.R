#!/usr/bin/env Rscript

library(argparse)
library(data.table)
library(ggplot2)
library(tools)

commandline_parser = ArgumentParser(
        description="")
commandline_parser$add_argument(
    '-f',
    '--file',
    type='character',
    nargs='?',
    default='../data/voxel_fractions.csv',
    help='file with the voxel fractions'
    )
commandline_parser$add_argument(
    '-a',
    '--age',
    type='character',
    nargs='?',
    default='../data/targets.csv',
    help='file with the ages'
    )
commandline_parser$add_argument(
    '-o',
    '--output',
    type='character',
    nargs='?',
    default='../data/fit_gm_age.rds',
    help='output for the gm vs age fit'
    )

args = commandline_parser$parse_args()

table = fread(args$f)
ages = fread(args$a)
table[, age := ages[id, V1]]
table[, empty := empty / 10]
print(table)


molten = melt(table, measure.vars=c("csf", "gm", "wm"))
#molten = melt(table, measure.vars=c("mean"))

#fit = lm(gm ~ age, data=table)
#b = fit$coefficients[1]
#a = fit$coefficients[2]
#saveRDS(fit, args$o)
#print(summary(fit))


plot = ggplot(molten, aes(x=age, y=value, color=variable)) +
    geom_point() +
    xlab("age")
print(plot)


width = 7
factor = 0.618
height = width * factor
ggsave("../plots/fractions.png", plot, width=width, height=height, dpi=300)
invisible(readLines("stdin", n=1))
