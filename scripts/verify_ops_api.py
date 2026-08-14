"""端到端验证：样地 CRUD/状态、共享图层、轨迹用户归属、人员状态。"""
import requests, json
B = 'http://106.15.35.204:18480'
t = requests.post(B + '/api/v1/auth/login', json={'username': 'admin', 'password': '30010223'}, timeout=30).json()['token']
H = {'Authorization': f'Bearer {t}'}

r = requests.post(B + '/api/v1/field/plots', json={'project_id': 1, 'code': 'NT-TEST', 'name': '测试样地', 'lon': 91.17, 'lat': 29.65, 'radius': 30}, headers=H, timeout=30)
print('创建样地:', r.status_code); pid = r.json().get('id')
r = requests.get(B + '/api/v1/field/plots?project_id=1', headers=H, timeout=30)
print('样地列表:', r.status_code, [(p['code'], p['status'], p['photo_count']) for p in r.json()])

gj = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [91.12, 29.66]}, 'properties': {'code': 'NT-I1', 'name': '导入样地'}}]}
r = requests.post(B + '/api/v1/field/plots/import?project_id=1', json={'geojson': gj}, headers=H, timeout=30)
print('导入样地:', r.status_code, r.json())

layer = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'Polygon', 'coordinates': [[[91.1, 29.6], [91.2, 29.6], [91.2, 29.7], [91.1, 29.7], [91.1, 29.6]]]}, 'properties': {'name': '研究区边界'}}]}
r = requests.post(B + '/api/v1/field/layers', json={'project_id': 1, 'name': '研究区边界.geojson', 'fmt': 'geojson', 'content': json.dumps(layer), 'color': '#2470d8'}, headers=H, timeout=30)
print('上传图层:', r.status_code); lid = r.json().get('id')
r = requests.get(B + '/api/v1/field/layers?project_id=1', headers=H, timeout=30)
print('图层列表:', r.status_code, [(l['name'], l['fmt'], l['created_by']) for l in r.json()])

r = requests.post(B + '/api/v1/field/tracks', json={'name': '接口验证轨迹', 'src': 'app', 'points_json': '[[29.65,91.11,3650,"2026-08-08T10:00:00Z"],[29.651,91.112,3655,"2026-08-08T10:05:00Z"]]', 'point_count': 2, 'distance_km': 0.15}, headers=H, timeout=30)
print('创建轨迹:', r.status_code, '归属:', r.json().get('username'), r.json().get('display_name')); tid = r.json().get('id')
r = requests.get(B + '/api/v1/field/team-status', headers=H, timeout=30)
print('人员状态:', r.status_code, json.dumps(r.json(), ensure_ascii=False)[:300])

requests.delete(B + f'/api/v1/field/plots/{pid}', headers=H, timeout=30)
requests.delete(B + f'/api/v1/field/layers/{lid}', headers=H, timeout=30)
requests.delete(B + f'/api/v1/field/tracks/{tid}', headers=H, timeout=30)
for p in requests.get(B + '/api/v1/field/plots?project_id=1', headers=H, timeout=30).json():
    if p['code'] == 'NT-I1':
        requests.delete(B + f"/api/v1/field/plots/{p['id']}", headers=H, timeout=30)
print('测试数据已清理')
