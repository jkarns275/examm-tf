import logging
from typing import List, Tuple, Optional

import tensorflow.keras as keras
import tensorflow as tf

from cnn.conv_edge import ConvEdge


class Layer:

    
    NEXT_LAYER_INNOVATION_NUMBER: int = 0


    @staticmethod
    def get_next_layer_innovation_number():
        number = Layer.NEXT_LAYER_INNOVATION_NUMBER
        Layer.NEXT_LAYER_INNOVATION_NUMBER = number + 1
        return number


    def __init__(self, layer_innovation_number: int, width: int, height: int, depth: int):
        self.layer_innovation_number: int = layer_innovation_number
        
        self.width: int = width
        self.height: int = height
        self.depth: int = depth

        self.output_shape: Tuple[int, int, int] = (width, height, depth)

        self.inputs: List[ConvEdge] = []

        self.tf_layer: Optional[tf.Tensor] = None


    def __getstate__(self):
        # Prevent the tensorflow layer from being pickled
        state = self.__dict__.copy()
        del state['tf_layer']
        return state


    def __setstate__(self, state):
        # Not sure if this is necessary but just make  
        self.__dict__.update(state)
        self.tf_layer = None


    def get_tf_layer(self) -> keras.layers.Layer:
        if self.tf_layer is not None:
            return self.tf_layer

        input_layers: List[tf.Tensor] = list(map(lambda edge: edge.get_tf_layer(), self.inputs))
        self.validate_tf_inputs(input_layers)
        
        if len(input_layers) > 1:
            self.tf_layer = keras.layers.Average()(input_layers)
        else:
            self.tf_layer = input_layers[0]

        return self.tf_layer


    def add_input(self, input_layer: keras.layers.Layer):
        self.inputs.append(input_layer)
        self.validate_input_layer(input_layer)
        
        # Just make sure the computation graph hasn't been created yet.
        assert self.tf_layer is None
        

    def validate_input_layer(self, input_layer: keras.layers.Layer):
        shape = input_layer.output_shape
        assert shape == (self.width, self.height, self.depth)


    def validate_tf_inputs(self, tf_inputs: List[tf.Tensor]):
        for input in tf_inputs:
            assert input.shape[1:] == self.output_shape
