#!/usr/bin/env Rscript

library(oro.nifti)
library(argparse)
library(data.table)

commandline_parser = ArgumentParser(
        description="")
commandline_parser$add_argument(
    '-f',
    '--files',
    type='character',
    nargs='*',
    help='image'
    )
commandline_parser$add_argument(
    '-a',
    '--age',
    type='character',
    nargs='?',
    default='data/targets.csv',
    help='file with the ages'
    )
commandline_parser$add_argument(
    '-o',
    '--output',
    type='character',
    nargs='?',
    default='data/voxel_fractions.rds',
    help='output file'
    )
args = commandline_parser$parse_args()

ages = fread(args$a)

nifti2data.table = function(file.name) {
    voxel = readNIfTI(file.name)@.Data
    voxel = as.data.table(voxel)
    n = nrow(voxel)
    empty = nrow(voxel[voxel == 0])
    csf = nrow(voxel[voxel > 0 & voxel < 315])
    gm = nrow(voxel[voxel >= 315 & voxel < 1110])
    wm = nrow(voxel[voxel >= 1110])
    id = as.numeric(strsplit(strsplit(file.name, "\\.")[[1]][1], "_")[[1]][3])
    return(data.table(id=id, age=ages[id, V1], empty=empty, csf=csf, gm=gm, wm=wm))
}

file.names = data.table(file.name=args$f)
voxels = file.names[, nifti2data.table(file.name), by=file.name]

saveRDS(voxels, args$o)
