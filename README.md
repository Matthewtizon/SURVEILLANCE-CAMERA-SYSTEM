Some text here 


Step 1: Manually Add Initialization to .bashrc
Since conda init didn't make any changes, let's manually add the required lines to your .bashrc file.

Open your .bashrc file:

nano ~/.bashrc

Add the following lines to the end of the file:

# Initialize Conda
. /home/johnmatthew/miniconda3/etc/profile.d/conda.sh

Save and exit (in nano, press CTRL + X, then Y, then Enter).

Step 2: Reload the Shell Configuration
After making these changes, apply them by running:


source ~/.bashrc
Step 3: Verify Conda Initialization
Now, check if conda is initialized by trying to activate your environment:


conda activate capstone














Steps 

Go to anaconda prompt

1. conda create -n <name> python=3.10
2. conda activate <name>
3. conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0
4. python -m pip install "tensorflow==2.10"
5. conda install numpy==1.26.4
6. python
7. ** Test GPU **

    import tensorflow as tf
    tf.config.list_physical_devices('GPU')

    tf.test.is_gpu_available()


    you will see like this 
        (new) C:\Users\John Matthew>python
        Python 3.10.14 | packaged by Anaconda, Inc. | (main, May  6 2024, 19:44:50) [MSC v.1916 64 bit (AMD64)] on win32
        Type "help", "copyright", "credits" or "license" for more information.
        >>> import tensorflow as tf
        >>> tf.config.list_physical_devices('GPU')
        [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
        >>>
        >>> tf.test.is_gpu_available()
        WARNING:tensorflow:From <stdin>:1: is_gpu_available (from tensorflow.python.framework.test_util) is deprecated and will be removed in a future version.
        Instructions for updating:
        Use `tf.config.list_physical_devices('GPU')` instead.
        2024-09-29 10:18:30.988609: I tensorflow/core/platform/cpu_feature_guard.cc:193] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  AVX AVX2
        To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
        2024-09-29 10:18:32.103480: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1616] Created device /device:GPU:0 with 5449 MB memory:  -> device: 0, name: NVIDIA GeForce RTX 4060 Laptop GPU, pci bus id: 0000:01:00.0, compute capability: 8.9
        True

8. exit()
9. conda install opencv-python==4.7.0.72
10. open your visual studio code and direct to your project directory
11. open new cmd terminal
12. type "pip install -r requirements.txt" in the terminal
13. check numpy version if not 1.26.4 uninstall it and install numpy==1.26.4