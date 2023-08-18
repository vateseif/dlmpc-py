from core import AbstractControllerConfig, AbstractLLMConfig, AbstractRobotConfig
from prompts.stack import *


class PlanLLMConfig(AbstractLLMConfig):
  prompt: str = TASK_PLANNER_PROMPT
  parsing: str = "plan"
  model_name: str = "gpt-3.5-turbo"
  temperature: float = 0.7

class ObjectiveLLMConfig(AbstractLLMConfig):
  prompt: str = OBJECTIVE_DESIGNER_PROMPT
  parsing: str = "objective"
  model_name: str = "gpt-3.5-turbo"
  temperature: float = 0.7

class OptimizationLLMConfig(AbstractLLMConfig):
  prompt: str = OPTIMIZATION_DESIGNER_PROMPT
  parsing: str = "optimization"
  model_name: str = "gpt-3.5-turbo"
  temperature: float = 0.7

class NMPCObjectiveLLMConfig(AbstractLLMConfig):
  prompt: str = NMPC_OBJECTIVE_DESIGNER_PROMPT
  parsing: str = "objective"
  model_name: str = "gpt-3.5-turbo"
  temperature: float = 0.7

class NMPCOptimizationLLMConfig(AbstractLLMConfig):
  prompt: str = NMPC_OPTIMIZATION_DESIGNER_PROMPT
  parsing: str = "optimization"
  model_name: str = "gpt-4"
  temperature: float = 0.7

class BaseControllerConfig(AbstractControllerConfig):
  nx: int = 3
  nu: int = 3 
  T: int = 15
  dt: float = 0.1
  lu: float = -0.5 # lower bound on u
  hu: float = 0.5  # higher bound on u

class BaseNMPCConfig(AbstractControllerConfig):
  nx: int = 3
  nu: int = 3 
  T: int = 10
  dt: float = 0.05
  lu: float = -0.2 # lower bound on u
  hu: float = 0.2  # higher bound on u
  model_type: str = "discrete"
  penalty_term_cons: float = 1e7
  

class BaseRobotConfig(AbstractRobotConfig):
  name: str = "objective"
  tp_type: str = "plan"               # Task planner
  od_type: str = "nmpc_optimization"          # Optimization Designer:  ["objective", "optimization"]
  controller_type: str = "nmpc_optimization"  # Controller type:        ["objective", "optimization"]
  open_gripper_time: int = 15

BaseLLMConfigs = {
  "plan": PlanLLMConfig,
  "objective": ObjectiveLLMConfig,
  "optimization": OptimizationLLMConfig,
  "nmpc_objective": NMPCObjectiveLLMConfig,
  "nmpc_optimization": NMPCOptimizationLLMConfig
}
