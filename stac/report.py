"""
Reporting component of sanity checker
"""

import codecs
import copy
import os
import re
import sys
import xml.etree.cElementTree as ET

from   stac.edu import Context
from   stac.sanity import *

# ----------------------------------------------------------------------
# printing/formatting helpers
# ----------------------------------------------------------------------

def html_span(parent, text=None, attrib={}, **kwargs):
    span = ET.SubElement(parent, 'span', attrib, **kwargs)
    if text:
        span.text = text
    return span

def html_br(parent):
    return ET.SubElement(parent, 'br')

def html_anno_id(parent, anno, bracket=False):
    id_str = ('(%s)' if bracket else '%s') % anno.local_id()
    html_span(parent, id_str, attrib={'class':'annoid'})

# ---------------------------------------------------------------------
# severity
# ---------------------------------------------------------------------

class Severity(object):
    known_levels = ['warning','error']

    def __init__(self, level):
        self.level = level.lower()
        if self.level not in self.known_levels:
            msg = "Unknown severity '%s', must be one of %s"\
                    % (self.level, self.known_levels)
            raise ValueError(msg)

    def index(self):
        """
        Return the current severity as a number
        """
        return self.known_levels.index(self.level)

    def __eq__(self, other):
        return self.level == other.level

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.index() < other.index()

    def __gt__(self, other):
        return other > self

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

sv_WARNING = Severity('warning')
sv_ERROR   = Severity('error')

# ---------------------------------------------------------------------
# report
# ---------------------------------------------------------------------

class Report(object):
    def __init__(self):
        pass

class TextReport(Report):
    def __init__(self, anno_files, verbose, **kwargs):
        super(TextReport,self).__init__(**kwargs)
        self.anno_files = anno_files
        self.verbose    = verbose
        self.blurted    = {} # already have a header for this

    def _mk_text_header(self, k):
        """
        Create a header for the text portion of a report
        """
        descr = str(k)
        path  = self.anno_files[k][0]
        return '\n'.join([descr, '-' * len(descr), path])

    def blurt(self, k, msg):
        raise NotImplementedError('TextReport.blurt')

    def blurt_bullet(self, k, item):
        """
        Blurt out a list of lines to the screen as a single
        bullet point (typical use case would be a single line,
        but sometimes you want to elaborate
        """
        lines = item.text()
        if lines:
            output_lines  = [ ' * ' + lines[0] ]
            output_lines += [ '   ' + l for l in lines[1:] ]
            self.blurt(k, "\n".join(output_lines))

    def report(self, k, err_type, severity, header, xs, noisy=False):
        if xs:
            self.blurt(k, err_type + ': ' + header)
            for x in xs:
                self.blurt_bullet(k, x)
            self.blurt(k, '')

class StdoutTextReport(TextReport):
    def __init__(self, anno_files, verbose, **kwargs):
        super(StdoutTextReport,self).__init__(anno_files, verbose, **kwargs)
        self.seen = set()

    def blurt(self, k, msg):
        """
        Print a message to the screen.
        If this is the first time we printed something for
        `k`, also print a section header
        """
        if k not in self.seen:
            print ""
            print self._mk_text_header(k)
            print ""
            self.seen.add(k)

        print msg

    def report(self, k, err_type, severity, header, xs, noisy=False):
        # text output
        if xs and noisy and not self.verbose:
            self.blurt(k, err_type + ': ' + header)
            instances = 'instances' if len(xs) > 1 else 'instance'
            msg = '%d %s found. Use --verbose or see report for more details.' % (len(xs), instances)
            self.blurt_bullet(k, SimpleReportItem([msg]))
        else:
            super(StdoutTextReport, self).report(k, err_type, severity, header, xs, noisy)

class FileTextReport(TextReport):
    def __init__(self, fname, anno_files, verbose, **kwargs):
        super(FileTextReport,self).__init__(anno_files, verbose, **kwargs)
        self.seen    = set()
        self.fname   = fname
        self.started = False

    def blurt(self, k, msg):
        """
        Print a message to the screen.
        If this is the first time we printed something for
        `k`, also print a section header
        """
        # overwrite old reports; but append if we're still working
        mode = 'a' if self.started else 'w'
        with codecs.open(self.fname, mode, 'utf-8') as f:
            if k not in self.seen:
                print >> f, ""
                print >> f, self._mk_text_header(k)
                print >> f, ""
                self.seen.add(k)
            print >> f, msg
            self.started = True

