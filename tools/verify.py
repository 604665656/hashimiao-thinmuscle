# -*- coding: utf-8 -*-
"""薄肌浓度检测仪 · 正式版 静态校验。

用法：
    python boji/tools/verify.py                 # 校验 Pages 根 index.html
    python boji/tools/verify.py boji/toy/index.html
"""
import os
import re
import sys
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT = os.path.join(ROOT, "boji", "index.html")
EXPECT_BYTES = 758937
EXPECT_SHA16 = "6e414053e514f67c"


def main():
    p = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    raw = open(p, "rb").read()
    h = raw.decode("utf-8", "replace")
    sha16 = hashlib.sha256(raw).hexdigest()[:16]
    t = re.search(r"<title[^>]*>(.*?)</title>", h, re.S | re.I)
    title = t.group(1).strip() if t else ""

    checks = [
        ("体积 758937 B", len(raw) == EXPECT_BYTES),
        ("体积 < 1MiB（Toy 入口）", len(raw) < 1048576),
        ("SHA256 前 16 位一致", sha16 == EXPECT_SHA16),
        ("标题正确", title == "薄肌浓度检测仪 · 陪练桌宠"),
        ("1 段内联 script", len(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>", h, re.I)) == 1),
        ("0 个 script[src]", len(re.findall(r"<script[^>]*\bsrc=", h, re.I)) == 0),
        ("1 段 style", len(re.findall(r"<style", h, re.I)) == 1),
        ("0 个 link[stylesheet]", len(re.findall(r"<link[^>]*stylesheet", h, re.I)) == 0),
        ("0 个 http(s) src/href", len(re.findall(r'(?:src|href)=["\']https?://', h, re.I)) == 0),
        ("内嵌素材 43 张", h.count("data:image") == 43),
        ("零 fetch(", h.count("fetch(") == 0),
        ("零 XMLHttpRequest", h.count("XMLHttpRequest") == 0),
        ("GALLERY 清单唯一 const", h.count("const GALLERY") == 1 and h.count("var GALLERY") == 0),
        ("12 周周次逻辑 weekOf", "weekOf" in h),
        ("跨周浓度口径 scoreIntoWeek", "scoreIntoWeek" in h),
        ("打卡 / 存档码文案", "打卡" in h and "存档码" in h),
        ("Canvas 成绩卡能力", h.count("getContext") >= 2),
        ("localStorage 本机存档", h.count("localStorage") >= 10),
        ("隐私口径：照片不上传", "不上传" in h),
        ("深链 ?tab= 支持", "?tab=" in h),
        ("HTML 闭合", h.rstrip().endswith("</html>")),
    ]

    ok = 0
    for name, passed in checks:
        print(("  PASS  " if passed else "  FAIL  ") + name)
        ok += int(bool(passed))
    print("\n%d/%d PASS  ->  %s  (%d B, sha16=%s)" %
          (ok, len(checks), os.path.relpath(p, ROOT), len(raw), sha16))
    return 0 if ok == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
