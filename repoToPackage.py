import xml.etree.ElementTree as ET
from git import Repo
from collections import defaultdict
import re
import os
from xml.dom import minidom
from sfdx_utils import get_metadata_info

def pretty_print_xml(elem, indent="    ", level=0):
    i = "\n" + level * indent
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            pretty_print_xml(elem, indent, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def create_package_file(components_by_type, output_filename):
    try:
        namespace = "http://soap.sforce.com/2006/04/metadata"
        ET.register_namespace('', namespace)
        
        manifest = None
        if os.path.exists(output_filename):
            print(f"Modifying existing manifest file '{output_filename}'...")
            try:
                tree = ET.parse(output_filename)
                manifest = tree.getroot()
                #manifest.set('xmlns', namespace)
            except ET.ParseError:
                print(f"Warning: Existing file '{output_filename}' is empty or corrupted. Creating a new one.")
                manifest = None

        if manifest is None:
            print(f"Creating new manifest file '{output_filename}'...")
            manifest = ET.Element("Package", xmlns=namespace)
            ET.SubElement(manifest, "version").text = "64.0"

        for metadata_type, component_names in components_by_type.items():
            types_elem = manifest.find(f"{{{namespace}}}types[{{{namespace}}}name='{metadata_type}']")

            if types_elem is None:
                types_elem = ET.SubElement(manifest, "types")
                ET.SubElement(types_elem, "name").text = metadata_type

            existing_members = {member.text for member in types_elem.findall(f'{{{namespace}}}members')}
        
            for name in sorted(list(component_names)):
                if name not in existing_members:
                    ET.SubElement(types_elem, "members").text = name

        pretty_print_xml(manifest)
   
        tree = ET.ElementTree(manifest)
        tree.write(output_filename, encoding='utf-8', xml_declaration=True)
        print(f"Manifest file '{output_filename}' updated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

def get_squash_merge_changes(repo_path, squash_commit_hash, new_filename='package.xml', delete_filename='deletePackage.xml'):
    """
    Compares a squash commit to its parent and creates package.xml files for added/modified
    and deleted components.
    """
    try:
        repo = Repo(repo_path)
        squash_commit = repo.commit(squash_commit_hash)

        if len(squash_commit.parents) != 1:
            print("The specified commit does not appear to be a squash commit (it has more or less than one parent).")
            return

        parent_commit = squash_commit.parents[0]
        diffs = parent_commit.diff(squash_commit)

        print(f"File changes introduced by squash commit {squash_commit_hash[:7]} (compared to its parent {parent_commit.hexsha[:7]}):")
        print(f"Total differences: {len(diffs)}")
        if not diffs:
            print("No file changes detected.")
        else:
            new_components_by_type = defaultdict(set)
            delete_components_by_type = defaultdict(set)
            for diff in diffs:
                change_type = diff.change_type
                old_path = diff.a_path
                new_path = diff.b_path
                
                # new component
                if change_type == 'A':
                    print(f"Added: {new_path}")
                    metadata_type, metadata_name = get_metadata_info(new_path)
                    if metadata_type and metadata_name:
                        new_components_by_type[metadata_type].add(metadata_name)

                # deleted component
                elif change_type == 'D':
                    print(f"Deleted: {old_path}")
                    metadata_type, metadata_name = get_metadata_info(old_path)
                    if metadata_type and metadata_name:
                        delete_components_by_type[metadata_type].add(metadata_name)

                # Modified component
                elif change_type == 'M':
                    print(f"Modified: {new_path}")
                    metadata_type, metadata_name = get_metadata_info(new_path)
                    if metadata_type and metadata_name:
                        new_components_by_type[metadata_type].add(metadata_name)

                # Rename component (deleted as well as created)
                elif change_type == 'R':
                    print(f"Renamed: {old_path} -> {new_path}")
                    metadata_type, metadata_name = get_metadata_info(new_path)
                    if metadata_type and metadata_name:
                        new_components_by_type[metadata_type].add(metadata_name)

                    metadata_type, metadata_name = get_metadata_info(old_path)
                    if metadata_type and metadata_name:
                        delete_components_by_type[metadata_type].add(metadata_name)

            if new_components_by_type:
                print("New components or Modified components found creating package")
                create_package_file(new_components_by_type, new_filename)
            if delete_components_by_type:
                print("Deleted components found creating package")
                create_package_file(delete_components_by_type, delete_filename)
    except Exception as e:
        print(f"An error occurred: {e}")

repo_path = 'C:/Users/Downloads/example/' # path of resitory with correct branch in local machine
squash_hash_list = ['commithash'] # list of commit hash to the branch
package = 'package.xml' # name of the package file to be created
delete_filename = 'deletePackage.xml' # name of the delete package file to be created
for i,squash_hash in enumerate(squash_hash_list):
    get_squash_merge_changes(repo_path, squash_hash, package, delete_filename) #give the file names

