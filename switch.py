import os
import re
from pathlib import Path
from uuid import uuid4


def tv_binaries():
    app_dir = Path('/Applications/TeamViewer.app/Contents/')
    targets = [
        'MacOS/TeamViewer',
        'MacOS/TeamViewer_Service',
        'Helpers/TeamViewer_Desktop'
    ]
    targets = [f for f in [app_dir / tgt for tgt in targets] if f.exists()]
    return targets


def rand_bytes(size: int):
    random = uuid4().hex[:size]
    return random.upper().encode()


def patch(target: Path, platform: bytes, serial: bytes):
    with target.open('rb') as f:
        data = f.read()
    data = re.sub(rb'(IOPlatformExpert)\w{6}', rb'\g<1>%s' % platform, data)
    data = re.sub(rb'(IOPlatformSerialNumber\x00)\w{8}(\x00)', rb'\g<1>%s\g<2>' % serial, data)
    with target.open('wb') as f:
        f.write(data)
        
    # Ad-hoc codesign the modified binary to fix `Code Signature Invalid` error.
    os.system('codesign -f -s - "%s" 2> /dev/null' % str(target))


def main():
    print('\nThe following binaries will be modified:')
    for binary in tv_binaries():
        print(' -', binary)
    input('\nPress [Enter] to continue...')

    platform, serial = map(rand_bytes, [6, 8])
    print('\nUsing platform "%s" and serial "%s".' % (platform.decode(), serial.decode()))

    for binary in tv_binaries():
        patch(binary, platform, serial)
    print('Done.')


if __name__ == "__main__":
    main()
