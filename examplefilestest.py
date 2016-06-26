# -*- coding: utf-8 -*-

import sortgtxt

a = sortgtxt.Catalog(filename="django.po")

b = sortgtxt.Catalog(filename="djangomixed.po")

a.sortbymsgid()
a.rawsave(filename="docel.po")

b.sortbymsgid()
b.rawsave(filename="docelmixed.po")

c = sortgtxt.POFileSorter("django.po")
c.sort_and_save()
