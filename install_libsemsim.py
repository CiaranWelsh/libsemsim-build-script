import os, glob, sys
import requests
import tarfile
import subprocess
import argparse

WORKING_DIRECTORY = os.path.dirname(__file__)

if sys.platform != "linux":
    raise ValueError("Non linux builds are not yet supported for libsemsim."
                     "Note, this script is not a long term solution "
                     "but a tool to allow collaborators quick "
                     "access while a CMake script is being generated "
                     "for the dependencies")


def dependency_urls():
    return {
        "tar": {
            "raptor2-2.0.15": "http://download.librdf.org/source/raptor2-2.0.15.tar.gz",
            "rasqal-0.9.33": "http://download.librdf.org/source/rasqal-0.9.33.tar.gz",
            "redland-1.0.17": "http://download.librdf.org/source/redland-1.0.17.tar.gz",
        },
        "git": {
            "libsemsim": "https://github.com/sys-bio/libsemsim.git"
        }
    }


def download_locations():
    dct = {}
    for download_type, download_dct in dependency_urls().items():
        dct[download_type] = {}
        if download_type == "tar":
            for package_name, package_url in download_dct.items():
                dct[download_type][package_name] = os.path.join(WORKING_DIRECTORY, package_name + ".tar.gz")
        elif download_type == "git":
            for package_name, package_url in download_dct.items():
                dct[download_type][package_name] = os.path.join(WORKING_DIRECTORY, package_name)
        else:
            raise ValueError("Nope")
    return dct


def extraction_locations():
    dct = {}
    for download_type, download_dct in dependency_urls().items():
        dct[download_type] = {}
        if download_type == "tar":
            for package_name, package_url in download_dct.items():
                dct[download_type][package_name] = os.path.join(WORKING_DIRECTORY, package_name)
        elif download_type == "git":
            pass
        else:
            raise ValueError("Nope")
    return dct


#
# def install_locations():
#     dct = {}
#     for download_type, download_dct in extraction_locations().items():
#         dct[download_type] = {}
#         if download_type == "tar":
#             for package_name, location_on_disk in download_dct.items():
#                 dct[download_type][package_name] = os.path.join(location_on_disk, package_name + "install")
#         else:
#             continue
#     return dct


def install_apt_get_deps():
    os.system("sudo apt install -y automake autotools-dev "
              "autoconf libtool gtk-doc-tools libxml2 libxml2-dev "
              "autogen")


def get_deps():
    for download_type, download_dct in dependency_urls().items():
        if download_type == "tar":
            for package, url in download_dct.items():
                print(f'downloading "{package}"')
                if os.path.isfile(download_locations()[download_type][package]):
                    continue
                with requests.get(url) as handle:
                    with open(download_locations()[download_type][package], 'wb') as f:
                        f.write(handle.content)

        elif download_type == "git":
            for package, url in download_dct.items():
                if os.path.isdir(url):
                    continue
                try:
                    os.system(f"git clone {url}")
                except subprocess.CalledProcessError:
                    raise ValueError(f"was unable to download using \"git clone \"")

        else:
            raise ValueError("nope")


def extract_tars():
    dct = {}
    for download_type, package_dct in download_locations().items():
        if download_type == "tar":
            for package_name, tar_path in package_dct.items():
                if os.path.isdir(tar_path):
                    continue
                print(f"untaring {package_name}")
                with tarfile.open(tar_path) as tarball:
                    tarball.extractall()


def get_folder_location(which='raptor2'):
    if which not in ["raptor2", "rasqal", "librdf"]:
        raise ValueError()

    glob_pattern = ""
    if which == "raptor2":
        glob_pattern = os.path.join(WORKING_DIRECTORY, "raptor2*")
    elif which == "rasqal":
        glob_pattern = os.path.join(WORKING_DIRECTORY, "rasqal*")
    elif which == "librdf":
        glob_pattern = os.path.join(WORKING_DIRECTORY, "redland*")
    else:
        raise ValueError

    dir = glob.glob(glob_pattern)
    dir = [i for i in dir if os.path.isdir(i)]
    if not len(dir) == 1:
        raise ValueError("Nopy")
    return dir[0]


def build_automake(directory, configure_script, additional_args=""):
    if not os.path.isdir(directory):
        raise ValueError(f"Not directory named {directory}")

    if not os.path.isfile(configure_script):
        raise ValueError(f"No file named {configure_script}")

    current_directory = os.getcwd()
    os.chdir(directory)

    autogen_command = f'{configure_script} ' \
                      f'{additional_args}'
    make_command = f"make"
    install_command = f"echo Nabduj123 | sudo -kS make install"
    full_command = f'{autogen_command} && {make_command} && {install_command}'
    os.system(full_command)
    os.chdir(current_directory)


def build_raptor():
    raptor2_dir = get_folder_location("raptor2")
    autogen_script = os.path.join(raptor2_dir, "autogen.sh")
    build_automake(raptor2_dir, autogen_script)


def build_rasqal():
    rasqal_dir = get_folder_location("rasqal")
    autogen_script = os.path.join(rasqal_dir, "autogen.sh")
    build_automake(rasqal_dir, autogen_script)


def build_librdf():
    librdf_dir = get_folder_location("librdf")
    autogen_script = os.path.join(librdf_dir, "autogen.sh")
    build_automake(librdf_dir, autogen_script)


def build_libsemsim():
    current_directory = os.getcwd()
    libsemsim_dir = glob.glob(os.path.join(WORKING_DIRECTORY, "libsemsim"))
    if not len(libsemsim_dir) == 1:
        raise ValueError
    libsemsim_dir = libsemsim_dir[0]
    os.chdir(libsemsim_dir)
    os.system("git checkout tags/v0.1.0")
    cmd = "mkdir -p build_libsemsim && " \
          "cd build_libsemsim && " \
          "cmake .. && " \
          "make && " \
          "echo Nabduj123 | sudo -kS make install "
    os.system(cmd)
    os.chdir(current_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='password',
                        type=str, required=True,
                        help="Linux sudo password. Used "
                             "for installing redland libraries into "
                             "standard location")
    args = parser.parse_args()

    get_deps()
    # extract_tars()
