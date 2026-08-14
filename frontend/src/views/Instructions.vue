<template>
  <div class="instructions-modern">
    <!-- Hero -->
    <div class="ins-hero">
      <div class="ins-hero-glow"></div>
      <div class="ins-hero-icon">
        <svg width="48" height="48" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="16" r="14" stroke="url(#hGrad)" stroke-width="2" fill="none"/>
          <path d="M16 6 L16 16 L24 20" stroke="url(#hGrad)" stroke-width="2" stroke-linecap="round"/>
          <circle cx="16" cy="16" r="3" fill="url(#hGrad)"/>
          <defs><linearGradient id="hGrad" x1="0" y1="0" x2="32" y2="32"><stop offset="0%" stop-color="#10b981"/><stop offset="100%" stop-color="#0b8fa8"/></linearGradient></defs>
        </svg>
      </div>
      <h1 class="ins-hero-title">拉萨南北山生态监测评估系统</h1>
      <p class="ins-hero-sub">使用说明 · 生态评估方法学</p>
      <p class="ins-hero-ver">版本 v0.5.0 | 最后更新 2026-08-05</p>
      <p class="ins-hero-intro">本说明系统阐述「五维生态评估体系」——<strong>覆盖结构、功能、压力、工程响应、稳定性</strong>五大维度 22 项评估指标的指标含义、计算方法、计算参数、栅格/矢量数据生成流程与数据处理要求。全部指标方法以现行国家标准、行业标准为基准，融合遥感生态学前沿方法（CASA 光能利用率模型、RUSLE 土壤侵蚀模型、InVEST 水源涵养模型、时间序列稳定性分析等），适用于青藏高原半干旱高海拔造林工程的生态监测与成效评估。</p>
    </div>

    <!-- 目录 -->
    <div class="ins-toc">
      <div class="toc-header"><el-icon :size="16" color="#2470d8"><Collection /></el-icon><span>目录导航</span></div>
      <div class="toc-grid">
        <a v-for="item in toc" :key="item.id" :href="'#' + item.id" class="toc-item" @click.prevent="scrollTo(item.id)">
          <span class="toc-num">{{ item.num }}</span><span>{{ item.title }}</span>
        </a>
      </div>
    </div>

    <!-- 1 系统概述 -->
    <section id="m1" class="ins-section doc">
      <h2 class="chap">1 系统概述</h2>
      <h3 class="sec">1.1 工程背景</h3>
      <p>拉萨南北山绿化工程是西藏生态安全屏障建设的核心组成部分，规划范围以拉萨河为主线、东西绵延近 200 km，计划完成国土绿化面积 <strong>206.72 万亩</strong>。工程在高海拔（3 650–4 100 m）、半干旱、强辐射、昼夜温差大的极端立地条件下开展规模化人工造林，实行海拔分区施策：<strong>海拔 3 900 m 以下以营造乔木林为主，3 900–4 100 m 以营造灌木林为主，4 100 m 以上以封山育林育草（飞播造林）为主</strong>。截至 2026 年累计完成营造林 93 万余亩、栽植苗木 1.25 亿株，总体成活率稳定在 85% 以上。</p>
      <h3 class="sec">1.2 平台定位</h3>
      <p>平台面向工程建设指挥部、林草主管部门、施工与管护单位，提供「天空地一体化」监测能力：</p>
      <ul>
        <li><strong>天</strong>：Sentinel-2（10 m）/ 高分一号、六号（2–16 m）/ Landsat（30 m）多源卫星遥感，提供 NDVI、FVC、NPP 等栅格产品；</li>
        <li><strong>空</strong>：无人机航测（厘米级正射影像、多光谱）与运苗调度回传；</li>
        <li><strong>地</strong>：固定样地每木检尺、土壤剖面采样、自动气象/土壤/水文站点与巡护终端。</li>
      </ul>
      <p>核心功能模块：工作台总览、生态一张图（GIS）、指标计算、巡检照片、野外科考、偏离预警、评估报告、设备清单与本使用说明。</p>
      <h3 class="sec">1.3 评估业务闭环</h3>
      <p>数据获取 → 预处理与质检 → 指标计算（第 4–8 章）→ 五维综合评估（第 9 章）→ 偏离预警（阈值比对）→ 报告生成与归档 → 反馈造林/管护作业设计。评估成果同时服务于<strong>造林任务落地上图、林长制考核与生态价值核算</strong>。</p>
    </section>

    <!-- 2 评估框架与标准依据 -->
    <section id="m2" class="ins-section doc">
      <h2 class="chap">2 评估框架与标准依据</h2>
      <h3 class="sec">2.1 五维指标体系设计逻辑</h3>
      <p>指标体系采用「状态—功能—压力—响应—持续性」的 <strong>DPSIR（驱动力—压力—状态—影响—响应）</strong>扩展框架，并对接《青藏高原生态屏障区生态保护和修复重大工程建设规划（2021—2035 年）》对工程成效监测的要求：</p>
      <table class="tbl">
        <tr><th style="width:110px">维度</th><th>评估目标</th><th>指标数</th><th>主要标准依据</th></tr>
        <tr><td><strong>覆盖结构</strong></td><td>绿化「量」与空间格局：植被盖度、林草面积、群落结构与景观连通性</td><td>5</td><td>HJ 1166/1171/1172-2021、GB/T 26424</td></tr>
        <tr><td><strong>功能</strong></td><td>生态系统服务「质」：水源涵养、土壤保持、固碳释氧、生物多样性</td><td>5</td><td>GB/T 38582-2020、HJ 1173-2021、HJ 623-2011</td></tr>
        <tr><td><strong>压力</strong></td><td>内外胁迫：土壤侵蚀、干旱、人为干扰、生物灾害</td><td>4</td><td>SL 190-2007、HJ 1174-2021、HJ 192-2015、GB/T 20481</td></tr>
        <tr><td><strong>工程响应</strong></td><td>工程建设与管护成效：成活率、保存率、苗木质量、灌溉管护</td><td>4</td><td>GB/T 15776-2023、GB 6000-1999、LY/T 1607</td></tr>
        <tr><td><strong>稳定性</strong></td><td>生态系统持续性与抗干扰能力：年际稳定性、恢复力、林分与土壤健康</td><td>4</td><td>HJ 1167-2021、HJ 1172-2021、NY/T 1121 系列</td></tr>
      </table>
      <h3 class="sec">2.2 规范性引用文件</h3>
      <ul>
        <li><span class="std-tag">GB/T 15776-2023</span>《造林技术规程》——造林成活率、株数保存率、郁闭度/盖度成效评价阈值；</li>
        <li><span class="std-tag">GB/T 38582-2020</span>《森林生态系统服务功能评估规范》——涵养水源、保育土壤、固碳释氧等 9 项功能的分布式测算方法与公式参数；</li>
        <li><span class="std-tag">HJ 1166～1176-2021</span>《全国生态状况调查评估技术规范》系列——遥感解译与野外核查、森林/草地野外观测、格局/质量/服务功能/生态问题评估、数据质量控制与集成；</li>
        <li><span class="std-tag">HJ 192-2015</span>《生态环境状况评价技术规范》——EI 指数五分指数结构（生物丰度、植被覆盖、水网密度、土地胁迫、污染负荷）与分级；</li>
        <li><span class="std-tag">SL 190-2007</span>《土壤侵蚀分类分级标准》——水力/风力/冻融侵蚀强度六级划分与容许土壤流失量；</li>
        <li><span class="std-tag">HJ 623-2011</span>《区域生物多样性评价标准》；<span class="std-tag">GB/T 26424-2010</span>《森林资源规划设计调查技术规程》；<span class="std-tag">GB 6000-1999</span>《主要造林树种苗木质量分级》；<span class="std-tag">NY/T 1121 系列</span>《土壤检测》；<span class="std-tag">GB/T 20481-2017</span>《气象干旱等级》；<span class="std-tag">TD/T 1055</span>《第三次全国国土调查技术规程》。</li>
      </ul>
      <div class="notebar"><strong>高原适用性说明：</strong>凡国家标准按气候区分级设定阈值的（如 GB/T 15776-2023），本区一律执行<strong>「青藏高寒区 / 干旱半干旱区」</strong>档：造林成活率 ≥ 70% 为合格（普通气候区为 85%）、3–5 年株数保存率 ≥ 65% 为有成林成效、灌木林盖度 ≥ 40% 为成效合格。工程内部管理目标（成活率 ≥ 85%）高于国标底线，评估时两档并列展示。</div>
    </section>

    <!-- 3 数据基础与预处理要求 -->
    <section id="m3" class="ins-section doc">
      <h2 class="chap">3 数据基础与预处理要求</h2>
      <h3 class="sec">3.1 空间基准与数据组织</h3>
      <ul>
        <li><strong>大地基准</strong>：CGCS2000 国家大地坐标系；高程采用 1985 国家高程基准；投影采用阿尔伯斯等积圆锥投影（面积统计类）或 UTM 47N（工程制图类），同一期成果基准必须统一。</li>
        <li><strong>评价单元</strong>：三级组织——工程全域 → 片区/流域 → 造林小班（最小评价与落地上图单元），小班边界与作业设计一致并赋唯一编码（区县代码 + 年度 + 流水号）。</li>
        <li><strong>数据格式</strong>：栅格 GeoTIFF（LZW 压缩、含金字塔与 NoData 定义）；矢量 GeoPackage / Shapefile（UTF-8 属性表）；属性成果同步入库，并附元数据（生产时间、数据源、处理流程、精度指标，参照 HJ 1176-2021 第 6 章数据集成要求）。</li>
      </ul>
      <h3 class="sec">3.2 遥感数据与预处理（HJ 1166-2021 第 6 章、HJ 1176-2021）</h3>
      <table class="tbl">
        <tr><th>环节</th><th>技术要求</th><th>验收指标</th></tr>
        <tr><td>数据获取</td><td>生长季（7–9 月）云量 &lt; 10% 影像为主，植被参数反演时相窗口 ±15 d 内拼接；非生长季影像用于裸土/雪被背景分析</td><td>时相一致性记录完整</td></tr>
        <tr><td>辐射定标</td><td>按传感器定标系数将 DN 值转为表观辐亮度/反射率</td><td>系数版本可追溯</td></tr>
        <tr><td>大气校正</td><td>Sentinel-2 用 Sen2Cor；高分/Landsat 用 FLAASH 或 6S 模型；高原气溶胶模型取「中纬度夏季/大陆型」，DEM 辅助地形辐射校正</td><td>地表反射率与实测光谱相对误差 ≤ 10%</td></tr>
        <tr><td>几何/正射校正</td><td>有理函数模型 + 控制点 + DEM（ALOS PALSAR 12.5 m 或无人机 DSM）</td><td>配准误差 ≤ 0.5 像元（平地）/ ≤ 1 像元（山地）</td></tr>
        <tr><td>云与阴影掩膜</td><td>QA 波段 + Fmask 算法；云阴影、积雪、水体一并掩除</td><td>掩膜精度抽检 ≥ 95%</td></tr>
        <tr><td>镶嵌与裁切</td><td>色调均衡后按评价单元裁切，保留 1 个像元缓冲</td><td>接边无明显色差</td></tr>
      </table>
      <h3 class="sec">3.3 地面调查体系（HJ 1167-2021、HJ 1168-2021、GB/T 26424-2010）</h3>
      <ul>
        <li><strong>固定样地</strong>：按海拔带（&lt;3 900 m / 3 900–4 100 m / &gt;4 100 m）与造林年度分层布设，乔木样地 30 m × 30 m（角点 RTK 定位，误差 ≤ 0.1 m），内嵌 4 个 5 m × 5 m 灌木样方与 4 个 1 m × 1 m 草本样方；</li>
        <li><strong>每木检尺</strong>：胸径 ≥ 2 cm（新造林地 ≥ 1 cm）逐株记录树种、胸径、树高、冠幅、成活率状态；</li>
        <li><strong>土壤剖面</strong>：0–20 / 20–40 / 40–100 cm 三层取混合样，环刀法测容重，重铬酸钾氧化-外加热法测有机质（NY/T 1121.6）；</li>
        <li><strong>遥感解译核查</strong>：野外核查点不少于图斑总数 2%，解译总体精度 ≥ 90%（HJ 1166-2021 附录 C 精度验证表）。</li>
      </ul>
      <h3 class="sec">3.4 数据更新频率</h3>
      <table class="tbl">
        <tr><th>数据类</th><th>更新频率</th><th>说明</th></tr>
        <tr><td>NDVI/FVC 栅格</td><td>生长季每 16 d，年度合成</td><td>年度采用生长季最大值合成（MVC）</td></tr>
        <tr><td>NPP / 水源涵养 / 土壤保持</td><td>每年 1 期</td><td>气象数据全年逐日驱动</td></tr>
        <tr><td>小班矢量（成活率/保存率）</td><td>春、秋两季核查</td><td>对接造林实绩核查与补植台账</td></tr>
        <tr><td>样地/土壤</td><td>每年 1 次（固定周期）</td><td>与遥感时相窗口匹配</td></tr>
        <tr><td>预警指标</td><td>影像/站点数据到达即触发</td><td>自动比对第 9.4 节阈值</td></tr>
      </table>
    </section>

    <!-- 4 维度一：覆盖结构 -->
    <section id="m4" class="ins-section doc">
      <h2 class="chap">4 维度一：覆盖结构（Coverage &amp; Structure，5 项）</h2>
      <p>覆盖结构维度回答「绿了多少、绿得怎样」——从盖度、面积、群落结构到景观格局四个尺度刻画工程增绿的数量与质量。指标 1–3 直接对应 HJ 1172-2021《生态系统质量评估》遥感关键生态参数，指标 4 对接 HJ 1167-2021 野外观测，指标 5 对接 HJ 1171-2021 生态系统格局评估。</p>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">1</div><div class="ind-title"><div class="ind-name">植被覆盖度（FVC）</div><div class="ind-en">Fractional Vegetation Cover</div></div>
          <div class="ind-meta"><span class="pill ok">栅格产品</span><span class="pill info">16 d / 年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：植被（含乔、灌、草）在地面的垂直投影面积占统计区总面积的百分比，是衡量地表绿化程度最核心的指标，也是 HJ 192-2015 植被覆盖指数与 HJ 1172-2021 质量评估的基础参数。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 1172-2021 附录 B</span>遥感关键生态参数计算方法；<span class="std-tag">HJ 192-2015</span>植被覆盖指数。</div>
        <div class="ind-sec"><b>▍计算方法（像元二分模型）</b>：</div>
        <div class="formula">NDVI = (ρ<sub>NIR</sub> − ρ<sub>Red</sub>) / (ρ<sub>NIR</sub> + ρ<sub>Red</sub>)<span class="fid">式 4-1</span></div>
        <div class="formula">FVC = (NDVI − NDVI<sub>soil</sub>) / (NDVI<sub>veg</sub> − NDVI<sub>soil</sub>) × 100%<span class="fid">式 4-2</span></div>
        <p class="param-note">参数：ρ<sub>NIR</sub>、ρ<sub>Red</sub> 为大气校正后近红外、红光波段地表反射率（Sentinel-2 取 B8/B4，GF-1 取 B4/B3）；NDVI<sub>soil</sub>、NDVI<sub>veg</sub> 分别为纯裸土与纯植被像元 NDVI，取评价区 NDVI 频率分布的 <strong>5% 与 95% 累积置信度截断值</strong>；FVC 超出 [0, 1] 的像元分别归一为 0 与 1。高原裸土区 NDVI<sub>soil</sub> 典型值 0.05–0.12，郁闭灌丛/林分 NDVI<sub>veg</sub> 典型值 0.78–0.86，须每期影像独立求解。</p>
        <div class="ind-sec"><b>▍栅格生成流程</b>：Sentinel-2 L1C → Sen2Cor 大气校正得 L2A 地表反射率 → 云/雪/阴影掩膜 → 波段运算得 NDVI 栅格（10 m）→ 像元二分模型得 FVC 栅格 → 生长季 MVC 最大值合成 → 按小班分区统计（zonal statistics）均值/分级面积。GF-1 2 m 融合产品用于重点小班的尺度验证。</div>
        <div class="ind-sec"><b>▍评价基准</b>：以 2021 年工程启动前同期 FVC 为本底；年度增量 ΔFVC ≥ 1.5 个百分点为「显著增绿」。青藏高原河谷区参考阈值：FVC &lt; 30% 低覆盖、30–50% 中低、50–70% 中、&gt; 70% 高覆盖。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">2</div><div class="ind-title"><div class="ind-name">林草覆盖率</div><div class="ind-en">Forest &amp; Grass Coverage Ratio</div></div>
          <div class="ind-meta"><span class="pill ok">矢量统计</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：（林地面积 + 草地面积）/ 评价区土地总面积 × 100%。对接国土「三调」地类口径，是政府考核与规划目标（206.72 万亩）对比的主指标。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">TD/T 1055</span>国土调查地类分类；<span class="std-tag">HJ 1166-2021 附录 A</span>全国生态系统分类体系（森林/灌丛/草地 3 个一级类、14 个二级类）。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">C<sub>fg</sub> = (A<sub>forest</sub> + A<sub>grass</sub>) / A<sub>total</sub> × 100%<span class="fid">式 4-3</span></div>
        <p class="param-note">参数：A<sub>forest</sub> 含乔木林（郁闭度 ≥ 0.2）、灌木林（盖度 ≥ 40%）与新造林地（GB/T 26424-2010 地类划分标准）；A<sub>grass</sub> 为草本盖度 ≥ 5% 的草地；面积一律用阿尔伯斯等积投影计算。</p>
        <div class="ind-sec"><b>▍矢量生成流程</b>：多光谱影像（GF-6 PMS 2 m + Sentinel-2）→ 面向对象分类（多尺度分割 + 随机森林，特征：光谱、NDVI/NDWI、纹理、坡度）→ 人机交互修正（HJ 1166-2021 §6.4）→ 生态系统类型矢量图 → 与造林小班、三调图斑叠加取并集 → 野外核查（抽样 ≥ 2%，Kappa ≥ 0.85）→ 面积统计表。</div>
        <div class="ind-sec"><b>▍数据处理要求</b>：分类样本按 HJ 1166-2021 附录 B 解译目标特征表采集，每类样本 ≥ 100 个；阴影区与冰雪覆盖区单独归类不参与林草判定。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">3</div><div class="ind-title"><div class="ind-name">乔木林郁闭度 / 灌木林盖度</div><div class="ind-en">Canopy Density / Shrub Coverage</div></div>
          <div class="ind-meta"><span class="pill ok">样地+栅格</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：郁闭度为乔木树冠垂直投影面积与林地面积之比；灌木林以盖度表征。二者是 GB/T 15776-2023 判定造林成效合格小班的法定指标（郁闭度 ≥ 0.2 或灌木盖度 ≥ 40%）。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB/T 15776-2023 §16.3</span>；<span class="std-tag">GB/T 26424-2010</span>；<span class="std-tag">HJ 1167-2021 §9</span>。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">P<sub>c</sub> = A<sub>crown</sub> / A<sub>plot</sub> × 100% （郁闭度，保留两位小数）<span class="fid">式 4-4</span></div>
        <p class="param-note">样地法：30 m × 30 m 样地内对角线等距设 10 个观测点，抬头望法/树冠投影法逐点判定，取均值；鱼眼镜头半球影像经 GLA 反演叶面积指数 LAI 后换算。遥感反演：以样地郁闭度为真值，建立 NDVI/RVI/纹理特征与郁闭度的随机森林回归模型（R² ≥ 0.75），外推至小班尺度。</p>
        <div class="ind-sec"><b>▍评价基准</b>：郁闭度 ≥ 0.2 → 有林地（成林）；0.1–0.19 → 疏林地；灌木盖度 ≥ 40% → 灌木林。海拔 3 900 m 以下乔木小班 2030 年目标郁闭度 ≥ 0.3。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">4</div><div class="ind-title"><div class="ind-name">群落垂直结构完整度</div><div class="ind-en">Vertical Structure Integrity</div></div>
          <div class="ind-meta"><span class="pill info">样地观测</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：乔—灌—草层片的完整程度，反映群落近自然化水平。单一乔木层结构在高原干旱区抗逆性弱，「乔灌草」复合结构是南北山作业设计的基本要求（乡土灌木如绢毛蔷薇、江孜沙棘占比 ≥ 30%）。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 1167-2021 §8</span>野外观测指标体系；<span class="std-tag">GB/T 15776-2023</span>混交林营造要求（单一树种比例 ≤ 80%）。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">VSI = (L<sub>tree</sub> + L<sub>shrub</sub> + L<sub>herb</sub>) / 3 × q<sub>mix</sub><span class="fid">式 4-5</span></div>
        <p class="param-note">L<sub>tree</sub>/L<sub>shrub</sub>/L<sub>herb</sub> 为层片存在性赋值：覆盖度 ≥ 5% 记 1，0.5–5% 记 0.5，&lt; 0.5% 记 0；q<sub>mix</sub> 为混交系数 = 1 − 优势树种株数占比（混交林 0.3–0.7，纯林 0）。VSI ∈ [0, 1]，≥ 0.6 为结构完整。</p>
        <div class="ind-sec"><b>▍数据生成</b>：固定样地分层调查（乔木层每木检尺、5×5 m 灌木样方、1×1 m 草本样方），结果关联小班矢量属性表，不参与栅格生产，作为结构维度评估的样地证据链。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">5</div><div class="ind-title"><div class="ind-name">景观格局指数（斑块密度 PD / 聚集度 AI）</div><div class="ind-en">Landscape Pattern Metrics</div></div>
          <div class="ind-meta"><span class="pill ok">矢量/栅格</span><span class="pill info">2–3 年</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：刻画造林斑块的空间配置合理性——斑块破碎化程度与连通性直接影响物种迁移与生态系统稳定，是 HJ 1171-2021 格局评估的核心内容，也是优化后续造林空间布局的依据。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 1171-2021</span>生态系统格局评估；前沿方法：FRAGSTATS 4 景观生态学指数体系。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">PD = n<sub>i</sub> / A × 10 000（个/hm²）；AI = [ g<sub>ii</sub> / max g<sub>ii</sub> ] × 100<span class="fid">式 4-6</span></div>
        <p class="param-note">n<sub>i</sub> 为 i 类斑块数，A 为总面积（m²）；g<sub>ii</sub> 为同类相邻像元数，max g<sub>ii</sub> 为理论最大邻接数。辅以平均斑块面积 MPS、边缘密度 ED、连通度 CONNECT（阈值距离 200 m，对应高原鸟类/小型哺乳动物扩散尺度）。</p>
        <div class="ind-sec"><b>▍数据生成流程</b>：生态系统类型矢量（指标 2 产品）转 10 m 栅格 → FRAGSTATS 批量计算 → 片区尺度指数表 → 与 2021 本底对比。PD 下降 + AI 上升 = 绿化由「点状分散」转向「集中连片」，格局优化。</div>
      </div>
    </section>

    <!-- 5 维度二：功能 -->
    <section id="m5" class="ins-section doc">
      <h2 class="chap">5 维度二：功能（Ecosystem Functions，5 项）</h2>
      <p>功能维度量化绿化的生态服务产出。物质量计算以 <span class="std-tag">GB/T 38582-2020</span> 分布式测算方法为法定基准（一级单元行政区划、二级单元优势树种组、三级单元起源、四级单元林龄组），空间化表达以 HJ 1173-2021《生态系统服务功能评估》为技术依据，模型选型采用当前生态水文学与遥感生态学主流方法（InVEST、RUSLE、CASA）。</p>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">6</div><div class="ind-title"><div class="ind-name">水源涵养量</div><div class="ind-en">Water Conservation</div></div>
          <div class="ind-meta"><span class="pill ok">栅格产品</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：生态系统（林冠层、枯落物层、土壤层）对降水的截留、蓄存与净化能力，单位 m³/a。工程预期目标：建成后年均新增储水约 4 980 万吨。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB/T 38582-2020</span>涵养水源（调节水量、净化水质）；<span class="std-tag">HJ 1173-2021</span>水源涵养功能评估。</div>
        <div class="ind-sec"><b>▍计算方法（水量平衡法，国标公式）</b>：</div>
        <div class="formula">Q<sub>w</sub> = Σ<sub>i</sub> 10 × A<sub>i</sub> × (P<sub>i</sub> − R<sub>i</sub> − ET<sub>i</sub>)<span class="fid">式 5-1</span></div>
        <p class="param-note">参数：Q<sub>w</sub> 为涵养水源量（m³/a）；A<sub>i</sub> 为第 i 类生态系统面积（hm²）；P 为年降水量（mm，自动气象站 + 国家站插值，TRMM/ERA5 校正）；R 为年地表径流量（mm），R = α × P，径流系数 α 按地类查 GB/T 38582-2020 附录：林地 0.10–0.20、灌丛 0.15–0.25、草地 0.20–0.35、裸地 0.45–0.60（半干旱区取中值并做坡度修正）；ET 为年蒸散量（mm），采用 FAO Penman-Monteith 参考蒸散 × 作物系数 Kc（林地 0.9–1.1、灌丛 0.7–0.85、草地 0.6–0.75）。系数 10 为单位换算（mm·hm² → m³）。</p>
        <div class="ind-sec"><b>▍栅格生成流程</b>：气象站点观测 → ANUSPLIN 薄盘样条插值（含高程协变量）得 P 栅格（1 km）→ MOD16/ERA5 蒸散产品经站点标定 → 地类矢量叠加径流系数 → 栅格代数运算得 Q<sub>w</sub> 空间分布 → 与 2021 本底差值即为工程新增涵养量。前沿校验：InVEST Seasonal Water Yield 模型交叉验证，两模型结果偏差 &gt; 20% 时须复核参数。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">7</div><div class="ind-title"><div class="ind-name">土壤保持量</div><div class="ind-en">Soil Conservation</div></div>
          <div class="ind-meta"><span class="pill ok">栅格产品</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：生态系统固持土壤、减少水力侵蚀的量（t/a），= 潜在土壤侵蚀量 − 实际土壤侵蚀量。拉萨河谷风蚀、水蚀、冻融侵蚀复合，绿化固土价值居各项生态服务前列。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB/T 38582-2020</span>保育土壤（固土、保肥）；<span class="std-tag">HJ 1173-2021</span>；强度分级执行 <span class="std-tag">SL 190-2007</span>。</div>
        <div class="ind-sec"><b>▍计算方法（RUSLE 修正通用土壤流失方程）</b>：</div>
        <div class="formula">A = R × K × LS × C × P<span class="fid">式 5-2</span></div>
        <div class="formula">S<sub>c</sub> = A<sub>potential</sub> − A<sub>actual</sub> = R·K·LS × (1 − C·P)<span class="fid">式 5-3</span></div>
        <p class="param-note">参数：A 为土壤侵蚀模数 t/(km²·a)；<strong>R</strong> 降雨侵蚀力因子（MJ·mm/(hm²·h·a)），用半月雨量公式或日降雨模型（章文波算法），拉萨河谷 R 典型值 800–1 500；<strong>K</strong> 土壤可蚀性因子（t·hm²·h/(hm²·MJ·mm)），EPIC 公式由砂粒/粉粒/黏粒/有机碳含量计算，高原山地草甸土 K 典型值 0.015–0.03；<strong>LS</strong> 坡度坡长因子，由 12.5 m DEM 计算（McCool 坡度公式 + Desmet &amp; Govers 坡长算法）；<strong>C</strong> 植被覆盖与生物措施因子，按 FVC 分段赋值（FVC&lt;10% 取 0.6，每增 20% C 值递减，FVC&gt;80% 取 0.004–0.01）；<strong>P</strong> 工程措施因子，水平阶/鱼鳞坑整地 0.3–0.5，无措施裸地 1.0。</p>
        <div class="ind-sec"><b>▍评价基准（SL 190-2007 表 4.1.2，北方土石山区档）</b>：微度 &lt; 200、轻度 200–2 500、中度 2 500–5 000、强烈 5 000–8 000、极强烈 8 000–15 000、剧烈 &gt; 15 000 t/(km²·a)。容许土壤流失量 200 t/(km²·a)。工程目标：造林 5 年后小班侵蚀模数降至轻度以下。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">8</div><div class="ind-title"><div class="ind-name">植被净初级生产力（NPP）</div><div class="ind-en">Net Primary Productivity</div></div>
          <div class="ind-meta"><span class="pill ok">栅格产品</span><span class="pill info">月度/年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：单位面积植被净固定的有机碳量（gC/(m²·a)），是生态系统质量与碳汇能力的综合表征，HJ 1172-2021 生态系统质量评估核心指标。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 1172-2021 附录 B</span>；前沿模型：<strong>CASA（Carnegie-Ames-Stanford Approach）光能利用率模型</strong>（Potter et al., 1993；朱文泉等中国区域参数化）。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">NPP(x,t) = APAR(x,t) × ε(x,t)<span class="fid">式 5-4</span></div>
        <div class="formula">APAR = SOL(x,t) × FPAR(x,t) × 0.5； ε = T<sub>ε1</sub> × T<sub>ε2</sub> × W<sub>ε</sub> × ε<sub>max</sub><span class="fid">式 5-5</span></div>
        <p class="param-note">参数：SOL 为月太阳总辐射（MJ/m²，气象站 + 山地辐射模型按坡度坡向校正，拉萨年总量约 7 500–8 400 MJ/m²）；FPAR 由 NDVI 线性关系估算，并与 SR 比值法取均值；常数 0.5 为光合有效辐射占比；T<sub>ε1</sub>、T<sub>ε2</sub> 为温度胁迫系数（最适温度取生长季月均温 12–16 ℃，高温上限 38 ℃）；W<sub>ε</sub> 水分胁迫系数 = 0.5 + 0.5×E/ET<sub>0</sub>（E 实际蒸散，ET<sub>0</sub> 潜在蒸散）；<strong>ε<sub>max</sub> 最大光能利用率</strong>（gC/MJ）：乔木 0.389–0.693、灌木 0.429、草地 0.542（朱文泉参数，高寒灌草丛按 0.35–0.45 校正）。</p>
        <div class="ind-sec"><b>▍栅格生成流程</b>：逐月 NDVI（10–30 m）+ 逐月气象栅格（1 km，降尺度）→ CASA 逐月 NPP → 年度累加 → 小班统计。产品经 MOD17（1 km）区域一致性校验（相对偏差 ≤ 15%）。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">9</div><div class="ind-title"><div class="ind-name">碳储量与固碳释氧量</div><div class="ind-en">Carbon Storage &amp; Sequestration</div></div>
          <div class="ind-meta"><span class="pill ok">栅格+样地</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：生态系统现存碳库（植被 + 土壤，t/hm²）与年固碳速率（t/(hm²·a)），服务「双碳」目标。工程预期：建成后年固碳约 22.91 万吨、释氧约 19.3 万吨。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB/T 38582-2020</span>固碳释氧；前沿：IPCC 生物量扩展因子法 + 异速生长方程。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">C<sub>veg</sub> = Σ BEF × V<sub>i</sub> × WD × (1 + R<sub>sd</sub>) × CF<span class="fid">式 5-6</span></div>
        <div class="formula">G<sub>CO2</sub> = 1.63 × R<sub>ab</sub> × B<sub>n</sub>；G<sub>O2</sub> = 1.19 × R<sub>ab</sub> × B<sub>n</sub><span class="fid">式 5-7</span></div>
        <p class="param-note">参数：V<sub>i</sub> 为林分蓄积量（m³/hm²，由每木检尺立木材积表求算，新造林地按异速生长方程 B = a(D²H)<sup>b</sup> 单木累加）；BEF 生物量扩展因子（油松 1.59、樟子松 2.51、杨树 1.45、沙棘/灌木按 0.95–1.2）；WD 木材密度（g/cm³，油松 0.36–0.46）；R<sub>sd</sub> 地下/地上生物量比（针叶 0.20–0.25、阔叶 0.23–0.26、灌木 0.4–0.6）；CF 含碳率 0.5（GB/T 38582-2020 推荐）；B<sub>n</sub> 为年净生产力干物质量（t/(hm²·a)，由 NPP 折算或生长量实测）。土壤碳库：SOC<sub>stock</sub> = SOC% × BD × Depth × (1−砾石比) × 100（t/hm²，0–100 cm 分层累加）。</p>
        <div class="ind-sec"><b>▍数据处理要求</b>：样地生物量实测值标定遥感反演模型（AGB 与 NDVI/树高纹理的幂函数回归，R² ≥ 0.7）；土壤有机质数据由 NY/T 1121.6 方法测定；不确定度以蒙特卡洛法评估，报告 ±95% 置信区间。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">10</div><div class="ind-title"><div class="ind-name">生物多样性指数（Shannon-Wiener）</div><div class="ind-en">Biodiversity Index</div></div>
          <div class="ind-meta"><span class="pill info">样地观测</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：植物群落物种丰富度与均匀度的综合度量；绿化后野生动物回归（鸟类、小型兽类）作为辅助指示。反映工程是否实现「增绿」向「增生态」转变。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 623-2011</span>《区域生物多样性评价标准》；<span class="std-tag">HJ 1167-2021</span>植物多样性观测。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">H′ = −Σ<sub>i=1</sub><sup>S</sup> p<sub>i</sub> ln p<sub>i</sub>， p<sub>i</sub> = n<sub>i</sub> / N<span class="fid">式 5-8</span></div>
        <p class="param-note">参数：S 为物种数（丰富度）；n<sub>i</sub> 为第 i 种个体数（草本/灌木按株丛数，乔木按株数）；N 为全部个体数。配套计算 Pielou 均匀度 J = H′/lnS 与 Simpson 优势度 D = 1 − Σp<sub>i</sub>²。HJ 623-2011 归一化生物多样性指数 BI = 0.35×野生维管束植物丰富度归一值 + 0.25×野生动物丰富度归一值 + 0.2×生态系统类型多样性 + 0.2×（1 − 外来物种入侵度），权重可按区域调整。</p>
        <div class="ind-sec"><b>▍评价基准</b>：以邻近原生灌草丛样地为参照（Reference）；H′ 达到参照值 80% 以上为「接近自然」。造林小班乡土树种占比 ≥ 70%、外来入侵物种为零为合格。</div>
      </div>
    </section>

    <!-- 6 维度三：压力 -->
    <section id="m6" class="ins-section doc">
      <h2 class="chap">6 维度三：压力（Pressures，4 项）</h2>
      <p>压力维度识别制约绿化成效的负向因子，对应 HJ 1174-2021《生态问题评估》与 HJ 192-2015 土地胁迫/污染负荷的评估逻辑。压力指标为逆向指标——数值越低越好，综合评估时作反向标准化。</p>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">11</div><div class="ind-title"><div class="ind-name">土壤侵蚀强度</div><div class="ind-en">Soil Erosion Intensity</div></div>
          <div class="ind-meta"><span class="pill ok">栅格产品</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：评价区实际土壤侵蚀模数与中度及以上侵蚀面积占比，直接反映造林地水土流失风险，与指标 7（土壤保持）互为表里——此处评估「压力现状」，指标 7 评估「功能产出」。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">SL 190-2007</span>分级标准；<span class="std-tag">HJ 1174-2021</span>水土流失评估；<span class="std-tag">HJ 192-2015</span>土地胁迫指数。</div>
        <div class="ind-sec"><b>▍计算方法</b>：RUSLE 实际侵蚀量（式 5-2，C·P 取现状值）+ 强度面积统计：</div>
        <div class="formula">E<sub>ratio</sub> = (A<sub>中度</sub> + A<sub>强烈</sub> + A<sub>极强烈</sub> + A<sub>剧烈</sub>) / A<sub>total</sub> × 100%<span class="fid">式 6-1</span></div>
        <p class="param-note">拉萨河谷属水力侵蚀为主的北方土石山区参照档（容许流失量 200 t/(km²·a)）；海拔 4 000 m 以上冻融侵蚀区按 SL 190-2007 第 6 章冻融侵蚀分级（冻融侵蚀指数 = 年较差 × 坡度 × 植被盖度修正）；河谷沙地叠加风力侵蚀判定（日均风速 ≥ 5 m/s 全年累计 ≥ 30 d 且降水 &lt; 300 mm）。</p>
        <div class="ind-sec"><b>▍栅格生成流程</b>：DEM（12.5 m）→ LS 因子栅格；气象站日雨量 → R 栅格；土壤图 + 剖面实测 → K 栅格；FVC（指标 1）→ C 栅格；工程措施台账 → P 栅格 → 栅格连乘 → SL 190-2007 六级重分类 → 侵蚀强度分布图。</div>
        <div class="ind-sec"><b>▍预警阈值</b>：单小班中度及以上侵蚀面积占比 &gt; 20%，或侵蚀模数年增幅 &gt; 15% 触发中优先级预警。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">12</div><div class="ind-title"><div class="ind-name">干旱胁迫指数（VCI / SPEI）</div><div class="ind-en">Drought Stress Index</div></div>
          <div class="ind-meta"><span class="pill ok">栅格产品</span><span class="pill info">16 d</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：量化水分亏缺对植被的胁迫程度。南北山造林成活的第一限制因子是水分——3–5 月春旱与 6 月初夏旱是苗木死亡高峰期，该指标直接驱动灌溉调度。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB/T 20481-2017</span>《气象干旱等级》（SPEI 分级）；前沿：植被状态指数 VCI（Kogan, 1990）与温度植被干旱指数 TVDI。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">VCI = (NDVI − NDVI<sub>min</sub>) / (NDVI<sub>max</sub> − NDVI<sub>min</sub>) × 100%<span class="fid">式 6-2</span></div>
        <div class="formula">SPEI = (D − μ) / σ， D = P − PET（3/6 个月尺度）<span class="fid">式 6-3</span></div>
        <p class="param-note">VCI 中 NDVI<sub>min</sub>/NDVI<sub>max</sub> 为该像元多年（≥ 10 年或工程以来）同期极值；VCI &lt; 35% 为干旱胁迫。SPEI 中 D 为降水与潜在蒸散差值序列，经 log-logistic 三参数分布拟合标准化；GB/T 20481-2017 分级：−0.5 &lt; SPEI 无旱，−1.0～−0.5 轻旱，−1.5～−1.0 中旱，−2.0～−1.5 重旱，≤ −2.0 特旱。TVDI 作为遥感校验，干边方程由地表温度-NDVI 特征空间拟合。</p>
        <div class="ind-sec"><b>▍栅格生成流程</b>：逐旬 NDVI → VCI 栅格；气象站逐日降水/气温 → Thornthwaite 或 PM 法 PET → SPEI 站点序列 → 克里金插值栅格化 → 与 VCI 交叉验证（一致性 ≥ 0.7）。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">13</div><div class="ind-title"><div class="ind-name">人类干扰强度（土地胁迫指数）</div><div class="ind-en">Human Disturbance / Land Stress</div></div>
          <div class="ind-meta"><span class="pill ok">矢量/栅格</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：建设用地扩张、道路、采挖、过度放牧等人为活动对造林地的侵占与扰动程度，对应 HJ 192-2015 土地胁迫指数与 HJ 1174-2021 生态破坏评估。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 192-2015 §5.4</span>土地胁迫指数；<span class="std-tag">HJ 1174-2021</span>；前沿：人类足迹指数（Human Footprint, Venter et al.）。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">LSI = Σ w<sub>j</sub> × (A<sub>j</sub> / A<sub>total</sub>) × 100<span class="fid">式 6-4</span></div>
        <p class="param-note">A<sub>j</sub> 为 j 类胁迫用地面积：建设用地 w=1.0、交通用地 w=0.6、采挖场 w=0.9、弃荒地 w=0.4；放牧压力以单位面积羊单位（SU/hm²）实测折算，封育区放牧检出即记违规图斑。LSI &gt; 100 时取 100。人类足迹版：人口密度、夜间灯光、道路密度、放牧点 4 因子 0–10 赋分叠加。</p>
        <div class="ind-sec"><b>▍数据生成</b>：两期生态系统类型矢量变化检测（post-classification comparison）→ 新增侵占图斑自动提取 → 无人机复核 → 执法/林长制处置闭环；年度土地胁迫指数随 EI 体系发布。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">14</div><div class="ind-title"><div class="ind-name">林业有害生物与鼠害发生率</div><div class="ind-en">Pest, Disease &amp; Rodent Incidence</div></div>
          <div class="ind-meta"><span class="pill info">样地+无人机</span><span class="pill info">生长季月度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：病虫鼠害对苗木的危害程度。高原主要威胁：杨树烂皮病、蚜虫类、地下害虫（蛴螬）、高原鼠兔/中华鼢鼠啃食根系与树皮。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">LY/T 1681</span>《林业有害生物发生及成灾标准》；<span class="std-tag">GB/T 15776-2023</span>未成林管护要求；草原鼠害参照 NY/T 1240 调查规程。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">I<sub>pest</sub> = N<sub>damaged</sub> / N<sub>total</sub> × 100%<span class="fid">式 6-5</span></div>
        <p class="param-note">样地逐株调查受害等级（健康/轻度/中度/重度/死亡）；发生率 = 受害株数占比；成灾标准按 LY/T 1681：叶部害虫失叶率 ≥ 60%、蛀干害虫受害株率 ≥ 20%、鼠害受害株率 ≥ 15%（新造林地）即达成灾。鼠密度以有效洞口法（个/hm²）调查，高原鼠兔 ≥ 60 洞口/hm² 为超标。</p>
        <div class="ind-sec"><b>▍数据生成</b>：样地月度调查 + 无人机多光谱异常图斑（红边波段 NDRE 对早期胁迫敏感）AI 初筛 → 地面复核 → 小班发生率属性更新 → 防治工单派发。</div>
      </div>
    </section>

    <!-- 7 维度四：工程响应 -->
    <section id="m7" class="ins-section doc">
      <h2 class="chap">7 维度四：工程响应（Engineering Response，4 项）</h2>
      <p>工程响应维度评估「人做了什么、做得如何」——以 GB/T 15776-2023 法定评价指标为骨干，直接对接营造林实绩核查与三年管护考核，是工程建设管理的核心抓手。</p>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">15</div><div class="ind-title"><div class="ind-name">造林成活率</div><div class="ind-en">Survival Rate of Afforestation</div></div>
          <div class="ind-meta"><span class="pill ok">小班矢量</span><span class="pill info">春/秋季</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：以小班为单元，造林地上成活苗木株（穴）数与作业设计种植株（穴）数的百分比。造林一年或一个完整生长季后评价。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB/T 15776-2023 §16.2</span>。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">P<sub>1</sub> = N<sub>1</sub> / N<sub>0</sub> × 100%<span class="fid">式 7-1</span></div>
        <p class="param-note">N<sub>1</sub> 为评价当年具有成活苗木的种植点穴数；N<sub>0</sub> 为作业设计种植点穴数。调查方法：小班面积 ≤ 15 hm² 全查；&gt; 15 hm² 机械抽样（样行/样带法，抽样强度 ≥ 5%，小班抽取比例不低于核查面积 10%）。<strong>分级（国标）</strong>：青藏高寒区/干旱半干旱区 ≥ 70% 合格，41%–69% 需补植，&lt; 41% 失败重造；<strong>工程内控目标</strong>：≥ 85%，优良区 ≥ 90%。</p>
        <div class="ind-sec"><b>▍矢量生成流程</b>：作业设计小班矢量（落地上图）→ 春/秋两季实地核查（RTK 定位样行）+ 无人机正射影像株数识别（深度学习目标检测，识别精度 ≥ 92% 时以机判为主、人查复核）→ 成活率属性写入小班表 → 分级渲染上图。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">16</div><div class="ind-title"><div class="ind-name">造林株数保存率 / 面积保存率</div><div class="ind-en">Reserving Rate (3–5 a)</div></div>
          <div class="ind-meta"><span class="pill ok">小班矢量</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：造林 3–5 年后保存株（穴）数与设计株（穴）数之比（P<sub>2</sub>），是判定「造林有成效」的法定指标；面积保存率用于评定单位汇总。高原因干旱高寒树冠伸展慢，国标明确：暂难达郁闭度/盖度标准者，<strong>株数保存率达标即视为有成效</strong>。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB/T 15776-2023 §16.3</span>。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">P<sub>2</sub> = N<sub>2</sub> / N<sub>0</sub> × 100%<span class="fid">式 7-2</span></div>
        <p class="param-note">N<sub>2</sub> 为造林 3–5 a 后成活株（穴）数。青藏高寒区合格线 ≥ 65%（中温带/暖温带为 80%）；成效合格小班并列条件：乔木郁闭度 ≥ 0.2，或灌木盖度 ≥ 40%。乔灌混交时乔、灌木株数一同纳入计算。调查与空间化流程同指标 15。</p>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">17</div><div class="ind-title"><div class="ind-name">苗木质量合格率</div><div class="ind-en">Seedling Quality Qualification</div></div>
          <div class="ind-meta"><span class="pill info">批次检测</span><span class="pill info">造林季</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：出圃/上山苗木达到质量分级标准的批次比例，从源头保障成活率。南北山要求：乡土树种为主（油松、樟子松、藏川杨、江孜沙棘、绢毛蔷薇等 30 余种），<strong>引种树种须在拉萨本地驯化 180 天以上</strong>。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">GB 6000-1999</span>《主要造林树种苗木质量分级》（Ⅰ、Ⅱ级苗为合格苗）；<span class="std-tag">LY/T 1607</span>《造林作业设计规程》。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">Q<sub>seedling</sub> = B<sub>qualified</sub> / B<sub>total</sub> × 100%<span class="fid">式 7-3</span></div>
        <p class="param-note">每批抽检 5%（不低于 100 株）：容器苗/裸根苗分别测定苗高、地径、根系长度与 &gt; 5 cm Ⅰ级侧根数，对照 GB 6000-1999 分树种分级表判定；Ⅱ级以上为合格。附加工程条款：驯化期 &lt; 180 d 的外地引种苗整批判不合格。合格率目标 ≥ 98%。</p>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">18</div><div class="ind-title"><div class="ind-name">灌溉保证率与管护到位率</div><div class="ind-en">Irrigation Assurance &amp; Tending Compliance</div></div>
          <div class="ind-meta"><span class="pill ok">站点+台账</span><span class="pill info">月度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：「水随林走、电随水走、路随林走」保障体系的实际运行水平：①灌溉保证率 = 实际有效灌溉面积 / 应灌面积（生长季逐月）；②管护到位率 = 按三年管护机制完成浇水、修剪、除草、防冻、病虫害防治台账的小班比例。</div>
        <div class="ind-sec"><b>▍标准依据</b>：工程「水电路」一体化配套设计要求；<span class="std-tag">GB/T 15776-2023</span>未成林造林地封育管护；林长制巡护考核办法。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">I<sub>assure</sub> = A<sub>irrigated</sub> / A<sub>required</sub> × 100%； T<sub>comply</sub> = P<sub>done</sub> / P<sub>planned</sub> × 100%<span class="fid">式 7-4</span></div>
        <p class="param-note">灌溉有效性以土壤墒情站 0–40 cm 体积含水率判定：灌溉后 48 h 内含水率 ≥ 田间持水量 60% 记有效；墒情站不足时按智能灌溉系统流量累计反演。管护计划按小班逐月生成（新造林地浇水 ≥ 4 次/生长季、培土防冻 1 次/年），T<sub>comply</sub> 按完成工单比例计。目标：I<sub>assure</sub> ≥ 90%、T<sub>comply</sub> = 100%。</p>
      </div>
    </section>

    <!-- 8 维度五：稳定性 -->
    <section id="m8" class="ins-section doc">
      <h2 class="chap">8 维度五：稳定性（Stability &amp; Resilience，4 项）</h2>
      <p>稳定性维度评估增绿成果能否「留得住、可持续」——采用时间序列遥感与长期定位观测相结合的前沿方法，刻画植被动态的年际稳定性、扰动后的恢复能力以及林分-土壤系统的健康走向，对应 HJ 1172-2021 质量评估的动态视角与 GB/T 38582-2020 支持服务的长期性。</p>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">19</div><div class="ind-title"><div class="ind-name">植被动态年际稳定性（NDVI-Cv / 趋势斜率）</div><div class="ind-en">Inter-annual Vegetation Stability</div></div>
          <div class="ind-meta"><span class="pill ok">时序栅格</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：植被绿度年际波动越小、趋势越向上，生态系统越稳定。新造林地允许前期波动，但 5 年后应进入「低变异 + 正趋势」通道。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 1172-2021</span>动态评估思想；前沿：时间序列变异系数法 + Sen 斜率 / Mann-Kendall 显著性检验（生态遥感主流方法）。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">C<sub>v</sub> = σ<sub>NDVI</sub> / μ<sub>NDVI</sub>；Slope = Sen 估计量，显著性用 Z<sub>MK</sub> 检验（|Z| ≥ 1.96 为 P &lt; 0.05）<span class="fid">式 8-1</span></div>
        <p class="param-note">以逐年生长季（7–9 月）MVC 合成 NDVI 序列为输入，逐像元计算 C<sub>v</sub> 与趋势。分级：C<sub>v</sub> &lt; 0.10 且斜率显著为正 → 稳定提升（优）；C<sub>v</sub> 0.10–0.20 → 基本稳定；C<sub>v</sub> &gt; 0.20 或斜率显著为负 → 不稳定（触发预警并回溯成因）。</p>
        <div class="ind-sec"><b>▍栅格生成流程</b>：2021 年以来逐旬 NDVI 数据立方体 → 年度 MVC 合成 → 逐像元时间序列分析（rasterio + pymannkendall）→ 稳定性分级图 → 与压力图层叠加归因（干旱年剔除法做稳健性检验）。</div>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">20</div><div class="ind-title"><div class="ind-name">生态系统恢复力（扰动-恢复指数）</div><div class="ind-en">Ecosystem Resilience</div></div>
          <div class="ind-meta"><span class="pill ok">时序栅格</span><span class="pill info">事件驱动</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：干旱、冻害、火灾等扰动后植被恢复到扰动前水平的速度与程度，是生态系统抵抗力的直接证据，也是评估混交/乡土树种配置合理性的依据。</div>
        <div class="ind-sec"><b>▍标准依据</b>：前沿方法：抵抗力-恢复力框架（Resistance-Resilience, Lloret et al.）；参考 <span class="std-tag">HJ 1174-2021</span>生态问题评估的扰动识别流程。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">R<sub>resist</sub> = NDVI<sub>during</sub> / NDVI<sub>pre</sub>； R<sub>recov</sub> = NDVI<sub>post</sub> / NDVI<sub>pre</sub>；R<sub>rs</sub> = R<sub>recov</sub> / (1 − R<sub>resist</sub> + ε)<span class="fid">式 8-2</span></div>
        <p class="param-note">NDVI<sub>pre</sub> 为扰动前 2 年同期均值；NDVI<sub>during</sub> 为扰动事件窗口值；NDVI<sub>post</sub> 为扰动后第 1–2 个生长季均值；ε = 0.01 防除零。R<sub>recov</sub> ≥ 0.95 为「完全恢复」，0.8–0.95 为「基本恢复」，&lt; 0.8 为「恢复不良」（列入补植/改植候选）。</p>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">21</div><div class="ind-title"><div class="ind-name">林分健康度</div><div class="ind-en">Stand Health Index</div></div>
          <div class="ind-meta"><span class="pill info">样地+无人机</span><span class="pill info">年度</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：苗木生长势、冠层色泽、受害状况的综合健康评价。健康林分是稳定性与功能持续发挥的前提。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">HJ 1167-2021</span>森林生态系统野外观测；<span class="std-tag">GB/T 15776-2023</span>幼林生长要求；退化防护林修复技术规定（树势判定口径）。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">SHI = 0.35×G + 0.25×C<sub>rown</sub> + 0.25×(1 − I<sub>pest</sub>) + 0.15×H<sub>inc</sub><span class="fid">式 8-3</span></div>
        <p class="param-note">G 生长势得分：当年高生长量达标率（油松 1–3 年生 ≥ 15 cm/a 记 1，按比例折算）；C<sub>rown</sub> 冠层色泽正常率（无人机多光谱 NDRE ≥ 0.25 且目视正常株占比）；I<sub>pest</sub> 病虫害发生率（指标 14）；H<sub>inc</sub> 树高年增量达标率。SHI ∈ [0,1]，≥ 0.8 健康、0.6–0.8 亚健康、&lt; 0.6 不健康。</p>
      </div>

      <div class="ind-card">
        <div class="ind-head"><div class="ind-no">22</div><div class="ind-title"><div class="ind-name">土壤质量改善度</div><div class="ind-en">Soil Quality Improvement</div></div>
          <div class="ind-meta"><span class="pill info">剖面实测</span><span class="pill info">2–3 年</span></div></div>
        <div class="ind-sec"><b>▍定义与意义</b>：造林后土壤有机质、容重、含水率等理化性质的改善幅度——决定林分能否跨越「成活 → 成林 → 自成维持」的阈值，是客土改良与施肥措施成效的直接证据。</div>
        <div class="ind-sec"><b>▍标准依据</b>：<span class="std-tag">NY/T 1121 系列</span>土壤检测方法；<span class="std-tag">HJ 1173-2021</span>土壤保持功能；客土改良执行作业设计（LY/T 1607）。</div>
        <div class="ind-sec"><b>▍计算方法</b>：</div>
        <div class="formula">SQI = Σ w<sub>k</sub> × (X<sub>k</sub> − X<sub>k0</sub>) / X<sub>k0</sub><span class="fid">式 8-4</span></div>
        <p class="param-note">指标与权重：有机质 0.4（NY/T 1121.6 重铬酸钾法，g/kg）、容重 0.2（环刀法 NY/T 1121.4，逆向计）、田间持水量 0.2、全氮 0.1（NY/T 1121.24）、有效磷 0.1（NY/T 1121.7）。X<sub>k0</sub> 为造林前本底。SQI &gt; 0.15 为显著改善，0–0.15 为改善，&lt; 0 为退化（须排查管护与灌溉制度）。采样：每片区按海拔带 × 造林年度布设固定剖面点，0–20 / 20–40 / 40–100 cm 分层，3 次重复。</p>
      </div>
    </section>

    <!-- 9 综合评估与分级 -->
    <section id="m9" class="ins-section doc">
      <h2 class="chap">9 综合评估与分级</h2>
      <h3 class="sec">9.1 指标标准化</h3>
      <p>22 项指标量纲各异，统一归一至 [0, 100]：</p>
      <div class="formula">正向指标：S<sub>i</sub> = (X<sub>i</sub> − X<sub>min</sub>) / (X<sub>target</sub> − X<sub>min</sub>) × 100<span class="fid">式 9-1</span></div>
      <div class="formula">逆向指标（压力维度）：S<sub>i</sub> = (X<sub>max</sub> − X<sub>i</sub>) / (X<sub>max</sub> − X<sub>target</sub>) × 100<span class="fid">式 9-2</span></div>
      <p class="param-note">X<sub>target</sub> 取规划目标值或国家标准合格线（如 FVC 目标 60%、成活率国标 70% / 内控 85%）；X<sub>min</sub> 取 2021 本底值，X<sub>max</sub> 取压力指标本底最差值；S<sub>i</sub> 截断至 [0, 100]。涉及国标阈值的指标另设「一票否决」下限：成活率 &lt; 41%（国标失败线）、发生林业有害生物成灾、发生违规侵占未整改的，该维度得分封顶 40 分。</p>
      <h3 class="sec">9.2 权重体系（层次分析法 AHP + 熵权法组合赋权）</h3>
      <table class="tbl">
        <tr><th>维度</th><th>权重</th><th>维度内指标权重</th></tr>
        <tr><td>覆盖结构</td><td>0.25</td><td>FVC 0.30 · 林草覆盖率 0.25 · 郁闭度/盖度 0.20 · 垂直结构 0.10 · 景观格局 0.15</td></tr>
        <tr><td>功能</td><td>0.25</td><td>水源涵养 0.25 · 土壤保持 0.20 · NPP 0.20 · 碳储量 0.20 · 生物多样性 0.15</td></tr>
        <tr><td>压力</td><td>0.15</td><td>土壤侵蚀 0.30 · 干旱胁迫 0.30 · 人类干扰 0.20 · 病虫鼠害 0.20</td></tr>
        <tr><td>工程响应</td><td>0.20</td><td>成活率 0.35 · 保存率 0.30 · 苗木质量 0.15 · 灌溉管护 0.20</td></tr>
        <tr><td>稳定性</td><td>0.15</td><td>年际稳定性 0.30 · 恢复力 0.25 · 林分健康 0.25 · 土壤改善 0.20</td></tr>
      </table>
      <p class="param-note">主观权重由 9 人专家群（造林、草原、水土保持、遥感、生态）两两比较矩阵获得，一致性比率 CR &lt; 0.1；熵权法按指标年度数据的离散度修正，最终权重 = 0.6×AHP + 0.4×熵权。权重每 2 年复评。</p>
      <h3 class="sec">9.3 综合指数与分级</h3>
      <div class="formula">GEI = Σ<sub>d=1</sub><sup>5</sup> W<sub>d</sub> × Σ<sub>i</sub> w<sub>di</sub> × S<sub>di</sub><span class="fid">式 9-3</span></div>
      <table class="tbl">
        <tr><th>GEI</th><th>≥ 85</th><th>70 – 85</th><th>55 – 70</th><th>40 – 55</th><th>&lt; 40</th></tr>
        <tr><td>等级</td><td><span class="pill ok">优</span></td><td><span class="pill info">良</span></td><td><span class="pill warn">中</span></td><td><span class="pill warn">较差</span></td><td><span class="pill bad">差</span></td></tr>
        <tr><td>管理含义</td><td>示范推广</td><td>巩固提升</td><td>定向补植</td><td>限期整改</td><td>重新作业设计</td></tr>
      </table>
      <p class="param-note">分级衔接 HJ 192-2015 生态环境状况五级分级的管理语义。工作台雷达图展示五维得分与 2030 目标对照；偏离度 = (目标 − 当前) / 目标 × 100%。</p>
      <h3 class="sec">9.4 偏离预警阈值规则</h3>
      <table class="tbl">
        <tr><th>级别</th><th>触发条件（任一）</th><th>处置时限</th></tr>
        <tr><td><span class="pill bad">高（红）</span></td><td>触碰国标底线：成活率 &lt; 41% / 保存率 &lt; 40% / 中度以上侵蚀面积 &gt; 40% / 有害生物成灾 / 违规侵占未整改</td><td>48 h 现场核查</td></tr>
        <tr><td><span class="pill warn">中（黄）</span></td><td>偏离年度目标 10%–20%；VCI &lt; 35% 持续 2 旬；灌溉保证率 &lt; 80%；SHI &lt; 0.6</td><td>7 d 内提出措施</td></tr>
        <tr><td><span class="pill info">低（蓝）</span></td><td>偏离目标 5%–10%；NDVI 趋势斜率转负（不显著）；单项指标连续两期下降</td><td>纳入下轮核查</td></tr>
      </table>
    </section>

    <!-- 10 栅格/矢量产品生产流程 -->
    <section id="m10" class="ins-section doc">
      <h2 class="chap">10 栅格 / 矢量产品生产流程（总工艺）</h2>
      <h3 class="sec">10.1 产品清单</h3>
      <table class="tbl">
        <tr><th>产品</th><th>类型</th><th>分辨率</th><th>更新</th><th>支撑指标</th></tr>
        <tr><td>NDVI / FVC 植被参数</td><td>栅格</td><td>10 m（重点区 2 m）</td><td>16 d / 年度 MVC</td><td>1, 7, 11, 19, 20</td></tr>
        <tr><td>生态系统类型图</td><td>矢量</td><td>≥ 1:10 000 精度</td><td>年度</td><td>2, 5, 13</td></tr>
        <tr><td>NPP 生产力</td><td>栅格</td><td>30 m（1 km 气象驱动降尺度）</td><td>月 / 年</td><td>8, 9</td></tr>
        <tr><td>水源涵养量</td><td>栅格</td><td>30 m</td><td>年</td><td>6</td></tr>
        <tr><td>土壤侵蚀强度</td><td>栅格</td><td>12.5–30 m</td><td>年</td><td>7, 11</td></tr>
        <tr><td>干旱胁迫 VCI/SPEI</td><td>栅格</td><td>10 m / 1 km</td><td>旬</td><td>12</td></tr>
        <tr><td>造林小班（成活率/保存率属性）</td><td>矢量</td><td>小班边界 ±1 m</td><td>春/秋</td><td>15, 16, 17, 18</td></tr>
        <tr><td>固定样地点位与调查表</td><td>矢量点 + 属性</td><td>RTK ≤ 0.1 m</td><td>年</td><td>3, 4, 10, 14, 21, 22</td></tr>
        <tr><td>无人机正射/多光谱</td><td>栅格</td><td>3–10 cm</td><td>按需/月度</td><td>14, 15, 21</td></tr>
      </table>
      <h3 class="sec">10.2 标准工艺流程</h3>
      <ol>
        <li><strong>任务规划</strong>：按年度监测方案确定时相窗口（生长季 7–9 月为主）、覆盖范围、云量阈值（&lt; 10%）与无人机补飞清单；</li>
        <li><strong>数据获取与入库</strong>：卫星影像、气象站点、无人机、样地调查四路数据统一入库（原始库），记录元数据；</li>
        <li><strong>预处理</strong>：执行第 3.2 节辐射定标 → 大气校正 → 正射校正 → 掩膜 → 镶嵌流水线，产出分析就绪数据（ARD）；</li>
        <li><strong>指标计算</strong>：按第 4–8 章模型链批处理（栅格代数 + 分区统计），模型版本与参数文件随成果归档；</li>
        <li><strong>空间综合</strong>：栅格产品 → 小班分区统计；矢量产品 → 属性更新；样地数据 → 反演模型标定；</li>
        <li><strong>质量检验</strong>：执行第 11 章精度验证，不合格产品退回重算；</li>
        <li><strong>发布应用</strong>：成果库发布 → 一张图服务（WMS/WMTS）→ 综合评估 → 预警与报告。</li>
      </ol>
      <h3 class="sec">10.3 自动化实现</h3>
      <p>平台后端以定时任务驱动：新影像到达 → 自动预处理 → 指标链重算 → 阈值比对 → 预警推送。模型链以 Python（rasterio / xarray / pymannkendall）实现，参数化配置；无人机株数识别采用深度学习目标检测（训练样本 ≥ 3 万标注株，mAP ≥ 0.92）。</p>
    </section>

    <!-- 11 质量控制 -->
    <section id="m11" class="ins-section doc">
      <h2 class="chap">11 质量控制与精度验证</h2>
      <h3 class="sec">11.1 过程质控（HJ 1176-2021）</h3>
      <ul>
        <li><strong>双检制度</strong>：遥感解译/分类成果一审（自检）一验（专检），错误图斑率 &gt; 3% 整批返工；</li>
        <li><strong>样本规范</strong>：训练/验证样本独立，比例 7:3，空间自相关控制（样本间距 ≥ 500 m 或分区抽样）；</li>
        <li><strong>版本管理</strong>：数据、模型、参数、成果四要素版本号绑定，任意成果可复现；</li>
        <li><strong>不确定度报告</strong>：碳储量、NPP、水源涵养量等模型产品须给出 ±95% 置信区间或相对误差。</li>
      </ul>
      <h3 class="sec">11.2 精度验收指标</h3>
      <table class="tbl">
        <tr><th>成果</th><th>验收方法</th><th>合格标准</th></tr>
        <tr><td>生态系统类型图</td><td>野外核查点混淆矩阵（HJ 1166-2021 附录 C）</td><td>总体精度 ≥ 90%，Kappa ≥ 0.85</td></tr>
        <tr><td>FVC 栅格</td><td>样地照相法/目估法真值回归</td><td>R² ≥ 0.80，RMSE ≤ 0.10</td></tr>
        <tr><td>郁闭度反演</td><td>样地真值回归</td><td>R² ≥ 0.75</td></tr>
        <tr><td>NPP 产品</td><td>与 MOD17 及生物量实测换算对比</td><td>相对偏差 ≤ 15%</td></tr>
        <tr><td>土壤侵蚀模数</td><td>小流域卡口站/径流小区输沙模数验证</td><td>相关系数 ≥ 0.7，Nash 系数 ≥ 0.5</td></tr>
        <tr><td>株数机判</td><td>人工抽样比对</td><td>株数识别精度 ≥ 92%</td></tr>
      </table>
    </section>

    <!-- 12 功能操作指南 -->
    <section id="m12" class="ins-section doc">
      <h2 class="chap">12 功能操作指南</h2>
      <table class="tbl">
        <tr><th style="width:130px">模块</th><th>操作说明</th></tr>
        <tr><td>工作台</td><td>查看工程总体 KPI、NDVI/FVC/碳储量趋势、五维雷达与快速入口；数字为年度综合值，悬停图表查看分期数值。</td></tr>
        <tr><td>生态一张图</td><td>左侧勾选图层（NDVI 栅格、小班矢量、样地点、水系灌溉、海拔分区、风险图）；点击小班查看属性（成活率、保存率、树种、年度）。</td></tr>
        <tr><td>指标计算</td><td>左侧按维度选择指标，右侧显示公式、参数与标准依据；输入实际观测值即时试算，并给出国标/内控双档判定。完整方法学见第 4–8 章。</td></tr>
        <tr><td>巡检照片</td><td>按日期/航线浏览巡检影像；自动提取 EXIF GPS 信息上图，支持缺陷标注（植被退化/病虫害/裸露）。</td></tr>
        <tr><td>野外科考</td><td>① <strong>照片采集</strong>：手机现场拍摄即时上传，或先拍照后集中上传；系统自动解析 JPEG EXIF 中的经纬度/海拔/拍摄时间，并可为每张照片添加物种、树高、胸径/丛幅、盖度等文本注释；选择项目后照片与注释可同步至「巡检照片」模块。② <strong>考察轨迹</strong>：支持手机浏览器实时记录（高精度 GPS 持续采点），以及导入 <strong>GPX（trk/rte/wpt）、KML、CSV/TXT 经纬度坐标表（自动识别中英文表头与列序）、照片坐标点批量成轨</strong>，兼容「两步路」「行者」「六只脚」等户外 App 导出的轨迹文件；坐标按 WGS84/CGCS2000 处理（差异 &lt; 1 m 免转换）；轨迹可导出 GPX 回传户外 App。③ 科考地图自动叠加照片点位与轨迹，并给出里程、点数、爬升、时长统计。野外数据在本地持久化保存，弱网/无网环境可用。</td></tr>
        <tr><td>偏离预警</td><td>按 9.4 节阈值规则自动生成；点击预警查看触发指标、偏离度与建议措施，处置后标记闭环。</td></tr>
        <tr><td>评估报告</td><td>选择报告类型/时段/范围一键生成；报告自动嵌入趋势图、雷达图、指标表与标准符合性结论。</td></tr>
        <tr><td>设备清单</td><td>蓄水池、管线、泵站、监测站、无人机台账与在线状态；故障设备自动生成运维工单。</td></tr>
        <tr><td>使用说明</td><td>本文档；可用浏览器打印/导出 PDF，作为监测实施细则附件存档。</td></tr>
      </table>
    </section>

    <!-- 13 参考标准与文献 -->
    <section id="m13" class="ins-section doc">
      <h2 class="chap">13 参考标准与文献</h2>
      <ol class="ref-list">
        <li>GB/T 15776-2023 造林技术规程</li>
        <li>GB/T 38582-2020 森林生态系统服务功能评估规范</li>
        <li>HJ 1166-2021 全国生态状况调查评估技术规范——生态系统遥感解译与野外核查</li>
        <li>HJ 1167-2021 ——森林生态系统野外观测；HJ 1168-2021 ——草地生态系统野外观测</li>
        <li>HJ 1171-2021 ——生态系统格局评估；HJ 1172-2021 ——生态系统质量评估；HJ 1173-2021 ——生态系统服务功能评估；HJ 1174-2021 ——生态问题评估；HJ 1175-2021 ——项目尺度生态影响评估；HJ 1176-2021 ——数据质量控制与集成</li>
        <li>HJ 192-2015 生态环境状况评价技术规范</li>
        <li>HJ 623-2011 区域生物多样性评价标准</li>
        <li>SL 190-2007 土壤侵蚀分类分级标准</li>
        <li>GB/T 26424-2010 森林资源规划设计调查技术规程；LY/T 1607 造林作业设计规程；GB 6000-1999 主要造林树种苗木质量分级</li>
        <li>GB/T 20481-2017 气象干旱等级；LY/T 1681 林业有害生物发生（危害）程度标准；NY/T 1121 系列 土壤检测</li>
        <li>TD/T 1055 第三次全国国土调查技术规程</li>
        <li>青藏高原生态屏障区生态保护和修复重大工程建设规划（2021—2035 年）；拉萨市南北山绿化相关规划与三年管护机制文件</li>
        <li>前沿方法：CASA（Potter et al., 1993；朱文泉等，2005 中国参数化）；RUSLE（Renard et al., 1997）；InVEST Water Yield；像元二分模型（李苗苗等）；Sen/Mann-Kendall 时序分析；Resistance–Resilience 框架（Lloret et al., 2011）</li>
      </ol>
      <div class="notebar">本方法学随国家标准与工程要求动态修订；如标准更新，以最新有效版本为准，平台指标计算模块同步升级并保留历史版本追溯。</div>
    </section>

    <el-backtop target=".main" :visibility-height="200" />
  </div>
