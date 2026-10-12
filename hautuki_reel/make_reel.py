#!/usr/bin/env python3
"""하우투키 앰버서더 릴스(9:16) 자동 편집 스크립트.

사용법: python3 make_reel.py <원본영상폴더> <출력.mp4> <폰트폴더>
필요: ffmpeg(zscale/tonemap/xfade 포함), Pillow
"""
import glob
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

SRC, OUT, FONTS = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1920, 30
XF = 0.4  # 크로스페이드 길이(초)
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_work")
os.makedirs(WORK, exist_ok=True)

FONT_HEAVY = os.path.join(FONTS, "noto-sans-kr-900.ttf")
FONT_BOLD = os.path.join(FONTS, "noto-sans-kr-700.ttf")

# iPhone HLG(HDR) -> SDR 변환
TONEMAP = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=203,"
           "format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def src(name):
    return glob.glob(os.path.join(SRC, f"*{name}.MOV"))[0]


# (파일, 시작, 길이, 추가 필터)
CLIPS = [
    ("IMG_7617", 1.2, 14.0, ""),           # 첫 화면: 패치 개봉 -> 부착 -> 미소
    ("IMG_7585", 0.0, 4.6, ""),            # 성장 기록 벽 + 세 아이 키
    ("IMG_7588", 6.0, 4.6, ""),            # 펜으로 키 표시
    ("IMG_7586", 6.0, 4.6, "transpose=1,"),  # 키 재기(원본이 옆으로 찍힘)
    ("IMG_7587", 0.0, 5.0, ""),            # 엔딩
]

# 자막: (시작, 끝, 메인, 서브)
starts, t = [], 0.0
for i, c in enumerate(CLIPS):
    starts.append(t)
    t += c[2] - XF
TOTAL = t + XF
s = starts
CAPTIONS = [
    (0.0, s[0] + 5.6, "하우투키 첫 개봉!", "키즈 웰니스 영양소 패치, 처음 써봐요"),
    (s[0] + 5.8, s[0] + 10.4, "떼서 붙이면 끝!", "아이 혼자서도 쉽게 붙였어요"),
    (s[0] + 10.6, s[1] + 0.1, "비타민D3 + 비타민K2", "어린이·청소년기 영양·흡수 균형 서포트"),
    (s[2] + 0.3, s[3] + 0.1, "오늘도 키 재는 날!", "부모라면 늘 신경 쓰이는 우리 아이 키"),
    (s[3] + 0.3, s[4] + 0.1, "국내 유일\n어린이 인체적용시험", "서울대학교 특허 흡수율 업그레이드 시스템"),
]
HEIGHTS = [("첫째", "161"), ("둘째", "144"), ("셋째", "133")]
HEIGHTS_TIME = (s[1] + 0.3, s[2] + 0.1)
END_START = s[4] + 0.3


def run(cmd):
    print(" ".join(cmd[:6]), "...")
    subprocess.run(cmd, check=True)


def text_size(draw, text, font):
    l, t_, r, b = draw.multiline_textbbox((0, 0), text, font=font, spacing=10)
    return r - l, b - t_, l, t_


