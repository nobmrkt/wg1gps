wg1gps
======
PENTAX Optio WG-1 GPS で撮影した動画から位置情報などを取得する。

製品ページ http://www.pentax.jp/japan/products/wg-1/


使用例
------
### コード ###
    import wg1gps
    meta = wg1gps.get_avi_metadata("IMGP0147.AVI")
    print "CameraModel:", meta.camera_model
    print "DateTimeOriginal:", meta.datetime_original
    print "GPSVersionID:", meta.gps_version_id
    print "GPSDateTime:", meta.gps_datetime
    print "GPSLatitude:", meta.gps_latitude
    print "GPSLongitude:", meta.gps_longitude
    print "GPSAltitude:", meta.gps_altitude
    print "GPSSatellites:", meta.gps_satellites
    print "GPSStatus:", meta.gps_status
    print "GPSMeasureMode:", meta.gps_measure_mode
    print "GPSMapDatum:", meta.gps_map_datum
    print "https://maps.google.co.jp/maps?q=%f,%f" % (meta.gps_latitude,
                                                      meta.gps_longitude)

### 出力 ###
    CameraModel: PENTAX Optio WG-1 GPS
    DateTimeOriginal: 2011-08-24 13:49:11
    GPSVersionID: 2.3.0.0
    GPSDateTime: 2011-08-24 11:49:56
    GPSLatitude: 48.44688
    GPSLongitude: 2.637815
    GPSAltitude: 103.2
    GPSSatellites: 07
    GPSStatus: A
    GPSMeasureMode: 3
    GPSMapDatum: WGS-84
    https://maps.google.co.jp/maps?q=48.446880,2.637815
