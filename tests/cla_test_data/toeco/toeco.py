# Simulate event and recover responses
import numpy as np
from scipy.io import matlab
import matplotlib as mpl

mpl.interactive(0)
mpl.use("Agg")

from pyyeti import n2p, op2, stats, ode, cla
from pyyeti.pp import PP

# event name:
event = "TOECO"

if 1:
    # load data recovery data:
    sc = cla.load("../cla_params.pgz")
    cla.PrintCLAInfo(sc["mission"], event)

    # load nastran data:
    nas = op2.rdnas2cam("../nas2cam")

    # form ulvs for some SEs:
    SC = 101
    n2p.addulvs(nas, SC)

    import sys

    sys.path.insert(0, "..")
    import alphajoint

    drdefs = alphajoint.get_drdefs(nas, sc)

    # prepare spacecraft data recovery matrices
    DR = cla.DR_Event()
    DR.add(nas, sc["drdefs"])
    DR.add(nas, drdefs)

    # initialize results (ext, mnc, mxc for all drms)
    results = DR.prepare_results(sc["mission"], event)

    # set rfmodes:
    rfmodes = nas["rfmodes"][0]

    # setup modal mass, damping and stiffness
    m = None  # None means identity
    k = nas["lambda"][0]
    k[: nas["nrb"]] = 0.0
    b = 2 * 0.02 * np.sqrt(k)
    mbk = (m, b, k)

    # load in forcing functions:
    toeco = matlab.loadmat("toeco_ffns.mat", squeeze_me=True, struct_as_record=False)
    toeco["ffns"] = toeco["ffns"][:2, ::2]
    toeco["sr"] = toeco["sr"] / 2
    toeco["t"] = toeco["t"][::2]

    # form force transform:
    T = n2p.formdrm(nas, 0, [[8, 12], [24, 13]])[0].T

    # do pre-calcs and loop over all cases:
    ts = ode.SolveUnc(*mbk, 1 / toeco["sr"], rf=rfmodes)
    LC = toeco["ffns"].shape[0]
    t = toeco["t"]
    for j, force in enumerate(toeco["ffns"]):
        print("Running {} case {}".format(event, j + 1))
        genforce = T @ ([[1], [0.1], [1], [0.1]] * force[None, :])
        # solve equations of motion
        sol = ts.tsolve(genforce, static_ic=1)
        sol.t = t
        sol = DR.apply_uf(sol, *mbk, nas["nrb"], rfmodes)
        caseid = "{} {:2d}".format(event, j + 1)
        results.time_data_recovery(sol, nas["nrb"], caseid, DR, LC, j)

    # save results:
    cla.save("results.pgz", results)

#     # make some srs plots and tab files:
#     # results.rptext()
#     # results.rpttab()
#     results.rpttab(excel='toeco')
#     results.srs_plots()
#     # results.srs_plots(fmt='png')
#     results.resp_plots()
