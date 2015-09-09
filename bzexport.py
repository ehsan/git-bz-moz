# Copyright (C) 2010 Mozilla Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


# Extracted from __init__.py from bzexport.


import os
import platform
import time
import urllib
import urllib2
import json
from mercurial import config, demandimport, util
from mercurial.i18n import _
try:
    import cPickle as pickle
except:
    import pickle
import bz
import bzauth

# requests doesn't like lazy importing
demandimport.disable()
import requests
demandimport.enable()

from auth import (
    getbugzillaauth,
    win_get_folder_path,
)

# For some reason hgexport calls the user cache the INI_CACHE_FILENAME.
INI_CACHE_FILENAME = ".gitbz.user.cache"

# Returns [ { search_string: original, names: [ str ], real_names: [ str ] } ]
def find_users(ui, api_server, user_cache_filename, auth, search_strings):
    c = bzauth.load_user_cache(ui, api_server, user_cache_filename)
    section = api_server

    search_results = []
    for search_string in search_strings:
        name = c.get(section, search_string)
        if name:
            search_results.append({"search_string": search_string,
                                   "names": [name],
                                   "real_names": ["not_a_real_name"]})
            continue

        try:
            try:
                users = bz.find_users(auth, search_string)
            except Exception as e:
                raise util.Abort(e.message)
            name = None
            real_names = map(lambda user: "%s <%s>" % (user["real_name"], user["email"])
                             if user["real_name"] else user["email"], users["users"])
            names = map(lambda user: user["name"], users["users"])
            search_results.append({"search_string": search_string,
                                   "names": names,
                                   "real_names": real_names})
            if len(real_names) == 1:
                c.set(section, search_string, names[0])
        except Exception, e:
            search_results.append({"search_string": search_string,
                                   "error": str(e),
                                   "real_names": None})
            raise
    bzauth.store_user_cache(c, user_cache_filename)
    return search_results


def prompt_manychoice(ui, message, prompts):
    while True:
        choice = ui.prompt(message, default='default')
        if choice == 'default':
            return 0
        choice = '&' + choice
        if choice in prompts:
            return prompts.index(choice)
        ui.write("unrecognized response\n")


def prompt_menu(ui, name, values,
                readable_values=None,
                message='',
                allow_none=False):
    if message and not message.endswith('\n'):
        message += "\n"
    prompts = []
    for i in range(0, len(values)):
        prompts.append("&" + str(i + 1))
        value = (readable_values or values)[i]
        message += "  %d. %s\n" % ((i + 1), value.encode('utf-8', 'replace'))
    if allow_none:
        prompts.append("&n")
        message += "  n. None\n\n"
    prompts.append("&a")
    message += "  a. Abort\n\n"
    message += _("Select %s:") % name

    choice = prompt_manychoice(ui, message, prompts)

    if allow_none and choice == len(prompts) - 2:
        return None
    if choice == len(prompts) - 1:
        raise util.Abort("User requested abort while choosing %s" % name)
    return values[choice]


def multi_user_prompt(ui, desc, search_results):
    return prompt_menu(ui, desc, search_results['names'],
                       readable_values=search_results['real_names'],
                       message="Multiple bugzilla users matching \"%s\":\n\n" % search_results["search_string"],
                       allow_none=True)

# search_strings is a simple list of strings
def validate_users(ui, api_server, auth, search_strings, multi_callback, multi_desc):
    search_results = find_users(ui, api_server, INI_CACHE_FILENAME, auth, search_strings)
    search_failed = False
    results = {}
    for search_result in search_results:
        if search_result["real_names"] is None:
            ui.write_err("Error: couldn't find user with search string \"%s\": %s\n" %
                         (search_result["search_string"], search_result["error"]))
            search_failed = True
        elif len(search_result["real_names"]) > 10:
            ui.write_err("Error: too many bugzilla users matching \"%s\":\n\n" % search_result["search_string"])
            for real_name in search_result["real_names"]:
                ui.write_err("  %s\n" % real_name.encode('ascii', 'replace'))
            search_failed = True
        elif len(search_result["real_names"]) > 1:
            user = multi_callback(ui, multi_desc, search_result)
            if user is not None:
                results[search_result['search_string']] = [user]
        elif len(search_result["real_names"]) == 1:
            results[search_result['search_string']] = search_result['names']
        else:
            ui.write_err("Couldn't find a bugzilla user matching \"%s\"!\n" % search_result["search_string"])
            search_failed = True
    return None if search_failed else results


def select_users(valid, keys):
    if valid is None:
        return None
    users = []
    for key in keys:
        users.extend(valid[key])
    return users


def flag_type_id(ui, api_server, config_cache_filename, flag_name, product, component):
    """
    Look up the numeric type id for the 'review' flag from the given bugzilla server
    """
    configuration = bzauth.load_configuration(ui, api_server, config_cache_filename)
    if not configuration or not configuration["flag_type"]:
        raise util.Abort(_("Could not find configuration object"))

    # Get the set of flag ids used for this product::component
    prodflags = configuration['product'][product]['component'][component]['flag_type']
    flagdefs = configuration['flag_type']

    flag_ids = [id for id in prodflags if flagdefs[str(id)]['name'] == flag_name]

    if len(flag_ids) != 1:
        raise util.Abort(_("Could not find unique %s flag id") % flag_name)

    return flag_ids[0]
