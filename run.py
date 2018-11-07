import os
import zipfile
import re
import json
import shutil
import numpy as np
from bruker2nifti.converter import Bruker2Nifti


def unzip_file(input_filepath):
    input_folder = os.path.join(os.path.dirname(input_filepath), '1')
    os.mkdir(input_folder)
    with open(input_filepath, 'r') as fp:
        zip = zipfile.ZipFile(fp)
        zip.extractall(input_folder)
        zip.close()

    print os.listdir(input_folder)
    if len(os.listdir(input_folder)) != 1:
        input_folder = os.path.dirname(input_folder)
    return input_folder


def initialize_converter(config):
    study_name = config.get('Study Name', '')
    if study_name == '':
        bru = Bruker2Nifti(input_folder, output_folder)
    else:
        bru = Bruker2Nifti(input_folder, output_folder, study_name=study_name)
    bru.verbose = config.get('Verbosity Level', 1)
    bru.correct_slope = config.get('Correct Slope', True)
    bru.get_acqp = config.get('Get ACQP', False)
    bru.get_method = config.get('Get Method', False)
    bru.get_reco = config.get('Get Reco', False)
    bru.nifti_version = config.get('Nifti Version', 1)
    bru.qform_code = config.get('Q-form Code', 1)
    bru.sform_code = config.get('S-form Code', 2)
    bru.save_human_readable = config.get('Save Human Readable', True)
    bru.save_b0_if_dwi = config.get('Save b0 if DWI', True)
    return bru


def write_out_metadata(vis_par_file, niftis, metadata_filepath, job_config):

    def array_to_list(array):
        if isinstance(array, np.ndarray):
            return array.tolist()
        raise TypeError('Not serializable')

    info_metadata = np.asscalar(np.load(vis_par_file))
    metadata = {
        job_config['destination']['type']: {
            'files': [
                {
                    'name': n,
                    'type': 'nifti',
                    'info': info_metadata,
                    'modality': 'MR'
                } for n in niftis
            ]
        }
    }

    with open(metadata_filepath, 'w') as fp:
        json.dump(metadata, fp, default=array_to_list)


def process_and_clean_output(output_folder, job_config, input_filename):
    vis_par_file = None
    niftis = []
    nifti_regex = re.compile('^.*\.nii(\.gz)?$')
    for root, dirs, files, in os.walk(output_folder):
        for f in files:
            if nifti_regex.match(f):
                niftis.append(os.path.join(root, f))
            if f.endswith('visu_pars.npy'):
                vis_par_file = os.path.join(root, f)
    scan_dir = os.path.dirname(vis_par_file)
    study_dir = os.path.dirname(scan_dir)
    new_nifti_names = ['{}{}'.format(input_filename.split('.')[0], os.path.basename(n)[len(os.path.basename(scan_dir)):]) for n in niftis]

    for i, nifti in enumerate(niftis):
        shutil.move(nifti, os.path.join(output_folder, new_nifti_names[i]))

    write_out_metadata(vis_par_file, new_nifti_names, os.path.join(output_folder, '.metadata.json'), job_config)
    shutil.rmtree(study_dir)


if __name__ == '__main__':

    # Gear basics
    input_folder = '/flywheel/v0/input/bruker/'
    output_folder = '/flywheel/v0/output/'
    CONFIG_PATH = '/flywheel/v0/config.json'

    # Grab the file paths
    input_filename = os.listdir(input_folder)[0]
    input_filepath = os.path.join(input_folder, input_filename)
    print input_filename

    # Extract the zip if it is a zip
    if input_filename.endswith('.zip'):
        input_folder = unzip_file(input_filepath)
    print input_folder

    with open(CONFIG_PATH) as config_file:
        job_config = json.load(config_file)

    config = job_config['config']
    # get the converter
    bru = initialize_converter(config)

    print('Scans list')
    print(bru.scans_list)
    print('New names of scans')
    print(bru.list_new_name_each_scan)

    print('Converting...')
    bru.convert()

    print('Processing Outputs...')
    process_and_clean_output(output_folder, job_config, input_filename)
