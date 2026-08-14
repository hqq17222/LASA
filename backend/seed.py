# 拉萨南北山生态监测评估系统数据种子
# 依据《拉萨南北山生态系统修复成效与稳定性监测评估技术实施方案》附录 A/B/C 初始化
import sys, os, random, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, init_db
from app.models import Project, DataSource, Observation, Alarm, Equipment, PhasePlan, PatrolPhoto


def _create_sample_photo(session, project_id, filename, lon, lat, flight_date, flight_route, defect_type="", defect_desc=""):
    """Create a sample patrol photo record with generated image."""
    from pathlib import Path
    from PIL import Image
    import io

    if session.query(PatrolPhoto).filter_by(project_id=project_id, original_name=filename).first():
        return

    img = Image.new('RGB', (640, 480), color=(random.randint(100, 200), random.randint(120, 220), random.randint(80, 180)))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    for _ in range(5):
        x1, y1 = random.randint(0, 500), random.randint(0, 300)
        x2, y2 = x1 + random.randint(50, 150), y1 + random.randint(30, 100)
        color = (random.randint(40, 120), random.randint(80, 160), random.randint(30, 100))
        draw.rectangle([x1, y1, x2, y2], fill=color)

    def _decimal_to_dms(value):
        degrees = int(value)
        minutes_float = (value - degrees) * 60
        minutes = int(minutes_float)
        seconds = round((minutes_float - minutes) * 60, 6)
        return ((degrees, 1), (minutes, 1), (int(seconds * 1000000), 1000000))

    exif_dict = {}
    exif_dict[271] = "DJI"
    exif_dict[272] = "M300RTK"
    exif_dict[306] = flight_date.replace("-", ":") + " 10:30:00"
    exif_dict[36867] = flight_date.replace("-", ":") + " 10:30:00"
    gps_ifd = {}
    gps_ifd[1] = 'N' if lat >= 0 else 'S'
    gps_ifd[2] = _decimal_to_dms(abs(lat))
    gps_ifd[3] = 'E' if lon >= 0 else 'W'
    gps_ifd[4] = _decimal_to_dms(abs(lon))
    gps_ifd[6] = (int(3700), 100)
    exif_dict[34853] = gps_ifd

    from app.core.config import settings
    dest_name = f"patrol_{project_id}_{filename}"
    dest_path = settings.UPLOAD_DIR / dest_name
    img.save(str(dest_path), "JPEG", exif=exif_dict)

    pp = PatrolPhoto(
        project_id=project_id,
        file_path=f"/static/{dest_name}",
        original_name=filename,
        lon=lon,
        lat=lat,
        altitude=37.0,
        flight_date=flight_date,
        flight_route=flight_route,
        photo_time=datetime.datetime.strptime(f"{flight_date} 10:30:00", "%Y-%m-%d %H:%M:%S"),
        camera_make="DJI",
        camera_model="M300RTK",
        image_width=640,
        image_height=480,
        defect_type=defect_type,
        defect_desc=defect_desc,
        defect_confidence=round(random.uniform(0.65, 0.95), 2) if defect_type else 0.0,
    )
    session.add(pp)
    session.commit()
    return pp


def _seed_patrol_photos(session, project_id):
    """Seed sample patrol photos with GPS coordinates."""
    if session.query(PatrolPhoto).filter_by(project_id=project_id).count() > 0:
        return

    base_lon, base_lat = 91.08, 29.64
    for i in range(6):
        _create_sample_photo(
            session, project_id,
            f"A01_{i+1:03d}.jpg",
            base_lon + i * 0.005,
            base_lat + random.uniform(-0.002, 0.002),
            "2026-07-15", "航线-A01",
            defect_type="" if i < 4 else "植被退化",
            defect_desc="" if i < 4 else "该片区植被覆盖度明显下降，建议补植",
        )

    base_lon, base_lat = 91.10, 29.65
    for i in range(5):
        _create_sample_photo(
            session, project_id,
            f"A02_{i+1:03d}.jpg",
            base_lon + i * 0.004,
            base_lat + random.uniform(-0.002, 0.002),
            "2026-07-15", "航线-A02",
            defect_type="" if i < 3 else "裸露",
            defect_desc="" if i < 3 else "边坡裸露面积扩大，需关注水土流失",
        )

    base_lon, base_lat = 91.06, 29.63
    for i in range(4):
        _create_sample_photo(
            session, project_id,
            f"B01_{i+1:03d}.jpg",
            base_lon + i * 0.006,
            base_lat + random.uniform(-0.003, 0.003),
            "2026-07-22", "航线-B01",
            defect_type="" if i < 2 else "病虫害",
            defect_desc="" if i < 2 else "发现疑似病虫害斑块，建议开展专项调查",
        )

    base_lon, base_lat = 91.12, 29.66
    for i in range(4):
        _create_sample_photo(
            session, project_id,
            f"B02_{i+1:03d}.jpg",
            base_lon + i * 0.005,
            base_lat + random.uniform(-0.002, 0.002),
            "2026-07-22", "航线-B02",
            defect_type="",
            defect_desc="",
        )

    print(f"Seeded {session.query(PatrolPhoto).filter_by(project_id=project_id).count()} patrol photos")


