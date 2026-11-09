#!/usr/bin/env python3
"""
OTTERFALL - generador de la Nutria Abismal (forma monstruosa, Fase 2).

Genera:
  - assets/otterfall/geo/otter_horror.geo.json
  - assets/otterfall/animations/otter_horror.animation.json
  - assets/otterfall/textures/entity/otter_horror.png   (1024x1024)

Uso (desde la raiz del repo):   python3 tools/generate_horror.py
Reutiliza el ruido y el empaquetador de generate_assets.py.
"""
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_assets as g  # noqa: E402

ASSETS = g.ASSETS
TEX = 1024            # la forma monstruosa usa 1024x1024 (muchos detalles pequenos: dientes, dedos)
g.TEX_SIZE = TEX
col = g.col
mix = g.mix
smooth = g.smooth
vnoise = g.vnoise

HY = 0.8          # elevacion de la cabeza/mandibula sobre el suelo
BONES = []
OPTS = {}         # nombre de cubo -> opciones (rotation, pivot, up)
rnd = random.Random(1337)


def bone(name, parent, pivot, cubes):
    BONES.append({"name": name, "parent": parent, "pivot": pivot, "cubes": cubes})


def cube(name, origin, size, zone, **opts):
    OPTS[name] = opts
    return (name, origin, size, zone)


def mx(x0, w, s):
    """Espeja una caja en X (s=-1)."""
    return x0 if s > 0 else -(x0 + w)


def spike(name, base, size, rot):
    bx, by, bz = base
    return cube(name, [bx - size[0] / 2, by, bz - size[2] / 2], size, "h_spike",
                pivot=[bx, by, bz], rotation=rot)


# ----------------------------------------------------------------------------
# MODELO
# ----------------------------------------------------------------------------
bone("root", None, [0, 6, 0], [])

bone("pelvis", "root", [0, 6, 5], [
    cube("pelvis", [-3.0, 3.4, 2.4], [6.0, 5.4, 6.2], "h_fur"),
    spike("spk_p1", [0.3, 8.7, 5.0], [1.0, 2.0, 1.0], [-15, 0, 10]),
    spike("spk_p2", [-0.9, 8.7, 7.4], [0.9, 1.7, 0.9], [20, 0, -14]),
])
bone("spine", "pelvis", [0, 8, -0.5], [
    cube("spine", [-2.7, 4.4, -3.4], [5.4, 6.4, 6.0], "h_fur"),
    spike("spk_s1", [0.0, 10.7, 0.8], [1.1, 2.4, 1.0], [-10, 0, -8]),
    spike("spk_s2", [0.8, 10.6, -1.2], [1.0, 2.0, 1.0], [-22, 0, 16]),
    spike("spk_s3", [-0.7, 10.6, -2.6], [0.9, 1.8, 0.9], [-30, 0, -20]),
])
bone("chest", "spine", [0, 7, -4.5], [
    cube("chest", [-3.2, 3.4, -9.6], [6.4, 5.8, 6.4], "h_fur"),
    spike("spk_c1", [0.2, 9.1, -5.2], [1.0, 1.9, 1.0], [-18, 0, 6]),
    spike("spk_c2", [-0.6, 9.1, -7.6], [0.9, 1.6, 0.9], [-26, 0, -10]),
])
bone("neck1", "chest", [0, 7.5, -9.2], [
    cube("neck1", [-1.7, 4.0, -13.4], [3.4, 3.9, 4.4], "h_fur"),
    spike("spk_n1", [0.0, 7.9, -10.8], [0.8, 1.5, 0.8], [-25, 0, 0]),
])
bone("neck2", "neck1", [0, 6.6, -12.8], [
    cube("neck2", [-1.5, 3.2, -17.0], [3.0, 3.4, 4.2], "h_skin"),
])

head_cubes = [
    cube("skull", [-3.2, 2.6 + HY, -22.0], [6.4, 4.2, 5.4], "h_head"),
    cube("snout", [-1.9, 2.8 + HY, -25.6], [3.8, 2.5, 3.8], "h_snout"),
    cube("nose", [-1.2, 3.9 + HY, -26.2], [2.4, 1.3, 0.7], "h_nose"),
    cube("brow_l", [0.9, 5.7 + HY, -22.3], [2.4, 0.7, 1.2], "h_brow"),
    cube("brow_r", [-3.1, 5.2 + HY, -22.3], [2.2, 0.8, 1.2], "h_brow"),
    cube("gum_u", [-1.7, 2.3 + HY, -25.4], [3.4, 0.5, 7.6], "h_gum"),
]
# dientes superiores (cuelgan de la encia): dos filas, algunos rotos o ausentes
for row, xrow in (("u_l", 1.5), ("u_r", -1.5)):
    n = 11
    z0, z1 = -25.2, -18.4
    for i in range(n):
        if rnd.random() < 0.12:
            continue
        zz = z0 + (z1 - z0) / n * i + rnd.uniform(-0.15, 0.15)
        ln = rnd.uniform(0.6, 1.3) + (0.7 if i < 2 else 0)
        w = rnd.uniform(0.28, 0.42)
        xx = xrow + rnd.uniform(-0.15, 0.15)
        base_y = 2.3 + HY
        head_cubes.append(cube(f"tooth_{row}{i}", [xx - w / 2, base_y - ln, zz], [w, ln, w], "h_tooth",
                               up=True, pivot=[xx, base_y, zz + w / 2],
                               rotation=[rnd.uniform(-10, 10), 0, rnd.uniform(-14, 14)]))
