import numpy as np
import cvxpy as cp
from typing import List, Optional, Tuple

from src.lmpc.constraints import LMPCConstraint
from src.lmpc.objectives import LMPCObjectiveFun
from src.lmpc.system_models import DistributedLTI
from src.lmpc.core import ControllerModel, ObjectiveFunc, Constraint


class LMPC(ControllerModel):

  def __init__(self, T:int) -> None:
    super().__init__()
    self.T = T
    self.model: DistributedLTI = None
    self.parentConstraint: LMPCConstraint = None
    self.constraints: List[Constraint] = [] 
    self.objectives: List[ObjectiveFunc] = [] 
    self.prob : Optional[cp.Problem] = None

  def __lshift__(self, model: DistributedLTI):
    ''' Overload lshift to augment the ControllerModel with the DistributedLTI'''
    assert isinstance(model, DistributedLTI), f"{model} isnt of type DistributedLTI"
    assert model.locality_model != None, f"{model} doesnt have any locality_model"
    self.model = model
    self.parentConstraint = LMPCConstraint(self.T, self.model)
    self.addConstraint(self.model.getSLSConstraint(self.T))
    self.addConstraint(self.model.getLocalityConstraint())
    self.addConstraint(self.model.getLowerTriangularConstraint())

  def addObjectiveFun(self, obj_fun: LMPCObjectiveFun):
    assert isinstance(obj_fun, LMPCObjectiveFun), "objective function not of type LMPCObjectiveFun"
    self.objectives.append(obj_fun)

  def addConstraint(self, con: LMPCConstraint):
    assert isinstance(con, LMPCConstraint), "constraint not of type LMPCConstraint"
    con._initFromParent(self.parentConstraint)
    self.constraints.append(con)

  def removeConstraintOfType(self, con_type: LMPCConstraint):
    ''' Remove constraints of con_type '''
    self.constraints = [c for c in self.constraints if not isinstance(c, con_type)]
    return

  def _applyConstraints(self, x0: np.ndarray, phi: cp.Variable) -> List:  
    ''' Returns list of cvxpy constraints'''
    # apply constraints stored in self.constraints
    constraints = []
    for con in self.constraints:
      constraints += con.compute(x0, phi)
    return constraints

  def _applyObjective(self, x0: np.ndarray, phi: cp.Variable):
    # compute system solution
    objective = sum([obj.compute(self.T, x0, phi) for obj in self.objectives])
    return cp.Minimize(objective)

  def _setupSolver(self, x0: np.ndarray):
    Nx, Nu, T = self.model.Nx, self.model.Nu, self.T
    assert x0.shape[0]==Nx or x0.shape[0]==Nx*(T+1), "x0 dim neither Nx not Nx*(T+1)"
    # define optim variables
    self.phi = cp.Variable((Nx*(T+1)+Nu*T, x0.shape[0]))
    # define param
    self.x0 = cp.Parameter(x0.shape)
    # solve
    self.prob = cp.Problem(
      self._applyObjective(self.x0, self.phi),
      self._applyConstraints(self.x0, self.phi)
    )
    return

  def solve(self, x0: np.ndarray) -> Tuple[np.ndarray, float]:
    ''' Solve the MPC problem and return u0 if solution is optimal else raise'''
    Nx, Nu, T = self.model.Nx, self.model.Nu, self.T
    # init cvxpy solver if first call
    if self.prob == None:
      self._setupSolver(x0)
    # update cvxpy parameter
    self.x0.value = x0
    self.prob.solve("SCS",verbose=False, warm_start=False)
    assert self.prob.status == "optimal", f"Solution not found. status: {self.prob.status}"
    # store results
    u0 = self.phi.value[Nx*(T+1):Nx*(T+1)+Nu, :Nx] @ x0[:Nx] # (Nu, 1)
    return u0, self.prob.value, self.phi.value