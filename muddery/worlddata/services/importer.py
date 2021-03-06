"""
This module imports data from files to db.
"""

import os, glob, tempfile, zipfile, shutil
from django.conf import settings
from muddery.server.upgrader.upgrade_handler import UPGRADE_HANDLER
from muddery.server.launcher import configs
from muddery.server.launcher.utils import copy_tree
from muddery.worlddata.services.data_importer import import_file
from muddery.worlddata.dao import model_mapper


def unzip_data_all(fp):
    """
    Import all data files from a zip file.
    """
    temp_path = tempfile.mkdtemp()

    try:
        archive = zipfile.ZipFile(fp, 'r')
        archive.extractall(temp_path)
        source_path = temp_path
        
        # if the zip file contains a root dir
        file_list = os.listdir(temp_path)
        if len(file_list) == 1:
            path = os.path.join(temp_path, file_list[0])
            if os.path.isdir(path):
                source_path = path

        # Upgrade game data.
        UPGRADE_HANDLER.upgrade_data(source_path, None, configs.MUDDERY_LIB)

        # import data from path
        import_data_path(source_path)

        # load system localized strings
        # system data file's path
        system_data_path = os.path.join(settings.MUDDERY_DIR, settings.WORLD_DATA_FOLDER)

        # localized string file's path
        system_localized_string_path = os.path.join(system_data_path,
                                                    settings.LOCALIZED_STRINGS_FOLDER,
                                                    settings.LANGUAGE_CODE)

        # load data
        import_table_path(system_localized_string_path, settings.LOCALIZED_STRINGS_MODEL)

        # load custom localized strings
        # custom data file's path
        custom_localized_string_path = os.path.join(source_path, settings.LOCALIZED_STRINGS_MODEL)

        file_names = glob.glob(custom_localized_string_path + ".*")
        if file_names:
            print("Importing %s" % file_names[0])
            try:
                import_file(file_names[0], table_name=settings.LOCALIZED_STRINGS_MODEL, clear=False)
            except Exception as e:
                print("Import error: %s" % e)

    finally:
        shutil.rmtree(temp_path)


def unzip_resources_all(fp):
    """
    Import all resource files from a zip file.
    """
    media_dir = os.path.join(settings.MEDIA_ROOT, settings.IMAGE_PATH)
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    temp_path = tempfile.mkdtemp()

    try:
        archive = zipfile.ZipFile(fp, 'r')
        archive.extractall(temp_path)
        source_path = temp_path
        
        # if the zip file contains a root dir
        file_list = os.listdir(temp_path)
        if len(file_list) == 1:
            path = os.path.join(temp_path, file_list[0])
            if os.path.isdir(path):
                source_path = path

        copy_tree(source_path, media_dir)

    finally:
        shutil.rmtree(temp_path)


def import_data_path(path, clear=True):
    """
    Import data from path.

    Args:
        path: (string) data path.
    """

    # import tables one by one
    models = model_mapper.get_all_models()
    for model in models:
        table_name = model.__name__
        file_names = glob.glob(os.path.join(path, table_name) + ".*")

        if file_names:
            print("Importing %s" % file_names[0])
            try:
                import_file(file_names[0], table_name=table_name, clear=clear)
            except Exception as e:
                print("Import error: %s" % e)


def import_table_path(path, table_name, clear=True):
    """
    Import a table's data from a path.
    """
    # clear old data
    model = model_mapper.get_model(table_name)
    if not model:
        return

    if clear:
        model.objects.all().delete()

    if not os.path.isdir(path):
        return

    for file_name in os.listdir(path):
        file_name = os.path.join(path, file_name)
        if os.path.isdir(file_name):
            # if it is a folder
            continue

        print("Importing %s" % file_name)
        try:
            import_file(file_name, table_name=table_name, clear=False)
        except Exception as e:
            print("Import error: %s" % e)
