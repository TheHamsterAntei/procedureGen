import numpy as np
import os
from PIL import Image, ImageDraw


def calculate_sharpness(value, power):
    mod = 1.0
    if value < 0.5:
        mod = -1.0
    val = min(0.5, abs(value - 0.5) ** (1 / (1 + 0.2 * power))) * mod + 0.5
    return val


def generate(name, width, height, mode, side_locked, detailed, scale, first_smoothing, smoothing, sharpness,
             humidity, heatness):
    if not os.path.exists(name + '/'):
        os.mkdir(name)
    #Нормализация значений
    humidity = max(0, min(2, humidity))
    heatness = max(-1, min(3, heatness))
    #Генерация исходного массива
    #Пиксельные детали
    detail_array = np.random.rand(width, height) / (detailed + 1)
    print('Первичное сглаживание мельчайших деталей...')
    for i in range(0, first_smoothing):
        smooth_queue = [(np.random.uniform(0, 100), x, y) for x in range(0, width) for y in range(0, height)]
        smooth_queue.sort(key=lambda k: k[0])
        for k in smooth_queue:
            mediana_val = detail_array[k[1]][k[2]]
            mediana_cnt = 1
            if k[1] > 0:
                mediana_val += detail_array[k[1] - 1][k[2]]
                mediana_cnt += 1
            else:
                if side_locked:
                    mediana_val += detail_array[width - 1][k[2]]
                    mediana_cnt += 1
            if k[1] < width - 1:
                mediana_val += detail_array[k[1] + 1][k[2]]
                mediana_cnt += 1
            else:
                if side_locked:
                    mediana_val += detail_array[0][k[2]]
                    mediana_cnt += 1
            if k[2] < height - 1:
                mediana_val += detail_array[k[1]][k[2] + 1]
                mediana_cnt += 1
            if k[2] > 0:
                mediana_val += detail_array[k[1]][k[2] - 1]
                mediana_cnt += 1
            mediana_val /= mediana_cnt
            detail_array[k[1]][k[2]] = mediana_val
    #Маленькие детали
    details = []
    match detailed:
        case 1:
            details = [101]
        case 2:
            details = [11, 101]
        case 3:
            details = [11, 47, 101]
        case 4:
            details = [5, 11, 47, 101]
        case 5:
            details = [5, 11, 47, 101, 223]
        case 6:
            details = [5, 11, 47, 73, 101, 223]
        case 7:
            details = [3, 5, 11, 47, 73, 101, 223]
        case 8:
            details = [3, 5, 11, 47, 73, 101, 151, 223]
        case 9:
            details = [3, 5, 11, 29, 47, 73, 101, 151, 223]
        case 10:
            details = [3, 5, 11, 17, 29, 47, 73, 101, 151, 223]
    sub_detail_array = [[] for i in range(0, detailed)]
    for i in range(1, detailed + 1):
        max_width = int(np.ceil(width / (details[i - 1] * scale)))
        max_height = int(np.ceil(height / (details[i - 1] * scale)))
        sub_detail_array[i - 1] = np.random.rand(max_width, max_height) / (detailed + 1)
        print('Первичное сглаживание ' + str(i) + '-го уровня детализации')
        for j in range(0, first_smoothing):
            smooth_queue = [(np.random.uniform(0, 100), x, y) for x in range(0, max_width)
                            for y in range(0, max_height)]
            smooth_queue.sort(key=lambda k: k[0])
            for k in smooth_queue:
                mediana_val = sub_detail_array[i - 1][k[1]][k[2]]
                mediana_cnt = 1
                if k[1] > 0:
                    mediana_val += sub_detail_array[i - 1][k[1] - 1][k[2]]
                    mediana_cnt += 1
                else:
                    if side_locked:
                        mediana_val += sub_detail_array[i - 1][max_width - 1][k[2]]
                        mediana_cnt += 1
                if k[1] < max_width - 1:
                    mediana_val += sub_detail_array[i - 1][k[1] + 1][k[2]]
                    mediana_cnt += 1
                else:
                    if side_locked:
                        mediana_val += sub_detail_array[i - 1][0][k[2]]
                        mediana_cnt += 1
                if k[2] < max_height - 1:
                    mediana_val += sub_detail_array[i - 1][k[1]][k[2] + 1]
                    mediana_cnt += 1
                if k[2] > 0:
                    mediana_val += sub_detail_array[i - 1][k[1]][k[2] - 1]
                    mediana_cnt += 1
                mediana_val /= mediana_cnt
                sub_detail_array[i - 1][k[1]][k[2]] = mediana_val

    #Карта высот
    height_map = np.full((width, height), 1.0)
    print('Построение карты высот...')
    for y in range(0, height):
        for x in range(0, width):
            height_map[x][y] = detail_array[x][y]
            for i in range(0, detailed):
                height_map[x][y] += sub_detail_array[i][int(x / details[i])][int(y / details[i])]
    print('Вторичное сглаживание карты высот...')
    for i in range(0, smoothing):
        smooth_queue = [(np.random.uniform(0, 100), x, y) for x in range(0, width) for y in range(0, height)]
        smooth_queue.sort(key=lambda k: k[0])
        for k in smooth_queue:
            mediana_val = height_map[k[1]][k[2]]
            mediana_cnt = 1
            if k[1] > 0:
                mediana_val += height_map[k[1] - 1][k[2]]
                mediana_cnt += 1
            else:
                if side_locked:
                    mediana_val += height_map[width - 1][k[2]]
                    mediana_cnt += 1
            if k[1] < width - 1:
                mediana_val += height_map[k[1] + 1][k[2]]
                mediana_cnt += 1
            else:
                if side_locked:
                    mediana_val += height_map[0][k[2]]
                    mediana_cnt += 1
            if k[2] < height - 1:
                mediana_val += height_map[k[1]][k[2] + 1]
                mediana_cnt += 1
            if k[2] > 0:
                mediana_val += height_map[k[1]][k[2] - 1]
                mediana_cnt += 1
            mediana_val /= mediana_cnt
            height_map[k[1]][k[2]] = mediana_val

    if sharpness > 0:
        print('Применение настроек резкости')
        for y in range(0, height):
            for x in range(0, width):
                h = calculate_sharpness(height_map[x][y], sharpness)
                height_map[x][y] = h

    image_heightmap = Image.new('RGB', (width, height), (0, 0, 0))
    for y in range(0, height):
        for x in range(0, width):
            image_heightmap.putpixel((x, y), (int(255 * height_map[x][y]), int(255 * height_map[x][y]),
                                    int(255 * height_map[x][y])))
    image_heightmap.save(name + '/HeightMap.png', 'PNG')

    if mode == 0:
        return True

    #Настройки климата
    #Шаг 1. Составить карту температуры
    print('Составление температурной карты')
    water_level = 135 * (humidity ** 0.5) * (np.sin((heatness + 1) * np.pi / 4))
    heat_map = np.full((width, height), 0.0)
    for y in range(0, height):
        for x in range(0, width):
            if side_locked:
                h_max = (height / 2)
                h = abs(y - h_max)
                pixel_heat = heatness - 2.0 * ((h / h_max) ** 2)
                d = height_map[x][y] * 255 - water_level
                if d > 0:
                    pixel_heat -= 2 * (height_map[x][y] * 255 - water_level) / (335 - water_level)
                heat_map[x][y] = max(-3, min(3, pixel_heat))
    image_heat = Image.new('RGB', (width, height), (0, 0, 0))
    for y in range(0, height):
        for x in range(0, width):
            red = int(max(0, min(255, 75 + heat_map[x][y] * 60)))
            green = 0
            blue = int(max(0, min(255, 75 - heat_map[x][y] * 60)))
            image_heat.putpixel((x, y), (red, green, blue))
    image_heat.save(name + '/HeatMap.png', 'PNG')
    #Шаг 2. Заполнить впадины водой
    print('Заполнение карты водой')
    colored_map = [[(0, 0, 0) for y in range(0, height)] for x in range(0, width)]
    humidity_map = np.full((width, height), 0.0)
    for y in range(0, height):
        for x in range(0, width):
            pixel_h = height_map[x][y] * 255
            if pixel_h < water_level:
                if heat_map[x][y] * 20 > -2.0:
                    bright = pixel_h / water_level
                    red = int(30 * bright)
                    green = int(90 * bright)
                    blue = int(220 * bright)
                    colored_map[x][y] = (red, green, blue)
                    humidity_map[x][y] = min(5.0, 2.0 * heat_map[x][y])
                else:
                    bright = min(1.0, (heat_map[x][y] - 1) * -1)
                    red = int(255 * bright)
                    green = int(255 * bright)
                    blue = int(255 * bright)
                    colored_map[x][y] = (red, green, blue)
    #Шаг 3. Отрисовка карты влажности
    print('Отрисовка влажности')
    itered_map = np.full((width, height), 0)
    itered_from_map = [[[0.0, 0.0, 0.0, 0.0] for j in range(0, height)] for i in range(0, width)]
    max_i = int((width * height) ** 0.5)
    for i in range(0, max_i):
        print(str(i) + '/' + str(max_i))
        pos_for_iter = []
        for x in range(0, width):
            for y in range(0, height):
                if itered_map[x][y] == 0:
                    if humidity_map[x][y] > 0.001:
                        pos_for_iter.append((x, y))
                        itered_map[x][y] = 1
        if len(pos_for_iter) == 0:
            break
        print(len(pos_for_iter))
        for pos in pos_for_iter:
            x = pos[0]
            y = pos[1]
            if itered_map[x][y] == 1:
                itered_map[x][y] = 2
            sides = 0
            check_list = []
            if side_locked:
                sides += 2
                if x > 0:
                    if height_map[x - 1][y] * 255 >= water_level:
                        check_list.append((x - 1, y, 3))
                    else:
                        sides -= 1
                else:
                    if height_map[width - 1][y] * 255 >= water_level:
                        check_list.append((width - 1, y, 3))
                    else:
                        sides -= 1
                if x < width - 1:
                    if height_map[x + 1][y] * 255 >= water_level:
                        check_list.append((x + 1, y, 1))
                    else:
                        sides -= 1
                else:
                    if height_map[x - 1][y] * 255 >= water_level:
                        check_list.append((0, y, 1))
                    else:
                        sides -= 1

            else:
                if x > 0:
                    if height_map[x - 1][y] * 255 >= water_level:
                        sides += 1
                        check_list.append((x - 1, y, 3))
                    if x < width - 1:
                        if height_map[x - 1][y] * 255 >= water_level:
                            sides += 1
                            check_list.append((x + 1, y, 1))
            if y > 0:
                if height_map[x - 1][y] * 255 >= water_level:
                    sides += 1
                    check_list.append((x, y - 1, 0))
                if y < height - 1:
                    if height_map[x - 1][y] * 255 >= water_level:
                        sides += 1
                        check_list.append((x, y + 1, 2))
            if sides <= 0:
                continue
            value = humidity_map[x][y]
            for p in check_list:
                xx = p[0]
                yy = p[1]
                if humidity_map[xx][yy] >= humidity_map[x][y] or height_map[xx][yy] * 255 < water_level:
                    continue
                dir = p[2]
                raining = 0.0
                d = 0.0
                if height_map[xx][yy] * 255 >= water_level:
                    if height_map[x][y] < water_level:
                        d += (height_map[xx][yy] * 255 - water_level) / (255 - water_level)
                    else:
                        d += max(0.0, ((height_map[xx][yy] - height_map[x][y]) * 255) / (256 - height_map[x][y] * 255))
                    if heat_map[xx][yy] < 3.0:
                        raining += 0.01 * (3.0 - heat_map[xx][yy])
                result = value * (1 - raining)
                stopping = d ** 0.5
                result *= 1 - stopping
                result = (result + scale - 1) / scale
                if result > 0.001:
                    if itered_from_map[xx][yy][(dir + 2) % 4] + 0.05 < result:
                        if humidity_map[xx][yy] + result - itered_from_map[xx][yy][(dir + 2) % 4] <= humidity_map[x][y]:
                            humidity_map[xx][yy] += result - itered_from_map[xx][yy][(dir + 2) % 4]
                        else:
                            humidity_map[xx][yy] = max(humidity_map[xx][yy], humidity_map[x][y])
                        if itered_map[xx][yy] == 2:
                            itered_map[xx][yy] = 0
                        itered_from_map[xx][yy][(dir + 2) % 4] = result
    image_humidity = Image.new('RGB', (width, height), (0, 0, 0))
    for y in range(0, height):
        for x in range(0, width):
            red = 0
            green = 0
            blue = int(max(0, min(255, humidity_map[x][y] * 50)))
            image_humidity.putpixel((x, y), (red, green, blue))
    image_humidity.save(name + '/Humidity.png', 'PNG')

    #Шаг 4. Заполнение биомов
    print('Заполнение биомов')
    #biome_map = [[(0, 0, 0) for j in range(0, height)] for i in range(0, width)]
    for y in range(0, height):
        for x in range(0, width):
            #Снежный биом
            pixel_h = height_map[x][y] * 255
            if pixel_h < water_level:
                continue
            #Ледники
            if heat_map[x][y] * 20 <= -2.0:
                bright = max(0.9, min(1.0, (pixel_h / 255) * (heat_map[x][y] * -2)))
                red = int(250 * bright)
                green = int(225 * bright)
                blue = int(210 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Высокие горы
            if height_map[x][y] * 255 > water_level + 60:
                bright = max(0.6, min(1.0, ((pixel_h - water_level) / (255 - water_level))))
                red = int(200 * bright)
                green = int(90 * bright)
                blue = int(0 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Тундра
            if heat_map[x][y] * 20 < 4:
                bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(140 * bright)
                green = int(180 * bright)
                blue = int(150 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Тайга
            if heat_map[x][y] * 20 < 10 and humidity_map[x][y] > 0.05:
                bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(100 * bright)
                green = int(210 * bright)
                blue = int(150 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Холодная пустошь
            if heat_map[x][y] * 20 < 12 and humidity_map[x][y] < 0.05:
                bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(90 * bright)
                green = int(110 * bright)
                blue = int(140 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Степь
            if heat_map[x][y] * 20 < 25 and humidity_map[x][y] < 0.3:
                bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(180 * bright)
                green = int(255 * bright)
                blue = int(50 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Лиственный лес
            if heat_map[x][y] * 20 < 28 and humidity_map[x][y] > 0.2:
                bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(80 * bright)
                green = int(255 * bright)
                blue = int(80 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Джунгли
            if heat_map[x][y] * 20 > 27 and humidity_map[x][y] > 0.8:
                bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(0 * bright)
                green = int(160 * bright)
                blue = int(70 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Саванны
            if heat_map[x][y] * 20 > 27 and humidity_map[x][y] > 0.1:
                bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(220 * bright)
                green = int(160 * bright)
                blue = int(0 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Пустыни
            if heat_map[x][y] * 20 > 27:
                bright = max(0.8, min(1.0, (pixel_h - water_level) / (255 - water_level)))
                red = int(255 * bright)
                green = int(230 * bright)
                blue = int(80 * bright)
                colored_map[x][y] = (red, green, blue)
                continue
            #Луга
            bright = max(0.6, min(1.0, (pixel_h - water_level) / (255 - water_level)))
            red = int(30 * bright)
            green = int(255 * bright)
            blue = int(30 * bright)
            colored_map[x][y] = (red, green, blue)
            continue
    image = Image.new('RGB', (width, height), (0, 0, 0))
    for y in range(0, height):
        for x in range(0, width):
            image.putpixel((x, y), (colored_map[x][y][0], colored_map[x][y][1], colored_map[x][y][2]))
    image.save(name + '/Biomes.png', 'PNG')
    return True


if __name__ == '__main__':
    name = 'Basic'
    width = 1600
    height = 1200
    mode = 1
    side_locked = True
    detailed = 4
    scale = 1.0
    first_smoothing = 5
    smoothing = 5
    sharpness = 5
    humidity = 1.5 #Влажность (процент от нормы)
    heatness = 1.5 #Жара (процент от нормы)
    generate(name, width, height, mode, side_locked, detailed, scale, first_smoothing, smoothing, sharpness,
             humidity, heatness)
    name = 'Hot'
    humidity = 1.5
    heatness = 2.5
    generate(name, width, height, mode, side_locked, detailed, scale, first_smoothing, smoothing, sharpness,
             humidity, heatness)
    name = 'LowSmooth'
    first_smoothing = 1
    smoothing = 3
    sharpness = 1
    humidity = 0.9
    heatness = 1.4
    generate(name, width, height, mode, side_locked, detailed, scale, first_smoothing, smoothing, sharpness,
             humidity, heatness)
    name = 'SuperDetailed'
    detailed = 9
    first_smoothing = 1
    smoothing = 5
    sharpness = 3
    humidity = 1.0
    heatness = 1.8
    generate(name, width, height, mode, side_locked, detailed, scale, first_smoothing, smoothing, sharpness,
             humidity, heatness)
    name = 'Scaled'
    detailed = 4
    first_smoothing = 3
    smoothing = 5
    sharpness = 3
    humidity = 1.0
    heatness = 1.5
    scale = 2.0
    generate(name, width, height, mode, side_locked, detailed, scale, first_smoothing, smoothing, sharpness,
             humidity, heatness)
    name = 'Arid'
    scale = 1.0
    humidity = 0.2
    heatness = 2.0
    generate(name, width, height, mode, side_locked, detailed, scale, first_smoothing, smoothing, sharpness,
             humidity, heatness)

