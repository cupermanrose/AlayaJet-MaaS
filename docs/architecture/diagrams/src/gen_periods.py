#!/usr/bin/env python3
"""三个时期图（方案 B）：黑白总架构图为底，每期一色高亮一条链路。
底图由 gen_overview.py 源码去色、去边标签后生成，方框位置与总架构图严格一致。"""
import math, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
BLUE, GREEN, ORANGE = "#2563EB", "#15803D", "#C2410C"
AUX = "#DC2626"   # 前置 / 持续机制 / 分支（红，与主色强对比）

# 各期都删的边标签（总架构图已说明）
COMMON_CUTS = ['"Inference API"', '"推理请求（OpenAI 兼容 · 流式 / 非流式）"',
               '"Usage Events（Kafka）"', '"用量事件 · 修正事件"',
               '"Management API"', '"发布 / 暂停 / 扩缩 · 节点准入"',
               '"日志 · usage"', '"转发请求 · 直连 Pod IP"',
               '"写 CR"', '"写对象"', '"watch · 上报"',
               '"KV 出"', '"KV 入"', '"集群外 · 引导救援"', '"权重预热源"']
# 可按期裁掉的外部方（胶囊 + 其连线）
PILL_BUSINESS = ['pill(GC - 78, 8, 156, 30, "上游业务平台")', 'linee(GC, 38, GC, GW_Y - 3)']
PILL_BILLING = ['pill(KC - 78, 8, 156, 30, "上游计费 / 消费方")', 'linee(KC, RY, KC, 41)']
PILL_OPS = ['pill(960, 8, 140, 30, "平台运维")', 'linee(1030, 38, 1030, 64)']
# 部署期用不到的关系箭头
DEPLOY_EDGE_CUTS = [
    'linee(LG_X, RY + 22',          # Usage Ledger → Kafka
    'linee(CP_X, RY + 22',          # CP → OME（黑色，被蓝② 取代）
    'linee(GW_X, GWM, LGC, GWM)',   # gateway → Ledger
    'linee(LGC, GWM, LGC, RY - 3)',
    'linee(GW_X + GW_W, GWM, 1112, GWM)',   # 请求转发路径
    'linee(1112, GWM, 1112, 356)',
    'linee(295, 356, 295, PB_Y - 3)',
    'linee(845, 356, 845, PB_Y - 3)',
    'linee(OMC, RY + RH, OMC, CY + 170)',   # OME → API Server（被蓝③ 取代）
    'linee(OMC, CY + 170, ASC, CY + 170)',
    'linee(ASC, CY + 170, ASC, KY - 3)',
    'linee(1030, 38, 1030, 64)',            # 运维 → CP（被蓝① 取代）
    'linee(CPC, 64, CPC, RY - 3)',
    'linee(ASC, KY + KH, ASC, PB_Y - 3)',   # watch·上报（被蓝⑤ 取代）
    'linee(430, PB_Y + PB_H',               # KV 出 / 入（执行期内容）
    'linee(1000, NET1, 1000',
]


def build_base(extra_cuts, replaces=(), wide=False):
    src = open("gen_overview.py").read()
    for old, new in replaces:
        assert src.count(old) == 1, f"replace: {old!r}"
        src = src.replace(old, new)
    src = src.replace('KBG, PBG, EBG, OBG, SBG = "#DCE9F7", "#EEF4FB", "#DFF0D8", "#EDE4F6", "#FDEBD3"',
                      'KBG, PBG, EBG, OBG, SBG = "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"')
    src = src.replace('GBG = "#E8EAED"', 'GBG = "#FFFFFF"')
    if wide:   # 部署期：拉宽普通 Pod 与 static Pod 间的走廊
        src = src.replace("W, H = 1400, 850", "W, H = 1400, 890")
        src = src.replace("CY, CH = 96, 252", "CY, CH = 96, 344")
        src = src.replace('rect(76, CY + 160, 992, 76, PBG, rx=8, dash="5,4")',
                          'rect(76, CY + 252, 992, 76, PBG, rx=8, dash="5,4")')
        src = src.replace('text(88, CY + 176, "static Pod", anchor="start", weight="bold")',
                          'text(88, CY + 268, "static Pod", anchor="start", weight="bold")')
        src = src.replace("KY, KH = CY + 182, 48", "KY, KH = CY + 274, 48")
        src = src.replace("PB_Y, PB_H = 380, 260", "PB_Y, PB_H = 500, 260")
        src = src.replace("MY = 418", "MY = 538")
        src = src.replace("NET1, NET2, NH = 668, 712, 26", "NET1, NET2, NH = 788, 832, 26")
    else:
        src = src.replace("W, H = 1400, 850", "W, H = 1400, 768")
    for needle in COMMON_CUTS + extra_cuts:
        lines = [l for l in src.split("\n") if needle in l]
        assert len(lines) == 1, f"cut: {needle!r} matched {len(lines)}"
        src = src.replace(lines[0] + "\n", "")
    i0 = src.index("# ==================== 图例")
    i1 = src.index('P.append("</svg>")')
    src = src[:i0] + src[i1:]
    src = src.replace('open("../overview.svg", "w").write(svg)', '__out__["svg"] = svg')
    out = {}
    exec(compile(src, "base_bw", "exec"), {"__out__": out})
    return out["svg"].replace("</svg>", "")