def run_seed():
    session = SessionLocal()

    # 创建项目
    p = session.query(Project).filter_by(code='LSKJ202622-DEMO').first()
    if not p:
        p = Project(
            name='拉萨南北山绿化工程示范样地',
            code='LSKJ202622-DEMO',
            description='用于系统调试与演示的虚拟样地，覆盖 3 个林班。坐标系统一采用 CGCS2000 / 高斯-克吕格3度带 91°30′E。',
            geometry_geojson=json.dumps({
                "type": "Polygon",
                "coordinates": [[
                    [91.05, 29.62], [91.15, 29.62], [91.15, 29.68], [91.05, 29.68], [91.05, 29.62]
                ]]
            })
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        print(f"Created project {p.id}")

    # 数据源
    ds = session.query(DataSource).filter_by(project_id=p.id, source_type='sample').first()
    if not ds:
        ds = DataSource(
            project_id=p.id,
            name='样地调查 2026',
            source_type='sample',
            format='csv',
            file_path='',
            naming_rule='LSNS-SAMPLE-XYQ-202607-V1.0.csv',
            quality_level='A',
            version='V1.0',
            coordinate_system='CGCS2000 / 高斯-克吕格3度带 91°30′E',
            meta_json='{}'
        )
        session.add(ds); session.commit(); session.refresh(ds)

    base_date = datetime.datetime(2026, 1, 1)

    def add_obs(name, values, text_values=None):
        if session.query(Observation).filter_by(project_id=p.id, indicator_name=name).count() > 0:
            return
        for i, v in enumerate(values):
            obs = Observation(
                project_id=p.id,
                indicator_name=name,
                sample_time=base_date + datetime.timedelta(days=i*30),
                lon=91.05 + random.random()*0.10,
                lat=29.62 + random.random()*0.06,
                value=v,
                value_text=text_values[i] if text_values and i < len(text_values) else "",
                source_id=ds.id,
            )
            session.add(obs)
        session.commit()
        print(f"Seeded observations for {name}")

    # 结构指标示例
    add_obs("ndvi", [0.30, 0.33, 0.36, 0.40, 0.43, 0.46])
    add_obs("fvc", [45.0, 50.0, 55.0, 60.0, 63.0, 66.0])
    add_obs("bl", [35.0, 30.0, 26.0, 22.0, 20.0, 18.0])
    add_obs("cc", [0.20, 0.24, 0.28, 0.31, 0.34, 0.37])
    add_obs("shannon", [None]*5, ['沙棘','江孜沙棘','锦鸡儿','杨','柳'])

    # 功能指标示例
    add_obs("wh", [120.5, 125.0, 130.2, 128.6, 135.0])
    add_obs("cs", [800.0, 950.0, 1100.0, 1250.0, 1400.0])
    add_obs("sc", [1500.0, 1600.0, 1750.0, 1850.0, 2000.0])
    add_obs("hq", [0.45, 0.48, 0.51, 0.53, 0.56])
    add_obs("sf", [1.5, 1.7, 1.9, 2.1, 2.3])
    add_obs("tc", [1.0, 1.2, 1.4, 1.5, 1.7])

    # 压力指标示例
    add_obs("smc", [12.0, 14.0, 15.5, 16.0, 14.5, 13.0])
    add_obs("spi", [-0.8, -0.6, -0.4, -0.2, -0.5])
    add_obs("sai", [40.0, 35.0, 32.0, 28.0, 25.0])
    add_obs("pa", [8.0, 6.0, 5.0, 4.0, 3.0])
    add_obs("fwi", [3.0, 3.5, 4.0, 3.2, 2.8])

    # 工程响应指标示例
    add_obs("sr", [78.0, 82.0, 85.0, 87.0, 89.0])
    add_obs("ir", [85.0, 88.0, 90.0, 92.0, 94.0])
    add_obs("frr", [75.0, 78.0, 80.0, 83.0, 85.0])
    add_obs("pr", [90.0, 93.0, 95.0, 97.0, 98.0])
    add_obs("pi", [88.0, 89.0, 90.0, 91.0, 92.0])

    # 稳定性指标示例
    add_obs("cv", [0.30, 0.28, 0.26, 0.24, 0.22])
    add_obs("er", [0.40, 0.45, 0.50, 0.55, 0.60])
    add_obs("sem", [500.0, 480.0, 460.0, 440.0, 420.0])
    add_obs("sdr", [12.0, 11.0, 10.0, 9.0, 8.0])
    add_obs("st", [0.30, 0.40, 0.50, 0.60, 0.70])

    # 预警
    if session.query(Alarm).filter_by(project_id=p.id).count() == 0:
        a = Alarm(project_id=p.id, alarm_type='deviation', level='yellow', title='B-12 NDVI 变化率低于均值 30%', message='建议检查灌溉设施', indicator_name='ndvi')
        session.add(a); session.commit()
        print("Seeded alarm")

    # 设备清单（附录 C）
    equipment_seed = [
        {"category": "satellite", "name": "高分二号/六号多光谱影像", "model_no": "GF-2/GF-6", "specs": "1—4m/8m 多光谱", "quantity": 1, "frequency": "季度", "purpose": "覆盖度变化、土地利用分类"},
        {"category": "satellite", "name": "哨兵二号多光谱影像", "model_no": "Sentinel-2", "specs": "10m 多光谱", "quantity": 1, "frequency": "月度", "purpose": "植被指数时序、大尺度监测"},
        {"category": "satellite", "name": "PlanetScope多光谱影像", "model_no": "PlanetScope", "specs": "3—5m 多光谱", "quantity": 1, "frequency": "月度", "purpose": "高频变化检测"},
        {"category": "satellite", "name": "InSAR卫星数据", "model_no": "SAR", "specs": "3—20m SAR干涉像对", "quantity": 1, "frequency": "月度/季度", "purpose": "边坡形变监测"},
        {"category": "uav", "name": "多光谱无人机", "model_no": "DJI P4M或同级", "specs": "5cm", "quantity": 2, "frequency": "季度/按需", "purpose": "植被指数、病虫害斑块"},
        {"category": "uav", "name": "激光雷达无人机", "model_no": "L1或同级", "specs": "10cm", "quantity": 1, "frequency": "半年/按需", "purpose": "地形DEM、林冠结构"},
        {"category": "uav", "name": "长航时巡检无人机", "model_no": "M300 RTK或同级", "specs": "可见光", "quantity": 1, "frequency": "月度", "purpose": "重点区域巡检、火情巡护"},
        {"category": "uav", "name": "大载重喷播无人机", "model_no": "T50或同级", "specs": "—", "quantity": 1, "frequency": "按需", "purpose": "高陡边坡种子基质喷播"},
        {"category": "sensor", "name": "自动气象站", "model_no": "—", "specs": "温湿度、风速风向、气压、辐射、降水", "quantity": 5, "frequency": "10min", "purpose": "蒸散发计算、火险评估"},
        {"category": "sensor", "name": "土壤水分传感器", "model_no": "FDR/TDR", "specs": "多层（10/20/40cm）", "quantity": 20, "frequency": "30min", "purpose": "水分亏缺预警"},
        {"category": "sensor", "name": "树干径流传感器", "model_no": "热扩散式", "specs": "0.01mm精度", "quantity": 10, "frequency": "1h", "purpose": "植物生理耗水"},
        {"category": "sensor", "name": "叶片水势传感器", "model_no": "压力室或原位式", "specs": "—", "quantity": 5, "frequency": "日/周", "purpose": "水分胁迫诊断"},
        {"category": "sensor", "name": "热成像云台摄像机", "model_no": "双光谱", "specs": "10km侦测", "quantity": 8, "frequency": "实时", "purpose": "火情识别、野生动物监测"},
        {"category": "sensor", "name": "手持三维扫描仪", "model_no": "—", "specs": "厘米级植被表型", "quantity": 2, "frequency": "按需", "purpose": "重点植株表型采集"},
        {"category": "communication", "name": "5G/4G网关", "model_no": "—", "specs": "公网回传", "quantity": 1, "frequency": "实时", "purpose": "有覆盖区域数据回传"},
        {"category": "communication", "name": "LoRa自组网", "model_no": "—", "specs": "低功耗窄带", "quantity": 1, "frequency": "小时", "purpose": "无公网区域传感器汇聚"},
        {"category": "communication", "name": "370MHz窄带通信", "model_no": "—", "specs": "应急通信", "quantity": 1, "frequency": "按需", "purpose": "偏远山区可靠回传"},
        {"category": "compute", "name": "边缘计算节点", "model_no": "NVIDIA Jetson或同级", "specs": "前端AI推理", "quantity": 2, "frequency": "实时", "purpose": "数据预处理"},
        {"category": "compute", "name": "云服务器", "model_no": "CPU+GPU", "specs": "≥64核/512GB", "quantity": 1, "frequency": "7×24h", "purpose": "平台部署、模型训练"},
    ]

    if session.query(Equipment).filter_by(project_id=p.id).count() == 0:
        for e in equipment_seed:
            eq = Equipment(project_id=p.id, **e)
            session.add(eq)
        session.commit()
        print(f"Seeded {len(equipment_seed)} equipments")

    # 阶段计划（第8章）
    phase_seed = [
        {
            "phase_no": 1,
            "name": "基础构建期",
            "time_range": "2026.01—2026.06",
            "goal": "完成工程区底图构建、监测设备选型与布点、数据规范制定、样地调查方案设计",
            "key_tasks": "资料整合；典型区踏勘；点位设计；指标确认；坐标系统一转换",
            "deliverables": "底图数据集、设备布点方案、数据规范文档、样地调查大纲",
            "milestones": "实施方案、底图、指标体系初稿",
            "progress": 30.0,
            "status": "ongoing",
        },
        {
            "phase_no": 2,
            "name": "平台搭建与试点期",
            "time_range": "2026.07—2027.06",
            "goal": "完成平台框架开发、多源数据接入、核心算法验证、典型区监测试点",
            "key_tasks": "传感器布设；数据链路搭建；平台开发；联调测试；多源数据融合",
            "deliverables": "平台V1.0、试点区评估报告、算法参数库、技术规程初稿",
            "milestones": "平台试运行版、数据规范",
            "progress": 0.0,
            "status": "pending",
        },
        {
            "phase_no": 3,
            "name": "模型完善与推广期",
            "time_range": "2027.07—2028.06",
            "goal": "优化评估模型、扩展示范应用场景、形成稳定运行的业务化流程、开展多单位协同应用",
            "key_tasks": "成效评估；气候适应性与滞后效应验证；示范应用扩展；多单位协同",
            "deliverables": "平台V2.0、多场景示范报告、模型优化说明、年度总结报告",
            "milestones": "典型区评估报告、模型参数库",
            "progress": 0.0,
            "status": "pending",
        },
        {
            "phase_no": 4,
            "name": "总结凝练与验收期",
            "time_range": "2028.07—2028.12",
            "goal": "整理项目数据与成果、编制标准文本与操作手册、组织专家验收、形成可推广模式",
            "key_tasks": "数据与成果整理；标准/规程编制；专家验收；推广应用准备",
            "deliverables": "验收报告、标准/规程文本、成果数据集、推广应用方案",
            "milestones": "技术规程、研究报告、验收材料",
            "progress": 0.0,
            "status": "pending",
        },
    ]

    if session.query(PhasePlan).filter_by(project_id=p.id).count() == 0:
        for ph in phase_seed:
            pp = PhasePlan(project_id=p.id, **ph)
            session.add(pp)
        session.commit()
        print(f"Seeded {len(phase_seed)} phase plans")

    # 巡检照片示例
    _seed_patrol_photos(session, p.id)

    session.close()
    print("Seed done")


if __name__ == '__main__':
    init_db()
    run_seed()