bone("head", "neck2", [0, 5.6, -16.6], head_cubes)

jaw_cubes = [
    cube("jaw", [-2.4, -0.4 + HY, -26.0], [4.8, 1.8, 8.8], "h_jaw"),
    cube("gum_l", [-2.2, 1.4 + HY, -25.8], [4.4, 0.4, 8.2], "h_gum"),
]
for row, xrow in (("l_l", 2.05), ("l_r", -2.05)):
    n = 12
    z0, z1 = -25.3, -18.2
    for i in range(n):
        if rnd.random() < 0.10:
            continue
        zz = z0 + (z1 - z0) / n * i + rnd.uniform(-0.15, 0.15)
        ln = rnd.uniform(0.6, 1.4) + (0.8 if i < 2 else 0)
        w = rnd.uniform(0.28, 0.42)
        xx = xrow + rnd.uniform(-0.15, 0.15)
        base_y = 1.8 + HY
        jaw_cubes.append(cube(f"tooth_{row}{i}", [xx - w / 2, base_y, zz], [w, ln, w], "h_tooth",
                              up=False, pivot=[xx, base_y, zz + w / 2],
                              rotation=[rnd.uniform(-10, 10), 0, rnd.uniform(-14, 14)]))
bone("jaw", "head", [0, 1.6 + HY, -17.4], jaw_cubes)

bone("ear_l", "head", [3.0, 7.4 + HY, -19.3], [
    cube("ear_l", [2.5, 7.0 + HY, -19.6], [1.4, 1.5, 0.8], "h_ear",
         pivot=[3.2, 7.0 + HY, -19.2], rotation=[0, 0, -25]),
])
bone("ear_r", "head", [-3.0, 7.4 + HY, -19.3], [
    cube("ear_r", [-3.8, 7.1 + HY, -19.8], [1.3, 2.1, 0.7], "h_ear",
         pivot=[-3.2, 7.1 + HY, -19.4], rotation=[0, 0, 22]),
])

# ---- cola irregular (5 segmentos, con pequenos desvios laterales)
bone("tail1", "pelvis", [0, 7.2, 8.2], [
    cube("tail1", [-1.4, 5.2, 8.2], [2.8, 2.6, 4.8], "h_tail"),
    spike("spk_t1", [0.2, 7.8, 10.0], [0.8, 1.4, 0.8], [-20, 0, 8]),
])
bone("tail2", "tail1", [0, 6.4, 12.8], [cube("tail2", [-1.1, 5.0, 12.6], [2.2, 2.1, 4.8], "h_tail")])
bone("tail3", "tail2", [0.3, 6.0, 17.2], [
    cube("tail3", [-0.2, 4.8, 17.0], [1.6, 1.7, 4.8], "h_tail", pivot=[0.6, 5.6, 17.0], rotation=[0, 14, 0])])
bone("tail4", "tail3", [0.7, 5.8, 21.6], [
    cube("tail4", [0.2, 4.6, 21.4], [1.1, 1.2, 4.8], "h_tailtip", pivot=[0.75, 5.2, 21.4], rotation=[0, -10, 0])])
bone("tail5", "tail4", [0.9, 5.6, 26.0], [cube("tail5", [0.5, 4.5, 25.8], [0.8, 0.9, 5.2], "h_tailtip")])


# ---- brazos largos (asimetricos: el derecho es mas corto, con 4 dedos)
def arm(s, up_len, fore_len, finger_lens):
    n = "l" if s > 0 else "r"
    elbow_y = 8.2 - up_len
    bone(f"arm_{n}", "chest", [s * 3.9, 8.2, -6.0], [
        cube(f"arm_{n}_u", [mx(3.1, 1.9, s), elbow_y - 0.1, -7.0], [1.9, up_len + 0.1, 2.0], "h_fur"),
    ])
    bone(f"forearm_{n}", f"arm_{n}", [s * 4.05, elbow_y, -6.0], [
        cube(f"farm_{n}", [mx(3.4, 1.5, s), 0.5, -6.8], [1.5, elbow_y + 0.1 - 0.5, 1.6], "h_skin"),
    ])
    cubes = [cube(f"palm_{n}", [mx(3.2, 1.9, s), 0.0, -7.5], [1.9, 0.8, 2.5], "h_skin")]
    k_n = len(finger_lens)
    for k, fl in enumerate(finger_lens):
        x0 = 3.2 + k * (1.9 - 0.38) / (k_n - 1)
        xo = mx(x0, 0.38, s)
        xc = xo + 0.19
        ry = (k - (k_n - 1) / 2) * 8 * s
        rx = rnd.uniform(-6, 6)
        cubes.append(cube(f"{n}_f{k}", [xo, 0.05, -7.5 - fl], [0.38, 0.4, fl], "h_finger",
                          pivot=[xc, 0.25, -7.5], rotation=[rx, ry, 0]))
        cubes.append(cube(f"{n}_c{k}", [xo, 0.05, -7.5 - fl - 1.2], [0.38, 0.36, 1.25], "h_claw",
                          pivot=[xc, 0.25, -7.5], rotation=[rx, ry, 0]))
    bone(f"hand_{n}", f"forearm_{n}", [s * 4.1, 0.9, -6.1], cubes)


