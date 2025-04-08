import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 역할 및 이모지 설정
reactions = ["👍", "👎", "😀", "😢", "🎉"]
roles = ["병원", "감옥", "방송국", "안식처", "지옥"]

message_id1 = 1162721987827871804  # 임베드 메시지 ID

@bot.event #봇 실행시 한번 실행
async def on_ready():
    print("실행중")
    await bot.change_presence(status = discord.Status.online, activity = discord.Game("테스트중"))

@bot.command()
async def parkjh_potal(ctx):
    # 임베드 생성
    embed1 = discord.Embed(
        title="비전이동",
        description="비전이동입니다~",
        color=discord.Color.blue()
    )

    # 임베드를 메시지로 보내기
    message1 = await ctx.send(embed=embed1)

     # 첫 번째 메시지 ID 저장 
    global message_id1  
    message_id1=message1.id  

   # 첫 번째 임베드에 이모지 반응 추가 (역할 부여)
    for reaction in reactions:
       await message1.add_reaction(reaction)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    # 반응한 이모지와 메시지 ID
    emoji = payload.emoji.name
    message_id = payload.message_id

    if message_id == message_id1:  # 1번 임베드에 반응한 경우 (역할 부여/제거)
        if emoji in reactions:
            role_name = roles[reactions.index(emoji)]
            role_to_add_or_remove = discord.utils.get(payload.member.guild.roles, name=role_name)
            member_roles_names=[role.name for role in payload.member.roles]
            
            if role_to_add_or_remove:
                member=payload.member
                
                for rname in roles: 
                    current_role=discord.utils.get(member.guild.roles,name=rname) 

                    if current_role and current_role in member.roles and rname != role_name:  
                        await member.remove_roles(current_role) 

                if role_to_add_or_remove in member.roles:  
                    await member.remove_roles(role_to_add_or_remove)
                else:  
                    await member.add_roles(role_to_add_or_remove)

                await asyncio.sleep(3)  # Wait for 3 seconds
                
                channel = bot.get_channel(payload.channel_id)  
                message = await channel.fetch_message(message_id) 

                await message.remove_reaction(emoji, member)

# 봇 토큰으로 봇을 실행합니다.
bot.run('token')
