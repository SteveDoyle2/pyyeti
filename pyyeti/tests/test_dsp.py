import numpy as np
import scipy.stats as stats
from pyyeti import dsp, locate, ytools
from nose.tools import *


def test_resample():
    p = 5
    q = 5
    n = 530
    d = np.random.randn(n) - 55
    x = np.arange(n) + 100

    rtol = atol = 1e-15
    d0, x0, fir0 = dsp.resample(d, p, q, t=x, getfir=1)
    assert np.allclose(d0, d, rtol, atol)
    assert np.allclose(x0, x, rtol, atol)
    n = 2*10 + 1
    mid = (n-1)//2
    assert np.allclose(fir0[mid], 1, rtol, atol)
    fir0[mid] = 0
    assert np.allclose(0, fir0, rtol, atol)

    pts = 5
    d0, x0, fir0 = dsp.resample(d, p, q, t=x, getfir=1, pts=pts)
    assert np.allclose(d0, d, rtol, atol)
    assert np.allclose(x0, x, rtol, atol)
    n = 2*pts + 1
    mid = (n-1)//2
    assert np.allclose(fir0[mid], 1, rtol, atol)
    fir0_ = fir0.copy()
    fir0[mid] = 0
    assert np.allclose(0, fir0, rtol, atol)
    d1, fir1 = dsp.resample(d, p, q, getfir=1, pts=pts)
    d2, x2 = dsp.resample(d, p, q, t=x, pts=pts)
    assert np.all(d1 == d0)
    assert np.all(d1 == d2)
    assert np.allclose(fir0_, fir1, rtol, atol)
    assert np.allclose(x2, x, rtol, atol)

    D = np.vstack((d, d)).T
    D2, X2 = dsp.resample(D, p, q, t=x, pts=pts)
    assert np.all(d1 == D[:, 0])
    assert np.all(d1 == D[:, 1])
    assert np.allclose(x2, X2)

    lcc = {}
    for pts in [10, 50]:
        dup4, xup4 = dsp.resample(d, 4, 1, t=x, pts=pts)
        dup2, xup2 = dsp.resample(dup4, 10, 20, t=xup4, pts=pts)
        d0, x0 = dsp.resample(dup2, 1, 2, t=xup2, pts=pts)
        assert np.allclose(x0, x, rtol, atol)
        lcc[pts] = stats.pearsonr(d0, d)[0]
        assert 1-lcc[pts] < .015
        assert np.abs(np.mean(d)-np.mean(d0)) < .005
    assert lcc[50] > lcc[10]


def test_windowends():
    s = dsp.windowends(np.ones(8), 4)
    assert np.allclose([0., 0.25, 0.75, 1., 1., 1., 1., 1.], s)
    s = dsp.windowends(np.ones(8), .7, ends='back')
    assert np.allclose([1., 1., 1., 1., 0.85355339059327373,
                        0.5, 0.14644660940672621, 0.], s)
    s = dsp.windowends(np.ones(8), .5, ends='both')
    assert np.allclose([0., 0.25, 0.75, 1., 1., 0.75, 0.25, 0.], s)
    s = dsp.windowends(np.ones(8), .5, ends='none')
    assert np.allclose([1., 1., 1., 1., 1., 1., 1., 1.], s)
    s = dsp.windowends(np.ones(8), 3)
    assert np.allclose([0., 0.5, 1., 1., 1., 1., 1., 1.], s)
    s = dsp.windowends(np.ones(8), 2)
    assert np.allclose([0., 0.5, 1., 1., 1., 1., 1., 1.], s)


