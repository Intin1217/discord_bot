import discord
from discord.ext import commands
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import json
import random

client = discord.Client()
# 파일에서 데이터를 로드하는 함수
def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except UnicodeDecodeError:
        print("UTF-8로 디코딩할 수 없는 문자가 발견되었습니다. 대체 문자를 사용하여 처리합니다.")
        with open(filename, 'r', encoding='utf-8', errors='replace') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"users": {}}
    except Exception as e:
        print(f"파일을 읽는 도중 오류가 발생했습니다: {e}")
        return None



# 데이터를 파일에 저장하는 함수
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

# 데이터 파일 이름
DATA_FILE = 'guild_members.json'

# 파일에서 데이터 로드
guild_members = load_data(DATA_FILE)

bot = commands.Bot(command_prefix='#')  # 봇을 #으로 명령어 호출

@bot.event
async def on_ready():
    print("실행중")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("#명령어"))
    
@bot.command()
async def 명령어(ctx):
    channel = ctx.channel
    
    CommandList = (
    """ #길드목록 [길드명] - 가장 최근에 가입한 길드원 20명 닉네임 출력
        #길드추적 [닉네임] - 해당 유저의 길드 내역을 조회합니다.
        #비약
        #보스
        #주사위
        #마법의소라고동님 [질문]
        
        ```길드 가입 일자는 처음 저장된 날짜입니다```
    """
    )
    
    embed = discord.Embed(title="명령어 목록", description=CommandList, color=0x00ff56)
    await channel.send(embed=embed)

@bot.command()
async def 길드목록(ctx, *, guild_name):
    channel = ctx.channel
    name_list = []
    if guild_name == "매구":
        await channel.send("조회불가")
    else:
        input_guild_name = urllib.parse.quote(guild_name)
        url = f"https://www.kr.playblackdesert.com/ko-KR/Adventure/Guild/GuildProfile?guildName={input_guild_name}&region=KR"
        
        sourcecode = urllib.request.urlopen(url).read()
        bs = BeautifulSoup(sourcecode, "html.parser")
        
        # 조회한 날짜
        join_date = datetime.today().strftime('%Y년%m월%d일')
        
        for guild_people_list in bs.find("div", class_="box_list_area").find_all("a"):
            for people_list in guild_people_list:
                # 기존 데이터에서 해당 이름의 가입 일자 가져오기
                existing_join_date = guild_members.get(people_list, {}).get("join_date", join_date)
                previous_guilds = guild_members.get(people_list, {}).get("previous_guilds", {})
                name_list.append({"name": people_list, "guild_name": guild_name, "active": True, "join_date": existing_join_date, "previous_guilds": previous_guilds})
        
        # 기존 데이터에서 나간 길드원 처리 ##현재 탈퇴자 날짜가 계속 갱신되어서 최신 날짜로 표기되는 현상이 존재
        for member_name, member_info in guild_members.items():
            # if member_info.get("active") == False:
            #     pass
                
            if member_info.get("guild_name") == guild_name and member_name not in [member["name"] for member in name_list]:
                # 해당 길드원의 가입 일자를 조회한 날짜로 변경하고 탈퇴로 표시
                member_info["join_date"] = join_date
                member_info["active"] = False
                
                # 현재 조회한 길드명과 가입일자를 이전 길드 목록에 추가
                previous_guilds = member_info.setdefault("previous_guilds", {})
                previous_guilds[guild_name] = join_date
                name_list.append(member_info)
        ############################################################################
        # 데이터 업데이트
        guild_members.update({member["name"]: member for member in name_list})

        # 데이터 저장
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(guild_members, file, ensure_ascii=False)
            
        sorted_name_list = sorted(name_list, key=lambda x: datetime.strptime(x['join_date'], '%Y년%m월%d일'))

        # 결과를 역순으로 정렬
        sorted_name_list.reverse()

        embed = discord.Embed(title=guild_name, color=0x00ff56)
        embed.description = ""

        # 최대 20명의 길드원 목록 추가
        for i, member in enumerate(sorted_name_list[:20], start=1):
            if member['active']:
                embed.description += f"가문명: {member['name']} / 가입기록: {member['join_date']} / {guild_name} 가입\n"
            else:
                embed.description += f"가문명: {member['name']} / 가입기록: {member['join_date']} / {guild_name} 탈퇴\n"

        await channel.send(embed=embed)
        
@bot.command()
async def 길드추적(ctx, *, user_name):
    channel = ctx.channel
    user_history = []
    if user_name == "인틴":
        await channel.send("추적X")
    else:
        for member_name, member_info in guild_members.items():
            if member_info.get("name") == user_name:
                status = "가입" if member_info["active"] else "탈퇴"
                guild_name = member_info["guild_name"]
                join_date = member_info["join_date"]
                
                # 이전 길드 정보 가져오기
                previous_guilds = member_info.get("previous_guilds", {})
                previous_guilds_str = ', '.join([f"{guild}: {date} 탈퇴" for guild, date in previous_guilds.items()])
                
                # 사용자의 가입/탈퇴 기록 및 이전 길드 정보를 문자열로 구성하여 리스트에 추가
                user_history.append(f"가문명: {user_name} / {join_date} / {guild_name} {status}\n-이전 길드 리스트-\n{previous_guilds_str}")
        
        # 사용자의 가입/탈퇴 기록 출력
        if user_history:
            # 리스트에 있는 문자열들을 합쳐서 한 번에 출력
            user_history_str = '\n\n'.join(user_history)
            await channel.send(f"{user_name}의 가입/탈퇴 기록:\n```{user_history_str}```")
        else:
            await channel.send(f"{user_name}의 가입/탈퇴 기록이 없습니다.")
            