</template>

<script setup>
import { Collection } from '@element-plus/icons-vue'

const toc = [
  { id: 'm1', num: '01', title: '系统概述' },
  { id: 'm2', num: '02', title: '评估框架与标准依据' },
  { id: 'm3', num: '03', title: '数据基础与预处理要求' },
  { id: 'm4', num: '04', title: '维度一：覆盖结构（5 项）' },
  { id: 'm5', num: '05', title: '维度二：功能（5 项）' },
  { id: 'm6', num: '06', title: '维度三：压力（4 项）' },
  { id: 'm7', num: '07', title: '维度四：工程响应（4 项）' },
  { id: 'm8', num: '08', title: '维度五：稳定性（4 项）' },
  { id: 'm9', num: '09', title: '综合评估与分级' },
  { id: 'm10', num: '10', title: '栅格/矢量产品生产流程' },
  { id: 'm11', num: '11', title: '质量控制与精度验证' },
  { id: 'm12', num: '12', title: '功能操作指南' },
  { id: 'm13', num: '13', title: '参考标准与文献' },
]

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
.instructions-modern { padding-bottom: 40px; max-width: 1100px; margin: 0 auto; }

/* Hero */
.ins-hero {
  position: relative;
  background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(11,143,168,0.08));
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;
  margin-bottom: 20px;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.08);
}
.ins-hero-glow {
  position: absolute; top: -50px; left: 50%; transform: translateX(-50%);
  width: 300px; height: 200px;
  background: radial-gradient(ellipse, rgba(16,185,129,0.18), transparent 70%);
  pointer-events: none;
}
.ins-hero-icon { margin-bottom: 14px; }
.ins-hero-title {
  font-size: 26px; font-weight: 700;
  background: linear-gradient(135deg, #0f2e1f, #2E9E63);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 8px;
}
.ins-hero-sub { font-size: 15px; color: #3d5a4c; margin: 0 0 4px; }
.ins-hero-ver { font-size: 11px; color: #9ab5a8; }
.ins-hero-intro {
  margin: 14px auto 0; max-width: 860px; text-align: justify;
  font-size: 13px; line-height: 2; color: #3d5a4c;
}

/* TOC */
.ins-toc {
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.toc-header { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #1e3a2f; font-size: 13px; margin-bottom: 12px; }
.toc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.toc-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; border-radius: 8px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(15,60,40,0.06);
  color: #3d5a4c; text-decoration: none; font-size: 12px;
  transition: all 0.2s;
}
.toc-item:hover { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.25); color: #0d9862; }
.toc-num { font-size: 10px; font-weight: 800; color: #9ab5a8; font-variant-numeric: tabular-nums; }

/* Sections */
.ins-section {
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px;
  padding: 26px 28px;
  margin-bottom: 14px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
  scroll-margin-top: 76px;
}
.doc h2.chap {
  font-size: 19px; font-weight: 800; color: #0f2e1f;
  padding-bottom: 12px; margin: 0 0 16px;
  border-bottom: 2px solid transparent;
  border-image: linear-gradient(90deg, #10b981, #0b8fa8, transparent) 1;
}
.doc h3.sec {
  font-size: 15px; font-weight: 800; color: #0f2e1f;
  margin: 22px 0 10px; display: flex; align-items: center; gap: 9px;
}
.doc h3.sec::before {
  content: ''; width: 5px; height: 18px; border-radius: 3px;
  background: linear-gradient(180deg, #10b981, #0b8fa8);
}
.doc p { font-size: 13px; line-height: 2; color: #3d5a4c; margin: 8px 0; text-align: justify; }
.doc ul, .doc ol { font-size: 13px; line-height: 2; color: #3d5a4c; padding-left: 22px; margin: 6px 0; }
.doc li { margin: 3px 0; }
.doc strong { color: #0f2e1f; }

/* Tables */
.tbl { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 12px; }
.tbl th {
  background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(11,143,168,0.08));
  color: #0f2e1f; font-weight: 700; text-align: left;
  padding: 8px 10px; border: 1px solid rgba(15,60,40,0.08);
}
.tbl td { padding: 8px 10px; border: 1px solid rgba(15,60,40,0.07); color: #3d5a4c; line-height: 1.7; }
.tbl tr:hover td { background: rgba(16,185,129,0.04); }

/* Indicator cards */
.ind-card {
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(15,60,40,0.07);
  border-radius: 14px;
  padding: 16px 18px;
  margin: 14px 0;
}
.ind-head { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.ind-no {
  width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #10b981, #0b8fa8);
  color: #fff; font-size: 15px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(14,159,110,0.3);
}
.ind-title { flex: 1; min-width: 180px; }
.ind-name { font-size: 15px; font-weight: 700; color: #0f2e1f; }
.ind-en { font-size: 11px; color: #7a968a; }
.ind-meta { display: flex; gap: 6px; }
.ind-sec { font-size: 13px; line-height: 1.9; color: #3d5a4c; margin: 7px 0; text-align: justify; }
.ind-sec b { color: #0f2e1f; }

/* Formula */
.formula {
  position: relative;
  background: linear-gradient(135deg, rgba(16,185,129,0.07), rgba(11,143,168,0.05));
  border: 1px solid rgba(16,185,129,0.18);
  border-radius: 10px;
  padding: 12px 90px 12px 16px;
  margin: 8px 0;
  font-size: 13.5px; color: #0f2e1f; font-weight: 600;
  font-family: "Cambria Math", Georgia, serif;
  overflow-x: auto;
}
.fid { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); font-size: 11px; color: #0d9862; font-weight: 700; }
.param-note { font-size: 12px !important; color: #5a7a6a !important; background: rgba(15,60,40,0.03); border-radius: 8px; padding: 8px 12px; }

/* Tags & pills */
.std-tag {
  display: inline-block; padding: 1px 8px; border-radius: 6px;
  background: rgba(36,112,216,0.08); color: #2470d8;
  font-size: 11px; font-weight: 600; white-space: nowrap;
}
.pill { display: inline-block; padding: 2px 10px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.pill.ok { background: rgba(16,185,129,0.12); color: #0d9862; }
.pill.info { background: rgba(36,112,216,0.1); color: #2470d8; }
.pill.warn { background: rgba(199,127,10,0.12); color: #c77f0a; }
.pill.bad { background: rgba(220,53,53,0.1); color: #dc3535; }

.notebar {
  background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(11,143,168,0.05));
  border-left: 4px solid #10b981;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 14px;
  font-size: 12.5px; line-height: 1.9; color: #3d5a4c;
}
.ref-list { font-size: 12.5px; line-height: 2.1; }

@media (max-width: 900px) {
  .toc-grid { grid-template-columns: repeat(2, 1fr); }
  .ins-section { padding: 18px 16px; }
  .ins-hero { padding: 28px 18px; }
  .ins-hero-title { font-size: 20px; }
  .formula { padding-right: 16px; }
  .fid { position: static; display: block; transform: none; margin-top: 4px; }
}
</style>