def cline(x1, y1, x2, y2, c, sw=4, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" '
            f'stroke-width="{sw}" stroke-opacity="{op}" stroke-linecap="round"{d}/>')

def crect(x, y, w, h, c, sw=2.2):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" '
            f'stroke="{c}" stroke-width="{sw}" stroke-dasharray="6,4" stroke-opacity="0.9"/>')

def chead(x, y, ang, c, s=13):
    x1, y1 = x - s*math.cos(ang-0.42), y - s*math.sin(ang-0.42)
    x2, y2 = x - s*math.cos(ang+0.42), y - s*math.sin(ang+0.42)
    return f'<polygon points="{x},{y} {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}" fill="{c}"/>'

def cnum(x, y, n, c):
    fs = 12 if len(str(n)) == 1 else 10
    return (f'<circle cx="{x}" cy="{y}" r="10" fill="#FFFFFF" stroke="{c}" stroke-width="2"/>'
            f'<text x="{x}" y="{y+4}" font-size="{fs}" font-weight="bold" fill="{c}" '
            f'text-anchor="middle">{n}</text>')

def ctext(x, y, s, c, anchor="start", fs=12.5):
    return (f'<text x="{x}" y="{y}" font-size="{fs}" font-weight="bold" fill="{c}" '
            f'text-anchor="{anchor}">{s}</text>')

def carc(x1, y1, cx, cy, x2, y2, c, sw=4):
    return (f'<path d="M {x1} {y1} Q {cx} {cy} {x2} {y2}" fill="none" stroke="{c}" '
            f'stroke-width="{sw}" stroke-linecap="round"/>')

def save(name, base, color, title, elems, lx=(560, 700)):
    if base is None:
        base = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 830" '
                'font-family="system-ui,-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif">'
                '<rect width="1400" height="830" rx="10" fill="#FFFFFF"/>')
    parts = [base, cline(60, 64, 94, 64, color, sw=5), ctext(102, 68.5, title, color, fs=13.5),
             cline(lx[0], 64, lx[0] + 34, 64, color), ctext(lx[0] + 42, 68.5, "主线步骤", color),
             cline(lx[1], 64, lx[1] + 34, 64, AUX), ctext(lx[1] + 42, 68.5, "前置 / 持续机制 / 分支", AUX)]
    parts += elems + ["</svg>"]
    open(f"../{name}", "w").write("\n".join(parts))
    print(name, "written")


DOWN, LEFT, UP = math.pi/2, math.pi, -math.pi/2

