# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
import pathlib
import time
import traceback
import typing
from datetime import datetime

import discord
from discord.ext import commands, tasks

from cogs.utils.common import CommonUtil
from cogs.utils.setting_manager import SettingManager


class Admin(commands.Cog, name='管理用コマンド群'):
    """
    管理用のコマンドです
    """

    def __init__(self, bot):
        self.bot = bot

        self.root_path = pathlib.Path(__file__).parents[1]

        self.data_path = self.root_path / 'data'

        self.auto_backup.stop()
        self.auto_backup.start()
        self.setting_mng = SettingManager()
        self.c = CommonUtil()

    async def cog_check(self, ctx):
        return ctx.guild and await self.bot.is_owner(ctx.author)

    @staticmethod
    def log_remove_guild(guild):
        error_content = f'サーバーを退出しました\nreason: black list\ndetail : {guild}'
        logging.error(error_content)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.setting_mng.create_table()
        guild_ids = [guild.id for guild in self.bot.guilds]
        await self.setting_mng.init_guilds(guild_ids)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """on_guild_join時に発火する関数
        """
        if guild_setting := await self.setting_mng.get_guild(guild.id):
            if guild_setting.black_server:
                await guild.leave()
                self.log_remove_guild(guild)
                return
        else:
            await self.setting_mng.register_guild(guild_id=guild.id)

        embed = discord.Embed(
            title="サーバーに参加しました",
            description=f"SCP公式チャット用utility-bot {self.bot.user.display_name}",
            color=0x2fe48d)
        embed.set_author(
            name=f"{self.bot.user.name}",
            icon_url=f"{self.bot.user.avatar.url}")
        await guild.system_channel.send(embed=embed)

    @commands.command(aliases=['re'], hidden=True)
    async def reload(self, ctx, cogname: typing.Optional[str] = "ALL"):
        """Cogをリロードする関数
        """
        cog_path = self.root_path / "cogs"
        if cogname == "ALL":
            reloaded_list = []
            for cog in os.listdir(cog_path):
                if cog.endswith(".py"):
                    try:
                        cog = cog[:-3]
                        self.bot.unload_extension(f'cogs.{cog}')
                        self.bot.load_extension(f'cogs.{cog}')
                        reloaded_list.append(cog)
                    except Exception:
                        traceback.print_exc()
            await ctx.reply(f"{reloaded_list}をreloadしました", mention_author=False)
        else:
            try:
                self.bot.unload_extension(f'cogs.{cogname}')
                self.bot.load_extension(f'cogs.{cogname}')
                await ctx.reply(f"{cogname}をreloadしました", mention_author=False)
            except Exception as e:
                print(e)
                await ctx.reply(e, mention_author=False)

    @commands.command(aliases=['st'], hidden=True)
    async def status(self, ctx, word: str):
        try:
            await self.bot.change_presence(activity=discord.Game(name=word))
            await ctx.reply(f"ステータスを{word}に変更しました", mention_author=False)
        except BaseException:
            pass

    @commands.command(hidden=True)
    async def add_black_list(self, ctx, server_id: int):
        guild = self.bot.get_guild(ctx.guild.id)
        if guild is None:
            await ctx.reply(f'サーバーid : {server_id}を発見できませんでした')
            return

        await guild.leave()
        self.log_remove_guild(guild)
        if not await self.setting_mng.is_exist(server_id):
            await ctx.reply(f'サーバーid : {server_id}をDB上に発見できませんでした')
        else:
            await self.setting_mng.set_black_list(server_id)
            await ctx.reply(f'サーバー : {guild}を退出しました')

    @commands.command(hidden=True)
    async def remove_black_list(self, ctx, server_id: int):
        if not await self.setting_mng.is_exist(server_id):
            await ctx.reply(f'サーバーid : {server_id}をDB上に発見できませんでした')
        else:
            await self.setting_mng.remove_black_list(server_id)
            await ctx.reply(f'サーバー : {server_id}をブラックリストから除去しました')

    @commands.command(aliases=['p'], hidden=True, description='疎通確認')
    async def ping(self, ctx):
        """Pingによる疎通確認を行うコマンド"""
        start_time = time.time()
        mes = await ctx.reply("Pinging....")
        await mes.edit(content="pong!\n" + str(round(time.time() - start_time, 3) * 1000) + "ms")

    @commands.command(aliases=['wh'], hidden=True)
    async def where(self, ctx):
        """今どこにいるかを確認する関数
        """
        await ctx.reply("現在入っているサーバーは以下です", mention_author=False)
        server_list = '\n'.join(
            [i.name.replace('\u3000', ' ') + ' : ' + str(i.id) for i in ctx.bot.guilds])

        await ctx.reply(f"{server_list}", mention_author=False)

    @commands.command(aliases=['mem'], hidden=True)
    async def num_of_member(self, ctx):
        """そのサーバーに何人いるかを確認する関数
        """
        await ctx.reply(f"{ctx.guild.member_count}", mention_author=False)

    @commands.command(hidden=True)
    async def back_up(self, ctx):
        """バックアップファイルを送信する関数
        """
        json_files = [filename for filename in os.listdir(
            self.data_path) if filename.endswith(".json")]
        sql_files = [filename for filename in os.listdir(
            self.data_path) if filename.endswith(".sqlite3")]

        json_files.extend(sql_files)

        my_files = [discord.File(f'{self.data_path / i}') for i in json_files]

        try:
            await ctx.send(files=my_files)
        except discord.HTTPException:
            await ctx.reply('ファイルサイズが大きすぎます')

    @commands.command(hidden=True)
    async def restore_one(self, ctx):
        """添付メッセージからファイルを取得する関数
        """
        for attachment in ctx.message.attachments:
            await attachment.save(f"{self.data_path / attachment.filename}")
            await ctx.send(f'{attachment.filename}を保存しました')

    @commands.command(hidden=True)
    async def restore(self, ctx):
        """バックアップチャンネルからファイルを取得する関数
        """
        async for message in ctx.channel.history(limit=100):
            if message.author.id == self.bot.user.id:
                if len(message.attachments) != 0:
                    attachments_name = ' '.join(
                        [i.filename for i in message.attachments])
                    msg_time = message.created_at.strftime('%m-%d %H:%M')
                    await ctx.send(f'{msg_time}の{attachments_name}を取り込みます')
                    for attachment in message.attachments:
                        await attachment.save(f"{self.data_path / attachment.filename}")
                    break

    @tasks.loop(minutes=1.0)
    async def auto_backup(self):
        now = datetime.utcnow()

        now_jst = self.c.convert_utc_into_jst(now)
        now_HM = now_jst.strftime('%H:%M')

        if now_HM == '04:00':
            channel = self.bot.get_channel(745128369170939965)

            json_files = [filename for filename in os.listdir(
                self.data_path) if filename.endswith(".json")]
            sql_files = [filename for filename in os.listdir(
                self.data_path) if filename.endswith(".sqlite3")]

            json_files.extend(sql_files)
            my_files = [
                discord.File(f'{self.data_path / i}')for i in json_files]

            await channel.send(files=my_files)

    @auto_backup.before_loop
    async def before_printer(self):
        print('admin waiting...')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Admin(bot))
