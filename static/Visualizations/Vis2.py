import numpy as np  # import auxiliary library, typical idiom
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, Select, Tabs, Panel, Button, ImageURL
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.models.callbacks import CustomJS
import PIL
from PIL import Image

sns.set()  # set Seaborn defaults

#load dataset
df_paths = pd.read_csv('Uploads/fixation_data.csv', parse_dates=[0])
df_paths = df_paths.astype({'Timestamp': int, 'StimuliName': str, 'FixationIndex': float, 'FixationDuration': float, 
    'MappedFixationPointX': int, 'MappedFixationPointY' : int, 'user': str, 'description': str})

#Global Variables
users = []
stations = []

src = ColumnDataSource(data = dict(url=[], x=[], y=[], timestamp=[], station=[], user=[]))

#Choosing the data we want
def make_dataset():
    plot_data = df_paths[(df_paths['StimuliName'] == selectStation.value) & (df_paths['user'] == selectUser.value)].copy()
    return plot_data

#making the plot
def make_plot(src):
    #Writing X-path
    p1 = figure(title="X path", plot_width = print_width, plot_height = print_height, 
        x_range = (0, width), color = 'navy', muted_alpha = 0.1, legend_label = 'Disable/Enable Graph')
    p1.grid.grid_line_alpha=0.3
    p1.xaxis.axis_label = 'X'
    p1.yaxis.axis_label = 'Time'
    p1.y_range.flipped = True
    p1.line(x='x', y='timestamp', source = src, width = 3)
    p1.legend.click_policy = 'mute'

    #Writing Y-path
    p2 = figure(title= "Y path", plot_width = print_width, plot_height = print_height, 
        y_range = (height, 0), color = 'navy', muted_alpha = 0.1, legend_label = 'Disable/Enable Graph')
    p2.grid.grid_line_alpha=0.3
    p2.xaxis.axis_label = 'Time'
    p2.yaxis.axis_label = 'Y'
    p2.line(x='timestamp', y='y', source = src, width = 3)
    p2.legend.click_policy = 'mute'
    
    #writing general path
    p3 = figure(title="General Path", plot_width = print_width, plot_height = print_height, 
        x_range = (0, width), y_range = (height, 0), color = 'navy', muted_alpha = 0.1, legend_label = 'Disable/Enable Graph')

    p3.grid.grid_line_alpha=0.3
    image = ImageURL(url = "url", x=0, y=0, w=width, h=height)
    p3.add_glyph(src, image)
    p3.xaxis.axis_label = 'X'
    p3.yaxis.axis_label = 'Y'
    p3.line(x='x', y='y', source = src, width = 3)
    p3.legend.click_policy = 'mute'
    return [p1, p2, p3]

#Select
for station in df_paths['StimuliName']:
    stations.append(station)
for person in df_paths['user']:
    users.append(person)
#to remove duplicates
stations = list(dict.fromkeys(stations))
users = list(dict.fromkeys(users))

selectStation = Select(title="Station:", value = '03_Bordeaux_S1.jpg', options=stations)
selectUser = Select(title='User:', value='p1', options=users)

#Update
def update():
    new_src = make_dataset()
    N = new_src.size//8
    src.data = dict(
        url = ["https://www.jelter.net/stimuli/"+selectStation.value]*N,
        x=new_src['MappedFixationPointX'],
        y=new_src['MappedFixationPointY'],
        timestamp=new_src['Timestamp'],
        station=new_src['StimuliName'],
        user=new_src['user']
    )

selectStation.on_change('value', lambda attr, old, new: update())
selectUser.on_change('value', lambda attr, old, new: update())
selections = [selectStation, selectUser]

image = PIL.Image.open('static/Visualizations/Stimuli/'+selectStation.value)
width, height = image.size
ratio = width/height

print_width = int(ratio * 360)
print_height = int(360)

plot = make_plot(src)

widgets = column(*selections, width = 320, height = 200)
layout = layout([
                [plot[2], plot[1], widgets],
                plot[0]])
update()

curdoc().add_root(layout)