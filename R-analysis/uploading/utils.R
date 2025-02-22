# Env set up and packages
knitr::opts_chunk$set(echo=FALSE, warning = FALSE)
knitr::opts_chunk$set(fig.width=12, fig.height=8) 

library(tidyverse)
library(fs)
library(ggplot2)
library(ez)
library(gt)

library(ezPurrr)

library(lme4)
library(lmerTest)

theme_set(theme_classic(7))

cbPalette <- c("#CC79A7","#0072B2","#009E73","#E69F00","#56B4E9","#F0E442","#D55E00","#999999")
#pink, green, blue, yellow

converting_read <- function(curr_path){
  print(curr_path)
  read_csv(curr_path) %>% mutate(sub = as.character(sub_x))
}

converting_read2 <- function(curr_path){
  print(curr_path)
  read_csv(curr_path) %>% mutate(sub = as.character(sub))
}

converting_read3 <- function(curr_path){
  print(curr_path)
  read_csv(curr_path) %>% mutate(sub = as.character(sub),
                                 resp_obj = as.character(resp_obj))
}

# return all modes
Modes <- function(x) {
  ux <- unique(x)
  tab <- tabulate(match(x, ux))
  ux[tab == max(tab)]
}

# project specific setup
sub_dir = dir_ls(here::here("./csv_files/python_summary_z-scores/"))
sub_behav_dir = dir_ls(here::here("./csv_files/behavior"))

rois_names = c('ca23dg-body', 'ca1-body', 
               'evc', 'ppa')

bad = c('13', '14', '20', '23', '24', '27', '30', '34')
# 14 30 34 for behav files
# 13 20 23 24 27 30 for scan and behav files

# loading data functions
loading_rolling_df <- function(){
files <- map(sub_dir, dir_ls, glob = '*/*rolling3_*summary_with_destination.csv') %>% unlist()
rolling <- map_dfr(files, converting_read)
rolling = rolling %>% 
  filter(!(sub %in% bad))
print(length(unique(rolling$sub)))
rolling
}

loading_rolling_rounds_df <- function(){
  files <- map(sub_dir, dir_ls, glob = '*/*rolling3_*summary_with_pairs_and_rounds.csv') %>% unlist()
  rolling <- map_dfr(files, converting_read)
  rolling = rolling %>% 
    filter(!(sub %in% bad))
  print(length(unique(rolling$sub)))
  rolling
}

loading_rolling_trial_df <- function(){
  files <- map(sub_dir, dir_ls, glob = '*/*rolling3_*summary_with_trials.csv') %>% unlist()
  rolling <- map_dfr(files, converting_read)
  rolling = rolling %>% 
    filter(!(sub %in% bad))
  print(length(unique(rolling$sub)))
  rolling
}

loading_norolloing_df <- function(){
  files <- map(sub_dir, dir_ls, glob = '*/*norolling_*summary_with_destination.csv') %>% unlist()
  norolling <- map_dfr(files, converting_read)
  norolling = norolling %>% 
    filter(!(sub %in% bad))
  print(length(unique(norolling$sub)))
  norolling
}

loading_postscan1_df <- function(){
  postscan1_behav <- map(sub_behav_dir, dir_ls, glob = '*postscan1*_behav*.csv') %>% unlist()
  postscan1_batch <- map_dfr(postscan1_behav, converting_read2)
  postscan1_batch <- postscan1_batch %>% 
    filter(!(sub %in% bad))
  postscan1_batch = postscan1_batch %>% 
    mutate(
      correct = ifelse(resp_obj == destination, 1, 0),
      conf = abs(resp))
}

loading_postscan2_df <- function(){
postscan2_behav <- map(sub_behav_dir, dir_ls, glob = '*postscan2*_behav*.csv') %>% unlist()
postscan2_batch <- map_dfr(postscan2_behav, converting_read2)
postscan2_batch <- postscan2_batch %>% 
  filter(!(sub %in% bad))
postscan2_batch = postscan2_batch %>% 
  mutate(
    correct = ifelse(!is.na(post_first_resp_obj) & post_first_resp_obj == destination, 1, 0))
print(length(unique(postscan2_batch$sub)))
postscan2_batch
}

loading_scan_behav_df <- function(){
  sub_dir = dir_ls(here::here("./csv_files/behavior"))
  scan_behav <- map(sub_dir, dir_ls, regexp = '(.*)_scan(\\d?\\d)_behav_.*') %>% unlist()
  scan_batch <- map_dfr(scan_behav, converting_read3)
  scan_batch <- scan_batch %>% 
    filter(sub != '14' & sub != '30' & sub != '34') %>% filter(!(sub %in% bad))
  print(length(unique(scan_batch$sub)))
  scan_batch %>% 
  mutate(
    correct = ifelse(!is.na(resp_obj) & resp_obj == destination, 1, 0),
    confidence = ifelse(!is.na(conf_resp) & conf_resp == 6, 1, 0),
    cor_conf = ifelse(!is.na(resp_obj) & !is.na(conf_resp) & (resp_obj == destination & 
                                                                conf_resp== 6), 1, 0))
}

loading_prescan_behav_df <- function(){
  sub_dir = dir_ls(here::here("./csv_files/behavior"))
  prescan_behav <- map(sub_dir, dir_ls, glob = '*prescan*_behav*.csv') %>% unlist()
  prescan_batch <- map_dfr(prescan_behav, converting_read2)
  prescan_batch <- prescan_batch %>% 
    filter(sub != '14' & sub != '30' & sub != '34') %>% filter(!(sub %in% bad))
  print(length(unique(prescan_batch$sub)))
  prescan_batch = prescan_batch %>% 
    mutate(
      nquestion = rep(c(1, 2, 3), times = nrow(prescan_batch)/3),
      correct = ifelse(!is.na(resp_obj) & resp_obj == destination, 1, 0),
      confidence = ifelse(!is.na(conf_resp) & conf_resp == 6, 1, 0),
      cor_conf = ifelse((!is.na(resp_obj) & !is.na(conf_resp) &
                           resp_obj == destination & 
                           conf_resp== 6), 1, 0))
}