@bot.command()
async def parkjh001217_DB_1217(ctx):
    channel = ctx.channel
    name_list = []
    G_count = 0 #길드 갯수 카운터
    
    guild_names = set()
    for guild_name_info in guild_members.values():
        guild_name = guild_name_info.get("guild_name")
        if guild_name:
            guild_names.add(guild_name)
    
    for guild_name in guild_names:
        
        if guild_name == "매구":
            pass
        
        input_guild_name = urllib.parse.quote(guild_name)
        url = f"https://www.kr.playblackdesert.com/ko-KR/Adventure/Guild/GuildProfile?guildName={input_guild_name}&region=KR"
        
        sourcecode = urllib.request.urlopen(url).read()
        bs = BeautifulSoup(sourcecode, "html.parser")
        
        # 조회한 날짜
        join_date = datetime.today().strftime('%Y년%m월%d일')
        
        for guild_people_list in bs.find("div", class_="box_list_area").find_all("a"):
            for people_list in guild_people_list:
                # 기존 데이터에서 해당 이름의 가입 일자 가져오기
                existing_join_date = guild_members.get(people_list, {}).get("join_date", join_date)
                previous_guilds = guild_members.get(people_list, {}).get("previous_guilds", {})
                name_list.append({"name": people_list, "guild_name": guild_name, "active": True, "join_date": existing_join_date, "previous_guilds": previous_guilds})
        
        # 기존 데이터에서 나간 길드원 처리 ##현재 탈퇴자 날짜가 계속 갱신되어서 최신 날짜로 표기되는 현상이 존재
        for member_name, member_info in guild_members.items():
            if member_info.get("active") == False:
                pass
                
            elif member_info.get("guild_name") == guild_name and member_name not in [member["name"] for member in name_list]:
                # 해당 길드원의 가입 일자를 조회한 날짜로 변경하고 탈퇴로 표시
                member_info["join_date"] = join_date
                member_info["active"] = False
                
                # 현재 조회한 길드명과 가입일자를 이전 길드 목록에 추가
                previous_guilds = member_info.setdefault("previous_guilds", {})
                previous_guilds[guild_name] = join_date
                name_list.append(member_info)
        ############################################################################
        # 데이터 업데이트
        guild_members.update({member["name"]: member for member in name_list})

        # 데이터 저장
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(guild_members, file, ensure_ascii=False)
            
        sorted_name_list = sorted(name_list, key=lambda x: datetime.strptime(x['join_date'], '%Y년%m월%d일'))

        # 결과를 역순으로 정렬
        sorted_name_list.reverse()

        G_count += 1
        print(f"{G_count}번째 길드: {guild_name}")
    print(f"{G_count}개 길드 목록 갱신 완료.")
    await channel.send(f"{G_count}개 길드 목록 갱신 완료.")
    
@bot.command()
async def 비약(ctx):
    channel = ctx.channel

    # 이미지를 지정한 URL에서 다운로드하여, "파일명.png"로 저장
    urllib.request.urlretrieve("https://s1.pearlcdn.com/KR/Upload/Community/9b26a7f0c4220210205172127088.png", "12비약.jpg")
    # 디스코드에 올릴 파일을 지정하고, attachment에서 사용할 이름을 "image.png"로 지정
    image = discord.File("12비약.jpg", filename="12비약.jpg")
    # Embed 메시지 구성
    embed = discord.Embed(title="12 비약", description="""1번: `방어, 사신, 간파, 충격`
                                                         2번: `그리폰, 의지, 광란, 집중` 
                                                         3번: `암살, 약탈, 파괴, 생명력`
                                                         """
                                                         , color=0x00ff56)
    # 아까 지정한 파일 이름으로 해야함.
    embed.set_thumbnail(url="attachment://12비약.jpg")
    # 메시지 보내기
    await channel.send(ctx.author.mention, embed=embed, file=image)
    
@bot.command()
async def 보스(ctx):
    channel = ctx.channel
    
    urllib.request.urlretrieve("https://s1.pearlcdn.com/KR/Upload/WIKI/497b2e5ee6f20231108100517453.png", "보스.jpg")
    image = discord.File("보스.jpg", filename="보스.jpg")
    await channel.send(ctx.author.mention, file=image)
    
@bot.command()
async def 주사위(ctx):
    channel = ctx.channel
    await channel.send(str(random.randrange(1, 6)))
    
@bot.command()
async def 마법의소라고동님(ctx):
    channel = ctx.channel
    Yes_or_No = [1, 2]
    club_spongbob = random.choice(Yes_or_No)
    
    if club_spongbob == 1: #YES
        urllib.request.urlretrieve("http://www.quickmeme.com/img/7b/7ba619277f6eefa6e99142715c47931557b7a45f646bbdc38da6fa069126c68c.jpg", "YES.jpg")
        image = discord.File("YES.jpg", filename="YES.jpg")
        await channel.send(ctx.author.mention, file=image) #이미지 부분
        
    else: #NO
        urllib.request.urlretrieve("https://wowzagiftshop.com/cdn/shop/products/MagicConch_139c23e9-e212-4c2c-b0b3-85a37bbcd28c.jpg?v=1646157735&width=1445", "NO.jpg")
        image = discord.File("NO.jpg", filename="NO.jpg")
        await channel.send(ctx.author.mention, file=image) #이미지 부분
        
bot.run('MTEzMDY3Njk3MzYwNjI3NzE2NA.G7OeOl.dmfFQBKuNFd7x7W6G2MTWI466vybqDNDpAbGlM')