def caption_png(path, main, sub, y_center=1290):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fm = ImageFont.truetype(FONT_HEAVY, 92)
    fs = ImageFont.truetype(FONT_BOLD, 44)
    mw, mh, ml, mt = text_size(d, main, fm)
    sw, sh, sl, st = text_size(d, sub, fs)
    gap = 34
    total_h = mh + gap + sh + 36
    y = y_center - total_h // 2
    # 메인: 흰 글씨 + 검정 외곽선
    d.multiline_text(((W - mw) / 2 - ml, y - mt), main, font=fm, fill="white",
                     stroke_width=9, stroke_fill=(20, 20, 20), align="center", spacing=10)
    # 서브: 노란 라운드 박스
    by = y + mh + gap
    pad_x, pad_y = 34, 18
    box = [(W - sw) / 2 - pad_x, by, (W + sw) / 2 + pad_x, by + sh + pad_y * 2]
    d.rounded_rectangle(box, radius=(sh + pad_y * 2) // 2, fill=(255, 214, 64, 245))
    d.text(((W - sw) / 2 - sl, by + pad_y - st), sub, font=fs, fill=(30, 30, 30))
    img.save(path)


def badge_png(path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_BOLD, 34)
    text = "광고 | 하우투키 앰버서더"
    w, h, l, t_ = text_size(d, text, f)
    x, y = 48, 150
    d.rounded_rectangle([x, y, x + w + 44, y + h + 28], radius=16, fill=(0, 0, 0, 150))
    d.text((x + 22 - l, y + 14 - t_), text, font=f, fill="white")
    img.save(path)


def heights_png(path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(FONT_HEAVY, 88)
    fl = ImageFont.truetype(FONT_BOLD, 54)
    fn = ImageFont.truetype(FONT_HEAVY, 96)
    title = "사용 시작 전 키 기록"
    w, h, l, t_ = text_size(d, title, ft)
    d.text(((W - w) / 2 - l, 760 - t_), title, font=ft, fill="white",
           stroke_width=9, stroke_fill=(20, 20, 20))
    y = 920
    for label, cm in HEIGHTS:
        box = [150, y, W - 150, y + 150]
        d.rounded_rectangle(box, radius=40, fill=(255, 255, 255, 235))
        lw, lh, ll, lt = text_size(d, label, fl)
        d.text((210 - ll, y + 75 - lh / 2 - lt), label, font=fl, fill=(90, 90, 90))
        num = f"{cm}cm"
        nw, nh, nl, nt = text_size(d, num, fn)
        d.text((W - 210 - nw - nl, y + 75 - nh / 2 - nt), num, font=fn, fill=(30, 30, 30))
        y += 180
    img.save(path)


def end_png(path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 하단 그라데이션
    for i in range(700):
        a = int(200 * (i / 700) ** 1.5)
        d.line([(0, H - 700 + i), (W, H - 700 + i)], fill=(0, 0, 0, a))
    f1 = ImageFont.truetype(FONT_HEAVY, 84)
    f2 = ImageFont.truetype(FONT_BOLD, 46)
    f3 = ImageFont.truetype(FONT_HEAVY, 60)
    lines = [
        ("한 달 뒤에\n다시 재볼게요!", f1, "white", 1180),
        ("우리 아이 영양루틴은 하우투키로", f2, (255, 214, 64), 1420),
        ("@hautuki.official", f3, "white", 1520),
    ]
    for text, f, color, y in lines:
        w, h, l, t_ = text_size(d, text, f)
        d.multiline_text(((W - w) / 2 - l, y - t_), text, font=f, fill=color,
                         stroke_width=6, stroke_fill=(20, 20, 20), align="center", spacing=10)
    img.save(path)


# 1) 각 클립을 1080x1920 SDR 30fps로 정규화
segs = []
for i, (name, ss, dur, pre) in enumerate(CLIPS):
    out = os.path.join(WORK, f"seg{i}.mp4")
    vf = (f"{pre}{TONEMAP},scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},fps={FPS},setsar=1,eq=saturation=1.08:contrast=1.03")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(dur), "-i", src(name),
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])
    segs.append(out)

# 2) 오버레이 이미지 생성
badge = os.path.join(WORK, "badge.png"); badge_png(badge)
endc = os.path.join(WORK, "end.png"); end_png(endc)
caps = []
hp = os.path.join(WORK, "heights.png"); heights_png(hp); caps.append((hp, *HEIGHTS_TIME))
for i, (a, b, m, sub) in enumerate(CAPTIONS):
    p = os.path.join(WORK, f"cap{i}.png"); caption_png(p, m, sub); caps.append((p, a, b))

# 3) 크로스페이드 이어붙이기 + 자막 오버레이
inputs = []
for sgm in segs:
    inputs += ["-i", sgm]
overlays = [(badge, 0, TOTAL)] + caps + [(endc, END_START, TOTAL)]
for p, a, b in overlays:
    inputs += ["-loop", "1", "-t", f"{TOTAL:.2f}", "-i", p]

fc, last = [], "[0:v]"
for i in range(1, len(segs)):
    off = starts[i]
    fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}]")
    last = f"[x{i}]"
n = len(segs)
for j, (p, a, b) in enumerate(overlays):
    k = n + j
    fades = []
    if a > 0.01:
        fades.append(f"fade=t=in:st={a:.2f}:d=0.25:alpha=1")
    if b < TOTAL - 0.01:
        fades.append(f"fade=t=out:st={b - 0.25:.2f}:d=0.25:alpha=1")
    fade = ",".join(fades) or "null"
    fc.append(f"[{k}:v]format=rgba,{fade}[o{j}]")
    fc.append(f"{last}[o{j}]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{j}]")
    last = f"[v{j}]"
fc.append(f"{last}fade=t=out:st={TOTAL - 0.5:.2f}:d=0.5,format=yuv420p[vout]")

# 무음 오디오 트랙(인스타그램에서 음악 추가용)
run(["ffmpeg", "-v", "error", "-y", *inputs,
     "-f", "lavfi", "-t", f"{TOTAL:.2f}", "-i", "anullsrc=r=48000:cl=stereo",
     "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n + len(overlays)}:a",
     "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
     "-c:a", "aac", "-b:a", "128k", "-r", str(FPS), "-movflags", "+faststart",
     "-t", f"{TOTAL:.2f}", OUT])
print(f"완료: {OUT} ({TOTAL:.1f}초)")
