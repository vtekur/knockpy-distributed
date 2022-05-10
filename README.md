# Knockpy

A python implementation of the knockoffs framework for variable selection. See https://amspector100.github.io/knockpy/ for detailed documentation and tutorials.

## Installation

To install knockpy, first install choldate using the following command:

``pip install git+git://github.com/jcrudy/choldate.git``

Then, install knockpy using pip:

``pip install knockpy[fast]``

To use the (optional) kpytorch submodule, you will need to install [pytorch](https://pytorch.org/). 

### What if installation fails?

knockpy relies on heavy-duty linear algebra routines which sometimes fail on non-Linux environments. 

1. To start, install a lightweight version of knockpy using
``pip install knockpy``. This should install correctly on all devices, and contains nearly all of the functionality of the prior installation. However, the algorithms for computing optimal distributions for Gaussian knockoffs, such as [minimum reconstructability knockoffs](https://arxiv.org/abs/2011.14625) and [SDP knockoffs](https://arxiv.org/abs/1610.02351), may be an order of magnitude slower.
2. [Optional] To speed up computation for minimum reconstructability knockoffs (the default knockoff type):

    (a) Run

        ``pip install cython>=0.29.14``  

    If the installation fails, likely due to the incorrect configuration of a C compiler, you have three options. First, the [Anaconda](https://docs.anaconda.com/anaconda/user-guide/tasks/install-packages/) package manager includes a compiler, so the command

        ``conda install cython``  

    should work on all platforms. Second, on Windows, you can install precompiled binaries for cython [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/). Lastly, on all platforms, the documentation [here](https://cython.readthedocs.io/en/latest/src/quickstart/install.html) describes how to properly configure a C compiler during installation.
    
    (b) Run

        ``pip install git+git://github.com/jcrudy/choldate.git``

3. [Optional] To speed up computation for (non-default) SDP knockoffs, you will need to install ``scikit-dsdp``. This can be challenging on non-Linux environments. We hope to provide more explicit instructions for installation of this package in the future.
 
## Quickstart

Given a data-matrix `X` and a response vector `y`, knockpy makes it easy to use knockoffs to perform variable selection using a wide variety of machine learning algorithms (also known as "feature statistic") and types of knockoffs. One quick example is shown below, where we use the cross-validated lasso to assign variable importances to the features and knockoffs.  

```
    import knockpy as kpy
    from knockpy.knockoff_filter import KnockoffFilter

    # Generate synthetic data from a Gaussian linear model
    data_gen_process = kpy.dgp.DGP()
    data_gen_process.sample_data(
        n=1500, # Number of datapoints
        p=500, # Dimensionality
        sparsity=0.1,
        x_dist='gaussian',
    )
    X = data_gen_process.X
    y = data_gen_process.y
    Sigma=data_gen_process.Sigma

    # Run model-X knockoffs
    kfilter = KnockoffFilter(
        fstat='lasso',
        ksampler='gaussian',
    )
    rejections = kfilter.forward(X=X, y=y, Sigma=Sigma)
```

Most importantly, ``knockpy`` is built to be modular, so researchers and analysts can easily layer functionality on top of it.

## Reference

If you use knockpy in an academic publication, please consider citing [Spector and Janson (2020)](https://arxiv.org/abs/2011.14625). The bibtex entry is below:

```
@article{AS-LJ:2020,
  title={Powerful Knockoffs via Minimizing Reconstructability},
  author={Spector, Asher and Janson, Lucas},
  journal={Annals of Statistics},
  year={2021+},
  note={To Appear}
}
```