arm(+1, 5.0, 2.7, [3.4, 4.2, 4.6, 4.0, 3.0])
arm(-1, 4.4, 3.3, [3.6, 4.4, 4.0, 3.2])


# ---- patas traseras digitigradas
def leg(s, shin_len, toe_lens):
    n = "l" if s > 0 else "r"
    bone(f"thigh_{n}", "pelvis", [s * 3.5, 8.0, 6.4], [
        cube(f"thigh_{n}", [mx(2.9, 2.4, s), 4.0, 5.2], [2.4, 4.6, 3.4], "h_fur"),
    ])
    bone(f"shin_{n}", f"thigh_{n}", [s * 3.7, 4.2, 7.4], [
        cube(f"shin_{n}", [mx(3.1, 1.6, s), 4.2 - shin_len, 7.0], [1.6, shin_len, 1.8], "h_skin"),
    ])
    cubes = [cube(f"sole_{n}", [mx(3.0, 1.9, s), 0.0, 5.6], [1.9, 0.8, 3.0], "h_skin")]
    k_n = len(toe_lens)
    for k, tl in enumerate(toe_lens):
        x0 = 3.0 + k * (1.9 - 0.45) / (k_n - 1)
        xo = mx(x0, 0.45, s)
        xc = xo + 0.225
        ry = (k - (k_n - 1) / 2) * 9 * s
        cubes.append(cube(f"{n}_t{k}", [xo, 0.05, 5.6 - tl], [0.45, 0.4, tl], "h_finger",
                          pivot=[xc, 0.25, 5.6], rotation=[0, ry, 0]))
        cubes.append(cube(f"{n}_tc{k}", [xo, 0.05, 5.6 - tl - 1.1], [0.45, 0.36, 1.15], "h_claw",
                          pivot=[xc, 0.25, 5.6], rotation=[0, ry, 0]))
    bone(f"foot_{n}", f"shin_{n}", [s * 3.9, 0.9, 8.0], cubes)


leg(+1, 3.4, [3.6, 4.2, 3.4])
leg(-1, 4.0, [3.4, 4.4, 4.0, 3.0])


# ----------------------------------------------------------------------------
# COLOR
# ----------------------------------------------------------------------------
F_DARK = col(17, 16, 19)
F_MID = col(38, 34, 38)
SKIN = col(100, 84, 90)
SKIN_D = col(58, 44, 52)
DIRT = col(70, 54, 40)
GUM = col(92, 26, 38)
TOOTH = col(216, 204, 166)
TOOTH_ST = col(152, 118, 76)


def skin_tex(P, seed):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    n = vnoise(x * 22, y * 22, z * 22, seed + 50)
    base = mix(SKIN, SKIN_D, vnoise(x * 2.4, y * 2.4, z * 2.4, seed + 51))
    c = base * (0.62 + 0.6 * n)[..., None]
    vein = np.abs(vnoise(x * 8, y * 8, z * 8, seed + 52) - 0.5) < 0.035
    c = np.where(vein[..., None], col(70, 36, 56), c)
    scab = vnoise(x * 13, y * 13, z * 13, seed + 53) > 0.83
    c = np.where(scab[..., None], col(96, 38, 34), c)
    return c


def hfur(P, seed, bare=0.0):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    fine, clump, patch = g.fur_strands(P, seed, stretch=2.6)
    base = mix(F_DARK, F_MID, smooth(0.25, 0.8, patch))
    c = base * ((0.45 + 1.1 * fine) * (0.8 + 0.4 * clump))[..., None]
    ridge = np.abs(vnoise(x * 7, y * 7, z * 1.6, seed + 40) - 0.5) * 2
    c = np.where(((ridge < 0.10) & (fine > 0.45))[..., None], c + col(26, 30, 40), c)
    dirt = vnoise(x * 1.7, y * 1.7, z * 1.4, seed + 20)
    c = mix(c, DIRT * (0.5 + 0.9 * fine)[..., None], smooth(0.58, 0.72, dirt) * 0.7)
    skin_mask = smooth(0.64, 0.7, vnoise(x * 1.2 + 5, y * 1.2, z * 1.0, seed + 30) + bare)
    return mix(c, skin_tex(P, seed), skin_mask)


