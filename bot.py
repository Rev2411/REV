import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True  # DM 허용

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1360421496962416782
CATEGORY_ID = 1365731076810477638
SUPPORT_ROLE_ID = 1360423916438425690
LOG_CHANNEL_ID = 1365732581102063696

ticket_counter = 0

class TicketModal(discord.ui.Modal, title="문의사항 작성"):
    inquiry = discord.ui.TextInput(
        label="문의하실 내용을 작성해주세요",
        placeholder="예시: 서버 이용 중 오류가 발생했습니다...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        global ticket_counter
        await interaction.response.defer(ephemeral=True)  # 즉시 응답 예약
        
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)

        ticket_counter += 1
        ticket_name = f"ticket-{ticket_counter:03d}"

        # 이미 열려있으면 막기
        for channel in guild.text_channels:
            if channel.topic and f"{interaction.user.id}" in channel.topic:
                await interaction.followup.send(f"❗ 이미 티켓이 열려있습니다: {channel.mention}", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites,
            topic=f"{interaction.user.id}"
        )

        # 문의사항을 티켓 채널에 보내기
        embed = discord.Embed(
            title="📨 문의사항",
            description=self.inquiry.value,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"작성자: {interaction.user.name}")
        await ticket_channel.send(content=f"{interaction.user.mention} | 지원팀이 곧 응답할 예정입니다.", embed=embed, view=TicketCloseButton())

        # 사용자에게 DM 알림 보내기
        try:
            await interaction.user.send(
                f"✅ 당신의 티켓이 생성되었습니다: {ticket_channel.mention}\n\n**문의 내용:** {self.inquiry.value}"
            )
        except discord.Forbidden:
            print(f"⚠️ {interaction.user} 님에게 DM을 보낼 수 없습니다.")

        await interaction.followup.send(f"✅ 티켓이 생성되었습니다: {ticket_channel.mention}", ephemeral=True)


class TicketOpenButton(discord.ui.View):
    @discord.ui.button(label="📩 티켓 열기", style=discord.ButtonStyle.gray)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())


class TicketCloseButton(discord.ui.View):
    @discord.ui.button(label="🔒 티켓 닫기", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("❗ 이 채널은 티켓 채널이 아닙니다.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 티켓을 닫는 중입니다...", ephemeral=True)

        # 채팅 기록 저장
        messages = []
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            if message.content:
                messages.append(f"[{message.created_at}] {message.author}: {message.content}")

        log_text = "\n".join(messages)

        # 로그 파일 경로 설정 (Windows 호환)
        if not os.path.exists("logs"):
            os.makedirs("logs")

        log_file_path = f"logs/{interaction.channel.name}.txt"

        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(log_text)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                content=f"📋 티켓 로그: {interaction.channel.name}",
                file=discord.File(log_file_path)
            )

        os.remove(log_file_path)

        await interaction.channel.delete()


@bot.event
async def on_ready():
    print(f"✅ 봇 준비 완료: {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ 명령어 동기화 완료 ({len(synced)}개)")
    except Exception as e:
        print(e)


@bot.tree.command(name="티켓버튼", description="티켓 열기 버튼을 보냅니다", guild=discord.Object(id=GUILD_ID))
async def ticket_button(interaction: discord.Interaction):
    view = TicketOpenButton()
    await interaction.response.send_message(
        content=" 문의하실 사항이 있으시면 아래 📩 버튼을 눌러주세요!",
        view=view
    )

const 포트 = 프로세스 .env.PORT || 4000​​​   
bot.run(os.environ['TOKEN']) 
