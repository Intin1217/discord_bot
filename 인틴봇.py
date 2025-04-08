import discord
from discord.ext import commands
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import json
import random

client = discord.Client()

bot = commands.Bot(command_prefix='#')  # 봇을 #으로 명령어 호출

@bot.event
async def on_ready():
    print("실행중")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("#명령어"))
    
@bot.command()
async def 명령어(ctx):
    channel = ctx.channel
    
    CommandList = (
    """ #비약
        #보스
        #주사위
        #마법의소라고동님 [질문]
    """
    )
    
    embed = discord.Embed(title="명령어 목록", description=CommandList, color=0x00ff56)
    await channel.send(embed=embed)
    
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
        
bot.run('token')