def horror_color(zone, P, N, fu, fv, seed, cname, origin, size, opts):
    nx, ny, nz = N
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    ox, oy, oz = origin
    sx, sy, sz = size
    if zone == "h_fur":
        c = hfur(P, seed)
    elif zone == "h_skin":
        c = mix(skin_tex(P, seed), hfur(P, seed), 0.25 * vnoise(x * 1.5, y * 1.5, z * 1.5, seed + 9))
    elif zone == "h_head":
        c = hfur(P, seed, bare=0.08)
        face = smooth(-19, -22, z)
        c = mix(c, skin_tex(P, seed), face * 0.5)
        if cname == "skull" and nz < -0.5:
            for (cx, cy, r, glint) in ((2.4, 5.9 + HY, 0.78, True), (-2.4, 5.0 + HY, 0.55, False)):
                d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
                ring = smooth(1.9, 1.0, d)
                c = mix(c, col(44, 26, 36), ring * 0.8)
                c = np.where((d < 1.0)[..., None], col(6, 5, 7), c)
                if glint:
                    dg = np.sqrt((x - (cx + 0.15)) ** 2 + (y - (cy + 0.12)) ** 2) / 0.17
                    c = np.where((dg < 1.0)[..., None], col(198, 194, 160), c)
    elif zone == "h_snout":
        if ny < -0.5:
            ridge = 0.5 + 0.5 * np.sin(z * 9)
            c = mix(col(120, 46, 56), col(66, 18, 28), ridge)
            c = c * (0.7 + 0.5 * vnoise(x * 14, y * 14, z * 14, seed))[..., None]
        else:
            c = mix(skin_tex(P, seed), hfur(P, seed), 0.3)
    elif zone == "h_nose":
        n = vnoise(x * 18, y * 18, z * 18, seed)
        c = np.broadcast_to(col(14, 12, 15), P.shape).copy() + (n - 0.5)[..., None] * 10
        if ny > 0.5:
            gx = 1 - np.clip(np.abs(fu - 0.5) * 2.2, 0, 1)
            gy = 1 - np.clip(np.abs(fv - 0.5) * 2.2, 0, 1)
            c = mix(c, col(130, 142, 160), np.clip((gx * gy) ** 1.4 * 0.7, 0, 1))
        if nz < -0.5:
            for cx in (0.28, 0.72):
                d = ((fu - cx) / 0.2) ** 2 + ((fv - 0.5) / 0.28) ** 2
                c = np.where((d < 1)[..., None], col(4, 3, 4), c)
    elif zone == "h_jaw":
        if ny > 0.5:
            n = vnoise(x * 6, y * 6, z * 6, seed)
            c = mix(col(64, 14, 22), col(30, 6, 12), n)
            c = c * (0.7 + 0.6 * vnoise(x * 20, y * 20, z * 20, seed + 1))[..., None]
        else:
            c = mix(skin_tex(P, seed), hfur(P, seed, bare=0.1), 0.45)
    elif zone == "h_gum":
        n = vnoise(x * 9, y * 9, z * 9, seed)
        c = mix(GUM, col(52, 12, 22), n) * (0.75 + 0.5 * vnoise(x * 24, y * 24, z * 24, seed + 3))[..., None]
        vein = np.abs(vnoise(x * 12, y * 12, z * 12, seed + 4) - 0.5) < 0.04
        c = np.where(vein[..., None], col(54, 10, 20), c)
    elif zone == "h_tooth":
        up = opts.get("up", False)
        ry = np.clip((y - oy) / sy, 0, 1)
        root = ry if up else 1 - ry
        stain = vnoise(x * 16, y * 16, z * 16, seed)
        c = mix(TOOTH, TOOTH_ST, np.clip(root ** 1.5 * 0.9 + stain * 0.35, 0, 1))
        c = mix(c, GUM * 0.8, smooth(0.78, 0.97, root))
        crack = np.abs(vnoise(x * 30, y * 8, z * 30, seed + 5) - 0.5) < 0.03
        c = np.where(crack[..., None], c * 0.55, c)
    elif zone == "h_claw":
        tip = np.clip(1 - (z - oz) / sz, 0, 1)
        c = mix(col(78, 68, 58), col(12, 10, 10), tip)
        c = c * (0.8 + 0.4 * vnoise(x * 20, y * 20, z * 20, seed))[..., None]
    elif zone == "h_finger":
        c = skin_tex(P, seed) * 0.9
        knuckle = (z * 2.2 - np.floor(z * 2.2)) < 0.14
        c = np.where(knuckle[..., None], col(40, 26, 34), c)
    elif zone in ("h_tail", "h_tailtip"):
        along = np.clip((z - 8.2) / 22, 0, 1)
        c = mix(hfur(P, seed), skin_tex(P, seed), smooth(0.25, 0.8, along) if zone == "h_tail" else along * 0 + 0.9)
        ring = (z * 1.3 - np.floor(z * 1.3)) < 0.08
        c = np.where((ring & (along > 0.3))[..., None], c * 0.6, c)
        if zone == "h_tailtip":
            c = mix(c, col(140, 126, 110), smooth(0.8, 1.0, along) * 0.6)
    elif zone == "h_ear":
        c = hfur(P, seed) * 0.9
        if abs(nz) > 0.5:
            r = np.sqrt(((fu - 0.5) / 0.5) ** 2 + ((fv - 0.55) / 0.5) ** 2)
            c = mix(c, col(118, 84, 90), smooth(0.85, 0.2, r) * 0.85)
    elif zone == "h_spike":
        ry = np.clip((y - oy) / max(sy, 0.01), 0, 1)
        c = mix(F_DARK * 1.2, col(92, 84, 86), ry ** 2)
        c = c * (0.6 + 0.9 * vnoise(x * 18, y * 6, z * 18, seed))[..., None]
    elif zone == "h_brow":
        c = mix(skin_tex(P, seed), col(30, 24, 28), 0.4)
        wr = 0.7 + 0.4 * np.sin(x * 9 + y * 3)
        c = c * wr[..., None]
    else:
        c = np.broadcast_to(col(255, 0, 255), P.shape).copy()
    if ny < -0.5:
        c = c * 0.7
    return np.clip(c, 0, 255)


