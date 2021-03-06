import os
import argparse

import tensorflow as tf

from dataset import Dataset
from hp import set_dataset
import hp


class ProgramArguments(argparse.ArgumentParser):

    def __init__(self, rank: int):
        super().__init__(description='Cnns through asynchronoUs Training and Evolution (cute) for TensorFlow', add_help=True)

        self.rank: int = rank
        self.dataset: str = ""
        self.output_directory: str = ""
        self.number_islands: int = -1
        self.population_size: int = -1
        self.max_genomes: int = -1
        self.backprop_iterations: int = -1

        self.add_argument('dataset', metavar='dataset', type=str, nargs=1,
                            help='the image dataset to be used, select one from the available datasets here: https://www.tensorflow.org/datasets/catalog/overview')
        self.add_argument('output_directory', metavar='output_directory', type=str, nargs=1,
                            help='the directory output logs should be stored in')
        self.add_argument('-ni', '--number_islands', metavar='number_islands', action='store',
                default=1, type=int, help='the number of separate islands to use')
        self.add_argument('-ps', '--population_size', metavar='population_size', action='store',
                default=10, type=int, help='the maximum number of genomes on each islands')
        self.add_argument('-mg', '--max_genomes', metavar='max_genomes', action='store',
                default=1000, type=int, help='the number of genomes to generate and evaluate')
        self.add_argument('-bpi', '--backprop_iterations', metavar='backprop_iterations', action='store',
                default=1, type=int, help='the number of iterations of backpropagation to be applied to generated genomes to evaluate them')
        self.add_argument('-ig', '--ignore_gpus', metavar='ignore_gpus', action='store',
                default=0, type=int, help='whether or not to ignore gpus. if set cpus will be used instead')
        self.add_argument('-l2', '--l2_weight', metavar='l2_weight', action='store', default=None, type=float,
                help='the weight to scale L2 loss by when calculating model loss')
        self.add_argument('-wi', '--weight_initialization', metavar='weight_init', action='store', default='kaiming',
                type=str, help='the method by which weights will be initialized in a network. Valid options are kaiming, xavier / glorot, and epigenetic / epi')
        self.add_argument('-sf', '--slurm_fix', metavar='slurm_fix', action='store', default=0, type=int, help='whether or not to apply a fix that ensures only a single gpu is visible to each MPI process')
        self.add_argument('-gr', '--gpu_ram', metavar='gpu_ram', action='store', default=1024, type=float,
                help='the amount of ram to allocate for logical GPU devices, in MB')
        
        self.args = self.parse_args()

        self.set_dataset()
        self.set_number_epochs()
        self.set_slurm_fix()
        self.set_ignore_gpus()
        self.set_weight_initialization()
    

    def set_weight_initialization(self):
        hp.set_weight_initialization(self.args.weight_initialization)


    def set_number_epochs(self):
        hp.set_number_epochs(self.args.backprop_iterations)
    

    def set_l2_weight(self):
        if self.args.l2_weight:
            x = self.args.l2_weight
        else: 
            x = 0.0

        hp.L2_REGULARIZATION_WEIGHT = x


    def set_dataset(self):
        self.args.dataset = self.args.dataset[0].lower()

        dataset = Dataset.dataset_from_arguments(self)
        set_dataset(dataset)
    

    def set_slurm_fix(self):
        pass


    def set_ignore_gpus(self):
        if self.args.ignore_gpus:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
            tf.config.experimental.set_visible_devices([], 'GPU')
