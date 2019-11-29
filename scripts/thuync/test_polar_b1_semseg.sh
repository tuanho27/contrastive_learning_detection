#!/usr/bin/env bash

CONFIG_FILE='ccdetection/configs/polarmask/polar_b1_semseg.py'
WORK_DIR='/home/member/Workspace/thuync/checkpoints/polar_b1_semseg/'

th=12
CHECKPOINT_FILE="${WORK_DIR}/epoch_${th}.pth"
RESULT_FILE="${WORK_DIR}/epoch_${th}.pkl"

GPUS=2
export CUDA_VISIBLE_DEVICES=1
PYTHON=${PYTHON:-"python"}

$PYTHON -m torch.distributed.launch --nproc_per_node=$GPUS \
	mmdetection/tools/test.py ${CONFIG_FILE} ${CHECKPOINT_FILE} \
	--launcher pytorch --out ${RESULT_FILE} --eval bbox segm