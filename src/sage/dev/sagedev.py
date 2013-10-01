- David Roe, Frej Drejhammar, Julian Rueth, Martin Raum, Nicolas M. Thiery, R.,
import os
import urllib, urlparse
import re

from patch import MercurialPatchMixin
from sage.env import TRAC_SERVER_URI
# the name of the branch which holds the vanilla clone of sage
USER_BRANCH = re.compile(r"^u/([^/]+)/")


#
# The first line should contain a short summary of your changes, the
# following lines should contain a more detailed description. Lines
# starting with '#' are ignored.
class SageDev(MercurialPatchMixin):
      stored in ``DOT_SAGE/devrc``.
        def move_legacy_saving_dict(key, old_file, new_file):
            '''
            We used to have these files in DOT_SAGE - this is not a good idea
            because a user might have multiple copies of sage which should each
            have their own set of files.

            This method moves an existing file mentioned in the config to its
            new position to support repositories created earlier.
            '''
            import sage.doctest
            if sage.doctest.DOCTEST_MODE:
                return
            import shutil
            if not os.path.exists(new_file) and os.path.exists(old_file):
                shutil.move(old_file, new_file)
                self._UI.show('The developer scripts used to store some of their data in "{0}". This file has now moved to "{1}". I moved "{0}" to "{1}". This might cause trouble if this is a fresh clone of the repository in which you never used the developer scripts before. In that case you should manually delete "{1}" now.'.format(old_file, new_file))
            if key in self.config['sagedev']:
                del self.config['sagedev'][key]

        ticket_file = os.path.join(self.git._dot_git, 'branch_to_ticket')
        move_legacy_saving_dict('ticketfile', self.config['sagedev'].get('ticketfile', os.path.join(DOT_SAGE, 'branch_to_ticket')), ticket_file)
        branch_file = os.path.join(self.git._dot_git, 'ticket_to_branch')
        move_legacy_saving_dict('branchfile', self.config['sagedev'].get('branchfile', os.path.join(DOT_SAGE, 'ticket_to_branch')), branch_file)
        dependencies_file = os.path.join(self.git._dot_git, 'dependencies')
        move_legacy_saving_dict('dependenciesfile', self.config['sagedev'].get('dependenciesfile', os.path.join(DOT_SAGE, 'dependencies')), dependencies_file)
        remote_branches_file = os.path.join(self.git._dot_git, 'remote_branches')
        move_legacy_saving_dict('remotebranchesfile', self.config['sagedev'].get('remotebranchesfile', os.path.join(DOT_SAGE, 'remote_branches')), remote_branches_file)
    def create_ticket(self):
        Create a new ticket on trac.
            :meth:`checkout`, :meth:`pull`, :meth:`edit_ticket`
            Created ticket #1 at https://trac.sagemath.org/1.

            Created ticket #2 at https://trac.sagemath.org/2.
        This fails if the internet connection is broken::
            sage: UI.append("Summary: ticket7\ndescription")
            sage: dev.create_ticket()
        """
        try:
            ticket = self.trac.create_ticket_interactive()
        except OperationCancelledError:
            self._UI.debug("Ticket creation aborted.")
            raise
        except TracConnectionError as e:
            self._UI.error("A network error ocurred, ticket creation aborted.")
            raise
        ticket_url = urlparse.urljoin(self.trac._config.get('server', TRAC_SERVER_URI), str(ticket))
        self._UI.show("Created ticket #{0} at {1}.".format(ticket, ticket_url))
        self._UI.info('To start work on ticket #{0}, create a new local branch'
                      ' for this ticket with "{1}".'
                      .format(ticket, self._format_command("checkout", ticket=ticket)))
        return ticket
    def checkout(self, ticket=None, branch=None, base=''):
        r"""
        Checkout another branch.
        If ``ticket`` is specified, and ``branch`` is an existing local branch,
        then ``ticket`` will be associated to it, and ``branch`` will be
        checked out into the working directory.
        Otherwise, if there is no local branch for ``ticket``, the branch
        specified on trac will be pulled to ``branch`` unless ``base`` is
        set to something other than the empty string ``''``. If the trac ticket
        does not specify a branch yet or if ``base`` is not the empty string,
        then a new one will be created from ``base`` (per default, the master
        branch).
        If ``ticket`` is not specified, then checkout the local branch
        ``branch`` into the working directory.
        INPUT:
        - ``ticket`` -- a string or an integer identifying a ticket or ``None``
          (default: ``None``)
        - ``branch`` -- a string, the name of a local branch; if ``ticket`` is
          specified, then this defaults to ticket/``ticket``.
        - ``base`` -- a string or ``None``, a branch on which to base a new
          branch if one is going to be created (default: the empty string
          ``''`` to create the new branch from the master branch), or a ticket;
          if ``base`` is set to ``None``, then the current ticket is used. If
          ``base`` is a ticket, then the corresponding dependency will be
          added. Must be ``''`` if ``ticket`` is not specified.
        .. SEEALSO::
            :meth:`pull`, :meth:`create_ticket`, :meth:`vanilla`
        TESTS:
        Set up a single user for doctesting::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
        Create a few branches::
            sage: dev.git.silent.branch("branch1")
            sage: dev.git.silent.branch("branch2")
        Checking out a branch::
            sage: dev.checkout(branch="branch1")
            sage: dev.git.current_branch()
            'branch1'
        Create a ticket and checkout a branch for it::
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: dev.git.current_branch()
            'ticket/1'
        """
        if ticket is not None:
            self.checkout_ticket(ticket=ticket, branch=branch, base=base)
        elif branch is not None:
            if base != '':
                raise SageDevValueError("base must not be specified if no ticket is specified.")
            self.checkout_branch(branch=branch)
        else:
            raise SageDevValueError("at least one of ticket or branch must be specified.")
    def checkout_ticket(self, ticket, branch=None, base=''):
        Checkout the branch associated to ``ticket``.
        associated to it, and ``branch`` will be checked out into the working directory.
        specified on trac will be pulled to ``branch`` unless ``base`` is
        set to something other than the empty string ``''``. If the trac ticket
        does not specify a branch yet or if ``base`` is not the empty string,
        then a new one will be created from ``base`` (per default, the master
        branch).
        - ``base`` -- a string or ``None``, a branch on which to base a new
          branch if one is going to be created (default: the empty string
          ``''`` to create the new branch from the master branch), or a ticket;
          if ``base`` is set to ``None``, then the current ticket is used. If
          ``base`` is a ticket, then the corresponding dependency will be
          added.

            :meth:`pull`, :meth:`create_ticket`, :meth:`vanilla`
        Alice tries to checkout ticket #1 which does not exist yet::
            sage: alice.checkout(ticket=1)
            ValueError: "1" is not a valid ticket name or ticket does not exist on trac.
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: bob.checkout(ticket=1)
        Now alice can check it out, even though there is no branch on the
            sage: alice.checkout(ticket=1)
        If Bob commits something to the ticket, a ``checkout`` by Alice
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.checkout(ticket=1)
        If Alice had not checked that ticket out before, she would of course
            sage: alice.checkout(ticket=1) # ticket #1 refers to the non-existant branch 'ticket/1'
            Ticket #1 refers to the non-existant local branch "ticket/1". If you have not manually interacted with git, then this is a bug in sagedev. Removing the association from ticket #1 to branch "ticket/1".
        Checking out a ticket with untracked files::
            Created ticket #2 at https://trac.sagemath.org/2.
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
        Checking out a ticket with untracked files which make a checkout
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
            This happened while executing "git -c user.email=doc@test.test -c
            user.name=alice checkout ticket/1".
        Checking out a ticket with uncommited changes::
            sage: open("tracked", "w").close()
            sage: alice.checkout(ticket=2)
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Keep/stash] d
        Now follow some single user tests to check that the parameters are interpreted correctly::
            sage: dev._wrap("_dependencies_for_ticket")
        First, create some tickets::
            sage: UI.append("Summary: ticket1\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: UI.append("Summary: ticket2\ndescription")
            sage: dev.create_ticket()
            Created ticket #2 at https://trac.sagemath.org/2.
            2
            sage: dev.checkout(ticket=2)
            sage: dev.git.silent.commit(allow_empty=True, message="second commit")
            sage: dev.git.commit_for_branch('ticket/2') != dev.git.commit_for_branch('ticket/1')
            True
        Check that ``base`` works::
            sage: UI.append("Summary: ticket3\ndescription")
            sage: dev.create_ticket()
            Created ticket #3 at https://trac.sagemath.org/3.
            3
            sage: dev.checkout(ticket=3, base=2)
            sage: dev.git.commit_for_branch('ticket/3') == dev.git.commit_for_branch('ticket/2')
            True
            sage: dev._dependencies_for_ticket(3)
            (2,)
            sage: UI.append("Summary: ticket4\ndescription")
            sage: dev.create_ticket()
            Created ticket #4 at https://trac.sagemath.org/4.
            4
            sage: dev.checkout(ticket=4, base='ticket/2')
            sage: dev.git.commit_for_branch('ticket/4') == dev.git.commit_for_branch('ticket/2')
            True
            sage: dev._dependencies_for_ticket(4)
            ()
        In this example ``base`` does not exist::
            sage: UI.append("Summary: ticket5\ndescription")
            sage: dev.create_ticket()
            Created ticket #5 at https://trac.sagemath.org/5.
            5
            sage: dev.checkout(ticket=5, base=1000)
            ValueError: "1000" is not a valid ticket name or ticket does not exist on trac.
        In this example ``base`` does not exist locally::
            sage: UI.append("Summary: ticket6\ndescription")
            sage: dev.create_ticket()
            Created ticket #6 at https://trac.sagemath.org/6.
            6
            sage: dev.checkout(ticket=6, base=5)
            ValueError: Branch field is not set for ticket #5 on trac.
        Creating a ticket when in detached HEAD state::
            sage: dev.git.super_silent.checkout('HEAD', detach=True)
            sage: UI.append("Summary: ticket detached\ndescription")
            sage: dev.create_ticket()
            Created ticket #7 at https://trac.sagemath.org/7.
            7
            sage: dev.checkout(ticket=7)
            sage: dev.git.current_branch()
            'ticket/7'
        Creating a ticket when in the middle of a merge::
            sage: dev.git.super_silent.checkout('ticket/7')
            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            Created ticket #8 at https://trac.sagemath.org/8.
            8
            sage: UI.append("n")
            sage: dev.checkout(ticket=8)
            Your repository is in an unclean state. It seems you are in the middle of a
            merge of some sort. To complete this command you have to reset your repository
            to a clean state. Do you want me to reset your repository? (This will discard
            many changes which are not commited.) [yes/No] n
            Could not check out branch "ticket/8" because your working directory is not
            in a clean state.
        Creating a ticket with uncommitted changes::

            sage: open('tracked', 'w').close()
            sage: dev.git.silent.add('tracked')
            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            Created ticket #9 at https://trac.sagemath.org/9.
            9

        The new branch is based on master which is not the same commit
        as the current branch ``ticket/7``, so it is not a valid
        option to ``'keep'`` changes::

            sage: UI.append("cancel")
            sage: dev.checkout(ticket=9)
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            Could not check out branch "ticket/9" because your working directory is not
            clean.

        Finally, in this case we can keep changes because the base is
        the same commit as the current branch

            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            Created ticket #10 at https://trac.sagemath.org/10.
            10
            sage: UI.append("keep")
            sage: dev.checkout(ticket=10, base='ticket/7')
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Keep/stash] keep
        """
        self._check_ticket_name(ticket, exists=True)
        ticket = self._ticket_from_ticket_name(ticket)

        # if branch points to an existing branch make it the ticket's branch and check it out
        if branch is not None and self._is_local_branch_name(branch, exists=True):
            if base != MASTER_BRANCH:
                raise SageDevValueError("base must not be specified if branch is an existing branch")
            if branch == MASTER_BRANCH:
                raise SageDevValueError("branch must not be the master branch")

            self._set_local_branch_for_ticket(ticket, branch)
            self._UI.debug('The branch for ticket #{0} is now "{1}".'.format(ticket, branch))
            self._UI.debug('Now checking out branch "{0}".'.format(branch))
            self.checkout_branch(branch)
            return

        # if there is a branch for ticket locally, check it out
        if branch is None:
            if self._has_local_branch_for_ticket(ticket):
                branch = self._local_branch_for_ticket(ticket)
                self._UI.debug('Checking out branch "{0}".'.format(branch))
                self.checkout_branch(branch)
                return
            else:
                branch = self._new_local_branch_for_ticket(ticket)

        # branch does not exist, so we have to create a new branch for ticket
        # depending on the value of base, this will either be base or a copy of
        # the branch mentioned on trac if any
        dependencies = self.trac.dependencies(ticket)
        if base is None:
            base = self._current_ticket()
        if base is None:
            raise SageDevValueError('currently on no ticket, "base" must not be None')
        if self._is_ticket_name(base):
            base = self._ticket_from_ticket_name(base)
            dependencies = [base] # we create a new branch for this ticket - ignore the dependencies which are on trac
            base = self._local_branch_for_ticket(base, pull_if_not_found=True)

        remote_branch = self.trac._branch_for_ticket(ticket)
        try:
            if base == '':
                base = MASTER_BRANCH
                if remote_branch is None: # branch field is not set on ticket
                    # create a new branch off master
                    self._UI.debug('The branch field on ticket #{0} is not set. Creating a new branch "{1}" off the master branch "{2}".'.format(ticket, branch, MASTER_BRANCH))
                    self.git.silent.branch(branch, MASTER_BRANCH)
                else:
                    # pull the branch mentioned on trac
                    if not self._is_remote_branch_name(remote_branch, exists=True):
                        self._UI.error('The branch field on ticket #{0} is set to "{1}". However, the branch "{1}" does not exist. Please set the field on trac to a field value.'.format(ticket, remote_branch))
                        raise OperationCancelledError("remote branch does not exist")
                    try:
                        self.pull(remote_branch, branch)
                        self._UI.debug('Created a new branch "{0}" based on "{1}".'.format(branch, remote_branch))
                    except:
                        self._UI.error('Could not check out ticket #{0} because the remote branch "{1}" for that ticket could not be pulled.'.format(ticket, remote_branch))
                        raise
            else:
                self._check_local_branch_name(base, exists=True)
                if remote_branch is not None:
                    if not self._UI.confirm('Creating a new branch for #{0} based on "{1}". The trac ticket for #{0} already refers to the branch "{2}". As you are creating a new branch for that ticket, it seems that you want to ignore the work that has already been done on "{2}" and start afresh. Is this what you want?'.format(ticket, base, remote_branch), default=False):
                        command = ""
                        if self._has_local_branch_for_ticket(ticket):
                            command += self._format_command("abandon", self._local_branch_for_ticket(ticket)) + "; "
                        command += self._format_command("checkout", ticket=ticket)
                        self._UI.info('To work on a fresh copy of "{0}", use "{1}".'.format(remote_branch, command))
                        raise OperationCancelledError("user requested")

                self._UI.debug('Creating a new branch for #{0} based on "{1}".'.format(ticket, base))
                self.git.silent.branch(branch, base)
        except:
            if self._is_local_branch_name(branch, exists=True):
                self._UI.debug('Deleting local branch "{0}".')
                self.git.super_silent.branch(branch, D=True)
            raise

        self._set_local_branch_for_ticket(ticket, branch)
        if dependencies:
            self._UI.debug("Locally recording dependency on {0} for #{1}.".format(", ".join(["#"+str(dep) for dep in dependencies]), ticket))
            self._set_dependencies_for_ticket(ticket, dependencies)
        self._set_remote_branch_for_branch(branch, self._remote_branch_for_ticket(ticket)) # set the remote branch for branch to the default u/username/ticket/12345
        self._UI.debug('Checking out to newly created branch "{0}".'.format(branch))
        self.checkout_branch(branch)

    def checkout_branch(self, branch):
        r"""
        Checkout to the local branch ``branch``.

        INPUT:

        - ``branch`` -- a string, the name of a local branch

        TESTS:

        Set up a single user for doctesting::

            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()

        Create a few branches::

            sage: dev.git.silent.branch("branch1")
            sage: dev.git.silent.branch("branch2")

        Checking out a branch::

            sage: dev.checkout(branch="branch1")
            sage: dev.git.current_branch()
            'branch1'

        The branch must exist::

            sage: dev.checkout(branch="branch3")
            ValueError: Branch "branch3" does not exist locally.

        Checking out branches with untracked files::

            sage: open("untracked", "w").close()
            sage: dev.checkout(branch="branch2")

        Checking out a branch with uncommitted changes::

            sage: open("tracked", "w").close()
            sage: dev.git.silent.add("tracked")
            sage: dev.git.silent.commit(message="added tracked")
            sage: with open("tracked", "w") as f: f.write("foo")
            sage: UI.append("cancel")
            sage: dev.checkout(branch="branch1")
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            Could not check out branch "branch1" because your working directory is not
            clean.

        We can stash uncommitted changes::

            sage: UI.append("s")
            sage: dev.checkout(branch="branch1")
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] s
            Your changes have been moved to the git stash stack. To re-apply your changes
            later use "git stash apply".

        And retrieve the stashed changes later::

            sage: dev.checkout(branch='branch2')
            sage: dev.git.echo.stash('apply')
            # On branch branch2
            # Changes not staged for commit:
            #   (use "git add <file>..." to update what will be committed)
            #   (use "git checkout -- <file>..." to discard changes in working directory)
            #
            #   modified:   tracked
            #
            # Untracked files:
            #   (use "git add <file>..." to include in what will be committed)
            #
            #   untracked
            no changes added to commit (use "git add" and/or "git commit -a")

        Or we can just discard the changes::

            sage: UI.append("discard")
            sage: dev.checkout(branch="branch1")
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] discard

        Checking out a branch when in the middle of a merge::

            sage: dev.git.super_silent.checkout('-b','merge_branch')
            sage: with open('merge', 'w') as f: f.write("version 0")
            sage: dev.git.silent.add('merge')
            sage: dev.git.silent.commit('-m','some change')
            sage: dev.git.super_silent.checkout('branch1')
            sage: with open('merge', 'w') as f: f.write("version 1")
            sage: dev.git.silent.add('merge')
            sage: dev.git.silent.commit('-m','conflicting change')
            sage: from sage.dev.git_error import GitError
            sage: try:
            ....:     dev.git.silent.merge('merge_branch')
            ....: except GitError: pass
            sage: UI.append('n')
            sage: dev.checkout(branch='merge_branch')
            Your repository is in an unclean state. It seems you are in the middle of a
            merge of some sort. To complete this command you have to reset your repository
            to a clean state. Do you want me to reset your repository? (This will discard
            many changes which are not commited.) [yes/No] n
            Could not check out branch "merge_branch" because your working directory is not
            in a clean state.
            sage: dev.git.reset_to_clean_state()

        Checking out a branch when in a detached HEAD::

            sage: dev.git.super_silent.checkout('branch2', detach=True)
            sage: dev.checkout(branch='branch1')
            sage: dev.checkout(branch='branch1')
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] discard
        Checking out a branch with untracked files that would be overwritten by
        the checkout::
            sage: dev.checkout(branch='branch2')
            This happened while executing "git -c user.email=doc@test.test -c
            user.name=doctest checkout branch2".
            error: The following untracked working tree files would be overwritten
            by checkout:
            self._UI.error('Could not check out branch "{0}" because your working directory is not in a clean state.'
                           .format(branch))
            self._UI.info('To checkout "{0}", use "{1}".'.format(branch, self._format_command("checkout",branch=branch)))
            raise

        current_commit = self.git.commit_for_ref('HEAD')
        target_commit = self.git.commit_for_ref(branch)
        try:
            self.clean(error_unless_clean=(current_commit != target_commit))
        except OperationCancelledError:
            self._UI.error('Could not check out branch "{0}" because your working directory is not clean.'.format(branch))
            # this leaves locally modified files intact (we only allow this to happen if current_commit == target_commit
    def pull(self, ticket_or_remote_branch=None, branch=None):
        Pull ``ticket_or_remote_branch`` to ``branch``.
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: alice.checkout(ticket=1)
        Bob attempts to pull for the ticket but fails because there is no
            sage: bob.pull(1)
            sage: bob.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
        Bob pulls the changes for ticket 1::
            sage: bob.pull()
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
        Alice can now pull the changes by Bob without the need to merge
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            Merge branch 'u/bob/ticket/1' of ... into ticket/1
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
        Now, the pull fails; one would have to use :meth:`merge`::
            sage: alice._UI.append("abort")
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            There was an error during the merge. Most probably there were conflicts when merging. The following should make it clear which files are affected:
            Auto-merging alices_file
            CONFLICT (add/add): Merge conflict in alices_file
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
        Undo the latest commit by alice, so we can pull again::
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            sage: alice._UI.append("abort")
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            There was an error during the merge. Most probably there were conflicts when merging. The following should make it clear which files are affected:
            Updating ...
            error: The following untracked working tree files would be overwritten by merge:
                bobs_other_file
            Please move or remove them before you can merge.
            Aborting
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
                raise SageDevValueError("branch must be None")

        # merge into the current branch if ticket_or_remote_branch refers to the current ticket
        if branch is None and ticket_or_remote_branch is not None and self._is_ticket_name(ticket_or_remote_branch) and self._ticket_from_ticket_name(ticket_or_remote_branch) == self._current_ticket():
            raise SageDevValueError('No "ticket_or_remote_branch" specified to pull.')
        self._UI.debug('Fetching remote branch "{0}" into "{1}".'.format(remote_branch, branch))
            self.merge(remote_branch, pull=True)
                self.git.super_silent.fetch(self.git._repository_anonymous, "{0}:{1}".format(remote_branch, branch))
                # then just nothing happened and we can abort the pull
                e.explain = 'Fetching "{0}" into "{1}" failed.'.format(remote_branch, branch)
                    e.advice = 'You can try to use "{2}" to checkout "{1}" and then use "{3}" to resolve these conflicts manually.'.format(remote_branch, branch, self._format_command("checkout",branch=branch), self._format_command("merge",remote_branch,pull=True))
                    e.explain += "We did not expect this case to occur.  If you can explain your context in sage.dev.sagedev it might be useful to others."
        This is most akin to mercurial's commit command, not git's,
        since we do not require users to add files.
            - :meth:`push` -- Push changes to the remote server.  This
              is the next step once you've committed some changes.
            - :meth:`diff` -- Show changes that will be committed.
            sage: dev.git.super_silent.checkout('-b', 'branch1')
            sage: dev._UI.extend(["added tracked", "y", "y", "y"])
            Do you want to add "tracked"? [yes/No] y
            Do you want to commit your changes to branch "branch1"? I will prompt you for a commit message if you do. [Yes/no] y
            Do you want to commit your changes to branch "branch1"? I will prompt you for a commit message if you do. [Yes/no] y
            self._UI.info('Use "{0}" to checkout a branch.'.format(self._format_command("checkout")))
            self._UI.debug('Committing pending changes to branch "{0}".'.format(branch))
                            if self._UI.confirm('Do you want to add "{0}"?'.format(file), default=False):
                    self.git.echo.add(patch=True)
                    self.git.echo.add(self.git._src, update=True)
                if not self._UI.confirm('Do you want to commit your changes to branch "{0}"?{1}'.format(branch, " I will prompt you for a commit message if you do." if message is None else ""), default=True):
                    self._UI.info('If you want to commit to a different branch/ticket, run "{0}" first.'.format(self._format_command("checkout")))
                if message is None:
                    from tempfile import NamedTemporaryFile
                    commit_message = NamedTemporaryFile()
                    commit_message.write(COMMIT_GUIDE)
                    commit_message.flush()
                    self._UI.edit(commit_message.name)
                    message = "\n".join([line for line in open(commit_message.name).read().splitlines() if not line.startswith("#")]).strip()
                self._UI.debug("A commit has been created.")
                self._UI.debug("Not creating a commit.")
                raise
            except:
                self._UI.error("No commit has been created.")
            - :meth:`push` -- To push changes after setting the remote
              branch
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
                self._UI.info('Checkout a branch with "{0}" or specify branch explicitly.'.format(self._format_command('checkout')))
        # If we add restrictions on which branches users may push to, we should append them here.
        m = USER_BRANCH.match(remote_branch)
        if remote_branch == 'master' or m and m.groups()[0] != self.trac._username:
            self._UI.warning('The remote branch "{0}" is not in your user scope. You might not have permission to push to that branch. Did you mean to set the remote branch to "u/{1}/{0}"?'.format(remote_branch, self.trac._username))
    def push(self, ticket=None, remote_branch=None, force=False):
        Push the current branch to the Sage repository.
          set to ``remote_branch`` after the current branch has been pushed there.
          branch to push to; if ``None``, then a default is chosen
        - ``force`` -- a boolean (default: ``False``), whether to push if
            - :meth:`commit` -- Save changes to the local repository.
            - :meth:`pull` -- Update a ticket with changes from the remote
              repository.
        TESTS:
        Alice tries to push to ticket 1 which does not exist yet::
            sage: alice.push(ticket=1)
            ValueError: "1" is not a valid ticket name or ticket does not exist on trac.
        Alice creates ticket 1 and pushes some changes to it::
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
        Now Bob can check that ticket out and push changes himself::
            sage: bob.checkout(ticket=1)
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
        Now Alice can pull these changes::
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
        After Alice pushed her changes, Bob can not set the branch field anymore::
            sage: alice.push()
            I will now push the following new commits to the remote branch "u/alice/ticket/1":
            I will now change the branch field of ticket #1 from its current value "u/bob/ticket/1" to "u/alice/ticket/1". Is this what you want? [Yes/no] y
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            Not setting the branch field for ticket #1 to "u/bob/ticket/1" because "u/bob/ticket/1" and the current value of the branch field "u/alice/ticket/1" have diverged.
            sage: bob.pull()
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            sage: bob.push(2)
            ValueError: "2" is not a valid ticket name or ticket does not exist on trac.
            Created ticket #2 at https://trac.sagemath.org/2.
            sage: bob.checkout(ticket=2)
            sage: bob.checkout(ticket=1)
            sage: bob.push(2)
            You are trying to push the branch "ticket/1" to "u/bob/ticket/2" for ticket #2.
            However, your local branch for ticket #2 seems to be "ticket/2". Do you really
            want to proceed? [yes/No] y
            The branch "u/bob/ticket/2" does not exist on the remote server yet. Do you want
            to create the branch? [Yes/no] y
            sage: bob.push(remote_branch="u/bob/branch1")
            The branch "u/bob/branch1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/bob/ticket/1" to "u/bob/branch1". Is this what you want? [Yes/no] y

        Check that dependencies are pushed correctly::
            sage: bob.merge(2)
            Merging the remote branch "u/bob/ticket/2" into the local branch "ticket/1".
            Added dependency on #2 to #1.
            sage: bob._UI.append("y")
            sage: bob.push()
            I will now change the branch field of ticket #1 from its current value
            "u/bob/branch1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            Uploading your dependencies for ticket #1: "" => "#2"
            sage: bob._sagedev._set_dependencies_for_ticket(1,())
            sage: bob._UI.append("keep")
            sage: bob.push()
            According to trac, ticket #1 depends on #2. Your local branch depends on no
            tickets. Do you want to upload your dependencies to trac? Or do you want to
            download the dependencies from trac to your local branch? Or do you want to keep
            your local dependencies and the dependencies on trac in its current state?
            [upload/download/keep] keep
            sage: bob._UI.append("download")
            sage: bob.push()
            According to trac, ticket #1 depends on #2. Your local branch depends on no
            tickets. Do you want to upload your dependencies to trac? Or do you want to
            download the dependencies from trac to your local branch? Or do you want to keep
            your local dependencies and the dependencies on trac in its current state?
            [upload/download/keep] download
            sage: bob.push()
            self._UI.error("Cannot push while in detached HEAD state.")
            raise OperationCancelledError("cannot push while in detached HEAD state")
                if user_confirmation or self._UI.confirm('You are trying to push the branch "{0}" to "{1}" for ticket #{2}. However, your local branch for ticket #{2} seems to be "{3}". Do you really want to proceed?'.format(branch, remote_branch, ticket, self._local_branch_for_ticket(ticket)), default=False):
                    self._UI.info('Use "{2}" To permanently set the branch associated to ticket #{0} to "{1}".'
                                  .format(ticket, branch, self._format_command("checkout",ticket=ticket,branch=branch)))
                if user_confirmation or self._UI.confirm('You are trying to push the branch "{0}" to "{1}" for ticket #{2}. However, that branch is associated to ticket #{3}. Do you really want to proceed?'.format(branch, remote_branch, ticket, self._ticket_for_local_branch(branch))):
                    self._UI.info('To permanently set the branch associated to ticket #{0} to "{1}", use "{2}". To create a new branch from "{1}" for #{0}, use "{3}" and "{4}".'.format(ticket, branch, self._format_command("checkout",ticket=ticket,branch=branch), self._format_command("checkout",ticket=ticket), self._format_command("merge", branch=branch)))
        self._UI.debug('Pushing your changes in "{0}" to "{1}".'.format(branch, remote_branch))
                if not self._UI.confirm('The branch "{0}" does not exist on the remote server yet. Do you want to create the branch?'.format(remote_branch), default=True):
                self.git.super_silent.fetch(self.git._repository_anonymous, remote_branch)
                    self._UI.error('Not pushing your changes because they would discard some of the commits on the remote branch "{0}".'.format(remote_branch))
                    self._UI.info('If this is really what you want, use "{0}" to push your changes.'.format(self._format_command("push",ticket=ticket,remote_branch=remote_branch,force=True)))
                self._UI.info('Not pushing your changes because the remote branch "{0}" is idential to your local branch "{1}". Did you forget to commit your changes with "{2}"?'.format(remote_branch, branch, self._format_command("commit")))
                            if not self._UI.confirm('I will now push the following new commits to the remote branch "{0}":\n{1}Is this what you want?'.format(remote_branch, commits), default=True):
                    self._upload_ssh_key() # make sure that we have access to the repository
            self._UI.debug('Changes in "{0}" have been pushed to "{1}".'.format(branch, remote_branch))
            self._UI.debug("Did not push any changes.")
                self._UI.debug('Not setting the branch field for ticket #{0} because it already'
                               ' points to your branch "{1}".'.format(ticket, remote_branch))
                self._UI.debug('Setting the branch field of ticket #{0} to "{1}".'.format(ticket, remote_branch))
                    self.git.super_silent.fetch(self.git._repository_anonymous, current_remote_branch)
                        self._UI.error('Not setting the branch field for ticket #{0} to "{1}" because'
                                       ' "{1}" and the current value of the branch field "{2}" have diverged.'
                                       .format(ticket, remote_branch, current_remote_branch))
                        self._UI.info(['To overwrite the branch field use "{0}".'
                                       .format(self._format_command("push", ticket=ticket,
                                                                    remote_branch=remote_branch, force=True)),
                                       'To merge in the changes introduced by "{1}", use "{0}".'
                                       .format(self._format_command("download", ticket=ticket),
                                               current_remote_branch)])
                    if not self._UI.confirm('I will now change the branch field of ticket #{0} from its current value "{1}" to "{2}". Is this what you want?'.format(ticket, current_remote_branch, remote_branch), default=True):
        if ticket and self._has_ticket_for_local_branch(branch):
            old_dependencies_ = self.trac.dependencies(ticket)
            old_dependencies = ", ".join(["#"+str(dep) for dep in old_dependencies_])
            new_dependencies_ = self._dependencies_for_ticket(self._ticket_for_local_branch(branch))
            new_dependencies = ", ".join(["#"+str(dep) for dep in new_dependencies_])

            upload = True
                if old_dependencies:
                    sel = self._UI.select("According to trac, ticket #{0} depends on {1}. Your local branch depends on {2}. Do you want to upload your dependencies to trac? Or do you want to download the dependencies from trac to your local branch? Or do you want to keep your local dependencies and the dependencies on trac in its current state?".format(ticket,old_dependencies,new_dependencies or "no tickets"),options=("upload","download","keep"))
                    if sel == "keep":
                        upload = False
                    elif sel == "download":
                        self._set_dependencies_for_ticket(ticket, old_dependencies_)
                        self._UI.debug("Setting dependencies for #{0} to {1}.".format(ticket, old_dependencies))
                        upload = False
                    elif sel == "upload":
                        pass
                    else:
                        raise NotImplementedError
            else:
                self._UI.debug("Not uploading your dependencies for ticket #{0} because the dependencies on trac are already up-to-date.".format(ticket))
                upload = False

            if upload:
                self._UI.show('Uploading your dependencies for ticket #{0}: "{1}" => "{2}"'.format(ticket, old_dependencies, new_dependencies))
                # Don't send an e-mail notification
    def reset_to_clean_state(self, error_unless_clean=True):
        INPUT:

        - ``error_unless_clean`` -- a boolean (default: ``True``),
          whether to raise an
          :class:`user_interface_error.OperationCancelledError` if the
          directory remains in an unclean state; used internally.

            sage: dev._wrap("reset_to_clean_state")
            Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. To complete this command you have to reset your repository to a clean state. Do you want me to reset your repository? (This will discard many changes which are not commited.) [yes/No] n
            Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. To complete this command you have to reset your repository to a clean state. Do you want me to reset your repository? (This will discard many changes which are not commited.) [yes/No] y
        if not self._UI.confirm("Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. {0}Do you want me to reset your repository? (This will discard many changes which are not commited.)".format("To complete this command you have to reset your repository to a clean state. " if error_unless_clean else ""), default=False):
            if not error_unless_clean:
                return
    def clean(self, error_unless_clean=True):
        Restore the working directory to the most recent commit.

        INPUT:

        - ``error_unless_clean`` -- a boolean (default: ``True``),
          whether to raise an
          :class:`user_interface_error.OperationCancelledError` if the
          directory remains in an unclean state; used internally.
            sage: dev.clean()
            sage: dev.clean()
            sage: dev.clean()
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] discard
            sage: dev.clean()
            sage: UI.append("cancel")
            sage: dev.clean()
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            sage: dev.clean()
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] stash
            Your changes have been moved to the git stash stack. To re-apply your changes
            later use "git stash apply".
            sage: dev.clean()
            self.reset_to_clean_state(error_unless_clean)
        files = [line[2:] for line in self.git.status(porcelain=True).splitlines()
                 if not line.startswith('?')]

        self._UI.show(
            ['The following files in your working directory contain uncommitted changes:'] +
            [''] +
            ['    ' + f for f in files ] +
            [''])
        cancel = 'cancel' if error_unless_clean else 'keep'
        sel = self._UI.select('Discard changes?',
                              options=('discard', cancel, 'stash'), default=1)
        elif sel == cancel:
            if error_unless_clean:
                raise OperationCancelledError("User requested not to clean the working directory.")
            self.git.super_silent.stash()
            self._UI.show('Your changes have been moved to the git stash stack. '
                          'To re-apply your changes later use "git stash apply".')
            :meth:`create_ticket`, :meth:`comment`,
            :meth:`set_needs_review`, :meth:`set_needs_work`,
            :meth:`set_positive_review`, :meth:`set_needs_info`
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
    def needs_review(self, ticket=None, comment=''):
        Set a ticket on trac to ``needs_review``.
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.

        - ``comment`` -- a comment to go with the status change.
            :meth:`edit_ticket`, :meth:`set_needs_work`,
            :meth:`set_positive_review`, :meth:`comment`,
            :meth:`set_needs_info`
        Create a ticket and set it to needs_review::
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
            sage: open("tracked", "w").close()
            sage: dev.git.super_silent.add("tracked")
            sage: dev.git.super_silent.commit(message="alice: added tracked")
            sage: dev._UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.needs_review(comment='Review my ticket!')
            sage: dev.trac._get_attributes(1)['status']
            'needs_review'
        self.trac.set_attributes(ticket, comment, notify=True, status='needs_review')
        self._UI.debug("Ticket #%s marked as needing review"%ticket)
    def needs_work(self, ticket=None, comment=''):
        Set a ticket on trac to ``needs_work``.
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.

        - ``comment`` -- a comment to go with the status change.
            :meth:`edit_ticket`, :meth:`set_needs_review`,
            :meth:`set_positive_review`, :meth:`comment`,
            :meth:`set_needs_info`
        TESTS:
        Create a doctest setup with two users::

            sage: from sage.dev.test.sagedev import two_user_setup
            sage: alice, config_alice, bob, config_bob, server = two_user_setup()

        Alice creates a ticket and set it to needs_review::

            sage: alice._chdir()
            sage: alice._UI.append("Summary: summary1\ndescription")
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: alice.checkout(ticket=1)
            sage: open("tracked", "w").close()
            sage: alice.git.super_silent.add("tracked")
            sage: alice.git.super_silent.commit(message="alice: added tracked")
            sage: alice._UI.append("y")
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')
        Bob reviews the ticket and finds it lacking::

            sage: bob._chdir()
            sage: bob.checkout(ticket=1)
            sage: bob.needs_work(comment='Need to add an untracked file!')
            sage: bob.trac._get_attributes(1)['status']
            'needs_work'
        if not comment:
            comment = self._UI.get_input("Please add a comment for the author:")
        self.trac.set_attributes(ticket, comment, notify=True, status='needs_work')
        self._UI.debug("Ticket #%s marked as needing work"%ticket)
    def needs_info(self, ticket=None, comment=''):
        Set a ticket on trac to ``needs_info``.
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.
        - ``comment`` -- a comment to go with the status change.
        .. SEEALSO::
            :meth:`edit_ticket`, :meth:`needs_review`,
            :meth:`positive_review`, :meth:`comment`,
            :meth:`needs_work`
        TESTS:
        Create a doctest setup with two users::
            sage: from sage.dev.test.sagedev import two_user_setup
            sage: alice, config_alice, bob, config_bob, server = two_user_setup()
        Alice creates a ticket and set it to needs_review::
            sage: alice._chdir()
            sage: alice._UI.append("Summary: summary1\ndescription")
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: alice.checkout(ticket=1)
            sage: alice.git.super_silent.add("tracked")
            sage: alice.git.super_silent.commit(message="alice: added tracked")
            sage: alice._UI.append("y")
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')
        Bob reviews the ticket and finds it lacking::
            sage: bob._chdir()
            sage: bob.checkout(ticket=1)
            sage: bob.needs_info(comment='Why is a tracked file enough?')
            sage: bob.trac._get_attributes(1)['status']
            'needs_info'
        if not comment:
            comment = self._UI.get_input("Please specify what information is required from the author:")
        self.trac.set_attributes(ticket, comment, notify=True, status='needs_info')
        self._UI.debug("Ticket #%s marked as needing info"%ticket)
    def positive_review(self, ticket=None, comment=''):
        r"""
        Set a ticket on trac to ``positive_review``.
        INPUT:
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.
        - ``comment`` -- a comment to go with the status change.
        .. SEEALSO::
            :meth:`edit_ticket`, :meth:`needs_review`,
            :meth:`needs_info`, :meth:`comment`,
            :meth:`needs_work`
        TESTS:
        Create a doctest setup with two users::
            sage: from sage.dev.test.sagedev import two_user_setup
            sage: alice, config_alice, bob, config_bob, server = two_user_setup()
        Alice creates a ticket and set it to needs_review::
            sage: alice._chdir()
            sage: alice._UI.append("Summary: summary1\ndescription")
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: alice.checkout(ticket=1)
            sage: open("tracked", "w").close()
            sage: alice.git.super_silent.add("tracked")
            sage: alice.git.super_silent.commit(message="alice: added tracked")
            sage: alice._UI.append("y")
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')
        Bob reviews the ticket and finds it good::
            sage: bob._chdir()
            sage: bob.checkout(ticket=1)
            sage: bob.positive_review()
            sage: bob.trac._get_attributes(1)['status']
            'positive_review'
        """
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        self.trac.set_attributes(ticket, comment, notify=True, status='positive_review')
        self._UI.debug("Ticket #%s reviewed!"%ticket)
    def comment(self, ticket=None):
        r"""
        Add a comment to ``ticket`` on trac.
        INPUT:
        - ``ticket`` -- an integer or string identifying a ticket or ``None``
          (default: ``None``), the number of the ticket to edit. If ``None``,
          edit the :meth:`_current_ticket`.
            :meth:`create_ticket`, :meth:`edit_ticket`
        Create a ticket and add a comment::
            sage: UI.append("Summary: summary1\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: UI.append("comment")
            sage: dev.comment()
            sage: server.tickets[1].comments
            ['comment']
        """
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        ticket = self._ticket_from_ticket_name(ticket)
        self.trac.add_comment_interactive(ticket)
    def browse_ticket(self, ticket=None):
        r"""
        Start a webbrowser at the ticket page on trac.
        INPUT:
        - ``ticket`` -- an integer or string identifying a ticket or ``None``
          (default: ``None``), the number of the ticket to edit. If ``None``,
          browse the :meth:`_current_ticket`.
        .. SEEALSO::
            :meth:`edit_ticket`, :meth:`comment`,
            :meth:`sage.dev.trac_interface.TracInterface.show_ticket`,
            :meth:`sage.dev.trac_interface.TracInterface.show_comments`
        EXAMPLES::
            sage: dev.browse_ticket(10000) # not tested
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        ticket = self._ticket_from_ticket_name(ticket)
        from sage.misc.viewer import browser
        from sage.env import TRAC_SERVER_URI
        browser_cmdline = browser() + ' ' + TRAC_SERVER_URI + '/ticket/' + str(ticket)
        import os
        os.system(browser_cmdline)
    def remote_status(self, ticket=None):
        Show information about the status of ``ticket``.
        INPUT:
        - ``ticket`` -- an integer or string identifying a ticket or ``None``
          (default: ``None``), the number of the ticket to edit.  If ``None``,
          show information for the :meth:`_current_ticket`.
        TESTS:
        Set up a single user for doctesting::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
        It is an error to call this without parameters if not on a ticket::
            sage: dev.remote_status()
            ValueError: ticket must be specified if not currently on a ticket.
        Create a ticket and show its remote status::
            sage: UI.append("Summary: ticket1\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: dev.remote_status()
            Ticket #1 (https://trac.sagemath.org/ticket/1)
            ==============================================
            Your branch "ticket/1" has 0 commits.
            No branch has been set on the trac ticket yet.
            You have not created a remote branch yet.
        After pushing the local branch::
            sage: UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.remote_status()
            Ticket #1 (https://trac.sagemath.org/ticket/1)
            ==============================================
            Your branch "ticket/1" has 0 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 0 commits. It does not differ from "ticket/1".
        Making local changes::
            sage: open("tracked", "w").close()
            sage: dev.git.silent.add("tracked")
            sage: dev.git.silent.commit(message="added tracked")
            sage: dev.remote_status()
            Ticket #1 (https://trac.sagemath.org/ticket/1)
            ==============================================
            Your branch "ticket/1" has 1 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 0 commits. "ticket/1" is ahead of "u/doctest/ticket/1" by 1 commits:
            ...: added tracked
        Pushing them::
            sage: UI.append("y")
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/1":
            ...: added tracked
            Is this what you want? [Yes/no] y
            sage: dev.remote_status()
            Ticket #1 (https://trac.sagemath.org/ticket/1)
            ==============================================
            Your branch "ticket/1" has 1 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 1 commits. It does not differ from "ticket/1".
        The branch on the ticket is ahead of the local branch::
            sage: dev.git.silent.reset('HEAD~', hard=True)
            sage: dev.remote_status()
            Ticket #1 (https://trac.sagemath.org/ticket/1)
            ==============================================
            Your branch "ticket/1" has 0 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 1 commits. "u/doctest/ticket/1" is ahead of "ticket/1" by 1 commits:
            ...: added tracked
        A mixed case::
            sage: open("tracked2", "w").close()
            sage: dev.git.silent.add("tracked2")
            sage: dev.git.silent.commit(message="added tracked2")
            sage: open("tracked3", "w").close()
            sage: dev.git.silent.add("tracked3")
            sage: dev.git.silent.commit(message="added tracked3")
            sage: open("tracked4", "w").close()
            sage: dev.git.silent.add("tracked4")
            sage: dev.git.silent.commit(message="added tracked4")
            sage: dev._UI.append("y")
            sage: dev.push(remote_branch="u/doctest/branch1", force=True)
            The branch "u/doctest/branch1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.git.silent.reset('HEAD~', hard=True)
            sage: dev.remote_status()
            Ticket #1 (https://trac.sagemath.org/ticket/1)
            ==============================================
            Your branch "ticket/1" has 2 commits.
            The trac ticket points to the branch "u/doctest/branch1" which has 3 commits. "u/doctest/branch1" is ahead of "ticket/1" by 1 commits:
            ...: added tracked4
            Your remote branch "u/doctest/ticket/1" has 1 commits. The branches "u/doctest/ticket/1" and "ticket/1" have diverged.
            "u/doctest/ticket/1" is ahead of "ticket/1" by 1 commits:
            ...: added tracked
            "ticket/1" is ahead of "u/doctest/ticket/1" by 2 commits:
            ...: added tracked2
            ...: added tracked3
        """
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        ticket = self._ticket_from_ticket_name(ticket)
        self._is_master_uptodate(action_if_not="warning")
        from sage.env import TRAC_SERVER_URI
        header = "Ticket #{0} ({1})".format(ticket, TRAC_SERVER_URI + '/ticket/' + str(ticket))
        underline = "="*len(header)
        commits = lambda a, b: list(reversed(self.git.log("{0}..{1}".format(a,b), "--pretty=%an <%ae>: %s").splitlines()))
        def detail(a, b, a_to_b, b_to_a):
            if not a_to_b and not b_to_a:
                return 'It does not differ from "{0}".'.format(b)
            elif not a_to_b:
                return '"{0}" is ahead of "{1}" by {2} commits:\n{3}'.format(a,b,len(b_to_a), "\n".join(b_to_a))
            elif not b_to_a:
                return '"{0}" is ahead of "{1}" by {2} commits:\n{3}'.format(b,a,len(a_to_b),"\n".join(a_to_b))
            else:
                return 'The branches "{0}" and "{1}" have diverged.\n"{0}" is ahead of "{1}" by {2} commits:\n{3}\n"{1}" is ahead of "{0}" by {4} commits:\n{5}'.format(a,b,len(b_to_a),"\n".join(b_to_a),len(a_to_b),"\n".join(a_to_b))
        branch = None
        merge_base_local = None
        if self._has_local_branch_for_ticket(ticket):
            branch = self._local_branch_for_ticket(ticket)
            merge_base_local = self.git.merge_base(MASTER_BRANCH, branch).splitlines()[0]
            master_to_branch = commits(merge_base_local, branch)
            local_summary = 'Your branch "{0}" has {1} commits.'.format(branch, len(master_to_branch))
        else:
            local_summary = "You have no local branch for this ticket"
        ticket_branch = self.trac._branch_for_ticket(ticket)
        if ticket_branch:
            ticket_to_local = None
            local_to_ticket = None
            if not self._is_remote_branch_name(ticket_branch, exists=True):
                ticket_summary = 'The trac ticket points to the branch "{0}" which does not exist.'
                self.git.super_silent.fetch(self.git._repository_anonymous, ticket_branch)
                merge_base_ticket = self.git.merge_base(MASTER_BRANCH, 'FETCH_HEAD').splitlines()[0]
                master_to_ticket = commits(merge_base_ticket, 'FETCH_HEAD')
                ticket_summary = 'The trac ticket points to the' \
                    ' branch "{0}" which has {1} commits.'.format(ticket_branch, len(master_to_ticket))
                if branch is not None:
                    if merge_base_local != merge_base_ticket:
                        ticket_summary += ' The branch can not be compared to your local' \
                            ' branch "{0}" because the branches are based on different versions' \
                            ' of sage (i.e. the "master" branch).'
                    else:
                        ticket_to_local = commits('FETCH_HEAD', branch)
                        local_to_ticket = commits(branch, 'FETCH_HEAD')
                        ticket_summary += " "+detail(ticket_branch, branch, ticket_to_local, local_to_ticket)
        else:
            ticket_summary = "No branch has been set on the trac ticket yet."

        remote_branch = self._remote_branch_for_ticket(ticket)
        if self._is_remote_branch_name(remote_branch, exists=True):
            remote_to_local = None
            local_to_remote = None
            self.git.super_silent.fetch(self.git._repository_anonymous, remote_branch)
            merge_base_remote = self.git.merge_base(MASTER_BRANCH, 'FETCH_HEAD').splitlines()[0]
            master_to_remote = commits(merge_base_remote, 'FETCH_HEAD')
            remote_summary = 'Your remote branch "{0}" has {1} commits.'.format(
                remote_branch, len(master_to_remote))
            if branch is not None:
                if merge_base_remote != merge_base_local:
                    remote_summary += ' The branch can not be compared to your local' \
                        ' branch "{0}" because the branches are based on different version' \
                        ' of sage (i.e. the "master" branch).'
                    remote_to_local = commits('FETCH_HEAD', branch)
                    local_to_remote = commits(branch, 'FETCH_HEAD')
                    remote_summary += " "+detail(remote_branch, branch, remote_to_local, local_to_remote)
            remote_summary = "You have not created a remote branch yet."

        show = [header, underline, local_summary, ticket_summary]
        if not self._is_remote_branch_name(remote_branch, exists=True) or remote_branch != ticket_branch:
            show.append(remote_summary)
        self._UI.show("\n".join(show))
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
                : master
            * #1: ticket/1 summary
                : master
            * #1: ticket/1 summary
            Cannot delete "ticket/1": is the current branch.
            Moved your branch "ticket/1" to "trash/ticket/1".
            - :meth:`prune_closed_tickets` -- abandon tickets that have
              been closed.
            - :meth:`local_tickets` -- list local non-abandoned tickets.
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
            sage: UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            Cannot delete "ticket/1": is the current branch.
            Moved your branch "ticket/1" to "trash/ticket/1".

        Start to work on a new branch for this ticket::
            sage: from sage.dev.sagedev import MASTER_BRANCH
            sage: UI.append("y")
            sage: dev.checkout(ticket=1, base=MASTER_BRANCH)
            Creating a new branch for #1 based on "master". The trac ticket for #1
            already refers to the branch "u/doctest/ticket/1". As you are creating
            a new branch for that ticket, it seems that you want to ignore the work
            that has already been done on "u/doctest/ticket/1" and start afresh. Is
            this what you want? [yes/No] y
        ticket = None

                raise SageDevValueError("Cannot abandon #{0}: no local branch for this ticket."
                                        .format(ticket))
        if self._has_ticket_for_local_branch(ticket_or_branch):
            ticket = self._ticket_for_local_branch(ticket_or_branch)

                self._UI.error("Cannot delete the master branch.")
                    self._UI.error('Cannot delete "{0}": is the current branch.'
                                   .format(branch))
                    self._UI.info('Use "{0}" to switch to the master branch first.'
                                  .format(self._format_command("vanilla")))
            self._UI.show('Moved your branch "{0}" to "{1}".'
                          .format(branch, new_branch))
        if ticket:
            self._set_local_branch_for_ticket(ticket, None)
            self._set_dependencies_for_ticket(ticket, None)
            self._UI.info('Use "{1}" to work on #{0} with a clean copy of the master branch.'
                          .format(ticket, self._format_command("checkout", ticket=ticket, base=MASTER_BRANCH)))

            - :meth:`merge` -- merge into the current branch rather
              than creating a new one
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            self.clean()
        self._UI.debug('Creating a new branch "{0}".'.format(branch))
            for local_remote,branch_name in branches:
                self._UI.debug('Merging {2} branch "{0}" into "{1}".'
                              .format(branch_name, branch, local_remote))
                self.merge(branch, pull=local_remote=="remote")
            self._UI.debug('Deleted branch "{0}".'.format(branch))
    def merge(self, ticket_or_branch=MASTER_BRANCH, pull=None, create_dependency=None):
          ticket, if ``pull`` is ``False``), for the name of a local or
          dependencies are merged in one by one.
        - ``pull`` -- a boolean or ``None`` (default: ``None``); if
          ``ticket_or_branch`` identifies a ticket, whether to pull the
          ``ticket_or_branch`` is a branch name, then ``pull`` controls
          whether it should be interpreted as a remote branch (``True``) or as
          a local branch (``False``). If it is set to ``None``, then it will
          take ``ticket_or_branch`` as a remote branch if it exists, and as a
          local branch otherwise.
          whether to create a dependency to ``ticket_or_branch``. If ``None``,
            the remote server during :meth:`push` and :meth:`pull`.
            - :meth:`show_dependencies` -- see the current
              dependencies.
            - :meth:`GitInterface.merge` -- git's merge command has
              more options and can merge multiple branches at once.
            - :meth:`gather` -- creates a new branch to merge into
              rather than merging into the current branch.
        TESTS:
            Created ticket #1 at https://trac.sagemath.org/1.
            Created ticket #2 at https://trac.sagemath.org/2.
            sage: alice.checkout(ticket=1)
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            sage: alice.checkout(ticket=2)
            sage: alice.merge("#1", pull=False)
            Merging the local branch "ticket/1" into the local branch "ticket/2".
        Check that merging dependencies works::

            sage: alice.merge("dependencies")
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/2".

            Merging the local branch "ticket/1" into the local branch "ticket/2".
        A remote branch for a local branch is only merged in if ``pull`` is set::
            Merging the local branch "ticket/1" into the local branch "ticket/2".
            sage: alice.merge("ticket/1", pull=True)
            ValueError: Branch "ticket/1" does not exist on the remote system.
            sage: bob.checkout(ticket=1)
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/2".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/2".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] resolved
        We cannot merge a ticket into itself::

            sage: alice.merge(2)
            ValueError: cannot merge a ticket into itself

        We also cannot merge if the working directory has uncommited changes::

            sage: alice._UI.append("cancel")
            sage: with open("alice2","w") as f: f.write("uncommited change")
            sage: alice.merge(1)
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                 alice2
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            Cannot merge because working directory is not in a clean state.
            <BLANKLINE>
            #  Use "sage --dev commit" to commit your changes.
            self.clean()
            self._UI.show(['',
                           '#  Use "{0}" to commit your changes.'
                           .format(self._format_command('commit'))])
            self._UI.error('Not on any branch. Use "{0}" to checkout a branch.'.format(self._format_command("checkout")))
        if ticket_or_branch == 'dependencies':
            if current_ticket == None:
                raise SageDevValueError("dependencies can only be merged if currently on a ticket.")
            if pull == False:
                raise SageDevValueError('"pull" must not be "False" when merging dependencies.')
            if create_dependency != None:
                raise SageDevValueError('"create_dependency" must not be set when merging dependencies.')
            for dependency in self._dependencies_for_ticket(current_ticket):
                self._UI.debug("Merging dependency #{0}.".format(dependency))
                self.merge(ticket_or_branch=dependency, pull=True)
            return
            if ticket == current_ticket:
                raise SageDevValueError("cannot merge a ticket into itself")
            if pull is None:
                pull = True
            if pull:
        elif pull == False or (pull is None and not self._is_remote_branch_name(ticket_or_branch, exists=True)):
            # ticket_or_branch should be interpreted as a local branch name
            branch = ticket_or_branch
            self._check_local_branch_name(branch, exists=True)
            pull = False
            if create_dependency == True:
                if self._has_ticket_for_local_branch(branch):
                    ticket = self._ticket_for_local_branch(branch)
                else:
                    raise SageDevValueError('"create_dependency" must not be "True" if "ticket_or_branch" is a local branch which is not associated to a ticket.')
            else:
                create_dependency = False
            # ticket_or_branch should be interpreted as a remote branch name
            self._check_remote_branch_name(remote_branch, exists=True)
            pull = True
                raise SageDevValueError('"create_dependency" must not be "True" if "ticket_or_branch" is a local branch.')
            create_dependency = False
        if pull:
                self._UI.error('Can not merge remote branch "{0}". It does not exist.'
                               .format(remote_branch))
            self._UI.show('Merging the remote branch "{0}" into the local branch "{1}".'
                          .format(remote_branch, current_branch))
            self.git.super_silent.fetch(self.git._repository_anonymous, remote_branch)
            self._UI.show('Merging the local branch "{0}" into the local branch "{1}".'
                          .format(branch, current_branch))
            local_merge_branch = branch
                lines.append('Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge.')
                if self._UI.select("\n".join(lines), ['resolved', 'abort']) == 'resolved':
                    self._UI.debug("Created a commit from your conflict resolution.")
                self._UI.debug("Not recording dependency on #{0} because #{1} already depends on #{0}."
                              .format(ticket, current_ticket))
    def local_tickets(self, include_abandoned=False, cached=True):
        - ``cached`` -- boolean (default: ``True``), whether to try to pull the
          summaries from the ticket cache; if ``True``, then the summaries
          might not be accurate if they changed since they were last updated.
          To update the summaries, set this to ``False``.

            - :meth:`abandon_ticket` -- hide tickets from this method.
            - :meth:`remote_status` -- also show status compared to
              the trac server.
            - :meth:`current_ticket` -- get the current ticket.
            * : master
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
            Created ticket #2 at https://trac.sagemath.org/2.
            sage: dev.checkout(ticket=2)
                : master
              #1: ticket/1 summary
            * #2: ticket/2 summary
        from git_error import DetachedHeadError
        try:
            current_branch = self.git.current_branch()
        except DetachedHeadError:
            current_branch = None
        ret = []
        for branch in branches:
            ticket = None
            ticket_summary = ""
            extra = " "
            if self._has_ticket_for_local_branch(branch):
                ticket = self._ticket_for_local_branch(branch)
                try:
                    try:
                        ticket_summary = self.trac._get_attributes(ticket, cached=cached)['summary']
                    except KeyError:
                        ticket_summary = self.trac._get_attributes(ticket, cached=False)['summary']
                except TracConnectionError:
                    ticket_summary = ""
            if current_branch == branch:
                extra = "*"
            ret.append(("{0:>7}: {1} {2}".format("#"+str(ticket) if ticket else "", branch, ticket_summary), extra))
        while all([info.startswith(' ') for (info, extra) in ret]):
            ret = [(info[1:],extra) for (info, extra) in ret]
        ret = sorted(ret)
        ret = ["{0} {1}".format(extra,info) for (info,extra) in ret]
        self._UI.show("\n".join(ret))

    def vanilla(self, release=MASTER_BRANCH):
        Return to a clean version of Sage.
        - ``release`` -- a string or decimal giving the release name (default:
          ``'master'``).  In fact, any tag, commit or branch will work.  If the
          tag does not exist locally an attempt to fetch it from the server
          will be made.
            - :meth:`checkout` -- checkout another branch, ready to
              develop on it.
            - :meth:`pull` -- pull a branch from the server and merge
              it.
        TESTS:

        Create a doctest setup with a single user::

            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
        Go to a sage release::
            sage: dev.git.current_branch()
            'master'
            sage: dev.vanilla()
            sage: dev.git.current_branch()
            Traceback (most recent call last):
            ...
            DetachedHeadError: unexpectedly, git is in a detached HEAD state
        release = str(release)
            self.clean()
            self._UI.error("Cannot checkout a release while your working directory is not clean.")
                self.git.super_silent.fetch(self.git._repository_anonymous, release)
                self._UI.error('"{0}" does not exist locally or on the remote server.'.format(release))
    def diff(self, base='commit'):
        - ``base`` -- a string; show the differences against the latest
          ``'commit'`` (the default), against the branch ``'master'`` (or any
          other branch name), or the merge of the ``'dependencies'`` of the
          current ticket (if the dependencies merge cleanly)
            - :meth:`commit` -- record changes into the repository.
            - :meth:`local_tickets` -- list local tickets (you may
              want to commit your changes to a branch other than the
              current one).
        TESTS:
        Create a doctest setup with a single user::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
        Create some tickets and make one depend on the others::
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #2 at https://trac.sagemath.org/2.
            2
            sage: dev.checkout(ticket=2)
            sage: UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/2" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #3 at https://trac.sagemath.org/3.
            3
            sage: dev.checkout(ticket=3)
            sage: UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/3" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.merge("#1")
            Merging the remote branch "u/doctest/ticket/1" into the local branch "ticket/3".
            Added dependency on #1 to #3.
            sage: dev.merge("#2")
            Merging the remote branch "u/doctest/ticket/2" into the local branch "ticket/3".
            Added dependency on #2 to #3.

        Make some non-conflicting changes on the tickets::

            sage: dev.checkout(ticket="#1")
            sage: with open("ticket1","w") as f: f.write("ticket1")
            sage: dev.git.silent.add("ticket1")
            sage: dev.git.super_silent.commit(message="added ticket1")

            sage: dev.checkout(ticket="#2")
            sage: with open("ticket2","w") as f: f.write("ticket2")
            sage: dev.git.silent.add("ticket2")
            sage: dev.git.super_silent.commit(message="added ticket2")
            sage: UI.append("y")
            sage: dev.push()
            I will now push the following new commits to the remote
            branch "u/doctest/ticket/2":
            ...: added ticket2
            Is this what you want? [Yes/no] y
            sage: dev.checkout(ticket="#3")
            sage: open("ticket3","w").close()
            sage: dev.git.silent.add("ticket3")
            sage: dev.git.super_silent.commit(message="added ticket3")
            sage: UI.append("y")
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/3":
            ...: added ticket3
            Is this what you want? [Yes/no] y
            Uploading your dependencies for ticket #3: "" => "#1, #2"

        A diff against the previous commit::

            sage: dev.diff()

        A diff against a ticket will always take the branch on trac::

            sage: dev.diff("#1")
            diff --git a/ticket3 b/ticket3
            new file mode ...
            index ...
            sage: dev.diff("ticket/1")
            diff --git a/ticket1 b/ticket1
            deleted file mode ...
            index ...
            diff --git a/ticket3 b/ticket3
            new file mode ...
            index ...
            sage: dev.checkout(ticket="#1")
            sage: UI.append("y")
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/1":
            ...: added ticket1
            Is this what you want? [Yes/no] y
            sage: dev.checkout(ticket="#3")
            sage: dev.diff("#1")
            diff --git a/ticket1 b/ticket1
            deleted file mode ...
            index ...
            diff --git a/ticket3 b/ticket3
            new file mode ...
            index ...

        A diff against the dependencies::

            sage: dev.diff("dependencies")
            Dependency #1 has not been merged into "ticket/3" (at least not its latest version).
            Dependency #2 has not been merged into "ticket/3" (at least not its latest version).
            diff --git a/ticket1 b/ticket1
            deleted file mode ...
            index ...
            diff --git a/ticket2 b/ticket2
            deleted file mode ...
            index ...
            diff --git a/ticket3 b/ticket3
            new file mode ...
            index ...
            sage: dev.merge("#1")
            Merging the remote branch "u/doctest/ticket/1" into the local branch "ticket/3".
            sage: dev.merge("#2")
            Merging the remote branch "u/doctest/ticket/2" into the local branch "ticket/3".
            sage: dev.diff("dependencies")
            diff --git a/ticket3 b/ticket3
            new file mode ...
            index ...

        This does not work if the dependencies do not merge::

            sage: dev.checkout(ticket="#1")
            sage: with open("ticket2","w") as f: f.write("foo")
            sage: dev.git.silent.add("ticket2")
            sage: dev.git.super_silent.commit(message="added ticket2")
            sage: UI.append("y")
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/1":
            ...: added ticket2
            Is this what you want? [Yes/no] y
            sage: dev.checkout(ticket="#3")
            sage: dev.diff("dependencies")
            Dependency #1 has not been merged into "ticket/3" (at least not its latest version).
            #2 does not merge cleanly with the other dependencies. Your diff could not be computed.
        if base == "dependencies":
            current_ticket = self._current_ticket()
            if current_ticket is None:
                raise SageDevValueError("'dependencies' are only supported if currently on a ticket.")
            try:
                self.reset_to_clean_state()
                self.clean()
            except OperationCancelledError:
                self._UI.error("Cannot create merge of dependencies because working directory is not clean.")
                raise
            self._is_master_uptodate(action_if_not="warning")
            branch = self.git.current_branch()
            merge_base = self.git.merge_base(branch, MASTER_BRANCH).splitlines()[0]
            temporary_branch = self._new_local_branch_for_trash("diff")
            self.git.super_silent.branch(temporary_branch, merge_base)
            try:
                self.git.super_silent.checkout(temporary_branch)
                try:
                    self._UI.debug("Merging dependencies of #{0}.".format(current_ticket))
                    for dependency in self._dependencies_for_ticket(current_ticket):
                        self._check_ticket_name(dependency, exists=True)
                        remote_branch = self.trac._branch_for_ticket(dependency)
                        if remote_branch is None:
                            self._UI.warning("Dependency #{0} has no branch field set.".format(dependency))
                        self._check_remote_branch_name(remote_branch, exists=True)
                        self.git.super_silent.fetch(self.git._repository_anonymous, remote_branch)
                        merge_base_dependency = self.git.merge_base(MASTER_BRANCH, 'FETCH_HEAD').splitlines()[0]
                        if merge_base_dependency != merge_base and self.git.is_child_of(merge_base_dependency, merge_base):
                            self._UI.show('The remote branch "{0}" is based on a later version of sage than your local branch "{1}". The diff might therefore contain many changes which were not introduced by your branch "{1}". Use "{2}" to rebase your branch to the latest version of sage.'.format(remote_branch, branch, self._format_command("merge")))
                        if self.git.is_child_of(merge_base, 'FETCH_HEAD'):
                            self._UI.debug("Dependency #{0} has already been merged into the master branch of your version of sage.".format(dependency))
                        else:
                            if not self.git.is_child_of(branch, 'FETCH_HEAD'):
                                self._UI.warning('Dependency #{0} has not been merged into "{1}" (at least not its latest version).'.format(dependency, branch))
                                self._UI.debug('#  Use "{0}" to merge it.'.format(
                                    self._format_command("merge", ticket_or_branch=str(dependency))))
                            from git_error import GitError
                            try:
                                self.git.super_silent.merge('FETCH_HEAD')
                            except GitError as e:
                                self._UI.error("#{0} does not merge cleanly with the other dependencies. Your diff could not be computed.".format(dependency))
                                raise OperationCancelledError("merge failed")

                    self.git.echo.diff("{0}..{1}".format(temporary_branch, branch))
                    return
                finally:
                    self.git.reset_to_clean_state()
                    self.git.reset_to_clean_working_directory()
                    self.git.super_silent.checkout(branch)
            finally:
                self.git.super_silent.branch("-D", temporary_branch)
        if base == "commit":
            base = "HEAD"
            if self._is_ticket_name(base):
                ticket = self._ticket_from_ticket_name(base)
                self._check_ticket_name(ticket, exists=True)
                base = self.trac._branch_for_ticket(ticket)
                if base is None:
                    self._UI.error("Ticket #{0} has no branch set on trac.".format(ticket))

            if self._is_local_branch_name(base, exists=True):
                pass
            else:
                self._check_remote_branch_name(base, exists=True)
                self._is_master_uptodate(action_if_not="warning")
                self.git.super_silent.fetch(self.git._repository_anonymous, base)
                base = 'FETCH_HEAD'

        self.git.echo.diff(base)
    def show_dependencies(self, ticket=None, all=False, _seen=None): # all = recursive
        Show the dependencies of ``ticket``.
        - ``ticket`` -- a string or integer identifying a ticket or ``None``
          (default: ``None``), the ticket for which dependencies are displayed.
          If ``None``, then the dependencies for the current ticket are
          displayed.
        - ``all`` -- boolean (default: ``True``), whether to recursively list
          all tickets on which this ticket depends (in depth-first order), only
          including tickets that have a local branch.
        .. NOTE::
            Ticket dependencies are stored locally and only updated with
            respect to the remote server during :meth:`push` and
            :meth:`pull`.
        .. SEEALSO::
            - :meth:`TracInterface.dependencies` -- Query Trac to find
              dependencies.
            - :meth:`remote_status` -- will show the status of tickets
              with respect to the remote server.
            - :meth:`merge` -- Merge in changes from a dependency.
            - :meth:`diff` -- Show the changes in this branch over the
              dependencies.
        TESTS:
        Create a doctest setup with a single user::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
        Create some tickets and add dependencies::
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #2 at https://trac.sagemath.org/2.
            2
            sage: dev.checkout(ticket=2)
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #3 at https://trac.sagemath.org/3.
            3
            sage: dev.checkout(ticket=3)
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #4 at https://trac.sagemath.org/4.
            4
            sage: dev.checkout(ticket=4)

            sage: dev.merge('ticket/2',create_dependency=True)
            Merging the local branch "ticket/2" into the local branch "ticket/4".
            Added dependency on #2 to #4.
            sage: dev.merge('ticket/3',create_dependency=True)
            Merging the local branch "ticket/3" into the local branch "ticket/4".
            Added dependency on #3 to #4.
            sage: dev.checkout(ticket='#2')
            sage: dev.merge('ticket/1', create_dependency=True)
            Merging the local branch "ticket/1" into the local branch "ticket/2".
            Added dependency on #1 to #2.
            sage: dev.checkout(ticket='#3')
            sage: dev.merge('ticket/1', create_dependency=True)
            Merging the local branch "ticket/1" into the local branch "ticket/3".
            Added dependency on #1 to #3.

        Check that the dependencies show correctly::

            sage: dev.checkout(ticket='#4')
            sage: dev.show_dependencies()
            Ticket #4 depends on #2, #3.
            sage: dev.show_dependencies('#4')
            Ticket #4 depends on #2, #3.
            sage: dev.show_dependencies('#3')
            Ticket #3 depends on #1.
            sage: dev.show_dependencies('#2')
            Ticket #2 depends on #1.
            sage: dev.show_dependencies('#1')
            Ticket #1 has no dependencies.
            sage: dev.show_dependencies('#4', all=True)
            Ticket #4 depends on #3, #1, #2.
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified")
        self._check_ticket_name(ticket)
        ticket = self._ticket_from_ticket_name(ticket)
        if not self._has_local_branch_for_ticket(ticket):
            raise SageDevValueError('ticket must be a ticket with a local branch. Use "{0}" to checkout the ticket first.'.format(self._format_command("checkout",ticket=ticket)))
        branch = self._local_branch_for_ticket(ticket)
        if all:
            stack = [ticket]
            while stack:
                t = stack.pop()
                if t in ret: continue
                ret.append(t)
                if not self._has_local_branch_for_ticket(t):
                    self._UI.warning("no local branch for ticket #{0} present, some dependencies might be missing in the output.".format(t))
                    continue
                deps = self._dependencies_for_ticket(t)
                for d in deps:
                    if d not in stack and d not in ret:
                        stack.append(d)
            ret = ret[1:]
            ret = self._dependencies_for_ticket(ticket)
        if ret:
            self._UI.show("Ticket #{0} depends on {1}.".format(ticket,", ".join(["#{0}".format(d) for d in ret])))
            self._UI.show("Ticket #{0} has no dependencies.".format(ticket))
    def upload_ssh_key(self, public_key=None):
        Upload ``public_key`` to gitolite through the trac interface.
        - ``public_key`` -- a string or ``None`` (default: ``None``), the path
          of the key file, defaults to ``~/.ssh/id_rsa.pub`` (or
          ``~/.ssh/id_dsa.pub`` if it exists).
        TESTS:
        Create a doctest setup with a single user::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
        Create and upload a key file::

            sage: import os
            sage: public_key = os.path.join(dev._sagedev.tmp_dir, "id_rsa.pub")
            sage: UI.append("no")
            sage: UI.append("yes")
            sage: dev.upload_ssh_key(public_key=public_key)
            I will now upload your ssh key at "..." to trac. This will enable access to the git repository there. Is this what you want? [Yes/no] yes
            I could not find a public key at "{0}". Do you want me to create one for you? [Yes/no] no
            sage: UI.append("yes")
            sage: UI.append("yes")
            sage: dev.upload_ssh_key(public_key=public_key)
            I will now upload your ssh key at "..." to trac. This will enable access to the git repository there. Is this what you want? [Yes/no] yes
            I could not find a public key at "{0}". Do you want me to create one for you? [Yes/no] yes
            Generating ssh key.
            Your key has been uploaded.
            sage: UI.append("yes")
            sage: dev.upload_ssh_key(public_key=public_key)
            I will now upload your ssh key at "..." to trac. This will enable access to the git repository there. Is this what you want? [Yes/no] yes
            Your key has been uploaded.
        try:
            import os
            if public_key is None:
                public_key = os.path.expanduser("~/.ssh/id_dsa.pub")
                if not os.path.exists(public_key):
                    public_key = os.path.expanduser("~/.ssh/id_rsa.pub")
            if not self._UI.confirm('I will now upload your ssh key at "{0}" to trac. This will enable access to the git repository there. Is this what you want?'.format(public_key), default=True):
                raise OperationCancelledError("do not upload key")
            if not os.path.exists(public_key):
                if not public_key.endswith(".pub"):
                    raise SageDevValueError('public key must end with ".pub".')
                if not self._UI.confirm('I could not find a public key at "{0}". Do you want me to create one for you?', default=True):
                    raise OperationCancelledError("no keyfile found")
                private_key = public_key[:-4]
                self._UI.show("Generating ssh key.")
                from subprocess import call
                success = call(['sage-native-execute', 'ssh-keygen', '-q', '-f', private_key, '-P', ''])
                if success == 0:
                    self._UI.debug("Key generated.")
                else:
                    self._UI.error("Key generation failed.")
                    self._UI.info('Please create a key in "{0}" and retry.'.format(public_key))
                    raise OperationCancelledError("ssh-keygen failed")
            with open(public_key, 'r') as F:
                public_key = F.read().strip()
            self.trac._authenticated_server_proxy.sshkeys.addkey(public_key)
            self._UI.show("Your key has been uploaded.")
        except OperationCancelledError:
            server = self.config.get('server', TRAC_SERVER_URI)
            url = urlparse.urljoin(server, urllib.pathname2url(os.path.join('prefs', 'sshkeys')))
            self._UI.info('Use "{0}" to upload a public key. Or set your key manually at {1}.'.format(self._format_command("upload_ssh_key"), url))
            raise
    def _upload_ssh_key(self):
        r"""
        Make sure that the public ssh key has been uploaded to the trac server.
        .. NOTE::
            This is a wrapper for :meth:`upload_ssh_key` which is only called
            one the user's first attempt to push to the repository, i.e., on
            the first attempt to acces ``SAGE_REPO_AUTHENTICATED``.
        TESTS:
        Create a doctest setup with a single user::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
            sage: del dev._sagedev.config['git']['ssh_key_set']
        We need to patch :meth:`upload_ssh_key` to get testable results since
        it depends on whether the user has an ssh key in ``.ssh/id_rsa.pub``::
            sage: from sage.dev.user_interface_error import OperationCancelledError
            sage: def upload_ssh_key():
            ....:     print "Uploading ssh key."
            ....:     raise OperationCancelledError("")
            sage: dev._sagedev.upload_ssh_key = upload_ssh_key
        The ssh key is only uploaded once::
            sage: dev._sagedev._upload_ssh_key()
            Uploading ssh key.
            sage: dev._sagedev._upload_ssh_key()
        """
        if self.config['git'].get('ssh_key_set', False):
            return

        from user_interface_error import OperationCancelledError
        try:
            self.upload_ssh_key()
        except OperationCancelledError:
            pass # do not bother the user again, probably the key has been uploaded manually already
        self.config['git']['ssh_key_set'] = "True"

    def _is_master_uptodate(self, action_if_not=None):
        Check whether the master branch is up to date with respect to the
        remote master branch.
        - ``action_if_not`` -- one of ``'error'``, ``'warning'``, or ``None``
          (default: ``None``), the action to perform if master is not up to
          date. If ``'error'``, then this raises a ``SageDevValueError``,
          otherwise return a boolean and print a warning if ``'warning'``.
        .. NOTE::
            In the transitional period from hg to git, this is a nop. This will
            change as soon as ``master`` is our actual master branch.
        TESTS:
        Create a doctest setup with a single user::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
            sage: dev._wrap("_is_master_uptodate")
        Initially ``master`` is up to date::
            sage: dev._is_master_uptodate()
            True

        When the remote ``master`` branches changes, this is not the case
        anymore::

            sage: server.git.super_silent.commit(allow_empty=True, message="a commit")
            sage: dev._is_master_uptodate()
            False
            sage: dev._is_master_uptodate(action_if_not="warning")
            Your version of sage, i.e., your "master" branch, is out of date. Your command might fail or produce unexpected results.
            False
            sage: dev._is_master_uptodate(action_if_not="error")
            ValueError: Your version of sage, i.e., your "master" branch, is out of date.

        We upgrade the local master::

            sage: dev.pull(ticket_or_remote_branch="master", branch="master")
            Merging the remote branch "master" into the local branch "master".
            sage: dev._is_master_uptodate()
            True
            sage: dev._is_master_uptodate(action_if_not="warning")
            True
            sage: dev._is_master_uptodate(action_if_not="error")
            True
        """
        remote_master = self._remote_branch_for_branch(MASTER_BRANCH)
        if remote_master is not None:
            self.git.fetch(self.git._repository_anonymous, remote_master)
            # In the transition from hg to git we are using
            # public/sage-git/master instead of master on the remote end.
            # This check makes sure that we are not printing any confusing
            # messages unless master is actually the latest (development)
            # version of sage.
            if self.git.is_child_of('FETCH_HEAD', MASTER_BRANCH):
                if self.git.commit_for_ref('FETCH_HEAD') != self.git.commit_for_branch(MASTER_BRANCH):
                    info = 'To upgrade your "{0}" branch to the latest version, use "{1}".'.format(MASTER_BRANCH, self._format_command("pull", ticket_or_branch=remote_master, branch=MASTER_BRANCH))
                    if action_if_not is None:
                        pass
                    elif action_if_not == "error":
                        self._UI.debug(info)
                        raise SageDevValueError('Your version of sage, i.e., your "{0}" branch, is out of date.'.format(MASTER_BRANCH))
                    elif action_if_not == "warning":
                        self._UI.warning('Your version of sage, i.e., your "{0}" branch, is out of date. Your command might fail or produce unexpected results.'.format(MASTER_BRANCH))
                        self._UI.debug(info)
                    else:
                        raise ValueError
                    return False
        return True
            sage: dev._is_ticket_name('')
            False
        if name is None:
            return False
            SageDevValueError: "1 000" is not a valid ticket name.
            SageDevValueError: "master" is not a valid ticket name.
            SageDevValueError: "1073741824" is not a valid ticket name or ticket does not exist on trac.
                raise SageDevValueError('"{0}" is not a valid ticket name or ticket does not exist on trac.'.format(name))
                raise SageDevValueError('"{0}" is not a valid ticket name.'.format(name))
            SageDevValueError: "1 000" is not a valid ticket name.
            if isinstance(ticket, str) and ticket and ticket[0] == "#":
                raise SageDevValueError('"{0}" is not a valid ticket name.'.format(name))
            raise SageDevValueError('"{0}" is not a valid ticket name.'.format(name))
        # branches which could be tickets are calling for trouble - cowardly refuse to accept them
        if self._is_ticket_name(name):
            return False
        if name in ["None", "True", "False", "dependencies"]:
            return False
        - ``exists`` -- a boolean or ``any`` (default: ``any``), if ``True``,
        # branches which could be tickets are calling for trouble - cowardly refuse to accept them
        if self._is_ticket_name(name):
            return False
            self.git.super_silent.ls_remote(self.git._repository_anonymous, "refs/heads/"+name, exit_code=True)
            SageDevValueError: "" is not a valid name for a local branch.
            SageDevValueError: Branch "ticket/1" does not exist locally.
            SageDevValueError: Branch "ticket/1" already exists, please choose a different name.
            raise SageDevValueError('"{0}" is not a valid name for a local branch.'.format(name))
                raise SageDevValueError('Branch "{0}" does not exist locally.'.format(name))
                raise SageDevValueError('Branch "{0}" already exists, please choose a different name.'.format(name))
            SageDevValueError: "" is not a valid name for a remote branch.
            SageDevValueError: Branch "ticket/1" does not exist on the remote system.
            raise SageDevValueError('"{0}" is not a valid name for a remote branch.'.format(name))
                raise SageDevValueError('Branch "{0}" does not exist on the remote system.'.format(name))
                raise SageDevValueError('Branch "{0}" already exists, please choose a different name.'.format(name))
            SageDevValueError: "master" is not a valid ticket name.
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
            Created ticket #1 at https://trac.sagemath.org/1.
            sage: dev.checkout(ticket=1)
            self._UI.warning('Ticket #{0} refers to the non-existant local branch "{1}". If you have not manually interacted with git, then this is a bug in sagedev. Removing the association from ticket #{0} to branch "{1}".'.format(ticket, branch))
    def _local_branch_for_ticket(self, ticket, pull_if_not_found=False):
        - ``pull_if_not_found`` -- a boolean (default: ``False``), whether
          to attempt to pull a branch for ``ticket`` from trac if it does
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: alice.checkout(ticket=1)
            sage: alice._sagedev._local_branch_for_ticket(1)
        If no local branch exists, the behaviour depends on ``pull_if_not_found``::
            sage: bob._sagedev._local_branch_for_ticket(1)
            sage: bob._sagedev._local_branch_for_ticket(1, pull_if_not_found=True)
            sage: attributes = alice.trac._get_attributes(1)
            sage: alice.trac._authenticated_server_proxy.ticket.update(1, "", attributes)
            sage: bob._sagedev._local_branch_for_ticket(1, pull_if_not_found=True)
            SageDevValueError: Branch "public/ticket/1" does not exist on the remote system.
            sage: bob._sagedev._local_branch_for_ticket(1, pull_if_not_found=True)
            sage: bob._sagedev._local_branch_for_ticket(1)
        if not pull_if_not_found:
        self.pull(ticket, branch)
        return self._local_branch_for_ticket(ticket, pull_if_not_found=False)
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: dev._set_dependencies_for_ticket(1, [2, 3])
            sage: dev._dependencies_for_ticket(1)
            sage: dev._set_dependencies_for_ticket(1, None)
            sage: dev._dependencies_for_ticket(1)
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev.checkout(ticket=1)
            sage: dev._set_dependencies_for_ticket(1, [2, 3])
            sage: dev._dependencies_for_ticket(1)
            sage: dev._set_dependencies_for_ticket(1, None)
            sage: dev._dependencies_for_ticket(1)
            SageDevValueError: Branch "ticket/1" does not exist locally.
        TESTS::
            sage: dev._sagedev._format_command('checkout')
            'sage --dev checkout'
            sage: dev._sagedev._format_command('checkout', ticket=int(1))
            'sage --dev checkout --ticket=1'
            kwargs = [ "--{0}{1}".format(str(key.split("_or_")[0]).replace("_","-"),"="+str(kwargs[key]) if kwargs[key] is not True else "") for key in kwargs ]
            return "sage --dev {0} {1}".format(command.replace("_","-"), " ".join(args+kwargs)).rstrip()
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            1
            sage: dev._current_ticket()
            sage: dev.checkout(ticket=1)

        sage: dev.checkout(ticket=-1)
        ValueError: "-1" is not a valid ticket name or ticket does not exist on trac.