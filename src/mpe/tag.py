import numpy as np
from utils import evaluate_policy
from agent import LMPCAgent, NNAgent
from pettingzoo.mpe import simple_tag_v2

n_episodes = 20000
n_frames_per_episode = 100
n_eval_episodes = 5
num_adversaries = 1
num_obstacles = 2

# init env
env = simple_tag_v2.parallel_env(num_adversaries=num_adversaries, num_obstacles=num_obstacles, max_cycles=n_frames_per_episode, continuous_actions=True, render_mode='rgb')
env.reset()

# init LMPC agents (adversaries) and learning-based agent
nn_agent = NNAgent(input_size=4+2*num_obstacles+2*num_adversaries, output_size=4)
adversary_agents = LMPCAgent(env.agents[:-1], "tag")


for i in range(n_episodes):
  obs = env.reset()
  trajectory = []
  while env.agents:
    actions = adversary_agents.act(obs)
    action, log_prob = nn_agent(obs["agent_0"])
    actions["agent_0"] = np.concatenate(([1e-5], action), dtype=np.float32)
    next_state, rewards, terminations, truncations, infos = env.step(actions)
    if abs(rewards["agent_0"]) < 1: rewards["agent_0"] = 1
    trajectory.append({"state":obs["agent_0"], "action":actions["agent_0"], "reward":rewards["agent_0"], "log_prob":log_prob})
    obs = next_state

  if i%20==0:
    evaluate_policy(nn_agent, adversary_agents, env, n_eval_episodes)

  policy_loss = nn_agent.train(trajectory)

env.close()