import base64
import os
import sys
from io import BytesIO
import pygame
import random
import requests
from PIL import Image
from pygame.locals import *
import colorsys

URl = 'http://47.102.118.1:8089/api/problem?stuid=031802230'
Path = 'imgs'
path = 'img.jpg'
# 一些常量
BACKGROUNDCOLOR = (255, 255, 255)
FPS = 40
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
VHNUMS = 3
CELLNUMS = VHNUMS * VHNUMS
MAXRANDTIME = 50


def get_json(url):
    """
    :param url: 获取json数据的URL
    :return: 图片，强制交换的步数，强制交换的格子，题目编号
    """
    html = requests.get(url)  # 获取json文件
    html_json = html.json()
    img_str = html_json['img']
    step = html_json['step']
    swap = html_json['swap']
    uuid = html_json['uuid']
    img_b64decode = base64.b64decode(img_str)  # base64解码
    file = open('test.jpg', 'wb')
    file.write(img_b64decode)
    file.close()
    image = BytesIO(img_b64decode)
    img = Image.open(image)
    return img, step, swap, uuid


def split_image(imga, row_num, col_num, save_path):  # 图片的分割保存
    """
    :param imga: 带分割的图片
    :param row_num: 分割的行数
    :param col_num: 分割的列数
    :param save_path: 图片存放文件夹
    :return: None
    """
    w, h = imga.size  # 图片大小
    if row_num <= h and col_num <= w:
        print('original image info:%sx%s,%s,%s' % (w, h, imga.format, imga.mode))
        print('开始处理图片切割，请稍候-')
        ext = 'jpg'
        num = 0
        rowheight = h // row_num
        colwidth = w // col_num
        for r in range(row_num):
            for c in range(col_num):
                box = (c * colwidth, r * rowheight, (c + 1) * colwidth, (r + 1) * rowheight)
                imga.crop(box).save(os.path.join(save_path, str(num) + '.' + ext))  # 切割完图片保存
                num = num + 1
        print('图片切割完毕，共生成%s张小图片。' % num)
    else:
        print('不合法的行列切割参数！')


def get_img(save_path, img):
    """
    :param img: 带分割的图片
    :return: 空白格的初始位置
    """
    # save_path = 'F:\imgs'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    row = 3
    col = 3
    if row > 0 and col > 0:
        split_image(img, row, col, save_path)
    else:
        print('无效的行列切割参数！')


def write_get(save_path):
    for k in range(9):
        image = Image.open(save_path + '//' + str(k) + '.jpg')
        image = image.convert('RGB')
        max_score = 0.0001
        dominant_color = None
        for count, (r, g, b) in image.getcolors(image.size[0] * image.size[1]):

            # 转为HSV标准

            saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]

            y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)

            y = (y - 16.0) / (235 - 16)

            score = (saturation + 0.1) * count

            if score > max_score:
                max_score = score

                dominant_color = (r, g, b)
        if dominant_color == (255, 255, 255):
            #print(k)
            return k


def min_imgs(paths, save_path):
    img = Image.open(paths)
    print(img.size)
    out = img.resize((300, 300))
    # save_path = "C:/Users/Administrator/软工/s/s.jpg"
    out.save(save_path)
    return save_path


def image_similarity(imag1_path, imag2_path):
    with open(imag1_path, "rb") as f:  # 转为二进制格式
        base64_data1 = base64.b64encode(f.read())  # 使用base64进行加密

    with open(imag2_path, "rb") as f:  # 转为二进制格式
        base64_data2 = base64.b64encode(f.read())  # 使用base64进行加密
    if base64_data1 == base64_data2:
        return 1
    else:
        return 0


# 计算图片的余弦距离


def terminate():
    pygame.quit()
    sys.exit()


# 随机生成游戏盘面
def newGameBoard():
    board = []
    for j in range(CELLNUMS):
        board.append(j)
    blackcell = CELLNUMS - 1
    board[blackcell] = -1
    for j in range(MAXRANDTIME):
        direction = random.randint(0, 3)
        if direction == 0:
            blackcell = move_A(board, blackcell)
        elif direction == 1:
            blackcell = move_D(board, blackcell)
        elif direction == 2:
            blackcell = move_S(board, blackcell)
        elif direction == 3:
            blackcell = move_W(board, blackcell)
    return board, blackcell


# 若空白图像块不在最左边，则将空白块左边的块移动到空白块位置
def move_D(board, blackcell):
    if blackcell % VHNUMS == 0:
        return blackcell
    board[blackcell - 1], board[blackcell] = board[blackcell], board[blackcell - 1]
    return blackcell - 1


# 若空白图像块不在最右边，则将空白块右边的块移动到空白块位置
def move_A(board, blackcell):
    if blackcell % VHNUMS == VHNUMS - 1:
        return blackcell
    board[blackcell + 1], board[blackcell] = board[blackcell], board[blackcell + 1]
    return blackcell + 1


# 若空白图像块不在最上边，则将空白块上边的块移动到空白块位置
def move_W(board, blackcell):
    if blackcell < VHNUMS:
        return blackcell
    board[blackcell - VHNUMS], board[blackcell] = board[blackcell], board[blackcell - VHNUMS]
    return blackcell - VHNUMS


