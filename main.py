import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests


# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path='./data/vgg'):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """

    # Use tf.saved_model.loader.load to load the model and weights
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'
    graph = tf.get_default_graph()
    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)

    # Get relevant layers
    vgg_input = graph.get_tensor_by_name(vgg_input_tensor_name)
    keep = graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    layer3 = graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    layer4 = graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    layer7 = graph.get_tensor_by_name(vgg_layer7_out_tensor_name)

    return vgg_input, keep, layer3, layer4, layer7
tests.test_load_vgg(load_vgg, tf)


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer3_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer7_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    
    # Number of filters to use for each layer, improve final prediction
    n_filters = 8 * num_classes
    
    # Perform a up-convolation of layer 3
    layer_3_up = tf.layers.conv2d_transpose(vgg_layer3_out, n_filters, 8, 8, padding = "SAME",
                                            kernel_regularizer = tf.contrib.layers.l2_regularizer(1e-3))

    # Perform a up-convolation of layer 4
    layer_4_up = tf.layers.conv2d_transpose(vgg_layer4_out, n_filters, 16, 16, padding = "SAME",
                                            kernel_regularizer = tf.contrib.layers.l2_regularizer(1e-3))

    # Perform a up-convolation of layer 7
    layer_7_up = tf.layers.conv2d_transpose(vgg_layer7_out, n_filters, 32, 32, padding = "SAME",
                                            kernel_regularizer = tf.contrib.layers.l2_regularizer(1e-3))
    
    # Concatenate all layers (instead of just adding them per FC paper) to optimize weight of each contribution
    layer_out = tf.concat([layer_3_up, layer_4_up, layer_7_up], axis = -1)
    layer_out = tf.layers.batch_normalization(layer_out)  # to normalize contribution of each layer

    # Perform convolutions for smoother edges and less pixelisation
    for i in range(3):        
        layer_out = tf.layers.conv2d(layer_out, n_filters, 9, 1, padding = "SAME", activation = tf.nn.relu)

    # Predict classes for each pixel
    output = tf.layers.conv2d(layer_out, num_classes, 1, 1, name="Output_conv")

    return output
tests.test_layers(layers)


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """

    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    labels = tf.reshape(correct_label, (-1, num_classes))
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=labels))
    train_op = tf.train.AdamOptimizer(learning_rate).minimize(loss)

    return logits, train_op, loss
tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """

    # Initialize variables
    init = tf.global_variables_initializer()
    sess.run(init)

    # Loop over epochs
    for epoch in range(epochs):
        print("Epoch ", epoch + 1)

        # Loop over batches
        for batch in get_batches_fn(batch_size):
            _, loss_value = sess.run([train_op, cross_entropy_loss],
                                        feed_dict={input_image: batch[0], correct_label: batch[1], keep_prob: 0.5, learning_rate: 0.001})
            print("  loss: ", loss_value)

tests.test_train_nn(train_nn)


def run():
    num_classes = 2
    image_shape = (160, 576)
    epochs = 5
    batch_size = 4
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # Disable GPU due to graphic card limitations, if needed
    config = tf.ConfigProto(device_count = {'GPU': 0})

    with tf.Session(config=config) as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')

        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # Build NN using load_vgg, layers, and optimize function
        vgg_input, keep, layer3, layer4, layer7 = load_vgg(sess)
        output = layers(layer3, layer4, layer7, num_classes)
        correct_label = tf.placeholder(tf.float32)
        learning_rate = tf.placeholder(tf.float32)
        logits, train_op, loss = optimize(output, correct_label, learning_rate, num_classes)

        # Train NN using the train_nn function
        train_nn(sess, epochs, batch_size, get_batches_fn, train_op, loss, vgg_input, correct_label, keep, learning_rate)

        # Save inference data using helper.save_inference_samples
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep, vgg_input)

if __name__ == '__main__':
    run()
