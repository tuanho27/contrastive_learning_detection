#!/usr/bin/env bash

PYTHON=${PYTHON:-"python"}

CONFIG_FILE=mmdetection/configs/retinanet_r50_fpn_1x.py
WORK_DIR=/home/chuong/Workspace/Experiments/retina-R50

th=12
CHECKPOINT_FILE=${WORK_DIR}/retinanet_r50_fpn_1x_20181125-7b0c2548.pth
RESULT_FILE=${WORK_DIR}/epoch_${th}_025.pkl
WRITE_TO=${WORK_DIR}/epoch_${th}_025.txt

GPUS=2
CUDA_VISIBLE_DEVICES=0,1

# mmdetection/tools/dist_test.sh ${CONFIG_FILE} ${CHECKPOINT_FILE} ${GPU} --out $WRITE_TO --eval bbox

$PYTHON -m torch.distributed.launch --nproc_per_node=$GPUS \
        mmdetection/tools/test.py ${CONFIG_FILE} ${CHECKPOINT_FILE} --launcher pytorch --out ${RESULT_FILE} --eval bbox
# $PYTHON mmdetection/tools/voc_eval.py ${RESULT_FILE} ${CONFIG_FILE} --iou-th=0.5 > $WRITE_TO
# cat $WRITE_TO