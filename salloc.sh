#!/bin/bash
salloc --ntasks=1 --time=0-01:00:00 --gres=gpu:rtx8000:1 --mem=32G --cpus-per-task=10