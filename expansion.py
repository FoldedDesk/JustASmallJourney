"""Authored world expansion. No recipe data belongs in browser assets."""

# key | name | icon | visual family | standard title | standard story | special title | special story | souvenir | icon
PLACE_ROWS = """
bamboo|竹露小径|🎋|forest|竹叶替我撑伞|露水从竹叶尖落下，我等它落完才走过小径。|风穿过竹节|空竹节发出短短的哨音，林子像有人在练习吹笛。|竹节小哨|🎋
maple|红叶邮路|🍁|forest|寄给秋天的信|邮路上铺满红叶，我挑了一片没有破角的夹好。|红色的回信|邮差让我替一封信盖章，印泥的颜色正像脚下的叶子。|枫叶信封|✉️
cedar|杉影栈道|🌲|forest|木板上的脚步|栈道吱呀响了一声，树上的松鼠也低头看我。|树梢的高度|走到栈道最高处，才发现鸟巢和自己一样高。|杉木圆片|🪵
moss|苔灯湿地|🌿|forest|轻轻绕过苔藓|湿地的苔藓像柔软地毯，我沿着踏石绕过去。|小灯亮在水边|傍晚有几只萤火虫亮起，水洼也拥有了星星。|苔色石扣|🟢
orchard|蜜果山坡|🍐|garden|果园的梯子|果农扶着梯子摘梨，分给我一只最小的尝鲜。|装满香气的筐|帮忙把落果放进筐，筐底藏着一张谢谢的小纸条。|果园木牌|🏷️
lavender|紫穗花田|🪻|garden|紫色的午睡|花田边的长椅很暖，我枕着花香打了个盹。|丝带量过风|园丁把丝带系在篱笆上，说这样就知道风从哪里来。|紫穗香包|🪻
sunflower|向阳坡地|🌻|garden|跟着花抬头|一整坡向日葵朝着亮处，我也跟着抬起头。|影子的合照|夕阳把我和花盘的影子接起来，像戴了一顶大帽子。|葵纹徽片|🌻
rose|蔷薇温室|🌹|garden|玻璃上的水雾|温室玻璃蒙着薄雾，用手擦开一小块就看见花了。|花瓣的色卡|园丁递来一张色卡，原来粉色也有那么多名字。|蔷薇色卡|🎨
tea_hill|青岚茶山|🍃|mountain|一芽两片叶|采茶人教我认新芽，指尖很快染上一点清香。|山腰的茶席|竹席摊在山腰，杯里的云随着茶水轻轻晃。|茶山竹夹|🥢
rice_field|稻浪田埂|🌾|garden|田埂上的让路|遇到一列搬谷粒的蚂蚁，我把脚步挪到了旁边。|稻草人的帽檐|替稻草人扶正帽子时，发现里面缝着一颗小铃铛。|稻穗挂饰|🌾
windmill|麦香风车|🌬️|town|风车转一圈|坐在磨坊门口数叶片，面粉在光里像细细的雪。|面粉画的太阳|磨坊主人用指尖在面粉上画了个太阳，邀我添一条路。|风车纸模型|🎐
vineyard|葡萄长廊|🍇|garden|走进果香里|葡萄架漏下一点阳光，紫色果实像一串小灯。|叶影桌布|长桌铺满叶子的影子，连空盘子都显得热闹。|葡萄藤环|⭕
waterfall|鸣泉瀑谷|💦|mountain|先听见水声|还没看见瀑布，背包上的扣子就被水雾沾湿了。|一小段彩虹|等风把水雾吹向阳光，岩石边出现一截彩虹。|水纹石片|💧
spring|暖石温泉|♨️|mountain|暖暖的石阶|温泉旁的石阶带着暖意，坐一会儿脚尖就不冷了。|热气画的山|热气遮住山又慢慢散开，好像有人反复画着同一幅画。|温泉木签|♨️
cliff|听风断崖|🪁|mountain|把帽子按住|崖边的风很大，我按住帽子，坐在护栏内看远山。|风筝越过云影|有人在空地放风筝，长尾巴掠过地上的云影。|风筝尾带|🪁
observatory|圆顶观星台|🔭|mountain|等镜头转过来|管理员慢慢转动望远镜，让每个排队的人都看一眼月亮。|月面的凹坑|原来月亮也有坑坑洼洼的地方，我忽然觉得它亲近了。|月面拓卡|🌔
cloud_station|云端驿站|☁️|mountain|云从窗外过|驿站的窗户开着，一团雾进来又悄悄走了。|写给山下的地址|明信片上的地址写到一半，才发现这里没有街道名字。|云纹邮票|☁️
glacier|蓝冰峡湾|🧊|snow|蓝色的裂纹|沿着围栏看冰壁，深处的蓝像藏了一整片傍晚。|冰下的回声|向导敲了敲岸边的小冰块，清脆的声音走了很远。|蓝冰玻璃珠|🔵
aurora|极光营地|🌌|snow|帐篷前的夜灯|营地给每顶帐篷留了一盏灯，找回自己的位置很容易。|天空展开围巾|极光慢慢铺开，我忘了喝手里的热饮。|极光织带|🌌
frost_village|霜糖村落|🏠|snow|屋顶撒了糖|雪落在矮屋顶上，面包师说这是村子的糖霜。|脚印通往烤炉|沿着一串新脚印，找到了正在烤面包的公共炉房。|雪屋陶铃|🔔
harbor|晨帆港口|⚓|sea|船还没醒来|清早的缆绳轻轻敲着船舷，我在岸上等第一声汽笛。|帆升起来的时候|帮船主递了一截绳子，看白帆从折叠的布变成翅膀。|船绳手结|🪢
lighthouse|灯塔岬角|🗼|sea|数完旋转楼梯|数到顶层差点忘记最后一级，窗外的海替我接上了。|灯光扫过海面|入夜后灯塔转了一圈，远处的船也闪了一下灯。|灯塔铜扣|🔆
tide_pool|潮汐石滩|🦀|sea|石缝里的水塘|退潮留下许多小水塘，每一汪都有自己的小居民。|螃蟹搬家的路线|小螃蟹拖着海草横穿石面，我等它走完才收好相机。|潮纹卵石|🪨
coral|珊瑚浅湾|🪸|sea|隔着水看花园|站在观景栈桥上看水下的珊瑚，没有把手伸进它们的家。|鱼群拐弯|一群小鱼同时转向，像有人把银色丝带翻了个面。|珊瑚陶片|🪸
island|椰影小岛|🥥|sea|树荫会挪动|躺椅一会儿就晒到了太阳，只好跟着椰树影子挪。|岛上的慢时钟|码头的钟停了，船夫说今天可以按潮水记时间。|椰壳小碗|🥥
reed|芦花河口|🦢|lake|芦花碰到鼻尖|芦花飘到鼻子上，差点把安静看鸟的自己逗笑。|河口的白帆|白鹭从苇丛飞起，倒影比它晚了一点离开水面。|芦花纸卡|🪶
canal|石桥水巷|🌉|lake|桥下的一声早安|小船从石桥下穿过，船夫的问候在桥洞里响了两次。|一窗灯一窗水|水巷的灯陆续亮起，河里也多了一条暖暖的街。|石桥木刻|🌉
lotus_pond|月弯莲池|🌙|lake|莲叶留的座位|池边小凳刚好空着，坐下就看见一只蜻蜓停在叶尖。|月亮落进叶间|月亮的倒影被莲叶分成几小块，水一动又拼起来。|莲纹杯垫|🪷
willow|柳岸渡口|🌿|lake|等一班小渡船|渡船还在对岸，柳条陪我在候船棚前晃了一会儿。|船票背面的画|船夫在票背面画了一只鸟，说认得它就不会走错岸。|柳叶船票|🎫
salt_lake|镜盐湖面|🧂|desert|天空铺在脚边|盐湖边的步道很窄，两侧却都装着很宽的天空。|云走了两遍|一朵云从头顶走过，又从脚边走过，我挥了两次手。|盐花晶簇|🤍
cactus|仙掌驿路|🌵|desert|把水留一半|驿路小牌提醒留水给回程，我在树荫下检查了水壶。|开在刺间的花|平日不起眼的仙人掌开了小花，驿站主人也来看。|仙掌陶章|🌵
oasis_market|绿洲集市|🏺|desert|遮阳棚下的颜色|一排布棚挡住热风，香料摊的罐子却像装着太阳。|铜壶里的凉意|摊主把铜壶放进泉水里，递来的杯子凉得刚好。|集市织纹片|🧶
pottery|陶火工坊|🏺|town|泥巴记住手指|转盘上的泥歪了一下，师傅说这只杯子很有自己的主意。|等窑门打开|大家站在窑门外等成品，每只小碗都长出了不同的颜色。|拇指陶杯|🍶
music|回声琴房|🎹|library|只弹一个音|先轻轻按下一枚琴键，房间安静地把声音还给我。|窗外也在合奏|练到一半，下雨了，雨点刚好填上曲子的空拍。|琴键书夹|🎹
clock_shop|滴答钟铺|🕰️|town|许多种滴答|钟铺里的钟走得不一样快，店主却说它们都很认真。|整点的小门|整点时钟面小门打开，一只木鸟向我点了头。|齿轮胸针|⚙️
paper_mill|溪边纸坊|📜|library|把水捞成纸|纸帘从水里提起来，薄薄一层纤维留住了窗光。|花瓣睡在纸里|纸匠让我放一片落花进去，晾干以后它就不会飘走了。|花纤手纸|📜
museum|旧物博物馆|🏛️|ruins|一把没有门的钥匙|展柜里的钥匙找不到原来的门，却有一张很长的说明卡。|修补过的玩具|馆员指给我看木马上的补痕，说喜欢的东西可以陪人很久。|木马纪念牌|🐴
railway|青石小站|🚂|town|没有赶时间|站台只有两张长椅，坐满以后大家就一起看远处的信号灯。|最后一节车厢|列车转过弯的时候，最后一节车厢像在回头告别。|站台号牌|🚏
castle|藤蔓钟楼|🏰|ruins|爬到钟声旁边|石梯上有浅浅的凹痕，不知道多少脚步曾经走到这里。|藤叶里的钟面|藤叶没有挡住指针，只在钟面旁边添了一圈绿边。|钟楼铜片|🕰️
lantern|灯笼夜街|🏮|town|跟着灯笼走|夜街的灯笼一盏接一盏，我挑最亮的那条小巷走。|写在灯上的愿望|店主借我一支笔，让我把一个小愿望写在纸灯底部。|纸灯小坠|🏮
""".strip()

