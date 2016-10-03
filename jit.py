import click
import git
import os

class Config(object):

	def __init__(self):
		self.root = os.getcwd()

pass_config = click.make_pass_decorator(Config, ensure=True)

class Jit():

	def __init__(self, root):
		self.root = root
		self.root_files = os.listdir(self.root)

	def getRepoRoot(self, repo_name):
		return self.root + repo_name

	def getRepoName(repo):
		return os.path.basename(repo.working_dir)

	def getRepos(self):
		repos = []
		for dir in self.root_files:
			dir_path = self.getRepoRoot(dir)
			if os.path.isdir(dir_path + '/.git'):
				repos.append(git.Repo(dir_path))

		return repos

	def getBranches(repo):
		branches = []
		for branch in repo.branches:
			if branch.name != 'master':
				branches.append(branch)

		return branches

	def formatActiveBranchOutput(self, repo):
		return self.getRepoName(repo).ljust(35) +  repo.active_branch.name

	def getDirtyRepos(self):
		 return [repo for repo in self.getRepos() if repo.is_dirty()]

	def handleDirtyRepos(self):
		dirty_repos = self.getDirtyRepos()
		if dirty_repos:
			print "Please commit or stash your changes in the following repos."
			for repo in dirty_repos:
				print self.formatActiveBranchOutput(repo)
			return True
		return False;

	def allToMaster(self):
		if not self.handleDirtyRepos():
			for repo in self.getRepos():
				repo.heads.master.checkout()

	def pullAll(self):
		if not self.handleDirtyRepos():
			for repo in self.getRepos():
				try:
					repo.remotes.origin.pull()
					click.echo("Pulled %s" % self.getRepoName(repo))
				except:
					click.echo("Could not pull %s" % self.getRepoName(repo))

	def displayUserRepos(self):
		for repo in self.getRepos():
			if (len(repo.branches) > 1):
				print self.getRepoName(repo)
			for branch in self.getBranches(repo):
				print branch.name.ljust(5)
				
	def displayCurrentBranches(self):
		repos = self.getRepos()
		for repo in repos:
			print self.formatActiveBranchOutput(repo)

	def displayDirtyRepos(self):
		for repo in self.getDirtyRepos():
			print self.formatActiveBranchOutput(repo)

@click.group()
@pass_config
def cli(config):
	"""jit allows you to interact with all git repositories within a directory in bulk."""
	pass

@cli.command()
@click.option('--update', is_flag=True, help="Set the root directory.")
@pass_config
def root(config, update):
	"""View/set the root directory."""
	config_dir = click.get_app_dir('jit')
	config_path = config_dir + '/config.txt'

	if not os.path.exists(config_path):
		os.makedirs(config_dir)

	config_file = open(config_path, 'w+')
	current_dir = os.getcwd()

	if os.path.isfile(config_path):
		root = config_file.read()
		print "root {}".format(root)
	else:
		root = current_dir
	
	if update:
		print "current dir {}".format(current_dir)
		config_file.write(current_dir)
	else:
		if root:
			print root
		else:
			print current_dir

	config_file.close()

@cli.command()
@pass_config
def	all(config):
	"""Display all current branches."""
	jit = Jit(config.root)
	jit.displayCurrentBranches()

@cli.command()
@pass_config
def mine(config):
	"""Display all branches for all repos."""
	jit = Jit(config.root)
	Jit.displayUserRepos()   

@cli.command()
@pass_config
def dirty(config):
	"""Display all repos with uncommitted changes."""
	jit = Jit(config.root)
	Jit.displayDirtyRepos()

@cli.command()
@pass_config
def master(config):
	"""Checkout master branch on all repos."""
	jit = Jit(config.root)
	jit.allToMaster()

@cli.command()
@pass_config
def pull(config):
	"""Pull from remote origin on all repos."""
	jit = Jit(config.root)
	jit.pullAll()
