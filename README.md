# imagekit-cli
ImageKit.io cli tool for cloudinary storage migration.


## Install

```sh
pip install imagekit-cli
```

## Configuration
Declare following Environment Variables before running the tool. 

#### Environment Variables:
* **CLOUDINARY_URL:**	Cloudinary Authentication URL from [Cloudinary Console](https://cloudinary.com/console).
* **IMAGEKIT_ID:**	Imagekit account ID from [Imagekit profile](https://imagekit.io/dashboard#profile)
* **IMAGEKIT_PUBLIC_KEY:**	Imagekit public API key from [Imagekit dashboard](https://imagekit.io/dashboard#developers)
* **IMAGEKIT_PRIVATE_KEY:**	Imagekit private API key from [Imagekit dashboard](https://imagekit.io/dashboard#developers)

> **Note**: Use ```export``` command to set the variables. 
```sh
export CLOUDINARY_URL=""
export IMAGEKIT_ID=""
export IMAGEKIT_PUBLIC_KEY=""
export IMAGEKIT_PRIVATE_KEY=""
```


## Usage

```sh
imagekitcli
```
    
CLI Arguments:

```
usage: imagekitcli [-h] [-m] [-l] [-u] [-o OUTPUT] [-c] [-s]

optional arguments:
  -h, --help            Show this help message and exit
  -m, --migrate         Migrate Cloudinary storage to ImageKit
  -l, --list            Cloudinary URL list
  -u, --usage           Cloudinary usage
  -o OUTPUT, --output OUTPUT
                        Output file path (used with --list)
  -c, --clean           Clean caches
  -s, --status          Check status
``` 
  >**Note:** Use Cloudinary Backup bucket to migrate if storage is more than 2GB or if you are on Cloudinary paid plan. 

  * Enable Cloudinary Backup Bucket [Guide](https://support.cloudinary.com/hc/en-us/articles/360029234052-Enabling-Automatic-File-Backups-in-your-Cloudinary-Account)
  * Contact [Imagekit support](mailto:support@imagekit.io) to add this bucket as Origin in Imagekit dashboard. 