# Three distinct clickable details for every new place: label, icon, response.
OBJECT_ROWS = """
bamboo|竹叶,🎋,叶尖的露水落在石头上，响了一小声。|竹桥,🌉,桥面只够两只小动物错身，先等对方走过吧。|竹笛,🪈,路边的竹笛铺正在试音，长音像一阵风。
maple|邮筒,📮,筒盖上压着一片红叶，像刚贴好的邮票。|落叶,🍁,叶脉分出许多岔路，却都连着同一个叶柄。|长椅,🪑,椅背刻着：信没写完，可以多坐一会儿。
cedar|年轮,🪵,一圈一圈的纹路里，夹着树慢慢长大的年份。|松鼠,🐿️,松鼠抱着果子停下，似乎也在看风景。|绳栏,🪢,绳栏上系着布条，提醒大家雨后慢行。
moss|踏石,🪨,挑干燥的那一块落脚，水里的倒影也跳了一下。|萤火,✨,小亮点忽明忽暗，不必追，它会自己飞过来。|蘑菇,🍄,蘑菇藏在枯木背后，帽沿接住了雨滴。
orchard|果筐,🧺,筐底垫着软草，给怕磕碰的果子留个好位置。|梯子,🪜,梯脚扎在土里，顶端靠着结满果子的树。|梨花牌,🏷️,牌子上贴着春天的照片，原来这里曾经全是白花。
lavender|香草束,🪻,晾起的花束倒挂着，颜色比田里的浅一点。|蜂箱,🐝,站远些听，箱子里像开着很小的缝纫机。|丝带,🎀,紫丝带绕着篱笆转了一圈，结打得像蝴蝶。
sunflower|花盘,🌻,花盘里藏着螺旋，一圈接着一圈。|水壶,🚿,园丁把水壶留在阴凉处，壶嘴挂着一滴水。|草帽,👒,借来的草帽太大，帽檐差点盖住眼睛。
rose|玻璃窗,🪟,在雾上画个圆，外面的世界就多一扇小窗。|花剪,✂️,花剪合好放在工具架上，旁边是修枝的日期。|喷雾壶,💦,细水雾落下来，叶面亮了一瞬。
tea_hill|竹篓,🧺,篓里的新芽不能压紧，要给清香留些空隙。|茶杯,🍵,杯口热气转了半圈，才向山风走去。|石阶,🪨,石阶比想象中窄，慢一点才能看见旁边的花。
rice_field|稻穗,🌾,谷粒把穗子压弯了，低头也是丰收的样子。|稻草人,🧑‍🌾,口袋里塞着一封孩子写给麻雀的信。|水渠,💧,小闸门抬起一点，水就排着队进了田。
windmill|磨盘,⚙️,磨盘缓缓转动，谷粒变成一小堆柔软。|面粉袋,🌾,袋口印着今天的日期，闻起来有新麦香。|叶片,🌬️,风停的时候，叶片也会休息。
vineyard|葡萄架,🍇,架子下面有条刚好能走过的绿隧道。|空盘子,🍽️,盘子装着叶影，像一份不用吃的午餐。|藤蔓,🌿,小卷须牢牢抓住木杆，爬得很认真。
waterfall|水雾,💦,伸手接不到一滴完整的水，却把手心弄凉了。|护栏,🪵,护栏上的水珠排成一行，像在等合照。|彩虹,🌈,往旁边挪一步，颜色就悄悄换了位置。
spring|蒸汽,♨️,热气拐过石头，把远山变得模糊。|木桶,🪣,桶沿磨得光滑，旁边挂着请冲洗的小牌。|毛巾架,🧺,毛巾叠得方方正正，最上面那条晒得暖暖的。
cliff|风筝,🪁,线绷紧又放松，像天空轻轻拉了拉手。|护栏牌,🪧,小牌提醒留在步道内，远方就在这里看也很好。|望远镜,🔭,镜头里能看见对面山腰的一间白屋。
observatory|星图,🗺️,顺着虚线找，散开的星星连成了小动物。|镜筒,🔭,镜筒慢慢转动，请等管理员调好再看。|圆顶,🌌,顶棚打开一道缝，夜空像翻开的一页书。
cloud_station|邮袋,✉️,邮袋系得很紧，山风可不能偷走地址。|窗框,🪟,窗外只有白白的雾，等一会儿山又出现了。|路标,🪧,箭头指向山下，背面写着：回来喝杯茶。
glacier|冰壁,🧊,蓝色越往深处越浓，像没有写完的墨水。|浮冰,🤍,小冰块碰在一起，发出玻璃杯似的声响。|观景牌,🪧,旧照片上的冰线和今天不同，时间也会留下轮廓。
aurora|帐篷,⛺,门帘上夹着名字卡，夜里回来不会认错。|营灯,🏮,灯罩挡住风，把一小圈地面照得很安心。|夜空,🌌,绿色的光缓缓舒展，像谁抖开了一条围巾。
frost_village|雪屋,🏠,窗台有两只小杯子，杯里冒出的热气碰到了一起。|烤炉,🔥,面包出炉时，门外等候的人一起吸了吸鼻子。|雪铲,🥄,小铲子靠在门旁，刚清出的路留给下一个人。
harbor|船锚,⚓,岸上的旧锚已经退休，现在负责陪大家合影。|白帆,⛵,帆鼓起来以后，船好像伸了个懒腰。|缆绳,🪢,船主教的绳结一拉就紧，一松就开。
lighthouse|灯室,🔆,厚玻璃把灯光聚成一道长长的问候。|楼梯,🪜,数着台阶向上走，每一层都能看见不同的海。|航海图,🗺️,图上密密的标记，是船夜里回家的线索。
tide_pool|潮池,💧,小鱼停在石头旁，尾巴轻轻扇动。|海草,🌿,海草贴着石面，涨潮后它会重新站起来。|螃蟹,🦀,它举着钳子走过去，好像抱着两把小剪刀。
coral|栈桥,🌉,桥下的影子给小鱼留了一条阴凉路。|珊瑚窗,🪸,透过观景窗看，珊瑚的枝头有细小的摆动。|鱼群,🐟,银色小鱼转弯时，整群同时亮了一下。
island|椰树,🌴,叶影落在沙上，每片叶子都有自己的条纹。|吊床,🛏️,躺下以后，海平线跟着轻轻晃。|码头钟,🕰️,停住的指针旁贴着手写的开船时间。
reed|芦花,🌾,一阵风吹来，细绒就有了自己的旅行。|观鸟窗,🪟,小窗开得很低，蹲下来刚好看见白鹭。|木桩,🪵,木桩上的水线记着昨夜的潮位。
canal|石桥,🌉,桥栏磨得圆润，手掌贴上去凉凉的。|小船,🛶,船尾留下一条窄窄的水路，很快又合上了。|窗灯,🏮,一扇窗亮起，水里就多一扇摇晃的窗。
lotus_pond|莲叶,🪷,一颗水珠滚过叶面，没把绿色弄湿。|蜻蜓,🦋,它停在细枝上，翅膀亮得像薄纸。|月影,🌙,别碰水，月亮刚刚才拼好自己的脸。
willow|柳条,🌿,柳条够到了水面，在倒影上画了一道线。|渡船,🛶,船板轻响，船夫招呼大家坐稳再出发。|候船铃,🔔,铃响的时候，对岸的人也抬起了头。
salt_lake|盐花,🤍,岸边的小晶体一簇簇挤在一起，像白色花园。|木步道,🪵,走在指定的木道上，就不会踩坏脆弱的盐壳。|倒影,☁️,向云挥手时，水里也有一只手挥了回来。
cactus|仙人掌,🌵,刺间的小花很轻，靠近看但别碰它。|水壶架,💧,架子上写着：饮水补满，再走下一段。|遮阳棚,⛺,棚下比路上凉快，先坐够了再出发。
oasis_market|铜壶,🫖,壶身倒映出弯弯的自己，像一幅有趣的画像。|香料罐,🏺,摊主打开一只罐子，空气里多了温暖的甜味。|织毯,🧶,花纹一行行排开，摊主能说出每一种纹样的名字。
pottery|转盘,⚙️,手指轻轻靠上去，泥就慢慢长高了。|窑门,🔥,门口挂着冷却中的牌子，惊喜也需要等一等。|釉色板,🎨,同一罐釉烧出来的颜色，竟和原来不太一样。
music|钢琴,🎹,最左边的音低低的，像一只很困的大熊。|谱架,🎼,谱子上的铅笔记号，是练习留下的脚印。|窗边铃,🔔,风铃只响了一下，给曲子留了一个句号。
clock_shop|木鸟钟,🐦,小门打开以前，能听见齿轮先轻轻动起来。|怀表,🕰️,表盖内刻着一句：慢一点也能到家。|零件盒,⚙️,小螺丝各住一格，找东西时就不会着急。
paper_mill|纸帘,🧺,提起纸帘要保持平稳，水流下去纸就留下。|晾纸绳,📜,一张张纸迎着光，纤维像细小的河流。|花瓣篮,🌸,篮里只收落花，明天它们会住进纸里。
museum|旧钥匙,🗝️,标签说门已经不在了，故事还可以继续保管。|木马,🐴,新补的一块木头颜色浅些，是被珍惜的证据。|留言簿,📖,有人写：原来外婆家也有这样的东西。
railway|信号灯,🚦,灯换了颜色，站长把小旗拿在手里。|长椅,🪑,椅背晒得暖，坐下就不想赶路了。|时刻牌,🚏,今天的末班车旁边，画着一颗手写的星星。
castle|钟面,🕰️,古老的指针慢慢走，藤叶在旁边轻轻摇。|藤蔓,🌿,新叶沿着石缝爬上来，给旧墙添了绿色。|石梯,🪨,扶好栏杆走到转角，那里藏着一扇窄窗。
lantern|纸灯,🏮,灯纸透出暖光，画在上面的兔子像醒过来了。|小摊,🍡,摊主用纸袋装好点心，把热的一面朝外。|愿望笔,🖌️,笔尖蘸好墨，写一个自己愿意慢慢实现的愿望。
""".strip()

