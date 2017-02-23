#!/usr/bin/env Rscript

library(ggplot2)
library(data.table)
library(argparse)

commandline_parser = ArgumentParser(
        description="")
commandline_parser$add_argument(
    'files',
    type='character',
    nargs="*",
    help='tgz files'
    )

args = commandline_parser$parse_args()
files.dt = data.table(file.name=args$files)
data = files.dt[, fread(file.name), by=file.name]
data[, file.name := NULL]
setnames(data, c("V1", "V2"), c("ID", "voxel"))
old.ages.cols = paste0(rep("V", 84), seq(3, 86))
new.ages.cols = as.character(seq(15, 98))
setnames(data, old.ages.cols, new.ages.cols)
setkey(data, "ID")
setkey(data, "voxel")
molten = melt(
    data,
    id.vars=c("ID", "voxel"),
    variable.name="age",
    value.name="prob"
    )
molten[, age := as.numeric(age)]
