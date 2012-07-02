# coding=utf-8

u"""PENTAX Optio WG-1 GPS で撮影した動画から位置情報などを取得する。

PENTAX Optio WG-1 GPS (http://www.pentax.jp/japan/products/wg-1/)
で撮影した動画から撮影日時、サムネイル、位置情報を取得する。
他の機種では動作しない。
"""

import re
from datetime import datetime
from struct import unpack, calcsize

# http://www.awaresystems.be/imaging/tiff/tifftags/privateifd/gps.html
GPS_VERSION_ID = 0
GPS_LATITUDE_REF = 1
GPS_LATITUDE = 2
GPS_LONGITUDE_REF = 3
GPS_LONGITUDE = 4
GPS_ALTITUDE_REF = 5
GPS_ALTITUDE = 6
GPS_TIME_STAMP = 7
GPS_SATELLITES = 8
GPS_STATUS = 9
GPS_MEASURE_MODE = 10
GPS_MAP_DATUM = 18
GPS_DATE_STAMP = 29


class Metadata(object):
    u"""動画のメタデータ。"""

    def __init__(self, camera_model, datetime_original, thumbnail, gpsinfo):
        self._camera_model = camera_model
        self._datetime_original = datetime_original
        self._thumbnail = thumbnail
        self._gpsinfo = gpsinfo

    @property
    def camera_model(self):
        u"""機種名を取得する。"""
        return self._camera_model

    @property
    def datetime_original(self):
        u"""撮影日時を取得する。

        カメラ本体のワールドタイムで設定されている場所の現地時間となる。
        """
        return self._datetime_original

    @property
    def thumbnail(self):
        u"""サムネイルのバイナリデータを取得する。"""
        return self._thumbnail

    def save_thumbnail(self, fname):
        u"""サムネイルをファイルに保存する。"""
        with open(fname, "wb") as f:
            f.write(self._thumbnail)

    @property
    def gpsinfo(self):
        u"""位置情報を辞書として取得する。

        位置情報が存在しない場合はNoneを返す。
        """
        return self._gpsinfo

    @property
    def gps_version_id(self):
        u"""GPSInfoIFDのバージョンを取得する。

        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            return ".".join(map(str, self._gpsinfo[GPS_VERSION_ID]))

    @property
    def gps_latitude(self):
        u"""緯度をdegree形式(単位は度)で取得する。

        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            latitude = self._latlong_deg(self._gpsinfo[GPS_LATITUDE])
            if self._gpsinfo[GPS_LATITUDE_REF] == "S":
                latitude = -latitude
            return latitude

    @property
    def gps_longitude(self):
        u"""経度をdegree形式(単位は度)で取得する。

        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            longitude = self._latlong_deg(self._gpsinfo[GPS_LONGITUDE])
            if self._gpsinfo[GPS_LONGITUDE_REF] == "W":
                longitude = -longitude
            return longitude

    @property
    def gps_altitude(self):
        u"""高度(単位はm)を取得する。

        海面下の場合は負の値となる。
        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            altitude = float(self._gpsinfo[GPS_ALTITUDE][0]) \
                    / self._gpsinfo[GPS_ALTITUDE][1]
            if self._gpsinfo[GPS_ALTITUDE_REF] == 1:
                altitude = -altitude
            return altitude

    @property
    def gps_satellites(self):
        u"""測位に使った衛星の情報を取得する。

        書式に規定がないため詳細は不明。(おそらく使用衛星数)
        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            return self._gpsinfo[GPS_SATELLITES]

    @property
    def gps_status(self):
        u"""撮影時のGPS受信機の状態を取得する。

        'A': 測位
        'V': 非測位
        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            return self._gpsinfo[GPS_STATUS]

    @property
    def gps_measure_mode(self):
        u"""測位モードを取得する。

        '2': 2次元測位
        '3': 3次元測位
        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            return self._gpsinfo[GPS_MEASURE_MODE]

    @property
    def gps_map_datum(self):
        u"""測位系('WGS-84'など)を取得する。

        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            return self._gpsinfo[GPS_MAP_DATUM]

    @property
    def gps_datetime(self):
        u"""測位時刻(UTC)を取得する。

        位置情報が存在しない場合はNoneを返す。
        """
        if self._gpsinfo:
            t = [str(int(r[0] / r[1])) for r in self._gpsinfo[GPS_TIME_STAMP]]
            timestamp = ":".join(t)
            datestamp = self._gpsinfo[GPS_DATE_STAMP].replace(':', '/')
            return datetime.strptime(datestamp + " " + timestamp,
                                     "%Y/%m/%d %H:%M:%S")

    def _latlong_deg(self, rationals):
        u"""緯度、経度をdegree形式に変換する。"""
        d = [float(r[0]) / r[1] for r in rationals]
        return d[0] + d[1] / 60 + d[2] / 3600


