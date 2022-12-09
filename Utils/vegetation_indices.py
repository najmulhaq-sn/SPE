#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np

def normalized_diff(b1, b2):
    """Take two n-dimensional numpy arrays and calculate the normalized
    difference.

    Math will be calculated (b1-b2) / (b1 + b2).

    Parameters
    ----------
    b1, b2 : numpy arrays
        Two numpy arrays that will be used to calculate the normalized
        difference. Math will be calculated (b1-b2) / (b1+b2).

    Returns
    ----------
    n_diff : numpy array
        The element-wise result of (b1-b2) / (b1+b2) calculation. Inf values
        are set to nan. Array returned as masked if result includes nan values.
        
    """
    
    if not (b1.shape == b2.shape):
        raise ValueError("Both arrays should have the same dimensions")
    
    
    # Ignore warning for division by zero
    with np.errstate(divide="ignore",invalid='ignore'):
        
       
        n_diff = (b1 - b2) / (b1 + b2)

    #Set inf values to nan and provide custom warning
    if np.isinf(n_diff).any():
        warnings.warn(
            "Divide by zero produced infinity values that will be replaced "
            "with nan values",
            Warning,
        )
        n_diff[np.isinf(n_diff)] = np.nan

    # Mask invalid values
    if np.isnan(n_diff).any():
        n_diff = np.ma.masked_invalid(n_diff)

    return n_diff