PLACES = {}
PRESENTATION = {}
SOUVENIRS = {}
for row in PLACE_ROWS.splitlines():
    key, name, icon, theme, title, story, special_title, special, gift, gift_icon = row.split('|')
    gift_key = key + '_keepsake'
    PLACES[key] = dict(name=name, gift=gift, gift_key=gift_key, lines=[story], special_lines=[special],
                       standard_title=title, special_title=special_title, theme=theme)
    PRESENTATION[key] = (icon, title, story)
    SOUVENIRS[gift_key] = dict(name=gift, icon=gift_icon, description='从'+name+'带回，记着「'+title+'」的那一天。')
for row in OBJECT_ROWS.splitlines():
    key, *objects = row.split('|')
    PLACES[key]['objects'] = [[parts[1],parts[0],parts[2],x,y] for parts,(x,y) in zip([o.split(',') for o in objects],[(22,59),(72,64),(48,77)])]
    icon, title, _ = PRESENTATION[key]
    PRESENTATION[key] = (icon, '在'+PLACES[key]['name']+'停一会儿', '沿途有'+ '、'.join(o[1] for o in PLACES[key]['objects'])+'，等你慢慢发现。')

# Additional rarities shared with neighbouring destinations; all have a travel source.
RARE_ROWS = """
bamboo|竹露珠串|🟩
maple|秋邮火漆|🔴
cedar|杉枝书夹|🌲
moss|萤光石瓶|✨
orchard|果农谢笺|📝
lavender|紫田丝结|🎀
sunflower|日光小镜|🪞
rose|温室玻璃坠|💎
tea_hill|茶芽标本卡|🍃
rice_field|草帽小铃|🔔
windmill|麦纹粉袋|🌾
vineyard|藤影餐巾|🟣
waterfall|虹色水晶|🌈
spring|暖石印章|♨️
cliff|风向布标|🪁
observatory|星轨描图|🌠
cloud_station|山顶邮章|📮
glacier|冰蓝音叉|🧊
aurora|夜营灯牌|🏕️
""".strip()
RARE_KEYS = []
for row in RARE_ROWS.splitlines():
    place, name, icon = row.split('|')
    key = place+'_rare'
    RARE_KEYS.append(key)
    SOUVENIRS[key] = dict(name=name, icon=icon, description='在'+PLACES[place]['name']+'多停留一会儿，才发现的小纪念。')
