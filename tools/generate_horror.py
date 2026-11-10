#!/usr/bin/env python3
"""
OTTERFALL - generador de la Nutria Abismal (forma monstruosa, version gigante).

Criatura de ~4 bloques de alto y ~3 de ancho (limbos abiertos), a cuatro patas,
espalda arqueada con espinas de hueso, torso costillar, brazos larguisimos,
mandibula goteando, pelo de alambre en la cabeza y ojos rojos brillantes.

Genera:
  - assets/otterfall/geo/otter_horror.geo.json
  - assets/otterfall/animations/otter_horror.animation.json
  - assets/otterfall/textures/entity/otter_horror.png            (2048x2048)
  - assets/otterfall/textures/entity/otter_horror_glowmask.png   (zonas que brillan)

Uso (desde la raiz del repo):   python3 tools/generate_horror.py
Reutiliza el ruido y el empaquetador de generate_assets.py. Tarda ~1 minuto.
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
TEX = 2048            # criatura de 4 bloques: 2048 esta justificado
g.TEX_SIZE = TEX
col = g.col
mix = g.mix
smooth = g.smooth
vnoise = g.vnoise

BONES = []
OPTS = {}
rnd = random.Random(2024)


def bone(name, parent, pivot, cubes):
    BONES.append({"name": name, "parent": parent, "pivot": pivot, "cubes": cubes})


def cube(name, origin, size, zone, **opts):
    OPTS[name] = opts
    return (name, origin, size, zone)


def mx(x0, w, s):
    return x0 if s > 0 else -(x0 + w)


def spike(name, base, size, rot, zone="h_bone"):
    bx, by, bz = base
    return cube(name, [bx - size[0] / 2, by, bz - size[2] / 2], size, zone,
                pivot=[bx, by, bz], rotation=rot)


# ----------------------------------------------------------------------------
# MODELO  (1 unidad = 1/16 de bloque; frente hacia -Z)
# ----------------------------------------------------------------------------
bone("root", None, [0, 0, 0], [])   # pivote en el suelo: la escala crece desde el piso

# ---------------- cadera
pelvis_cubes = [
    cube("pelvis", [-10, 26, 12], [20, 24, 20], "h_torso"),
    spike("spk_p1", [3, 50, 20], [2.4, 9, 2.4], [-12, 0, 8]),
    spike("spk_p2", [-4, 50, 26], [2.2, 8, 2.2], [14, 0, -10]),
    cube("boil_p", [10, 34, 22], [1.8, 6, 6], "h_wound"),
]
bone("pelvis", "root", [0, 40, 22], pelvis_cubes)

# ---------------- abdomen
spine_cubes = [cube("abdomen", [-8.5, 24, -6], [17, 24, 20], "h_torso")]
for i in range(5):
    y = 27 + i * 4.2
    spine_cubes.append(cube(f"rib_a_l{i}", [8.2, y, -4], [2.8, 2.0, 15], "h_rib"))
    spine_cubes.append(cube(f"rib_a_r{i}", [-11.0, y, -4], [2.8, 2.0, 15], "h_rib"))
bone("spine", "pelvis", [0, 40, 6], spine_cubes)

# ---------------- torax
chest_cubes = [
    cube("chest", [-11, 26, -26], [22, 26, 22], "h_torso"),
    cube("hump", [-8, 52, -22], [16, 5, 14], "h_torso"),
    cube("boil_c", [-12.8, 38, -20], [1.8, 6, 6], "h_wound"),
    spike("spk_h1", [0, 57, -12], [2.6, 10, 2.6], [-8, 0, 4]),
    spike("spk_h2", [4.5, 57, -17], [2.4, 8.5, 2.4], [-14, 0, 16]),
    spike("spk_h3", [-4.5, 57, -17], [2.4, 9, 2.4], [-10, 0, -18]),
    spike("spk_h4", [0, 57, -21], [2.2, 7, 2.2], [-24, 0, 0]),
    spike("spk_c1", [11, 46, -20], [2.2, 7, 2.2], [0, 0, 55]),
    spike("spk_c2", [-11, 44, -16], [2.2, 6.5, 2.2], [0, 0, -60]),
    spike("spk_c3", [11, 34, -12], [2, 6, 2], [0, 0, 70]),
]
for i in range(5):
    y = 29 + i * 4.4
    chest_cubes.append(cube(f"rib_c_l{i}", [10.6, y, -24], [2.8, 2.0, 18], "h_rib"))
    chest_cubes.append(cube(f"rib_c_r{i}", [-13.4, y, -24], [2.8, 2.0, 18], "h_rib"))
bone("chest", "spine", [0, 44, -10], chest_cubes)

# ---------------- cuello
bone("neck1", "chest", [0, 46, -24], [
    cube("neck1", [-7, 34, -38], [14, 14, 16], "h_limb"),
    spike("spk_n1", [0, 48, -30], [2.2, 8, 2.2], [-20, 0, 0]),
    spike("spk_n2", [4, 47, -34], [2, 6, 2], [-30, 0, 20]),
])
bone("neck2", "neck1", [0, 40, -36], [cube("neck2", [-6.5, 26, -46], [13, 14, 12], "h_limb")])

# ---------------- cabeza
head_cubes = [
    cube("skull", [-10, 22, -58], [20, 15, 15], "h_head"),
    cube("snout", [-5.5, 23.5, -66], [11, 8.5, 8.5], "h_snout"),
    cube("nose", [-3.5, 29, -67.2], [7, 3, 1.6], "h_nose"),
    cube("brow_l", [5.5, 33, -59.5], [5, 2.5, 3.5], "h_brow"),
    cube("brow_r", [-9.5, 32, -59.5], [4.5, 2.8, 3.5], "h_brow"),
    cube("eye_l", [6.2, 28.4, -59.8], [3.6, 4.0, 1.5], "h_eye"),
    cube("eye_r", [-9.4, 27.6, -59.6], [3.0, 3.2, 1.3], "h_eye"),
    cube("gum_u", [-5, 21, -65.5], [10, 2.4, 21], "h_gum"),
    spike("spk_hd1", [6, 37, -50], [2.2, 7, 2.2], [-18, 0, 26]),
    spike("spk_hd2", [-6, 37, -49], [2.2, 8, 2.2], [-22, 0, -24]),
    spike("spk_hd3", [9, 33, -52], [2, 6, 2], [0, 0, 62]),
    spike("spk_hd4", [-9.5, 32, -53], [2, 5.5, 2], [0, 0, -66]),
]
for row, xrow in (("u_l", 3.8), ("u_r", -3.8)):
    n = 10
    z0, z1 = -64.0, -47.0
    for i in range(n):
        if rnd.random() < 0.12:
            continue
        zz = z0 + (z1 - z0) / n * i + rnd.uniform(-0.4, 0.4)
        ln = rnd.uniform(3.5, 7.5) + (3.0 if i < 2 else 0)
        w = rnd.uniform(1.2, 1.9)
        xx = xrow + rnd.uniform(-0.5, 0.5)
        head_cubes.append(cube(f"tooth_{row}{i}", [xx - w / 2, 21 - ln, zz], [w, ln, w], "h_tooth",
                               up=True, pivot=[xx, 21, zz + w / 2],
                               rotation=[rnd.uniform(-10, 10), 0, rnd.uniform(-14, 14)]))
for i in range(16):  # pelo de alambre
    bx = rnd.uniform(-8.5, 8.5)
    bz = rnd.uniform(-56, -45)
    ln = rnd.uniform(9, 18)
    head_cubes.append(cube(f"hair{i}", [bx - 0.5, 36.6, bz], [1.0, 1.0, ln], "h_hair",
                           pivot=[bx, 37, bz], rotation=[rnd.uniform(20, 55), rnd.uniform(-28, 28), 0]))
bone("head", "neck2", [0, 34, -44], head_cubes)

jaw_cubes = [
    cube("jaw", [-7, 13.5, -65], [14, 5.5, 20], "h_jaw"),
    cube("gum_l", [-6.2, 19, -64.5], [12.4, 2, 19], "h_gum"),
]
for row, xrow in (("l_l", 5.0), ("l_r", -5.0)):
    n = 9
    z0, z1 = -63.0, -47.5
    for i in range(n):
        if rnd.random() < 0.10:
            continue
        zz = z0 + (z1 - z0) / n * i + rnd.uniform(-0.4, 0.4)
        ln = rnd.uniform(3.5, 7.0) + (3.0 if i < 2 else 0)
        w = rnd.uniform(1.2, 1.9)
        xx = xrow + rnd.uniform(-0.5, 0.5)
        jaw_cubes.append(cube(f"tooth_{row}{i}", [xx - w / 2, 21, zz], [w, ln, w], "h_tooth",
                              up=False, pivot=[xx, 21, zz + w / 2],
                              rotation=[rnd.uniform(-10, 10), 0, rnd.uniform(-14, 14)]))
bone("jaw", "head", [0, 19.5, -45], jaw_cubes)

# babeo negro goteando de la mandibula
for i, (dx, dz, ln) in enumerate(((3.5, -62, 11), (-2.0, -64, 12), (-5.0, -56, 8), (5.0, -52, 10), (0.5, -58, 12))):
    bone(f"drip{i + 1}", "jaw", [dx, 14, dz], [
        cube(f"drip{i + 1}", [dx - 0.6, 14 - ln, dz - 0.6], [1.2, ln, 1.2], "h_ooze")])

bone("ear_l", "head", [8, 35, -50], [
    cube("ear_l", [7, 35, -51], [4, 5, 2.4], "h_ear", pivot=[8.5, 35, -50], rotation=[0, 0, -28])])
bone("ear_r", "head", [-8, 35, -50], [
    cube("ear_r", [-10.4, 35, -51.5], [3.4, 6.4, 2.2], "h_ear", pivot=[-9, 35, -50.5], rotation=[0, 0, 24])])

# ---------------- cola corta y rota
bone("tail1", "pelvis", [0, 38, 31], [cube("tail1", [-4.5, 30, 31], [9, 9, 11], "h_tail"),
                                      spike("spk_t1", [0, 39, 36], [2, 6, 2], [-20, 0, 8])])
bone("tail2", "tail1", [0, 34, 41], [cube("tail2", [-3, 27, 41], [6, 7, 11], "h_tail")])
bone("tail3", "tail2", [0.5, 30, 51], [cube("tail3", [-1.2, 23, 51], [3.4, 6, 11], "h_tail",
                                              pivot=[0.5, 28, 51], rotation=[0, 12, 0])])


# ---------------- brazos larguisimos (asimetricos)
def arm(s, up_len, finger_lens):
    n = "l" if s > 0 else "r"
    elbow_y = 50 - up_len
    bone(f"arm_{n}", "chest", [s * 12, 48, -16], [
        cube(f"arm_{n}_u", [mx(11, 10, s), elbow_y, -22], [10, up_len, 12], "h_limb"),
        spike(f"spk_sh_{n}", [s * 14, 50, -16], [2.4, 9, 2.4], [0, 0, s * -30]),
        cube(f"wrap_{n}_u", [mx(10.7, 10.6, s), elbow_y + 6, -22.3], [10.6, 4.5, 12.6], "h_cloth"),
    ])
    bone(f"forearm_{n}", f"arm_{n}", [s * 16, elbow_y, -16], [
        cube(f"farm_{n}", [mx(12, 9, s), 5, -21], [9, elbow_y + 1 - 5, 10], "h_limb"),
        cube(f"wrap_{n}_a", [mx(11.4, 10.2, s), elbow_y - 10, -21.6], [10.2, 4.5, 11.2], "h_cloth"),
        cube(f"wrap_{n}_b", [mx(11.4, 10.2, s), 8, -21.6], [10.2, 4, 11.2], "h_cloth"),
        cube(f"strip_{n}_a", [mx(14, 3.2, s), elbow_y - 20, -22.2], [3.2, 11, 0.6], "h_cloth",
             pivot=[s * 15.6, elbow_y - 10, -22.2], rotation=[10, 0, s * 6]),
        cube(f"strip_{n}_b", [mx(17.5, 2.6, s), 0, -22.2], [2.6, 9, 0.6], "h_cloth",
             pivot=[s * 18.8, 9, -22.2], rotation=[6, 0, s * -8]),
        cube(f"boil_{n}_f", [mx(21, 1.8, s), 13, -19], [1.8, 5.5, 5.5], "h_wound"),
    ])
    cubes = [cube(f"palm_{n}", [mx(11.5, 10, s), 0, -24], [10, 5, 13], "h_limb")]
    k_n = len(finger_lens)
    fw = (10 - 0.6 * (k_n - 1)) / k_n
    for k, fl in enumerate(finger_lens):
        x0 = 11.5 + k * (fw + 0.6)
        xo = mx(x0, fw, s)
        xc = xo + fw / 2
        ry = (k - (k_n - 1) / 2) * 9 * s
        rx = rnd.uniform(-5, 5)
        cubes.append(cube(f"{n}_f{k}", [xo, 0.5, -24 - fl], [fw, 3.2, fl], "h_finger",
                          pivot=[xc, 2.5, -24], rotation=[rx, ry, 0]))
        cubes.append(cube(f"{n}_c{k}", [xo + 0.1, 0.8, -24 - fl - 7], [fw - 0.2, 2.4, 7.2], "h_claw",
                          pivot=[xc, 2.5, -24], rotation=[rx, ry, 0]))
    bone(f"hand_{n}", f"forearm_{n}", [s * 16.5, 7, -16], cubes)


arm(+1, 26, [12, 14.5, 15.5, 14, 10])
arm(-1, 22, [12.5, 15, 14, 11])


# ---------------- patas traseras
def leg(s, shin_len, toe_lens):
    n = "l" if s > 0 else "r"
    bone(f"thigh_{n}", "pelvis", [s * 10, 46, 28], [
        cube(f"thigh_{n}", [mx(9, 12, s), 28, 20], [12, 22, 16], "h_limb"),
        cube(f"boil_t_{n}", [mx(20.4, 1.8, s), 36, 24], [1.8, 6, 6], "h_wound"),
    ])
    bone(f"shin_{n}", f"thigh_{n}", [s * 13, 30, 34], [
        cube(f"shin_{n}", [mx(10.5, 8, s), 32 - shin_len, 31], [8, shin_len, 10], "h_limb"),
        cube(f"wrap_{n}_s", [mx(10.2, 8.6, s), 14, 30.7], [8.6, 4.5, 10.6], "h_cloth"),
    ])
    cubes = [cube(f"sole_{n}", [mx(10, 10, s), 0, 22], [10, 5, 20], "h_limb")]
    k_n = len(toe_lens)
    tw = (10 - 0.6 * (k_n - 1)) / k_n
    for k, tl in enumerate(toe_lens):
        x0 = 10 + k * (tw + 0.6)
        xo = mx(x0, tw, s)
        xc = xo + tw / 2
        ry = (k - (k_n - 1) / 2) * 9 * s
        cubes.append(cube(f"{n}_t{k}", [xo, 0.5, 22 - tl], [tw, 3.2, tl], "h_finger",
                          pivot=[xc, 2.5, 22], rotation=[0, ry, 0]))
        cubes.append(cube(f"{n}_tc{k}", [xo + 0.1, 0.8, 22 - tl - 7], [tw - 0.2, 2.4, 7.2], "h_claw",
                          pivot=[xc, 2.5, 22], rotation=[0, ry, 0]))
    bone(f"foot_{n}", f"shin_{n}", [s * 14.5, 7, 38], cubes)


leg(+1, 26, [11, 13, 10.5])
leg(-1, 30, [10.5, 13.5, 12, 9])


# ----------------------------------------------------------------------------
# COLOR
# ----------------------------------------------------------------------------
BLACK_D = col(9, 9, 12)
BLACK_M = col(26, 26, 32)
BLACK_L = col(58, 63, 76)
FLESH = col(124, 16, 22)
FLESH_L = col(188, 70, 64)
BLOOD_D = col(54, 8, 12)
BONE = col(206, 192, 166)
BONE_D = col(112, 96, 82)
CLOTH = col(94, 84, 72)
GUM = col(74, 14, 24)
TOOTH = col(198, 186, 152)


def black_skin(P, seed, vertical=False, wounds=True):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    if vertical:
        fine = vnoise(x * 2.6, y * 0.55, z * 2.6, seed) * 0.6 + vnoise(x * 6, y * 1.2, z * 6, seed + 7) * 0.4
    else:
        fine = vnoise(x * 1.2, y * 2.4, z * 0.9, seed) * 0.6 + vnoise(x * 3, y * 5, z * 2.2, seed + 7) * 0.4
    patch = vnoise(x * 0.35, y * 0.35, z * 0.35, seed + 11)
    base = mix(BLACK_D, BLACK_M, smooth(0.25, 0.85, patch))
    c = base * (0.5 + 1.1 * fine)[..., None]
    wr = np.abs(vnoise(x * 0.55, y * 1.5, z * 0.55, seed + 21) - 0.5) < 0.028
    c = np.where(wr[..., None], c * 0.35, c)
    ridge = np.abs(vnoise(x * 0.9, y * 0.9, z * 0.9, seed + 40) - 0.5) * 2
    c = np.where(((ridge < 0.07) & (fine > 0.5))[..., None], c + col(24, 28, 38), c)
    c = np.where((vnoise(x * 5, y * 5, z * 5, seed + 41) > 0.93)[..., None], c + BLACK_L * 0.4, c)
    if wounds:
        wn = vnoise(x * 0.26, y * 0.26, z * 0.26, seed + 30)
        flesh = mix(FLESH, FLESH_L, vnoise(x * 3, y * 3, z * 3, seed + 31) * 0.6)
        rim = smooth(0.80, 0.83, wn) * (1 - smooth(0.83, 0.86, wn))
        c = mix(c, col(70, 10, 14), rim)
        c = mix(c, flesh, smooth(0.83, 0.87, wn))
        stain = vnoise(x * 1.1, y * 0.22, z * 1.1, seed + 33) > 0.82
        c = np.where(stain[..., None], mix(c, BLOOD_D, 0.55), c)
    return c


def horror_color(zone, P, N, fu, fv, seed, cname, origin, size, opts):
    nx, ny, nz = N
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    ox, oy, oz = origin
    sx, sy, sz = size
    rel_y = np.clip((y - oy) / max(sy, 1e-3), 0, 1)
    rel_z = np.clip((z - oz) / max(sz, 1e-3), 0, 1)
    if zone == "h_torso":
        c = black_skin(P, seed)
        if abs(nx) > 0.5 or abs(nz) > 0.5:       # pliegues horizontales (piel apretada sobre las costillas)
            g_ = np.sin(y * 1.45 + vnoise(x * 0.2, y * 0.2, z * 0.2, seed + 5) * 3.0)
            c = np.where((g_ > 0.55)[..., None], c + col(20, 23, 30), c)
            c = np.where((g_ < -0.7)[..., None], c * 0.45, c)
    elif zone == "h_limb":
        c = black_skin(P, seed, vertical=True)
    elif zone == "h_head":
        c = black_skin(P, seed, wounds=False)
        if nz < -0.5:
            for (cx, cy, r) in ((8.0, 30.4, 4.6), (-7.9, 29.2, 4.0)):
                d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
                c = mix(c, col(34, 8, 16), smooth(1.0, 0.25, d) * 0.85)
    elif zone == "h_snout":
        if ny < -0.5:
            ridge = 0.5 + 0.5 * np.sin(z * 2.2)
            c = mix(col(98, 26, 36), col(44, 8, 16), ridge)
            c = c * (0.7 + 0.5 * vnoise(x * 3, y * 3, z * 3, seed))[..., None]
        else:
            c = black_skin(P, seed, wounds=False)
    elif zone == "h_nose":
        n = vnoise(x * 4, y * 4, z * 4, seed)
        c = np.broadcast_to(col(8, 8, 10), P.shape).copy() + (n - 0.5)[..., None] * 8
        if ny > 0.5:
            gx = 1 - np.clip(np.abs(fu - 0.5) * 2.2, 0, 1)
            gy = 1 - np.clip(np.abs(fv - 0.5) * 2.2, 0, 1)
            c = mix(c, col(120, 130, 150), np.clip((gx * gy) ** 1.4 * 0.7, 0, 1))
        if nz < -0.5:
            for cx in (0.27, 0.73):
                d = ((fu - cx) / 0.2) ** 2 + ((fv - 0.5) / 0.3) ** 2
                c = np.where((d < 1)[..., None], col(2, 2, 3), c)
    elif zone == "h_jaw":
        if ny > 0.5:
            n = vnoise(x * 1.5, y * 1.5, z * 1.5, seed)
            c = mix(col(70, 12, 20), col(26, 4, 9), n)
            c = c * (0.7 + 0.6 * vnoise(x * 5, y * 5, z * 5, seed + 1))[..., None]
        else:
            c = black_skin(P, seed, wounds=False)
    elif zone == "h_gum":
        n = vnoise(x * 2, y * 2, z * 2, seed)
        c = mix(GUM, col(40, 8, 16), n) * (0.75 + 0.5 * vnoise(x * 6, y * 6, z * 6, seed + 3))[..., None]
        vein = np.abs(vnoise(x * 3, y * 3, z * 3, seed + 4) - 0.5) < 0.04
        c = np.where(vein[..., None], col(46, 6, 14), c)
    elif zone == "h_tooth":
        up = opts.get("up", False)
        root = rel_y if up else 1 - rel_y
        stain = vnoise(x * 3.5, y * 3.5, z * 3.5, seed)
        c = mix(TOOTH, col(140, 108, 70), np.clip(root ** 1.5 * 0.9 + stain * 0.4, 0, 1))
        c = mix(c, BLOOD_D * 1.6, smooth(0.75, 0.97, root))
        crack = np.abs(vnoise(x * 6, y * 2, z * 6, seed + 5) - 0.5) < 0.03
        c = np.where(crack[..., None], c * 0.55, c)
    elif zone == "h_claw":
        tip = 1 - rel_z
        c = mix(col(86, 80, 74), col(6, 6, 7), np.clip(tip * 1.3, 0, 1))
        c = c * (0.75 + 0.5 * vnoise(x * 4, y * 4, z * 4, seed))[..., None]
    elif zone == "h_finger":
        c = black_skin(P, seed, wounds=False)
        knuckle = (z * 0.32 - np.floor(z * 0.32)) < 0.13
        c = np.where(knuckle[..., None], mix(c, BONE_D * 0.7, 0.6), c)
    elif zone == "h_bone":
        root = 1 - rel_y
        stain = vnoise(x * 3, y * 3, z * 3, seed)
        c = mix(BONE, BONE_D, np.clip(stain * 0.55 + root * 0.35, 0, 1))
        c = mix(c, BLOOD_D * 1.5, smooth(0.6, 0.95, root) * 0.9)
        c = c * (0.8 + 0.4 * vnoise(x * 6, y * 1.5, z * 6, seed + 2))[..., None]
    elif zone == "h_rib":
        c = mix(col(70, 58, 52), col(30, 26, 28), vnoise(x * 1.4, y * 1.4, z * 1.4, seed))
        c = c * (0.75 + 0.5 * vnoise(x * 4, y * 4, z * 4, seed + 3))[..., None]
        if ny > 0.5:
            c = c + col(18, 16, 16)
    elif zone == "h_hair":
        c = mix(col(8, 8, 10), col(66, 70, 82), np.clip(1 - rel_z, 0, 1) ** 2 * 0.8)
        c = c * (0.8 + 0.5 * vnoise(x * 4, y * 4, z * 4, seed))[..., None]
    elif zone == "h_cloth":
        weave = 0.75 + 0.25 * np.sin(x * 5.0) * np.sin(z * 5.0 + y * 3.0)
        c = CLOTH * weave[..., None] * (0.6 + 0.8 * vnoise(x * 1.5, y * 1.5, z * 1.5, seed))[..., None]
        blood = vnoise(x * 0.5, y * 0.5, z * 0.5, seed + 8)
        c = mix(c, col(96, 18, 20), smooth(0.45, 0.65, blood) * 0.85)
        c = mix(c, col(20, 18, 16), smooth(0.7, 0.9, vnoise(x * 0.9, y * 0.9, z * 0.9, seed + 9)) * 0.7)
    elif zone == "h_ooze":
        c = np.broadcast_to(col(3, 3, 5), P.shape).copy()
        spec = np.clip(1 - np.abs(fu - 0.3) * 6, 0, 1)
        c = mix(c, col(86, 96, 120), spec * 0.8)
    elif zone == "h_wound":
        r = np.sqrt(((fu - 0.5) / 0.5) ** 2 + ((fv - 0.5) / 0.5) ** 2)
        c = mix(col(210, 52, 48), FLESH, smooth(0.0, 0.7, r))
        c = mix(c, col(186, 110, 104), smooth(0.7, 0.88, r) * (1 - smooth(0.88, 1.0, r)))
        c = mix(c, col(30, 6, 10), smooth(0.92, 1.0, r))
        c = c * (0.8 + 0.4 * vnoise(x * 4, y * 4, z * 4, seed))[..., None]
    elif zone == "h_eye":
        c = np.broadcast_to(col(40, 6, 8), P.shape).copy()
        if nz < -0.5:
            r = np.sqrt(((fu - 0.5) / 0.5) ** 2 + ((fv - 0.5) / 0.5) ** 2)
            c = mix(col(255, 236, 214), col(255, 44, 32), smooth(0.05, 0.4, r))
            c = mix(c, col(170, 6, 8), smooth(0.45, 0.85, r))
            c = mix(c, col(46, 4, 8), smooth(0.88, 1.0, r))
    elif zone == "h_brow":
        c = black_skin(P, seed, wounds=False) * 0.7
        c = c * (0.7 + 0.5 * np.sin(x * 2.0 + y * 0.8))[..., None]
    elif zone == "h_ear":
        c = black_skin(P, seed, wounds=False)
        if abs(nz) > 0.5:
            r = np.sqrt(((fu - 0.5) / 0.5) ** 2 + ((fv - 0.55) / 0.5) ** 2)
            c = mix(c, col(86, 30, 40), smooth(0.85, 0.2, r) * 0.7)
    elif zone == "h_tail":
        c = black_skin(P, seed, wounds=True)
        ring = (z * 0.3 - np.floor(z * 0.3)) < 0.07
        c = np.where(ring[..., None], c * 0.5, c)
    else:
        c = np.broadcast_to(col(255, 0, 255), P.shape).copy()
    if ny < -0.5:
        c = c * 0.65
    return np.clip(c, 0, 255)


def alpha_for(zone, cname, N, fu, fv, seed):
    a = np.full(fu.shape, 255, dtype=np.uint8)
    z0 = np.zeros_like(fu)
    if zone == "h_ear" and abs(N[2]) > 0.5:
        n = vnoise(fu * 6, fv * 6, z0, seed + 70)
        if cname == "ear_l":
            torn = ((fu > 0.45) & (fv < 0.5) & (n > 0.3)) | (n > 0.82)
        else:
            torn = (fu > 0.7) & (fv < 0.3) & (n > 0.45)
        a = np.where(torn, 0, a).astype(np.uint8)
    if zone == "h_cloth" and cname.startswith("strip"):
        n = vnoise(fu * 5, fv * 9, z0, seed + 71)
        ragged = (fv > 0.78 + 0.3 * (n - 0.5)) | (fu < 0.08 * n) | (fu > 1 - 0.18 * n)
        a = np.where(ragged, 0, a).astype(np.uint8)
    return a


def glow_for(zone, N, fu, fv):
    """Devuelve alfa de brillo (0..255) para la mascara emisiva, o None."""
    if zone == "h_eye" and N[2] < -0.5:
        r = np.sqrt(((fu - 0.5) / 0.5) ** 2 + ((fv - 0.5) / 0.5) ** 2)
        return (255 * (1 - smooth(0.80, 1.0, r))).astype(np.uint8)
    if zone == "h_eye":
        return np.full(fu.shape, 90, dtype=np.uint8)
    if zone == "h_wound":
        r = np.sqrt(((fu - 0.5) / 0.5) ** 2 + ((fv - 0.5) / 0.5) ** 2)
        return (150 * (1 - smooth(0.2, 0.75, r))).astype(np.uint8)
    return None


# ----------------------------------------------------------------------------
# TEXTURA + GEO
# ----------------------------------------------------------------------------

def build():
    g.BONES = BONES
    density, layout = g.best_layout()
    print(f"[horror] densidad: {density} px/unidad ({TEX}x{TEX}), caras: {len(layout)}")
    img = np.zeros((TEX, TEX, 4), dtype=np.uint8)
    glow = np.zeros((TEX, TEX, 4), dtype=np.uint8)
    geo_bones = []
    for b in BONES:
        gb = {"name": b["name"], "pivot": b["pivot"]}
        if b["parent"]:
            gb["parent"] = b["parent"]
        cubes = []
        for (cname, origin, size, zone) in b["cubes"]:
            opts = OPTS.get(cname, {})
            seed = (sum(ord(ch) * (i + 1) for i, ch in enumerate(cname)) % 60) + 1
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
                ga = glow_for(zone, normal, fu, fv)
                if ga is not None:
                    glow[v0:v0 + ph, u0:u0 + pw, :3] = rgb.astype(np.uint8)
                    glow[v0:v0 + ph, u0:u0 + pw, 3] = ga
                for arr in (img, glow):
                    arr[v0 - 1, u0:u0 + pw] = arr[v0, u0:u0 + pw]
                    arr[v0 + ph, u0:u0 + pw] = arr[v0 + ph - 1, u0:u0 + pw]
                    arr[v0:v0 + ph, u0 - 1] = arr[v0:v0 + ph, u0]
                    arr[v0:v0 + ph, u0 + pw] = arr[v0:v0 + ph, u0 + pw - 1]
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
                "visible_bounds_width": 10,
                "visible_bounds_height": 6,
                "visible_bounds_offset": [0, 2.0, 0],
            },
            "bones": geo_bones,
        }],
    }
    return img, glow, geo


# ----------------------------------------------------------------------------
# ANIMACIONES  (criatura enorme: movimientos lentos, pesados y amenazantes)
# Convencion: rotacion X positiva = el frente (-Z) baja (las puntas de las
# extremidades colgantes se van hacia atras). Avanzar un brazo = X negativa.
# ----------------------------------------------------------------------------
TAU = g.TAU
s = g.s


def sstep(a, b, t):
    return float(g.smooth(a, b, t))


BASE = {
    "arm_l": [-6, 0, 0], "arm_r": [-6, 0, 0],
    "forearm_l": [4, 0, 0], "forearm_r": [4, 0, 0],
    "hand_l": [4, 0, 0], "hand_r": [4, 0, 0],
    "thigh_l": [-10, 0, 0], "thigh_r": [-10, 0, 0],
    "shin_l": [18, 0, 0], "shin_r": [18, 0, 0],
    "foot_l": [-8, 0, 0], "foot_r": [-8, 0, 0],
    "neck1": [10, 0, 0], "neck2": [12, 0, 0], "head": [-16, 0, 0],
}
DRIPS = ["drip1", "drip2", "drip3", "drip4", "drip5"]


def R(a, bone_name, fn):
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


def drips(a, period, amp=7.0):
    for i, name in enumerate(DRIPS):
        a.rot(name, lambda t, i=i: [amp * 0.6 * s(t, period, i * 1.1), 0, amp * s(t, period * 0.8, i * 0.7)])


def tail3(a, period, amp_y, amp_x, lag=0.6, base_x=0.0):
    for i, name in enumerate(("tail1", "tail2", "tail3")):
        k = i + 1
        a.rot(name, lambda t, k=k: [base_x + amp_x * (0.7 + 0.3 * k) * s(t, period, -lag * k),
                                    amp_y * (0.5 + 0.35 * k) * s(t, period, -lag * k), 0])


def make_animations():
    P = "animation.otter_horror."
    A = {}

    # ---- idle: respira pesadamente, mandibula colgando y goteando
    L = 5.0
    a = g.Anim(L, dt=0.1)
    a.pos("pelvis", lambda t: [0, 0.5 * s(t, 2.5), 0])
    a.rot("spine", lambda t: [1.2 * s(t, 2.5), 0, 0])
    a.rot("chest", lambda t: [2.0 * s(t, 2.5, 0.5), 2 * s(t, L), 0])
    R(a, "neck1", lambda t: [2 * s(t, L, 0.3), 7 * s(t, L), 0])
    R(a, "neck2", lambda t: [2 * s(t, L, 0.8), 9 * s(t, L, 0.3), 0])
    R(a, "head", lambda t: [3 * s(t, L, 1.0), 11 * s(t, L, 0.5) + 4 * s(t, L / 2), 5 * s(t, L, 2.0)])
    a.rot("jaw", lambda t: [22 + 5 * s(t, 2.5, 0.8), 0, 0])
    a.rot("ear_l", lambda t: [0, 0, 8 * max(0, s(t, L / 2, 1.2))])
    a.rot("ear_r", lambda t: [0, 0, -6 * max(0, s(t, L / 2, 2.4))])
    R(a, "hand_l", lambda t: [3 * s(t, L / 2), 0, 0])
    R(a, "hand_r", lambda t: [3 * s(t, L / 2, 1.5), 0, 0])
    drips(a, 2.5)
    tail3(a, L, 6, 2, lag=0.45)
    A[P + "idle"] = finish(a)

    # ---- crawl: paso lento y pesado, una pata trasera se arrastra, la cabeza gira antes
    L = 1.8
    a = g.Anim(L)
    R(a, "arm_l", lambda t: [-24 * s(t, L), 0, 0])
    R(a, "arm_r", lambda t: [-14 * s(t, L, math.pi), 0, 0])
    R(a, "forearm_l", lambda t: [14 * max(0, s(t, L, 0.8)), 0, 0])
    R(a, "forearm_r", lambda t: [6 * s(t, L, math.pi + 0.8), 0, 0])
    R(a, "hand_l", lambda t: [-12 * s(t, L, 1.2), 0, 0])
    R(a, "thigh_r", lambda t: [-20 * s(t, L), 0, 0])
    R(a, "thigh_l", lambda t: [-8 * s(t, L, math.pi), 0, 0])       # se arrastra
    R(a, "shin_r", lambda t: [20 * max(0, s(t, L, 0.9)), 0, 0])
    R(a, "shin_l", lambda t: [4 * s(t, L, math.pi + 0.9), 0, 0])
    R(a, "foot_l", lambda t: [-10 * max(0, s(t, L, math.pi + 1.5)), 0, 0])
    a.pos("arm_l", lambda t: [0, 3.0 * max(0, math.cos(TAU * t / L)), 0])
    a.pos("thigh_r", lambda t: [0, 3.0 * max(0, math.cos(TAU * t / L)), 0])
    a.rot("spine", lambda t: [2 * s(t, L / 2, 0.5), 6 * s(t, L), 0])
    a.rot("chest", lambda t: [0, -8 * s(t, L, 0.4), 0])
    a.rot("pelvis", lambda t: [0, 5 * s(t, L, math.pi), 0])
    R(a, "neck1", lambda t: [0, -9 * s(t, L, -0.9), 0])
    R(a, "neck2", lambda t: [0, -11 * s(t, L, -1.2), 0])
    R(a, "head", lambda t: [3 * s(t, L / 2, 2.0), -13 * s(t, L, -1.5), 0])
    a.rot("jaw", lambda t: [24 + 4 * s(t, L / 2), 0, 0])
    a.pos("pelvis", lambda t: [0, 1.2 * s(t, L / 2), 0])
    drips(a, 1.2, 9)
    tail3(a, L, 12, 2, lag=0.55)
    A[P + "crawl"] = finish(a)

    # ---- run: embestida a cuatro extremidades, zancadas enormes
    L = 0.8
    a = g.Anim(L, dt=0.04)
    R(a, "arm_l", lambda t: [-6 + 42 * s(t, L), 0, 0])
    R(a, "arm_r", lambda t: [-6 + 42 * s(t, L, 0.5), 0, 0])
    R(a, "forearm_l", lambda t: [16 * max(0, s(t, L, 0.9)), 0, 0])
    R(a, "forearm_r", lambda t: [16 * max(0, s(t, L, 1.4)), 0, 0])
    R(a, "thigh_l", lambda t: [38 * s(t, L, 1.9), 0, 0])
    R(a, "thigh_r", lambda t: [38 * s(t, L, 2.1), 0, 0])
    R(a, "shin_l", lambda t: [32 * max(0, s(t, L, 2.8)), 0, 0])
    R(a, "shin_r", lambda t: [32 * max(0, s(t, L, 3.0)), 0, 0])
    a.pos("arm_l", lambda t: [0, 4.0 * max(0, math.cos(TAU * t / L)), 0])
    a.pos("arm_r", lambda t: [0, 4.0 * max(0, math.cos(TAU * t / L + 0.5)), 0])
    a.pos("thigh_l", lambda t: [0, 4.0 * max(0, math.cos(TAU * t / L + 1.9)), 0])
    a.pos("thigh_r", lambda t: [0, 4.0 * max(0, math.cos(TAU * t / L + 2.1)), 0])
    a.rot("spine", lambda t: [8 * s(t, L, 0.6), 0, 0])
    a.rot("pelvis", lambda t: [-4 * s(t, L, 0.6), 0, 0])
    a.rot("chest", lambda t: [6 * s(t, L, 1.8), 0, 0])
    R(a, "neck1", lambda t: [6, 0, 0])
    R(a, "neck2", lambda t: [6 * s(t, L, 2.4), 0, 0])
    R(a, "head", lambda t: [-5 * s(t, L, 2.4), 0, 0])
    a.rot("jaw", lambda t: [42 + 8 * s(t, L / 2), 0, 0])
    a.pos("pelvis", lambda t: [0, 3.5 * max(0, s(t, L, 1.0)), 0])
    drips(a, 0.5, 14)
    tail3(a, L, 8, 5, lag=0.35, base_x=8)
    A[P + "run"] = finish(a)

    # ---- swim
    L = 1.6
    a = g.Anim(L)
    a.rot("arm_l", lambda t: [58 + 10 * s(t, L), 0, 0])
    a.rot("arm_r", lambda t: [58 + 10 * s(t, L, 0.6), 0, 0])
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
    a.rot("spine", lambda t: [8 * s(t, L), 0, 0])
    a.rot("chest", lambda t: [5 * s(t, L, -0.7), 0, 0])
    a.rot("neck1", lambda t: [4, 6 * s(t, L, -1.0), 0])
    a.rot("neck2", lambda t: [4, 8 * s(t, L, -1.3), 0])
    a.rot("head", lambda t: [-4, 0, 0])
    a.rot("jaw", lambda t: [18, 0, 0])
    a.pos("pelvis", lambda t: [0, -3.0 + 1.2 * s(t, L, 0.5), 0])
    drips(a, 1.0, 8)
    tail3(a, L, 22, 8, lag=0.55)
    A[P + "swim"] = a

    # ---- swim_idle
    L = 4.0
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
    a.rot("jaw", lambda t: [14 + 3 * s(t, L / 2), 0, 0])
    a.pos("pelvis", lambda t: [0, -3.0 + 0.8 * s(t, L), 0])
    drips(a, 2.0, 6)
    tail3(a, L, 12, 4, lag=0.5)
    A[P + "swim_idle"] = a

    # ---- still: inmovil, cabeza alzada, mirando fijamente
    L = 4.0
    a = g.Anim(L, dt=0.2)
    R(a, "head", lambda t: [-16 + 0.3 * s(t, L), 0, 0])
    R(a, "neck1", lambda t: [-8, 0, 0])
    R(a, "neck2", lambda t: [-6, 0, 0])
    a.rot("chest", lambda t: [-4, 0, 0])
    a.rot("jaw", lambda t: [18 + 0.3 * s(t, L), 0, 0])
    drips(a, 3.0, 3)
    A[P + "still"] = finish(a)

    # ---- rise: levanta la cabeza (y el torso) muy despacio y la mantiene
    L = 7.0
    a = g.Anim(L, dt=0.1)

    def rp(t):
        return sstep(0, 4.0, t) * (1 - sstep(6.0, 7.0, t))
    R(a, "head", lambda t: [-34 * rp(t), 5 * s(t, 1.6) * rp(t), 0])
    R(a, "neck1", lambda t: [-18 * rp(t), 0, 0])
    R(a, "neck2", lambda t: [-16 * rp(t), 0, 0])
    a.rot("chest", lambda t: [-14 * rp(t), 0, 0])
    a.rot("spine", lambda t: [-5 * rp(t), 0, 0])
    R(a, "arm_l", lambda t: [-18 * rp(t), 0, 0])
    R(a, "arm_r", lambda t: [-18 * rp(t), 0, 0])
    a.rot("jaw", lambda t: [18 + 22 * rp(t), 0, 0])
    drips(a, 2.0, 5)
    A[P + "rise"] = finish(a)

    # ---- jaw: abre la mandibula exageradamente, tiembla y cierra de golpe
    L = 2.4
    a = g.Anim(L, dt=0.025)

    def op(t):
        return sstep(0.0, 0.45, t) * (1 - sstep(1.8, 1.95, t))
    a.rot("jaw", lambda t: [18 + 52 * op(t) + 2.5 * math.sin(TAU * 16 * t) * op(t), 0, 0])
    R(a, "head", lambda t: [-16 * op(t), 0, 0])
    R(a, "neck1", lambda t: [-10 * op(t), 0, 0])
    R(a, "neck2", lambda t: [-8 * op(t), 0, 0])
    a.rot("chest", lambda t: [-8 * op(t), 0, 0])
    a.rot("ear_l", lambda t: [0, 0, 10 * op(t)])
    drips(a, 0.6, 12)
    A[P + "jaw"] = finish(a)

    # ---- spasm: sacudidas violentas e irregulares
    L = 1.2
    a = g.Anim(L, dt=0.02)

    def env(t):
        return 1.0 if (t < 0.4 or 0.65 < t < 0.95) else 0.15

    def n1(t):
        return s(t, 0.13) + 0.6 * s(t, 0.21, 1) + 0.4 * s(t, 0.07, 2)

    def n2(t):
        return s(t, 0.11, 0.5) + 0.7 * s(t, 0.17, 2) + 0.3 * s(t, 0.06, 1)

    def n3(t):
        return s(t, 0.09, 1.3) + 0.5 * s(t, 0.19, 0.2)
    R(a, "head", lambda t: [12 * n2(t) * env(t), 26 * n1(t) * env(t), 8 * n3(t) * env(t)])
    R(a, "neck1", lambda t: [6 * n3(t) * env(t), 14 * n2(t) * env(t), 0])
    a.rot("spine", lambda t: [4 * n2(t) * env(t), 0, 12 * n1(t) * env(t)])
    a.rot("chest", lambda t: [0, 10 * n2(t) * env(t), 8 * n3(t) * env(t)])
    R(a, "arm_l", lambda t: [26 * n3(t) * env(t), 0, 0])
    R(a, "arm_r", lambda t: [-22 * n1(t) * env(t), 0, 0])
    R(a, "thigh_r", lambda t: [36 * max(0, n2(t)) * env(t), 0, 0])
    a.rot("jaw", lambda t: [24 + 18 * max(0, n3(t)) * env(t), 0, 0])
    drips(a, 0.3, 18)
    tail3(a, 0.35, 28, 6, lag=0.3)
    A[P + "spasm"] = finish(a)

    # ---- bite: embestida con mordisco y zarpazo
    L = 0.8
    a = g.Anim(L, dt=0.02)

    def bp(t):
        return sstep(0, 0.2, t) * (1 - sstep(0.45, 0.8, t))

    def jo(t):
        return sstep(0.05, 0.22, t) * (1 - sstep(0.36, 0.43, t))
    R(a, "neck1", lambda t: [26 * bp(t), 0, 0])
    R(a, "neck2", lambda t: [18 * bp(t), 0, 0])
    R(a, "head", lambda t: [14 * bp(t), 0, 0])
    a.rot("jaw", lambda t: [18 + 48 * jo(t), 0, 0])
    a.rot("chest", lambda t: [12 * bp(t), 0, 0])
    a.rot("pelvis", lambda t: [-8 * bp(t), 0, 0])
    R(a, "arm_l", lambda t: [-42 * bp(t), 0, 0])
    R(a, "arm_r", lambda t: [-34 * sstep(0.12, 0.35, t) * (1 - sstep(0.5, 0.8, t)), 0, 0])
    drips(a, 0.4, 16)
    tail3(a, L, 5, 3, lag=0.4, base_x=6)
    A[P + "bite"] = finish(a)


    # ---- transform (fase B, modelo monstruoso): nace pequena y retorcida y se despliega hasta su tamano real
    L = 4.5
    a = g.Anim(L, loop="hold_on_last_frame", dt=0.05)

    def grow(t):
        return 0.16 + 0.84 * (0.06 * sstep(0, 1.0, t) + 0.49 * sstep(1.0, 2.4, t) + 0.45 * sstep(2.3, 3.4, t)
                              + 0.08 * sstep(3.3, 3.6, t) - 0.08 * sstep(3.6, 4.5, t))

    def unf(t):                      # 0 = encogida, 1 = desplegada
        return sstep(1.0, 3.0, t)

    def sp(t):                       # intensidad de espasmos
        return (0.4 + 0.6 * sstep(0, 0.6, t)) * (1 - sstep(2.8, 3.6, t))

    def n1(t):
        return s(t, 0.13) + 0.6 * s(t, 0.21, 1) + 0.4 * s(t, 0.07, 2)

    def n2(t):
        return s(t, 0.11, 0.5) + 0.7 * s(t, 0.17, 2) + 0.3 * s(t, 0.06, 1)
    a.chan("root", "scale", lambda t: [grow(t)] * 3)
    R(a, "arm_l", lambda t: [-45 * (1 - unf(t)) + 12 * n1(t) * sp(t), 0, 0])
    R(a, "arm_r", lambda t: [-45 * (1 - unf(t)) - 12 * n2(t) * sp(t), 0, 0])
    R(a, "forearm_l", lambda t: [60 * (1 - unf(t)), 0, 0])
    R(a, "forearm_r", lambda t: [60 * (1 - unf(t)), 0, 0])
    R(a, "thigh_l", lambda t: [-40 * (1 - unf(t)) + 10 * n2(t) * sp(t), 0, 0])
    R(a, "thigh_r", lambda t: [-40 * (1 - unf(t)) - 10 * n1(t) * sp(t), 0, 0])
    R(a, "shin_l", lambda t: [50 * (1 - unf(t)), 0, 0])
    R(a, "shin_r", lambda t: [50 * (1 - unf(t)), 0, 0])
    for nm in ("arm_l", "arm_r", "thigh_l", "thigh_r"):
        a.chan(nm, "scale", lambda t: [1, 0.55 + 0.45 * sstep(0.8, 3.2, t), 1])
    for nm in ("neck1", "neck2"):
        a.chan(nm, "scale", lambda t: [1, 1, 0.55 + 0.45 * sstep(1.0, 3.0, t)])
    a.rot("spine", lambda t: [14 * (1 - unf(t)) + 6 * n2(t) * sp(t), 0, 14 * n1(t) * sp(t)])
    a.rot("chest", lambda t: [-14 * sstep(2.6, 3.2, t) + 14 * sstep(3.6, 4.3, t), 10 * n2(t) * sp(t), 8 * n1(t) * sp(t)])
    R(a, "neck1", lambda t: [25 * (1 - unf(t)) + 8 * n1(t) * sp(t), 14 * n2(t) * sp(t), 0])
    R(a, "neck2", lambda t: [25 * (1 - unf(t)), 12 * n1(t) * sp(t), 0])
    R(a, "head", lambda t: [30 * (1 - unf(t)) - 30 * sstep(2.6, 3.2, t) + 30 * sstep(3.6, 4.3, t) + 10 * n2(t) * sp(t),
                            26 * n1(t) * sp(t), 8 * n2(t) * sp(t)])
    a.rot("jaw", lambda t: [4 + 66 * sstep(2.3, 3.0, t) - 48 * sstep(3.7, 4.4, t)
                            + 3 * math.sin(TAU * 16 * t) * sstep(2.6, 3.0, t) * (1 - sstep(3.7, 4.0, t)), 0, 0])
    a.rot("ear_l", lambda t: [0, 0, 10 * n1(t) * sp(t)])
    drips(a, 0.5, 14)
    tail3(a, 0.45, 26, 8, lag=0.4)
    A[P + "transform"] = finish(a)
    A[P + "transform_frenzy"] = g.ScaledAnim(a, 3.5 / 4.5, 1.0)     # 3.5 s, mas rapida y brusca

    # ---- untransform (modelo monstruoso): se encoge, convulsiona y se repliega
    L = 3.5
    a = g.Anim(L, loop="hold_on_last_frame", dt=0.05)

    def shrink(t):
        return 1 - 0.84 * (0.3 * sstep(0.2, 1.2, t) + 0.7 * sstep(1.2, 3.0, t))

    def fold(t):                     # 0 = desplegada, 1 = encogida
        return sstep(0.6, 3.0, t)

    def sp2(t):
        return sstep(0, 0.5, t) * (1 - sstep(2.6, 3.4, t))
    a.chan("root", "scale", lambda t: [shrink(t)] * 3)
    R(a, "arm_l", lambda t: [-45 * fold(t) + 12 * n1(t) * sp2(t), 0, 0])
    R(a, "arm_r", lambda t: [-45 * fold(t) - 12 * n2(t) * sp2(t), 0, 0])
    R(a, "forearm_l", lambda t: [60 * fold(t), 0, 0])
    R(a, "forearm_r", lambda t: [60 * fold(t), 0, 0])
    R(a, "thigh_l", lambda t: [-40 * fold(t) + 10 * n2(t) * sp2(t), 0, 0])
    R(a, "thigh_r", lambda t: [-40 * fold(t) - 10 * n1(t) * sp2(t), 0, 0])
    R(a, "shin_l", lambda t: [50 * fold(t), 0, 0])
    R(a, "shin_r", lambda t: [50 * fold(t), 0, 0])
    for nm in ("arm_l", "arm_r", "thigh_l", "thigh_r"):
        a.chan(nm, "scale", lambda t: [1, 1 - 0.45 * sstep(0.5, 3.0, t), 1])
    for nm in ("neck1", "neck2"):
        a.chan(nm, "scale", lambda t: [1, 1, 1 - 0.45 * sstep(0.8, 3.0, t)])
    a.rot("spine", lambda t: [14 * fold(t) + 6 * n2(t) * sp2(t), 0, 14 * n1(t) * sp2(t)])
    a.rot("chest", lambda t: [-12 * sstep(0, 0.4, t) * (1 - sstep(0.9, 1.4, t)), 10 * n2(t) * sp2(t), 8 * n1(t) * sp2(t)])
    R(a, "neck1", lambda t: [25 * fold(t) + 8 * n1(t) * sp2(t), 14 * n2(t) * sp2(t), 0])
    R(a, "neck2", lambda t: [25 * fold(t), 12 * n1(t) * sp2(t), 0])
    R(a, "head", lambda t: [30 * fold(t) - 24 * sstep(0, 0.4, t) * (1 - sstep(0.9, 1.4, t)) + 10 * n2(t) * sp2(t),
                            26 * n1(t) * sp2(t), 8 * n2(t) * sp2(t)])
    a.rot("jaw", lambda t: [22 + 44 * sstep(0.0, 0.4, t) * (1 - sstep(0.7, 1.2, t)) - 22 * sstep(1.2, 2.2, t), 0, 0])
    drips(a, 0.5, 14)
    tail3(a, 0.45, 26, 8, lag=0.4)
    A[P + "untransform"] = finish(a)

    return {"format_version": "1.8.0", "animations": {k: v.to_json() for k, v in A.items()}}


def main():
    img, glow, geo = build()
    tex_dir = os.path.join(ASSETS, "textures", "entity")
    Image.fromarray(img, "RGBA").save(os.path.join(tex_dir, "otter_horror.png"), optimize=True)
    Image.fromarray(glow, "RGBA").save(os.path.join(tex_dir, "otter_horror_glowmask.png"), optimize=True)
    with open(os.path.join(ASSETS, "geo", "otter_horror.geo.json"), "w") as f:
        json.dump(geo, f, indent=1)
    with open(os.path.join(ASSETS, "animations", "otter_horror.animation.json"), "w") as f:
        json.dump(make_animations(), f, separators=(",", ":"))
    print("OK")


if __name__ == "__main__":
    main()
