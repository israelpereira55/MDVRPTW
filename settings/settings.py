import json
from constants import Settings, Solomon

class SoftwareSettings:
  def check_solve_method(self, solve_method):
    if solve_method == 'ACO':
      return Settings.ACO
    else:
      return Settings.GRASP

  def check_cluster(self, cluster):
    if cluster == 'Urgencies' or cluster == 'urgencies':
      return Settings.Urgencies
    else:
      return Settings.KMeans

  def __init__(self, filename, print_settings=True):
    with open(filename) as file:
      data = json.load(file)
      
    self.seed = data['seed']
    self.cluster = self.check_cluster(data['clusterMethod'])
    cluster_string = "Urgencies" if self.cluster == Settings.Urgencies else 'KMeans' 

    self.solve_method = self.check_solve_method(data['solveMethod'])
    solve_method_string = "ACO" if self.solve_method == Settings.ACO else "GRASP"

    if print_settings:
      print("\n========== SOFTWARE SETTINGS ============\n"
            "Parameters\n" 
            f"  seed: {self.seed}\n" 
            f"  cluster method: {cluster_string}\n" 
            f"  solve method: {solve_method_string}\n" 
            "=========================================\n")


class GRASPSettings:
  def check_local_search(self, local_search):
    if local_search == 'VND':
      return Settings.VND
    else:
      return Settings.LS

  def __init__(self, filename, print_settings=True):
    with open(filename) as file:
      data = json.load(file)

    self.alpha = data['alpha']
    self.max_iterations = data['maxIterations']
    self.number_of_attempts = data['numberOfAttempts']
    self.local_search = self.check_local_search(data['localSearch'])
    local_search_string = "VND" if self.local_search == Settings.VND else 'LS' 

    if print_settings:
      print("============ GRASP SETTINGS =============\n"
            "Parameters\n" 
            f"  alpha: {self.alpha}\n" 
            f"  max_iterations: {self.max_iterations}\n" 
            f"  local search: {local_search_string}\n" 
            "=========================================\n")


class ACOSettings:
  def check_local_search(self, local_search):
    if local_search == 'VND':
      return Settings.VND
    else:
      return Settings.LS

  def __init__(self, filename, print_settings=True):
    with open(filename) as file:
      data = json.load(file)

    self.m = data['m']
    self.ro = data['ro']
    self.alpha = data['alpha']
    self.beta = data['beta']
    self.max_iterations = data['max_iterations']
    self.tau0 = data['tau0']
    self.Q = data['Q']

    self.local_search = self.check_local_search(data['localSearch'])
    local_search_string = "VND" if self.local_search == Settings.VND else 'LS' 

    if print_settings:
      print("============== ACO SETTINGS =============\n" 
            "Parameters\n" 
            f"  m: {self.m}\n" 
            f"  ro: {self.ro}\n" 
            f"  alpha: {self.alpha}\n" 
            f"  beta: {self.beta}\n" 
            f"  max_iterations: {self.max_iterations}\n" 
            f"  tau0: {self.tau0}\n" 
            f"  Q: {self.Q}\n" 
            f"  local search: {local_search_string}\n" 
            "=========================================\n")



class SolomonSettings:
  def check_init_criteria(self, init_criteria):
    if init_criteria == 'CLOSEST_TW':
      return Solomon.CLOSEST_TW
    else:
      return Solomon.FARTHEST_CLIENT

  def __init__(self, filename, print_settings=True):
    with open(filename) as file:
      data = json.load(file)

    self.alpha1 = data['alpha1']
    self.alpha2 = data['alpha2']
    self.mu = data['mu']
    self.lambdaa = data['lambda']

    self.init_criteria = self.check_init_criteria(data['initCriteria'])
    init_criteria_string = "CLOSEST_TW" if self.init_criteria == Solomon.CLOSEST_TW else 'FARTHEST_CLIENT' 

    if print_settings:
      print("=========== SOLOMON SETTINGS ============\n"
            "Parameters\n" 
            f"  init criteria: {init_criteria_string}\n" 
            f"  alpha1: {self.alpha1}\n" 
            f"  alpha2: {self.alpha2}\n" 
            f"  mu: {self.mu}\n" 
            f"  lambda: {self.lambdaa}\n" 
            "=========================================\n")