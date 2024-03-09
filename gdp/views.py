import math
from django.shortcuts import render
from gdp.models import GDP
from django.db.models import Max, Min
from django.shortcuts import render

from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, NumeralTickFormatter, HoverTool
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.palettes import Bright6

def index(request):
    max_year = GDP.objects.aggregate(max_yr = Max('year'))['max_yr']
    min_year = GDP.objects.aggregate(min_yr = Min('year'))['min_yr']
    year = request.GET.get('year', max_year)
    count = int(request.GET.get('count', 10))

    gdps = GDP.objects.filter(year=year).order_by('gdp').reverse()[:count]

    country_names = [d.country for d in gdps]
    country_gdps = [d.gdp for d in gdps]

    source = ColumnDataSource(data=dict(country_names=country_names, country_gdps=country_gdps))

    fig = figure(x_range=country_names, height=500, title=f"Top {count} GDP ({year})")
    fig.vbar(source=source, x='country_names', top='country_gdps', width=0.5,  color='blue')
    fig.title.align= 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format='$0.0a')
    fig.xaxis.major_label_orientation = math.pi / 4

    tooltips = [
        ('Country', '@country_names'),
        ('GDP', '@country_gdps{,}')
    ]
    fig.add_tools(HoverTool(tooltips=tooltips))
    html = file_html(fig, CDN, "my plot")

    context = {
        'html': html,
        'years': range(min_year, max_year+1),
        'count': count,
        'year_selected': year
    }

    if request.htmx:
        return render(request, 'partials/gdp_bar.html', context)

    return render(request, 'index.html', context)


