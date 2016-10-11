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
    default='data/finite_mixtures_set_train.csv',
    help='file with the voxel fractions'
    )

args = commandline_parser$parse_args()

table = fread(args$f)
print(table)


#molten = melt(table, measure.vars=c("lambda_csf", "lambda_gm", "lambda_wm"))
#molten = melt(table, measure.vars=c("mu_csf", "mu_gm", "mu_wm"))
molten = melt(table, measure.vars=c("sigma_csf", "sigma_gm", "sigma_wm"))

#fit = lm(gm ~ age, data=table)
#b = fit$coefficients[1]
#a = fit$coefficients[2]
#saveRDS(fit, args$o)
#print(summary(fit))


plot = ggplot(molten, aes(x=age, y=value, color=variable)) +
    geom_point()
print(plot)


width = 7
factor = 0.618
height = width * factor
ggsave("plots/finite.mixtures.png", plot, width=width, height=height, dpi=300)
invisible(readLines("stdin", n=1))