# ==================== 部署期（蓝） ====================
LB = "#DBEAFE"   # 高亮背景：本期决策组件
base = build_base(PILL_BUSINESS + PILL_BILLING + DEPLOY_EDGE_CUTS, wide=True)
dot = lambda x, y, c: f'<circle cx="{x}" cy="{y}" r="3.5" fill="{c}"/>'
deploy = [
    # ⓪ 权重预热（发布前提）
    cline(1130, 823, 922, 823, AUX),
    cline(922, 823, 922, 744, AUX), chead(922, 739, UP, AUX),
    cnum(1030, 823, 0, AUX), ctext(910, 827, "权重预热（发布前提）", AUX, anchor="end", fs=12),
    # ① 变更请求：平台运维 → Control Plane
    cline(1030, 42, 1030, 64, BLUE), cline(1030, 64, 962, 64, BLUE),
    cline(962, 64, 962, 188, BLUE), chead(962, 193, DOWN, BLUE),
    cnum(962, 122, 1, BLUE), ctext(946, 118, "发布 / 扩容 / 回滚 / 缩容", BLUE, anchor="end"),
    # ② CP → API Server（泳道 y=330）
    cline(962, 244, 962, 330, BLUE), cline(962, 330, 282, 330, BLUE),
    cline(282, 330, 282, 364, BLUE), chead(282, 369, DOWN, BLUE),
    cnum(962, 284, 2, BLUE), ctext(944, 270, "渲染并提交 CR", BLUE, anchor="end"),
    ctext(974, 262, "ClusterBaseModel", BLUE, fs=9),
    ctext(974, 278, "ClusterServingRuntime", BLUE, fs=9),
    ctext(974, 294, "InferenceService", BLUE, fs=9),
    # ③ OME watch CR（teal 常驻，泳道 y=292）
    cline(247, 370, 247, 292, AUX), cline(247, 292, 746, 292, AUX),
    cline(746, 292, 746, 248, AUX), chead(746, 243, UP, AUX),
    cnum(560, 292, 3, AUX), ctext(576, 286, "watch CR", AUX, fs=11),
    # ④ OME → API Server：创建 / 更新工作负载（泳道 y=310）
    cline(772, 244, 772, 310, BLUE),
    cline(772, 310, 262, 310, BLUE),
    cline(262, 310, 262, 364, BLUE), chead(262, 369, DOWN, BLUE),
    cnum(490, 310, 4, BLUE), ctext(784, 300, "创建 / 更新工作负载", BLUE),
    # ⑤ Kueue（泳道 y=268）与 Scheduler（带内 y=356）
    cline(620, 244, 620, 268, BLUE), cline(620, 268, 232, 268, BLUE),
    cline(232, 268, 232, 364, BLUE), chead(232, 369, DOWN, BLUE),
    cnum(430, 268, "5a", BLUE), ctext(446, 261, "gang 放行（整组准入）", BLUE),
    cline(652, 370, 652, 356, BLUE), cline(652, 356, 302, 356, BLUE),
    cline(302, 356, 302, 364, BLUE), chead(302, 369, DOWN, BLUE),
    cnum(620, 356, "5b", BLUE), ctext(682, 362, "绑机（逐 Pod 选节点）", BLUE, fs=11),
    # ⑥ 下发：kubelet 拉起 Pod
    cline(202, 422, 202, 494, BLUE), chead(202, 499, DOWN, BLUE),
    cnum(202, 460, 6, BLUE), ctext(186, 464, "下发 · 拉起实例", BLUE, anchor="end"),
    # ⑦ 加载权重
    f'<path d="M 438 538 A 30 30 0 1 1 478 566" fill="none" stroke="{BLUE}" '
    f'stroke-width="4" stroke-linecap="round"/>',
    chead(469, 568, 3.05, BLUE),
    cnum(489, 517, 7, BLUE),
    ctext(430, 516, "加载 NVMe 权重（分钟级）", BLUE, anchor="end", fs=11.5),
    # ⑧ 服务发现：gateway watch API Server（沿左侧上行）
    cline(92, 394, 32, 394, AUX),
    cline(32, 394, 32, 167, AUX),
    cline(32, 167, 384, 167, AUX), chead(389, 167, 0, AUX),
    cnum(258, 167, 8, AUX), ctext(100, 157, "服务发现（watch）", AUX, fs=12),
    # ⑨ 缩容分支：删除指令下发到被缩容机器
    cline(270, 422, 270, 476, AUX), cline(270, 476, 684, 476, AUX),
    cline(684, 476, 684, 532, AUX), chead(684, 537, DOWN, AUX),
    cnum(600, 476, 9, AUX), ctext(700, 468, "缩容：排空 → 删 Pod → 释放整机", AUX, fs=12),
]
save("period_deploy.svg", base, BLUE, "部署期（分钟级）", deploy)


