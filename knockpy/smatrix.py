import numpy as np
import scipy.cluster.hierarchy as hierarchy
from . import mrc
from . import mac
from . import dgp
from . import utilities
from . import constants


def parse_method(method, groups, p):
    """ Decides which method to use to create the knockoff S matrix """
    if method is not None:
        return method
    if np.all(groups == np.arange(1, p + 1, 1)):
        method = "mvr"
    else:
        method = "sdp"
    return method


def divide_computation(Sigma, max_block):
    """
    Approximates Sigma as a block-diagonal matrix.
    
    Parameters
    ----------
    Sigma : np.ndarray
        ``(p, p)``-shaped covariance matrix of X
    max_size : int
        Maximum size of a block in the block-diagonal approximation.

    Returns
    -------
    blocks : np.ndarray
        ``(p, )``-shaped numpy array where ``blocks[i] == j`` indicates
        that variable ``i`` belongs to block ``j``. 
    """


def divide_computation(Sigma, max_block):
    """
    Approximates a correlation matrix Sigma as a block-diagonal matrix
    using hierarchical clustering. Roughly follows the R knockoff package.
    """

    # Correlation tree. We add noise to deal with highly structured Sigma.
    p = Sigma.shape[0]
    noise = np.random.randn(p, p) * 1e-6
    noise += noise.T
    Sigma = Sigma + noise
    link = dgp.create_correlation_tree(Sigma)

    # Set up binary search
    max_clusters = p
    min_clusters = 1
    prev_max_clusters = p
    prev_min_clusters = 1

    # Binary search to create clusters
    for j in range(100):
        # Create new groups and check maximum size
        n_clusters = int((max_clusters + min_clusters) / 2)
        groups = hierarchy.cut_tree(link, n_clusters).reshape(-1) + 1
        current_max_block = utilities.calc_group_sizes(groups).max()

        # Cache search info and check maximum size
        prev_max_clusters = max_clusters
        prev_min_clusters = min_clusters
        if current_max_block > max_block:
            min_clusters = n_clusters
        else:
            max_clusters = n_clusters
        # Break if nothing has changed between iterations
        if min_clusters == prev_min_clusters and max_clusters == prev_max_clusters:
            if current_max_block > max_block:
                groups = hierarchy.cut_tree(link, n_clusters + 1).reshape(-1) + 1
            break

    return merge_groups(groups, max_block)


def merge_groups(groups, max_block):
    """
    Merges groups of variables together while ensuring all new groups
    have size less than max_block.
    """
    p = groups.shape[0]
    new_groups = np.zeros(p)
    # Loop through groups and concatenate them together
    # until we exceed max size
    current_size = 0
    new_group_id = 1
    old_group_ids = np.unique(groups)
    np.random.shuffle(old_group_ids)
    # Iterate through old groups
    for old_group_id in old_group_ids:
        flag = groups == old_group_id
        old_group_size = flag.sum()
        # Either count old group as part of new group
        if current_size + old_group_size <= max_block:
            current_size += old_group_size
        # Or add a new group
        elif old_group_size <= max_block:
            current_size = old_group_size
            new_group_id += 1
        else:
            raise ValueError(
                f"Group {old_group_id} has size {old_group_size}, exceeding max_block {max_block}"
            )
        new_groups[flag] = new_group_id

    return new_groups


