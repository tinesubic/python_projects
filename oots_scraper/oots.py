import urllib.request
import os
from tqdm import tqdm
import multiprocessing
ROOT_URL = 'http://www.giantitp.com/comics/images/'

MAX = 1103

def dl_file(num):

    url = '{0}oots{1}.gif'.format(ROOT_URL, str(num).zfill(4))
    try:
        urllib.request.urlretrieve(url, './oots/oots' + str(num).zfill(4) + '.gif')
    except:
        print(url)







if __name__ == '__main__':
   # multiprocessing.freeze_support()
    if not os.path.exists('./oots'):
        os.makedirs('./oots')

    nums = [x for x in range(1, 1104)]

    with multiprocessing.Pool(processes=16) as p:
        max_ = 1104
        with tqdm(total=max_) as pbar:
            for i, _ in tqdm(enumerate(p.imap_unordered(dl_file, nums))):
                pbar.update()




