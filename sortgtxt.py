# -*- coding: utf-8 -*-

import re

from babeldenormalize import denormalize

# regex for finding quotes
quot = re.compile(r'"(?:\\.|[^"\\])*"')

# regex for finding msgstr lists in plural entries
msgstrbracke = re.compile('msgstr\[(\d*)]')


class EmptyLine(Exception):
    """EmptyLine is raised in case an entry contains an empty line"""
    pass


class UnknownToken(Exception):
    """UnknownToken is raised in case there is an unknown token at the beginning of a line"""
    pass


class UntiedQuote(UnknownToken):
    """UntiedQuote is raised in case there is a string untied to some other token, like msgid, msgstr..."""
    pass


def callbackentries(opened, callback):
    """callbackentries separates entries separated with empty lines and calls callback(tuple_of_entry_lines)"""
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
    """Catalog represents a single .po file"""

    def __init__(self, opened):
        self.entries = []
        callbackentries(
            opened, lambda x: self.entries.append(self.parse_entry(x)))
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

    @staticmethod
    def getquot(line):
        return denormalize(quot.findall(line)[0])

    @staticmethod
    def msgstrdigit(line):
        return msgstrbracke.findall(line)[0]

    @staticmethod
    def startswithhash(l):
        if l.startswith("# "):
            return TransComment(l)
        elif l.startswith("#."):
            return ExtraComment(l)
        elif l.startswith("#:"):
            return ReferenceComment(l)
        elif l.startswith("#,"):
            return FlagsLine(l)
        elif l.startswith("#|"):
            return PreviousComment(l)
        elif l.startswith("#~"):
            return TildedComment(l)
        elif l.strip() == "#":
            return SamHash(l)
        else:
            raise UnknownToken(l)

    @classmethod
    def parse_entry(cls, lines):
        """Function for parsing a single entry,
        raising EmptyLine in case of an empty line"""
        for l in lines:
            if not l.strip():
                raise EmptyLine
        k = ""
        comments = []
        listfound = False
        msgid = False
        msgid_plural = None
        msgstr = None
        msgctxt = None
        msgstrlist = None
        getquot = cls.getquot
        for l in lines:
            if l.startswith('"'):
                if k == "msgid":
                    msgid += getquot(l)
                elif k == "msgid_plural":
                    msgid_plural += getquot(l)
                elif k == "msgstr":
                    msgstr += getquot(l)
                elif k == "msgctxt":
                    msgctxt += getquot(l)
                elif k == "msgstr[":
                    a = msgstrlist.pop()
                    a += getquot(l)
                    msgstrlist.append(a)
                else:
                    raise UntiedQuote(l)

            elif l.startswith("msgid "):
                msgid = getquot(l)
                k = "msgid"
            elif l.startswith("msgid_plural "):
                msgid_plural = getquot(l)
                k = "msgid_plural"
            elif l.startswith("msgstr "):
                msgstr = getquot(l)
                k = "msgstr"
            elif l.startswith("msgctxt "):
                msgctxt = getquot(l)
                k = "msgctxt"
            elif l.startswith("msgstr["):
                if not listfound:
                    listfound = True
                    msgstrlist = []
                msgstrlist.append((
                    cls.msgstrdigit(l),
                    getquot(l)
                ))
                k = "msgstr["
            elif l.startswith("#"):
                comments.append(cls.startswithhash(l))
            else:
                raise UnknownToken(l)
        if listfound:
            return Plural(lines, msgid, msgid_plural, msgstrlist, comments, msgctxt=msgctxt)
        elif msgid is False:
            return SomeLines(lines, comments)
        elif len(msgid) == 0:
            return Meta(lines, msgstr, comments, msgctxt=msgctxt)
        else:
            return Entry(lines, msgid, msgstr, comments, msgctxt=msgctxt)


class SomeLines(object):
    """SomeLines represents some lines from between two empty lines, not necessarily an Entry"""

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
    """Entry represents an entry (with msgid and msgstr), inheritts from SomeLines"""

    def __init__(self, listoflines, msgid, msgstr, comments, msgctxt=None):
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

    def __init__(self, listoflines, msgid, msgid_plural, msgstrlist, comments, msgctxt=None):
        self.msgid_plural = msgid_plural
        Entry.__init__(self, listoflines, msgid, msgstrlist,
                       comments, msgctxt=msgctxt)


class Meta(Entry):
    """Meta is an Entry eith msgid \"\", which has metadata in comments"""

    def __init__(self, listoflines, msgstr, comments, msgctxt=None):
        Entry.__init__(self, listoflines, "", msgstr, comments, msgctxt=msgctxt)


class Comment(object):

    def __init__(self, line):
        self.line = line

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.line


class SamHash(Comment):
    """SamHash is a comment without content, just the hash (#)"""
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
