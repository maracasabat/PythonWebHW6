from aiopath import AsyncPath
import asyncio
import shutil
from time import time

from normalize import normalize


async def get_extensions(filename: AsyncPath, scan_folder: AsyncPath) -> None:
    file_folder = filename.suffix[1:].upper()
    if filename.suffix in ['.jpg', '.png', '.jpeg', '.bmp', '.gif', 'svg']:
        await handler_folders(filename, scan_folder / 'images' / file_folder)
    elif filename.suffix in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a']:
        await handler_folders(filename, scan_folder / 'audio' / file_folder)
    elif filename.suffix in ['.avi', '.mpg', '.mpeg', '.mkv', '.mov', '.flv', '.wmv', '.mp4', '.webm']:
        await handler_folders(filename, scan_folder / 'video' / file_folder)
    elif filename.suffix in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.rtf']:
        await handler_folders(filename, scan_folder / 'documents' / file_folder)
    elif filename.suffix in ('.zip', '.tar', '.gz'):
        await handle_archive(filename, scan_folder / 'archives')
    else:
        await handler_folders(filename, scan_folder / 'other')


async def handler_folders(filename: AsyncPath, target_folder: AsyncPath):
    await target_folder.mkdir(exist_ok=True, parents=True)
    await filename.replace(str(target_folder / normalize(filename.name)))


async def handle_archive(filename: AsyncPath, target_folder: AsyncPath):
    await target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    await folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename), str(folder_for_file))
    except shutil.ReadError:
        print(f'{filename} is not a archive!')
        await folder_for_file.rmdir()
        return None
    await filename.unlink()


async def handle_del_folder(del_folder: AsyncPath):
    try:
        await del_folder.rmdir()
    except OSError:
        print(f'The folder {del_folder} has not been deleted!')


async def scan(main_folder: AsyncPath, scan_folder: AsyncPath) -> None:
    tasks = []
    async for filename in main_folder.iterdir():
        if await filename.is_dir():
            tasks.append(asyncio.create_task(scan(filename, scan_folder)))
        else:
            tasks.append(asyncio.create_task(get_extensions(filename, scan_folder)))
    await asyncio.gather(*tasks)
    if scan_folder != main_folder:
        await handle_del_folder(main_folder)


if __name__ == '__main__':
    folder = AsyncPath(input('Enter the path to the folder: '))
    timer = time()
    asyncio.run(scan(folder, folder))
    print(f'Done in {time() - timer:.2f} seconds')
