# CarND: Semantic Segmentation

The present repository is my solution to the [Udacity Semantic Segmentation Project](https://github.com/udacity/CarND-Semantic-Segmentation).

The objective of the project was to recognize pixels belonging to the road by using a previously labeled dataset.

The main inspiration was to use an architecture similar to Fully Convolution Network. My solution is also using ideas from the U-Net architecture:
* additional features are used before trying to predict the correct classes
* features are stacked from different layers
* additional convolutions are performed after the up-convolutions to integrate the features and obtain smoother edges
* a 1x1 convolution is performed on the final features in order to let the network learn the correct contributions of each layer to predict the correct class of each pixel

Some tools such as batch normalization, dropout and L2 regulizers had to be used and hyperparameters had to be refined in order to get a correct predictions.

![alt text](runs\1509724493.1589382\um_000019.png "Project example")

---

## Original README

Here below is a reproduction of the original project README.

### Introduction
In this project, you'll label the pixels of a road in images using a Fully Convolutional Network (FCN).

### Setup
##### Frameworks and Packages
Make sure you have the following is installed:
 - [Python 3](https://www.python.org/)
 - [TensorFlow](https://www.tensorflow.org/)
 - [NumPy](http://www.numpy.org/)
 - [SciPy](https://www.scipy.org/)
##### Dataset
Download the [Kitti Road dataset](http://www.cvlibs.net/datasets/kitti/eval_road.php) from [here](http://www.cvlibs.net/download.php?file=data_road.zip).  Extract the dataset in the `data` folder.  This will create the folder `data_road` with all the training a test images.

### Start
##### Implement
Implement the code in the `main.py` module indicated by the "TODO" comments.
The comments indicated with "OPTIONAL" tag are not required to complete.
##### Run
Run the following command to run the project:
```
python main.py
```
**Note** If running this in Jupyter Notebook system messages, such as those regarding test status, may appear in the terminal rather than the notebook.

### Submission
1. Ensure you've passed all the unit tests.
2. Ensure you pass all points on [the rubric](https://review.udacity.com/#!/rubrics/989/view).
3. Submit the following in a zip file.
 - `helper.py`
 - `main.py`
 - `project_tests.py`
 - Newest inference images from `runs` folder  (**all images from the most recent run**)
 
 ## How to write a README
A well written README file can enhance your project and portfolio.  Develop your abilities to create professional README files by completing [this free course](https://www.udacity.com/course/writing-readmes--ud777).