# 若空白图像块不在最下边，则将空白块下边的块移动到空白块位置
def move_S(board, blackcell):
    if blackcell >= CELLNUMS - VHNUMS:
        return blackcell
    board[blackcell + VHNUMS], board[blackcell] = board[blackcell], board[blackcell + VHNUMS]
    return blackcell + VHNUMS


# 是否完成
def isFinished(board):
    for j in range(CELLNUMS - 1):
        if board[j] != j:
            return False
    return True


# 获取文件夹中的图片路径
def getFileList(dir, Filelist, ext=None):
    """
    获取文件夹及其子文件夹中文件列表
    输入 dir：文件夹根目录
    输入 ext: 扩展名
    返回： 文件路径列表
    """
    if os.path.isfile(dir):
        if ext is None:
            Filelist.append(dir)
        else:
            if ext in dir[-3:]:
                Filelist.append(dir)

    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            newDir = os.path.join(dir, s)
            getFileList(newDir, Filelist, ext)

    return Filelist


# 将文件夹中的图片遍历并进行操作 返回原图的路径
def ergodic_file(Path):
    org_img_folder = './org'
    # 检索文件
    imglist = getFileList(Path, [], 'jpg')
    print('本次执行检索到 ' + str(len(imglist)) + ' 张图像\n')
    print(imglist)
    z = 0
    save_path = 'img'
    img = random.choice(imglist)  # 每个图片都遍历一次 并开始进行对比操作
    img_temp = Image.open(img)
    get_img(save_path, img_temp)
    count_1 = 0
    stop_flag = 0
    print(img)
    return img


    # return imgpath
    # img_text文件夹中保存的九个小块就是原图分割出来的


# img_text文件夹中保存的九个小块就是原图分割出来


def main():
    # 初始化
    pygame.init()
    mainClock = pygame.time.Clock()
    # 加载图片
    # img, step, swap, uuid = get_json(URl)
    #img = Image.open(path)
    # ergodic_file()
    # k = get_img(Path, img)
    #k = write_get(Path)
    #print(get_img(Path, img))
    save_path = "s/s.jpg"
    img = min_imgs(ergodic_file(Path), save_path)
    gameImage = pygame.image.load(img)
    space = pygame.image.load(img)
    gameRect = gameImage.get_rect()
    # 设置窗口
    screen = pygame.display.set_mode((800, 300))
    pygame.display.set_caption('拼图')
    cellWidth = int(gameRect.width / VHNUMS)
    cellHeight = int(gameRect.height / VHNUMS)
    finish = False
    # space = pygame.image.load("b_ (2).jpg").convert_alpha()
    pygame.display.flip()
    gameBoard, blackCell = newGameBoard()
    text = pygame.font.Font("C:/Windows/Fonts/simsun.ttc", 50)
    text_fmt = text.render("原图", 1, (0, 0, 0))
    # 游戏主循环
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if finish:
                continue
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == ord('a'):
                    blackCell = move_A(gameBoard, blackCell)
                if event.key == K_RIGHT or event.key == ord('d'):
                    blackCell = move_D(gameBoard, blackCell)
                if event.key == K_UP or event.key == ord('w'):
                    blackCell = move_S(gameBoard, blackCell)
                if event.key == K_DOWN or event.key == ord('s'):
                    blackCell = move_W(gameBoard, blackCell)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                col = int(x / cellWidth)
                row = int(y / cellHeight)
                index = col + row * VHNUMS
                if (
                        index == blackCell - 1 or index == blackCell + 1 or index == blackCell - VHNUMS or index == blackCell + VHNUMS):
                    gameBoard[blackCell], gameBoard[index] = gameBoard[index], gameBoard[blackCell]
                    blackCell = index
        if isFinished(gameBoard):
            gameBoard[blackCell] = CELLNUMS - 1
            finish = True
        screen.fill(BACKGROUNDCOLOR)
        for i in range(CELLNUMS):
            rowDst = int(i / VHNUMS)
            colDst = int(i % VHNUMS)
            rectDst = pygame.Rect(colDst * cellWidth, rowDst * cellHeight, cellWidth, cellHeight)
            if gameBoard[i] == -1:
                continue
            rowArea = int(gameBoard[i] / VHNUMS)
            colArea = int(gameBoard[i] % VHNUMS)
            rectArea = pygame.Rect(colArea * cellWidth, rowArea * cellHeight, cellWidth, cellHeight)
            screen.blit(gameImage, rectDst, rectArea, )
        for i in range(VHNUMS + 1):
            pygame.draw.line(screen, BLACK, (i * cellWidth, 0), (i * cellWidth, gameRect.height))
        for i in range(VHNUMS + 1):
            pygame.draw.line(screen, BLACK, (0, i * cellHeight), (gameRect.width, i * cellHeight))
        screen.blit(text_fmt, (400, 120))
        screen.blit(space, (500, 0))
        pygame.display.update()
        mainClock.tick(FPS)


main()
