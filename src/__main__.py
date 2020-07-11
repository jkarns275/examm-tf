import os
import sys
import pickle
import logging
from typing import List
# This hides tensorflow debug output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # or any {'0', '1', '2'}

from mpi4py import MPI
import tensorflow as tf

import hp
from cnn import ConvEdge, CnnGenome, DenseEdge, Edge, Layer, InputLayer, OutputLayer
from cute import Cute
from master import Master
from worker import Worker
from dataset import Dataset
from program_arguments import ProgramArguments

def gpu_fix():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(e)


def graph_genome_main(args: List[str]):
    gpu_fix()
    
    genome_path = args[2]
    image_dst = args[3]

    genome: CnnGenome = pickle.load(open(genome_path, 'rb'))

    model = genome.create_model()

    model.summary()

    tf.keras.utils.plot_model(
        model,
        to_file=image_dst,
        show_shapes=True,
        show_layer_names=True,
        rankdir="TB",
        expand_nested=False,
        dpi=96,
    )


def train_genome_main(args: List[str]):
    gpu_fix()
    hp.set_dataset(Dataset.make_mnist_dataset())
    genome_path = args[2]
    
    genome: CnnGenome = pickle.load(open(genome_path, 'rb'))

    genome.train()


def evo_main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    logging.basicConfig(level=logging.DEBUG, format=f'[%(asctime)s][rank {rank}] %(message)s')
    
    pa = ProgramArguments()
    
    gpu_fix()

    if rank == 0:
        max_rank: int = comm.Get_size()

        cute: Cute = Cute(pa)
        master = Master(cute, comm, max_rank)
        master.run()
    else:
        worker = Worker(rank, comm)
        worker.run()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    if sys.argv[1] == "graph_genome":
        graph_genome_main(sys.argv)
    elif sys.argv[1] == "train_genome":
        train_genome_main(sys.argv)
    else:
        evo_main()