for index, place in enumerate(PLACES.values()):
    place['extra_gift_key'] = RARE_KEYS[index % len(RARE_KEYS)]
for key, extra in zip(list(PLACES)[19:], [
    'snowman_button','sea_glass','postmark','shell','bubble_photo','oasis_leaf','duck_feather',
    'tea_coaster','lotus_photo','margin_note','ice_crystal','desert_rose','vineyard_rare',
    'pottery_shard','reading_sketch','north_star_pin','pink_petals','arch_rubbing',
    'ticket_stub','mosaic_tile','bakery_ribbon',
]):
    PLACES[key]['extra_gift_key'] = extra

# key | name | icon | price | two destination preferences | description
FOOD_ROWS = """
bamboo_rice|竹筒饭|🎋|4|bamboo,cedar|打开竹盖，米饭也染上了清香。
maple_biscuit|枫糖饼|🍁|4|maple,windmill|薄饼边缘酥酥的，甜味像秋天。
pine_nut_cake|松仁糕|🥮|5|cedar,moss|把松仁藏进松软的糕里。
mint_jelly|薄荷凉粉|🟩|3|moss,waterfall|清凉的一小盒，适合林间歇脚。
pear_compote|冰糖炖梨|🍐|4|orchard,rose|梨块炖得透亮，糖水留着果香。
lavender_scone|薰衣草司康|🪻|5|lavender,vineyard|掰开司康，先闻到一点淡淡花香。
sunflower_cracker|葵籽脆饼|🌻|3|sunflower,rice_field|葵籽烤香了，装成方便分享的小片。
rose_mochi|玫瑰糯米糍|🌹|5|rose,lantern|软糯的外皮裹住花瓣馅。
matcha_roll|抹茶卷|🍵|5|tea_hill,bamboo|绿色蛋糕卷里夹着薄薄奶油。
millet_ball|小米饭球|🌾|3|rice_field,willow|捏得小小的，一口一个刚刚好。
wheat_bun|麦香圆包|🥯|3|windmill,railway|扎实的圆面包，不怕在背包里颠簸。
grape_tart|葡萄挞|🍇|5|vineyard,orchard|紫葡萄铺满酥皮，酸甜正好。
cucumber_roll|黄瓜寿司|🥒|3|waterfall,reed|卷进一条清脆，走热了也想吃。
egg_sandwich|鸡蛋软包|🥚|4|spring,cloud_station|蛋沙拉夹在软面包中，温柔又顶饿。
chestnut_rice|栗子饭|🌰|5|cliff,maple|栗子甜甜的，米饭也很有精神。
star_cookie|星形小饼|⭐|4|observatory,aurora|每块五个角，吃之前先许个愿。
cloud_cake|云朵蒸糕|☁️|4|cloud_station,mountain|白白软软，拿在手里像一小团云。
blueberry_yogurt|蓝莓酸奶|🫐|4|glacier,salt_lake|果粒在酸奶里留下一道道蓝色。
ginger_milk|姜汁热奶|🥛|5|aurora,frost_village|保温瓶里的一点辛香，暖到指尖。
cinnamon_roll|肉桂卷|🌀|5|frost_village,clock_shop|一圈圈卷进肉桂香，慢慢撕着吃。
tuna_onigiri|金枪鱼饭团|🍙|4|harbor,tide_pool|海苔包好鱼肉饭团，咸香不漏出来。
orange_muffin|香橙麦芬|🍊|4|lighthouse,island|橙皮带一点清香，蛋糕顶鼓鼓的。
seaweed_crisp|海苔脆片|🌊|3|tide_pool,coral|纸袋轻轻一响，就是脆脆的海味。
pineapple_bun|菠萝小酥|🍍|4|coral,island|金色酥皮里装着酸甜果馅。
coconut_jelly|椰奶冻|🥥|4|island,harbor|椰奶凝成柔软的小方块。
sesame_rice|芝麻饭糕|🍘|3|reed,lotus_pond|芝麻撒得密密的，咬一口很香。
redbean_bun|红豆包|🫘|4|canal,lantern|红豆馅细细绵绵，包在暖面皮里。
lotus_pastry|莲蓉小酥|🪷|5|lotus_pond,lake|酥皮一层一层，藏着清甜莲蓉。
peach_tea|蜜桃冷茶|🍑|4|willow,canal|拧开瓶盖，先闻见桃子的夏天。
salt_caramel|海盐焦糖块|🧂|4|salt_lake,desert|一点盐让焦糖的甜更清楚。
date_bar|椰枣能量棒|🟤|4|cactus,oasis_market|椰枣和坚果压成一条，走长路时拆开。
apricot_dried|杏干小袋|🍑|3|oasis_market,cactus|酸酸甜甜，路上可以一片片吃。
pumpkin_soup|南瓜浓汤|🎃|5|pottery,spring|浓汤是暖橙色，杯盖也热乎乎的。
lemon_cake|柠檬磅蛋糕|🍋|5|music,lavender|细细的柠檬糖霜，给厚蛋糕添点轻快。
walnut_bread|核桃面包|🥖|4|clock_shop,museum|核桃藏在切面里，像许多小惊喜。
osmanthus_jelly|桂花冻|🌼|4|paper_mill,library|透明的小冻里，桂花像停住了的雨。
fig_sandwich|无花果三明治|🥪|5|museum,ruins|无花果切开像花，和奶酪一起夹好。
potato_salad|土豆沙拉|🥔|4|railway,town|小盒里装好软土豆，附上一把木勺。
blackberry_scone|黑莓司康|🫐|5|castle,ruins|深色果汁藏在司康的裂缝里。
tangyuan|芝麻汤圆|🥣|5|lantern,canal|保温罐里圆圆的几颗，像装好的一家团圆。
plum_juice|酸梅饮|🍹|3|tea_hill,desert|酸甜的一瓶，适合午后小口喝。
tomato_bread|番茄佛卡夏|🍅|4|town,pottery|小番茄嵌进面包，烤得红润又多汁。
""".strip()
FOODS, FOOD_BIASES = {}, {}
for row in FOOD_ROWS.splitlines():
    key,name,icon,price,bias,description = row.split('|')
    FOODS[key] = dict(name=name,icon=icon,price=int(price),description=description)
    FOOD_BIASES[key] = tuple(bias.split(','))

