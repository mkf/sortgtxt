# -*- coding: utf-8 -*-

import sortgtxt

with open("django.po") as f:
    a = sortgtxt.Baza(f)

with open("djangomixed.po") as g:
    b = sortgtxt.Baza(g)

with open("docel.po", "w") as tar:
    tar.truncate()
    a.sortbymsgid()
    a.rawzapisdopliku(tar)
    tar.close()

with open("docelmixed.po", "w") as toa:
    toa.truncate()
    b.sortbymsgid()
    b.rawzapisdopliku(toa)
    toa.close()
