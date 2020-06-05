#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import requests
import time

from tqdm import tqdm


# In[2]:


# setting download parameters
sba = 'NW' # Other subareas (Table 3)
var = 'CHL' # variable name
comp = 'day' # monthly composite | here can be 'day', 'month' or 'year'
init = 'S' # Initial character of the sensor name, MODIS-Aqua (A) and SGLI-GCOMC (GS)
ys = 1997 # start year
ms = 9 # start month
ds = 10 # start day of month
ye = 1998 # end year + 1, if end is 1997 then use yend = 1997 + 1
me = 11 # end month + 1, if end is 12 (Dec) then use 13, if 1 then use 2
de = 11 # end day
file_ext = ('nc', 'png') # file extension (type) to download, ('nc', 'png') or ('nc',) or ('png',)
url = 'https://ocean.nowpap3.go.jp/image_search/{filetype}/{subarea}/{year}/{filename}'


# In[3]:


# Day month fetching file generator
def daymonth_filegen(filetype:tuple=file_ext):
    # Define the netCDF (PNG) file name
    for month in range(ms, me):
        if comp == 'day':
            for day in range(ds, de):
                files = [f'{init}{year}{month:02}{day:02}_{var}_{sba}_{comp}.{ext}'
                         for ext in filetype]

                yield from [url.format(filetype='netcdf', subarea=sba, year=year, filename=f)
                            if f.endswith('.nc') else
                            url.format(filetype='images', subarea=sba, year=year, filename=f)
                            for f in files]

        if comp == 'month':
            files = [f'{init}{year}{month:02}_{var}_{sba}_{comp}.{ext}'
                     for ext in filetype]

            yield from [url.format(filetype='netcdf', subarea=sba, year=year, filename=f)
                        if f.endswith('.nc') else
                        url.format(filetype='images', subarea=sba, year=year, filename=f)
                        for f in files]


# In[4]:


# Function to download the data
def get_file(query_url:str):
    getfile = os.path.basename(query_url)
    with requests.get(query) as r:
        if r.status_code != 200:
            print(f'{os.path.basename(query_url)}: FileNotFound')
            return
        total = int(r.headers.get('content-length'))
        print('File: {} '.format(getfile), end='')
        with tqdm(total=total) as bar, open(getfile, "wb") as handle:
            for chunk in r.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                # download progress check tqdm
                if chunk:
                    handle.write(chunk)
                    time.sleep(0.1)
                    bar.update(len(chunk))


# In[5]:


# Now retrieve the data from NMEW
for year in range(ys, ye):
    print(f'{year}...')
    if comp in ('day', 'month'):
        for query in daymonth_filegen():
            # ----------------------
            get_file(query_url=query)
            # ----------------------

    if comp == 'year':
        ncfile = f'{init}{year}_{var}_{sba}_{comp}.nc'
        query = url.format(filetype='netcdf', subarea=sba, year=year, filename=ncfile)
        # ----------------------
        get_file(query_url=query)
        # ----------------------

        pngfile = f'{init}{year}_{var}_{sba}_{comp}.png'
        query = url.format(filetype='images', subarea=sba, year=year, filename=pngfile)
        # ----------------------
        get_file(query_url=query)
        # ----------------------

print('done!')
