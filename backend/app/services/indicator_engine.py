# 拉萨南北山生态修复成效与稳定性评估指标引擎
# 文档来源：附录 A《监测评估指标体系》
from typing import List, Dict, Any, Optional
from app.models import Observation
import math
import statistics

# 五维指标体系：结构 / 功能 / 压力 / 工程响应 / 稳定性
INDICATOR_META: Dict[str, Dict[str, Any]] = {
    # === 结构指标 ===
    "fvc": {
        "display_name": "植被覆盖度",
        "symbol": "FVC",
        "dimension": "structure",
        "unit": "%",
        "formula": "(植被像元数/总像元数)×100%",
        "data_source": "遥感反演",
        "threshold": "≥65%",
        "desc": "反映区域植被覆盖比例，判断恢复是否“绿起来”",
    },
    "ndvi": {
        "display_name": "归一化植被指数",
        "symbol": "NDVI",
        "dimension": "structure",
        "unit": "",
        "formula": "(NIR−Red)/(NIR+Red)",
        "data_source": "遥感/无人机",
        "threshold": "≥0.45",
        "desc": "生长季均值，反映植被长势",
    },
    "shannon": {
        "display_name": "树种多样性指数",
        "symbol": "Shannon",
        "dimension": "structure",
        "unit": "",
        "formula": "−ΣPi×ln(Pi)",
        "data_source": "样地调查",
        "threshold": "≥1.2",
        "desc": "反映群落物种多样性",
    },
    "fn": {
        "display_name": "景观破碎度",
        "symbol": "FN",
        "dimension": "structure",
        "unit": "",
        "formula": "斑块数/总面积",
        "data_source": "遥感分类",
        "threshold": "≤0.15",
        "desc": "反映景观格局完整性",
    },
    "bl": {
        "display_name": "裸地比例",
        "symbol": "BL",
        "dimension": "structure",
        "unit": "%",
        "formula": "裸地面积/总面积×100%",
        "data_source": "遥感分类",
        "threshold": "≤20%",
        "desc": "反映裸地退化程度",
    },
    "cc": {
        "display_name": "郁闭度",
        "symbol": "CC",
        "dimension": "structure",
        "unit": "",
        "formula": "林冠投影面积/林地面积",
        "data_source": "无人机摄影测量",
        "threshold": "≥0.35",
        "desc": "反映林地冠层覆盖程度",
    },
    # === 功能指标 ===
    "wh": {
        "display_name": "水源涵养量",
        "symbol": "WH",
        "dimension": "function",
        "unit": "万m³/年",
        "formula": "降雨−径流−蒸散发",
        "data_source": "气象/水文监测",
        "threshold": "≥设计值80%",
        "desc": "与基准年比较",
    },
    "cs": {
        "display_name": "碳汇量",
        "symbol": "CS",
        "dimension": "function",
        "unit": "tCO₂/年",
        "formula": "植被生物量增量×含碳率",
        "data_source": "样地+遥感",
        "threshold": "逐年增加",
        "desc": "参与碳汇核算",
    },
    "sc": {
        "display_name": "土壤保持量",
        "symbol": "SC",
        "dimension": "function",
        "unit": "t/yr",
        "formula": "USLE/RUSLE模型",
        "data_source": "遥感+DEM+土壤",
        "threshold": "≥设计值75%",
        "desc": "减少侵蚀模数",
    },
    "hq": {
        "display_name": "生境质量指数",
        "symbol": "HQ",
        "dimension": "function",
        "unit": "",
        "formula": "InVEST Habitat Quality",
        "data_source": "土地利用+威胁源",
        "threshold": "≥0.55",
        "desc": "逐年改善",
    },
    "sf": {
        "display_name": "固土保肥效益",
        "symbol": "SF",
        "dimension": "function",
        "unit": "万吨/年",
        "formula": "土壤流失减少量×养分含量",
        "data_source": "土壤采样",
        "threshold": "≥2.0万吨/年",
        "desc": "与裸地对照",
    },
    "tc": {
        "display_name": "降温增湿效应",
        "symbol": "TC",
        "dimension": "function",
        "unit": "℃",
        "formula": "地表温度差/相对湿度差",
        "data_source": "热红外遥感",
        "threshold": "城区边缘≥1.5℃",
        "desc": "夏季午后",
    },
    # === 压力指标 ===
    "smc": {
        "display_name": "土壤含水量",
        "symbol": "SMC",
        "dimension": "pressure",
        "unit": "%",
        "formula": "体积含水率",
        "data_source": "土壤传感器",
        "threshold": "≥凋萎系数+5%",
        "desc": "根系层20cm",
    },
    "spi": {
        "display_name": "气象干旱指数",
        "symbol": "SPI/SPEI",
        "dimension": "pressure",
        "unit": "",
        "formula": "标准化降水/蒸散发指数",
        "data_source": "气象站",
        "threshold": "SPI≥−1.0",
        "desc": "月尺度",
    },
    "sai": {
        "display_name": "风沙活动强度",
        "symbol": "SAI",
        "dimension": "pressure",
        "unit": "",
        "formula": "起沙风日数/总风日数",
        "data_source": "气象站",
        "threshold": "≤30%",
        "desc": "冬春季",
    },
    "pa": {
        "display_name": "病虫害发生面积",
        "symbol": "PA",
        "dimension": "pressure",
        "unit": "%",
        "formula": "受害斑块面积/总面积",
        "data_source": "无人机多光谱",
        "threshold": "≤5%",
        "desc": "早发现早处置",
    },
    "fwi": {
        "display_name": "火险等级",
        "symbol": "FWI",
        "dimension": "pressure",
        "unit": "级",
        "formula": "综合火险指数",
        "data_source": "气象+植被可燃物",
        "threshold": "≤高火险",
        "desc": "分级响应",
    },
    # === 工程响应指标 ===
    "sr": {
        "display_name": "造林成活率",
        "symbol": "SR",
        "dimension": "response",
        "unit": "%",
        "formula": "成活株数/栽植株数×100%",
        "data_source": "样地调查",
        "threshold": "≥85%",
        "desc": "当年秋季",
    },
    "ir": {
        "display_name": "灌溉保证率",
        "symbol": "IR",
        "dimension": "response",
        "unit": "%",
        "formula": "实际灌溉次数/计划次数×100%",
        "data_source": "平台记录",
        "threshold": "≥90%",
        "desc": "关键生育期",
    },
    "frr": {
        "display_name": "沙障保存率",
        "symbol": "FRR",
        "dimension": "response",
        "unit": "%",
        "formula": "完好沙障长度/总长度×100%",
        "data_source": "无人机巡检",
        "threshold": "≥80%",
        "desc": "风季后",
    },
    "pr": {
        "display_name": "补植完成率",
        "symbol": "PR",
        "dimension": "response",
        "unit": "%",
        "formula": "实际补植株数/计划株数×100%",
        "data_source": "施工台账",
        "threshold": "≥95%",
        "desc": "按年度计划",
    },
    "pi": {
        "display_name": "管护巡检频次",
        "symbol": "PI",
        "dimension": "response",
        "unit": "%",
        "formula": "实际巡检次数/计划次数",
        "data_source": "移动APP",
        "threshold": "≥90%",
        "desc": "月度考核",
    },
    # === 稳定性指标 ===
    "cv": {
        "display_name": "NDVI变异系数",
        "symbol": "CV",
        "dimension": "stability",
        "unit": "",
        "formula": "标准差/均值",
        "data_source": "遥感时序",
        "threshold": "≤0.25",
        "desc": "年尺度",
    },
    "er": {
        "display_name": "生态系统恢复力",
        "symbol": "ER",
        "dimension": "stability",
        "unit": "",
        "formula": "扰动后恢复速度",
        "data_source": "时序模型",
        "threshold": "逐年增强",
        "desc": "需长期序列",
    },
    "sem": {
        "display_name": "土壤侵蚀模数",
        "symbol": "SEM",
        "dimension": "stability",
        "unit": "t/(km²·a)",
        "formula": "土壤流失量/(面积×时间)",
        "data_source": "监测+模型",
        "threshold": "≤容许值",
        "desc": "与基准年比较",
    },
    "sdr": {
        "display_name": "边坡位移变化率",
        "symbol": "SDR",
        "dimension": "stability",
        "unit": "mm/年",
        "formula": "InSAR形变速率",
        "data_source": "卫星InSAR",
        "threshold": "≤±10mm/年",
        "desc": "危险区重点监测",
    },
    "st": {
        "display_name": "植被群落演替趋势",
        "symbol": "ST",
        "dimension": "stability",
        "unit": "",
        "formula": "优势种/指示种变化",
        "data_source": "样地调查",
        "threshold": "正向演替",
        "desc": "3年以上序列",
    },
}


