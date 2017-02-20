# -*- coding:utf8 -*-
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random, sys, os, platform

# 生成验证码例子
os_version = platform.system()
_letter_cases = '0123456789'  # 也可以使用字母
_upper_cases = _letter_cases.upper()
_numbers = ''.join(map(str, range(3, 10)))
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))


def creat_validata_code(size=(110, 32), chars=init_chars, img_type='png',
                        mode='RGB', bg_color=(255, 255, 255), fg_color=(0, 0, 255),
                        font_size=18, font_type='arial.ttf',
                        length=4, draw_lines=True, n_line=(1, 2),
                        draw_points=True, point_chance=2):
    if os_version != "Windows":
        """注意，默认的DejaVuSans字体文件并不在/usr/share/fonts/truetype/目录下，
        需要从下一级目录拷贝过来，注意arial.ttf是windows字体，不是linux用的，所以
        如果你是在linux下面，一定要确保/usr/share/fonts/truetype/目录下面有你在这里
        设定的字体文件存在，否设会抛出异常，建议cp命令来拷贝一个。例如：
        sudo cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /usr/share/fonts/truetype/
        """
        font_type = "DejaVuSans.ttf"
    width, height = size
    img = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)

    def get_chars():
            return random.sample(chars, length)

    def creat_line():
        line_num = random.randint(*n_line)  # sign that the param is a list

        for i in range(line_num):
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points():
        chance = min(100, max(0, int(point_chance)))
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars)
        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)
        draw.text(((width - font_width) / 3, (height - font_height) / 3),
                  strs, font=font, fill=fg_color)
        return ''.join(c_chars)

    if draw_lines:
        creat_line()
    if draw_points:
        create_points()
    strs = create_strs()

    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, strs


# code_img,capacha_code= creat_validata_code()
# code_img.save('xx.jpg','JPEG')
# print(capacha_code)
def get_validate_code():  # 返回验证码
    code_img, capacha_code = creat_validata_code()
    current_path = sys.path[0]  # 获取当前执行脚本的路径
    current_path += os.path.sep + "static" + os.path.sep + "image" + os.path.sep
    code_img.save(current_path+'xx.jpg','JPEG')
    return capacha_code


# get_validate_code()
#creat_validata_code(the_num=["1","2","3"])
