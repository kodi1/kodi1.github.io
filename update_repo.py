from helper import *


addons = get_addons_list()
updated_addons = []

for addon in addons:
    if is_updated(addon):
        updated_addons.append(addon)
        temp_addon_path = download(addon)
        if not temp_addon_path:
            continue
        copy_to_repo(temp_addon_path, addon)

deleted_folders_count = delete_orphan_addon_folders(addons)

if len(updated_addons) == 0 and deleted_folders_count == 0:
    log("No new addons found!")
    log("Skipping repo update!")
    sys.exit(0)

generate_addonsxml(addons)
generate_md5_file()
update_last_update_time()
update_readme(updated_addons)

