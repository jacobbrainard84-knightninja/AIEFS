import unittest
from check_study_entrypoints import validate_rows

class EntrypointTests(unittest.TestCase):
    def test_exact_and_glob_positive(self):
        rows=[{"study_id":"S1","canonical_entrypoints":"src/main.py;src/test_*.py"}]
        self.assertEqual(validate_rows(rows,{"src/main.py","src/test_a.py"}),[])
    def test_missing_exact_rejected(self):
        rows=[{"study_id":"S1","canonical_entrypoints":"src/missing.py"}]
        self.assertTrue(any("not tracked" in x for x in validate_rows(rows,set())))
    def test_unmatched_glob_rejected(self):
        rows=[{"study_id":"S1","canonical_entrypoints":"AIEF_1_0_*.py"}]
        self.assertTrue(any("no tracked-file match" in x for x in validate_rows(rows,{"README.md"})))
    def test_glob_does_not_cross_directory(self):
        rows=[{"study_id":"S1","canonical_entrypoints":"AIEF_1_0_*.py"}]
        self.assertTrue(validate_rows(rows,{"archive/AIEF_1_0_old.py"}))
    def test_path_traversal_rejected(self):
        rows=[{"study_id":"S1","canonical_entrypoints":"../outside.py"}]
        self.assertTrue(any("unsafe" in x for x in validate_rows(rows,{"../outside.py"})))
    def test_duplicate_study_id_rejected(self):
        rows=[{"study_id":"S1","canonical_entrypoints":"a.py"},{"study_id":"S1","canonical_entrypoints":"a.py"}]
        self.assertTrue(any("duplicate study_id" in x for x in validate_rows(rows,{"a.py"})))
if __name__=="__main__": unittest.main()
