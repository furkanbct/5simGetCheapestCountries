# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from rich    import print
from asyncio import run, sleep, Semaphore, create_task, gather
from aiohttp import ClientSession
from atexit  import register as kapatirken

class SimNet:
    def __oturum_kapa(self):
        run(self.oturum.close())

    def __init__(self):
        self.oturum  = ClientSession()
        kapatirken(self.__oturum_kapa)
        self.__limit = Semaphore(50)

    async def __ulkeler_ve_hatlar(self) -> dict[str, list[str]]:
        async with self.oturum.get("https://5sim.net/v1/guest/countries") as istek:
            ulkeler_veri = await istek.json()

        return {
            ulke: [key for key in detay.keys() if key.startswith("virtual")]
              for ulke, detay in ulkeler_veri.items()
        }

    async def __hat_fiyat_ver(self, ulke:str, hat:str, hizmet:str="telegram") -> dict | None:
        async with self.__limit:
            if self.__limit.locked():
                await sleep(1)

            while True:
                try:
                    async with self.oturum.get(f"https://5sim.net/v1/guest/products/{ulke}/{hat}") as istek:
                        hizmetler_veri = await istek.json()
                    break
                except Exception:
                    await sleep(.1)

            return {
                "hat"   : hat,
                "fiyat" : hizmetler_veri[hizmet]["Price"],
                "adet"  : hizmetler_veri[hizmet]["Qty"]
            } if hizmet in hizmetler_veri.keys() else None

    async def __ulke_fiyatlari(self, ulke:str, hatlar:str, hizmet:str) -> dict | None:
        hat_fiyatlari = []
        for hat_bilgi in await gather(*(create_task(self.__hat_fiyat_ver(ulke, hat, hizmet)) for hat in hatlar)):
            if hat_bilgi and hat_bilgi["adet"] > 0:
                hat_fiyatlari.append(hat_bilgi)

        return {ulke: sorted(hat_fiyatlari, key=lambda sozluk: sozluk["fiyat"])} if hat_fiyatlari else None

    async def en_ucuz_hatlar(self, hizmet:str="telegram"):
        ulkeler_ve_hatlar = await self.__ulkeler_ve_hatlar()

        for ulke, hatlar in ulkeler_ve_hatlar.items():
            veri = await self.__ulke_fiyatlari(ulke, hatlar, hizmet)
            if veri:
                yield veri

from asyncio   import new_event_loop
from Kekik.cli import konsol, temizle

async def ana_fonksiyon(hizmet:str):
    temizle()

    print(f"\n\n\t\t[yellow]5Sim.Net {hizmet.title()} için En Ucuz Hatlar\n\n")

    print(f"[green1]{'Ülke':^23} [red]|[/] [turquoise2]{'Hat Adı':>10} [red]|[/] [green3]{'Fiyat':^8} [red]|[/] [yellow4]{'Adet':<8}")
    print(f"[green1]{'----':^23} [red]|[/] [turquoise2]{'-------':>10} [red]|[/] [green3]{'-----':^8} [red]|[/] [yellow4]{'----':<8}\n")

    sim_net = SimNet()

    en_ucuz_hatlar = []
    async for veri in sim_net.en_ucuz_hatlar(hizmet.lower()):
        for ulke, hatlar in veri.items():
            en_ucuz_hat = {
                "ulke"  : ulke,
                "hat"   : hatlar[0]["hat"],     # * 0 En Ucuz » -1 En Pahalı
                "fiyat" : hatlar[0]["fiyat"],   # * 0 En Ucuz » -1 En Pahalı
                "adet"  : hatlar[0]["adet"]     # * 0 En Ucuz » -1 En Pahalı
            }
            break

        en_ucuz_hatlar.append(en_ucuz_hat)

        print(f"[green1]{en_ucuz_hat['ulke']:^23} [red]|[/] [turquoise2]{en_ucuz_hat['hat']:>10} [red]|[/] [green3]{en_ucuz_hat['fiyat']:^8} [red]|[/] [yellow4]{en_ucuz_hat['adet']:<8}")

    temizle()
    sirali_liste = sorted(en_ucuz_hatlar, key=lambda sozluk: sozluk["fiyat"])

    print("\n\n\t\t[yellow]5Sim.Net Telegram için En Ucuz Hatlar\n\n")

    print(f"[green1]{'Ülke':^23} [red]|[/] [turquoise2]{'Hat Adı':>10} [red]|[/] [green3]{'Fiyat':^8} [red]|[/] [yellow4]{'Adet':<8}")
    print(f"[green1]{'----':^23} [red]|[/] [turquoise2]{'-------':>10} [red]|[/] [green3]{'-----':^8} [red]|[/] [yellow4]{'----':<8}\n")

    for en_ucuz_hat in sirali_liste:
        print(f"[green1]{en_ucuz_hat['ulke']:^23} [red]|[/] [turquoise2]{en_ucuz_hat['hat']:>10} [red]|[/] [green3]{en_ucuz_hat['fiyat']:^8} [red]|[/] [yellow4]{en_ucuz_hat['adet']:<8}")

if __name__ == "__main__":
    hizmet = konsol.input("\n\n[magenta]Hangi Hizmet İçin EN Ucuz Ülkeler Gelsin? (Örn.: Telegram): ")
    loop = new_event_loop()
    loop.run_until_complete(ana_fonksiyon(hizmet))