def _values(observations: List[Observation], name: str) -> List[float]:
    return [o.value for o in observations if o.value is not None and o.indicator_name == name]


def _text_counts(observations: List[Observation], name: str) -> Dict[str, int]:
    counts = {}
    for o in observations:
        if o.indicator_name == name and o.value_text:
            counts[o.value_text] = counts.get(o.value_text, 0) + 1
    return counts


def compute(name: str, observations: List[Observation], params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """基于观测或参数计算单个指标。返回字典包含 value, value_text, dimension。"""
    meta = INDICATOR_META.get(name)
    if not meta:
        return None

    vals = _values(observations, name)

    # 计算辅助：均值、变化率、CV
    def mean(vs):
        return statistics.mean(vs) if vs else None

    def change_rate(vs):
        return (vs[-1] - vs[0]) / max(vs[0], 1e-9) * 100 if len(vs) >= 2 else None

    def calc_cv(vs):
        m = mean(vs)
        return (statistics.stdev(vs) / m if len(vs) > 1 and m else None)

    result = {"dimension": meta["dimension"], "unit": meta["unit"]}

    # --- 结构指标 ---
    if name == "fvc":
        # 直接返回最近一次观测或参数中的 fvc 值
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"植被覆盖度 {result['value']}%" if result["value"] is not None else "缺少FVC观测"

    elif name == "ndvi":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 3) if v is not None else None
        result["value_text"] = f"NDVI={result['value']}" if result["value"] is not None else "缺少NDVI观测"

    elif name == "shannon":
        counts = _text_counts(observations, name)
        if not counts and params.get("species_counts"):
            counts = params["species_counts"]
        if not counts:
            result["value"] = None
            result["value_text"] = "无物种数据"
        else:
            total = sum(counts.values())
            sh = -sum((c / total) * math.log(c / total) for c in counts.values() if c > 0)
            result["value"] = round(sh, 3)
            result["value_text"] = f"Shannon 指数 {result['value']}"

    elif name == "fn":
        v = params.get("fn") or (vals[-1] if vals else None)
        result["value"] = round(v, 3) if v is not None else None
        result["value_text"] = f"景观破碎度 {result['value']}" if result["value"] is not None else "需提供斑块数/总面积"

    elif name == "bl":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"裸地比例 {result['value']}%" if result["value"] is not None else "缺少裸地比例"

    elif name == "cc":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 3) if v is not None else None
        result["value_text"] = f"郁闭度 {result['value']}" if result["value"] is not None else "缺少郁闭度观测"

    # --- 功能指标 ---
    elif name == "wh":
        p, r, et = params.get("precip", 500), params.get("runoff", 50), params.get("et", 400)
        wh = p - r - et
        result["value"] = round(wh, 2)
        result["value_text"] = f"水源涵养量 {wh:.2f} 万m³/年（P-R-ET 估算）"

    elif name == "cs":
        area = params.get("area_ha", 1000)
        rate = params.get("rate_tco2_ha_yr", 1.25)
        cs = area * rate
        result["value"] = round(cs, 2)
        result["value_text"] = f"碳汇量 {cs:.2f} tCO₂/年"

    elif name == "sc":
        r = params.get("R", 500)
        k = params.get("K", 0.3)
        ls = params.get("LS", 5)
        c = params.get("C", 0.5)
        p = params.get("P", 1.0)
        area = params.get("area_ha", 1000)
        a = r * k * ls * c * p * area / 10000.0  # t/yr
        result["value"] = round(a, 2)
        result["value_text"] = f"RUSLE 土壤保持量 {a:.2f} t/yr"

    elif name == "hq":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 3) if v is not None else None
        result["value_text"] = f"生境质量指数 {result['value']}" if result["value"] is not None else "缺少生境质量计算结果"

    elif name == "sf":
        v = params.get("value") or (vals[-1] if vals else None)
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"固土保肥效益 {result['value']} 万吨/年" if result["value"] is not None else "缺少固土保肥效益数据"

    elif name == "tc":
        v = params.get("value") or (vals[-1] if vals else None)
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"降温效应 {result['value']}℃" if result["value"] is not None else "缺少热红外遥感数据"

    # --- 压力指标 ---
    elif name == "smc":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"土壤含水量 {result['value']}%" if result["value"] is not None else "缺少土壤含水量"

    elif name == "spi":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"SPI={result['value']}" if result["value"] is not None else "缺少SPI/SPEI数据"

    elif name == "sai":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"风沙活动强度 {result['value']}%" if result["value"] is not None else "缺少风沙活动数据"

    elif name == "pa":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"病虫害发生面积 {result['value']}%" if result["value"] is not None else "缺少病虫害面积"

    elif name == "fwi":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"火险等级 {result['value']}" if result["value"] is not None else "缺少火险指数"

    # --- 工程响应指标 ---
    elif name in ("sr", "ir", "frr", "pr", "pi"):
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        cn = meta["display_name"]
        if result["value"] is not None:
            result["value_text"] = f"{cn} {result['value']}%"
        else:
            result["value_text"] = f"缺少{cn}数据"

    # --- 稳定性指标 ---
    elif name == "cv":
        if len(vals) < 2:
            result["value"] = None
            result["value_text"] = "需要至少两期 NDVI 序列"
        else:
            m = mean(vals)
            std = statistics.stdev(vals)
            cv = std / m if m else 0
            result["value"] = round(cv, 3)
            result["value_text"] = f"NDVI 变异系数 CV={result['value']}"

    elif name == "er":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 3) if v is not None else None
        result["value_text"] = f"生态系统恢复力 {result['value']}" if result["value"] is not None else "需要长期时序数据"

    elif name == "sem":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"土壤侵蚀模数 {result['value']} t/(km²·a)" if result["value"] is not None else "缺少土壤侵蚀模数"

    elif name == "sdr":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 2) if v is not None else None
        result["value_text"] = f"边坡位移变化率 {result['value']} mm/年" if result["value"] is not None else "缺少InSAR形变数据"

    elif name == "st":
        v = vals[-1] if vals else params.get("value")
        result["value"] = round(v, 3) if v is not None else None
        result["value_text"] = f"群落演替趋势指数 {result['value']}" if result["value"] is not None else "需要3年以上样地序列"

    else:
        return None

    return result


def evaluate_threshold(name: str, value: Optional[float]) -> Dict[str, Any]:
    """根据指标阈值给出预警级别和提示（简化版）。"""
    meta = INDICATOR_META.get(name, {})
    if value is None:
        return {"level": "unknown", "message": "无数据"}
    th = meta.get("threshold", "")
    desc = meta.get("desc", "")
    level = "normal"
    msg = "指标正常"

    # 通用判断：含≥的是越大越好，含≤的是越小越好
    if "≥" in th:
        try:
            target = float(th.replace("≥", "").replace("%", ""))
            if value < target:
                level = "yellow" if value >= target * 0.8 else "orange"
                msg = f"低于目标阈值 {th}"
        except Exception:
            pass
    elif "≤" in th:
        try:
            target = float(th.replace("≤", "").replace("%", "").replace("±", ""))
            if value > target:
                level = "yellow" if value <= target * 1.2 else "orange"
                msg = f"高于目标阈值 {th}"
        except Exception:
            pass

    return {"level": level, "message": msg, "threshold": th, "desc": desc}


def list_supported() -> List[Dict[str, Any]]:
    return [{"name": k, **v} for k, v in INDICATOR_META.items()]
