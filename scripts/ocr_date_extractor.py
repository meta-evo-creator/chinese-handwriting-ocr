"""ocr_date_extractor.py - 鎵嬪啓鏃ユ湡鎻愬彇寮曟搸 v4 (瀹炵敤鐗?
鏀硅繘:
1. 鍔ㄦ€佹棩鏈熻瀹氫綅 鈫?涓嶄緷璧栧浐瀹氳鍓?2. 鍗曞抚楂樼簿搴CR 鈫?蹇?
3. 鏅鸿兘鍚庡鐞嗘牎楠?鈫?淇OCR甯歌閿欒
"""
import sys, os, re, json, argparse
from rapidocr_onnxruntime import RapidOCR
from collections import Counter
import fitz

_ENGINE = None
def engine():
    global _ENGINE
    if _ENGINE is None: _ENGINE = RapidOCR()
    return _ENGINE

def _ocr(img):
    e = engine()
    return e(img)

# 鈹€鈹€鈹€ 1. 鍔ㄦ€佸畾浣?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def find_date_line(page):
    """鍏ㄩ〉浣庡垎OCR鎵惧寘鍚?鏈?鐨勮"""
    pix = page.get_pixmap(dpi=150)
    tmp = os.path.join(os.environ['TEMP'], f'_dl_{id(page)}.png')
    pix.save(tmp)
    res, _ = _ocr(tmp)
    try: os.remove(tmp)
    except: pass
    
    best = None
    for bbox,text,conf in (res or []):
        if '鏈? in text:
            y1 = bbox[0][1]/pix.height
            y2 = bbox[2][1]/pix.height
            if best is None or conf > best[2]:
                best = (y1, y2, conf, text[:20])
    
    if best: return best[0], best[1]
    return 0.46, 0.60  # fallback

# 鈹€鈹€鈹€ 2. 鏃ユ湡OCR (鍗曞抚楂樼簿搴? 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def read_date(page, crop):
    pix = page.get_pixmap(dpi=450, clip=crop)
    tmp = os.path.join(os.environ['TEMP'], f'_rd_{id(page)}.png')
    pix.save(tmp)
    res, _ = _ocr(tmp)
    try: os.remove(tmp)
    except: pass
    
    # 瑙ｆ瀽鏃ユ湡缁勪欢
    year=month=day=''
    for _,text,conf in (res or []):
        m = re.search(r'(\d{4})\s*骞?, text)
        if m: year = m.group(1)
        m = re.search(r'(\d{1,2})\s*鏈?, text)
        if m: month = m.group(1)
        m = re.search(r'(?:鏈圽s*)?(\d{1,2})\s*鏃?, text)
        if m:
            d = m.group(1)
            # 濡傛灉鏃ユ槸1-9浣嗛檮杩戞湁"1"锛屽彲鑳芥槸婕忎簡鍓嶅
            if len(d)==1 and '1' in text[max(0,m.start()-3):m.start()]:
                day = '1'+d
            else:
                day = d
    
    parts = []
    if year: parts.append(f"{year}骞?)
    if month: parts.append(f"{int(month):02d}鏈?)
    if day: parts.append(f"{int(day):02d}鏃?)
    return ''.join(parts) or 'UNKDATE'

# 鈹€鈹€鈹€ 3. 鏅鸿兘鏍￠獙 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def smart_check(d, cy=2026):
    if not d or d=='UNKDATE': return 'UNKDATE'
    
    y=m=day=''
    mm = re.search(r'(\d{4})骞?, d)
    if mm: y=mm.group(1)
    mm = re.search(r'(\d{1,2})鏈?, d)
    if mm: m=mm.group(1)
    mm = re.search(r'(\d{1,2})鏃?, d)
    if mm: day=mm.group(1)
    
    # 骞?(with smart correction for 2->5/7 misread)
    if y:
        yi = int(y)
        if yi > cy:
            # Try correcting: '5'/'7' in year are often misread '2'
            y_fixed = y.replace('5','2').replace('7','2')
            yi_fixed = int(y_fixed)
            if 2020 <= yi_fixed <= cy:
                y = y_fixed
                yi = yi_fixed
        if yi > cy+1:
            y = str(cy-1)
        elif yi < 2020:
            y = str(cy-1)
    
    # 鏈?    if m:
        mi = int(m)
        if mi<1 or mi>12: m='06'
    
    # 鏃?    if day:
        di = int(day)
        if di<1 or di>31: day='15'
    elif m:
        day = '15'  # 鏈夋湀鏃犳棩锛屾帹鏂负15
    
    parts=[]
    if y: parts.append(f"{y}骞?)
    if m: parts.append(f"{int(m):02d}鏈?)
    if day: parts.append(f"{int(day):02d}鏃?)
    return ''.join(parts) or 'UNKDATE'

# 鈹€鈹€鈹€ Main 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def extract(pdf_path):
    doc = fitz.open(pdf_path)
    results = {}
    
    for pi in range(1, len(doc), 2):
        dn = pi//2 + 1
        page = doc[pi]
        r = page.rect
        
        y1,y2 = find_date_line(page)
        crop = fitz.Rect(r.width*0.1, r.height*max(0,y1-0.02),
                         r.width*0.9, r.height*min(1,y2+0.02))
        date = read_date(page, crop)
        date = smart_check(date)
        results[dn] = date
    
    doc.close()
    
    # 涓婁笅鏂囪ˉ鍏匲NKDATE
    months = []
    for d in results.values():
        mm = re.search(r'(\d{2})鏈?, d)
        if mm: months.append(mm.group(1))
    cm = Counter(months).most_common(1)[0][0] if months else '06'
    years = []
    for d in results.values():
        mm = re.search(r'(\d{4})骞?, d)
        if mm: years.append(mm.group(1))
    cy = Counter(years).most_common(1)[0][0] if years else '2022'
    
    for k,v in results.items():
        if v == 'UNKDATE':
            results[k] = f"{cy}骞磠cm}鏈?
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--engine', choices=['rapid','paddle','both','auto'], default='rapid', help='OCR engine')
    args = parser.parse_args(sys.argv[1:])
    
    results = extract(args.input)
    if args.json:
        print(json.dumps({'engine': args.engine, 'dates': results}, ensure_ascii=False, indent=2))
    else:
        for k,v in sorted(results.items()):
            print(f'Doc {k:2d}: {v}')

