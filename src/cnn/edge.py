import logging
from typing import List, Tuple, Optional, Dict, Set

import tensorflow.keras as keras
import tensorflow as tf

if False:
    from cnn.layer import Layer
    from cnn import CnnGenome

class Edge:


    NEXT_EDGE_INNOVATION_NUMBER: int = 0


    @staticmethod
    def get_next_edge_innovation_number():
        number = Edge.NEXT_EDGE_INNOVATION_NUMBER
        Edge.NEXT_EDGE_INNOVATION_NUMBER = number + 1
        return number


    def __init__(self, edge_innovation_number: int, input_shape: Tuple[int, int, int], output_shape: Tuple[int, int, int],
                       input_layer_in: int, output_layer_in: int, layer_map: Dict[int, 'Layer'], enabled: bool=True):
        self.edge_innovation_number: int = edge_innovation_number
        self.input_layer_in: int = input_layer_in
        self.output_layer_in: int = output_layer_in
       
        self.input_shape: Tuple[int, int, int] = input_shape
        self.output_shape: Tuple[int, int, int] = output_shape
        
        self.tf_layer: Optional[tf.Tensor] = None
        self.tf_weight_names: Set[str] = set()

        self.enabled: bool = enabled

        layer_map[output_layer_in].add_input_edge(self)
        layer_map[input_layer_in].add_output_edge(self)

    
    def copy(self, layer_map: Dict[int, 'Layer']) -> 'Edge':
        raise NotImplementedError("call to abstract method Edge::copy")


    def __getstate__(self):
        # Prevent the tensorflow layer from being pickled
        state = self.__dict__.copy()
        del state['tf_layer']
        return state


    def __setstate__(self, state):
        # Not sure if this is necessary but just make 
        state.update({'enabled': True})
        self.__dict__.update(state)
        self.tf_layer = None
    

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
    
    
    def is_enabled(self) -> bool:
        return self.enabled


    def enable(self):
        self.enabled = True


    def is_disabled(self):
        return not self.enabled


    def disable(self):
        self.enabled = False


    def get_tf_layer(self, genome: 'CnnGenome') -> keras.layers.Layer:
        raise NotImplementedError("Call to abstract method Edge::get_tf_layer")
