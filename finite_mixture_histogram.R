#!/usr/bin/env Rscript

library(argparse)
library(data.table)
library(mixtools)
library(ggplot2)
library(oro.nifti)

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
    default='data/finite.mixtures.csv',
    help='output file'
    )
args = commandline_parser$parse_args()

ages = fread(args$a)
nifti2data.table = function(file.name) {
    voxel = readNIfTI(file.name)@.Data
    voxel = as.data.table(voxel)[voxel > 0]
    finite.mixtures = normalmixEM(
        voxel[, voxel],
        mu=c(270, 800, 1330),
        sigma=c(70, 70, 70)
        )
    id = as.numeric(strsplit(strsplit(file.name, "\\.")[[1]][1], "_")[[1]][3])
    return(
        data.table(
            id=id,
            age=ages[id, V1],
            lambda_csf = finite.mixtures$lambda[1],
            mu_csf = finite.mixtures$mu[1],
            sigma_csf = finite.mixtures$sigma[1],
            lambda_gm = finite.mixtures$lambda[2],
            mu_gm = finite.mixtures$mu[2],
            sigma_gm = finite.mixtures$sigma[2],
            lambda_wm = finite.mixtures$lambda[3],
            mu_wm = finite.mixtures$mu[3],
            sigma_wm = finite.mixtures$sigma[3]
            )
        )
}

file.names = data.table(file.name=args$f)
voxels = file.names[,
    nifti2data.table(file.name),
    by=file.name
    ]

write.csv(voxels, file=args$o, row.names=FALSE)
