# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
#     path: /home/robin/.local/share/jupyter/kernels/python3
# ---

# ---
# format: gfm
# ---
#
# # Transport Data Mini Hack: Routing Engines
#
#  As part of the the [Network Planning Tool for Scotland](https://nptscot.github.io) project, we are looking to explore different options for routing and associated data processing tasks.
#
# We'll run this session in 1 pars:
#
# ## Part 1: Data pre-processing and idea generation, 10:00-13:00
#
# This will done asynchronously, with participants working alone or in-person to generate input datasets and discuss needs.
#
# ## Part 2: Development and hacking, 14:00-16:00
#
# This will be the 'hackathon' part of the day, where people will work alone or in groups synchronously to develop code and test routing solutions.
# We will set-up Microsoft Teams for anyone to contribute remotely.
#
# ## Hack ideas
#
#
# - Benchmarking different engines in terms of ease of setup, with Valhalla, Graphhopper, OSRM, and [AequilibraE](https://www.outerloop.io/blog/20240729_route_choice/) and any other open source routing engine being options
#   - As a ballpark for performance levels of current code we're getting around:
#     - 1-5 routes per second for one-by-one API requests
#     - 30-100 routes per second for batch routing with CycleStreets
#     - ??? Can we go faster while retaining valuable route level info ??? See `od2net` for an example of fast network generation
#     - Can we keep summary stats on origin and destination groups? See https://github.com/Urban-Analytics-Technology-Platform/od2net/issues/35
# - Obtaining segment-level data from route-level data, overcoming an issue with the NPT workflow in which duplicate segments are represented multiple times (if that makes sense...)
#   - That could involve spatial joins, e.g. with https://github.com/nptscot/rnetmatch or other packages
# - Ease of customising routing weights
# - Network pre-processing, with reference to existing documentation, e.g. from [sDNA](https://sdna-plus.readthedocs.io/en/latest/network_preparation.html)
#
# ## Logistics
#
# We have in-person space at the University of Leeds from 10:00, get in touch if you'd like to join remotely or in person if you don't know where to find us.
#
# ## Sharing code
#
# You can put code whereever you like but please do share reproducible examples with a link to your code and by putting the code here directly with pull requests to this repository. We will share input datasets in the Releases of this repository.
#
# **Please create issues describing ideas before putting in PRs.**
#
# See specific guidance on opening issues and associated Pull Requests here: https://github.com/ITSLeeds/routingday/blob/main/test_osmnx_rl.md#how-to-contribute-to-the-repo
#
# ## Getting started 
#
# To get the input datasets and example code, first install the `gh` command line tool, then run:
#
# ```bash
# gh repo clone itsleeds/routingday
# ```
#
# ## Input datasets
#
# The input datasets in this repo were created with the following packages:
#
# ```{r}
# library(tidyverse)
# library(sf)
# ```
#
# ### Origin-destination data
#
# You can get this in some countries (UK, Republic of Ireland, USA for example) from census data.
# You can also simulate it (e.g. for travel to school, shops and other purposes) and that could be a topic for your hack, although the main focus is on routing. 
# In the NPT project we use Census data for travel to work and data on travel to school for school travel. We simulate travel to shops, leisure and personal trips with a spatial interaction model.
#
# ```{r}
# #| eval: false
# remotes::install_dev("simodels")
# od_data_leeds = simodels::si_od_census
# names(od_data_leeds)
# od_data_leeds = od_data_leeds |>
#   filter(O != D) |>
#   select(O, D, all)
# zones_msoa_leeds = simodels::si_zones
# set.seed(42)
# od_data_100 = od_data_leeds |>
#   sample_n(100, weight = all)
# od_data_100_sf = od::od_to_sf(od_data_100, zones_msoa_leeds)
# # Save to input_data folder:
# dir.create("input_data")
# sf::write_sf(zones_msoa_leeds, "input_data/zones_msoa_leeds.geojson", delete_dsn = TRUE)
# sf::write_sf(od_data_100_sf, "input_data/od_data_100_sf.geojson", delete_dsn = TRUE)
# readr::write_csv(od_data_100, "input_data/od_data_100.csv")
# ```
#
# We can read-in and visualise the data with R as follows:
#
# ```{r}
# #| label: input-data-leeds-base
# od_geo = sf::read_sf("input_data/od_data_100_sf.geojson")
# plot(od_geo)
# ```
#
# Let's visualise the OD data in Python:

import geopandas as gpd
od_gdf = gpd.read_file("input_data/od_data_100_sf.geojson")
od_gdf.plot()

# ## Basic routing
#
# There are many ways to generate routes from this OD data and that's the focus of this event.
# For the NPT project we use an external web service hosted by CycleStreets.net.
# You can generate routes from CycleStreets.net as follows (note: requires API key):
#
#
# ```{r}
# #| eval: false
# library(stplanr)
# routes_1 = route(
#     l = od_geo,
#     route_fun = cyclestreets::journey,
#     plan = "fastest"
# )
# sf::write_sf(routes_1, "input_data/routes_1.geojson", delete_dsn = TRUE)
# ```
#
# We can visualise the route data as follows:
#
# ```{r}
# #| label: routes_1
# routes_1 = sf::read_sf("input_data/routes_1.geojson")
# names(routes_1)
# nrow(routes_1)
# routes_1 |>
#   select(quietness, gradient_smooth, all) |>
#   plot()
# #   tm_shape() +
# #   tm_lines("all")
# ```
#

#| label: routes_1_py
import geopandas as gpd
routes_1_gdf = gpd.read_file("input_data/routes_1.geojson")
routes_1_gdf.plot();

# There are many ways to generate routes but few are easy.
# For 'good' quality routes you often need an API key which, when used to generate many routes, can be expensive (e.g. Google, Graphopper).
# One service that is free for small scale usage is OSRM's public instance, which we can call from R as follows:
#
#
# ```{r}
# library(stplanr)
# system.time({
# routes_2 = route(
#     l = od_geo,
#     route_fun = route_osrm,
#     osrm.profile = "foot"
# )
# })
#
# nrow(routes_2)
# names(routes_2)
# plot(routes_2)
# ```
#
# As the timing exercise shows, it took almost a minute to generate 100 routes. 
#
# **Challenge: get under 1 second**
#
# A common requirement is to set routing profiles for different transport modes and users.
# For cycle network planning, for example, your users may be interested in the quietest routes.
# You can calculate those with CycleStreets as follows:
#
# ```{r}
# #| eval: false
# library(stplanr)
# routes_quietest = route(
#     l = od_geo,
#     route_fun = cyclestreets::journey,
#     plan = "quietest"
# )
# sf::write_sf(routes_quietest, "input_data/routes_quietest.geojson", delete_dsn = TRUE)
# ```
#
#
# ```{r}
# #| label: routes_quietest
# routes_quietest = sf::read_sf("input_data/routes_quietest.geojson")
# names(routes_quietest)
# nrow(routes_quietest)
# routes_quietest |>
#   select(quietness, gradient_smooth, all) |>
#   plot()
# #   tm_shape() +
# #   tm_lines("all")
# ```
#
# ### Batch routing
#
# You can use the function `cyclestreets::batch()` for batch routing that gives around a 10x speed-up.
#
# # Routing using a local copy of OSM
#
# ...
