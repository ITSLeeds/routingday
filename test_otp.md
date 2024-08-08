# otp test


``` r
library(sf)
```

    Linking to GEOS 3.11.2, GDAL 3.8.2, PROJ 9.3.1; sf_use_s2() is TRUE

``` r
library(osmextract)
```

    Data (c) OpenStreetMap contributors, ODbL 1.0. https://www.openstreetmap.org/copyright.
    Check the package website, https://docs.ropensci.org/osmextract/, for more details.

``` r
library(tidyverse)
```

    ── Attaching core tidyverse packages ──────────────────────── tidyverse 2.0.0 ──
    ✔ dplyr     1.1.4     ✔ readr     2.1.5
    ✔ forcats   1.0.0     ✔ stringr   1.5.1
    ✔ ggplot2   3.5.1     ✔ tibble    3.2.1
    ✔ lubridate 1.9.3     ✔ tidyr     1.3.1
    ✔ purrr     1.0.2     

    ── Conflicts ────────────────────────────────────────── tidyverse_conflicts() ──
    ✖ dplyr::filter() masks stats::filter()
    ✖ dplyr::lag()    masks stats::lag()
    ℹ Use the conflicted package (<http://conflicted.r-lib.org/>) to force all conflicts to become errors

``` r
library(tmap)
```

    Breaking News: tmap 3.x is retiring. Please test v4, e.g. with
    remotes::install_github('r-tmap/tmap')

Reading the OD data

``` r
od_geo = sf::read_sf("input_data/od_data_100_sf.geojson")
```

Extracting Origins and Destinations

``` r
origins <- lwgeom::st_startpoint(od_geo) |> st_as_sf()
origins$O <- od_geo$O


destinations <- lwgeom::st_endpoint(od_geo) |> st_as_sf()
destinations$D <- od_geo$D
```

### Setting up OTP

Creating the folder structure

``` r
dir.create("OTP/graphs/Leeds",recursive = T,showWarnings = F)
```

Getting OSM data

``` r
leeds_osm <- osmextract::oe_get("Leeds",
                                download_directory = "OTP/graphs/Leeds")
```

    No exact match found for place = Leeds and provider = geofabrik. Best match is Laos. 
    Checking the other providers.

    An exact string match was found using provider = bbbike.

    The chosen file was already detected in the download directory. Skip downloading.

    The corresponding gpkg file was already detected. Skip vectortranslate operations.

    Reading layer `lines' from data source 
      `C:\Users\ts18jpf\OneDrive - University of Leeds\03_PhD\00_Misc_projects\routingday\OTP\graphs\leeds\bbbike_Leeds.gpkg' 
      using driver `GPKG'
    Simple feature collection with 174124 features and 9 fields
    Geometry type: LINESTRING
    Dimension:     XY
    Bounding box:  xmin: -1.889999 ymin: 53.65 xmax: -1.280002 ymax: 53.88
    Geodetic CRS:  WGS 84

``` r
library(opentripplanner)
library(tmap)
```

``` r
path_data <- file.path("OTP")
# dir.create(path_data)
path_otp <- otp_dl_jar(path_data, cache = TRUE)
```

    Using cached version from C:/Users/ts18jpf/AppData/Local/R/win-library/4.4/opentripplanner/jar/otp-1.5.0-shaded.jar

Creating the config file for the router

``` r
if(!file.exists("OTP/graphs/leeds/router-config.json")){
router_config <- otp_make_config("router")
otp_validate_config(router_config)
otp_write_config(router_config,                # Save the config file
                 dir = path_data,
                 router = "Leeds")  
}
```

Creating the graph

``` r
if(!file.exists("OTP/graphs/leeds/Graph.obj")){
log1 <- otp_build_graph(otp = path_otp,router = "Leeds", dir = path_data,memory = 15000)
}
```

Initialising OTP

``` r
log2 <- otp_setup(otp = path_otp, dir = path_data,router = "Leeds",memory = 15e3)
```

    You have the correct version of Java for OTP 1.x

    2024-08-08 12:44:35.243263 OTP is loading and may take a while to be useable

    Router http://localhost:8080/otp/routers/Leeds exists

    2024-08-08 12:45:05.84992 OTP is ready to use Go to localhost:8080 in your browser to view the OTP

``` r
otpcon <- otp_connect(timezone = "Europe/London",router = "Leeds")
```

    Router http://localhost:8080/otp/routers/Leeds exists

Generating the routes and measuring the time

``` r
system.time({
routes2 <- otp_plan(otpcon = otpcon,
         fromPlace = origins,toPlace = destinations,fromID = origins$O,toID = destinations$D,
         mode = "BICYCLE")
})
```

    2024-08-08 12:45:06.496605 sending 100 routes requests using 19 threads

    Done in 0 mins

    2024-08-08 12:45:09.078369 processing results

    6 routes returned errors. Unique error messages are:

    6x messages: "No trip found. There may be no transit service within the maximum specified distance or at the specified time, or your start or end point might not be safely accessible."

    2024-08-08 12:45:09.345947 done

       user  system elapsed 
       0.28    0.09    2.89 