def test_waterfall():
    from pyyeti import srs
    sig, t, f = ytools.gensweep(10, 1, 50, 4)
    sr = 1/t[1]
    frq = np.arange(1., 5.1)
    Q = 20
    sig2 = sig[:int(sr*1.5), None]
    def func(s):
        return srs.srs(s, sr, frq, Q), frq
    mp, t, f = dsp.waterfall(2, .5, sig, sr, func,
                                which=0, freq=1)
    mp, t, f = dsp.waterfall(2, .5, sig2, sr, func,
                                which=0, freq=1)
    assert_raises(ValueError, dsp.waterfall, 2, .5, sig, sr, func,
                  which=None, freq=1)
    assert_raises(ValueError, dsp.waterfall, 2, 1.5, sig, sr, func,
                  which=None, freq=frq)
    sig = np.hstack((sig2, sig2))
    assert_raises(ValueError, dsp.waterfall, 2, .5, sig, sr, func,
                  which=None, freq=frq)


def test_get_turning_pts():
    y, x = dsp.get_turning_pts([1, 2, 3, 3, 3], [1, 2, 3, 4, 5],
                                  getindex=False)
    assert np.all([1, 3, 3] == y)
    assert np.all([1, 3, 5] == x)
    y2 = dsp.get_turning_pts([1, 2, 3, 3, 3], getindex=False)
    assert np.all(y == y2)
    assert_raises(ValueError, dsp.get_turning_pts,
                  [1, 2, 3, 3, 3], [1, 2, 3, 3, 5])
    assert_raises(ValueError, dsp.get_turning_pts,
                  [1, 2, 3, 3, 3, 5], [1, 2, 3, 4, 5])


def test_calcenv():
    p = 5
    x = [1, 2, 3, 2, 5]
    y = [1, 4, 9, 4, 2]
    assert_raises(ValueError, dsp.calcenv, x, y, p)

    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16]
    assert_raises(ValueError, dsp.calcenv, x, y, p)

    assert_raises(ValueError, dsp.calcenv, [0, 1, 2],
                  [0, 5, 0], method='default')

    xe, ye, *_ = dsp.calcenv([0, 1, 2], [0, 5, 0], makeplot='no')
    x_sb = [0, .95, 1.05, 2*1.05]
    y_sb = [0, 5, 5, 0]
    yi = np.interp(xe, x_sb, y_sb)
    err = abs(yi-ye).max()
    assert err < .006

    xen, yen, *_ = dsp.calcenv([0, 1, 2], [0, -5, 0],
                                  makeplot='no', method='min')
    assert np.allclose(xe, xen)
    assert np.allclose(ye, -yen)

    xe, ye, *_ = dsp.calcenv([0, 1, 2], [0, 5, 0],
                                p=3, n=4000, makeplot='no')
    x_sb = [0, .97, 1.03, 2*1.03]
    y_sb = [0, 5, 5, 0]
    yi = np.interp(xe, x_sb, y_sb)
    assert abs(yi-ye).max() < err/2

    xe, ye, *_ = dsp.calcenv([0, 1, 2], [0, -5, 0],
                                p=20, makeplot='no', method='max')
    # find where the 2 line segments meet
    # first, get the line segments:
    #  y1 => (0, 0) to (1.20*1, -5): y1 = -5/1.2 x
    #  y2 => (.8, -5) to (.8*2, 0):  y2 = 5/.8 x + b
    #     get b:  0 = 5/.8 * 1.6 + b; b = -10
    #  y1 = -5/1.2 x
    #  y2 = 6.25 x - 10
    #  --> intersect @ x = 10 / (6.25+5/1.2)
    x_int = 10 / (6.25+5/1.2)
    y_int = -5/1.2 * x_int
    x_sb = [0, x_int, 1.6]
    y_sb = [0, y_int, 0]
    yi = np.interp(xe, x_sb, y_sb)
    assert abs(yi-ye).max() < .006

    xen, yen, *_ = dsp.calcenv([0, 1, 2], [0, 5, 0],
                                  p=20, makeplot='no', method='min')
    assert np.allclose(xe, xen)
    assert np.allclose(ye, -yen)

    (xmax, ymax,
     xmin, ymin, h) = dsp.calcenv([0, 1, 2], [0, -5, 0], n=200,
                                     p=20, makeplot='no', base=None)
    yi = np.interp(xmax, x_sb, y_sb)
    assert abs(yi-ymax).max() < .06
    x_sb = [0, .8, 1.2, 2*1.2]
    y_sb = [0, -5, -5, 0]
    yi = np.interp(xmin, x_sb, y_sb)
    assert abs(yi-ymin).max() < .06

    (xmax, ymax,
     xmin, ymin, h) = dsp.calcenv([0, 1, 2], [0, -5, 0], n=200,
                                     p=20, makeplot='no',
                                     method='both')
    assert np.all(xmax == [0, 2])
    assert np.all(ymax == [0, 0])
    assert h is None
    x_sb = [0, .8, 1.2, 2*1.2]
    y_sb = [0, -5, -5, 0]
    yi = np.interp(xmin, x_sb, y_sb)
    assert abs(yi-ymin).max() < .06

    # test base:
    base = 2
    xe, ye, *_ = dsp.calcenv([0, 1, 2], [0-base, 5-base, 0-base],
                                 makeplot='no', n=100)
    xeb, yeb, *_ = dsp.calcenv([0, 1, 2], [0, 5, 0], makeplot='no',
                                  base=base, n=100)
    assert np.allclose(xe, xeb)
    assert np.allclose(ye+base, yeb)

    base = 2
    xe, ye, *_ = dsp.calcenv([0, 1, 2], [0-base, 5-base, 0-base],
                                makeplot='no', n=100, method='min')
    xeb, yeb, *_ = dsp.calcenv([0, 1, 2], [0, 5, 0], makeplot='no',
                                  base=base, n=100, method='min')
    assert np.allclose(xe, xeb)
    assert np.allclose(ye+base, yeb)

    base = 2
    (xex, yex,
     xen, yen, h) = dsp.calcenv([0, 1, 2], [0-base, 5-base, 0-base],
                                   makeplot='no', n=100, method='both')
    (xexb, yexb,
     xenb, yenb, h) = dsp.calcenv([0, 1, 2], [0, 5, 0],
                                     makeplot='no',
                                     base=base, n=100, method='both')
    assert np.allclose(xex, xexb)
    assert np.allclose(yex+base, yexb)
    assert np.allclose(xen, xenb)
    assert np.allclose(yen+base, yenb)


