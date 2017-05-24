# Objects to wrap tensor flow nodes for conversion to matconvnet,
# based on the mcn-caffe importer
# # author: Samuel Albanie 

from collections import OrderedDict
from math import floor, ceil
from operator import mul
import numpy as np
from numpy import array
import pdb
import scipy
import scipy.io
import scipy.misc
import ipdb
import copy
import collections

# --------------------------------------------------------------------
#                                                       Basic TF Nodes
# --------------------------------------------------------------------

class TFNode(object):
    def __init__(self, name, input_names, input_types):
        self.name = name
        self.input_names = input_names
        self.input_types = input_types
        self.inputs = [] # used to store node references

    def summary_str(self, obj_type):
        summary = """TF {} object:
        + name : {} 
        + input_names : {}
        + input_types : {}"""
        return summary.format(obj_type, self.name, self.input_names, self.input_types)
        

class TFPlaceHolder(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('PlaceHolder')

class TFPad(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('Pad')

class TFSub(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('Sub')

class TFRealDiv(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('RealDiv')

class TFMul(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('Mul')

class TFMaximum(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('Maximum')

class TFIdentity(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('Identity')

class TFNoOp(TFNode):
    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return super().summary_str('NoOp')

class TFConst(TFNode):
    def __init__(self, name, input_names, input_types, shape, value):
        super().__init__(name, input_names, input_types)
        self.shape = shape
        self.value = value

    def __repr__(self):
        common = super().summary_str('Const')
        summary = """{}
        + shape : {}"""
        return summary.format(common, self.shape)

class TFConcatV2(TFNode):
    def __init__(self, name, input_names, input_types, axis):
        super().__init__(name, input_names, input_types)
        self.axis = axis

    def __repr__(self):
        common = super().summary_str('ConcatV2')
        summary = """{}
        + axis : {}"""
        return summary.format(common, self.axis)

class TFBiasAdd(TFNode):
    def __init__(self, name, input_names, input_types, data_format):
        super().__init__(name, input_names, input_types)
        self.data_format = data_format 

    def __repr__(self):
        common = super().summary_str('BiasAdd')
        summary = """{}
        + data_format : {}"""
        return summary.format(common, self.data_format)

class TFMaxPool(TFNode):
    def __init__(self, name, input_names, stride, pad_type, ksize, input_types, 
                                                                  data_format):
        super().__init__(name, input_names, input_types)
        self.stride = stride
        self.ksize = ksize
        self.pad_type = pad_type
        self.data_format = data_format

    def __repr__(self):
        common = super().summary_str('MaxPool')
        summary = """{}
        + stride : {}
        + ksize : {}
        + pad_type : {}
        + data_format : {}"""
        return summary.format(common, self.stride, self.ksize, self.pad_type, 
                                                             self.data_format)

class TFConv2D(TFNode):
    def __init__(self, name, input_names, stride, pad_type, input_types, 
                                                                 data_format):
        super().__init__(name, input_names, input_types)
        self.stride = stride
        self.pad_type = pad_type
        self.data_format = data_format

    def __repr__(self):
        common = super().summary_str('Conv2D')
        summary = """{}
        + stride : {}
        + pad_type : {}
        + data_format : {}"""
        return summary.format(common, self.stride, self.pad_type, 
                                                             self.data_format)

class TFExtractImagePatches(TFNode):
    def __init__(self, name, input_names, rate, stride, pad_type, ksize, 
                                                                  input_types):
        super().__init__(name, input_names, input_types)
        self.rate = rate
        self.stride = stride
        self.ksize = ksize
        self.pad_type = pad_type

    def __repr__(self):
        common = super().summary_str('Const')
        summary = """{}
        + rate : {}
        + stride : {}
        + ksize : {}
        + pad_type : {}"""
        return summary.format(common, self.rate, self.stride, self.ksize, 
                                                            self.pad_type)

# --------------------------------------------------------------------
#                                                             TF Graph
# --------------------------------------------------------------------

class TFGraph(object):
    def __init__(self, node_list):
        self.nodes = node_list

    def print(self):
        for node in self.nodes:
            print(self.node)

    def __repr__(self):
        return 'TensorFlow graph object with {} nodes'.format(len(self.nodes))

# --------------------------------------------------------------------
#                                                   Matconvnet objects
# --------------------------------------------------------------------
class McnNode(object):

    def __init__(self, name, value, op, input_nodes=None):
        self.name = name 
        self.value = value
        self.op = op
        self.input_nodes = input_nodes

class McnLayer(object):
    def __init__(self, name, inputs, outputs):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.params = []
        self.model = None

    def reshape(self, model):
        pass

    def transpose(self, model):
        raise NotImplementedError

    def setBlob(self, model, i, blob):
        raise NotImplementedError

    def display(self):
        print('Layer \'{}\''.format(self.name))
        print('  +- type: {}'.format(self.__class__.__name__))
        print('  +- inputs: {}'.format(self.inputs,))
        print('  +- outputs: %s'.format(self.outputs,))
        print('  +- params: %s'.format(self.params,))

    def toMatlab(self):
        mlayer = np.empty(shape=[1,],dtype=mlayerdt)
        mlayer['name'][0] = self.name
        mlayer['type'][0] = None
        mlayer['inputs'][0] = rowcell(self.inputs)
        mlayer['outputs'][0] = rowcell(self.outputs)
        mlayer['params'][0] = rowcell(self.params)
        mlayer['block'][0] = dictToMatlabStruct({})
        return mlayer

class McnConv(McnLayer):
    def __init__(self, name, tf_node, input_nodes, dilation=[1,1]):

        # parse the expression formed by input nodes
        assert len(input_nodes) == 2, 'conv layer expects two nodes as inputs'

        # parse input nodes
        for node in input_nodes:
            if node.op == 'pad':
                padding_node = node
            elif node.op == 'const':
                filter_node = node
            else:
                raise ValueError('unexpected input op {}'.format(node.op))

        # define input and output variable names
        inputs = padding_node.name
        outputs = name

        super().__init__(name, inputs, outputs)

        # determine filter dimensions
        self.kernel_size = filter_node.value.shape[:2]
        self.num_out = filter_node.value.shape[3]

        # a bias is often not used in conjuction with batch norm
        self.bias_term = 0 

        # reformat padding to match mcn
        tf_pad = padding_node.value
        param_format = tf_node.data_format
        pad_top_bottom = tf_pad[param_format[0],:]
        pad_left_right = tf_pad[param_format[1],:]
        self.pad = np.hstack((pad_top_bottom, pad_left_right))

        # reformat stride to match mcn
        stride_x = tf_node.stride[param_format[0]]
        stride_y = tf_node.stride[param_format[1]]
        self.stride = np.hstack((stride_x, stride_y))
        self.op = 'conv'
        self.input_nodes = input_nodes

        # check options are correctly formatted
        assert len(self.pad) == 4, ('padding format does hvae the '
         'required number of elements for `[top bottom left right]`')
        assert len(self.stride) == 2, ('stride format does hvae the '
         'expected number of elements for `[strideY strideX]`')
        assert len(self.kernel_size) == 2, ('kernel size should contain '
          'exactly two elements')

        # set dilation 
        # TODO(sam) - handle dilated convs properly
        self.dilation = dilation

        # set param names and store weights on the layer - note that
        # params are not set on the shared model until all the layers
        # have been constructed
        self.params = [name + '_filter']
        if self.bias_term: self.params.append(name + '_bias')
        self.filters = filter_node.value
        self.filter_depth = filter_node.value.shape[3]

    def display(self):
        super().display()
        print("  +- filter dimension:", self.filter_depth)
        print("  c- num_output (num filters): %s" % self.num_output)
        print("  c- bias_term: %s" % self.bias_term)
        print("  c- pad: %s" % (self.pad,))
        print("  c- kernel_size: %s" % self.kernel_size)
        print("  c- stride: %s" % (self.stride,))
        print("  c- dilation: %s" % (self.dilation,))
        print("  c- group: %s" % (self.group,))

    def setParams(self, filters, data_format):
        # TODO(sam): implement
        ipdb.set_trace()
        model.params[self.params[i]].value = blob
        model.params[self.params[i]].shape = blob.shape

class McnReLU(McnLayer):
    def __init__(self, name, tf_node, input_nodes):
        assert len(input_nodes) == 2, 'relu layer expects two nodes as inputs'

        # parse inputs
        for node in input_nodes:
            if node.op == 'mul':
                mul_node = node
            else:
                raw_node = node

        for node in mul_node.input_nodes:
            if node.op == 'const':
                leak_node = node
            else:
                other_node = node

        inputs = raw_node.outputs
        outputs = name

        super().__init__(name, inputs, outputs)

        # check for leak
        self.leak = leak_node.value
        self.op = 'relu'

    @staticmethod
    def is_leaky_relu_expression(tf_node, input_nodes):
        """ 
        pattern match to check for leaky relu
        """
        # parse previous layer of inputs
        for node in input_nodes:
            if node.op == 'mul':
                mul_node = node
            else:
                raw_node = node

        # check that at least one node was a multiplier
        if 'mul_node' not in locals(): 
            return False

        #TODO(sam): add in more robust checks
        is_leaky_relu = id(raw_node) in [id(node) for node in mul_node.input_nodes]
        return is_leaky_relu

    def toMatlab(self):
        mlayer = super().toMatlab()
        mlayer['type'][0] = u'dagnn.ReLU'
        mlayer['block'][0] = dictToMatlabStruct({'leak': self.leak })
        return mlayer

class McnConcat(McnLayer):
    def __init__(self, name, tf_node, input_nodes):
        assert len(input_nodes) == 3, 'concat layer expects three nodes as inputs'

        inputs = [node.outputs for node in input_nodes[:2]]
        outputs = name
 
        super().__init__(name, inputs, outputs)

        self.axis = tf_node.axis
        self.op = 'concat'

    def toMatlab(self):
        mlayer = super().toMatlab()
        mlayer['type'][0] = u'dagnn.Concat'
        mlayer['block'][0] = dictToMatlabStruct({'dim': float(self.axis) + 1})
        return mlayer

class McnExtractImagePatches(McnLayer):
    def __init__(self, name, tf_node, input_nodes):
        assert len(input_nodes) == 1, 'extract image patches layer expects one node as input'

        # parse inputs
        src_node = input_nodes[0]
        param_format = [1,2,3,0] # this is currently the form of the TF layer, but may change

        inputs = src_node.outputs
        outputs = name

        super().__init__(name, inputs, outputs)

        # reformat kernel size to match mcn
        tf_stride = tf_node.stride
        stride_y = tf_stride[param_format[0]]
        stride_x = tf_stride[param_format[1]]
        self.stride = np.hstack((stride_y, stride_x))

        # reformat kernel size to match mcn
        tf_rate = tf_node.rate
        rate_y = tf_rate[param_format[0]]
        rate_x = tf_rate[param_format[1]]
        self.rate = np.hstack((rate_y, rate_x))

        #TODO(sam) fix properly on the first pass
        self.pad = [1, 1, 1, 1]
        self.pad_type = tf_node.pad_type

    def toMatlab(self):
        mlayer = super().toMatlab()
        mlayer['type'][0] = u'dagnn.ExtractImagePatches'
        mlayer['block'][0] = dictToMatlabStruct(
            {'stride': row(self.stride),
             'rate': row(self.rate),
             'pad': row(self.pad)})
        if not self.pad_corrected:
            print(('Warning: pad correction for layer {} could not be ',
                 ('computed because the layer input shape could not be ', 
                  'determined').format(self.name)))
        return mlayer

class McnBatchNorm(McnLayer):

    def __init__(self, name, tf_node, input_nodes, eps=1e-5):
        # parse the expression formed by input nodes
        assert len(input_nodes) == 2, 'batch norm layer expects two nodes as inputs'

        # parse inputs
        for node in input_nodes:
            if node.op == 'const':
                bias_node = node
            elif node.op == 'mul':
                mul_node = node

        # parse inputs
        for node in mul_node.input_nodes:
            if node.op == 'const':
                gain_node = node
            elif node.op == 'div':
                div_node = node

        # parse inputs
        for node in div_node.input_nodes:
            if node.op == 'const':
                var_node = node
            elif node.op == 'sub':
                sub_node = node

        # parse inputs
        for node in sub_node.input_nodes:
            if node.op == 'const':
                mean_node = node
            elif node.op == 'conv':
                conv_node = node

        # parse inputs
        self.bias_term = bias_node.value
        self.scale_factor = gain_node.value
        self.variance = var_node.value
        self.mean = mean_node.value

        # define input and output variable names
        inputs = conv_node.outputs
        outputs = name

        super().__init__(name, inputs, outputs)

        self.eps = eps
        self.op = 'batch_norm'
        self.params = [name + u'_mean',
                       name + u'_variance',
                       name + u'_scale_factor']

    @staticmethod
    def is_batch_norm_expression(tf_node, input_nodes):
        """ 
        in order to extract batch normalization layers from a tensor flow
        computational graph, we need to be able to match against the set
        of operations which constitute batch norm.  This method performs
        that pattern matching
        """

        # parse inputs
        for node in input_nodes:
            if node.op == 'const':
                bias_node = node
            elif node.op == 'mul':
                mul_node = node
            else:
                return False # unexpected format from batch norm
              
        # check for required sequence of ops
        expected_div_ops = {'const', 'div'}
        div_ops = set([node.op for node in mul_node.input_nodes])

        # parse previous layer of inputs
        for node in mul_node.input_nodes:
            if node.op == 'const':
                var_node = node
            elif node.op == 'div':
                div_node = node
            else:
                return False # unexpected format from batch norm

        expected_sub_ops = {'const', 'sub'}
        sub_ops = set([node.op for node in div_node.input_nodes])
        is_bn = (sub_ops == expected_sub_ops) and (div_ops == expected_div_ops)

        #TODO(sam): add in more robust checks
        return is_bn

    def setBlob(self, model, i, blob):
        assert(i < 3)
        model.params[self.params[i]].value = blob
        model.params[self.params[i]].shape = blob.shape

    def reshape(self, model):
        shape = model.vars[self.inputs[0]].shape
        mean = model.params[self.params[0]].value
        variance = model.params[self.params[1]].value
        scale_factor = model.params[self.params[2]].value
        for i in range(3): del model.params[self.params[i]]
        self.params = [self.name + u'_mult',
                       self.name + u'_bias',
                       self.name + u'_moments']

        model.addParam(self.params[0])
        model.addParam(self.params[1])
        model.addParam(self.params[2])

        if shape:
            mult = np.ones((shape[2],),dtype='float32')
            bias = np.zeros((shape[2],),dtype='float32')
            model.params[self.params[0]].value = mult
            model.params[self.params[0]].shape = mult.shape
            model.params[self.params[1]].value = bias
            model.params[self.params[1]].shape = bias.shape

        if mean.size:
            moments = np.concatenate(
                (mean.reshape(-1,1) / scale_factor,
                 np.sqrt(variance.reshape(-1,1) / scale_factor + self.eps)),
                axis=1)
            model.params[self.params[2]].value = moments
            model.params[self.params[2]].shape = moments.shape

        model.vars[self.outputs[0]].shape = shape

    def toMatlab(self):
        mlayer = super().toMatlab()
        mlayer['type'][0] = u'dagnn.BatchNorm'
        mlayer['block'][0] = dictToMatlabStruct(
            {'epsilon': self.eps})
        return mlayer

class McnPooling(McnLayer):

    def __init__(self, name, tf_node, input_nodes, method):

        assert len(input_nodes) == 1, 'pooling layer takes a single input node'

        # parse inputs
        pool_node = input_nodes[0]

        # reformat kernel size to match mcn
        tf_kernel_size = tf_node.ksize
        param_format = tf_node.data_format
        kernel_size_y = tf_kernel_size[param_format[0]]
        kernel_size_x = tf_kernel_size[param_format[1]]
        self.kernel_size = np.hstack((kernel_size_y, kernel_size_x))

        # reformat kernel size to match mcn
        tf_stride = tf_node.stride
        param_format = tf_node.data_format
        stride_y = tf_stride[param_format[0]]
        stride_x = tf_stride[param_format[1]]
        self.stride = np.hstack((stride_y, stride_x))

        #TODO(sam) fix properly on the first pass
        self.pad = [1, 1, 1, 1]

        # define input and output variable names
        inputs = pool_node.outputs
        outputs = name

        super().__init__(name, inputs, outputs)

        self.method = method
        self.op = 'pool'

    def display(self):
        super(CaffePooling, self).display()
        print("  c- method: ".format(self.method))
        print("  c- pad: {}".format(self.pad))
        print("  c- kernel_size: {}".format(self.kernel_size))
        print("  c- stride: {}".format(self.stride))

    def reshape(self, model):
        shape = model.vars[self.inputs[0]].shape
        if not shape: return
        # MatConvNet uses a slighly different definition of padding, which we think
        # is the correct one (it corresponds to the filters)
        self.pad_corrected = copy.deepcopy(self.pad)
        for i in [0, 1]:
            self.pad_corrected[1 + i*2] = min(
                self.pad[1 + i*2] + self.stride[i] - 1,
                self.kernel_size[i] - 1)
        model.vars[self.outputs[0]].shape = \
            getFilterOutputSize(shape[0:2],
                                self.kernel_size,
                                self.stride,
                                self.pad_corrected) + shape[2:5]

    def getTransforms(self, model):
        return [[getFilterTransform(self.kernel_size, self.stride, self.pad)]]

    def transpose(self, model):
        self.kernel_size = reorder(self.kernel_size, [1,0])
        self.stride = reorder(self.stride, [1,0])
        self.pad = reorder(self.pad, [2,3,0,1])
        if self.pad_corrected:
            self.pad_corrected = reorder(self.pad_corrected, [2,3,0,1])

    def toMatlab(self):
        mlayer = super(CaffePooling, self).toMatlab()
        mlayer['type'][0] = u'dagnn.Pooling'
        mlayer['block'][0] = dictToMatlabStruct(
            {'method': self.method,
             'poolSize': row(self.kernel_size),
             'stride': row(self.stride),
             'pad': row(self.pad_corrected)})
        if not self.pad_corrected:
            print(('Warning: pad correction for layer {} could not be ',
                 ('computed because the layer input shape could not be ', 
                  'determined').format(self.name)))
        return mlayer
