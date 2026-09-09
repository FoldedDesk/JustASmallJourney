"""Handwritten travel content; shared by the API, shop and packing guide."""

EXTRA_FOODS = {
    key: {'name': name, 'icon': icon, 'description': description, 'price': price}
    for key, name, icon, description, price in [
        ('croissant', '黄油可颂', '🥐', '层层酥皮，装着街角早餐的香气。', 4),
        ('honey_toast', '蜂蜜吐司', '🍯', '淋了一点蜂蜜，森林和花园都喜欢这份甜。', 5),
        ('strawberry', '草莓小盒', '🍓', '一盒红红的小心情，适合带去看花。', 4),
        ('jam_bread', '果酱面包', '🍞', '把果香夹好，沿着古老的路慢慢走。', 4),
        ('sweet_potato', '烤红薯', '🍠', '纸袋里还暖着，走长路也不慌。', 4),
        ('corn', '甜玉米', '🌽', '金黄的小颗粒，想和湖边的风分享。', 3),
        ('mushroom_soup', '蘑菇浓汤', '🥣', '装进保温杯，给冷天留一点暖。', 6),
        ('cocoa', '热可可', '☕', '一口浓浓的温柔，适合山谷与雪原。', 5),
        ('lemon_soda', '柠檬汽水', '🍋', '气泡蹦蹦跳跳，想去海边和沙丘。', 5),
        ('berry_pie', '莓果派', '🥧', '派皮里藏着酸甜，适合慢慢品尝。', 6),
        ('cheese_bread', '奶酪面包', '🧀', '柔软又满足，陪你读完一本厚书。', 5),
        ('dango', '三色团子', '🍡', '把三个小愿望串在一起。', 5),
    ]
}

PLACE_PRESENTATION = {
    'forest': ('🌳', '走进一片绿意', '树荫、苔藓，还有藏在风里的小惊喜。'),
    'sea': ('🐚', '听一听海的声音', '沿着沙滩，捡起被海浪磨亮的贝壳。'),
    'mountain': ('⛰️', '离天空再近一点', '穿过山谷，等一颗星星亮起来。'),
    'library': ('📚', '在书页里晒太阳', '找一个靠窗的位置，把下午慢慢读完。'),
    'town': ('🏘️', '走过叮当响的街角', '石板路、风铃和刚出炉的面包香。'),
    'garden': ('🌼', '闻一闻雨后的草木', '花瓣上还有露水，云正在慢慢散开。'),
    'lake': ('🪷', '沿着水面发一会儿呆', '荷叶、小木桥，和一圈圈慢慢散开的涟漪。'),
    'desert': ('🏜️', '去沙丘读一封风的信', '金色起伏之间，有一汪安静的小绿洲。'),
    'snow': ('❄️', '踩出一行软软的脚印', '雪原、松林，还有亮着灯的山间驿站。'),
    'ruins': ('🏛️', '走过很久以前的时光', '长着青苔的石阶，把旧故事留给路过的人。'),
}

EXTRA_PLACES = {
    'lake': {'name': '荷风湖畔', 'gift': '一粒莲子', 'gift_key': 'lotus_seed', 'extra_gift_key': 'reed_whistle',
             'lines': ['坐在木桥上，数了数水面慢慢散开的圆圈。', '荷叶轻轻摇了一下，好像在和我打招呼。', '小船从桥下经过，把水里的云揉碎了。'],
             'special_lines': ['把荷叶上的一滴水留在画面里，像收藏了一颗小月亮。', '水面映出两片天空，真想把这一刻寄给你。']},
    'desert': {'name': '风信沙丘', 'gift': '一瓶细沙', 'gift_key': 'sand_bottle', 'extra_gift_key': 'desert_rose',
               'lines': ['沙丘背后竟有一片绿洲，在树荫下歇了歇脚。', '风把脚印慢慢抹平，只有回忆还认得来路。', '傍晚的沙子变成金色，像一封很长的信。'],
               'special_lines': ['留住了沙纹弯弯的线条，像风写下的字。', '绿洲的倒影里，一朵云正慢慢经过。']},
    'snow': {'name': '白绒雪原', 'gift': '一枚松针', 'gift_key': 'snow_pine', 'extra_gift_key': 'ice_crystal',
             'lines': ['雪地上的脚印一深一浅，通向亮着灯的小屋。', '戴好围巾，听松枝上的雪轻轻落下。', '驿站门口有人堆了一个很小的雪人。'],
             'special_lines': ['记录下一片雪花落在围巾上的模样。', '雪原尽头亮起一抹淡淡的光，世界安静了。']},
    'ruins': {'name': '苔痕古城', 'gift': '一片陶片', 'gift_key': 'pottery_shard', 'extra_gift_key': 'mosaic_tile',
              'lines': ['沿着长满青苔的石阶，读到了很久以前的春天。', '旧拱门框住一小片天空，云从故事里穿过去。', '石墙缝里开了一朵花，今天也有新的故事。'],
              'special_lines': ['把拱门和花影留在同一幅画面里，新旧时光碰了碰头。', '夕阳经过石柱，留下长长的一封信。']},
}

