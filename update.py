import bpy
import os
import requests
from pathlib import Path
from bpy.props import BoolProperty

def download_file(url, destination):
    response = requests.get(url)
    with open(destination, 'wb') as file:
        file.write(response.content)

def download_repository_files():
    files = []

    current_directory = Path(__file__).resolve().parent
    for file in current_directory.iterdir():
        if file.name.endswith(".py"):
            files.append(file.name)

    for file in files:
        file_url = f'https://raw.githubusercontent.com/vmcomix/RigUI/master/{file}'
        destination = Path(os.path.split(__file__)[0]) / file
        download_file(file_url, destination)

def latest_commit_sha():
    url = f'https://api.github.com/repos/vmcomix/RigUI/commits/master'
    response = requests.get(url)
    if response.status_code == 200:
        commit_data = response.json()
        latest_commit_sha = commit_data['sha']
        return latest_commit_sha
    else:
            print(f'Error getting latest commit. Status code: {response.status_code}')
            return None

class RigUIAddonUpdate(bpy.types.Operator):
    bl_idname = "pose.rigui_update_addon"
    bl_label = "Update add-on"
    bl_description = "Download and install new version."
    bl_options = {"REGISTER"}

    check_update: BoolProperty(default=False)

    update: BoolProperty(default=False)

    def execute(self, context):

        current_directory = Path(__file__).resolve().parent

        if self.check_update:
            current_directory = Path(__file__).resolve().parent
            if Path(current_directory / "hash" / latest_commit_sha()).exists():
                context.preferences.addons["RigUI"].preferences.update = "Up to date"
            else:
                context.preferences.addons["RigUI"].preferences.update = "Update available"
            self.check_update = False
        elif self.update:

            hash = None
            for file in Path(current_directory / "hash").iterdir():
                hash = file.stem
                break

            if hash:
                old_hash = current_directory / "hash" / hash
            new_hash = current_directory / "hash" /latest_commit_sha()

            if hash:
                old_hash.rename(new_hash)
            else:
                with open(current_directory / new_hash, 'w') as file:
                    pass
            download_repository_files()

            context.preferences.addons["RigUI"].preferences.update = "Updated!"
            self.update = False
            bpy.ops.script.reload()


        return {'FINISHED'}
