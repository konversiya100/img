from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import math

OUTPUT=(1080,1350)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TITLES={
"mtg":[
"Победа или красивая комбинация?","Первая колода","Один цвет или пять?",
"Commander за кухонным столом","Бюджетная колода","Бумажная игра или Arena",
"Самая любимая карта","Как хранить коллекцию?","Pauper: сила простых карт",
"Играем без конфликтов","Кого научить играть?","Ищем игроков в Самаре"
],
"aircon":[
"Почему кондиционер пахнет?","Обогрев в ноябре","Не забывайте о фильтрах",
"Куда направлять поток воздуха?","Шум наружного блока","Кондиционер и сухой воздух",
"Как выбрать место установки","Что такое инвертор?","Почему капает вода?",
"Нужна ли вентиляция?","Как выбрать мощность","Проверка перед сезоном"
],
"jk":[
"Соседи, давайте знакомиться","Уютный двор","Парковка без ссор",
"Соседская помощь","Тишина в доме","Где гуляете рядом?",
"Питомцы и общий двор","Уют в общих пространствах","Обмен полезными вещами",
"Мастера по рекомендации","Зимние бытовые вопросы","О чём писать дальше?"
],
"atelier":[
"Почему вещь не сидит?","Старые джинсы — новые идеи","Как выбрать ткань",
"Длина решает","Платье к событию","Вторая жизнь жакета",
"Что выдаёт качественный шов","Одежда для разных фигур","Почему ткань мнётся?",
"От идеи до выкройки","Переделка или новая вещь","Удобный базовый гардероб"
]
}
THEMES={
"mtg": {"label":"КАРТОЧНЫЕ ИГРЫ • САМАРА","footer":"MAGIC: THE GATHERING / ОБСУЖДЕНИЕ","accent":(246,129,82),"sector":(0,0)},
"aircon":{"label":"КОМФОРТ ДОМА • САМАРА","footer":"КОНДИЦИОНЕРЫ / ПОЛЕЗНЫЕ СОВЕТЫ","accent":(84,197,231),"sector":(1,0)},
"jk":{"label":"СОСЕДИ • САМАРА","footer":"ЖК «РЕКОРД» / ОБСУЖДЕНИЕ","accent":(152,208,128),"sector":(0,1)},
"atelier":{"label":"СТИЛЬ И ПОШИВ • САМАРА","footer":"АТЕЛЬЕ-САМАРА / СОВЕТЫ","accent":(254,166,191),"sector":(1,1)}
}

def load_panel(group,i):
    if group=="mtg" and i<6 and Path("sheets/mtg-01.png").exists():
        with Image.open("sheets/mtg-01.png") as src:
            w,h=src.size
            c,r=i%2,i//2
            inset=2
            return src.crop((round(c*w/2)+inset,round(r*h/3)+inset,
                             round((c+1)*w/2)-inset,round((r+1)*h/3)-inset)).convert("RGB")
    source=Path(f"sheets/mix-{(i%4)+1:02}.jpg")
    with Image.open(source) as src:
        w,h=src.size
        c,r=THEMES[group]["sector"]
        return src.crop((round(c*w/2)+1,round(r*h/2)+1,
                         round((c+1)*w/2)-1,round((r+1)*h/2)-1)).convert("RGB")

def wrap(draw,title,font,max_width):
    lines=[]
    for word in title.split():
        proposal=(lines[-1]+" "+word).strip() if lines else word
        if lines and draw.textbbox((0,0),proposal,font=font)[2]>max_width:
            lines.append(word)
        elif lines:
            lines[-1]=proposal
        else:
            lines=[word]
    return lines

def render(group,i):
    theme=THEMES[group]
    img=ImageOps.fit(load_panel(group,i),OUTPUT,method=Image.Resampling.LANCZOS).convert("RGBA")
    w,h=OUTPUT
    gradient=Image.new("RGBA",OUTPUT,(0,0,0,0))
    d=ImageDraw.Draw(gradient)
    for y in range(h):
        t=y/h
        dark=int(36*(1-t)+215*(t**2.2))
        if t>0.58: dark=min(236,int(dark+55*((t-0.58)/0.42)))
        d.line((0,y,w,y),fill=(8,13,22,dark))
    img=Image.alpha_composite(img,gradient)
    overlay=Image.new("RGBA",OUTPUT,(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    accent=theme["accent"]
    d.rounded_rectangle((65,70,700,143),radius=29,fill=(9,14,23,170))
    d.rectangle((79,91,86,125),fill=accent)
    label_f=ImageFont.truetype(FONT_BOLD,26)
    d.text((106,88),theme["label"],font=label_f,fill="white")
    d.text((900,94),f"{i+1:02} / 12",font=ImageFont.truetype(FONT_BOLD,28),fill="white")
    d.rounded_rectangle((68,1040,106,1053),radius=5,fill=accent)
    img=Image.alpha_composite(img,overlay)
    d=ImageDraw.Draw(img)
    title=TITLES[group][i]
    size=78
    while size>=52:
        title_f=ImageFont.truetype(FONT_BOLD,size)
        lines=wrap(d,title,title_f,930)
        heights=len(lines)*(size+13)
        if heights<=345: break
        size-=4
    block_height=len(lines)*(size+13)
    start_y=1070-block_height
    for n,line in enumerate(lines):
        d.text((74,start_y+n*(size+13)),line,font=title_f,fill=(255,255,255,255),
               stroke_width=1,stroke_fill=(15,20,30,240))
    d.line((76,1165,1006,1165),fill=(255,255,255,105),width=2)
    small=ImageFont.truetype(FONT_BOLD,28)
    d.text((76,1205),theme["footer"],font=small,fill=(255,255,255,222))
    d.text((76,1256),"Иллюстрация для обсуждения",font=ImageFont.truetype(FONT,23),fill=(255,255,255,160))
    img=img.convert("RGB").filter(ImageFilter.UnsharpMask(radius=1.0,percent=55,threshold=3))
    dest=Path("covers")/group/f"post-{i+1:02}.jpg"
    dest.parent.mkdir(parents=True,exist_ok=True)
    img.save(dest,format="JPEG",quality=88,optimize=True)
    print(dest)

for group in THEMES:
    for i in range(12):
        render(group,i)
