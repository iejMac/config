#!/bin/bash
#SBATCH --partition=compute-od-gpu
#SBATCH --job-name=openclip-frozenlm
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 8
#SBATCH --cpus-per-gpu=6
#SBATCH --gres=gpu:8
#SBATCH --output=%x_%j.out
#SBATCH --comment "Key=Monitoring,Value=ON"
#SBATCH --exclusive

# sent to sub script
export HOSTNAMES=`scontrol show hostnames "$SLURM_JOB_NODELIST"`
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=12802
export COUNT_NODE=`scontrol show hostnames "$SLURM_JOB_NODELIST" | wc -l`

export TOKENIZERS_PARALLELISM=false

echo go $COUNT_NODE
echo $HOSTNAMES

source /fsx/iejmac/open_clip/.env/bin/activate
cd /fsx/iejmac/open_clip/src/

srun --cpu-bind=v --accel-bind=gn python3.8 -m training.main \
        --train-data="pipe:aws s3 cp s3://s-mas/cc3m/{00000..00329}.tar -" \
        --train-num-samples 3000000 \
        --val-data="pipe:aws s3 cp s3://s-mas/cc3m/{00330..00331}.tar -" \
        --val-num-samples 10000 \
        --dataset-type webdataset \
        --batch-size 256 \
        --warmup 2000 \
        --epochs 10 \
        --lr 5e-4 \
        --precision amp \
        --workers 6 \
        --model "ViT-B-32" \
        --name "scratch_lm_baseline" \
        --report-to "tensorboard" \
