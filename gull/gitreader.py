
from git import Repo

class GitReader(object):
    '''
    GitPython repository reader.
    It expose easier to use methods in order to play / navigate though git
    repository.
    '''

    _instance = None

    def __init__(self, repo_path):
        '''
        Init git.Repo
        '''
        self.repo = Repo(repo_path)
        self.git = self.repo.git


    def _parse_branches(self, text):
        return [b.strip() for b in text.replace('*', '').splitlines()]


    @property
    def branches(self):
        '''
        List all branches in repository
        '''
        return [b.strip() for b in self._parse_branches(self.git.branch())]


    @property
    def currentcommit(self):
        '''
        Get current revision commit.
        '''
        return self.git.rev_parse('HEAD').strip()


    def shorten(self, commitid):
        return self.git.rev_parse('--short', commitid).strip()

    def firstcommit(self, branch):
        '''
        Get first commit hash of given branch
        '''
        return self.git.log('master..{}'.format(branch), oneline=True, reverse=True).split('\n')[0][0:7]


    def lastcommit(self, branch):
        '''
        Get last commit hash of given branch
        '''
        return self.git.log('master..{}'.format(branch), oneline=True).split('\n')[0][0:7]


    def listfiles(self, branch=None, commit=None):
        '''
        List files (on filesystem) within last commit of `branch` or `commit`.
        '''
        if commit is None and branch is None:
            commit = self.currentcommit
        elif commit is None and branch is not None:
            commit = self.lastcommit(branch)

        self.git.checkout(commit)
        return [f.strip() for f in self.git.ls_files().splitlines()]


    def getfile(self, file_path, branch=None, commit=None):
        '''
        Get file's content of `file_path` within last commit of `branch` or
        `commit`.
        '''
        if commit is None and branch is None:
            commit = self.currentcommit
        elif commit is None and branch is not None:
            commit = self.lastcommit(branch)

        return self.git.show('{}:{}'.format(commit, file_path))


    def getcommit(self, commit=None):
        '''
        Get commit's content (description + meta)
        '''
        return self.git.show('--quiet', commit)


    # XXX
    def getbranch(self, commit):
        '''
        Get source branch of a commit
        TODO: Check which branch is the first
        '''
        branches = self._parse_branches(self.git.branch('--contains', commit))
        branches = [b for b in branches if "HEAD" not in b]
        return branches[0]


    @classmethod
    def instanciate(cls, repo_path):
        '''
        Instanciate class as class attribute.
        It allow to manipulate one single instance of self, really useful when
        handling a Git repository and switching revisions.
        '''
        cls._instance = cls(repo_path)
        return cls._instance


    @classmethod
    def get_instance(cls):
        '''
        Get instance of class.
        Instanciate itself if needed.

        This should be the only way to access GitReader instance.
        '''
        if cls._instance is not None:
            return cls._instance
        else:
            raise AttributeError('cls._instance not instanciated.')

