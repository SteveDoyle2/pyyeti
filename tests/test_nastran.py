import numpy as np
import os
from io import StringIO
import matplotlib.pyplot as plt
from pyyeti import nastran
from pyyeti.nastran import op2, n2p, op4
from nose.tools import *


def test_rdcards():
    a = nastran.rdcards(
        "tests/nas2cam_extseout/assemble.out", "CCC", no_data_return="no CCC"
    )
    assert a == "no CCC"

    assert_raises(
        ValueError,
        nastran.rdcards,
        "tests/nas2cam_extseout/assemble.out",
        "grid",
        return_var="bad option",
    )


def test_wtgrids():
    xyz = np.array([[0.1, 0.2, 0.3], [1.1, 1.2, 1.3]])
    with StringIO() as f:
        nastran.wtgrids(f, [100, 200], xyz=xyz, cd=10, form="{:8.2f}", ps=123, seid=100)
        s = f.getvalue()
    assert s == (
        "GRID         100       0    0.10    0.20"
        "    0.30      10     123     100\n"
        "GRID         200       0    1.10    1.20"
        "    1.30      10     123     100\n"
    )

    with StringIO() as f:
        nastran.wtgrids(
            f, [100, 200], xyz=xyz, cd=10, form="{:16.2f}", ps=123, seid=100
        )
        s = f.getvalue()
    assert s == (
        "GRID*                100               0"
        "            0.10            0.20\n"
        "*                   0.30              10"
        "             123             100\n"
        "GRID*                200               0"
        "            1.10            1.20\n"
        "*                   1.30              10"
        "             123             100\n"
    )
    assert_raises(ValueError, nastran.wtgrids, 1, 100, form="{:9f}")


def test_wttabled1():
    t = np.arange(0, 1, 0.05)
    d = np.sin(2 * np.pi * 3 * t)
    with StringIO() as f:
        nastran.wttabled1(f, 4000, t, d, form="{:16.2f}{:16.5f}")
        s = f.getvalue()
    sbe = (
        "TABLED1*            4000\n"
        "*\n"
        "*                   0.00         0.00000            0.05         0.80902\n"
        "*                   0.10         0.95106            0.15         0.30902\n"
        "*                   0.20        -0.58779            0.25        -1.00000\n"
        "*                   0.30        -0.58779            0.35         0.30902\n"
        "*                   0.40         0.95106            0.45         0.80902\n"
        "*                   0.50         0.00000            0.55        -0.80902\n"
        "*                   0.60        -0.95106            0.65        -0.30902\n"
        "*                   0.70         0.58779            0.75         1.00000\n"
        "*                   0.80         0.58779            0.85        -0.30902\n"
        "*                   0.90        -0.95106            0.95        -0.80902\n"
        "*       ENDT\n"
    )
    assert s == sbe
    assert_raises(ValueError, nastran.wttabled1, 1, 10, [1, 2], 1)
    assert_raises(
        ValueError, nastran.wttabled1, 1, 10, [1, 2], [1, 2], form="{:9f}{:9f}"
    )


def test_rdtabled1():
    tab = """TABLED1,    1
  , 0.39700, 0.00066, 0.39708, 0.00064, 0.39717, 0.00062, 0.39725, 0.00059,
  , 0.39733, 0.00057, 0.39742, 0.00054, 0.39750, 0.00051, 0.39758, 0.00048,
  , 0.39767, 0.00046, 0.39775, 0.00043, 0.39783, 0.00040, 0.39792, 0.00037,
  , 0.39800, 0.00035, 0.39808, 0.00032, 0.39817, 0.00030, 0.39825, 0.00027,
  , 0.39833, 0.00025, 0.39842, 0.00022, 0.39850, 0.00020, 0.39858, 0.00018,
  , 0.39867, 0.00016, 0.39875, 0.00014, 0.39883, 0.00012, 0.39892, 0.00010,
  , 0.39900, 0.00009, 0.39908, 0.00007, 0.39917, 0.00006, 0.39925, 0.00005,
  , 0.39933, 0.00004, 0.39942, 0.00003, 0.39950, 0.00002, 0.39958, 0.00001,
  , 0.39967, 0.00001, 0.39975, 0.00000, 0.39983, 0.00000,15.00000, 0.00000,
  ,    ENDT
"""
    with StringIO(tab) as f:
        dct = nastran.rdtabled1(f)
    with StringIO(tab) as f:
        lines = f.readlines()
    mat = np.array(
        [[float(num) for num in line[3:-2].split(",")] for line in lines[1:-1]]
    ).ravel()
    t = mat[::2]
    d = mat[1::2]
    assert np.allclose(dct[1][:, 0], t)
    assert np.allclose(dct[1][:, 1], d)


