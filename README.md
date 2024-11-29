### Election Dashboard
This dashboard serves as a tool to visually explore social media dynamics during the 2021 german federal election. The data includes social media postings from Facebook, Twitter and Instagram that were published in the 6 week period prior to the election. The primary focus lies on identifying cross-party partisans (accounts that shared the same images but are affiliated to different parties) with the help of an interactive network visualization. Additionally the dissemination of images across different social media platforms is visually analyzed on a micro level. The tool provides functionalities to recognize cross-party partisanship intuitively, identify joint opinions between individual accounts, and get a feeling for the dissemination of images across social media platforms over time.

### Setup
1. 
2. Install the requirements specified in the `requirements.txt` file
3. Put all the images into the directory `images/` using the following naming convention: `<image_hash>.jpg`
to mount: `docker run -p 8050:8050 -it --rm -v /c/users/tobia/network_dashboard:/app ubuntu /bin/bash`

### TODO
- log transform the weights to map to the edge widths