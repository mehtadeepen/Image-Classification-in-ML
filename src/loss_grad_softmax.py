
import numpy as np

def loss_grad_softmax_naive(W, X, y, reg):
    """
    Compute the loss and gradients using softmax function
    with loop, which is slow.
    Parameters
    ----------
    W: (K, D) array of weights, K is the number of classes and D is the dimension of one sample.
    X: (D, N) array of training data, each column is a training sample with D-dimension.
    y: (N, ) 1-dimension array of target data with length N with lables 0,1, ... K-1, for K classes
    reg: (float) regularization strength for optimization.
    Returns
    -------
    a tuple of two items (loss, grad)
    loss: (float)
    grad: (K, D) with respect to W
    """
    loss = 0
    grad = np.zeros_like(W)
    dim, num_train = X.shape
    num_classes = W.shape[0]
    for i in range(num_train):
        sample_x = X[:, i]
        scores = np.zeros(num_classes) # [K, 1] unnormalized score
        for cls in range(num_classes):
            w = W[cls, :]
            scores[cls] = w.dot(sample_x)
        # Shift the scores so that the highest value is 0
        scores -= np.max(scores)
        correct_class = y[i]
        sum_exp_scores = np.sum(np.exp(scores))

        corr_cls_exp_score = np.exp(scores[correct_class])
        loss_x = -np.log(corr_cls_exp_score / sum_exp_scores)
        loss += loss_x

        # compute the gradient
        percent_exp_score = np.exp(scores) / sum_exp_scores
        for j in range(num_classes):
            grad[j, :] += percent_exp_score[j] * sample_x


        grad[correct_class, :] -= sample_x # deal with the correct class

    loss /= num_train
    loss += 0.5 * reg * np.sum(W * W) # add regularization
    grad /= num_train
    grad += reg * W
    return loss, grad

def loss_grad_softmax_vectorized(W, X, y, reg):
    """ Compute the loss and gradients using softmax with vectorized version"""
    loss = 0
    grad = np.zeros_like(W)
    dim, num_train = X.shape

    scores = W.dot(X) # [K, N]
    # Shift scores so that the highest value is 0
    scores -= np.max(scores)
    scores_exp = np.exp(scores)
    correct_scores_exp = scores_exp[y, range(num_train)] # [N, ]
    scores_exp_sum = np.sum(scores_exp, axis=0) # [N, ]
    loss = -np.sum(np.log(correct_scores_exp / scores_exp_sum))
    loss /= num_train
    loss += 0.5 * reg * np.sum(W * W)

    scores_exp_normalized = scores_exp / scores_exp_sum
    # deal with the correct class
    scores_exp_normalized[y, range(num_train)] -= 1 # [K, N]
    grad = scores_exp_normalized.dot(X.T)
    grad /= num_train
    grad += reg * W

    return loss, grad


def loss_grad_svm_vectorized(W, X, y, reg):
    """
    Compute the loss and gradients using softmax function 
    with loop, which is slow.

    Parameters
    ----------
    W: (K, D) array of weights, K is the number of classes and D is the dimension of one sample.
    X: (D, N) array of training data, each column is a training sample with D-dimension.
    y: (N, ) 1-dimension array of target data with length N with lables 0,1, ... K-1, for K classes
    reg: (float) regularization strength for optimization.

    Returns
    -------
    a tuple of two items (loss, grad)
    loss: (float)
    grad: (K, D) with respect to W
    """

    dW = np.zeros(W.shape)
    loss = 0.0
    delta = 1.0

    num_train = y.shape[0]

    # compute all scores
    scores_mat = W.dot(X) # [C x N] matrix
     
    
    # get the correct class score 
    correct_class_score = scores_mat[y, xrange(num_train)] # [1 x N]
    
    margins_mat = scores_mat - correct_class_score + delta # [C x N]

    # set the negative score to be 0
    margins_mat = np.maximum(0, margins_mat)
    margins_mat[y, xrange(num_train)] = 0

    loss = np.sum(margins_mat) / num_train

    # add regularization to loss
    loss += 0.5 * reg * np.sum(W * W)

    # compute gradient
    scores_mat_grad = np.zeros(scores_mat.shape)

    # compute the number of margin > 0 for each sample
    num_pos = np.sum(margins_mat > 0, axis=0)
    scores_mat_grad[margins_mat > 0] = 1
    scores_mat_grad[y, xrange(num_train)] = -1 * num_pos

    # compute dW
    dW = scores_mat_grad.dot(X.T) / num_train + reg * W
    
    return loss, dW
    