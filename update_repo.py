from helper import *


addons = get_addons_list()

for addon in addons:
    if is_updated(addon):
        temp_addon_path = download(addon)
        if not temp_addon_path:
            continue
        copy_to_repo(temp_addon_path, addon)

delete_orphan_addon_folders(addons)
generate_addonsxml(addons)
generate_md5_file()
update_last_update_time()
update_readme()