TOOL_ROWS = """
binoculars|望远镜|🔭|18|special|observatory,reed|看清远处的星光和鸟影。
watercolors|水彩盒|🎨|18|special|rose,vineyard|把沿途的颜色画进明信片。
notebook|口袋笔记|📒|12|special|paper_mill,museum|随手记下店主和旧物的故事。
music_box|八音盒|🎵|18|special|music,clock_shop|歇脚时放一小段旋律。
lantern_tool|营地提灯|🏮|16|extra|aurora,moss|照亮脚边容易错过的小东西。
walking_stick|登山杖|🦯|14|extra|cliff,waterfall|扶稳脚步，再多看一眼山路。
thermos|保温壶|🫖|14|extra|spring,frost_village|留一口暖水，冷天可以多走一会儿。
raincoat|轻便雨披|🧥|12|extra|bamboo,waterfall|挡住细雨，沿湿润的小路慢慢找。
picnic_mat|野餐垫|🧺|14|special|sunflower,orchard|铺开坐下，把午餐和风景留在一起。
field_guide|草木手册|📗|16|extra|tea_hill,cedar|按叶子的样子，认一认路旁的植物。
shell_pouch|拾贝小袋|👝|12|extra|tide_pool,harbor|装好岸上拾到的小纪念，不带走活物。
stamp_book|旅行印册|📕|16|special|maple,cloud_station|请途中的小店盖上一枚到访印记。
kite|口袋风筝|🪁|14|special|windmill,cliff|把歇脚的片刻交给风。
magnifier|放大镜|🔍|12|extra|salt_lake,castle|近一点看石纹与盐花的细节。
sewing_kit|针线小盒|🧵|14|extra|oasis_market,lavender|修好松开的布扣，也学一段当地针法。
folding_cup|折叠茶杯|🥤|12|special|canal,lotus_pond|和偶然遇见的人一起喝杯茶。
""".strip()
TOOLS, TOOL_BIASES = {}, {}
for row in TOOL_ROWS.splitlines():
    key,name,icon,price,effect,bias,description = row.split('|')
    TOOLS[key] = dict(name=name,icon=icon,price=int(price),effect=effect,description=description+('更容易留下特别风景。' if effect=='special' else '更容易发现额外纪念品。'))
    TOOL_BIASES[key] = tuple(bias.split(','))