def test_rdtabled1_2():
    tab = """newname,    1
  , 0.39700, 0.00066, 0.39708, 0.00064, 0.39717, 0.00062, 0.39725, 0.00059,
  , 0.39733, 0.00057, 0.39742, 0.00054, 0.39750, 0.00051, 0.39758, 0.00048,
  , 0.39767, 0.00046, 0.39775, 0.00043, 0.39783, 0.00040, 0.39792, 0.00037,
  , 0.39800, 0.00035, 0.39808, 0.00032, 0.39817, 0.00030, 0.39825, 0.00027,
  , 0.39833, 0.00025, 0.39842, 0.00022, 0.39850, 0.00020, 0.39858, 0.00018,
  , 0.39867, 0.00016, 0.39875, 0.00014, 0.39883, 0.00012, 0.39892, 0.00010,
  , 0.39900, 0.00009, 0.39908, 0.00007, 0.39917, 0.00006, 0.39925, 0.00005,
  , 0.39933, 0.00004, 0.39942, 0.00003, 0.39950, 0.00002, 0.39958, 0.00001,
  , 0.39967, 0.00001, 0.39975, 0.00000, 0.39983, 0.00000,15.00000, 0.00000,
  ,    ENDT
"""
    with StringIO(tab) as f:
        dct = nastran.rdtabled1(f, "newname")
    with StringIO(tab) as f:
        lines = f.readlines()
    mat = np.array(
        [[float(num) for num in line[3:-2].split(",")] for line in lines[1:-1]]
    ).ravel()
    t = mat[::2]
    d = mat[1::2]
    assert np.allclose(dct[1][:, 0], t)
    assert np.allclose(dct[1][:, 1], d)


def test_rdwtbulk():
    with StringIO() as f:
        nastran.rdwtbulk("tests/nas2cam_csuper/inboard.out", f)
        s = f.getvalue()
    with open("tests/nas2cam_csuper/yeti_outputs/inboard_yeti.bulk") as f:
        sy = f.read()
    assert s == sy

    with StringIO() as f:
        nastran.rdwtbulk("tests/nas2cam_csuper/fake_bulk.out", f)
        s = f.getvalue()
    with open("tests/nas2cam_csuper/yeti_outputs/fake_bulk.blk") as f:
        sy = f.read()
    assert s == sy


