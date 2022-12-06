#!/bin/bash
#SBATCH --job-name=math23k_question --output=%x_%j.out --ntasks=1 --time=2-0:00:00 --gres=gpu:rtx8000:4 --mem=32G --cpus-per-task=10
bash scripts/run_math23k_train_test.bash