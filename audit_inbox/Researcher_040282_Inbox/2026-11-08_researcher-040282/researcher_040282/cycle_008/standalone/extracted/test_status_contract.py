"""Same twelve public API contracts on original and candidate, also with -O."""
import unittest
from status_contract import cases,groups,checked,ContractMismatch


def suite(api,bundle):
    class PublicOracleContract(unittest.TestCase):
        pass
    def method(group):
        def test(self):
            selected=[case for case in cases() if case.group==group]
            self.assertTrue(selected,'Missing nonvacuity fixture')
            violations=[]
            for case in selected:
                try:checked(api,bundle,case)
                except ContractMismatch as e:violations.append(str(e))
            self.assertEqual(len(violations),0,str(len(violations))+' mismatches; first3='+repr(violations[:3]))
        return test
    for group in groups():setattr(PublicOracleContract,'test_'+group,method(group))
    return unittest.defaultTestLoader.loadTestsFromTestCase(PublicOracleContract)
