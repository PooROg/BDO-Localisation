import os
import urllib.request
import configparser
import shutil
import tempfile
import struct
import zlib
from collections import OrderedDict


# Sheet IDs:
# 1 = GAME
# 2 = RESOURCE
# 3 = ACTIONCHART
# 4 = TOOL
# 5 = WEB


class Translation(object):
    def __init__(self):
        self.str_type = 0  # int, 0 - 78
        self.key1 = 0  # int, can be string hash
        self.key2 = 0  # short, can be sheet id
        self.key3 = 0  # signed byte
        self.string_no = 0  # unsigned byte
        self.str_source = None
        self.str_translation = ''
        self.region_word = ''
        self.npc_info = ''

    @property
    def index(self):
        return self.str_type, self.key1, self.key2, self.key3, self.string_no

    def from_string(self, string):
        parts = string.split('\t')
        assert len(parts) == 9 or len(parts) == 6
        self.str_type = int(parts[0])
        self.key1 = int(parts[1])
        self.key2 = int(parts[2])
        self.key3 = int(parts[3])
        self.string_no = int(parts[4])
        if len(parts) == 9:
            self.str_source = parts[5].replace('\\t', '\t').replace('\\n', '\n')
            self.str_translation = parts[6]
            self.region_word = parts[7]
            self.npc_info = parts[8]
        else:
            self.str_source = None
            self.str_translation = parts[5]
        self.str_translation = self.str_translation.replace('\\t', '\t').replace('\\n', '\n')

    def to_string(self):
        string = self.str_translation.replace('\t', '\\t').replace('\n', '\\n')
        if self.str_source is None:
            return f'{self.str_type}\t{self.key1}\t{self.key2}\t{self.key3}\t{self.string_no}\t{string}\n'
        else:
            string_source = self.str_source.replace('\t', '\\t').replace('\n', '\\n')
            return f'{self.str_type}\t{self.key1}\t{self.key2}\t{self.key3}\t{self.string_no}\t{string_source}\t{string}\t{self.region_word}\t{self.npc_info}\n'

    def from_bytes(self, data: memoryview):
        self.str_source = None
        str_size = struct.unpack('=I', data[:4].tobytes())[0]
        self.str_type, self.key1, self.key2, self.key3, self.string_no, self.str_translation, unk1 = \
            struct.unpack(f'=IihbB{str_size * 2}sI', data[4:4 + str_size * 2 + 16].tobytes())
        self.str_translation = self.str_translation.decode('utf-16le')
        assert unk1 == 0
        return 16 + str_size * 2 + 4

    def to_bytes(self):
        str_translation = self.str_translation
        if not str_translation:
            # Replace missing translations with translation information so we can find them and fix them.
            str_translation = f'<{self.str_type},{self.key1},{self.key2},{self.key3},{self.string_no}>'
        return struct.pack(
            f'=IIihbB{len(self.str_translation) * 2}sI', len(str_translation), self.str_type, self.key1,
            self.key2, self.key3, self.string_no, str_translation.encode('utf-16le'), 0)

    def __hash__(self):
        return hash((self.str_type, self.key1, self.key2, self.key3, self.string_no))


def read_from_txt(file_name, max_type):
    translations = OrderedDict()
    with open(file_name, 'r', encoding='utf-8') as fp:
        for ln in fp:
            ln = ln.strip('\r\n')
            if ln:
                translation = Translation()
                translation.from_string(ln)
                if translation.str_type <= max_type:
                    translations[translation] = translation
    return translations.values()


def save_to_txt(file_name, translations):
    with open(file_name, 'w+', encoding='utf-8') as fp:
        for translation in translations:
            fp.write(translation.to_string())


def read_from_loc(file_name, max_type):
    translations = []
    with open(file_name, 'rb') as fp:
        n = struct.unpack('I', fp.read(4))[0]  # uncompressed_length
        data = fp.read()
        data = zlib.decompress(data)
        assert len(data) == n
        data = memoryview(data)
    i = 0
    while i < len(data):
        translation = Translation()
        i += translation.from_bytes(data[i:])
        if translation.str_type <= max_type:
            translations.append(translation)
    return translations


def save_to_loc(file_name, translations):
    entries = []
    for translation in translations:
        entries.append(translation.to_bytes())
    with open(file_name, 'w+b') as fp:
        data = b''.join(entries)
        fp.write(struct.pack('I', len(data)))
        fp.write(zlib.compress(data, 1))


def get_region_from_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    res_value = config.get('SERVICE', 'RES')
    language_code = res_value.strip('_').lower()
    return language_code


def download_file(url, destination_folder):
    response = urllib.request.urlopen(url)
    destination = os.path.join(destination_folder, os.path.basename(url))
    with open(destination, 'wb') as file:
        file.write(response.read())
    return destination


def copy_unique_category_lines(original_file, translated_file):
    # Create a set to store unique identifiers from the translated file
    existing_ids = set()

    # Read the first 5 digits in lines from the translated file
    with open(translated_file, 'r', encoding='utf-8') as trans:
        for line in trans:
            parts = line.split('\t')
            if len(parts) >= 5:
                ids = tuple(parts[:5])
                existing_ids.add(ids)

    # Read the original file and copy missing lines by comparing the first five digits
    with open(original_file, 'r', encoding='utf-8') as orig, open(translated_file, 'a', encoding='utf-8') as trans:
        for line in orig:
            parts = line.split('\t')
            if len(parts) >= 5:
                ids = tuple(parts[:5])
                if ids not in existing_ids:
                    trans.write(line)


