from helper import *

addons = get_addons_list()
updated_addons_list = []
files_to_copy = ["addon.xml", "icon.png", "changelog.txt" ]

for addon in addons:
    if is_updated(addon):
        temp_addon_file = download(addon)
        if not temp_addon_file:
            continue
        temp_addon_folder = extract_addon_content(addon["name"], temp_addon_file)
        for file in files_to_copy:
            copy_file(os.path.join(temp_addon_folder, file), os.path.join(addon["folder"], file))

        addon["new_version"] = get_addon_version_from_xml_file(os.path.join(temp_addon_folder, "addon.xml"))
        new_addon_file_name = create_new_addon_file_name(addon["name"], addon["new_version"])
        copy_file(temp_addon_file, os.path.join(addon["folder"], new_addon_file_name))
        log("Updated addon \033[1;32m%s\033[0m\n " % addon["name"])
        updated_addons_list.append(addon)

update_last_update_time()
deleted_folders_count = delete_orphan_addon_folders(addons)

if len(updated_addons_list) == 0 and deleted_folders_count == 0:
    log("No new addons found!")
    log("Skipping repo update!")
    sys.exit(0)

generate_addonsxml(addons)
generate_md5_file()
update_readme(updated_addons_list)
