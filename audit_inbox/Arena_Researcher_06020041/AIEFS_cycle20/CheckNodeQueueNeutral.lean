import AIEFGateCore.NodeQueueNeutral
#print axioms AIEFGate.QueueNeutral.histSum_shift
#print axioms AIEFGate.QueueNeutral.aggregate_step
#print axioms AIEFGate.QueueNeutral.queue_conserved_evolve
#print axioms AIEFGate.NodeQueueNeutral.neighbour_total
#print axioms AIEFGate.NodeQueueNeutral.total_step
#print axioms AIEFGate.NodeQueueNeutral.node_conserved_evolve

open AIEFGate.QueueNeutral
example : histSum 2 (fun k => (k : ℝ)) = 3 := by
  norm_num [histSum, Finset.sum_range_succ]
example : histSum 0 (fun k => (k : ℝ)) = 0 := by
  norm_num [histSum]

