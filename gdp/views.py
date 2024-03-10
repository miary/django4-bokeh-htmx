import math, re
from django.shortcuts import render
from gdp.models import GDP
from django.db.models import Max, Min
from django.shortcuts import render

from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, NumeralTickFormatter, HoverTool
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import CDN

from pandas import read_csv


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


def line(request):
    countries = GDP.objects.values_list('country', flat=True).distinct()

    country = request.GET.get('country', 'Germany')

    gdps = GDP.objects.filter(country=country).order_by('year')

    country_years = [d.year for d in gdps]
    country_gdps = [d.gdp for d in gdps]

    source = ColumnDataSource(data=dict(country_years=country_years, country_gdps=country_gdps))

    fig = figure(height=500, title=f"{country} GDP")
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format='$0.0a')

    fig.line(source=source, x='country_years', y='country_gdps', line_width=2)

    tooltips = [
        ('Year', '@country_years'),
        ('GDP', '@country_gdps{,}')
    ]
    fig.add_tools(HoverTool(tooltips=tooltips))
    html = file_html(fig, CDN, "GDP by Year")

    context = {
        'countries': countries,
        'country': country,
        'html': html
    }

    if request.htmx:
        return render(request, 'partials/gdp_bar.html', context)

    return render(request, 'line.html', context)


def gdp_csv(request):
    data = read_csv("data\GDP.csv", nrows=20)
    countries = data['country'].tolist()
    gdps = data['gdp'].tolist()

    fig = figure(x_range=countries, height=400, title="GDP", tools="")
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format='$0.0a')
    fig.xaxis.major_label_orientation = math.pi / 4

    fig.vbar(x=countries, top=gdps, width=0.5)
    
    html = file_html(fig, CDN, "Countries GDP")

    context = {
        'html': html
    }

    return render(request, 'country.html', context)

