## -----------------------------------------------------------------------------
library(tidyverse)
library(sf)


## -----------------------------------------------------------------------------
#| eval: false
## remotes::install_dev("simodels")
## od_data_leeds = simodels::si_od_census
## names(od_data_leeds)
## od_data_leeds = od_data_leeds |>
##   filter(O != D) |>
##   select(O, D, all)
## zones_msoa_leeds = simodels::si_zones
## set.seed(42)
## od_data_100 = od_data_leeds |>
##   sample_n(100, weight = all)
## od_data_100_sf = od::od_to_sf(od_data_100, zones_msoa_leeds)
## # Save to input_data folder:
## dir.create("input_data")
## sf::write_sf(zones_msoa_leeds, "input_data/zones_msoa_leeds.geojson", delete_dsn = TRUE)
## sf::write_sf(od_data_100_sf, "input_data/od_data_100_sf.geojson", delete_dsn = TRUE)
## readr::write_csv(od_data_100, "input_data/od_data_100.csv")


## -----------------------------------------------------------------------------
#| label: input-data-leeds-base
od_geo = sf::read_sf("input_data/od_data_100_sf.geojson")
plot(od_geo)


## import geopandas as gpd
## od_gdf = gpd.read_file("input_data/od_data_100_sf.geojson")
## od_gdf.plot()

## -----------------------------------------------------------------------------
#| eval: false
## library(stplanr)
## routes_1 = route(
##     l = od_geo,
##     route_fun = cyclestreets::journey,
##     plan = "fastest"
## )
## sf::write_sf(routes_1, "input_data/routes_1.geojson", delete_dsn = TRUE)


## -----------------------------------------------------------------------------
#| label: routes_1
routes_1 = sf::read_sf("input_data/routes_1.geojson")
names(routes_1)
nrow(routes_1)
routes_1 |>
  select(quietness, gradient_smooth, all) |>
  plot()
#   tm_shape() +
#   tm_lines("all")


## import geopandas as gpd
## routes_1_gdf = gpd.read_file("input_data/routes_1.geojson")
## routes_1_gdf.plot();

## -----------------------------------------------------------------------------
library(stplanr)
system.time({
routes_2 = route(
    l = od_geo,
    route_fun = route_osrm,
    osrm.profile = "foot"
)
})

nrow(routes_2)
names(routes_2)
plot(routes_2)


## -----------------------------------------------------------------------------
#| eval: false
## library(stplanr)
## routes_quietest = route(
##     l = od_geo,
##     route_fun = cyclestreets::journey,
##     plan = "quietest"
## )
## sf::write_sf(routes_quietest, "input_data/routes_quietest.geojson", delete_dsn = TRUE)


## -----------------------------------------------------------------------------
#| label: routes_quietest
routes_quietest = sf::read_sf("input_data/routes_quietest.geojson")
names(routes_quietest)
nrow(routes_quietest)
routes_quietest |>
  select(quietness, gradient_smooth, all) |>
  plot()
#   tm_shape() +
#   tm_lines("all")