class GlobalTextReport(FileTextReport):
    def __init__(self, anno_files, output_dir, **kwargs):
        report_txt = os.path.join(output_dir, 'report.txt')
        super(GlobalTextReport,self).__init__(report_txt, anno_files, verbose=True, **kwargs)

        # global report
        if os.path.exists(report_txt):
            os.remove(report_txt) # we want to append incrementally, so should be empty

# ---------------------------------------------------------------------
# HTML based reporting
# ---------------------------------------------------------------------

class HtmlReport(Report):
    css = """
.annoid  { font-family: monospace; font-size: small; }
.feature { font-family: monospace; }
.snippet { font-style: italic; }
.indented { margin-left:1em; }
.hidden   { display:none; }
.naughty  { color:red;  }
.spillover { color:red; font-weight: bold; } /* needs help to be visible */
.missing  { color:red;  }
.excess   { color:blue; }
"""

    js = """
function has(xs, x) {
    for (e in xs) {
       if (xs[e] === x) { return true; }
    }
    return false;
}


function toggle_hidden(name) {
    var ele = document.getElementById(name);
    var anc = document.getElementById('anc_' + name);
    if (has(ele.classList, "hidden")) {
        ele.classList.remove("hidden");
        anc.innerText = "[hide]";
    } else {
        ele.classList.add("hidden");
        anc.innerText = "[show]";
   }
}
"""
    def __init__(self, anno_files, output_dir, **kwargs):
        self.subreports         = {}
        self.subreport_sections = {}
        self.subreport_started  = {}
        self.anno_files         = anno_files
        self.output_dir         = output_dir

    @classmethod
    def mk_output_path(cls, odir, k, extension=''):
        relpath        = stac.id_to_path(k)
        ofile_dirname  = os.path.join(odir, os.path.dirname(relpath))
        ofile_basename = os.path.basename(relpath)
        return os.path.join(ofile_dirname, ofile_basename) + extension

    def write(self, k, path):
        """
        Write the subreport for a given key to the path.
        No-op if we don't have a sub-report for the given key
        """
        if k in self.subreports:
            htree = self.subreports[k]
            with open(path, 'w') as f:
                print >> f, ET.tostring(htree, encoding='utf-8')

    def delete(self, k):
        """
        Delete the subreport for a given key.
        This can be used if you want to iterate through lots of different
        keys, generating reports incrementally and then deleting them to
        avoid building up memory.

        No-op if we don't have a sub-report for the given key
        """
        if k in self.subreports:
            del self.subreports[k]
            del self.subreport_sections[k]

    def _add_subreport_link(self, k, html, sep, descr):
        k2       = copy.copy(k)
        k2.stage = 'discourse'
        rel_p    = self.mk_output_path('../../../', k, '.svg')
        sp       = ET.SubElement(html, 'span')
        sp.text  = sep
        h_a      = ET.SubElement(html, 'a', href=rel_p)
        h_a.text = descr

    def init_subreport(self, k):
        htree = ET.Element('html')
        self.subreports[k]         = htree
        self.subreport_sections[k] = {}
        self.subreport_started[k]  = {}

        hhead   = ET.SubElement(htree, 'head')
        style   = ET.SubElement(hhead, 'style', type='text/css')
        style.text = self.css
        script  = ET.SubElement(hhead, 'script', type='text/javascript')
        script.text = self.js

        h1      = ET.SubElement(htree, 'h1')
        h1.text    = str(k)

        hlinks     = html_span(htree)
        hpath      = ET.SubElement(hlinks, 'i')
        hpath.text = self.anno_files[k][0]
        if k.stage == 'discourse':
            self._add_subreport_link(k, hlinks, ' | ', 'graph')

        ET.SubElement(htree, 'hr')

        # placeholder sections for each severity level,
        # most severe first (ensure error comes before warnings)
        for sv in reversed(Severity.known_levels):
            self.subreport_sections[k][sv] = ET.SubElement(htree, 'div')
            self.subreport_started[k][sv]  = False

        return htree

    def subreport_path(self, k, extension='.report.html'):
        return self.mk_output_path(self.output_dir, k, extension)

    def flush_subreport(self, k):
        """
        Write and delete (to save memory)
        """
        html_path = self.subreport_path(k)
        if os.path.exists(html_path):
            os.remove(html_path) # might be leftover from past check
        self.write(k, html_path)
        self.delete(k)

    def anchor_name(self, k, header):
        mooshed = (str(k) + ' ' + header).lower()
        mooshed = re.sub(r'[^a-z0-9]+', '_', mooshed)
        return mooshed

    def report(self, k, err_type, severity, header, xs, noisy=False):
        if not xs:
            return

        if k in self.subreports:
            htree = self.subreports[k]
        else:
            htree = self.init_subreport(k)

        subtree = self.subreport_sections[k][severity.level]

        # emit a header if we haven't yet done so for this section
        # (avoid showing headers unless we have content for this
        # level of severity)
        if not self.subreport_started[k][severity.level]:
            h2      = ET.SubElement(subtree, 'h2')
            h2.text = (severity.level + 's').upper()
            self.subreport_started[k][severity.level] = True

        subdiv     = ET.SubElement(subtree, "div")
        descr      = ET.SubElement(subdiv, "span")
        descr.text = err_type + ' ' + severity.level.upper() + ': ' + header

        if noisy:
            script        = "toggle_hidden('" + self.anchor_name(k, header) + "');"
            descr.text    = descr.text + ' '
            expander      = ET.SubElement(subdiv, "a", href='#', onclick=script)
            expander.text = "[show]"
            expander.attrib['id'] = 'anc_' + self.anchor_name(k, header)

        ul = ET.SubElement(subdiv, "ul")
        ul.attrib['id'] = self.anchor_name(k, header)
        if noisy:
            ul.attrib['class'] = 'hidden'

        for x in xs:
            li      = ET.SubElement(ul, "li")
            li.append(x.html())
            # this is slightly evil: modify the offending annotations
            # with a highlight feature that the educe graphing lib
            # can pick up
            if severity == sv_ERROR:
                for anno in x.annotations():
                    anno.features["highlight"] = "red"

