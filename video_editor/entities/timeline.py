"""
This entity represents the final timeline.
"""
from lxml import etree
import os


class Timeline():
    def __init__(self, videos_folder):
        self.fcpxml = etree.Element('fcpxml', version="1.11")
        self.tree = etree.ElementTree(self.fcpxml)
        self.spine = None
        self.video_assets_refs = []
        self.video_assets = {}

        self.output_folder = os.path.join(videos_folder, 'timeline')
        self.fcpxml_filename = os.path.join(self.output_folder, 'timeline.fcpxml')


    def add_default_header(self, file):
        """
        Add the default header to the FCPXML file.
        """
        file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(b'<!DOCTYPE fcpxml>\n')


    def generate_fcpxml_file(self):
        """
        Create the FCPXML file.
        """
        os.makedirs(self.output_folder, exist_ok=True)

        with open(self.fcpxml_filename, 'wb') as file:
            # Write default configuration in file
            self.add_default_header(file)

            # Indent the tree to 4 spaces
            etree.indent(self.tree, space='    ')

            # Add FCPXML tree to the file
            self.tree.write(file, encoding='UTF-8', pretty_print=True)

        print("FCPXML file created successfully.")