# place | food | optional tool | title | reward | authored story
COMBO_ROWS = """
bamboo|bamboo_rice|raincoat|竹盖接住的雨|bamboo_rare|穿着雨披打开竹筒饭，落在竹盖上的雨珠像一串透明珠子，竹器铺送来同样形状的小珠串。
maple|maple_biscuit|stamp_book|枫糖味的邮戳|maple_rare|分享枫糖饼后，邮差借来火漆，在印册旁压下一枚红叶印。
cedar|pine_nut_cake|field_guide|杉叶夹在哪一页|cedar_rare|照手册认出落下的杉枝，吃完松仁糕，护林员帮我把枝条做成书夹。
moss|mint_jelly|lantern_tool|提灯下的凉粉|moss_rare|提灯照着点心盒，薄荷凉粉亮晶晶的，守湿地的人送了一瓶会反光的小石子。
orchard|pear_compote|picnic_mat|梨树下留一块垫子|orchard_rare|把野餐垫分给歇脚的果农，炖梨刚好温着，他留下一张写着来年再见的纸条。
lavender|lavender_scone|sewing_kit|补好花篮的提带|lavender_rare|吃完司康，用针线补好园丁的花篮提带，她把一段紫丝带系在我的背包上。
sunflower|sunflower_cracker|picnic_mat|一小块日光|sunflower_rare|野餐垫铺在花影下，分享葵籽饼的孩子送来一面小镜子，里面装满了阳光。
rose|rose_mochi|watercolors|玫瑰的第七种粉|rose_rare|糯米糍还没吃完，水彩已经调出好几种粉色，园丁送来一枚同色的玻璃坠。
tea_hill|matcha_roll|field_guide|茶芽与蛋糕卷|tea_hill_rare|对着手册认完新芽，再尝一口抹茶卷，茶农帮我压好一张茶芽标本卡。
rice_field|millet_ball||稻草人的饭点|rice_field_rare|把饭球盒放在田边，替稻草人扶好帽子，农人送了一只和帽檐上一样的小铃。
windmill|wheat_bun|kite|风车与风筝的午餐|windmill_rare|风筝在磨坊上空转圈，面包放在膝头，磨坊主人给我一只印着麦穗的小布袋。
vineyard|grape_tart|watercolors|把叶影画在餐巾上|vineyard_rare|吃葡萄挞时照着桌上的叶影画画，果园主人把这块餐巾送给了我。
waterfall|cucumber_roll|walking_stick|水雾中的清脆午餐|waterfall_rare|拄着手杖走到观景台，吃黄瓜寿司时看见彩虹，向导送来一颗虹色水晶。
spring|egg_sandwich|thermos|保温壶旁的木印|spring_rare|保温壶和软包摆在暖石边，店主邀我在纪念木印上刻一道泉水纹。
cliff|chestnut_rice|kite|栗子饭等风来|cliff_rare|在安全的空地吃完栗子饭，风筝终于升起来，放风筝的朋友送我一条风向布标。
observatory|star_cookie|binoculars|吃掉一颗饼干星|observatory_rare|望远镜找到北方的星，我从盒里挑一块星形饼，管理员赠了一张今晚的星轨描图。
cloud_station|cloud_cake|stamp_book|云朵盖了章|cloud_station_rare|蒸糕像窗外的云，驿站主人边笑边给印册盖章，又送了一枚小小的山顶邮章。
glacier|blueberry_yogurt||蓝莓色的回声|glacier_rare|酸奶留下的蓝纹很像冰壁，导览员敲响冰蓝音叉，让我把这段声音带回去。
aurora|ginger_milk|lantern_tool|等极光的姜奶|aurora_rare|提灯守着帐篷，姜奶暖着手，营地主人递来一块写有今晚日期的小灯牌。
frost_village|cinnamon_roll|thermos|热水壶等面包熟|snowman_button|用保温壶的热水配肉桂卷，帮烤炉房守门的雪人扶好围巾，主人送来一颗备用木纽扣。
harbor|tuna_onigiri|shell_pouch|饭团盒旁的海玻璃|sea_glass|饭团吃完后用拾贝袋收好岸边的海玻璃，船主说那是浪花磨了很久的礼物。
lighthouse|orange_muffin|camera|橙色的灯塔早茶|sunset_spoon|守塔人用小勺分开麦芬，相机留下两份早餐的影子，临走时小勺也送给了我。
tide_pool|seaweed_crisp|shell_pouch|潮退以后的脆片声|shell|把海苔纸袋收好，再用拾贝袋装一枚空贝壳，没有打扰潮池里的小居民。
coral|pineapple_bun|watercolors|水下花园的颜色|bubble_photo|吃完小酥，对着观景窗调水彩，工作人员送来一张用气泡边框装饰的浅湾照片。
island|coconut_jelly||椰影里的吊床课|oasis_leaf|船夫教我把吊床系稳，分享椰奶冻以后，我们各夹好一片树下的落叶。
reed|sesame_rice|binoculars|饭糕与第一只白鹭|duck_feather|望远镜里出现白鹭时，饭糕刚吃一半，观鸟员把整理步道时拾到的羽毛送给我。
canal|redbean_bun|folding_cup|桥下分一杯热茶|tea_coaster|红豆包分成两半，折叠杯里倒好热茶，茶摊主人送来一块带山纹的旧杯垫。
lotus_pond|lotus_pastry|folding_cup|月亮也有一份莲蓉|lotus_photo|杯子映着月亮，莲蓉酥摆在一旁，池边摄影师送来一张三色荷影照。
willow|peach_tea|notebook|渡船停靠的第几页|margin_note|在笔记里记下渡船时间，船夫喝了蜜桃茶，在页边补上一句慢慢走。
salt_lake|salt_caramel|magnifier|焦糖与盐花的形状|ice_crystal|放大镜下的盐花像小城堡，讲解员尝了海盐焦糖，送来一枚冰晶形状的挂坠。
""".strip()
COMBINATIONS = []
for row in COMBO_ROWS.splitlines():
    place,food,tool,title,reward,message = row.split('|')
    COMBINATIONS.append(dict(key=place+'_picnic',place=place,food=food,tool=tool or None,title=title,reward=reward,message=message))
