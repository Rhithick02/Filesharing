import os
import shutil
import hashlib
import asyncio
import datetime

async def get_hash(file):
    with open(file, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            buffer = f.read(8192)
            if not buffer:
                break
            md5.update(buffer)
            await asyncio.sleep(0.0001)
        return md5.hexdigest()

async def get_cache(path):
    basefile = os.path.basename(path)
    cache_time = datetime.datetime.utcnow()
    proper_time = cache_time.strftime("%Y%m%d_%H%M%S")

    cache_modified = os.path.getmtime(path)
    cache_hash = await get_hash(path)
    cache_path = os.path.normpath(os.path.join(os.getcwd(), f'cache/{basefile}_{proper_time}'))
    os.makedirs(cache_path)
    shutil.copy2(path, os.path.join(cache_path, basefile))

    return basefile, proper_time, cache_modified, cache_hash, cache_path

async def update_cache(db, share):
    print(f"Updating cache for {share['filename']}..")
    _, proper_time, cache_modified, cache_hash, cache_path = await get_cache(share['share_path'])
    new_cache = {'cache_path': cache_path,
                 'cache_time': proper_time,
                 'cache_modified': cache_modified,
                 'cache_hash': cache_hash
                }
    cache_list = share['cache']
    cache_list.append(new_cache)
    
    if len(cache_list) > 2:
        old_cache = cache_list.pop(0)
        shutil.rmtree(old_cache['cache_path'])
    db.Shares.update({'_id': share['_id']}, {'$set': {'cache': cache_list}})
    print(f"Updated cache for {share['filename']}..")

async def check_local_file(db, shared_files):
    while True:
        print("checking for updation...")
        for share in db.Shares.find():
            if share['cache'][-1]['cache_modified'] != os.path.getmtime(share['share_path']):
                print(f"Modified date has been changed for {share['filename']}")
                if share['cache'][-1]['cache_hash'] != await get_hash(share['share_path']):
                    print(f"Hash value has been changed for {share['filename']}")
                    await update_cache(db, share)
                else:
                    new_cache = {'cache_path': share['cache'][-1]['cache_path'],
                                 'cache_time': share['cache'][-1]['cache_time'],
                                 'cache_modified': os.path.getmtime(share['share_path']),
                                 'cache_hash': share['cache'][-1]['cache_hash']}
                    cache_list = share['cache']
                    cache_list[-1] = new_cache
                    db.Shares.update({'_id': share['_id']}, {'$set': {'cache': cache_list}})
                    shared_files = db.Shares.find()
        print("Done checking")
        await asyncio.sleep(10)