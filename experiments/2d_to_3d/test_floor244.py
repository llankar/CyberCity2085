import copy,unittest
from build_floor244 import compile_plan
class FloorSupport(unittest.TestCase):
 def test_exact_union_never_adds_route_cells(self):
  data={'grid':[4,3],'walls':[{'cells':[[0,0],[1,0]]},{'cells':[[1,0],[3,2]]}]};before=copy.deepcopy(data)
  plan=compile_plan(data);self.assertEqual(plan['cells'],[[0,0],[1,0],[3,2]]);self.assertEqual(data,before)
 def test_rejects_outside_map(self):
  with self.assertRaises(ValueError):compile_plan({'grid':[4,3],'walls':[{'cells':[[4,0]]}]})
 def test_rejects_non_integer_cells(self):
  with self.assertRaises(ValueError):compile_plan({'grid':[4,3],'walls':[{'cells':[[1.5,0]]}]})
if __name__=='__main__':unittest.main()