def modify_lines(txt_file, categories, group3_old, group3_new):
    with open(txt_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(txt_file, 'w', encoding='utf-8') as file:
        for line in lines:
            parts = line.split('\t')
            if len(parts) >= 4 and int(parts[0]) in categories and int(parts[3]) == group3_old:
                parts[3] = str(group3_new)
            file.write('\t'.join(parts))


class PatchUrlNotFoundException(Exception):
    pass


def process_files(region, loc_deep_active):
    # Path to the ads folder
    ads_folder = 'ads'

    # Getting the region from the resource.ini file
    original_region = get_region_from_ini('resource.ini')

    # Path to the edit folder
    edit_folder = tempfile.mkdtemp(prefix='edit_loc_')
    if not os.path.exists(edit_folder):
        os.makedirs(edit_folder)

    try:
        # Getting the download link for the localization file from the service.ini file
        config = configparser.ConfigParser()
        config.read('service.ini', encoding='utf-8')
        patch_url = None
        for section in config.sections():
            if config.has_option(section, 'PATCH_URL'):
                patch_url = config.get(section, 'PATCH_URL')
                break
        if patch_url is None:
            raise PatchUrlNotFoundException()

        # Paths to localization files
        original_loc_path = download_file(f'{patch_url}ads/languagedata_{original_region}.loc', edit_folder)
        original_txt_path = os.path.join(edit_folder, f'languagedata_{original_region}.txt')
        translated_txt_path = os.path.join(edit_folder, f'languagedata_translated_{region}.txt')
        translated_loc_path = os.path.join(tempfile.gettempdir(), f'languagedata_translated_{region}.loc')
        translated_loc_new_path = os.path.join(ads_folder, f'languagedata_{original_region}.loc')

        # Checking the region and setting the corresponding link to download the localization file
        download_url = {
            'ru': 'http://nez-o-dn.playblackdesert.com/UploadData/ads/languagedata_ru.loc',
            'en': 'http://naeu-o-dn.playblackdesert.com/UploadData/ads/languagedata_en.loc',
            'de': 'http://naeu-o-dn.playblackdesert.com/UploadData/ads/languagedata_de.loc',
            'fr': 'http://naeu-o-dn.playblackdesert.com/UploadData/ads/languagedata_fr.loc',
            'sp': 'http://naeu-o-dn.playblackdesert.com/UploadData/ads/languagedata_sp.loc',
            'jp': 'http://jpo-o-dn.playblackdesert.com/UploadData/ads/languagedata_jp.loc',
            'es': 'http://sa-o-dn.playblackdesert.com/UploadData/ads/languagedata_es.loc',
            'pt': 'http://sa-o-dn.playblackdesert.com/UploadData/ads/languagedata_pt.loc',
            'tr': 'http://dn.tr.playblackdesert.com/UploadData/ads/languagedata_tr.loc',
            'tw': 'http://dn.blackdesert.com.tw/UploadData/ads/languagedata_tw.loc'
        }.get(region, None)

        # Conversion of the original .loc file to .txt
        original_translations = read_from_loc(original_loc_path, 0xFF)
        save_to_txt(original_txt_path, original_translations)

        # Downloading the localization file
        downloaded_loc_file = download_file(download_url, edit_folder)

        # Conversion of the downloaded .loc file to .txt
        translated_translations = read_from_loc(downloaded_loc_file, 0xFF)
        save_to_txt(translated_txt_path, translated_translations)

        # Advanced translation
        if original_region == 'en':
            if region == 'ru' and loc_deep_active:
                modify_lines(translated_txt_path, [50, 71, 72, 73, 80, 120], 8, 12)
        elif original_region == 'jp':
            if region == 'ru' and loc_deep_active:
                modify_lines(translated_txt_path, [50, 71, 72, 73, 80, 120], 8, 6)
        elif original_region in ['pt', 'es']:
            if region == 'ru' and loc_deep_active:
                modify_lines(translated_txt_path, [50, 71, 72, 73, 80, 120], 8, 16)
        elif original_region == 'tr':
            if region == 'ru' and loc_deep_active:
                modify_lines(translated_txt_path, [50, 71, 72, 73, 80, 120], 8, 12)
        elif original_region == 'tw':
            if region == 'ru' and loc_deep_active:
                modify_lines(translated_txt_path, [50, 71, 72, 73, 80, 120], 14, 12)

        # Copying lines with categories
        copy_unique_category_lines(original_txt_path, translated_txt_path)

        # Conversion of the updated .txt file back to .loc
        translated_translations = read_from_txt(translated_txt_path, 0xFF)
        save_to_loc(translated_loc_path, translated_translations)

        # Moving the converted .loc file back to the ads_folder
        shutil.move(translated_loc_path, translated_loc_new_path)

        shutil.rmtree(edit_folder)
        return original_region
    finally:
        # Deleting the edit folder
        if os.path.exists(edit_folder):
            shutil.rmtree(edit_folder)
