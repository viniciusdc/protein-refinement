from Scripts.utils import prod_interno, dist_matrix_projection, centralizar
from Scripts.obj import *
import logging
from ctypes import *
so_file = r"../" + r'protein-refinement/libc/obj/objfun.o'
obj_fun = CDLL(so_file)
fun = obj_fun.objfun()


def protein_spg(grad_fun, initial_point, initial_dist_vector, ops, debug_mode=False
):
    """ spectral projected gradient method for protein like conformations using stress as objective function"""
    # Get Logger
    logger = logging.getLogger('root.load_spg.spg')
    if debug_mode:
        # Enable debug level messages
        logger.setLevel(10)

    u, v, w, lb, ub, tol, max_iter, num_memory = ops

    # initial point and distance vector setup
    xo = np.array(initial_point)
    yo = np.array(initial_dist_vector)

    # initial stress evaluation:
    fo = fun(len(xo), xo, len(yo), yo, u, v, w)

    # memory vector for non monotone line search:
    f_memory = np.zeros(num_memory)
    f_memory[0] = fo

    # first gradient evaluation:
    gx, gy = grad_fun(xo, yo, u, v, w)

    # aux variables initiation:
    backtracking = 0
    # inner product gradient--direction
    gtd = 0.0
    # norm for projected direction:
    norm_d = 0
    # espectral step
    pb = 1.0
    # iterator:
    k = 0
    # debug mode --true
    logger.info(
        f">> Iter - Obj ------ GtD ------ |d| ------ pB ------ alpha ----"
    )
    while k < max_iter:
        # first stop criteria;
        if fo < tol:
            logger.info(">> objective function value less than tolerance !")
            return xo, backtracking, k, fo, gtd, norm_d

        # first update (using the spectral gradient), when k == 1 it's a gradient like step:
        sx = xo - (gx / pb)
        sy = yo - (gy / pb)

        # projection in each coordinate onto [lb, ub] using numpy.clip()
        sy = np.clip(sy, lb, ub)
        # for i in range(len(yo)):
        #     if sy[i] < lb[i]:
        #         sy[i] = lb[i]
        #     elif sy[i] > ub[i]:
        #         sy[i] = ub[i]

        # new direction, projected gradient like
        dx = sx - xo
        dy = sy - yo
        gtd = prod_interno(gx, dx, gy, dy)
        norm_d = prod_interno(dx, dx, dy, dy)

        # second stop criteria;
        if abs(gtd) < 1e-6:
            logger.info(f">> Product --Gradient x direction-- less than tolerance {1e-6}!")
            return xo, backtracking, k, fo, gtd, norm_d

        # non-monotone line search with backtracking
        alpha = 1.0
        xp, yp = xo, yo
        gxp, gyp = gx, gy

        xn = xp + alpha * dx
        yn = yp + alpha * dy
        fn = obj_fun(xn, yn, u, v, w)
        f_max = max(f_memory)

        while fn > f_max + 1e-4 * alpha * gtd:
            backtracking = backtracking + 1
            alpha = 0.5 * alpha
            xn = xp + alpha * dx
            yn = yp + alpha * dy
            fn = obj_fun(xn, yn, u, v, w)

        logger.info(
            f">> {k:<5}: {fn:<10.3e} {gtd:<10.3e} {norm_d:<10.3e} {pb:<10.3e} {alpha:<10}"
        )

        # variables update:
        f_memory[k % num_memory] = fn
        xo = xn
        yo = yn
        fo = fn
        gx, gy = grad_fun(xn, yn, u, v, w)

        # Barzilai-Borwein spectral step calculation:
        yx = gx - gxp
        yy = gy - gyp
        zx = xo - xp
        zy = yo - yp
        pb = prod_interno(yx, zx, yy, zy) / prod_interno(zx, zx, zy, zy)
        # safe guards:
        if pb < 1e-16:
            pb = 1e-16
        if pb > 1e16:
            pb = 1e16

        k = k + 1

    logger.info(f">> Fail, Maximum iterations reached!")
    return xo, backtracking, k, fo, gtd, norm_d


# simple test for protein_spg using stress function
if __name__ == "__main__":
    test_solution = [[0, 0, 0], [3, 0, 0], [3, 4, 0], [0, 4, 0]]
    test_solution = np.array(test_solution)
    index_u = np.array([0, 0, 0, 1, 1, 2])
    index_v = np.array([1, 2, 3, 2, 3, 3])
    m = len(index_u)
    weight_w = np.ones(m)
    lower_b = [3.0, 5.0, 4.0, 4.0, 5.0, 2.98]
    upper_b = [3.0, 5.0, 4.0, 4.0, 5.0, 3.01]

    test = 1e-1 * np.asarray([np.random.normal(0, 1, 4) for i in range(3)]).T
    test = test + test_solution

    test = centralizar(test)
    test_distances = dist_matrix_projection(m, index_u, index_v, lower_b, upper_b, test)

    # function test
    options = [index_u, index_v, weight_w, lower_b, upper_b, 1e-8, 1000, 5]
    solve = protein_spg(stress, grad_stress, test, test_distances, options, True)
    spg_solution = solve[0]
    print(f"solution found: {spg_solution}")
    print(f"expected solution: {centralizar(test_solution)}")
