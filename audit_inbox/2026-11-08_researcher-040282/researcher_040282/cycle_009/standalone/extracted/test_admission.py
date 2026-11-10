"""Same nine proposed admission-contract methods against real API/new guard."""
import unittest
from admission_contract import checked,scenarios,groups,ContractMismatch


def suite(target,fixture,official_pin,records):
    class AdmissionContract(unittest.TestCase):pass
    def method(group):
        def test(self):
            cases=[case for case in scenarios() if case.group==group]
            self.assertTrue(cases,'Vacuous fixture group')
            violations=[]
            for case in cases:
                try:checked(target,fixture,official_pin,case,records)
                except ContractMismatch as error:violations.append(str(error))
            self.assertEqual(len(violations),0,repr(violations))
        return test
    for group in groups():setattr(AdmissionContract,'test_'+group,method(group))
    return unittest.defaultTestLoader.loadTestsFromTestCase(AdmissionContract)
