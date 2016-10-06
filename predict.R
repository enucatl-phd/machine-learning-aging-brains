#!/usr/bin/env Rscript

library(argparse)
library(data.table)

commandline_parser = ArgumentParser(
        description="")
commandline_parser$add_argument(
    '-f',
    '--file',
    type='character',
    nargs='?',
    default='data/set_test_fractions.rds',
    help='table with gm fractions'
    )
commandline_parser$add_argument(
    '-r',
    '--regression',
    type='character',
    nargs='?',
    default='data/fit_gm_age.rds',
    help='fit with the gm vs age regression'
    )
commandline_parser$add_argument(
    '-o',
    '--output',
    type='character',
    nargs='?',
    default='data/prediction.csv',
    help='output for the competition'
    )
args = commandline_parser$parse_args()

fit = readRDS(args$r)
table = readRDS(args$f)
print(fit)
print(table)


prediction = data.table(predict(fit, table, interval="confidence"))
output = prediction[, .(ID=.I, Prediction=round(fit))]
print(output)

write.csv(output, args$o, row.names=FALSE, quote=FALSE)
