CUDA_VISIBLE_DEVICES=0 \
  python3 universal_main.py \
    --device=cuda:0 \
    --model_folder=mathqa_question_best \
    --mode=test --height=10 \
    --train_max_height=15 \
    --num_epochs=1000 \
    --consider_multiple_m0=1 \
    --train_file=data/MathQA/mathqa_train_nodup_our_filtered.json \
    --add_replacement=1 \
    --train_num=-1 \
    --dev_num=-1 \
    --batch_size=5 \
    --var_update_mode=gru \
    --dev_file=data/MathQA/mathqa_dev_nodup_our_filtered.json \
    --test_file=data/MathQA/mathqa_test_nodup_our_filtered.json \
    --bert_model_name=roberta-base \
    --use_constant=1 \
    --fp16=1 \
    --parallel=1 \
    --learning_rate=2e-5