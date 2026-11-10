#!/usr/bin/env python3
"""
OTTERFALL - generador de recursos de la nutria normal (Fase 1).

Genera:
  - assets/otterfall/geo/otter.geo.json          (modelo GeckoLib / Bedrock geometry)
  - assets/otterfall/animations/otter.animation.json
  - assets/otterfall/textures/entity/otter.png   (512x512, pelaje procedural en 3D)

Uso (desde la raiz del repo):   python3 tools/generate_assets.py
Requiere: numpy y Pillow.

La textura se pinta evaluando un campo de color en 3D sobre la superficie de cada
cubo, asi las costuras entre caras y piezas quedan continuas.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets", "otterfall")
TEX_SIZE = 512
PAD = 2

# ----------------------------------------------------------------------------
# 1. DEFINICION DEL MODELO
# ----------------------------------------------------------------------------
# Cada cubo: (nombre, origen[x,y,z], tamano[sx,sy,sz], zona)
# El frente de la nutria mira hacia -Z. Unidades = 1/16 de bloque.

BONES = []


def bone(name, parent, pivot, cubes):
    BONES.append({"name": name, "parent": parent, "pivot": pivot, "cubes": cubes})


bone("root", None, [0, 4.5, 0], [])

bone("body", "root", [0, 3.4, 4.5], [
    ("chest", [-3.3, 3.2, -6.2], [6.6, 5.2, 7.4], "body"),
    ("hips", [-3.6, 2.9, 0.6], [7.2, 5.4, 7.2], "body"),
    ("nape", [-2.7, 6.6, -7.6], [5.4, 2.6, 3.2], "body"),
    ("chest_fluff", [-2.3, 3.0, -7.0], [4.6, 2.6, 1.5], "fluff"),
])

bone("head", "body", [0, 6.4, -6.6], [
    ("skull", [-3.1, 5.0, -10.8], [6.2, 4.6, 4.6], "skull"),
    ("muzzle", [-1.9, 5.0, -13.2], [3.8, 2.7, 2.5], "muzzle"),
    ("nose", [-1.1, 6.3, -13.8], [2.2, 1.4, 0.7], "nose"),
    ("eye_l", [1.85, 7.2, -10.95], [1.2, 1.4, 0.3], "eye"),
    ("eye_r", [-3.05, 7.2, -10.95], [1.2, 1.4, 0.3], "eye"),
    ("cheek_l", [3.0, 5.0, -10.2], [0.9, 2.0, 2.8], "fluff"),
    ("cheek_r", [-3.9, 5.0, -10.2], [0.9, 2.0, 2.8], "fluff"),
    ("whisker_l1", [1.9, 6.4, -13.0], [3.4, 0.1, 0.1], "whisker"),
    ("whisker_l2", [1.9, 5.9, -12.9], [3.2, 0.1, 0.1], "whisker"),
    ("whisker_r1", [-5.3, 6.4, -13.0], [3.4, 0.1, 0.1], "whisker"),
    ("whisker_r2", [-5.1, 5.9, -12.9], [3.2, 0.1, 0.1], "whisker"),
])

# mandibula inferior pequena: invisible cerrada, se abre en la transformacion
bone("jaw", "head", [0, 5.3, -10.4], [
    ("chin", [-1.5, 4.3, -12.7], [3.0, 1.0, 2.6], "muzzle"),
])

bone("ear_l", "head", [2.6, 9.3, -8.2], [
    ("ear_l", [1.9, 9.2, -8.7], [1.5, 1.3, 0.9], "ear"),
])
bone("ear_r", "head", [-2.6, 9.3, -8.2], [
    ("ear_r", [-3.4, 9.2, -8.7], [1.5, 1.3, 0.9], "ear"),
])

bone("tail1", "body", [0, 5.3, 7.6], [("tail1", [-1.9, 3.9, 7.4], [3.8, 2.8, 5.2], "tail")])
bone("tail2", "tail1", [0, 5.1, 12.4], [("tail2", [-1.5, 3.9, 12.2], [3.0, 2.4, 4.8], "tail")])
bone("tail3", "tail2", [0, 4.9, 16.8], [("tail3", [-1.0, 4.0, 16.6], [2.0, 1.8, 4.4], "tail")])

# patas delanteras cuelgan del cuerpo (para poder sentarse), las traseras de root
bone("leg_fl", "body", [2.5, 3.8, -4.3], [
    ("fl_leg", [1.5, 0.9, -5.3], [2.0, 2.9, 2.0], "leg"),
    ("fl_paw", [1.3, 0.0, -6.3], [2.4, 1.0, 3.0], "paw"),
])
bone("leg_fr", "body", [-2.5, 3.8, -4.3], [
    ("fr_leg", [-3.5, 0.9, -5.3], [2.0, 2.9, 2.0], "leg"),
    ("fr_paw", [-3.7, 0.0, -6.3], [2.4, 1.0, 3.0], "paw"),
])
bone("leg_bl", "root", [2.7, 3.8, 5.8], [
    ("bl_leg", [1.6, 0.9, 4.7], [2.2, 3.0, 2.8], "leg"),
    ("bl_paw", [1.4, 0.0, 3.9], [2.6, 1.0, 3.6], "paw"),
])
bone("leg_br", "root", [-2.7, 3.8, 5.8], [
    ("br_leg", [-3.8, 0.9, 4.7], [2.2, 3.0, 2.8], "leg"),
    ("br_paw", [-4.0, 0.0, 3.9], [2.6, 1.0, 3.6], "paw"),
])

FACES = ["north", "south", "east", "west", "up", "down"]


def face_dims(size, face):
    sx, sy, sz = size
    if face in ("north", "south"):
        return sx, sy
    if face in ("east", "west"):
        return sz, sy
    return sx, sz


# ----------------------------------------------------------------------------
# 2. EMPAQUETADO DE UVs
# ----------------------------------------------------------------------------

def pack(density):
    """Empaqueta todas las caras en un atlas TEX_SIZE x TEX_SIZE. Devuelve dict o None."""
    rects = []
    for b in BONES:
        for (cname, origin, size, zone) in b["cubes"]:
            for f in FACES:
                w, h = face_dims(size, f)
                pw = max(2, int(math.ceil(w * density)))
                ph = max(2, int(math.ceil(h * density)))
                rects.append((cname, f, pw, ph))
    rects.sort(key=lambda r: (-r[3], -r[2]))
    placed = {}
    x = PAD
    y = PAD
    shelf_h = 0
    for (cname, f, pw, ph) in rects:
        if x + pw + PAD > TEX_SIZE:
            x = PAD
            y += shelf_h + PAD
            shelf_h = 0
        if y + ph + PAD > TEX_SIZE:
            return None
        placed[(cname, f)] = (x, y, pw, ph)
        x += pw + PAD
        shelf_h = max(shelf_h, ph)
    return placed


def best_layout():
    d = 16.0
    while d > 4:
        lay = pack(d)
        if lay is not None:
            return d, lay
        d -= 0.5
    sys.exit("No cabe la textura")


# ----------------------------------------------------------------------------
# 3. RUIDO Y COLOR
# ----------------------------------------------------------------------------

def _h(ix, iy, iz, seed):
    n = (ix.astype(np.int64).astype(np.uint32) * np.uint32(374761393)
         + iy.astype(np.int64).astype(np.uint32) * np.uint32(668265263)
         + iz.astype(np.int64).astype(np.uint32) * np.uint32(1274126177)
         + np.uint32((seed * 911382323) & 0xFFFFFFFF))
    n = (n ^ (n >> np.uint32(13))) * np.uint32(1274126177)
    n = n ^ (n >> np.uint32(16))
    return n.astype(np.float64) / 4294967295.0


def vnoise(x, y, z, seed=0):
    xi, yi, zi = np.floor(x), np.floor(y), np.floor(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    u = xf * xf * (3 - 2 * xf)
    v = yf * yf * (3 - 2 * yf)
    w = zf * zf * (3 - 2 * zf)

    def c(dx, dy, dz):
        return _h(xi + dx, yi + dy, zi + dz, seed)

    x00 = c(0, 0, 0) * (1 - u) + c(1, 0, 0) * u
    x10 = c(0, 1, 0) * (1 - u) + c(1, 1, 0) * u
    x01 = c(0, 0, 1) * (1 - u) + c(1, 0, 1) * u
    x11 = c(0, 1, 1) * (1 - u) + c(1, 1, 1) * u
    y0 = x00 * (1 - v) + x10 * v
    y1 = x01 * (1 - v) + x11 * v
    return y0 * (1 - w) + y1 * w


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    t = np.asarray(t)[..., None]
    return a * (1 - t) + b * t


def col(r, g, b):
    return np.array([r, g, b], dtype=np.float64)


C_DARK = col(58, 37, 24)
C_MID = col(94, 62, 38)
C_LIGHT = col(132, 92, 58)
C_BELLY = col(172, 134, 94)
C_CREAM = col(214, 188, 150)


def fur_strands(P, seed, stretch=3.4, scale=1.0):
    x, y, z = P[..., 0] * scale, P[..., 1] * scale, P[..., 2] * scale
    fine = vnoise(x * 13, y * 13, z * stretch, seed) * 0.55 + vnoise(x * 29, y * 29, z * stretch * 2.2, seed + 7) * 0.45
    clump = vnoise(x * 5, y * 5, z * 0.9, seed + 3)
    patch = vnoise(x * 1.3, y * 1.3, z * 1.1, seed + 11)
    return fine, clump, patch


def sparkle(P, seed):
    ix = np.floor(P[..., 0] * 40)
    iy = np.floor(P[..., 1] * 40)
    iz = np.floor(P[..., 2] * 40)
    return _h(ix, iy, iz, seed)


def body_fur(P, seed=1):
    y = P[..., 1]
    z = P[..., 2]
    t = np.clip((y - 2.9) / 6.1, 0, 1)
    base = mix(C_BELLY, C_MID, smooth(0.10, 0.42, t))
    base = mix(base, C_DARK, smooth(0.55, 0.98, t) * 0.85)
    base = mix(base, C_LIGHT, smooth(0.35, 0.55, t) * (1 - smooth(0.55, 0.8, t)) * 0.35)
    # pecho y garganta crema
    chest = smooth(-3.0, -6.5, z) * (1 - smooth(4.2, 6.4, y))
    base = mix(base, C_CREAM, chest * 0.75)
    fine, clump, patch = fur_strands(P, seed)
    shade = (0.74 + 0.5 * fine) * (0.9 + 0.2 * clump)
    base = base * shade[..., None]
    base = base + ((patch - 0.5) * 2)[..., None] * col(9, 4, -3)
    sp = sparkle(P, seed + 5)
    base = np.where((sp > 0.94)[..., None], base * 1.22 + 6, base)
    base = np.where((sp < 0.05)[..., None], base * 0.78, base)
    return base


def head_fur(P, seed=2):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    base = body_fur(P, seed)
    face = smooth(-8.2, -10.8, z) * smooth(8.4, 6.0, y)
    cheek = smooth(2.4, 3.1, np.abs(x)) * smooth(7.2, 5.3, y)
    cream = np.clip(face * 0.65 + cheek * 0.7, 0, 0.9)
    base = mix(base, C_CREAM * 0.92, cream)
    # frente y coronilla mas oscuras
    base = mix(base, C_DARK * 1.15, smooth(7.6, 9.4, y) * 0.55)
    return base


def zone_color(zone, P, N, fu, fv, seed):
    """P: puntos 3D (h,w,3). N: normal (3,). fu/fv: coords de cara 0..1."""
    nx, ny, nz = N
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    if zone == "body":
        c = body_fur(P, seed)
    elif zone == "skull":
        c = head_fur(P, seed)
    elif zone == "fluff":
        fine, clump, patch = fur_strands(P, seed, stretch=2.2, scale=1.3)
        c = mix(C_CREAM * 0.97, C_BELLY, smooth(0.0, 1.0, patch) * 0.5)
        c = c * (0.8 + 0.4 * fine)[..., None]
        top = smooth(6.8, 8.8, y)
        c = mix(c, body_fur(P, seed) * 1.0, top * 0.8)
    elif zone == "muzzle":
        fine, clump, patch = fur_strands(P, seed, stretch=2.5, scale=1.4)
        c = mix(C_CREAM * 0.95, C_BELLY, 0.35 * patch)
        bridge = smooth(6.9, 7.7, y)
        c = mix(c, C_MID * 1.05, bridge * 0.8)
        c = c * (0.82 + 0.34 * fine)[..., None]
        if abs(nx) > 0.5 or nz < -0.5:
            gu = z * 3.4 + 0.6 * np.sign(x) if abs(nx) > 0.5 else x * 3.4
            gv = y * 3.4
            du = (gu - np.floor(gu)) - 0.5
            dv = (gv - np.floor(gv)) - 0.5
            dots = (du * du + dv * dv) < 0.04
            dots &= vnoise(x * 5, y * 5, z * 5, seed + 9) > 0.35
            dots &= (y < 7.0)
            c = np.where(dots[..., None], col(88, 62, 52), c)
    elif zone == "nose":
        n = vnoise(x * 18, y * 18, z * 18, seed)
        c = np.broadcast_to(col(26, 20, 22), P.shape).copy()
        c = c + (n - 0.5)[..., None] * 10
        if ny > 0.5:
            gx = 1 - np.clip(np.abs(fu - 0.5) * 2.4, 0, 1)
            gy = 1 - np.clip(np.abs(fv - 0.45) * 2.6, 0, 1)
            gloss = (gx * gy) ** 1.2
            c = mix(c, col(176, 186, 196), np.clip(gloss * 0.8, 0, 1))
        if nz < -0.5:
            for cx in (0.28, 0.72):
                d = ((fu - cx) / 0.2) ** 2 + ((fv - 0.62) / 0.16) ** 2
                c = np.where((d < 1)[..., None], col(8, 6, 8), c)
            hl = ((fu - 0.5) / 0.35) ** 2 + ((fv - 0.2) / 0.1) ** 2
            c = np.where((hl < 1)[..., None], mix(c, col(150, 156, 166), 0.45 * (1 - hl)), c)
    elif zone == "eye":
        c = np.broadcast_to(col(70, 46, 30), P.shape).copy()
        if nz < -0.5:
            cx, cy = fu - 0.5, fv - 0.5
            r = np.sqrt((cx / 0.5) ** 2 + (cy / 0.5) ** 2)
            c = np.broadcast_to(col(12, 10, 13), P.shape).copy()
            iris = smooth(0.55, 0.9, r) * (1 - smooth(0.9, 1.0, r))
            c = mix(c, col(58, 34, 22), iris * 0.9)
            c = mix(c, body_fur(P, seed + 1) * 0.9, smooth(0.86, 1.02, r))
            h1 = np.sqrt(((fu - 0.67) / 0.19) ** 2 + ((fv - 0.3) / 0.16) ** 2)
            c = mix(c, col(255, 255, 255), np.clip(1 - h1, 0, 1) ** 0.6 * (h1 < 1))
            h2 = np.sqrt(((fu - 0.3) / 0.09) ** 2 + ((fv - 0.72) / 0.08) ** 2)
            c = mix(c, col(190, 200, 215), np.clip(1 - h2, 0, 1) * 0.8 * (h2 < 1))
        else:
            fine, clump, patch = fur_strands(P, seed)
            c = c * (0.7 + 0.5 * fine)[..., None]
    elif zone == "ear":
        c = body_fur(P, seed) * 0.85
        c = mix(c, C_DARK, 0.4)
        if nz < -0.5:
            r = np.sqrt(((fu - 0.5) / 0.5) ** 2 + ((fv - 0.55) / 0.5) ** 2)
            c = mix(c, col(158, 108, 98), smooth(0.8, 0.2, r) * 0.9)
        rim = vnoise(x * 22, y * 22, z * 22, seed + 4)
        c = c * (0.85 + 0.3 * rim)[..., None]
    elif zone == "whisker":
        n = vnoise(x * 6, y * 30, z * 30, seed)
        c = mix(col(226, 216, 196), col(250, 246, 236), n)
    elif zone == "leg":
        c = body_fur(P, seed)
        low = smooth(2.2, 0.9, y)
        c = mix(c, col(48, 32, 22), low * 0.7)
    elif zone == "paw":
        fine, clump, patch = fur_strands(P, seed, stretch=2.0, scale=1.4)
        c = mix(col(52, 36, 26), col(86, 60, 42), patch * 0.6)
        c = c * (0.75 + 0.5 * fine)[..., None]
        if ny > 0.5:      # dorso: separacion de dedos
            tx = fu * 4
            line = np.abs(tx - np.round(tx))
            toe = (line < 0.09) & (fv < 0.55) & (np.round(tx) % 4 != 0)
            c = np.where(toe[..., None], col(22, 15, 12), c)
        if ny < -0.5:     # almohadillas
            c = np.broadcast_to(col(30, 26, 27), P.shape).copy()
            pads = np.zeros(fu.shape, dtype=bool)
            for cx in (0.2, 0.4, 0.6, 0.8):
                pads |= (((fu - cx) / 0.095) ** 2 + ((fv - 0.22) / 0.13) ** 2) < 1
            pads |= (((fu - 0.5) / 0.3) ** 2 + ((fv - 0.66) / 0.22) ** 2) < 1
            tex = vnoise(x * 25, y * 25, z * 25, seed + 2)
            padc = mix(col(70, 58, 57), col(88, 74, 72), tex)
            c = np.where(pads[..., None], padc, c)
        if nz < -0.5:     # garras
            tx = fu * 4
            line = np.abs(tx - np.round(tx))
            claw = (fv > 0.62) & (line > 0.12)
            c = np.where(claw[..., None], col(196, 182, 160), c)
            sep = (line < 0.07) & (np.round(tx) % 4 != 0)
            c = np.where(sep[..., None], col(18, 12, 10), c)
    elif zone == "tail":
        t = np.clip((y - 3.9) / 2.8, 0, 1)
        along = np.clip((z - 7.4) / 13.6, 0, 1)
        base = mix(C_BELLY * 0.85, C_MID, smooth(0.0, 0.5, t))
        base = mix(base, C_DARK, smooth(0.5, 1.0, t) * 0.9)
        base = mix(base, C_DARK * 0.8, along * 0.55)
        fine, clump, patch = fur_strands(P, seed, stretch=1.6)
        base = base * (0.72 + 0.56 * fine)[..., None]
        sp = sparkle(P, seed + 5)
        base = np.where((sp > 0.945)[..., None], base * 1.25 + 5, base)
        c = base
    else:
        c = np.broadcast_to(col(255, 0, 255), P.shape).copy()

    # oclusion ambiental horneada
    shade = 1.0
    if ny < -0.5:
        shade = 0.74
    elif ny > 0.5:
        shade = 1.04
    c = c * shade
    return np.clip(c, 0, 255)


# ----------------------------------------------------------------------------
# 4. TEXTURA + GEO
# ----------------------------------------------------------------------------

def face_points(origin, size, face, fu, fv):
    x0, y0, z0 = origin
    sx, sy, sz = size
    x1, y1, z1 = x0 + sx, y0 + sy, z0 + sz
    if face == "north":
        return x1 - fu * sx, y1 - fv * sy, np.full_like(fu, z0), (0, 0, -1)
    if face == "south":
        return x0 + fu * sx, y1 - fv * sy, np.full_like(fu, z1), (0, 0, 1)
    if face == "west":
        return np.full_like(fu, x0), y1 - fv * sy, z0 + fu * sz, (-1, 0, 0)
    if face == "east":
        return np.full_like(fu, x1), y1 - fv * sy, z1 - fu * sz, (1, 0, 0)
    if face == "up":
        return x1 - fu * sx, np.full_like(fu, y1), z1 - fv * sz, (0, 1, 0)
    return x1 - fu * sx, np.full_like(fu, y0), z0 + fv * sz, (0, -1, 0)


def build_texture_and_geo():
    density, layout = best_layout()
    print(f"densidad de textura: {density} px/unidad  ({TEX_SIZE}x{TEX_SIZE})")
    img = np.zeros((TEX_SIZE, TEX_SIZE, 4), dtype=np.uint8)
    img[..., 3] = 0

    seed_of = {}
    geo_bones = []
    for bi, b in enumerate(BONES):
        gb = {"name": b["name"], "pivot": b["pivot"]}
        if b["parent"]:
            gb["parent"] = b["parent"]
        cubes = []
        for ci, (cname, origin, size, zone) in enumerate(b["cubes"]):
            seed = (sum(ord(ch) for ch in zone) % 50) + 1
            uv = {}
            for f in FACES:
                (u0, v0, pw, ph) = layout[(cname, f)]
                jj, ii = np.mgrid[0:ph, 0:pw]
                fu = (ii + 0.5) / pw
                fv = (jj + 0.5) / ph
                px, py, pz, normal = face_points(origin, size, f, fu, fv)
                P = np.stack([px, py, pz], axis=-1)
                rgb = zone_color(zone, P, normal, fu, fv, seed)
                img[v0:v0 + ph, u0:u0 + pw, :3] = rgb.astype(np.uint8)
                img[v0:v0 + ph, u0:u0 + pw, 3] = 255
                # sangrado de 1 px para evitar costuras
                img[v0 - 1, u0:u0 + pw] = img[v0, u0:u0 + pw]
                img[v0 + ph, u0:u0 + pw] = img[v0 + ph - 1, u0:u0 + pw]
                img[v0:v0 + ph, u0 - 1] = img[v0:v0 + ph, u0]
                img[v0:v0 + ph, u0 + pw] = img[v0:v0 + ph, u0 + pw - 1]
                uv[f] = {"uv": [u0, v0], "uv_size": [pw, ph]}
            cubes.append({"origin": origin, "size": size, "uv": uv})
        if cubes:
            gb["cubes"] = cubes
        geo_bones.append(gb)

    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.otter",
                "texture_width": TEX_SIZE,
                "texture_height": TEX_SIZE,
                "visible_bounds_width": 4,
                "visible_bounds_height": 3,
                "visible_bounds_offset": [0, 0.75, 0],
            },
            "bones": geo_bones,
        }],
    }
    return img, geo


# ----------------------------------------------------------------------------
# 5. ANIMACIONES (Bedrock animation format)
# Convencion: rotacion X positiva = el frente (-Z) baja.
# ----------------------------------------------------------------------------

TAU = 2 * math.pi


def vec(v):
    return [round(float(c), 4) for c in v]


class Anim:
    def __init__(self, length, loop=True, dt=0.05):
        self.length = length
        self.loop = loop
        self.dt = dt
        self.bones = {}

    def chan(self, bone_name, channel, fn):
        steps = int(round(self.length / self.dt))
        keys = {}
        for i in range(steps + 1):
            t = min(i * self.dt, self.length)
            keys[str(round(t, 4))] = vec(fn(t))
        self.bones.setdefault(bone_name, {})[channel] = keys
        return self

    def rot(self, bone_name, fn):
        return self.chan(bone_name, "rotation", fn)

    def pos(self, bone_name, fn):
        return self.chan(bone_name, "position", fn)

    def to_json(self):
        return {"loop": self.loop, "animation_length": self.length, "bones": self.bones}

    def to_json_scaled(self, ts, amp):
        """Copia con el tiempo escalado por ts y las rotaciones por amp (variante 'frenesi', mas rapida y violenta)."""
        bones = {}
        for b, chans in self.bones.items():
            nb = {}
            for ch, keys in chans.items():
                nk = {}
                for k, v in keys.items():
                    nt = str(round(float(k) * ts, 4))
                    nk[nt] = [round(c * amp, 4) for c in v] if ch == "rotation" else v
                nb[ch] = nk
            bones[b] = nb
        return {"loop": self.loop, "animation_length": round(self.length * ts, 4), "bones": bones}


class ScaledAnim:
    def __init__(self, anim, ts, amp):
        self.anim, self.ts, self.amp = anim, ts, amp

    def to_json(self):
        return self.anim.to_json_scaled(self.ts, self.amp)


def smooth_np(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def s(t, period, phase=0.0):
    return math.sin(TAU * t / period + phase)


def tail_wave(a, period, amp_y, amp_x, lag=0.55, base_x=0.0):
    a.rot("tail1", lambda t: [base_x + amp_x * s(t, period, -lag * 0.0), amp_y * 0.5 * s(t, period, -lag * 1), 0])
    a.rot("tail2", lambda t: [amp_x * 1.3 * s(t, period, -lag * 2), amp_y * 0.8 * s(t, period, -lag * 2), 0])
    a.rot("tail3", lambda t: [amp_x * 1.6 * s(t, period, -lag * 3), amp_y * 1.1 * s(t, period, -lag * 3), 0])


def make_animations():
    A = {}

    # ---- idle
    L = 4.0
    a = Anim(L, dt=0.1)
    a.pos("body", lambda t: [0, 0.12 * s(t, 2.0), 0])
    a.rot("head", lambda t: [4 * s(t, L, 0.5), 12 * s(t, L) + 5 * s(t, L / 2), 2 * s(t, L / 2)])
    a.rot("ear_l", lambda t: [0, 0, 5 * max(0, s(t, L / 2, 1.2))])
    a.rot("ear_r", lambda t: [0, 0, -5 * max(0, s(t, L / 2, 2.4))])
    tail_wave(a, L, 10, 2.5)
    A["animation.otter.idle"] = a

    # ---- walk
    L = 0.9
    a = Anim(L)
    for name, ph in (("leg_fl", 0.0), ("leg_br", 0.0), ("leg_fr", math.pi), ("leg_bl", math.pi)):
        a.rot(name, lambda t, ph=ph: [32 * s(t, L, ph), 0, 0])
        a.pos(name, lambda t, ph=ph: [0, 0.7 * max(0, math.cos(TAU * t / L + ph)), 0])
    a.pos("body", lambda t: [0, 0.25 * s(t, L / 2, 0.6), 0])
    a.rot("body", lambda t: [2 * s(t, L / 2, 1.0), 3 * s(t, L), 0])
    a.rot("head", lambda t: [3 * s(t, L / 2, 2.0), -5 * s(t, L), 0])
    tail_wave(a, L, 18, 3, lag=0.6)
    A["animation.otter.walk"] = a

    # ---- run (galope en saltos)
    L = 0.5
    a = Anim(L, dt=0.025)
    for name, ph in (("leg_fl", 0.0), ("leg_fr", 0.15), ("leg_bl", 0.9), ("leg_br", 1.05)):
        a.rot(name, lambda t, ph=ph: [55 * s(t, L, ph), 0, 0])
        a.pos(name, lambda t, ph=ph: [0, 0.8 * max(0, math.cos(TAU * t / L + ph)), 0])
    a.pos("body", lambda t: [0, 0.8 * max(0, s(t, L, 1.2)), 0])
    a.rot("body", lambda t: [9 * s(t, L, 0.4), 2 * s(t, L), 0])
    a.rot("head", lambda t: [-9 * s(t, L, 0.4) - 4, 0, 0])
    a.rot("tail1", lambda t: [10 + 5 * s(t, L, 0.8), 6 * s(t, L), 0])
    a.rot("tail2", lambda t: [6 + 6 * s(t, L, 1.2), 10 * s(t, L, -0.5), 0])
    a.rot("tail3", lambda t: [4 + 8 * s(t, L, 1.6), 14 * s(t, L, -1.0), 0])
    A["animation.otter.run"] = a

    # ---- swim
    L = 1.0
    a = Anim(L)
    a.rot("body", lambda t: [6 * s(t, L), 0, 0])
    a.pos("body", lambda t: [0, -0.4 + 0.3 * s(t, L, 0.5), 0])
    a.rot("head", lambda t: [-8 - 4 * s(t, L, 0.8), 0, 0])
    a.rot("leg_fl", lambda t: [70 + 8 * s(t, L), 0, 0])
    a.rot("leg_fr", lambda t: [70 + 8 * s(t, L, 0.4), 0, 0])
    a.rot("leg_bl", lambda t: [40 + 35 * s(t, L), 0, 0])
    a.rot("leg_br", lambda t: [40 + 35 * s(t, L, math.pi), 0, 0])
    tail_wave(a, L, 22, 14, lag=0.55)
    A["animation.otter.swim"] = a

    # ---- swim_idle
    L = 3.0
    a = Anim(L, dt=0.1)
    a.pos("body", lambda t: [0, -0.4 + 0.25 * s(t, L), 0])
    a.rot("body", lambda t: [3 * s(t, L, 0.7), 0, 0])
    a.rot("head", lambda t: [-6 + 3 * s(t, L, 1.0), 8 * s(t, L / 1.0), 0])
    a.rot("leg_fl", lambda t: [45 + 12 * s(t, L / 2), 0, 0])
    a.rot("leg_fr", lambda t: [45 + 12 * s(t, L / 2, math.pi), 0, 0])
    a.rot("leg_bl", lambda t: [30 + 15 * s(t, L / 2, 1.0), 0, 0])
    a.rot("leg_br", lambda t: [30 + 15 * s(t, L / 2, 1.0 + math.pi), 0, 0])
    tail_wave(a, L, 14, 6, lag=0.5)
    A["animation.otter.swim_idle"] = a

    # ---- back_float (flotar boca arriba)
    L = 5.0
    a = Anim(L, dt=0.1)
    a.rot("root", lambda t: [0, 0, 180])
    a.pos("root", lambda t: [0, 0.8 + 0.2 * s(t, L), 0])
    a.rot("body", lambda t: [2 * s(t, L, 0.5), 0, 4 * s(t, L)])
    a.rot("head", lambda t: [-18, 6 * s(t, L), 0])
    a.rot("leg_fl", lambda t: [68 + 4 * s(t, L / 2), 0, 0])
    a.rot("leg_fr", lambda t: [68 + 4 * s(t, L / 2, 0.5), 0, 0])
    a.rot("leg_bl", lambda t: [22 + 10 * s(t, L / 2, 1.0), 0, 0])
    a.rot("leg_br", lambda t: [22 + 10 * s(t, L / 2, 2.0), 0, 0])
    tail_wave(a, L, 14, 5, lag=0.5)
    A["animation.otter.back_float"] = a

    # ---- sit (sentada, erguida)
    L = 3.0
    a = Anim(L, dt=0.1)
    a.rot("body", lambda t: [-32 + 0.8 * s(t, L / 2), 0, 0])
    a.pos("body", lambda t: [0, -2.0 + 0.08 * s(t, L / 2), 0])
    a.rot("head", lambda t: [26 + 3 * s(t, L), 14 * s(t, L, 0.3), 0])
    a.rot("leg_fl", lambda t: [58 + 3 * s(t, L / 2), 0, 0])
    a.rot("leg_fr", lambda t: [58 + 3 * s(t, L / 2, 0.8), 0, 0])
    a.rot("leg_bl", lambda t: [-78, 0, 0])
    a.rot("leg_br", lambda t: [-78, 0, 0])
    a.pos("leg_bl", lambda t: [0, -2.5, 0])
    a.pos("leg_br", lambda t: [0, -2.5, 0])
    a.rot("ear_l", lambda t: [0, 0, 4 * max(0, s(t, L, 0.4))])
    tail_wave(a, L, 8, 2, lag=0.5, base_x=-6)
    A["animation.otter.sit"] = a

    # ---- sleep (acurrucada)
    L = 4.0
    a = Anim(L, dt=0.1)
    a.pos("body", lambda t: [0, -2.1 + 0.1 * s(t, L / 2), 0])
    a.rot("body", lambda t: [4, 0, 0])
    a.rot("head", lambda t: [38, 28, 0])
    a.rot("leg_fl", lambda t: [-70, 0, 0])
    a.rot("leg_fr", lambda t: [-70, 0, 0])
    a.rot("leg_bl", lambda t: [-82, 0, 0])
    a.rot("leg_br", lambda t: [-82, 0, 0])
    for n in ("leg_fl", "leg_fr", "leg_bl", "leg_br"):
        a.pos(n, lambda t: [0, -2.2, 0])
    a.rot("tail1", lambda t: [0, 35, 0])
    a.rot("tail2", lambda t: [0, 48, 0])
    a.rot("tail3", lambda t: [0, 58, 0])
    a.rot("ear_l", lambda t: [0, 0, 0])
    A["animation.otter.sleep"] = a

    # ---- scratch (sentada, rascandose con la pata trasera)
    L = 0.5
    a = Anim(L, dt=0.025)
    a.rot("body", lambda t: [-32, 0, 0])
    a.pos("body", lambda t: [0, -2.0, 0])
    a.rot("head", lambda t: [30, 0, 12])
    a.rot("leg_fl", lambda t: [58, 0, 0])
    a.rot("leg_fr", lambda t: [58, 0, 0])
    a.rot("leg_bl", lambda t: [-50 + 40 * s(t, L / 2), 0, 0])
    a.pos("leg_bl", lambda t: [0, -1.4, 0])
    a.rot("leg_br", lambda t: [-78, 0, 0])
    a.pos("leg_br", lambda t: [0, -2.5, 0])
    tail_wave(a, L, 6, 2, lag=0.5, base_x=-6)
    A["animation.otter.scratch"] = a

    # ---- sniff
    L = 1.6
    a = Anim(L, dt=0.05)
    a.rot("head", lambda t: [14 + 8 * s(t, L / 4), 15 * s(t, L), 0])
    a.pos("head", lambda t: [0, 0.2 * s(t, L / 4, 1.0), 0])
    a.rot("ear_l", lambda t: [0, 0, 6 * s(t, L / 4)])
    a.rot("ear_r", lambda t: [0, 0, -6 * s(t, L / 4, 1.5)])
    a.rot("body", lambda t: [3, 0, 0])
    tail_wave(a, L, 8, 2, lag=0.5)
    A["animation.otter.sniff"] = a

    # ---- shake (sacudirse el agua)
    L = 0.6
    a = Anim(L, dt=0.025)
    a.rot("body", lambda t: [0, 16 * s(t, L / 4), 0])
    a.rot("head", lambda t: [0, -22 * s(t, L / 4), 0])
    a.rot("tail1", lambda t: [0, -20 * s(t, L / 4), 0])
    a.rot("tail2", lambda t: [0, -30 * s(t, L / 4, -0.5), 0])
    a.rot("tail3", lambda t: [0, -40 * s(t, L / 4, -1.0), 0])
    a.rot("ear_l", lambda t: [0, 0, 12 * s(t, L / 4)])
    a.rot("ear_r", lambda t: [0, 0, -12 * s(t, L / 4)])
    A["animation.otter.shake"] = a


    # ---- suspicious: inmovil, cabeza inclinada de forma antinatural, temblando
    L = 4.0
    a = Anim(L, dt=0.05)
    a.pos("body", lambda t: [0.07 * s(t, 0.22), 0.08 * s(t, 0.6), 0])
    a.rot("body", lambda t: [0, 0, 1.2 * s(t, 0.22, 1.0)])
    a.rot("head", lambda t: [-3 + 2 * s(t, 0.3), 16 + 9 * max(0, s(t, 4.0, 1.0)) ** 3, 38 + 4 * s(t, 0.2)])
    a.rot("ear_l", lambda t: [0, 0, 22])
    a.rot("ear_r", lambda t: [0, 0, -22])
    a.rot("jaw", lambda t: [3 * abs(s(t, 0.4)), 0, 0])
    for name in ("leg_fl", "leg_fr", "leg_bl", "leg_br"):
        a.rot(name, lambda t: [4 * s(t, 0.22, 0.5), 0, 0])
    a.rot("tail1", lambda t: [-10, 1.5 * s(t, 0.25), 0])
    a.rot("tail2", lambda t: [-8, 2 * s(t, 0.25, 0.4), 0])
    a.rot("tail3", lambda t: [-6, 2.5 * s(t, 0.25, 0.8), 0])
    A["animation.otter.suspicious"] = a

    # ---- transform (fase A, modelo normal): se detiene, tiembla, la cabeza se tuerce,
    #      la mandibula se abre, la columna se arquea y el cuerpo se deforma
    L = 3.5
    a = Anim(L, loop="hold_on_last_frame", dt=0.05)

    def ss(a_, b_, t):
        return float(smooth_np(a_, b_, t))

    def trem(t):
        return s(t, 0.11) + 0.5 * s(t, 0.07, 1.0)

    def envs(t):
        return ss(0.3, 1.2, t) * (1 - 0.4 * ss(2.4, 3.2, t))
    arch = lambda t: ss(1.8, 3.0, t)
    a.pos("body", lambda t: [0.3 * trem(t) * envs(t), 1.2 * arch(t) * 0 + 0.1 * trem(t) * envs(t), 0])
    a.rot("body", lambda t: [-20 * arch(t) + 2 * trem(t) * envs(t), 4 * trem(t) * envs(t), 3 * trem(t) * envs(t)])
    a.chan("body", "scale", lambda t: [1, 1 - 0.1 * arch(t), 1 + 0.25 * arch(t)])
    a.pos("root", lambda t: [0, 1.8 * ss(1.8, 3.2, t), 0])
    a.rot("head", lambda t: [-16 * ss(2.6, 3.2, t) + 3 * trem(t) * envs(t),
                             38 * ss(0.9, 1.6, t) - 70 * ss(2.3, 2.45, t) + 5 * trem(t) * envs(t),
                             55 * ss(0.8, 1.3, t) - 25 * ss(2.4, 2.6, t) + 6 * trem(t) * envs(t)])
    a.rot("jaw", lambda t: [58 * ss(1.4, 2.4, t) + 4 * trem(t) * ss(1.6, 2.6, t), 0, 0])
    a.rot("ear_l", lambda t: [0, 0, 32 * ss(0.8, 1.4, t)])
    a.rot("ear_r", lambda t: [0, 0, -32 * ss(0.8, 1.4, t)])
    for name, ph in (("leg_fl", 0.0), ("leg_fr", 1.3), ("leg_bl", 2.1), ("leg_br", 0.7)):
        a.rot(name, lambda t, ph=ph: [14 * ss(1.6, 2.8, t) + 6 * s(t, 0.1, ph) * envs(t), 0, 0])
        a.chan(name, "scale", lambda t: [1, 1 + 0.5 * ss(1.8, 3.2, t), 1])
    a.chan("tail1", "scale", lambda t: [1, 1, 1 + 0.6 * ss(1.8, 3.2, t)])
    a.rot("tail1", lambda t: [10 * ss(1.8, 3.0, t), 14 * trem(t) * envs(t), 0])
    a.rot("tail2", lambda t: [14 * ss(1.8, 3.0, t), 22 * trem(t) * envs(t), 0])
    a.rot("tail3", lambda t: [18 * ss(1.8, 3.0, t), 30 * trem(t) * envs(t), 0])
    A["animation.otter.transform"] = a
    A["animation.otter.transform_frenzy"] = ScaledAnim(a, 2.0 / 3.5, 1.35)   # 2 s, mas violenta

    # ---- untransform (modelo normal): vuelve a la normalidad, temblando y relajandose
    L = 2.0
    a = Anim(L, loop="hold_on_last_frame", dt=0.05)

    def decay(t):
        return 1 - smooth_np(0.0, 1.6, t)
    a.pos("body", lambda t: [0.25 * s(t, 0.1) * decay(t), -1.6 * decay(t) ** 2, 0])
    a.rot("body", lambda t: [6 * decay(t), 3 * s(t, 0.1, 1.0) * decay(t), 3 * s(t, 0.12) * decay(t)])
    a.rot("head", lambda t: [34 * decay(t) ** 2, 22 * s(t, 0.5) * decay(t), 14 * decay(t)])
    a.rot("jaw", lambda t: [26 * decay(t) ** 2, 0, 0])
    for name in ("leg_fl", "leg_fr", "leg_bl", "leg_br"):
        a.rot(name, lambda t: [-16 * decay(t) ** 2, 0, 0])
    a.rot("tail1", lambda t: [-6 * decay(t), 10 * s(t, 0.2) * decay(t), 0])
    a.rot("tail2", lambda t: [-6 * decay(t), 14 * s(t, 0.2, 0.5) * decay(t), 0])
    a.rot("tail3", lambda t: [-6 * decay(t), 18 * s(t, 0.2, 1.0) * decay(t), 0])
    A["animation.otter.untransform"] = a

    return {
        "format_version": "1.8.0",
        "animations": {k: v.to_json() for k, v in A.items()},
    }


# ----------------------------------------------------------------------------

def make_corrupt(img):
    """Version 'corrompida' del pelaje (fase intermedia de la transformacion)."""
    out = img.copy()
    rgb = img[..., :3].astype(np.float64)
    lum = rgb.mean(axis=-1, keepdims=True)
    dark = (rgb * 0.40 + lum * 0.12) * np.array([0.85, 0.92, 1.15])
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    zeros = np.zeros_like(xx)
    veins = np.abs(vnoise(xx * 0.05, yy * 0.05, zeros, 91) - 0.5) < 0.018
    dark = np.where(veins[..., None], np.array([96.0, 24.0, 52.0]), dark)
    patch = vnoise(xx * 0.03, yy * 0.03, zeros, 92) > 0.68
    dark = np.where(patch[..., None], dark * 0.6 + np.array([40.0, 34.0, 40.0]) * 0.4, dark)
    out[..., :3] = np.clip(dark, 0, 255).astype(np.uint8)
    return out


def main():
    os.makedirs(os.path.join(ASSETS, "geo"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "animations"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "textures", "entity"), exist_ok=True)
    img, geo = build_texture_and_geo()
    Image.fromarray(img, "RGBA").save(os.path.join(ASSETS, "textures", "entity", "otter.png"), optimize=True)
    corrupt = make_corrupt(img)
    Image.fromarray(corrupt, "RGBA").save(os.path.join(ASSETS, "textures", "entity", "otter_corrupt.png"), optimize=True)
    cglow = np.zeros((TEX_SIZE, TEX_SIZE, 4), dtype=np.uint8)
    cglow[0, 0] = (0, 0, 0, 255)
    Image.fromarray(cglow, "RGBA").save(os.path.join(ASSETS, "textures", "entity", "otter_corrupt_glowmask.png"))
    # mascara de brillo de la nutria normal: GeckoLib exige al menos un pixel NO transparente.
    # (0,0) no esta usado por ninguna cara y el negro emisivo no se ve.
    glow = np.zeros((TEX_SIZE, TEX_SIZE, 4), dtype=np.uint8)
    glow[0, 0] = (0, 0, 0, 255)
    Image.fromarray(glow, "RGBA").save(os.path.join(ASSETS, "textures", "entity", "otter_glowmask.png"))
    with open(os.path.join(ASSETS, "geo", "otter.geo.json"), "w") as f:
        json.dump(geo, f, indent=1)
    with open(os.path.join(ASSETS, "animations", "otter.animation.json"), "w") as f:
        json.dump(make_animations(), f, separators=(",", ":"))
    print("OK")


if __name__ == "__main__":
    main()