def get_avi_metadata(fname):
    u"""PENTAX Optio WG-1 GPS で撮影した動画から Metadata を取得する。

    他の機種で撮影した動画の場合、ファイル形式が異なる場合などはNoneを返す。
    """
    junk_chunk = _get_junk_chunk(fname)
    if junk_chunk:
        gpsformat = '<4B2s6L2s6LB2L16x6L3s2s2s7s11s'
        pattern = r'(%s).*?(%s).*?(%s)GPS_(%s)' % (
            r'PENTAX Optio WG-1 GPS',
            r'[A-Z][a-z]{2} [A-Z][a-z]{2} \d{2} \d{2}:\d{2}:\d{2} \d{4}',
            r'\xFF\xD8.*\xFF\xD9',
            r'.{%d}' % calcsize(gpsformat))
        m = re.search(pattern, junk_chunk, re.S)
        if m:
            camera_model = m.group(1)
            datetime_original = datetime.strptime(m.group(2),
                                                  "%a %b %d %H:%M:%S %Y")
            thumbnail = m.group(3)
            gpsdata = list(unpack(gpsformat, m.group(4)))
            gpsinfo = {
                GPS_VERSION_ID:     gpsdata[0:4],
                GPS_LATITUDE_REF:   gpsdata[4].rstrip(' \0'),
                GPS_LATITUDE:       zip(gpsdata[5:11:2], gpsdata[6:11:2]),
                GPS_LONGITUDE_REF:  gpsdata[11].rstrip(' \0'),
                GPS_LONGITUDE:      zip(gpsdata[12:18:2], gpsdata[13:18:2]),
                GPS_ALTITUDE_REF:   gpsdata[18],
                GPS_ALTITUDE:       (gpsdata[19], gpsdata[20]),
                GPS_TIME_STAMP:     zip(gpsdata[21:27:2], gpsdata[22:27:2]),
                GPS_SATELLITES:     gpsdata[27].rstrip(' \0'),
                GPS_STATUS:         gpsdata[28].rstrip(' \0'),
                GPS_MEASURE_MODE:   gpsdata[29].rstrip(' \0'),
                GPS_MAP_DATUM:      gpsdata[30].rstrip(' \0'),
                GPS_DATE_STAMP:     gpsdata[31].rstrip(' \0')
            }
            if gpsinfo[GPS_LATITUDE_REF] == '':
                gpsinfo = None
            return Metadata(camera_model,
                            datetime_original,
                            thumbnail,
                            gpsinfo)


def _get_junk_chunk(fname):
    u"""AVIファイルのヘッダからJUNKチャンクを取得する。

    見つからない場合はNoneを返す。
    """
    with open(fname, 'rb') as f:
        chunk, size, type = unpack('<4sL4s', f.read(12))
        if chunk == 'RIFF' and type == 'AVI ':
            while True:
                chunk, size = unpack('<4sL', f.read(8))
                if chunk == 'JUNK':
                    return f.read(size)
                elif chunk == 'LIST':
                    if f.read(4) == 'movi':
                        return
                    else:
                        f.seek(size - 4, 1)
                else:
                    f.seek(size, 1)