# ==================== 请求期（绿） ====================
REQ_CUTS = [PILL_BUSINESS[1], PILL_BILLING[0], PILL_BILLING[1], PILL_OPS[0]] + DEPLOY_EDGE_CUTS
base_req = build_base(REQ_CUTS)
request = [
    # ① 推理请求：上游业务平台 → gateway
    cline(550, 42, 550, 142, GREEN), chead(550, 147, DOWN, GREEN),
    cnum(550, 62, 1, GREEN), ctext(534, 66, "推理请求", GREEN, anchor="end"),
    # ② 选点并直连转发（一步：决策 + 执行）
    cline(752, 167, 1112, 167, GREEN),
    cline(1112, 167, 1112, 364, GREEN),
    cline(290, 364, 1112, 364, GREEN),
    cline(290, 364, 290, 407, GREEN), chead(290, 412, DOWN, GREEN),
    cline(800, 364, 800, 407, GREEN), chead(800, 412, DOWN, GREEN),
    cnum(940, 167, 2, GREEN), ctext(912, 150, "cache-aware 选 P · 负载选 D · 直连 leader Pod IP", GREEN, anchor="middle", fs=12),
    # ③ 逐 token 流回：D 实例 → gateway
    cline(998, 480, 1150, 480, GREEN),
    cline(1150, 480, 1150, 112, GREEN), cline(1150, 112, 700, 112, GREEN),
    cline(700, 112, 700, 142, GREEN), chead(700, 147, DOWN, GREEN),
    cnum(1150, 430, 3, GREEN), ctext(1164, 434, "逐 token 流回", GREEN),
    # ④ 流式响应：gateway → 上游
    cline(606, 150, 606, 45, GREEN), chead(606, 40, UP, GREEN),
    cnum(606, 112, 4, GREEN), ctext(622, 116, "流式响应", GREEN),
    # ⑤ 旁路计量（红）：日志 · usage → Ledger → Kafka（投递上游为异步）
    cline(392, 178, 301, 178, AUX), cline(301, 178, 301, 188, AUX), chead(301, 193, DOWN, AUX),
    cline(216, 218, 193, 218, AUX), chead(188, 218, LEFT, AUX),
    cnum(348, 178, 5, AUX), ctext(200, 170, "旁路计量 · 幂等事件", AUX, fs=11.5),
    # ⑥ 重试分支（红）：换实例重投（仅响应开始前）
    dot(350, 364, AUX),
    cline(350, 364, 350, 407, AUX), chead(350, 412, DOWN, AUX),
    cnum(350, 388, 6, AUX), ctext(366, 398, "重试：换实例（仅响应开始前）", AUX, fs=12),
    # ⑦ 取消（红）：上游断连沿直连传播，引擎 abort
    dot(870, 364, AUX),
    cline(870, 364, 870, 407, AUX), chead(870, 412, DOWN, AUX),
    cnum(870, 388, 7, AUX), ctext(886, 398, "取消：断连 → abort_request", AUX, fs=12),
    # ⑧ 健康探测（红，持续机制）：gateway 直连探活，故障摘除
    cline(392, 150, 32, 150, AUX),
    cline(32, 150, 32, 430, AUX),
    cline(32, 430, 84, 430, AUX), chead(89, 430, 0, AUX),
    cnum(110, 150, 8, AUX),
    ctext(180, 142, "健康探测（health_generate）· 故障摘除", AUX, fs=11.5),
]
save("period_request.svg", base_req, GREEN, "请求期（毫秒级）", request, lx=(760, 900))


# ==================== 执行期（紫）：SGLang 多进程拆解 ====================
PURPLE = "#6D28D9"
BK = "#111827"

def xr(x, y, w, h, sw=1.3, dash=None, rx=6):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#FFFFFF" '
            f'stroke="{BK}" stroke-width="{sw}"{d}/>')

def xt(x, y, t, anchor="middle", weight="normal", fs=12):
    return (f'<text x="{x}" y="{y}" font-size="{fs}" fill="{BK}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{t}</text>')

def xchip(x, y, w, h, l1, l2=None, fs=12):
    out = xr(x, y, w, h)
    if l2:
        out += xt(x + w/2, y + h/2 - 3, l1, weight="bold", fs=fs)
        out += xt(x + w/2, y + h/2 + 13, l2, fs=fs - 1)
    else:
        out += xt(x + w/2, y + h/2 + 4, l1, weight="bold", fs=fs)
    return out

def machine_ex(x, title, procs, r2, zgap):
    out = [xr(x, 160, 620, 560, sw=2.4, rx=10), xt(x + 310, 184, title, weight="bold")]
    out.append(xr(x + 16, 196, 588, 168, dash="5,4", rx=8))
    out.append(xt(x + 28, 212, "Pod · SGLang（多进程）", anchor="start", weight="bold"))
    for cx, cw, l1, l2 in procs:
        out.append(xchip(x + cx, 222, cw, 52, l1, l2))
    for cx, cw, l1 in r2:
        out.append(xchip(x + cx, 302, cw, 44, l1))
    out.append(cline(x + zgap[0], 248, x + zgap[1] - 4, 248, BK, sw=1.4))
    out.append(chead(x + zgap[1], 248, 0, BK, s=8))
    out.append(xt(x + (zgap[0] + zgap[1]) / 2, 240, "ZeroMQ", fs=9))
    out.append(xchip(x + 28, 400, 564, 36, "KV cache · HBM 显存池（paged，随卡）"))
    gw = 564 / 8
    for i in range(8):
        out.append(xr(x + 28 + i * gw, 450, gw - 6, 50, sw=1.5, rx=3))
        out.append(xt(x + 28 + i * gw + (gw - 6)/2, 480, str(i), weight="bold"))
    out.append(xt(x + 310, 522, "8 × GPU · NVLink 全互联", fs=11))
    return out