def test_fixtime():
    import sys
    for v in list(sys.modules.values()):
        if getattr(v, '__warningregistry__', None):
            v.__warningregistry__ = {}

    assert_raises(ValueError, dsp.fixtime,
                  ([1, 2, 3, 4], [1, 2, 3]))

    t = [0, 1, 6, 7]
    y = [1, 2, 3, 4]
    with assert_warns(RuntimeWarning):
        tn, yn = dsp.fixtime((t, y), sr=1)
        ty2 = dsp.fixtime(np.vstack([t, y]).T, sr=1)

    t2, y2 = ty2.T
    assert np.all(tn == t2)
    assert np.all(yn == y2)
    assert np.all(tn == np.arange(8))
    assert np.all(yn == [1, 2, 2, 2, 2, 2, 3, 4])

    with assert_warns(RuntimeWarning):
        ((t2, y2), pv,
         sr_stats, tp) = dsp.fixtime((t, y), getall=True,
                                        sr=1)
    assert np.all(tn == t2)
    assert np.all(yn == y2)
    assert np.all(pv == [False, False, False, False])
    assert np.allclose(sr_stats, [1, .2, 3/7, 1, 200/3])
    assert np.all(tp == np.arange(4))
    assert_raises(ValueError, dsp.fixtime, (1, 1, 1))

    drop = -1.40130E-45
    t = [0, .5, 1, 6, 7]
    y = [1, drop, 2, 3, 4]

    with assert_warns(RuntimeWarning):
        t2, y2 = dsp.fixtime([t, y], sr=1)
    assert np.all(tn == t2)
    assert np.all(yn == y2)

    t = [1, 2, 3]
    y = [drop, drop, drop]
    assert_warns(RuntimeWarning, dsp.fixtime, (t, y), 'auto')

    ((t2, y2), drops,
     sr_stats, tp) = dsp.fixtime((t, y), 'auto', deldrops=False,
                                    getall=True)
    assert np.all(tp == [0, 2])
    assert np.all(t2 == t)
    assert np.all(y2 == y)
    assert np.all(drops == [True, True, True])

    t = np.arange(100.)
    t = np.hstack((t, 200.))
    y = np.arange(101)
    with assert_warns(RuntimeWarning):
        t2, y2 = dsp.fixtime((t, y), 'auto')
    assert np.all(t2 == np.arange(100.))
    assert np.all(y2 == np.arange(100))

    with assert_warns(RuntimeWarning):
        t2, y2 = dsp.fixtime((t, y), 'auto', deloutliers=0)
    assert np.all(t2 == np.arange(200.1))
    sbe = np.ones(201, int)*99
    sbe[:100] = np.arange(100)
    sbe[-1] = 100
    assert np.all(y2 == sbe)

    t = [0, 1, 2, 3, 4, 5, 7, 6]
    y = [0, 1, 2, 3, 4, 5, 7, 6]
    with assert_warns(RuntimeWarning):
        t2, y2 = dsp.fixtime((t, y), 1)
    assert np.all(t2 == np.arange(8))
    assert np.all(y2 == np.arange(8))

    assert_raises(ValueError, dsp.fixtime, (t, y), 1,
                  negmethod='stop')

    t = np.arange(8)[::-1]
    assert_raises(ValueError, dsp.fixtime, (t, y), 1)

    t = np.arange(0, 1, .001)
    noise = np.random.randn(t.size)
    noise = noise / noise.max() / 100000
    y = np.random.randn(t.size)
    t2, y2 = dsp.fixtime((t+noise, y), 'auto', base=0)
    assert np.allclose(t, t2)
    assert np.all(y == y2)

    dt = np.ones(100)
    dt[80:] = .91*dt[80:]
    t = dt.cumsum()
    y = np.arange(100)
    with assert_warns(RuntimeWarning):
        t2, y2 = dsp.fixtime((t, y), 1)

    dt = np.ones(100)
    dt[80:] = 1.08*dt[80:]
    t = dt.cumsum()
    y = np.arange(100)
    with assert_warns(RuntimeWarning):
        t2, y2 = dsp.fixtime((t, y), 1)


