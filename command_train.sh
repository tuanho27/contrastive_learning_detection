CONFIG_FILE="mmdetection/configs/retinanet_r50_fpn_1x.py"
GPUS=2
SEED=0

export CUDA_VISIBLE_DEVICES=0,1
python -m torch.distributed.launch --nproc_per_node=$GPUS \
	--master_port=$((RANDOM + 10000)) \
    mmdetection/tools/train.py $CONFIG_FILE --launcher pytorch --seed $SEED  #--validate

# export CUDA_VISIBLE_DEVICES=1
# python  mmdetection/tools/train.py $CONFIG_FILE
