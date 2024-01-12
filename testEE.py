import ee
ee.Authenticate()
ee.Initialize(project='potential-evap')
print(ee.Image("NASA/NASADEM_HGT/001").get("title").getInfo())