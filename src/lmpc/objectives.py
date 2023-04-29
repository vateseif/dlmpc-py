import numpy as np
import cvxpy as cp
from typing import Optional

from src.lmpc.core import ObjectiveFunc

class LMPCObjectiveFun(ObjectiveFunc):

  def compute(self, 
              T: int,
              x0: np.ndarray,
              phi: cp.Variable):
    pass


class QuadForm(LMPCObjectiveFun):
  def __init__(self, 
              Q: np.ndarray,
              R: np.ndarray,
              xud: Optional[np.ndarray] = None) -> None:
    
    self.Q = Q
    self.R = R
    self.xud = xud  # reference states and inputs


  def compute(self, 
              T: int,
              x0: np.ndarray, 
              phi: cp.Variable) -> cp.atom.Atom:

    if self.xud is None:
      self.xud = np.zeros((phi.shape[0], 1))

    # compute system response
    Nx = self.Q.shape[0]
    Nu = self.R.shape[0]
    off = Nx*(T+1) # offset of states indices
    xu = phi[:, :Nx] @ x0[:Nx]  # (Nx*(T+1)+Nu*T, 1)
    
    # compute obj
    obj = 0
    for t in range(T):
      obj += cp.quad_form(xu[t*Nx:(t+1)*Nx] - self.xud[t*Nx:(t+1)*Nx], self.Q)
      obj += cp.quad_form(xu[off+t*Nu:off+(t+1)*Nu] - self.xud[off+t*Nu:off+(t+1)*Nu], self.R)

    return obj