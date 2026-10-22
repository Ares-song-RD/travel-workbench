# -*- coding: utf-8 -*-
"""预处理市级行政区划数据：精简字段 + 坐标精度压缩 + 合并"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CITY_DIR = os.path.join(BASE, 'assets', 'cities')

def round_coords(ring, prec=3):
    out = []
    for pt in ring:
        out.append([round(pt[0], prec), round(pt[1], prec)])
    return out

def process(feature):
    p = feature['properties']
    g = feature['geometry']
    out = {
        'adcode': str(p['adcode']),
        'name': p['name'],
        'level': p.get('level', 'city'),
        'center': [round(p['center'][0], 5), round(p['center'][1], 5)],
    }
    # 保留质心（标签定位更准确）
    if p.get('centroid'):
        out['centroid'] = [round(p['centroid'][0], 5), round(p['centroid'][1], 5)]
    # 压缩几何：统一存成 [polygon][ring][point] 三层结构
    coords = g['coordinates']
    if g['type'] == 'MultiPolygon':
        new_coords = [[round_coords(ring) for ring in poly] for poly in coords]
    else:  # Polygon
        new_coords = [[round_coords(ring) for ring in coords]]
    out['g'] = new_coords
    return out

def main():
    result = {}
    geo = json.load(open(os.path.join(BASE, 'assets', 'china_geo.json')))
    total = 0
    for f in geo['features']:
        ac = str(f['properties'].get('adcode'))
        if ac == '100000_JD':
            continue
        path = os.path.join(CITY_DIR, ac + '.json')
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        feats = [process(x) for x in d['features']]
        result[ac] = feats
        size = len(json.dumps(feats, ensure_ascii=False, separators=(',', ':')))
        total += size
        print(f'{ac} {f["properties"]["name"]}: {len(feats)} 个区划, {size/1024:.0f}KB')

    out_path = os.path.join(BASE, 'assets', 'cities_merged.json')
    s = json.dumps(result, ensure_ascii=False, separators=(',', ':'))
    open(out_path, 'w').write(s)
    print(f'\n合并文件: {out_path}, 大小 {len(s.encode("utf-8"))/1024:.0f}KB')

if __name__ == '__main__':
    main()
