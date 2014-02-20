import copy

import educe.stac.graph   as egr
from   educe.stac.tests import FakeEDU, FakeCDU, FakeRelInst, FakeDocument, FakeKey, graph_ids

from   stac_sanity import *
from stac.edu import Context

class SanityCheckerTest(unittest.TestCase):
    def setUp(self):
        self.dia1    = FakeEDU('d1',span=(1,10),type='Dialogue')
        self.turn1_1 = FakeEDU('t1.1',span=(1,5),type='Turn')
        self.turn1_2 = FakeEDU('t1.2',span=(6,8),type='Turn')
        self.edu1_1  = FakeEDU('e1.1',span=(1,2))
        self.edu1_2  = FakeEDU('e1.2',span=(2,5))
        self.edu1_3  = FakeEDU('e1.3',span=(7,8))

        self.dia2    = FakeEDU('d2',span=(11,20),type='Dialogue')
        self.turn2_1 = FakeEDU('t2',span=(16,18),type='Turn')
        self.edu2_1  = FakeEDU('e3',span=(16,18))

        self.edus1 = [self.edu1_1, self.edu1_2, self.edu1_3,
                      self.edu2_1,
                      self.turn1_1, self.turn1_2,
                      self.turn2_1,
                      self.dia1, self.dia2]

class CduPunctureTest(SanityCheckerTest):
    def mk_graph(self, doc):
        k = FakeKey('k')
        return egr.Graph.from_doc({k:doc}, k)

    def enclose(self, x, y, cdus, noop=True):
        if noop: return cdus
        cdus2 = copy.copy(cdus)
        cw    = FakeCDU('cw',[x,y])
        cdus2.append(cw)
        return cdus2

    def assertIntact(self, g, r):
        ids = graph_ids(g)
        self.assertFalse(is_puncture(g, ids[r.local_id()]), 'unexpected puncture')

    def assertPunctured(self, g, r):
        ids = graph_ids(g)
        self.assertTrue(is_puncture(g, ids[r.local_id()]), 'failed to detect puncture')

    def test_non_puncture(self, enclose=False):
        c1       = FakeCDU('c1', [self.edu1_1, self.edu1_2])
        r        = FakeRelInst('r', c1, self.edu1_3)
        cdus     = self.enclose(c1, self.edu1_3, [c1], enclose)
        doc      = FakeDocument(self.edus1, [r], cdus)
        g        = self.mk_graph(doc)
        self.assertIntact(g, r)

    def test_simple_dangler(self, enclose=False):
        """
        Danglers are not treated as punctures
        """
        c1       = FakeCDU('c1', [self.edu1_1, self.edu1_2])
        r        = FakeRelInst('r', self.edu1_2, self.edu1_3)
        cdus     = self.enclose(c1, self.edu1_3, [c1], enclose)
        doc      = FakeDocument(self.edus1, [r], cdus)
        g        = self.mk_graph(doc)
        self.assertIntact(g, r)

    def test_double_dangler(self, enclose=False):
        """
        Danglers can poke out of multiple CDUs
        """
        c1       = FakeCDU('c1', [self.edu1_1, self.edu1_2])
        c2       = FakeCDU('c2', [c1])
        r        = FakeRelInst('r', self.edu1_2, self.edu1_3)
        cdus     = self.enclose(c2, self.edu1_3, [c1, c2], enclose)
        doc      = FakeDocument(self.edus1, [r], cdus)
        g        = self.mk_graph(doc)
        self.assertIntact(g, r)

    def test_simple_puncture(self, enclose=False):
        c1       = FakeCDU('c1', [self.edu1_1, self.edu1_2])
        r        = FakeRelInst('r', self.edu1_3, self.edu1_2)
        cdus     = self.enclose(self.edu1_3, c1, [c1], enclose)
        doc      = FakeDocument(self.edus1, [r], cdus)
        g        = self.mk_graph(doc)
        self.assertPunctured(g, r)

    def test_cross_puncture(self, enclose=False):
        c1       = FakeCDU('c1', [self.edu1_1, self.edu1_2])
        c2       = FakeCDU('c2', [self.edu1_3])
        r        = FakeRelInst('r', self.edu1_3, self.edu1_2)
        cdus     = self.enclose(c2, c1, [c1, c2], enclose)
        doc      = FakeDocument(self.edus1, [r], cdus)
        g        = self.mk_graph(doc)
        self.assertPunctured(g, r)

    def test_cdu_chain(self):
        c1  = FakeCDU('c1', [self.edu1_1, self.edu1_2])
        c2  = FakeCDU('c2', [self.edu1_3, c1])
        doc = FakeDocument(self.edus1, [], [c1, c2])
        g   = self.mk_graph(doc)
        ids = graph_ids(g)
        def get_id(x):
            return g.mirror(ids[x.local_id()])
        mark = self.edu1_2.local_id()
        self.assertEqual(map(get_id, [c1,c2]),
                         containing_cdu_chain(g, ids[mark]))

    def test_enclosed(self):
        """
        Repeat tests but wrapping members in a common CDU
        """
        fns = [ self.test_non_puncture
              , self.test_simple_dangler
              , self.test_simple_puncture
              , self.test_cross_puncture
              ]
        for fn in fns:
            fn(enclose=True)

class DialogueBoundaryTest(SanityCheckerTest):
    def test_innocent(self):
        src  = self.edu1_1
        tgt  = self.edu1_2
        rel  = FakeRelInst('r', src, tgt)

        doc      = FakeDocument(self.edus1, [rel], [])
        contexts = Context.for_edus(doc)
        cp       = doc.copies
        self.assertTrue(stac.is_edu(cp[src]))
        self.assertTrue(stac.is_edu(cp[rel].source))
        self.assertFalse(is_cross_dialogue(contexts)(cp[rel]))

    def test_simple_segment_cross(self):
        src  = self.edu1_1
        tgt  = self.edu2_1
        rel  = FakeRelInst('r', src, tgt)

        doc      = FakeDocument(self.edus1, [rel], [])
        contexts = Context.for_edus(doc)
        cp       = doc.copies
        self.assertTrue(is_cross_dialogue(contexts)(cp[rel]))

    def test_innocent_cdu(self):
        cdu = FakeCDU('c1',[self.edu1_1, self.edu1_2])
        src = cdu
        tgt = self.edu1_3
        rel = FakeRelInst('r', src, tgt)

        doc      = FakeDocument(self.edus1, [rel], [cdu])
        contexts = Context.for_edus(doc)
        cp       = doc.copies
        self.assertFalse(is_cross_dialogue(contexts)(cp[rel]))
        self.assertFalse(is_cross_dialogue(contexts)(cp[cdu]))

    def test_cdu_cross(self):
        cdu = FakeCDU('c1',[self.edu1_1, self.edu1_2])
        src = cdu
        tgt = self.edu2_1
        rel = FakeRelInst('r', src, tgt)

        doc      = FakeDocument(self.edus1, [rel], [cdu])
        contexts = Context.for_edus(doc)
        cp       = doc.copies
        self.assertTrue(is_cross_dialogue(contexts)(cp[rel]))

    def test_cdu_itself_cross(self):
        cdu = FakeCDU('c1',[self.edu1_1, self.edu2_1])
        doc      = FakeDocument(self.edus1, [], [cdu])
        contexts = Context.for_edus(doc)
        cp       = doc.copies
        self.assertTrue(is_cross_dialogue(contexts)(cp[cdu]))