def test_bulk2uset():
    xyz = np.array([[0.1, 0.2, 0.3], [1.1, 1.2, 1.3]])
    with StringIO() as f:
        nastran.wtgrids(f, [100, 200], xyz=xyz)
        u, c = nastran.bulk2uset(f)

    uset = n2p.addgrid(None, 100, "b", 0, xyz[0], 0)
    uset = n2p.addgrid(uset, 200, "b", 0, xyz[1], 0)
    assert np.allclose(uset, u)
    coord = {0: np.array([[0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])}
    assert coord.keys() == c.keys()
    assert np.allclose(coord[0], c[0])

    blk = """
CORD2R  10      0       0.0     0.0     0.0     1.0     0.0     0.0
        0.0     1.0     0.0
"""

    with StringIO(blk) as f:
        uset, cord = nastran.bulk2uset(f)
    assert uset.size == 0
    assert len(cord) == 2


def test_wtextseout():
    nas = op2.rdnas2cam("tests/nas2cam_csuper/nas2cam")
    se = 101
    maa = nas["maa"][se]
    kaa = nas["kaa"][se]
    pv = np.any(maa, axis=0)
    pv = np.ix_(pv, pv)
    maa = maa[pv]
    kaa = kaa[pv]

    uset = nas["uset"][se]
    bset = n2p.mksetpv(uset, "p", "b")
    usetb = nas["uset"][se].iloc[bset]
    b = n2p.mksetpv(uset, "a", "b")
    q = ~b
    b = np.nonzero(b)[0]
    baa = np.zeros_like(maa)
    baa[q, q] = 2 * 0.05 * np.sqrt(kaa[q, q])
    name = "_wtextseout_test_"
    pre = "tests/nas2cam_csuper/yeti_outputs/se101y"
    for bh, nm in zip((True, False), ("_bh", "")):
        try:
            nastran.wtextseout(
                name,
                se=101,
                maa=maa,
                kaa=kaa,
                baa=baa,
                bset=b,
                uset=usetb,
                spoint1=9900101,
                bh=bh,
            )
            names, mats, f, t = op4.load(name + ".op4", into="list")
            namesy, matsy, fy, ty = op4.load(pre + nm + ".op4", into="list")
            assert names == namesy
            assert f == fy
            assert t == ty
            for i, (m, my) in enumerate(zip(mats, matsy)):
                assert np.allclose(m, my)
            if bh:
                lst = (".asm", ".pch", ".baa_dmig")
            else:
                lst = (".asm", ".pch")
            for ext in lst:
                with open(name + ext) as f:
                    s = f.read()
                with open(pre + nm + ext) as f:
                    sy = f.read()
                assert s.replace(name.upper(), "SE101") == sy
        finally:
            for ext in (".asm", ".pch", ".op4", ".baa_dmig"):
                if os.path.exists(name + ext):
                    os.remove(name + ext)

    # test the additional writing of matrices:
    mug1 = np.arange(12).reshape(3, 4)
    mef1 = 10 * mug1
    try:
        nastran.wtextseout(
            name,
            se=101,
            maa=maa,
            kaa=kaa,
            baa=baa,
            bset=b,
            uset=usetb,
            spoint1=9900101,
            mug1=mug1,
            mef1=mef1,
        )
        names, mats, f, t = op4.load(name + ".op4", into="list")
        namesy, matsy, fy, ty = op4.load(pre + ".op4", into="list")
        assert names == namesy
        for i, (m, my) in enumerate(zip(mats, matsy)):
            if names[i] in ("mug1", "mef1"):
                assert np.allclose(m, eval(names[i]))
            else:
                assert f[i] == fy[i]
                assert t[i] == ty[i]
                assert np.allclose(m, my)
        lst = (".asm", ".pch")
        for ext in lst:
            with open(name + ext) as f:
                s = f.read()
            with open(pre + nm + ext) as f:
                sy = f.read()
            assert s.replace(name.upper(), "SE101") == sy

    finally:
        for ext in (".asm", ".pch", ".op4", ".baa_dmig"):
            if os.path.exists(name + ext):
                os.remove(name + ext)


def test_rdeigen():
    e1 = nastran.rdeigen("tests/nas2cam_csuper/assemble.out")
    e2 = nastran.rdeigen("tests/nas2cam_csuper/assemble.out", use_pandas=False)

    sbe = np.array(
        [
            2.776567e-05,
            1.754059e-05,
            1.183176e-05,
            1.708013e-05,
            2.299500e-05,
            4.592735e-05,
            1.699652e00,
            1.768612e00,
            1.857731e00,
            3.439703e00,
            7.024192e00,
            7.025385e00,
            1.072738e01,
            1.098313e01,
            1.389833e01,
            1.448323e01,
            1.466003e01,
            1.526510e01,
            2.519912e01,
            2.530912e01,
            2.925036e01,
            4.243738e01,
            4.311826e01,
            4.689425e01,
            4.780881e01,
            6.915960e01,
            8.182875e01,
            9.652563e01,
            9.655103e01,
            9.999950e01,
            1.746837e02,
            1.889342e02,
            1.996603e02,
            2.436533e02,
            2.839537e02,
            3.144806e02,
            4.254619e02,
            4.504501e02,
            5.460081e02,
            6.784015e02,
            7.837016e02,
            8.376910e02,
            8.747553e02,
            8.875936e02,
            9.451668e02,
            9.907786e02,
            1.020666e03,
            1.065056e03,
            1.360919e03,
            1.407037e03,
            1.675989e03,
            1.837844e03,
            1.970020e03,
            5.281664e03,
        ]
    )
    assert np.allclose(sbe, e1[0].cycles)
    assert np.allclose(e2[0], e1[0].values)


def test_rdeigen2():
    # hand-crafted example to trip an old error:
    data = """
1    SYSTEM MODES                                                              JUNE  10, 2015  NX NASTRAN  5/ 1/14   PAGE    72
                                                                                                        SUPERELEMENT 20
0

                                              R E A L   E I G E N V A L U E S
                                         (BEFORE AUGMENTATION OF RESIDUAL VECTORS)
   MODE    EXTRACTION      EIGENVALUE            RADIANS             CYCLES            GENERALIZED         GENERALIZED
    NO.       ORDER                                                                       MASS              STIFFNESS
        1         1       -3.043520E-08        1.744569E-04        2.776567E-05        1.000000E+00       -3.043520E-08
        2         2       -1.214641E-08        1.102107E-04        1.754059E-05        1.000000E+00       -1.214641E-08
        3         3        5.526609E-09        7.434117E-05        1.183176E-05        1.000000E+00        5.526609E-09
        4         4        1.151707E-08        1.073176E-04        1.708013E-05        1.000000E+00        1.151707E-08
        5         5        2.087500E-08        1.444818E-04        2.299500E-05        1.000000E+00        2.087500E-08
        6         6        8.327270E-08        2.885701E-04        4.592735E-05        1.000000E+00        8.327270E-08
1    SYSTEM MODES                                                              JUNE  10, 2015  NX NASTRAN  5/ 1/14   PAGE    73
                                                                                                        SUPERELEMENT 20
0
1    SYSTEM MODES                                                              JUNE  10, 2015  NX NASTRAN  5/ 1/14   PAGE    74
                                                                                                        SUPERELEMENT 0
0

                                              R E A L   E I G E N V A L U E S
                                         (AFTER AUGMENTATION OF RESIDUAL VECTORS)
   MODE    EXTRACTION      EIGENVALUE            RADIANS             CYCLES            GENERALIZED         GENERALIZED
    NO.       ORDER                                                                       MASS              STIFFNESS
        1         1        5.440398E+04        2.332466E+02        3.712235E+01        1.000000E+00        5.440398E+04
        2         2        5.579406E+04        2.362077E+02        3.759362E+01        1.000000E+00        5.579406E+04
        3         3        4.037157E+05        6.353862E+02        1.011249E+02        1.000000E+00        4.037157E+05
        4         4        3.110918E+06        1.763780E+03        2.807142E+02        1.000000E+00        3.110918E+06
        5         5        4.394972E+06        2.096419E+03        3.336554E+02        1.000000E+00        4.394972E+06
        6         6        5.312899E+06        2.304973E+03        3.668478E+02        1.000000E+00        5.312899E+06
        7         7        5.829790E+06        2.414496E+03        3.842789E+02        1.000000E+00        5.829790E+06
        8         8        6.409046E+06        2.531609E+03        4.029181E+02        1.000000E+00        6.409046E+06
"""
    with StringIO(data) as f:
        e = nastran.rdeigen(f)

    cyc20 = [
        2.776567e-05,
        1.754059e-05,
        1.183176e-05,
        1.708013e-05,
        2.299500e-05,
        4.592735e-05,
    ]
    cyc0 = [
        3.712235e01,
        3.759362e01,
        1.011249e02,
        2.807142e02,
        3.336554e02,
        3.668478e02,
        3.842789e02,
        4.029181e02,
    ]
    assert np.allclose(e[20]["cycles"].values, cyc20)
    assert np.allclose(e[0]["cycles"].values, cyc0)


def test_wtqcset():
    with StringIO() as f:
        nastran.wtqcset(f, 990001, 5)
        assert f.getvalue() == ("QSET1      12345  990001\nCSET1          6  990001\n")

    with StringIO() as f:
        nastran.wtqcset(f, 990001, 6)
        assert f.getvalue() == ("QSET1     123456  990001\n")

    with StringIO() as f:
        nastran.wtqcset(f, 990001, 7)
        assert f.getvalue() == (
            "QSET1     123456  990001\n"
            "QSET1          1  990002\n"
            "CSET1      23456  990002\n"
        )

    with StringIO() as f:
        nastran.wtqcset(f, 990001, 12)
        assert f.getvalue() == ("QSET1     123456  990001 THRU     990002\n")


def test_wtrbe3():
    assert_raises(ValueError, nastran.wtrbe3, 1, 100, 9900, 123456, [1, 2, 3])


def test_rdgpwg():
    # get third table:
    s1 = "W E I G H T"
    mass, cg, ref, Is = nastran.rdgpwg("tests/nas2cam_extseout/assemble.out", [s1, s1])
    r = 0
    m = np.array(
        [
            [
                3.345436e00,
                1.598721e-13,
                -1.132427e-12,
                -1.873559e-10,
                5.018153e02,
                -5.018153e02,
            ],
            [
                1.622036e-13,
                3.345436e00,
                -1.922240e-12,
                -5.018153e02,
                2.731554e-09,
                2.118899e03,
            ],
            [
                -1.133316e-12,
                -1.928013e-12,
                3.345436e00,
                5.018153e02,
                -2.118899e03,
                -1.996398e-09,
            ],
            [
                -1.874909e-10,
                -5.018153e02,
                5.018153e02,
                5.433826e05,
                -3.178349e05,
                -3.178349e05,
            ],
            [
                5.018153e02,
                2.734168e-09,
                -2.118899e03,
                -3.178349e05,
                2.441110e06,
                -7.527230e04,
            ],
            [
                -5.018153e02,
                2.118899e03,
                -1.992703e-09,
                -3.178349e05,
                -7.527230e04,
                2.772279e06,
            ],
        ]
    )
    c = np.array(
        [
            [3.345436e00, -5.600344e-11, 1.500000e02, 1.500000e02],
            [3.345436e00, 6.333702e02, 8.165016e-10, 1.500000e02],
            [3.345436e00, 6.333702e02, 1.500000e02, -5.967527e-10],
        ]
    )
    i = np.array(
        [
            [3.928379e05, 5.339971e-07, 6.432529e-07],
            [5.339971e-07, 1.023790e06, -2.849381e-06],
            [6.432529e-07, -2.849381e-06, 1.354959e06],
        ]
    )
    assert np.allclose(m, mass)
    assert np.allclose(c, cg)
    assert r == ref
    assert np.allclose(i, Is)

    a = nastran.rdgpwg("tests/nas2cam_extseout/assemble.out", "asdfsadfasdf")
    for i in a:
        assert i is None

    a = nastran.rdgpwg("tests/nas2cam_extseout/assemble.out", (s1, s1, "END OF JOB"))
    for i in a:
        assert i is None


def test_fsearch():
    with open("tests/nas2cam_extseout/assemble.out") as f:
        a, p = nastran.fsearch(f, "asdfadfadfadsfasf")
    assert a is None
    assert p is None


def test_wtrspline():
    assert_raises(ValueError, nastran.wtrspline, 1, 1, 1)
    ids = np.array(
        [
            [100, 1],
            [101, 0],
            [102, 0],
            [103, 1],
            [104, 0],
            [105, 1],
            [106, 0],
            [107, 0],
            [108, 0],
            [109, 1],
            [110, 0],
            [111, 0],
            [112, 1],
        ]
    )
    with StringIO() as f:
        nastran.wtrspline(f, 10, ids)
        s = f.getvalue()

    sbe = (
        "RSPLINE       10     0.1     100     101  123456     102  123456     103\n"
        "RSPLINE       11     0.1     103     104  123456     105\n"
        "RSPLINE       12     0.1     105     106  123456     107  123456     108\n"
        "          123456     109\n"
        "RSPLINE       13     0.1     109     110  123456     111  123456     112\n"
    )
    assert sbe == s

    # test for first and last must be independent error:
    ids[-1, 1] = 0
    assert_raises(ValueError, nastran.wtrspline, 1, 10, ids)

    # test for "no independents" error:
    ids[:, 1] = 1
    assert_raises(ValueError, nastran.wtrspline, 1, 10, ids)


def test_wtrspline_rings():
    theta1 = np.arange(0, 359, 360 / 5) * np.pi / 180
    rad1 = 50.0
    sta1 = 0.0
    n1 = len(theta1)
    ring1 = np.vstack(
        (
            np.arange(1, n1 + 1),  # ID
            sta1 * np.ones(n1),  # x
            rad1 * np.cos(theta1),  # y
            rad1 * np.sin(theta1),
        )
    ).T  # z
    theta2 = np.arange(10, 359, 360 / 7) * np.pi / 180
    rad2 = 45.0
    sta2 = 1.0
    n2 = len(theta2)
    ring2 = np.vstack(
        (
            np.arange(1, n2 + 1) + 100,  # ID
            sta2 * np.ones(n2),  # x
            rad2 * np.cos(theta2),  # y
            rad2 * np.sin(theta2),
        )
    ).T  # z

    uset1 = (
        "Name 1",
        n2p.addgrid(None, ring1[:, 0].astype(int), "b", 0, ring1[:, 1:], 0),
    )
    uset2 = (
        "Name 2",
        n2p.addgrid(None, ring2[:, 0].astype(int), "b", 0, ring2[:, 1:], 0),
    )

    fig = plt.figure("rspline demo", figsize=(8, 6))
    fig.clf()
    ax = fig.add_subplot(1, 1, 1, projection="3d")

    with StringIO() as f:
        nastran.wtrspline_rings(
            f, ring1, ring2, 1001, 2001, makeplot=ax, independent="ring1"
        )
        u, c = nastran.bulk2uset(f)
        rsplines1 = nastran.rdcards(f, "RSPLINE")

    with StringIO() as f:
        nastran.wtrspline_rings(
            f, uset1, uset2, 1001, 2001, makeplot=ax, independent="n amE 2"
        )
        u2, c2 = nastran.bulk2uset(f)
        rsplines2 = nastran.rdcards(f, "RSPLINE")

    assert np.allclose(u, u2)
    for k, v in c2.items():
        assert np.allclose(c[k], v)

    # x coord of new grids should be same as ring 2 ... 1.0:
    assert np.allclose(1, u.loc[(slice(None), 1), "x"])

    # y, z coords should be like ring1, but with reduced radius to
    # match ring 2:
    assert np.allclose(ring1[:, 2:] * rad2 / rad1, u.loc[(slice(None), 1), "y":"z"])

    # the local coord:
    #  z_local is x
    #  x_local points through node 1 ... which is on y
    to_local = [[0, 1.0, 0], [0, 0, 1], [1.0, 0, 0]]
    assert np.allclose(c[10010][-3:].T, to_local)

    # rsplines1 should have the 1001 series of numbers being
    # independent:
    assert (rsplines1[:, 2] > 1000).all()

    # rsplines2 should have the 101 series of numbers being
    # independent:
    assert (rsplines2[:, 2] < 1000).all()

    assert_raises(
        ValueError,
        nastran.wtrspline_rings,
        1,
        uset1,
        uset2,
        1001,
        2001,
        makeplot="no",
        independent="badoption",
    )

    uset1 = uset1[1]
    assert_raises(
        ValueError,
        nastran.wtrspline_rings,
        1,
        uset1[:-1],
        uset2,
        1001,
        2001,
        makeplot="no",
    )

    uset3 = None
    for row in ring2:
        uset3 = n2p.addgrid(uset3, int(row[0]), "b", 0, [row[3], row[1], row[2]], 0)
    assert_raises(
        ValueError, nastran.wtrspline_rings, 1, uset1, uset3, 1001, 2001, makeplot="no"
    )


def test_wtcoordcards():
    with StringIO() as f:
        nastran.wtcoordcards(f, None)
        assert f.getvalue() == ""
        nastran.wtcoordcards(f, {})
        assert f.getvalue() == ""


def test_mknast():
    name = "_test_mknast_.sh"
    try:
        nastran.mknast(
            name,
            stoponfatal="yes",
            files=["tt.py", "tt", "doruns.sh", "subd/t.t"],
            before="# BEFORE",
            after="# AFTER",
            top="# TOP",
            bottom="# BOTTOM",
        )
        with open(name) as f:
            s = f.read().splitlines()
    finally:
        if os.path.exists(name):
            os.remove(name)

    sbe = [
        "#!/bin/sh",
        "cd --",
        "",
        "# TOP",
        "",
        "# ******** File tt.py ********",
        "# BEFORE",
        "  nast9p1 'batch=no' 'tt.py'",
        "  if [ X != X`grep -l '[*^][*^][*^].*FATAL' tt.out` ] ; then",
        "    exit",
        "  fi",
        "# AFTER",
        "",
        "# ******** File tt ********",
        "# BEFORE",
        "  nast9p1 'batch=no' 'tt'",
        "  if [ X != X`grep -l '[*^][*^][*^].*FATAL' tt.out` ] ; then",
        "    exit",
        "  fi",
        "# AFTER",
        "",
        "# ******** File doruns.sh ********",
        "# BEFORE",
        "  nast9p1 'batch=no' 'doruns.sh'",
        "  if [ X != X`grep -l '[*^][*^][*^].*FATAL' doruns.out` ] ; then",
        "    exit",
        "  fi",
        "# AFTER",
        "",
        "# ******** File subd/t.t ********",
        "  cd subd",
        "# BEFORE",
        "  nast9p1 'batch=no' 't.t'",
        "  if [ X != X`grep -l '[*^][*^][*^].*FATAL' t.out` ] ; then",
        "    exit",
        "  fi",
        "# AFTER",
        "  cd --",
        "# BOTTOM",
    ]

    for i, st in enumerate(sbe):
        if st == "  cd --":
            assert s[i][:4] == "  cd"
        elif st == "cd --":
            assert s[i][:2] == "cd"
        else:
            print(s[i])
            print(st)
            assert s[i] == st


def test_rddtipch():
    d = nastran.rddtipch("tests/nas2cam_csuper/fake_dtipch.pch", "TEF1")
    dof = [
        (10, 8),
        (97, 8),
        (3140051, 8),
        (3000108, 77),
        (3000113, 77),
        (3000299, 77),
        (3000310, 77),
        (3000330, 77),
    ]
    n = 0
    for i in dof:
        n += i[1]
    sbe = np.empty((n, 2), dtype=np.int64)
    n = 0
    for i in dof:
        sbe[n : n + i[1], 0] = i[0]
        sbe[n : n + i[1], 1] = np.arange(1, i[1] + 1)
        n += i[1]
    assert np.all(d == sbe)


def test_rddmig():
    dct = nastran.rddmig("tests/nastran_dmig_data/matrix_factory.pch")
    dct2 = nastran.rddmig("tests/nastran_dmig_data/matrix.op2")

    for key, val in dct.items():
        val2 = dct2["m" + key]
        assert np.allclose(val, val2)

    assert np.all((dct["ident"] == np.eye(dct["ident"].shape[0])).values)
    pattern_mat = np.empty(dct["patrn"].shape)
    for i in range(dct["patrn"].shape[1]):
        pattern_mat[:, i] = i + 1
    assert np.all((pattern_mat == dct["patrn"]).values)

    assert sorted(dct.keys()) == ["cmplx", "ident", "patrn", "randm"]

    dct = nastran.rddmig(
        "tests/nastran_dmig_data/matrix_factory.pch", ("patrn", "randm")
    )
    dct2 = nastran.rddmig("tests/nastran_dmig_data/matrix.op2", ("mpatrn", "mrandm"))

    for key, val in dct.items():
        val2 = dct2["m" + key]
        assert np.allclose(val, val2)

    assert sorted(dct.keys()) == ["patrn", "randm"]


def test_rddmig2():
    dct = nastran.rddmig("tests/nastran_dmig_data/matrix.op2", "mrandm")

    # chop out some DOF so we can test 'expanded':
    slc = (slice(None), slice(3))
    mrandm = dct["mrandm"].loc[slc, slc]

    with StringIO() as f:
        nastran.wtdmig(f, dict(mrandm=mrandm))
        default = nastran.rddmig(f)
        expanded = nastran.rddmig(f, expanded=True)

    assert np.allclose(expanded["mrandm"].sum().sum(), default["mrandm"].sum().sum())
    assert default["mrandm"].shape == (12, 12)
    assert expanded["mrandm"].shape == (21, 21)
    assert np.allclose(mrandm, default["mrandm"])
    assert np.allclose(mrandm, expanded["mrandm"].loc[slc, slc])
    slc2 = (slice(None), slice(4, None))
    assert np.all(expanded["mrandm"].loc[slc2, slc2] == 0.0)

    # test symmetric writing/reading:
    symm = np.arange(12)[:, None] * np.arange(12)
    symm = symm.T @ symm
    default["mrandm"].iloc[:, :] = symm.astype(float)

    with StringIO() as f:
        nastran.wtdmig(f, default)
        dct = nastran.rddmig(f)
        s = f.getvalue()

    assert np.allclose(dct["mrandm"], default["mrandm"].iloc[1:, 1:])
    assert s.startswith(
        "DMIG    MRANDM         0       6       2       0       0"
        "              12\n"
        "DMIG*   MRANDM                         1               2\n"
        "*                      1               2 5.060000000D+02\n"
        "*                      1               3 1.012000000D+03\n"
        "*                      2               1 1.518000000D+03\n"
        "*                      2               2 2.024000000D+03\n"
        "*                      2               3 2.530000000D+03\n"
        "*                      3               1 3.036000000D+03\n"
        "*                      3               2 3.542000000D+03\n"
        "*                      3               3 4.048000000D+03\n"
        "*                     10               0 4.554000000D+03\n"
        "*                     11               0 5.060000000D+03\n"
        "*                     12               0 5.566000000D+03\n"
        "DMIG*   MRANDM                         1               3\n"
    )

    assert s.endswith(
        "DMIG*   MRANDM                        10               0\n"
        "*                     10               0 4.098600000D+04\n"
        "*                     11               0 4.554000000D+04\n"
        "*                     12               0 5.009400000D+04\n"
        "DMIG*   MRANDM                        11               0\n"
        "*                     11               0 5.060000000D+04\n"
        "*                     12               0 5.566000000D+04\n"
        "DMIG*   MRANDM                        12               0\n"
        "*                     12               0 6.122600000D+04\n"
    )