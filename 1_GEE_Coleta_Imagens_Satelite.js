var START = '2024-06-01';
var END   = '2024-11-30';
var CLD_PRB_THRESH = 40; // s2cloudless
var BUFFER = 50; // dilatação (m)

// Pasta = /content/drive/MyDrive/GEE_DataSet

// AOI pelo retangulo entre os dois pontos diagonais
// Pontos (lat, lon):
// Ponto 1: 4°29'45"S 58°20'19"W → lat -4.495833, lon -58.338611 v2
// Ponto 2: 8°32'46"S 54°41'01"W → lat -8.546111, lon -54.683611 v2
// GEE Rectangle: [lon_min, lat_min, lon_max, lat_max]
var aoi = ee.Geometry.Rectangle(
  [-58.338611, -8.546111, -54.683611, -4.495833], // xmin, ymin, xmax, ymax  
  null, false  // geodesic=false para bordas retas
);

Map.centerObject(aoi, 7);

// Sentinel-2 (SR + s2cloudless)
function getS2SR() {
  var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi).filterDate(START, END)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60));

  var s2clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
    .filterBounds(aoi).filterDate(START, END);

  var joined = ee.ImageCollection(ee.Join.saveFirst('cloud_mask').apply({
    primary: s2, secondary: s2clouds,
    condition: ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'})
  }));

  // Mascara robusta (sem directionalDistanceTransform)
  function maskCloudsAndShadows(img) {
    var cldPrb = ee.Image(img.get('cloud_mask')).select('probability');
    var isCloud = cldPrb.gt(CLD_PRB_THRESH);

    // escuros no NIR (B8) ajudam a capturar sombra
    var nirDark = img.select('B8').lt(0.15);

    // dilata nuvem e pontos escuros como sombras (regiao escura perto de nuvens)
    var cloudDilated  = isCloud.focal_max(BUFFER);
    var darkDilated   = nirDark.focal_max(BUFFER);
    var shadowsApprox = darkDilated.and(cloudDilated);

    var mask = cloudDilated.or(shadowsApprox).not();

    return img.updateMask(mask)
              .select(['B2','B3','B4','B8','B11','B12'])
              .divide(10000)
              .copyProperties(img, img.propertyNames());
  }

  return joined.map(maskCloudsAndShadows);
}

// Landsat 8/9 L2
function maskLandsatL2(img) {
  var refl = img.select(['SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7'])
                .multiply(0.0000275).add(-0.2)
                .rename(['B2','B3','B4','B5','B6','B7']);
  var qa = img.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(1<<1).eq(0)
           .and(qa.bitwiseAnd(1<<3).eq(0))
           .and(qa.bitwiseAnd(1<<4).eq(0))
           .and(qa.bitwiseAnd(1<<5).eq(0));
  return refl.updateMask(mask).copyProperties(img, img.propertyNames());
}
function getLandsat() {
  var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(aoi).filterDate(START, END);
  var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(aoi).filterDate(START, END);
  return l8.merge(l9).map(maskLandsatL2).select(['B2','B3','B4','B5','B6','B7']);
}

// Composites (median)
var s2Median = getS2SR().median().clip(aoi);
var lsMedian = getLandsat().median().clip(aoi);

// Visualizacao
Map.addLayer(s2Median, {bands:['B4','B3','B2'], min:0.02, max:0.3}, 'S2 median RGB');
Map.addLayer(s2Median, {bands:['B12','B8','B4'], min:0.02, max:0.35}, 'S2 SWIR comp');
Map.addLayer(lsMedian, {bands:['B4','B3','B2'], min:0.02, max:0.3}, 'Landsat median RGB');

// Exports 
Export.image.toDrive({
  image: s2Median,
  description: 'v3_new_ret_s2_median_2024_dry',
  fileNamePrefix: 'v3_new_ret_s2_median_2024_dry',
  region: aoi, scale: 10, maxPixels: 1e13, crs: 'EPSG:4326'
});
Export.image.toDrive({
  image: lsMedian,
  description: 'v3_new_ret_ls_median_2024_dry',
  fileNamePrefix: 'v3_new_ret_ls_median_2024_dry',
  region: aoi, scale: 30, maxPixels: 1e13, crs: 'EPSG:4326'
});

// Grid (chips de 2.56 km)
function makeGrid(region, cellSizeMeters){
  var proj = ee.Image().projection().atScale(cellSizeMeters);
  return ee.Geometry(region).bounds().coveringGrid(proj);
}
var CHIP_SIZE_M = 2560; 
var grid = makeGrid(aoi, CHIP_SIZE_M);
Map.addLayer(grid, {}, 'grid chips');