def test_fixtime2():
    dt = .001
    sr = 1000
    t = np.arange(0, 1, dt)
    t[1:] += dt/2
    # t[400:] -= dt/2
    noise = np.random.randn(t.size)
    noise = noise / noise.max() / 100000
    y = np.random.randn(t.size)
    told = t+noise

    t2, y2 = dsp.fixtime((t+noise, y), 'auto', base=None)
    pv = locate.find_subsequence(y2, y[1:-1])
    assert pv.size > 0

    t3, y3 = dsp.fixtime((t+noise, y), 'auto', base=0.0)
    pv = locate.find_subsequence(y2, y[1:-1])
    assert pv.size > 0
    assert not np.allclose(t2[0], t3[0])
    assert np.allclose(t2-t2[0], t3-t3[0])
    assert abs(t3 - .003).min() < 1e-14


def test_fixtime_drift():
    L = 10000
    for factor in (.9995, 1.0005):
        t = np.arange(L)*(.001*factor)
        y = np.random.randn(L)
        t2, y2 = dsp.fixtime((t, y), 1000, base=0)
        t3, y3 = dsp.fixtime((t, y), 1000, fixdrift=1, base=0)

        i = np.argmax(y[3:100])
        i2 = np.nonzero(y2[:103] == y[i])[0][0]
        i3 = np.nonzero(y3[:103] == y[i])[0][0]
        d2 = abs(t2[i2] - t[i])
        d3 = abs(t3[i3] - t[i])

        L = len(y)
        i = L-100 + np.argmax(y[-100:-3])
        L = len(y2)
        i2 = L-103 + np.nonzero(y2[-103:] == y[i])[0][0]
        L = len(y3)
        i3 = L-103 + np.nonzero(y3[-103:] == y[i])[0][0]
        d2 += abs(t2[i2] - t[i])
        d3 += abs(t3[i3] - t[i])
        assert d3 < d2


