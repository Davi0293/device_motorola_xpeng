#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.extract import extract_fns_user_type
from extract_utils.extract_star import extract_star_firmware

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)

from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)

from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

# -----------------------------------------
# Namespace imports (combinação dos dois)
# -----------------------------------------
namespace_imports = [
    'hardware/motorola',
    'hardware/qcom-caf/sm8350',
    'hardware/qcom-caf/wlan',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]

# -----------------------------------------
# Função de sufixo vendor
# -----------------------------------------
def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

# -----------------------------------------
# lib_fixups mesclados
# -----------------------------------------
lib_fixups: lib_fixups_user_type = {
    **lib_fixups,

    # Do primeiro script (sm7325-common)
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.diaghal@1.0',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.imsrtpservice@3.0',
        'vendor.qti.qspmhal@1.0',
    ): lib_fixup_vendor_suffix,

    (
        'libofflinelog',
        'libthermalclient',
    ): lib_fixup_remove,

    # Do segundo script (xpeng)
    (
        'motorola.hardware.camera.desktop@1.0',
        'motorola.hardware.camera.desktop@2.0',
    ): lib_fixup_vendor_suffix,
}

# -----------------------------------------
# blob_fixups mesclados
# -----------------------------------------
blob_fixups: blob_fixups_user_type = {

    # Do primeiro script
    'system_ext/etc/permissions/moto-telephony.xml': blob_fixup()
        .regex_replace('/system/', '/system_ext/'),

    'system_ext/priv-app/ims/ims.apk': blob_fixup()
        .apktool_patch('ims-patches'),

    'vendor/lib64/libwvhidl.so': blob_fixup()
        .add_needed('libcrypto_shim.so'),

    # Em ambos os scripts
    'vendor/lib64/sensors.moto.so': blob_fixup()
        .add_needed('libbase_shim.so'),

    # Do segundo script
    (
        'vendor/lib64/camera/components/com.mot.node.c2d.so',
        'vendor/lib64/camera/components/com.qti.node.dewarp.so',
        'vendor/lib64/camera/components/com.vidhance.node.ica.so',
        'vendor/lib64/camera/components/com.vidhance.node.processing.so'
    ): blob_fixup()
        .replace_needed('libui.so', 'libui-v34.so'),
}

# -----------------------------------------
# extract_fns do segundo script
# -----------------------------------------
extract_fns: extract_fns_user_type = {
    r'(bootloader|radio)\.img': extract_star_firmware,
}

# -----------------------------------------
# Módulo combinado, baseado no script xpeng
# -----------------------------------------
module = ExtractUtilsModule(
    'xpeng',
    'motorola',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    extract_fns=extract_fns,
    add_firmware_proprietary_file=True,
    add_generated_carriersettings=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm7325-common', module.vendor
    )
    utils.run()