parts = []
parts += machine_ex(60, "Prefill 实例 · b300-01（整机独占）",
    [(28, 190, "HTTP Server", "TokenizerManager"),
     (260, 330, "Scheduler ×8（TP rank 进程）", "waiting 队列 → 每步组 batch")],
    [(28, 240, "Model Runner · CUDA graph"), (300, 240, "Mooncake TE / NIXL（发）")],
    (218, 260))
parts += [xchip(88, 560, 270, 34, "NVMe（权重 · KV 第三层）", fs=11.5),
          xchip(380, 560, 272, 34, "主机内存 DDR（HiCache 层）", fs=11.5)]
parts += machine_ex(720, "Decode 实例 · b300-03（LWS 组代表机）",
    [(28, 300, "Scheduler ×8（TP rank 进程）", "每步全体 running 各出 1 token"),
     (360, 230, "DetokenizerManager", "增量还原文本")],
    [(28, 240, "Mooncake TE / NIXL（收）"), (300, 240, "Model Runner · CUDA graph")],
    (328, 360))
parts += [xchip(748, 560, 270, 34, "NVMe（权重）", fs=11.5),
          xchip(1040, 560, 272, 34, "主机内存 DDR（HiCache 层）", fs=11.5)]
parts += [xr(60, 750, 1280, 30, sw=2.4, rx=6), xt(700, 770, "计算网 · RDMA（IB / RoCE）", weight="bold")]

execute = parts + [
    ctext(60, 88, "① 请求送入：gateway 逐请求（HTTP，非批）→ Tokenizer 转 token ids，经 ZeroMQ 交给 Scheduler", PURPLE, fs=11.5),
    ctext(60, 106, "② 组批：Scheduler（独立进程）每步组一个 batch——连续批处理，新请求随进、完成随出", PURPLE, fs=11.5),
    ctext(60, 124, "③ 前向：CPU 下发 kernel（CUDA graph）→ GPU 计算 → 新 token ids 回传（D2H）；KV 写入 HBM", PURPLE, fs=11.5),
    ctext(60, 142, "④ KV 传输：Mooncake / NIXL 经 RDMA 直达对端 HBM（GPUDirect，不经 CPU / DDR）", PURPLE, fs=11.5),
    ctext(760, 88, "⑤ decode：同 ②③ 机制，每步全体 running 请求各生成 1 token", PURPLE, fs=11.5),
    ctext(760, 106, "⑥ detokenize（独立进程）→ SSE 流回 gateway（见请求期）", PURPLE, fs=11.5),
    ctext(760, 124, "⑦ HiCache：HBM ⇄ PCIe ⇄ DDR ⇄ NVMe，KV 分层换入换出", AUX, fs=11.5),
    cline(255, 150, 255, 216, PURPLE), chead(255, 221, DOWN, PURPLE), cnum(255, 186, 1, PURPLE),
    cline(1190, 216, 1190, 152, PURPLE), chead(1190, 147, UP, PURPLE), cnum(1190, 186, 6, PURPLE),
    cnum(455, 222, 2, PURPLE), cnum(898, 222, 5, PURPLE),
    cline(150, 348, 150, 394, PURPLE), chead(150, 399, DOWN, PURPLE),
    cline(250, 398, 250, 352, PURPLE), chead(250, 347, UP, PURPLE),
    cnum(200, 374, 3, PURPLE),
    cline(600, 324, 692, 324, PURPLE),
    cline(692, 324, 692, 745, PURPLE), chead(692, 750, DOWN, PURPLE),
    cline(708, 750, 708, 324, PURPLE), cline(708, 324, 744, 324, PURPLE),
    chead(749, 324, 0, PURPLE),
    cnum(692, 560, 4, PURPLE),
    cline(658, 438, 658, 558, AUX, sw=3.5), chead(658, 436, UP, AUX), chead(658, 560, DOWN, AUX),
    cline(378, 577, 362, 577, AUX, sw=3.5), chead(360, 577, LEFT, AUX), chead(380, 577, 0, AUX),
    cnum(658, 498, 7, AUX),
]
save("period_execute.svg", None, PURPLE, "执行期（每 token）", execute)