EXTRA_SOUVENIRS = {
    key: {'name': name, 'icon': icon, 'description': description}
    for key, name, icon, description in [
        ('lotus_seed', '莲子', '🪷', '荷风湖畔送来的一粒夏日。'),
        ('reed_whistle', '芦苇哨', '🎶', '轻轻吹，就像湖风经过芦苇。'),
        ('sand_bottle', '细沙瓶', '⌛', '风信沙丘的一点金色时光。'),
        ('desert_rose', '沙漠玫瑰石', '🪨', '风与沙慢慢雕刻的花。'),
        ('snow_pine', '雪松针', '🌲', '还带着松林的清香。'),
        ('ice_crystal', '冰晶挂坠', '❄️', '把雪原的小小亮光留了下来。'),
        ('pottery_shard', '彩陶片', '🏺', '古城留下的温柔颜色。'),
        ('mosaic_tile', '花纹石砖', '🔷', '一角花纹，也是一段旧故事。'),
    ]
}

# The more specific food + place + tool recipe wins over a food + place recipe.
COMBINATIONS = []
for key, place, food, tool, title, reward, icon, name, text in [
    ('forest_apple', 'forest', 'apple', None, '树下的苹果午餐', 'apple_leaf', '🍎', '苹果叶书签', '在树下分了一小块苹果，一只小鸟留下了红叶作谢礼。'),
    ('forest_honey', 'forest', 'honey_toast', 'sketchbook', '蜂蜜色的林间茶会', 'honey_sketch', '🐝', '蜜蜂速写', '闻到吐司香的蜜蜂绕着速写本转了一圈，纸上多了一位小客人。'),
    ('sea_pudding', 'sea', 'pudding', None, '把日落装进布丁', 'sunset_spoon', '🥄', '日落小勺', '布丁和日落是同一种颜色，海边茶摊送了一把纪念小勺。'),
    ('sea_soda', 'sea', 'lemon_soda', 'camera', '气泡里的海', 'bubble_photo', '🫧', '海风气泡相片', '举起汽水对着海，相机刚好留下气泡里小小的帆船。'),
    ('mountain_tea', 'mountain', 'hot_tea', None, '山谷的一杯暖意', 'tea_coaster', '🍵', '山纹杯垫', '在观景台喝完热茶，守山人送来一块刻着山纹的杯垫。'),
    ('mountain_cocoa', 'mountain', 'cocoa', 'compass', '可可与北方的星', 'north_star_pin', '🌟', '北星徽章', '沿着指南针找到背风的山坡，用一杯可可等来了第一颗星。'),
    ('library_cookie', 'library', 'cookie', None, '书页间的曲奇香', 'cookie_stamp', '🍪', '曲奇印章', '在阅读休息区分享曲奇，管理员盖了一枚点心形状的印章。'),
    ('library_cheese', 'library', 'cheese_bread', 'sketchbook', '会画画的午后', 'reading_sketch', '📔', '窗边速写页', '奶酪面包吃到一半，速写本上已经画满了窗边的光。'),
    ('town_croissant', 'town', 'croissant', None, '面包店的早安', 'bakery_ribbon', '🎀', '烘焙小缎带', '带着可颂去问早，面包师给行囊系了一条暖色缎带。'),
    ('town_sandwich', 'town', 'sandwich', 'camera', '街角野餐照', 'street_photo', '📸', '风铃街合影', '把三明治放在街角长椅上，相机拍下风铃街热闹的一刻。'),
    ('garden_strawberry', 'garden', 'strawberry', None, '草莓色的花信', 'pink_petals', '🌸', '粉色花瓣袋', '带着草莓走进花园，园丁送来一袋和它一样颜色的花瓣。'),
    ('garden_honey', 'garden', 'honey_toast', 'map', '花径尽头的甜', 'secret_seed', '🌱', '花径种子瓶', '循着地图来到花径尽头，在蜂蜜吐司旁发现园丁留下的小种子瓶。'),
    ('lake_corn', 'lake', 'corn', None, '木桥边的玉米午餐', 'duck_feather', '🪶', '湖鸭羽毛', '坐在桥边吃玉米，捡到一片随风落在木板上的羽毛。'),
    ('lake_dango', 'lake', 'dango', 'camera', '三色湖光', 'lotus_photo', '🪷', '荷影三色照', '团子、荷花和天色刚好凑成三种颜色，相机把它们留在一起。'),
    ('desert_potato', 'desert', 'sweet_potato', None, '沙丘上的暖纸袋', 'oasis_leaf', '🌴', '绿洲叶片', '吃完烤红薯，在绿洲的树荫下夹好了一片落叶。'),
    ('desert_soda', 'desert', 'lemon_soda', 'compass', '汽水指向绿洲', 'oasis_compass', '🧭', '绿洲方向牌', '指南针带我走到清凉的泉边，喝汽水时发现一块旧方向牌。'),
    ('snow_cocoa', 'snow', 'cocoa', None, '雪地可可时间', 'snowman_button', '⛄', '雪人纽扣', '喝着热可可堆了个小雪人，驿站主人送了一颗木纽扣。'),
    ('snow_soup', 'snow', 'mushroom_soup', 'map', '汤香通往暖屋', 'cabin_patch', '🧣', '暖屋布章', '地图上的小屋真的亮着灯，分享浓汤后收到一枚手缝布章。'),
    ('ruins_bread', 'ruins', 'jam_bread', None, '拱门下的果香', 'arch_rubbing', '📜', '拱门拓印', '靠着古城拱门吃面包，向看门人学着拓下一角石纹。'),
    ('ruins_pie', 'ruins', 'berry_pie', 'sketchbook', '莓果色的旧时光', 'ancient_sketch', '🎨', '古城彩绘页', '莓果派的颜色像旧壁画，把这次发现画进了速写本。'),
]:
    EXTRA_SOUVENIRS[reward] = {'name': name, 'icon': icon, 'description': '来自「' + title + '」的专属纪念。'}
    COMBINATIONS.append({'key': key, 'place': place, 'food': food, 'tool': tool, 'title': title, 'reward': reward, 'message': text})


