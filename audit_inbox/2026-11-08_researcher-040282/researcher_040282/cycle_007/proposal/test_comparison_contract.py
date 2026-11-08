"""Same11 contracts on original and proposed predicates; safe under python -O."""
import unittest
from comparison_contract import cases, checked, ContractMismatch, group_names


def make_suite(target):
    fixtures = cases()
    class ComparisonContract(unittest.TestCase):
        pass
    def method(group):
        def test(self):
            selected = [case for case in fixtures if case.group == group]
            self.assertTrue(selected, 'No positive fixture for group ' + group)
            violations = []
            for case in selected:
                try:
                    checked(target, case)
                except ContractMismatch as error:
                    violations.append(str(error))
            self.assertEqual(len(violations), 0,
                             str(len(violations)) + ' contract mismatches; first3=' + repr(violations[:3]))
        return test
    for group in group_names():
        setattr(ComparisonContract, 'test_' + group, method(group))
    return unittest.defaultTestLoader.loadTestsFromTestCase(ComparisonContract)
