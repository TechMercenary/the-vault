import unittest
from tkinter import Tk
from menu import AppMenu

class TestMenu(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.menu = AppMenu(self.root)

    def test_file_menu(self):
        file_menu = self.menu.get_file_menu()
        self.assertIsNotNone(file_menu, "File menu not found")

    def test_edit_menu(self):
        edit_menu = self.menu.get_edit_menu()
        self.assertIsNotNone(edit_menu, "Edit menu not found")

    def test_help_menu(self):
        help_menu = self.menu.get_reports_menu()
        self.assertIsNotNone(help_menu, "Reports menu not found")

    def tearDown(self):
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()