# ---------------------------------------------------------------------
# combined report
# ---------------------------------------------------------------------

class CombinedReport(HtmlReport):
    """
    An HTML report with alternative text-based reporters on the side
    """
    def __init__(self, anno_files, output_dir, verbose, **kwargs):
        super(CombinedReport, self).__init__(anno_files, output_dir, **kwargs)
        self._has_errors = {} # has non-warnings
        self.reporters =\
                [super(CombinedReport, self),
                 StdoutTextReport(anno_files, verbose,    **kwargs),
                 GlobalTextReport(anno_files, output_dir, **kwargs)]

    def report(self, k, err_type, severity, header, xs, noisy=False):
        for r in self.reporters:
            r.report(k, err_type, severity, header, xs, noisy)
        if xs and severity.level == 'error':
            self.set_has_errors(k)

    def set_has_errors(self, k):
        self._has_errors[k] = True

    def has_errors(self, k):
        """
        If we have error-level reports for the given key
        """
        return self._has_errors.get(k, False)

# ---------------------------------------------------------------------
# report item
# ---------------------------------------------------------------------

class ReportItem:
    def __init__(self):
        pass

    def annotations(self):
        return []

    def text(self):
        return []

    def html(self):
        parent         = ET.Element('span')
        lines          = self.text()
        line_span      = html_span(parent, lines[0])
        for l in lines[1:]:
            html_br(parent)
            line_span = html_span(parent, l)
        return parent

class ContextItem(ReportItem):
    def __init__(self, doc, contexts):
        self.doc      = doc
        self.contexts = contexts
        ReportItem.__init__(self)

class SimpleReportItem(ReportItem):
    def __init__(self, lines):
        ReportItem.__init__(self)
        self.lines = lines

    def text(self):
        return self.lines
