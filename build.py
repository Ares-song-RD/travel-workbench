# -*- coding: utf-8 -*-
"""构建脚本：把地图 GeoJSON 和城市坐标注入 HTML 模板，生成最终单文件应用"""
import json
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from cities import CITIES, PROVINCE_INTRO, TAIWAN_COUNTIES

def main():
    # 读取模板
    with open(os.path.join(BASE, 'template.html'), 'r', encoding='utf-8') as f:
        html = f.read()

    # 读取 GeoJSON（去除九段线，只保留省份）
    with open(os.path.join(BASE, 'assets', 'china_geo.json'), 'r', encoding='utf-8') as f:
        geo = json.load(f)
    feats = [f for f in geo['features'] if f['properties'].get('adcode') != '100000_JD']
    geo_out = {'type': 'FeatureCollection', 'features': feats}
    geo_json = json.dumps(geo_out, ensure_ascii=False, separators=(',', ':'))

    # 读取市级区划合并数据
    with open(os.path.join(BASE, 'assets', 'cities_merged.json'), 'r', encoding='utf-8') as f:
        city_geo = json.load(f)
    # 台湾省用简化县市点数据（DataV 无边界）
    taiwan = [{'adcode': '710000_' + str(i), 'name': c['name'], 'level': 'city',
               'center': [round(c['lng'], 5), round(c['lat'], 5)], 'point': True,
               'lng': round(c['lng'], 5), 'lat': round(c['lat'], 5)}
              for i, c in enumerate(TAIWAN_COUNTIES)]
    city_geo['710000'] = taiwan
    city_geo_json = json.dumps(city_geo, ensure_ascii=False, separators=(',', ':'))

    cities_json = json.dumps(CITIES, ensure_ascii=False, separators=(',', ':'))
    intro_json = json.dumps(PROVINCE_INTRO, ensure_ascii=False, separators=(',', ':'))

    html = html.replace('__GEO__', geo_json)
    html = html.replace('__CITIES__', cities_json)
    html = html.replace('__INTRO__', intro_json)
    html = html.replace('__CITY_GEO__', city_geo_json)

    out_path = os.path.join(BASE, '旅途记录工作台.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print('生成成功:', out_path)
    print('文件大小: %.1f KB' % (os.path.getsize(out_path) / 1024))

if __name__ == '__main__':
    main()