def test_fixtime_too_many_tp():
    # actual data:
    fd = np.array([[ 0.91878125,  1.17070317],
                   [ 0.9226875 ,  1.17070317],
                   [ 0.9226875 ,  1.17070317],
                   [ 0.92659375,  1.17070317],
                   [ 0.92659375,  1.17070317],
                   [ 0.9305    ,  1.17070317],
                   [ 0.9305    ,  1.17070317],
                   [ 0.93440625,  1.17070317],
                   [ 0.93440625,  1.17070317],
                   [ 0.9383125 ,  1.17070317],
                   [ 0.9383125 ,  1.36582029],
                   [ 0.94221875,  1.29265141],
                   [ 0.94221875,  0.97558594],
                   [ 0.946125  ,  1.63410652],
                   [ 0.946125  ,  0.92680663],
                   [ 0.95003125,  1.5365479 ],
                   [ 0.95003125,  1.07314456],
                   [ 0.9539375 ,  1.26826179],
                   [ 0.9539375 ,  1.31704104],
                   [ 0.95784375,  1.1950928 ],
                   [ 0.95784375,  1.29265141],
                   [ 0.96175   ,  1.04875493],
                   [ 0.96175   ,  1.34143066],
                   [ 0.96565625,  0.92680663],
                   [ 0.96565625,  1.36582029],
                   [ 0.9695625 ,  0.87802738],
                   [ 0.9695625 ,  1.24387205],
                   [ 0.97346875,  0.97558594],
                   [ 0.97346875,  1.14631355],
                   [ 0.977375  ,  0.99997562],
                   [ 0.977375  ,  1.14631355],
                   [ 0.98128125,  1.07314456],
                   [ 0.98128125,  1.07314456],
                   [ 0.9851875 ,  1.1950928 ],
                   [ 0.9851875 ,  1.09753418],
                   [ 0.98909375,  1.1950928 ],
                   [ 0.98909375,  1.1219238 ],
                   [ 0.993     ,  1.1950928 ],
                   [ 0.993     ,  1.17070317],
                   [ 0.99690625,  1.1950928 ],
                   [ 0.99690625,  1.14631355],
                   [ 1.0008125 ,  1.17070317]])

    import sys
    for v in list(sys.modules.values()):
        if getattr(v, '__warningregistry__', None):
            v.__warningregistry__ = {}

    assert_raises(ValueError, dsp.fixtime,
                  ([1, 2, 3, 4], [1, 2, 3]))

    with assert_warns(RuntimeWarning):
        t, d = dsp.fixtime((*fd.T,), sr='auto')
    assert np.all(fd[:, 1] == d)
    assert np.allclose(np.diff(t), .002)
    assert np.allclose(t[0], fd[0, 0])


def test_fixtime_naninf():
    import sys
    for v in list(sys.modules.values()):
        if getattr(v, '__warningregistry__', None):
            v.__warningregistry__ = {}

    t = np.arange(15)
    y = [1, 2, 3, 4, np.nan, 6, 7, np.inf, 9, 10,
         -np.inf, 12, -1.40130E-45, 14, 15]
    
    with assert_warns(RuntimeWarning):
        (tn, yn), d, sr, tp = dsp.fixtime((t, y), sr=1, getall=1)

    d = np.nonzero(d)[0]
    assert np.all(t == tn)
    assert np.all(yn == [1, 2, 3, 4, 4, 6, 7, 7, 9,
                         10, 10, 12, 12, 14, 15])
