# PiEC-project
Simple python script analysing music data and creating html report [student project for "Python in Engineering Calculations"].

More details are included in the file *doc.pdf* but there are some the most important info:
- All necessary packages are listed in *env.yml* file that is needed for creating new environment where the script can be executed. 
<br>Command: `conda env create –f env.yml`
- Basically the script requires two arguments that will determine which mode should be executed. 
The third argument is optional and it contains the name of the output report. 
Below there are listed examples of commands:
  - The first mode – 2 decades comparison: `python make_report.py 70s 10s`
  - The second mode – years from 1921 to 2020: `python make_report.py all decades`
  - Changing name of the report (2 ways): `python make_report.py 70s 10s --name report`
  <br>(or shorter: python `make_report.py 70s 10s -n report`)
  
Example results (**NOTE: It might take some time to load whole page with css**): 
- [example.html](https://htmlpreview.github.io/?https://github.com/bartosz-rogowski/PiEC-project/blob/main/results/example.html) 
- [rep.html](https://htmlpreview.github.io/?https://github.com/bartosz-rogowski/PiEC-project/blob/main/results/rep.html).

Data source: [here](https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks).
