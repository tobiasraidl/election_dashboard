### Election Dashboard
This dashboard serves as a tool to visually explore social media dynamics during the 2021 german federal election. The data includes social media postings from Facebook, Twitter and Instagram that were published in the 6 week period prior to the election. The primary focus lies on identifying cross-party partisans (accounts that shared the same images but are affiliated to different parties) with the help of an interactive network visualization. Additionally the dissemination of images across different social media platforms is visually analyzed on a micro level. The tool provides functionalities to recognize cross-party partisanship intuitively, identify joint opinions between individual accounts, and get a feeling for the dissemination of images across social media platforms over time.

![example_image](https://github.com/user-attachments/assets/783cb032-911e-4f76-8e8d-3ac76a0b3766)

### Setup
1. Put all the images into the app/images/ directory using the following naming convention: `<image_hash>.jpg`. *
2. Build the docker image: In the directory with the Dockerfile run `docker build -t election-dashboard .` (make sure docker is running)
3. Run the docker iamge as a container: In the directory with the Dockerfile run `docker run -d --name election-dashboard-container -p 8050:8050 election-dashboard`

*Contact me for the images at e11717659@student.tuwien.ac.at

### Links
Detailed description of the dashboard: https://polarvis.github.io/dashboard/#the-polarvis-election-dashboard
POLARVIS: https://polarvis.github.io/

