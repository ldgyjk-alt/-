#!/usr/bin/env python3
"""하우투키 앰버서더 릴스 2탄(9:16) 자동 편집 스크립트.

순서: 제품 -> 키 재기 -> 측정값 -> 아이가 직접 부착 -> 침대에서 마무리
사용법: python3 make_reel2.py <원본영상폴더> <출력.mp4> <폰트폴더>
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
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_work2")
os.makedirs(WORK, exist_ok=True)

FONT_HEAVY = os.path.join(FONTS, "noto-sans-kr-900.ttf")
FONT_BOLD = os.path.join(FONTS, "noto-sans-kr-700.ttf")

# iPhone HLG(HDR) -> SDR 변환
TONEMAP = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=203,"
           "format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")


def src(prefix):
    return glob.glob(os.path.join(SRC, f"{prefix}*.MOV"))[0]


# (파일 접두어, 시작, 길이, HDR 여부)
CLIPS = [
    ("68084c29", 0.3, 6.2, True),    # 1. 제품 박스
    ("6f0f3e89", 0.2, 4.6, False),   # 2. 벽에 서서 키 재기
    ("8c50f7c0", 0.0, 2.4, False),   # 3. 측정값 클로즈업
    ("247c96dc", 2.6, 10.0, False),  # 4. 아이가 직접 떼서 붙이고 웃음
    ("fa607f33", 1.4, 5.4, False),   # 5. 침대에서 패치 보여주며 마무리
]

starts, t = [], 0.0
for c in CLIPS:
    starts.append(t)
    t += c[2] - XF
TOTAL = t + XF
s = starts

TOP, LOW = 330, 1290  # 자막 세로 위치(아이 손/얼굴을 가리지 않도록 클립별 선택)
# 자막: (시작, 끝, 메인, 서브, 세로중심)
CAPTIONS = [
    (0.0, 3.2, "하우투키 도착!", "키즈 웰니스 영양소 패치", LOW),
    (3.4, s[1] + 0.1, "비타민D3 + 비타민K2", "어린이·청소년기 영양 균형 서포트", LOW),
    (s[1] + 0.3, s[3] + 0.1, "오늘의 키 기록", "성장 기록은 꾸준히!", TOP),
    (s[3] + 0.3, s[3] + 6.6, "혼자서도 척척!", "떼서 붙이기만 하면 끝", TOP),
    (s[3] + 6.8, s[4] + 0.1, "흡수율까지 꼼꼼하게", "서울대학교 특허 흡수율 업그레이드 시스템", TOP),
]
END_START = s[4] + 0.4


def run(cmd):
    print(" ".join(cmd[:6]), "...")
    subprocess.run(cmd, check=True)


def text_size(draw, text, font):
    l, t_, r, b = draw.multiline_textbbox((0, 0), text, font=font, spacing=10)
    return r - l, b - t_, l, t_


def caption_png(path, main, sub, y_center):
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
        ("오늘 밤도\n하우투키와 함께", f1, "white", 1180),
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
for i, (name, ss, dur, hdr) in enumerate(CLIPS):
    out = os.path.join(WORK, f"seg{i}.mp4")
    vf = (f"{TONEMAP if hdr else ''}scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},fps={FPS},setsar=1,eq=saturation=1.08:contrast=1.03,format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(dur), "-i", src(name),
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])
    segs.append(out)

# 2) 오버레이 이미지 생성
badge = os.path.join(WORK, "badge.png"); badge_png(badge)
endc = os.path.join(WORK, "end.png"); end_png(endc)
caps = []
for i, (a, b, m, sub, yc) in enumerate(CAPTIONS):
    p = os.path.join(WORK, f"cap{i}.png"); caption_png(p, m, sub, yc); caps.append((p, a, b))

# 3) 크로스페이드 이어붙이기 + 자막 오버레이
inputs = []
for sgm in segs:
    inputs += ["-i", sgm]
overlays = [(badge, 0, TOTAL)] + caps + [(endc, END_START, TOTAL)]
for p, a, b in overlays:
    inputs += ["-loop", "1", "-t", f"{TOTAL:.2f}", "-i", p]

fc, last = [], "[0:v]"
for i in range(1, len(segs)):
    fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={XF}:offset={starts[i]:.2f}[x{i}]")
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
