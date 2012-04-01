#!/usr/bin/env python
import gzip
import cPickle
import random

import numpy as np
import scipy.io

import display_network

def randrange(r):
    """Accepts an integer
        Returns a random integer from 0..r-1
    """
    return random.randint(0, r-1)


def random_sample(images, size=(8,8)):
    """Accepts an array of images.
        images.ndim = (xdim, ydim, num_images)
        Also accepts the size of the sample, a 2-tuple.
       Returns a flattened array of a random patch of a random image.
            Will be a (size[0]*size[1]) x 1 size array.
    """
    num_images = images.shape[2]
    image = images[:,:,randrange(num_images)]
    
    x,y = size
    mx, my = tuple(np.array(image.shape) - np.array(size))
    rx, ry = randrange(mx), randrange(my)
    patch = image[rx:rx+x,ry:ry+y]
    return patch.flatten()

def load_matlab_images(matlab_filename):
    """Accepts a string.
        String points to file which is a matlab matrix .mat file.
        Loads the file and extracts the images in the first key that
            begins with "IMAGES".
    """
    d = scipy.io.loadmat(matlab_filename)
    key = [k for k in d.keys() if k.startswith('IMAGES')][0]
    images = d[key]
    return images


def normalize_data(patches, norm):
    """Accepts columns of data, norm 2-tuple.
       Zero-centers the patches.

       Squash data to [norm[0], norm[1]] since we use 
           sigmoid as the activation function in the output layer
    """
    assert norm[1] > norm[0]
    # Remove DC (mean of images). 
    patches = patches - np.mean(patches)
    assert np.allclose(np.mean(patches), 0)

    # Truncate to +/-3 standard deviations and scale to -1 to 1
    pstd = 3 * np.std(patches)
    patches = np.maximum(np.minimum(patches, pstd), -pstd) / pstd;
    assert np.all(-1 <= patches) and np.all(patches <= 1)

    # Rescale from [-1,1] to [0.1,0.9]
    patches = ((patches + 1) * ((norm[1] - norm[0])/2.0)) + norm[0];

    assert np.all(norm[0] <= patches) and np.all(patches <= norm[1])
    return patches

def sample(images, num_samples, size=(8,8), norm=(0.1, 0.9)):
    """Accepts an array of images.
        images.ndim = (xdim, ydim, num_images)
        Also accepts the size of the sample, a 2-tuple, (xdim, ydim).
       Returns an array of flattened images.
            Will be a (size[0]*size[1]) x num_samples size array.
    """
    d = np.array([random_sample(images, size) for i in xrange(num_samples)]).T
    if norm is not None:
        output = normalize_data(d, norm)
    else:
        output = d
    return output

def load_mnist_images(filename):
    """Accepts filename.
        Reads in MNIST data.
        Returns 3-tuple of training, validation, and test set.
    """
    with gzip.open(filename, 'rb') as f:
        train_set, valid_set, test_set = cPickle.load(f)
    return train_set, valid_set, test_set
    
if __name__=='__main__':
    '''
    num_samples = 10000
    images = load_matlab_images('IMAGES.mat')
    samples = sample(images, num_samples, (8,8))

    subset = samples[:, :200]
    try: 
        display_nework.display_network('samples.png', subset)
    except Exception, e:
        print e
        import pdb; pdb.post_mortem()
    '''
    train, valid, test = load_mnist_images('data/mnist.pkl.gz')
    display_network.display_network('mnist.png', train[0].T[:,:100])
