import click
import git
import os

class Jit(object):

	def __init__(self):
		self.root = self.getRoot(os.getcwd())
		self.root_files = []
		if not self.root:
			print "Could not find a root directory."
			return

		self.root_files = os.listdir(self.root)
		return

	def getRoot(self, dir):
		"""
		Recursively look for directory containing git repos
		"""
		if self.isRepo(dir):
			return os.path.dirname(dir)
		elif len(dir) <= 1:
			return False
		else:
			return self.getRoot(os.path.dirname(dir))

	def getRepoRoot(self, repo_name):
		"""
		Get root directory for specified repo.
		"""
		return self.root + '/' + repo_name

	def getRepoName(self, repo):
		"""
		Find name for currently accessed repo.
		"""
		return os.path.basename(repo.working_dir)

	def getRepos(self):
		"""
		Get list of all accessible repos (based on current path).
		"""
		repos = []
		for dir in self.root_files:
			dir_path = self.getRepoRoot(dir)
			if self.isRepo(dir_path):
				repos.append(git.Repo(dir_path))

		return repos

	def isRepo(self, dir_path):
		"""
		Determine whether current directory is a repository root.
		"""
		return os.path.isdir(dir_path + '/.git')


	def getBranches(self, repo):
		"""
		Get list of branches for specified repository.
		"""
		branches = []
		for branch in repo.branches:
			if branch.name != 'master':
				branches.append(branch)

		return branches

	def formatActiveBranchOutput(self, repo):
		"""
		Format name of current repo branch.
		"""
		return self.getRepoName(repo).ljust(35) +  repo.active_branch.name

	def getDirtyRepos(self):
		"""
		Get list of repos with uncommitted changes.
		"""
		return [repo for repo in self.getRepos() if repo.is_dirty()]

	def findDirtyRepos(self, dirty_repos = None):
		"""
		Alert user of dirty repos.
		"""
		if dirty_repos is None:
			dirty_repos = self.getDirtyRepos()

		if dirty_repos:
			print "Please commit or stash your changes in the following repos."
			for repo in dirty_repos:
				print self.formatActiveBranchOutput(repo)
			return True
		return False;

	def getRelevantRepos(self, branch_name):
		"""
		Get repos with branch matching specified name.
		"""
		relevant_repos = []
		for repo in self.getRepos():
			for branch in repo.branches:
				if branch.name == branch_name:
					relevant_repos.append(repo)

		return relevant_repos

	def checkoutRelevantRepos(self, branch_name):
		"""
		Checkout repos with branch matching specified name.
		"""
		for repo in self.getRelevantRepos(branch_name):
			repo.git.checkout(branch_name)
			print self.formatActiveBranchOutput(repo)

	def allToMaster(self):
		"""
		Checkout master on all repos.
		"""
		if not self.findDirtyRepos():
			for repo in self.getRepos():
				repo.heads.master.checkout()

	def pullAll(self):
		"""
		Pull from remote on all repos.
		"""
		if not self.findDirtyRepos():
			for repo in self.getRepos():
				try:
					repo.remotes.origin.pull()
					click.echo("Pulled %s" % self.getRepoName(repo))
				except:
					click.echo("Could not pull %s" % self.getRepoName(repo))

	def displayUserRepos(self):
		"""
		Print all local branch names on all repos.
		"""
		for repo in self.getRepos():
			if (len(repo.branches) > 1):
				print self.getRepoName(repo)
			for branch in self.getBranches(repo):
				print branch.name.ljust(5)

	def displayCurrentBranches(self):
		"""
		Print current checked out branch on all repos.
		"""
		repos = self.getRepos()
		for repo in repos:
			print self.formatActiveBranchOutput(repo)

	def displayDirtyRepos(self):
		"""
		Display all repos with uncommited changes on checked out branch.
		"""
		for repo in self.getDirtyRepos():
			print self.formatActiveBranchOutput(repo)

	def displayRelevantRepos(self, branch_name):
		"""
		Print name of all repos with specified branch name.
		"""
		for repo in self.getRelevantRepos(branch_name):
			print self.formatActiveBranchOutput(repo)

@click.group()
def cli():
	"""jit allows you to interact with all git repositories within a directory in bulk."""
	pass

@cli.command()
def	all():
	"""Display all current branches."""
	jit = Jit()
	jit.displayCurrentBranches()

@cli.command()
def mine():
	"""Display all branches for all repos."""
	jit = Jit()
	jit.displayUserRepos()

@cli.command()
def dirty():
	"""Display all repos with uncommitted changes."""
	jit = Jit()
	jit.displayDirtyRepos()

@cli.command()
def master():
	"""Checkout master branch on all repos."""
	jit = Jit()
	jit.allToMaster()

@cli.command()
def pull():
	"""Pull from remote origin on all repos."""
	jit = Jit()
	jit.pullAll()

@click.command()
@click.argument('branch')
def show(branch):
	"""Show all repos that contain specified branch name."""
	jit = Jit()
	jit.displayRelevantRepos(branch)

@click.command()
@click.argument('branch')
def co(branch):
	"""Checkout specified branch in all repos where it exists."""
	jit = Jit()
	jit.checkoutRelevantRepos(branch)

cli.add_command(show)
cli.add_command(co)
