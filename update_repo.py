from helper import *

addons = get_enabled_addons()
updated_addons = []
failed_addons_count = 0

for addon in addons:
    if should_update(addon) and download(addon):
        if update(addon):
            updated_addons.append(addon)
        else:
            failed_addons_count += 1

update_last_update_time()
deleted_folders_count = delete_orphan_addon_folders(addons)

if len(updated_addons) == 0 and deleted_folders_count == 0:
    log("No new addons found!")
    log("Skipping repo update!")
else:
    generate_addons_xml_file(addons)
    generate_md5_file()
    update_readme(updated_addons)

if failed_addons_count > 0:
    log("Some addons failed to update. Check the log for details!. Leaving temp folder intact %s" % get_temp_folder())
else:
    try_delete_folder(get_temp_folder())