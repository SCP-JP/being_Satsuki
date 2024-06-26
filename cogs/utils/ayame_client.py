import asyncio
import datetime
import logging
from urllib.parse import urlencode

import aiohttp
from pydantic.dataclasses import dataclass

logger = logging.getLogger("discord")


@dataclass
class AyameSearchResult:
    fullname: str
    title: str
    created_at: datetime.datetime
    created_by_unix: str
    rating: int
    tags: list
    metatitle: str
    page_id: int


@dataclass
class AyameSearchQuery:
    title: str | None
    tags: list[str] | None
    author: str | None
    rate_min: int | None
    rate_max: int | None
    date_from: datetime.datetime | None
    date_to: datetime.datetime | None
    page: int | None
    show: int | None

    def to_query(self) -> str:
        query = []

        if self.title is not None:
            query.append(("title", self.title))

        if self.tags is not None:
            for tag in self.tags:
                query.append(("tags", tag))

        if self.author is not None:
            query.append(("author", self.author))

        if self.rate_min is not None:
            query.append(("rate_min", str(self.rate_min)))

        if self.rate_max is not None:
            query.append(("rate_max", str(self.rate_max)))

        if self.date_from is not None:
            query.append(("date_from", self.date_from.isoformat()))

        if self.date_to is not None:
            query.append(("date_to", self.date_to.isoformat()))

        if self.page is not None:
            query.append(("page", str(self.page)))

        if self.show is not None:
            query.append(("show", str(self.show)))

        return urlencode(query)


@dataclass
class AyameSearchCountQuery:
    title: str | None
    tags: list[str] | None
    author: str | None
    rate_min: int | None
    rate_max: int | None
    date_from: datetime.datetime | None
    date_to: datetime.datetime | None

    def to_query(self) -> str:
        query = []

        if self.title is not None:
            query.append(("title", self.title))

        if self.tags is not None:
            for tag in self.tags:
                query.append(("tags", tag))

        if self.author is not None:
            query.append(("author", self.author))

        if self.rate_min is not None:
            query.append(("rate_min", str(self.rate_min)))

        if self.rate_max is not None:
            query.append(("rate_max", str(self.rate_max)))

        if self.date_from is not None:
            query.append(("date_from", self.date_from.isoformat()))

        if self.date_to is not None:
            query.append(("date_to", self.date_to.isoformat()))

        return urlencode(query)


class AyameClient:
    def __init__(self) -> None:
        pass

    async def search_complex(self, query: AyameSearchQuery) -> list[AyameSearchResult]:
        url = f"https://ayameapidev.yukkuriikouze.com/search/complex?{query.to_query()}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(
                        f"Failed to get data from Ayame API: {response.status}, {query.to_query()}"
                    )
                    return []

                data = await response.json()

        results = []

        for item in data:
            # itemにmetatitleのキーがない場合、空文字列を代入
            if "metatitle" not in item:
                item["metatitle"] = ""

            # tagsが""の場合、空リストを代入
            if item["tags"] == "":
                item["tags"] = []
            result = AyameSearchResult(
                fullname=item["fullname"],
                title=item["title"],
                created_at=datetime.datetime.fromisoformat(item["created_at"]),
                created_by_unix=item["created_by_unix"],
                rating=item["rating"],
                tags=item["tags"],
                metatitle=item["metatitle"],
                page_id=item["id"],
            )
            results.append(result)

        return results

    async def search_complex_count(self, query: AyameSearchCountQuery) -> int:
        url = f"https://ayameapidev.yukkuriikouze.com/search/complex_count?{query.to_query()}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return 0

                return await response.json()


if __name__ == "__main__":
    ayame = AyameClient()

    # count_query = AyameSearchCountQuery(
    #     title=None,
    #     tags=None,
    #     author="burnin-a-gogo",
    #     rate_min=None,
    #     rate_max=None,
    #     date_from=None,
    #     date_to=None,
    # )

    # results_num = asyncio.run(ayame.search_complex_count(count_query))
    # print(results_num)

    # query = AyameSearchQuery(
    #     title=None,
    #     tags=None,
    #     author="burnin-a-gogo",
    #     rate_min=None,
    #     rate_max=None,
    #     date_from=None,
    #     date_to=None,
    #     page=None,
    #     show=None,
    # )

    # results = asyncio.run(ayame.search_complex(query))

    import random

    branches = [
        "en",
        "jp",
        "ru",
        "ko",
        "cn",
        "fr",
        "pl",
        "es",
        "th",
        "de",
        "it",
        "ua",
        "pt",
        "sc",
        "zh",
        "vn",
    ]

    object_classes = [
        "safe",
        "euclid",
        "keter",
        "thaumiel",
        "neutralized",
        "explained",
        "apollyon",
        "archon",
        "decommissioned",
        "pending",
        "esoteric-class",
    ]

    results = []

    while results == []:
        # 0から9999までのランダムな数字を生成
        # random_page = random.randint(0, 9999)

        # en,jp,ru,ko,cn,fr,pl,es,th,de,it,ua,pt,sc,zh,vnからランダムに選択
        lang = random.choice(branches)

        # オブジェクトクラスからランダムに選択
        object_class = random.choice(object_classes)

        print(object_class, lang)

        # ランダムなページを取得
        query = AyameSearchQuery(
            title=None,
            tags=[lang, object_class, "scp"],
            author=None,
            rate_min=None,
            rate_max=None,
            date_from=None,
            date_to=None,
            page=None,
            show=None,
        )

        results = asyncio.run(ayame.search_complex(query))

    # resultsからランダムに選択
    result = random.choice(results)

    print(result)
