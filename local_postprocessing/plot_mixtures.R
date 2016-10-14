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
    default='../data/finite_mixtures_set_train.csv',
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
    help='fit'
    )

args = commandline_parser$parse_args()

table = fread(args$f)
ages = fread(args$a)
setnames(table, c("file.name", "gl_csf", "gl_gm", "gl_wm", "csf", "gm", "wm"))
table[, id := as.numeric(strsplit(basename(file_path_sans_ext(file.name)), "_")[[1]][2]), by=file.name]
table[, age := ages[id, V1]]
print(table)


fit = lm(gm ~ age, data=table)
b = fit$coefficients[1]
a = fit$coefficients[2]
saveRDS(fit, args$o)
print(summary(fit))


molten = melt(table, measure.vars=c("gl_csf", "gl_gm", "gl_wm", "gm", "wm"))
plot = ggplot(molten, aes(x=age, y=value, color=variable)) +
    geom_point() +
    geom_abline(slope=a, intercept=b)
print(plot)


width = 7
factor = 0.618
height = width * factor
ggsave("../plots/finite.mixtures.png", plot, width=width, height=height, dpi=300)
invisible(readLines("stdin", n=1))
