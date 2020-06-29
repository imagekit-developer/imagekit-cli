import os
import sys
import json
import logging
import argparse
import cloudinary.api
from imagekitio import ImageKit
from concurrent.futures import ThreadPoolExecutor, as_completed
BATCH_SIZE=500
TOMIGRATE="tomigrate.log"
LOG_FILE="migration.log"
WORKERS=5


logging.basicConfig(filename=LOG_FILE, format='%(message)s', level=logging.INFO)


def check_connections():
    if not os.environ.get('CLOUDINARY_URL'):
        raise EnvironmentError("ENV {CLOUDINARY_URL} does not exist")

    if not os.environ.get('IMAGEKIT_ID'):
        raise EnvironmentError("ENV {IMAGEKIT_ID} does not exist")
    else:
        IMAGEKIT_ID = os.environ.get('IMAGEKIT_ID')

    if not os.environ.get('IMAGEKIT_PUBLIC_KEY'):
        raise EnvironmentError("ENV {IMAGEKIT_PUBLIC_KEY} does not exist")
    else:
        IMAGEKIT_PUBLIC_KEY=os.environ.get('IMAGEKIT_PUBLIC_KEY')

    if not os.environ.get('IMAGEKIT_PRIVATE_KEY'):
        raise EnvironmentError("ENV {IMAGEKIT_PRIVATE_KEY} does not exist")
    else:
        IMAGEKIT_PRIVATE_KEY=os.environ.get('IMAGEKIT_PRIVATE_KEY')

    try:
        cloudinary.api.usage()
    except Exception as ex:
        raise(ex)

    global imagekit
    imagekit = ImageKit(
        private_key = IMAGEKIT_PRIVATE_KEY,
        public_key = IMAGEKIT_PUBLIC_KEY,
        url_endpoint = 'https://ik.imagekit.io/'+IMAGEKIT_ID
    )

def get_cloudinary_usage():
    res = cloudinary.api.usage()
    plan=res['plan']
    storage_usage = res['storage']['usage']
    storage_usage = round((storage_usage/1024/1024/1024), 2)
    bandwidth_usage = res['bandwidth']['usage']
    bandwidth_usage = round((bandwidth_usage/1024/1024/1024), 2)
    print("\nCurrent Plan       : {}".format(plan))
    print("Current Storage    : {}G".format(storage_usage))
    print("Current Bandwidth  : {}G".format(bandwidth_usage))
    print("Resources          : {}".format(res['resources']))
    print("Derived Resources  : {}\n".format(res['derived_resources']))
    if storage_usage > 2:
        print('\n NOTE: Storage is more than 2G. Faster way to integrate would be to enable \n backup bucket in Cloudinary and attach that to Imagekit. Backup bucket\n feature is available on all paid plan on Cloudinary.\n')
        sys.exit()


def get_cloudinary_data():
    count=0
    print("Getting data from cloudinary ..")
    f = open(TOMIGRATE, "w")
    res = cloudinary.api.resources(type="upload", resource_type="image", context=True, tags=True, max_results=BATCH_SIZE)
    while res.get('next_cursor'):
        for doc in res['resources']:
            try:
                doc = json.dumps(doc)
                f.write(doc + os.linesep)
            except Exception as ex:
                os.remove(TOMIGRATE)
                raise ex
            else:
                count+=1
        res = cloudinary.api.resources(type="upload", resource_type="image", context=True, tags=True, max_results=BATCH_SIZE, next_cursor=res['next_cursor'])

    for doc in res['resources']:
        try:
            doc = json.dumps(doc)
            f.write(doc + os.linesep)
        except Exception as ex:
            os.remove(TOMIGRATE)
            raise ex
        else:
            count+=1
    f.close()
    print("Total resources fetched: {}\n".format(count))


def get_urls():
    urls = []
    if not os.path.exists(TOMIGRATE):
        get_cloudinary_data()
    for doc in open(TOMIGRATE, 'r'):
        doc = json.loads(doc)
        urls.append(doc['url'])
    return urls


def upload_file(doc):
    url = doc['url']
    tags = doc['tags']
    path=url.split('/', 4)[-1]
    filename=path.rsplit('/', 1)[1]
    folder=path.rsplit('/', 1)[0]
    resp = imagekit.upload_file(
        file=url,
        file_name=filename,
        options = {
            "folder" : folder,
            "tags": tags,
            "is_private_file": False,
            "use_unique_file_name": False,
        }
    )
    return resp

def clean_cache():
    open(LOG_FILE, 'w').close()
    open(TOMIGRATE, 'w').close()
    return "Cache cleaned!"

def migrate_data(status):
    if not os.path.exists(TOMIGRATE):
        get_cloudinary_data()

    count=0
    url_list = []
    succ_list = []

    for log in open(LOG_FILE, 'r'):
        if 'SUCCESS' in log:
            succ_list.append(log.split()[1].rstrip())

    for doc in open(TOMIGRATE, 'r'):
        doc = json.loads(doc)
        path = doc['url'].split('/', 4)[-1]
        count+=1
        if path not in succ_list:
            url_list.append(doc)

    print("\nTotal Images          : {}".format(count))
    print("Migrated              : {}".format(len(succ_list)))
    print("To migrate            : {}".format(len(url_list)))
    print("-------------------------------------\n")
    
    if status == True:
        sys.exit()

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        results = executor.map(upload_file, url_list)
        for r in results:
            if r['error']:
                print(r)
                logging.info('ERROR '+str(r))
            else:
                res = r['response']['url']
                print("Success: {}".format(res))
                path = res.split('/', 4)[-1]
                logging.info('SUCCESS '+path)
    
    scount=0
    for log in open(LOG_FILE, 'r'):
        if 'SUCCESS' in log: 
            scount+=1

    print("\n-------------------------------------")
    print("Successfully migrated : {}".format(scount))
    ecount=count-scount
    if ecount > 0:
        print("Errors                : {}".format(ecount))
    print("Migration logs        : {}\n".format(LOG_FILE))



def main():
    check_connections()

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--migrate", help="migrate image resources from Cloudinary to ImageKit", action="store_true")
    parser.add_argument("-l", "--list", help="Cloudinary URL list", action="store_true")
    parser.add_argument("-u", "--usage", help="Cloudinary usage", action="store_true")
    parser.add_argument("-o", "--output", help="Output file path (used with --list)")
    parser.add_argument("-c", "--clean", help="Clean caches", action="store_true")
    parser.add_argument("-s", "--status", help="Check status", action="store_true")

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    if args.usage:
        get_cloudinary_usage()
    elif args.migrate:
        migrate_data(False)
    elif args.status:
        migrate_data(True)
    elif args.clean:
        print(clean_cache())
    elif args.list:
        urls = get_urls()
        if args.output:
            f = open(args.o, "w")
            for url in urls:
                f.write(url + os.linesep)
            f.close()
        else:
            for url in urls:
                print(url)


if __name__ == '__main__':
    main()

