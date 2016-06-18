# -*- coding: utf-8 -*-

import re

from babel.messages.pofile import denormalize
# that's a fairly large dependency, from which I am using just a few lines
# of code (denormalize() function, and its dependency, unescape())

quot = re.compile(r'"(?:\\.|[^"\\])*"')

msgstrbracke = re.compile('msgstr\[(\d*)]')


def parse_entry(lines):
    for l in lines:
        if not l.strip():
            raise EmptyLine
    k = ""
    comments = []
    listfound = False
    msgid = False
    for l in lines:
        if l.startswith('"'):
            if k == "msgid":
                msgid += denormalize(quot.findall(l)[0])
            elif k == "msgid_plural":
                msgid_plural += denormalize(quot.findall(l)[0])
            elif k == "msgstr":
                msgstr += denormalize(quot.findall(l)[0])
            elif k == "msgstr[":
                a = msgstrlist.pop()
                a += denormalize(quot.findall(l)[0])
                msgstrlist.append(a)
            else:
                raise UntiedQuote(l)

        elif l.startswith("msgid "):
            msgid = denormalize(quot.findall(l)[0])
            k = "msgid"
        elif l.startswith("msgid_plural "):
            msgid_plural = denormalize(quot.findall(l)[0])
            k = "msgid_plural"
        elif l.startswith("msgstr "):
            msgstr = denormalize(quot.findall(l)[0])
            k = "msgstr"
        elif l.startswith("msgstr["):
            if not listfound:
                listfound = True
                msgstrlist = []
            msgstrlist.append((
                msgstrbracke.findall(l)[0], 
                denormalize(quot.findall(l)[0])
            ))
            k = "msgstr["
        elif l.startswith("# "):
            comments.append(TransComment(l))
        elif l.startswith("#."):
            comments.append(ExtraComment(l))
        elif l.startswith("#:"):
            comments.append(ReferenceComment(l))
        elif l.startswith("#,"):
            comments.append(FlagsLine(l))
        elif l.startswith("#|"):
            comments.append(PreviousComment(l))
        elif l.startswith("#~"):
            comments.append(TildedComment(l))
        elif l.strip() == "#":
            comments.append(SamHash(l))
        else:
            raise UnknownToken(l)
    if listfound:
        return Plural(lines, msgid, msgid_plural, msgstrlist, comments)
    elif msgid == False:
        return SomeLines(lines, comments)
    elif len(msgid) == 0:
        return Meta(lines, msgstr, comments)
    else:
        return Entry(lines, msgid, msgstr, comments)


class EmptyLine(Exception):
    pass


class UnknownToken(Exception):
    pass


class UntiedQuote(UnknownToken):
    pass


def callbackentries(opened, callback):
    bufor = []
    for l in opened:
        if not l.strip():
            if len(bufor) > 0:
                callback(tuple(bufor))
                bufor = []
        else:
            bufor.append(l)
    if len(bufor) > 0:
        callback(tuple(bufor))


class Catalog(object):

    def __init__(self, opened):
        self.entries = []
        callbackentries(opened, lambda x: self.entries.append(parse_entry(x)))
        popthem = []
        for i in range(len(self.entries)):
            if isinstance(self.entries[i], Meta):
                popthem.append(i)
        for i in popthem:
            self.meta = self.entries.pop(i)

    def rawzapisdopliku(self, opened):
        self.meta.rawwrite(opened)
        for entry in self.entries:
            entry.rawwrite(opened)

    def sortbymsgid(self):
        self.entries = sorted(self.entries, key=lambda x: x.sortingname())


class SomeLines(object):

    def __init__(self, listoflines, comments):
        self.listoflines = listoflines
        self.comments = comments
        self.getourid()

    def getourid(self):
        cmsgid = None
        if not isinstance(self, Entry):
            for i in self.comments:
                if isinstance(i, TildedComment):
                    if cmsgid is None:
                        a = i.has_msgid()
                        if a is not None:
                            cmsgid = [a, ]
                    else:
                        a = i.has_quot()
                        if a is not None:
                            cmsgid.append(a)
        self.cmsgid = ''.join(cmsgid)

    def __str__(self):
        return str(self.listoflines) + "\ncomments:" + str(self.comments)

    def __repr__(self):
        return str(self)

    def rawwrite(self, opened):
        for line in self.listoflines:
            opened.write(line)
        opened.write("\n")

    def sortingname(self):
        if self.cmsgid is not None:
            return self.cmsgid
        print(self.comments[0].line)
        return self.comments[0].line


class Entry(SomeLines):

    def __init__(self, listoflines, msgid, msgstr, comments):
        self.msgid = msgid
        self.msgstr = msgstr
        for l in listoflines:
            if not l.strip():
                raise EmptyLine
        SomeLines.__init__(self, listoflines, comments)

    def sortingname(self):
        print(self.msgid)
        return self.msgid

    def getourid(self):
        pass


class Plural(Entry):

    def __init__(self, listoflines, msgid, msgid_plural, msgstrlist, comments):
        self.msgid_plural = msgid_plural
        Entry.__init__(self, listoflines, msgid, msgstrlist, comments)


class Meta(Entry):

    def __init__(self, listoflines, msgstr, comments):
        Entry.__init__(self, listoflines, "", msgstr, comments)


class Comment(object):

    def __init__(self, line):
        self.line = line

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.line


class SamHash(Comment):
    pass


class TransComment(Comment):
    pass


class ExtraComment(Comment):
    pass


class ReferenceComment(Comment):
    pass


class FlagsLine(Comment):
    pass


class PreviousComment(Comment):
    pass


class TildedComment(Comment):

    def has_msgid(self):
        if self.line.startswith("#~ msgid "):
            return denormalize(quot.findall(self.line)[0])
        else:
            return None

    def has_quot(self):
        if self.line.startswith('#~ "'):
            return denormalize(quot.findall(self.line)[0])
        else:
            return None
