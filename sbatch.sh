#!/bin/bash
#SBATCH --job-name=mathqa_rev --output=%x_%j.out --ntasks=1 --time=2-0:00:00 --gres=gpu:rtx8000:4 --mem=32G --cpus-per-task=10
bash scripts/train_mathqa.bash