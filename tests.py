import unittest, glob, os

import install_libsemsim

class BuildTests(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_download_packages(self):
        install_libsemsim.get_deps()
        dirs = glob.glob("*")

    def test_install_apt_get_packages(self):
        install_libsemsim.install_apt_get_deps()

    def test_extract_tars(self):
        install_libsemsim.extract_tars()

    def test_build_raptor(self):
        install_libsemsim.build_raptor()

    def test_build_rasqal(self):
        install_libsemsim.build_rasqal()

    def test_build_librdf(self):
        install_libsemsim.build_librdf()

    def test_build_libsemsim(self):
        install_libsemsim.build_libsemsim()
