from __future__ import division
import argparse
import os
CUDA_LAUNCH_BLOCKING=1
import torch
from mmcv import Config

from mmdet import __version__
from mmdet.apis import (get_root_logger, init_dist, set_random_seed,
                        train_detector)
from mmdet.datasets import build_dataset
from mmdet.models import build_detector

from mmdet.datasets import DATASETS, build_dataloader


def parse_args():
    parser = argparse.ArgumentParser(description='Train a detector')
    parser.add_argument('config', help='train config file path')
    parser.add_argument('--work_dir', help='the dir to save logs and models')
    parser.add_argument(
        '--resume_from', help='the checkpoint file to resume from')
    parser.add_argument(
        '--validate',
        action='store_true',
        help='whether to evaluate the checkpoint during training')
    parser.add_argument(
        '--gpus',
        type=int,
        default=1,
        help='number of gpus to use '
        '(only applicable to non-distributed training)')
    parser.add_argument('--seed', type=int, default=None, help='random seed')
    parser.add_argument(
        '--launcher',
        choices=['none', 'pytorch', 'slurm', 'mpi'],
        default='none',
        help='job launcher')
    parser.add_argument('--local_rank', type=int, default=0)
    parser.add_argument(
        '--autoscale-lr',
        action='store_true',
        help='automatically scale lr with the number of gpus')
    parser.add_argument('--data_root', help='data root')
    args = parser.parse_args()
    if 'LOCAL_RANK' not in os.environ:
        os.environ['LOCAL_RANK'] = str(args.local_rank)

    return args


def main():
    args = parse_args()

    cfg = Config.fromfile(args.config)
    # update workdir and data_root:
    if args.work_dir:
        cfg.work_dir  = args.work_dir
    if args.data_root:
        cfg.data.train.ann_file  = cfg.data.train.ann_file.replace(cfg.data_root,args.data_root)
        cfg.data.train.img_prefix= cfg.data.train.img_prefix.replace(cfg.data_root,args.data_root)
        cfg.data.val.ann_file    = cfg.data.val.ann_file.replace(cfg.data_root,args.data_root)
        cfg.data.val.img_prefix  = cfg.data.val.img_prefix.replace(cfg.data_root,args.data_root)
        cfg.data.test.ann_file   = cfg.data.test.ann_file.replace(cfg.data_root,args.data_root)
        cfg.data.test.img_prefix = cfg.data.test.img_prefix.replace(cfg.data_root,args.data_root)
        cfg.data_root = args.data_root

    # Copy config file to work_dir
    os.makedirs(cfg.work_dir, exist_ok=True)
    os.system("cp %s %s" % (args.config, cfg.work_dir))

    # set cudnn_benchmark
    if cfg.get('cudnn_benchmark', False):
        torch.backends.cudnn.benchmark = True
    # update configs according to CLI args
    if args.resume_from is not None:
        cfg.resume_from = args.resume_from
    cfg.gpus = args.gpus

    # if args.autoscale_lr:
    #     # apply the linear scaling rule (https://arxiv.org/abs/1706.02677)
    #     cfg.optimizer['lr'] = cfg.optimizer['lr'] * cfg.gpus / 8

    # init distributed env first, since logger depends on the dist info.
    if args.launcher == 'none':
        distributed = False
    else:
        distributed = True
        init_dist(args.launcher, **cfg.dist_params)

    # init logger before other steps
    logger = get_root_logger(cfg.log_level)
    logger.info('Distributed training: {}'.format(distributed))

    # set random seeds
    if args.seed is not None:
        logger.info('Set random seed to {}'.format(args.seed))
        set_random_seed(args.seed)

    model = build_detector(
        cfg.model, train_cfg=cfg.train_cfg, test_cfg=cfg.test_cfg)
        
    datasets = [build_dataset(cfg.data.train)]
    if len(cfg.workflow) == 2:
        datasets.append(build_dataset(cfg.data.val))
    if cfg.checkpoint_config is not None:
        # save mmdet version, config file content and class names in
        # checkpoints as meta data
        cfg.checkpoint_config.meta = dict(
            mmdet_version=__version__,
            config=cfg.text,
            CLASSES=datasets[0].CLASSES)
    # add an attribute for visualization convenience
    model.CLASSES = datasets[0].CLASSES

    train_detector(
        model,
        datasets,
        cfg,
        distributed=distributed,
        validate=args.validate,
        logger=logger)

if __name__ == '__main__':
    main()