def match_combination(place, food, tool):
    matches = [c for c in COMBINATIONS if c['place'] == place and c['food'] == food and (c['tool'] is None or c['tool'] == tool)]
    return max(matches, key=lambda c: bool(c['tool']), default=None)

# Additive weights keep every destination reachable. These are local game rules.
FOOD_DESTINATIONS = {
    'rice_ball': (), 'apple': ('forest', 'garden'), 'sandwich': ('town', 'mountain'),
    'pudding': ('sea', 'lake'), 'cookie': ('library', 'town'), 'hot_tea': ('mountain', 'library'),
    'croissant': ('town', 'ruins'), 'honey_toast': ('forest', 'garden'),
    'strawberry': ('garden', 'lake'), 'jam_bread': ('ruins', 'forest'),
    'sweet_potato': ('desert', 'snow'), 'corn': ('lake', 'garden'),
    'mushroom_soup': ('snow', 'forest'), 'cocoa': ('snow', 'mountain'),
    'lemon_soda': ('sea', 'desert'), 'berry_pie': ('ruins', 'lake'),
    'cheese_bread': ('library', 'town'), 'dango': ('lake', 'garden'),
}
TOOL_DESTINATIONS = {
    'camera': ('sea', 'mountain'), 'sketchbook': ('library', 'ruins'),
    'map': ('forest', 'snow'), 'compass': ('desert', 'mountain'),
}

def destination_weights(food, tool):
    return {place: 10 + (30 if place in FOOD_DESTINATIONS.get(food, ()) else 0)
            + (10 if place in TOOL_DESTINATIONS.get(tool, ()) else 0)
            for place in PLACE_PRESENTATION}

def choose_destination(food, tool):
    import random
    weights = destination_weights(food, tool)
    return random.choices(list(weights), weights=list(weights.values()), k=1)[0]