def alpha_for(zone, cname, N, fu, fv, seed):
    a = np.full(fu.shape, 255, dtype=np.uint8)
    if zone == "h_ear" and abs(N[2]) > 0.5:
        n = vnoise(fu * 6, fv * 6, np.zeros_like(fu), seed + 70)
        if cname == "ear_l":      # oreja desgarrada
            torn = ((fu > 0.45) & (fv < 0.5) & (n > 0.3)) | (n > 0.82) | (fv < 0.12 + 0.25 * n) & (fu > 0.6)
        else:                     # pequena muesca
            torn = (fu > 0.7) & (fv < 0.3) & (n > 0.45)
        a = np.where(torn, 0, a).astype(np.uint8)
    return a


# ----------------------------------------------------------------------------
# TEXTURA + GEO
# ----------------------------------------------------------------------------

def build():
    g.BONES = BONES
    density, layout = g.best_layout()
    print(f"[horror] densidad de textura: {density} px/unidad ({TEX}x{TEX}), caras: {len(layout)}")
    img = np.zeros((TEX, TEX, 4), dtype=np.uint8)
    geo_bones = []
    for b in BONES:
        gb = {"name": b["name"], "pivot": b["pivot"]}
        if b["parent"]:
            gb["parent"] = b["parent"]
        cubes = []
        for (cname, origin, size, zone) in b["cubes"]:
            opts = OPTS.get(cname, {})
            seed = (sum(ord(ch) for ch in cname) % 60) + 1
            uv = {}
            for f in g.FACES:
                (u0, v0, pw, ph) = layout[(cname, f)]
                jj, ii = np.mgrid[0:ph, 0:pw]
                fu = (ii + 0.5) / pw
                fv = (jj + 0.5) / ph
                px, py, pz, normal = g.face_points(origin, size, f, fu, fv)
                P = np.stack([px, py, pz], axis=-1)
                rgb = horror_color(zone, P, normal, fu, fv, seed, cname, origin, size, opts)
                al = alpha_for(zone, cname, normal, fu, fv, seed)
                img[v0:v0 + ph, u0:u0 + pw, :3] = rgb.astype(np.uint8)
                img[v0:v0 + ph, u0:u0 + pw, 3] = al
                img[v0 - 1, u0:u0 + pw] = img[v0, u0:u0 + pw]
                img[v0 + ph, u0:u0 + pw] = img[v0 + ph - 1, u0:u0 + pw]
                img[v0:v0 + ph, u0 - 1] = img[v0:v0 + ph, u0]
                img[v0:v0 + ph, u0 + pw] = img[v0:v0 + ph, u0 + pw - 1]
                uv[f] = {"uv": [u0, v0], "uv_size": [pw, ph]}
            cj = {"origin": origin, "size": size, "uv": uv}
            if "rotation" in opts:
                cj["pivot"] = opts["pivot"]
                cj["rotation"] = opts["rotation"]
            cubes.append(cj)
        if cubes:
            gb["cubes"] = cubes
        geo_bones.append(gb)
    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.otter_horror",
                "texture_width": TEX,
                "texture_height": TEX,
                "visible_bounds_width": 6,
                "visible_bounds_height": 4,
                "visible_bounds_offset": [0, 1.0, 0],
            },
            "bones": geo_bones,
        }],
    }
    return img, geo


# ----------------------------------------------------------------------------
# ANIMACIONES
# Convencion: rotacion X positiva = el frente (-Z) baja (las puntas de las
# extremidades colgantes se van hacia atras).
# ----------------------------------------------------------------------------
TAU = g.TAU
s = g.s
SM = g.smooth


def sstep(a, b, t):
    return float(SM(a, b, t))


BASE = {
    "arm_l": [-12, 0, 0], "arm_r": [-12, 0, 0],
    "forearm_l": [6, 0, 0], "forearm_r": [6, 0, 0],
    "hand_l": [8, 0, 0], "hand_r": [8, 0, 0],
    "thigh_l": [-14, 0, 0], "thigh_r": [-14, 0, 0],
    "shin_l": [24, 0, 0], "shin_r": [24, 0, 0],
    "foot_l": [-10, 0, 0], "foot_r": [-10, 0, 0],
    "neck1": [8, 0, 0], "neck2": [10, 0, 0], "head": [-10, 0, 0],
}


def R(a, bone_name, fn):
    """Rotacion relativa a la postura base."""
    b = BASE.get(bone_name, [0, 0, 0])

    def f(t):
        d = fn(t)
        return [b[0] + d[0], b[1] + d[1], b[2] + d[2]]
    a.rot(bone_name, f)


