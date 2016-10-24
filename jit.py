import click
import git
import os

class Jit():

	def __init__(self):
		self.root = self.getRoot(os.getcwd())
		if not self.root:
			print "Could not find a root directory."
			return

		self.root_files = os.listdir(self.root)
		return

	def getRoot(self, dir):
		if self.isRepo(dir):
			return os.path.dirname(dir)
		elif len(dir) < 1:
			return False
		else:
			return self.getRoot(os.path.dirname(dir))

	def getRepoRoot(self, repo_name):
		return self.root + '/' + repo_name

	def getRepoName(self, repo):
		return os.path.basename(repo.working_dir)

	def getRepos(self):
		repos = []
		for dir in self.root_files:
			dir_path = self.getRepoRoot(dir)
			if self.isRepo(dir_path):
				repos.append(git.Repo(dir_path))

		return repos

	def isRepo(self, dir_path):
		return os.path.isdir(dir_path + '/.git')


	def getBranches(self, repo):
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
