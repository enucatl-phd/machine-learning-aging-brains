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
    default='data/voxel_fractions_test.csv',
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
    '-a',
    '--age',
    type='character',
    nargs='?',
    default='data/targets.csv',
    help='ages'
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
table = fread(args$f)
ages = fread(args$a)
setnames(table, c("file.name", "gl_csf", "gl_gm", "gl_wm", "csf", "gm", "wm"))
table[, id := as.numeric(strsplit(basename(file_path_sans_ext(file.name)), "_")[[1]][2]), by=file.name]
table[, age := ages[id, V1]]
print(fit)
print(table)

p_a = hist(ages[, V1], breaks=20)
get.age.probability = function(age) {
    binwidth = p_a$breaks[2] - p_a$breaks[1]
    cell = floor((age - p_a$breaks[1]) / binwidth) + 1
    value = p_a$density[cell]
    return(value)           
}
age.classes = data.table(age=15:99)
age.classes[, p_a := get.age.probability(age), by=age]
print(age.classes)


get.gm.given.age.probability = function(gm, age) {
    prediction = data.table(predict(fit, age, interval="prediction", level=0.6827))
    prediction$age = age$age
    prediction$p.age = age$p_a
    prediction[, gm.given.age.prob := dnorm(gm, fit, fit - lwr)]
    age.fit = (gm - fit$coefficients[1]) / fit$coefficients[2]
    prediction[, age.fit := age.fit]
    prediction[, gm := gm]
    return(prediction)
}

probabilities = table[, get.gm.given.age.probability(gm, age.classes), by=id]
probabilities[, p.age.given.gm := gm.given.age.prob * p.age]
probabilities[, norm := gm.given.age.prob %*% p.age, by=id]
probabilities[, p.age.given.gm := p.age.given.gm / norm]

print(probabilities)

bayes.ages = probabilities[, p.age.given.gm %*% age, by=id]
setnames(bayes.ages, "V1", "age")
bayes.ages$age.fit = probabilities[, mean(age.fit), by=id]$V1
print(bayes.ages)


width = 7
factor = 0.618
height = width * factor
plot = ggplot(bayes.ages, aes(x=age.fit, y=age)) + geom_point()
print(plot)
ggsave("../plots/linear.age.vs.bayes.age.png", plot, width=width, height=height, dpi=300)
output = bayes.ages[order(id), .(ID=id, Prediction=round(age))]
print(output)


invisible(readLines("stdin", n=1))
write.csv(output, args$o, row.names=FALSE, quote=FALSE)