def finish(a):
    for name, v in BASE.items():
        if "rotation" not in a.bones.get(name, {}):
            a.rot(name, lambda t, v=v: v)
    return a


def tail5(a, period, amp_y, amp_x, lag=0.5, base_x=0.0, bias=0.0):
    for i, name in enumerate(("tail1", "tail2", "tail3", "tail4", "tail5")):
        k = i + 1
        a.rot(name, lambda t, k=k: [base_x + amp_x * (0.6 + 0.3 * k) * s(t, period, -lag * k),
                                    bias + amp_y * (0.5 + 0.25 * k) * s(t, period, -lag * k), 0])


def make_animations():
    P = "animation.otter_horror."
    A = {}

    # ---- idle: respiracion humeda, mandibula entreabierta, cabeza ladeada
    L = 4.0
    a = g.Anim(L, dt=0.1)
    a.rot("spine", lambda t: [1.2 * s(t, 2.0), 0, 0])
    a.rot("chest", lambda t: [1.6 * s(t, 2.0, 0.5), 2 * s(t, L), 0])
    R(a, "neck1", lambda t: [2 * s(t, L, 0.3), 6 * s(t, L), 0])
    R(a, "neck2", lambda t: [2 * s(t, L, 0.8), 8 * s(t, L, 0.3), 0])
    R(a, "head", lambda t: [3 * s(t, L, 1.0), 10 * s(t, L, 0.5) + 4 * s(t, L / 2), 5 * s(t, L, 2.0)])
    a.rot("jaw", lambda t: [6 + 3 * s(t, 2.0, 0.8), 0, 0])
    a.rot("ear_l", lambda t: [0, 0, 8 * max(0, s(t, L / 2, 1.2))])
    a.rot("ear_r", lambda t: [0, 0, -6 * max(0, s(t, L / 2, 2.4))])
    R(a, "hand_l", lambda t: [3 * s(t, L / 2), 0, 0])
    tail5(a, L, 7, 2, lag=0.45)
    A[P + "idle"] = finish(a)

    # ---- crawl: cuerpo bajo, la cabeza gira antes que el cuerpo, una pata trasera se arrastra
    L = 1.2
    a = g.Anim(L)
    R(a, "arm_l", lambda t: [-26 * s(t, L), 0, 0])
    R(a, "arm_r", lambda t: [-15 * s(t, L, math.pi), 0, 0])
    R(a, "forearm_l", lambda t: [10 * max(0, s(t, L, 0.8)), 0, 0])
    R(a, "forearm_r", lambda t: [6 * s(t, L, math.pi + 0.8), 0, 0])
    R(a, "hand_l", lambda t: [-10 * s(t, L, 1.2), 0, 0])
    R(a, "thigh_r", lambda t: [-22 * s(t, L), 0, 0])
    R(a, "thigh_l", lambda t: [-8 * s(t, L, math.pi), 0, 0])        # esta pata se arrastra
    R(a, "shin_r", lambda t: [18 * max(0, s(t, L, 0.9)), 0, 0])
    R(a, "shin_l", lambda t: [4 * s(t, L, math.pi + 0.9), 0, 0])
    R(a, "foot_l", lambda t: [-12 * max(0, s(t, L, math.pi + 1.5)), 0, 0])
    a.pos("arm_l", lambda t: [0, 0.6 * max(0, math.cos(TAU * t / L)), 0])
    a.pos("thigh_r", lambda t: [0, 0.6 * max(0, math.cos(TAU * t / L)), 0])
    a.rot("spine", lambda t: [2 * s(t, L / 2, 0.5), 7 * s(t, L), 0])
    a.rot("chest", lambda t: [0, -9 * s(t, L, 0.4), 0])
    a.rot("pelvis", lambda t: [0, 5 * s(t, L, math.pi), 0])
    R(a, "neck1", lambda t: [0, -8 * s(t, L, -0.9), 0])
    R(a, "neck2", lambda t: [0, -10 * s(t, L, -1.2), 0])
    R(a, "head", lambda t: [3 * s(t, L / 2, 2.0), -12 * s(t, L, -1.5), 0])
    a.rot("jaw", lambda t: [8 + 3 * s(t, L / 2), 0, 0])
    a.pos("pelvis", lambda t: [0, 0.12 * s(t, L / 2), 0])
    tail5(a, L, 14, 2, lag=0.55)
    A[P + "crawl"] = finish(a)

    # ---- run: sprint con las cuatro extremidades, cuerpo estirado
    L = 0.55
    a = g.Anim(L, dt=0.025)
    R(a, "arm_l", lambda t: [-8 + 50 * s(t, L), 0, 0])
    R(a, "arm_r", lambda t: [-8 + 50 * s(t, L, 0.5), 0, 0])
    R(a, "forearm_l", lambda t: [14 * max(0, s(t, L, 0.9)), 0, 0])
    R(a, "forearm_r", lambda t: [14 * max(0, s(t, L, 1.4)), 0, 0])
    R(a, "thigh_l", lambda t: [45 * s(t, L, 1.9), 0, 0])
    R(a, "thigh_r", lambda t: [45 * s(t, L, 2.1), 0, 0])
    R(a, "shin_l", lambda t: [30 * max(0, s(t, L, 2.8)), 0, 0])
    R(a, "shin_r", lambda t: [30 * max(0, s(t, L, 3.0)), 0, 0])
    a.pos("arm_l", lambda t: [0, 0.8 * max(0, math.cos(TAU * t / L)), 0])
    a.pos("arm_r", lambda t: [0, 0.8 * max(0, math.cos(TAU * t / L + 0.5)), 0])
    a.pos("thigh_l", lambda t: [0, 0.8 * max(0, math.cos(TAU * t / L + 1.9)), 0])
    a.pos("thigh_r", lambda t: [0, 0.8 * max(0, math.cos(TAU * t / L + 2.1)), 0])
    a.rot("spine", lambda t: [10 * s(t, L, 0.6), 0, 0])
    a.rot("pelvis", lambda t: [-4 * s(t, L, 0.6), 0, 0])
    a.rot("chest", lambda t: [6 * s(t, L, 1.8), 0, 0])
    R(a, "neck1", lambda t: [4, 0, 0])
    R(a, "neck2", lambda t: [6 * s(t, L, 2.4), 0, 0])
    R(a, "head", lambda t: [-4 * s(t, L, 2.4), 0, 0])
    a.rot("jaw", lambda t: [26 + 6 * s(t, L / 2), 0, 0])
    a.pos("pelvis", lambda t: [0, 0.9 * max(0, s(t, L, 1.0)), 0])
    tail5(a, L, 8, 5, lag=0.35, base_x=8)
    A[P + "run"] = finish(a)

    # ---- swim
    L = 1.2
    a = g.Anim(L)
    a.rot("arm_l", lambda t: [60 + 10 * s(t, L), 0, 0])
    a.rot("arm_r", lambda t: [60 + 10 * s(t, L, 0.6), 0, 0])
    a.rot("forearm_l", lambda t: [0, 0, 0])
    a.rot("forearm_r", lambda t: [0, 0, 0])
    a.rot("hand_l", lambda t: [10, 0, 0])
    a.rot("hand_r", lambda t: [10, 0, 0])
    a.rot("thigh_l", lambda t: [30 + 18 * s(t, L, math.pi), 0, 0])
    a.rot("thigh_r", lambda t: [30 + 18 * s(t, L), 0, 0])
    a.rot("shin_l", lambda t: [10, 0, 0])
    a.rot("shin_r", lambda t: [10, 0, 0])
    a.rot("foot_l", lambda t: [0, 0, 0])
    a.rot("foot_r", lambda t: [0, 0, 0])
    a.rot("spine", lambda t: [9 * s(t, L), 0, 0])
    a.rot("chest", lambda t: [5 * s(t, L, -0.7), 0, 0])
    a.rot("neck1", lambda t: [4, 6 * s(t, L, -1.0), 0])
    a.rot("neck2", lambda t: [4, 8 * s(t, L, -1.3), 0])
    a.rot("head", lambda t: [-4, 0, 0])
    a.rot("jaw", lambda t: [14, 0, 0])
    a.pos("pelvis", lambda t: [0, -0.5 + 0.3 * s(t, L, 0.5), 0])
    tail5(a, L, 24, 10, lag=0.55)
    A[P + "swim"] = a

    # ---- swim_idle
    L = 3.0
    a = g.Anim(L, dt=0.1)
    a.rot("arm_l", lambda t: [40 + 8 * s(t, L), 0, 0])
    a.rot("arm_r", lambda t: [40 + 8 * s(t, L, 1.2), 0, 0])
    a.rot("hand_l", lambda t: [10, 0, 0])
    a.rot("hand_r", lambda t: [10, 0, 0])
    a.rot("thigh_l", lambda t: [25 + 8 * s(t, L, 2), 0, 0])
    a.rot("thigh_r", lambda t: [25 + 8 * s(t, L), 0, 0])
    a.rot("spine", lambda t: [3 * s(t, L), 0, 0])
    a.rot("neck1", lambda t: [4, 6 * s(t, L), 0])
    a.rot("head", lambda t: [-6, 8 * s(t, L, 1.0), 0])
    a.rot("jaw", lambda t: [8 + 3 * s(t, L / 2), 0, 0])
    a.pos("pelvis", lambda t: [0, -0.5 + 0.2 * s(t, L), 0])
    tail5(a, L, 12, 4, lag=0.5)
    A[P + "swim_idle"] = a

    # ---- still: inmovil, cabeza ligeramente alzada, mandibula entreabierta
    L = 4.0
    a = g.Anim(L, dt=0.2)
    R(a, "head", lambda t: [-14 + 0.4 * s(t, L), 0, 0])
    R(a, "neck1", lambda t: [-6, 0, 0])
    R(a, "neck2", lambda t: [-4, 0, 0])
    a.rot("jaw", lambda t: [12 + 0.4 * s(t, L), 0, 0])
    A[P + "still"] = finish(a)

    # ---- rise: levanta la cabeza muy despacio y la mantiene
    L = 6.0
    a = g.Anim(L, dt=0.1)

    def rp(t):
        return sstep(0, 3.5, t) * (1 - sstep(5.0, 6.0, t))
    R(a, "head", lambda t: [-40 * rp(t), 6 * s(t, 1.5) * rp(t), 0])
    R(a, "neck1", lambda t: [-16 * rp(t), 0, 0])
    R(a, "neck2", lambda t: [-14 * rp(t), 0, 0])
    a.rot("chest", lambda t: [-10 * rp(t), 0, 0])
    R(a, "arm_l", lambda t: [-22 * rp(t), 0, 0])
    R(a, "arm_r", lambda t: [-22 * rp(t), 0, 0])
    a.rot("jaw", lambda t: [4 + 14 * rp(t), 0, 0])
    A[P + "rise"] = finish(a)

    # ---- jaw: abre la mandibula exageradamente, tiembla y cierra de golpe
    L = 2.0
    a = g.Anim(L, dt=0.025)

    def op(t):
        return sstep(0.0, 0.35, t) * (1 - sstep(1.4, 1.55, t))
    a.rot("jaw", lambda t: [4 + 66 * op(t) + 3 * math.sin(TAU * 18 * t) * op(t), 0, 0])
    R(a, "head", lambda t: [-14 * op(t), 0, 0])
    R(a, "neck1", lambda t: [-8 * op(t), 0, 0])
    R(a, "neck2", lambda t: [-6 * op(t), 0, 0])
    a.rot("chest", lambda t: [-6 * op(t), 0, 0])
    a.rot("ear_l", lambda t: [0, 0, 10 * op(t)])
    A[P + "jaw"] = finish(a)

    # ---- spasm: sacudidas violentas e irregulares
    L = 1.0
    a = g.Anim(L, dt=0.02)

    def env(t):
        return 1.0 if (t < 0.35 or 0.55 < t < 0.8) else 0.15

    def n1(t):
        return s(t, 0.13) + 0.6 * s(t, 0.21, 1) + 0.4 * s(t, 0.07, 2)

    def n2(t):
        return s(t, 0.11, 0.5) + 0.7 * s(t, 0.17, 2) + 0.3 * s(t, 0.06, 1)

    def n3(t):
        return s(t, 0.09, 1.3) + 0.5 * s(t, 0.19, 0.2)
    R(a, "head", lambda t: [12 * n2(t) * env(t), 28 * n1(t) * env(t), 8 * n3(t) * env(t)])
    R(a, "neck1", lambda t: [6 * n3(t) * env(t), 14 * n2(t) * env(t), 0])
    a.rot("spine", lambda t: [4 * n2(t) * env(t), 0, 14 * n1(t) * env(t)])
    a.rot("chest", lambda t: [0, 10 * n2(t) * env(t), 8 * n3(t) * env(t)])
    R(a, "arm_l", lambda t: [30 * n3(t) * env(t), 0, 0])
    R(a, "arm_r", lambda t: [-24 * n1(t) * env(t), 0, 0])
    R(a, "thigh_r", lambda t: [40 * max(0, n2(t)) * env(t), 0, 0])
    a.rot("jaw", lambda t: [20 + 20 * max(0, n3(t)) * env(t), 0, 0])
    tail5(a, 0.35, 30, 6, lag=0.3)
    A[P + "spasm"] = finish(a)

    # ---- bite: embestida con mordisco
    L = 0.6
    a = g.Anim(L, dt=0.02)

    def bp(t):
        return sstep(0, 0.15, t) * (1 - sstep(0.35, 0.6, t))

    def jo(t):
        return sstep(0.05, 0.18, t) * (1 - sstep(0.28, 0.34, t))
    R(a, "neck1", lambda t: [28 * bp(t), 0, 0])
    R(a, "neck2", lambda t: [20 * bp(t), 0, 0])
    R(a, "head", lambda t: [15 * bp(t), 0, 0])
    a.rot("jaw", lambda t: [6 + 62 * jo(t), 0, 0])
    a.rot("chest", lambda t: [12 * bp(t), 0, 0])
    a.rot("pelvis", lambda t: [-8 * bp(t), 0, 0])
    R(a, "arm_l", lambda t: [-45 * bp(t), 0, 0])
    R(a, "arm_r", lambda t: [-38 * sstep(0.1, 0.3, t) * (1 - sstep(0.4, 0.6, t)), 0, 0])
    tail5(a, L, 5, 3, lag=0.4, base_x=6)
    A[P + "bite"] = finish(a)

    return {"format_version": "1.8.0", "animations": {k: v.to_json() for k, v in A.items()}}


def main():
    img, geo = build()
    Image.fromarray(img, "RGBA").save(os.path.join(ASSETS, "textures", "entity", "otter_horror.png"), optimize=True)
    with open(os.path.join(ASSETS, "geo", "otter_horror.geo.json"), "w") as f:
        json.dump(geo, f, indent=1)
    with open(os.path.join(ASSETS, "animations", "otter_horror.animation.json"), "w") as f:
        json.dump(make_animations(), f, separators=(",", ":"))
    print("OK")


if __name__ == "__main__":
    main()