def compute_smatrix(
    Sigma,
    groups=None,
    method=None,
    solver="cd",
    max_block=1000,
    num_processes=1,
    **kwargs,
):
    """
    Wraps a variety of S-matrix generation functions.
    For mvr, maxent, mmi, and sdp methods, this uses a block-diagonal
    approximation of Sigma if the dimension of Sigma exceeds
    max_block.

    Parameters
    ----------
    Sigma : np.ndarray
    ``(p, p)``-shaped covariance matrix of X
    groups : np.ndarray
        For group knockoffs, a p-length array of integers from 1 to 
        num_groups such that ``groups[j] == i`` indicates that variable `j`
        is a member of group `i`. Defaults to ``None`` (regular knockoffs). 
    method : str
        Method for constructing S-matrix. One of mvr, maxent, mmi, sdp, equicorrelated, ci.
    solver : str
        Method for solving mrc knockoffs. One of 'cd' (coordinate descent) 
        or 'psgd' (projected gradient descent). Coordinate descent is 
        highly recommended.
    max_block : int
        The maximum size of a block in a block-diagonal approximation of Sigma.
    num_processes : int
        Number of parallel process to use if Sigma is approximated as
        a block-diagonal matrix. 
    kwargs : dict
        kwargs to pass to one of the wrapped S-matrix solvers.

    Notes
    -----
    mmi stands for minimum mutual information, which is the same as maximizing
    entropy.

    Returns
    -------
    S : np.ndarray
        ``(p, p)``-shaped (block) diagonal matrix used to generate knockoffs
    """
    # If S in kwargs, just return S (important
    # for chaining methods in metro sampling)
    kwargs = kwargs.copy()
    if "S" in kwargs:
        if kwargs["S"] is not None:
            return kwargs["S"]
        else:
            kwargs.pop("S")

    # Initial params
    p = Sigma.shape[0]
    if method is not None:
        method = str(method).lower()
    method = parse_method(method, groups, p)
    # These two are the same
    if method == 'mmi':
        method = 'maxent'
    if groups is None:
        groups = np.arange(1, p + 1, 1)

    # Scale to correlation matrix
    scale = np.sqrt(np.diag(Sigma))
    scale_matrix = np.outer(scale, scale)
    Sigma = Sigma / scale_matrix

    # Possibly use block-diagonal approximation, either using
    # hierarchical clustering for non-grouped knockoffs or
    # randomly merging groups for group knockoffs.
    if p > max_block and method not in ["equicorrelated", "eq", "ci", "ciknock"]:
        if np.all(groups == np.arange(1, p + 1, 1)):
            blocks = divide_computation(Sigma, max_block)
        else:
            blocks = merge_groups(groups, max_block)
        block_sizes = utilities.calc_group_sizes(blocks)
        nblocks = block_sizes.shape[0]
        print(
            f"Using blockdiag approx. with nblocks={nblocks} and max_size={block_sizes.max()}..."
        )
        Sigma_blocks = utilities.blockdiag_to_blocks(Sigma, blocks)
        group_blocks = []
        for j in range(int(blocks.min()), int(blocks.max()) + 1):
            group_blocks.append(utilities.preprocess_groups(groups[blocks == j]))
        # Recursive subcall for each block. Possibly use multiprocessing.
        constant_inputs = {
            "method": method,
            "solver": solver,
            "max_block": p,
        }
        for key in kwargs:
            constant_inputs[key] = kwargs[key]
        S_blocks = utilities.apply_pool(
            func=compute_smatrix,
            constant_inputs=constant_inputs,
            Sigma=Sigma_blocks,
            groups=group_blocks,
            num_processes=num_processes,
        )
        print("Finished comp of blocks, putting together")
        # Put blocks together
        S = np.zeros((p, p))
        block_id = 1
        for Sigma_block, S_block in zip(Sigma_blocks, S_blocks):
            block_inds = np.where(blocks == block_id)[0]
            block_inds = np.ix_(block_inds, block_inds)
            S[block_inds] = S_block
            block_id += 1
        # Make S feasible
        S, _ = utilities.scale_until_PSD(
            Sigma=Sigma,
            S=S,
            tol=kwargs.get("tol", constants.DEFAULT_TOL),
            num_iter=kwargs.get("num_iter", 10),
        )
        # Line search for MRC methods
        smoothing = 1
        if "smoothing" in kwargs:
            smoothing = kwargs["smoothing"]
        if method == "mvr":
            obj = mrc.mvr_loss
        elif method == "maxent":
            obj = mrc.maxent_loss
        if method in ["mvr", "maxent"]:
            best_gamma = 1
            best_loss = obj(Sigma=Sigma, S=S, smoothing=smoothing)
            for gamma in constants.GAMMA_VALS:
                loss = obj(Sigma=Sigma, S=gamma * S, smoothing=smoothing)
                if loss < best_loss:
                    best_gamma = gamma
                    best_loss = loss
        else:
            gamma = 1

        return S * gamma * scale_matrix

    # Currently cd solvers cannot handle group knockoffs
    # (this is todo)
    if not np.all(groups == np.arange(1, p + 1, 1)):
        solver = "psgd"
    if (method == "mvr" or method == "maxent") and solver == "psgd":
        # Check for imports
        utilities.check_kpytorch_available(purpose="group MRC knockoffs OR PSGD solver")
        from .kpytorch import mrcgrad

        S = mrcgrad.solve_mrc_psgd(Sigma=Sigma, groups=groups, method=method, **kwargs)
    elif method == "mvr":
        S = mrc.solve_mvr(Sigma=Sigma, **kwargs)
    elif method == "maxent":
        S = mrc.solve_maxent(Sigma=Sigma, **kwargs)
    elif method == "sdp" or method == "asdp":
        S = mac.solve_group_SDP(Sigma, groups, **kwargs,)
    elif method == "ciknock" or method == "ci":
        S = mrc.solve_ciknock(Sigma, **kwargs)
    elif method == "equicorrelated" or method == "eq":
        S = mac.solve_equicorrelated(Sigma, groups, **kwargs)
    else:
        raise ValueError(f"Unrecognized method {method}")

    # Rescale and return
    return S * scale_matrix
