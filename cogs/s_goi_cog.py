# !/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Union

import discord
from discord.ext import commands
from discord.ext.menus import ListPageSource, MenuPages

from .utils.article_manager import ArticleManager, SCPArticleDatacls
from .utils.common import CommonUtil


class GoIPager(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=10)
        self.root_url = 'http://scp-jp.wikidot.com/'
        self.c = CommonUtil()

    async def write_page(self, menu, fields: List[SCPArticleDatacls] = []) -> discord.Embed:
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = discord.Embed(
            title="該当するGoIフォーマットは以下の通りです",
            description=f"{len_data}件ヒット",
            color=discord.Color.darker_grey())

        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} records.")

        for data in fields:
            embed.add_field(
                name=self.c.select_title(data),
                value=f'{self.root_url}{data.fullname}\nAuthor : {data.created_by}',
                inline=False)

        return embed

    async def format_page(self, menu, entries):

        return await self.write_page(menu, entries)


class GoIArticleCog(commands.Cog, name='GoIフォーマットコマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.article_mng = ArticleManager()
        self.c = CommonUtil()

    async def start_paginating(self, ctx, data_list: List[SCPArticleDatacls]):
        menu = MenuPages(source=GoIPager(ctx, data_list),
                         delete_message_after=False,
                         clear_reactions_after=True,
                         timeout=60.0)
        await menu.start(ctx)

    async def send_message(self, ctx, data_list: Union[List[SCPArticleDatacls], None]) -> None:
        if data_list is None:
            msg = await ctx.reply("該当するGoIフォーマットは見つかりませんでした")
            await self.c.autodel_msg(msg=msg)
            return

        elif len(data_list) == 1:
            data = data_list[0]
            title = self.c.select_title(data)
            await ctx.send(f'{title}\n{self.bot.root_url}{data.fullname}')
            return

        else:
            await self.start_paginating(ctx, data_list)
            return

    @commands.group(invoke_without_command=True, description='GoIフォーマットを検索するコマンド', aliases=['goi'])
    async def goi_format(self, ctx, word: str):
        """引数からGoIフォーマットを検索するコマンド\n`/goi 単語`で、その単語を含むGOIフォーマットを検索します"""
        if ctx.invoked_subcommand is None:
            data_list = await self.article_mng.get_data_from_all_and_tag(all_=word, tags=['goi-format'])

            await self.send_message(ctx, data_list)

    @goi_format.command(description='GoIフォーマットの詳細版を表示するコマンド', aliases=['-d'])
    async def detail(self, ctx, all_: str):
        """GoIフォーマットの詳細版を検索するコマンド\n`/goi -d 単語`で、その単語を含むGoI フォーマットの記事の詳細を表示します\n複数ヒットした場合は通常の一覧表示を行います"""

        data_list = await self.article_mng.get_data_from_all_and_tag(all_=all_, tags=['goi-format'])
        if data_list is None:
            msg = await ctx.reply("該当するGoIフォーマットは見つかりませんでした")
            await self.c.autodel_msg(msg=msg)

        elif len(data_list) > 1:
            await self.send_message(ctx, data_list)
            msg = await ctx.reply('複数ヒットしたため、一覧を表示します')
            await self.c.autodel_msg(msg=msg)

        else:
            embed = self.c.create_detail_embed(data_list[0])
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GoIArticleCog(bot))
