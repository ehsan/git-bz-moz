git-bz-moz
==========

A fork of the git-bz tool with a few tweaks specific to bugzilla.mozilla.org, and other fixes not upstreamed.

To authenticate, you need to specify your bugzilla user name and API key.

You can set your bugzilla user name by running:
  git config --global bz.username <your username>

An API key can be obtained here:
  https://bugzilla.mozilla.org/userprefs.cgi?tab=apikey
Once obtained, set the API key by running:
  git config --global bz.apikey <your bugzilla API key>

Some code is imported from the Mozilla version-control-tools repository, revision 35edcee4c73415fa45ff95ed07bb8129d41821f9
The repository is located at https://hg.mozilla.org/hgcustom/version-control-tools/
  - auth.py is copied from pylib/mozhg/mozhg/
  - bz.py and bzauth.py are copied from hgext/bzexport/
  - bzexport.py is a few pieces of code copied from hgext/bzexport/__init__.py

In addition, a patch to bzauth.py for bug 1336147 was manually applied.