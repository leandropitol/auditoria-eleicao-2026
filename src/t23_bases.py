"""Bases de T2 e T3 (docs/desenho_T2_T3.md): ponte TSE→IBGE, covariáveis do Censo 2022, votos municipais e por seção.

Uso: python src/t23_bases.py   (grava parquets reconstruíveis em data/processed/t23_*.parquet)
"""

import re
import unicodedata
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd

from common import PROCESSED, RAW

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
NAO_NOMINAIS = {"95", "96", "97", "98"}
ANOS_T3 = [2014, 2018, 2022, 2026]
LIMIAR_CANDIDATO = 1.0  # % nacional no 1º turno para entrar como preditor próprio


def _sem_acento(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _csvs(zip_path, filtro=lambda n: True):
    """(zip aberto, nome) de cada CSV; o zip fica aberto enquanto houver referência a ele."""
    z = zipfile.ZipFile(zip_path)
    return [(z, n) for n in z.namelist() if n.lower().endswith(".csv") and filtro(n)]


# --- locais de votação e ponte TSE→IBGE ------------------------------------------------------------

def locais_2026() -> pd.DataFrame:
    cols = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO",
            "NR_LATITUDE", "NR_LONGITUDE"]
    partes = []
    for z, n in _csvs(RAW / "D3" / "eleitorado_local_votacao_2026.zip"):
        df = pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str, usecols=cols)
        partes.append(df[df["SG_UF"] != "ZZ"])
    df = pd.concat(partes).drop_duplicates(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"])
    df["lat"] = pd.to_numeric(df["NR_LATITUDE"].str.replace(",", "."), errors="coerce")
    df["lon"] = pd.to_numeric(df["NR_LONGITUDE"].str.replace(",", "."), errors="coerce")
    valida = df["lat"].between(-34.5, 5.5) & df["lon"].between(-74.5, -28.5)
    df.loc[~valida, ["lat", "lon"]] = np.nan
    return df.rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "mun", "NM_MUNICIPIO": "nm_mun_tse",
                              "NR_ZONA": "zona", "NR_SECAO": "secao", "NR_LOCAL_VOTACAO": "local"})[
        ["uf", "mun", "nm_mun_tse", "zona", "secao", "local", "lat", "lon"]]


def malha_municipal() -> gpd.GeoDataFrame:
    g = gpd.read_file(f"zip://{(RAW / 'D7' / 'BR_Municipios_2022.zip').as_posix()}!BR_Municipios_2022.shp")
    return g[["CD_MUN", "NM_MUN", "SIGLA_UF", "geometry"]]


def ponte_tse_ibge(locais: pd.DataFrame, malha: gpd.GeoDataFrame) -> pd.DataFrame:
    """Ponte TSE→IBGE em duas etapas.

    1. Nome normalizado (sem acentos e sinais) dentro da mesma UF.
    2. Para os municípios TSE que sobram: maioria espacial dos seus locais de votação, restrita aos municípios IBGE
       da mesma UF ainda não atribuídos (coordenadas erradas de alguns locais impedem usar a maioria espacial pura).
    """
    tse = locais.drop_duplicates(["uf", "mun"])[["uf", "mun", "nm_mun_tse"]].copy()
    tse["chave_nome"] = tse["nm_mun_tse"].map(_sem_acento)
    ibge = malha[["CD_MUN", "NM_MUN", "SIGLA_UF"]].copy()
    ibge["chave_nome"] = ibge["NM_MUN"].map(_sem_acento)
    por_nome = tse.merge(ibge, left_on=["uf", "chave_nome"], right_on=["SIGLA_UF", "chave_nome"], how="inner")
    por_nome = por_nome[~por_nome.duplicated(["uf", "mun"], keep=False)].assign(metodo="nome")

    resto = tse[~tse.set_index(["uf", "mun"]).index.isin(por_nome.set_index(["uf", "mun"]).index)]
    livres = ibge[~ibge["CD_MUN"].isin(por_nome["CD_MUN"])]
    pontos = locais.merge(resto[["uf", "mun"]]).dropna(subset=["lat", "lon"]).drop_duplicates(["uf", "mun", "local"])
    gp = gpd.GeoDataFrame(pontos, geometry=gpd.points_from_xy(pontos["lon"], pontos["lat"]), crs="EPSG:4674")
    poligonos = malha[malha["CD_MUN"].isin(livres["CD_MUN"])].to_crs("EPSG:4674")
    j = gpd.sjoin(gp, poligonos, how="inner", predicate="within")
    j = j[j["uf"] == j["SIGLA_UF"]]
    cont = j.groupby(["uf", "mun", "CD_MUN"]).size().rename("n_locais").reset_index()
    cont["prop"] = cont["n_locais"] / cont.groupby(["uf", "mun"])["n_locais"].transform("sum")
    espacial = (cont.sort_values("prop", ascending=False).drop_duplicates(["uf", "mun"])
                .merge(resto, on=["uf", "mun"]).merge(ibge[["CD_MUN", "NM_MUN", "SIGLA_UF"]], on="CD_MUN")
                .assign(metodo="espacial"))
    ponte = pd.concat([por_nome, espacial], ignore_index=True)
    sem = resto[~resto.set_index(["uf", "mun"]).index.isin(espacial.set_index(["uf", "mun"]).index)]
    ponte = pd.concat([ponte, sem.assign(metodo="sem_correspondencia")], ignore_index=True)
    return ponte.rename(columns={"CD_MUN": "cd_ibge"})[
        ["uf", "mun", "nm_mun_tse", "cd_ibge", "NM_MUN", "metodo", "n_locais", "prop"]]


# --- covariáveis do Censo 2022 ----------------------------------------------------------------------

def _censo(arquivo: str, cols: list[str]) -> pd.DataFrame:
    z, n = _csvs(RAW / "D6" / arquivo)[0]
    df = pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str, usecols=["CD_MUN"] + cols)
    for c in cols:
        df[c] = pd.to_numeric(df[c].str.replace(",", "."), errors="coerce")
    return df


def covariaveis_municipais() -> pd.DataFrame:
    renda = _censo("Agregados_por_municipios_renda_responsavel_BR_20260508_csv.zip", ["V06004"])
    # V00644–V00656: pessoas de 15+ por faixa; V00748–V00760: pessoas alfabetizadas nas mesmas faixas
    total15 = [f"V00{i}" for i in range(644, 657)]
    alfab15 = [f"V00{i}" for i in range(748, 761)]
    alf = _censo("Agregados_por_municipios_alfabetizacao_BR.zip", total15 + alfab15)
    idades = [f"V010{i}" for i in range(34, 42)]
    dem = _censo("Agregados_por_municipios_demografia_BR.zip", idades)
    z, n = _csvs(RAW / "D6" / "Agregados_por_setores_basico_BR_20260520.zip")[0]
    set_ = pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str, usecols=["CD_MUN", "SITUACAO", "v0001"])
    set_["v0001"] = pd.to_numeric(set_["v0001"], errors="coerce").fillna(0)
    urb = (set_.assign(u=set_["v0001"] * (set_["SITUACAO"].str.lower().str.startswith("urb")))
           .groupby("CD_MUN")[["u", "v0001"]].sum())
    cov = pd.DataFrame({"cd_ibge": renda["CD_MUN"], "log_renda": np.log(renda["V06004"])})
    pop15 = dem.set_index("CD_MUN")[idades].sum(axis=1)
    a = alf.set_index("CD_MUN")
    cov = cov.set_index("cd_ibge")
    cov["alfabetizacao_15mais"] = a[alfab15].sum(axis=1) / a[total15].sum(axis=1)
    cov["idosos_60mais_sobre_15mais"] = dem.set_index("CD_MUN")[["V01040", "V01041"]].sum(axis=1) / pop15
    cov["urbanizacao"] = urb["u"] / urb["v0001"]
    return cov.reset_index()


# --- votos ------------------------------------------------------------------------------------------

def votos_municipais(ano: int) -> pd.DataFrame:
    """Votos nominais de Presidente por UF, município TSE, turno e candidato."""
    if ano == 2026:
        cols = ["NR_TURNO", "CD_CARGO", "SG_UF", "CD_MUNICIPIO", "NR_VOTAVEL", "QT_VOTOS"]
        partes = []
        for z, n in _csvs(RAW / "D2" / "votacao_secao_2026_BR.zip"):
            for b in pd.read_csv(z.open(n), sep=";", encoding="latin-1", usecols=cols, dtype=str, chunksize=2_000_000):
                b = b[(b["CD_CARGO"] == "1") & ~b["NR_VOTAVEL"].isin(NAO_NOMINAIS)]
                partes.append(b.assign(QT_VOTOS=b["QT_VOTOS"].astype(int))
                               .groupby(["SG_UF", "CD_MUNICIPIO", "NR_TURNO", "NR_VOTAVEL"])["QT_VOTOS"].sum())
        s = pd.concat(partes).groupby(level=[0, 1, 2, 3]).sum()
        df = s.rename("votos").reset_index()
        df.columns = ["uf", "mun", "turno", "candidato", "votos"]
    else:
        partes = []
        for z, n in _csvs(RAW / "D8" / f"votacao_candidato_munzona_{ano}.zip"):
            d = pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str)
            d = d[d["CD_CARGO"] == "1"]
            if d.empty:
                continue
            col = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in d else "QT_VOTOS_NOMINAIS"
            partes.append(d[["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_TURNO", "NR_CANDIDATO", col]]
                          .rename(columns={col: "votos"}))
        d = pd.concat(partes).drop_duplicates(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_TURNO", "NR_CANDIDATO"])
        d["votos"] = d["votos"].astype(int)
        df = d.groupby(["SG_UF", "CD_MUNICIPIO", "NR_TURNO", "NR_CANDIDATO"])["votos"].sum().reset_index()
        df.columns = ["uf", "mun", "turno", "candidato", "votos"]
    df["mun"] = df["mun"].str.zfill(5)
    df["turno"] = df["turno"].astype(int)
    return df[df["uf"] != "ZZ"]


def painel_municipal(ano: int, ponte: pd.DataFrame, cov: pd.DataFrame) -> pd.DataFrame:
    v = votos_municipais(ano)
    v1 = v[v["turno"] == 1]
    nac = v1.groupby("candidato")["votos"].sum()
    nac = 100 * nac / nac.sum()
    preditores = sorted(nac[nac >= LIMIAR_CANDIDATO].index)
    w1 = v1.pivot_table(index=["uf", "mun"], columns="candidato", values="votos", aggfunc="sum", fill_value=0)
    s1 = w1.div(w1.sum(axis=1), axis=0) * 100
    s1 = s1[preditores].add_prefix("t1_c")
    w2 = v[v["turno"] == 2].pivot_table(index=["uf", "mun"], columns="candidato", values="votos",
                                         aggfunc="sum", fill_value=0)
    outro = [c for c in w2.columns if c != "13"]
    assert len(outro) == 1, f"{ano}: finalistas inesperados {list(w2.columns)}"
    y = (100 * w2["13"] / (w2["13"] + w2[outro[0]])).rename("y")
    df = s1.join(y, how="inner").join((w2["13"] + w2[outro[0]]).rename("votos_2t")).reset_index()
    df = df.merge(ponte[["uf", "mun", "cd_ibge"]], on=["uf", "mun"], how="left")
    df = df.merge(cov, on="cd_ibge", how="left")
    df["ano"] = ano
    return df


# --- base por seção (2026) ----------------------------------------------------------------------------

def secoes_2026() -> pd.DataFrame:
    chave = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    cols = ["NR_TURNO", "CD_CARGO", *chave, "NR_VOTAVEL", "QT_VOTOS"]
    partes = []
    for z, n in _csvs(RAW / "D2" / "votacao_secao_2026_BR.zip"):
        for b in pd.read_csv(z.open(n), sep=";", encoding="latin-1", usecols=cols, dtype=str, chunksize=2_000_000):
            b = b[(b["CD_CARGO"] == "1") & (b["SG_UF"] != "ZZ") & ~b["NR_VOTAVEL"].isin(NAO_NOMINAIS)]
            partes.append(b.assign(QT_VOTOS=b["QT_VOTOS"].astype(int)))
    v = pd.concat(partes)
    nac = v[v["NR_TURNO"] == "1"].groupby("NR_VOTAVEL")["QT_VOTOS"].sum()
    preditores = sorted((100 * nac / nac.sum())[lambda s: s >= LIMIAR_CANDIDATO].index)
    w1 = v[v["NR_TURNO"] == "1"].pivot_table(index=chave, columns="NR_VOTAVEL", values="QT_VOTOS",
                                             aggfunc="sum", fill_value=0)
    s1 = (w1.div(w1.sum(axis=1), axis=0) * 100)[preditores].add_prefix("t1_c")
    w2 = v[v["NR_TURNO"] == "2"].pivot_table(index=chave, columns="NR_VOTAVEL", values="QT_VOTOS",
                                             aggfunc="sum", fill_value=0)
    outro = [c for c in w2.columns if c != "13"][0]
    base = s1.join((100 * w2["13"] / (w2["13"] + w2[outro])).rename("y"), how="outer")
    base = base.join((w2["13"] + w2[outro]).rename("votos_2t"), how="left")

    det_cols = ["NR_TURNO", "CD_CARGO", *chave, "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES",
                "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS"]
    partes = []
    for z, n in _csvs(RAW / "D4" / "detalhe_votacao_secao_2026.zip"):
        d = pd.read_csv(z.open(n), sep=";", encoding="latin-1", usecols=det_cols, dtype=str)
        partes.append(d[(d["CD_CARGO"] == "1") & (d["SG_UF"] != "ZZ")])
    d = pd.concat(partes).drop_duplicates([*chave, "NR_TURNO"])
    for c in det_cols[6:]:
        d[c] = d[c].astype(float)
    d1 = d[d["NR_TURNO"] == "1"].set_index(chave)
    d2 = d[d["NR_TURNO"] == "2"].set_index(chave)
    base["abst_1t"] = d1["QT_ABSTENCOES"] / d1["QT_APTOS"]
    base["bn_1t"] = (d1["QT_VOTOS_BRANCOS"] + d1["QT_VOTOS_NULOS"]) / d1["QT_COMPARECIMENTO"]
    base["d_comparecimento"] = d2["QT_COMPARECIMENTO"] / d2["QT_APTOS"] - d1["QT_COMPARECIMENTO"] / d1["QT_APTOS"]
    base["d_bn"] = ((d2["QT_VOTOS_BRANCOS"] + d2["QT_VOTOS_NULOS"]) / d2["QT_COMPARECIMENTO"]) - base["bn_1t"]
    base = base.reset_index().rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "mun", "NR_ZONA": "zona",
                                              "NR_SECAO": "secao"})
    for c, w in (("mun", 5), ("zona", 4), ("secao", 4)):
        base[c] = base[c].str.zfill(w)
    return base.merge(perfil_secoes(), on=["uf", "mun", "zona", "secao"], how="left")


def perfil_secoes() -> pd.DataFrame:
    chave = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
    partes = []
    for uf in UFS:
        for z, n in _csvs(RAW / "D3" / f"perfil_eleitor_secao_2026_{uf}.zip"):
            for b in pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str, chunksize=2_000_000,
                                 usecols=[*chave, "DS_GENERO", "DS_FAIXA_ETARIA", "DS_GRAU_ESCOLARIDADE",
                                          "QT_ELEITORES"]):
                b["q"] = b["QT_ELEITORES"].astype(float)
                idade = b["DS_FAIXA_ETARIA"].str.extract(r"(\d+)")[0].astype(float)
                esc = b["DS_GRAU_ESCOLARIDADE"].map(_sem_acento)
                b["fem"] = b["q"] * b["DS_GENERO"].str.upper().str.startswith("FEM")
                b["id_16_24"] = b["q"] * (idade < 25)
                b["id_25_44"] = b["q"] * idade.between(25, 44)
                b["id_45_59"] = b["q"] * idade.between(45, 59)
                b["id_60_69"] = b["q"] * idade.between(60, 69)
                b["esc_superior"] = b["q"] * esc.str.contains("superior")
                b["esc_medio"] = b["q"] * esc.str.contains("medio")
                partes.append(b.groupby(chave)[["q", "fem", "id_16_24", "id_25_44", "id_45_59", "id_60_69",
                                                "esc_superior", "esc_medio"]].sum())
    p = pd.concat(partes).groupby(level=[0, 1, 2, 3]).sum()
    out = p.drop(columns="q").div(p["q"], axis=0).add_prefix("p_")
    out["eleitores_perfil"] = p["q"]
    out = out.reset_index().rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "mun", "NR_ZONA": "zona",
                                            "NR_SECAO": "secao"})
    for c, w in (("mun", 5), ("zona", 4), ("secao", 4)):
        out[c] = out[c].str.zfill(w)
    return out


def main() -> None:
    locais = locais_2026()
    for c, w in (("mun", 5), ("zona", 4), ("secao", 4)):
        locais[c] = locais[c].str.zfill(w)
    locais.to_parquet(PROCESSED / "t23_locais_2026.parquet", index=False)
    malha = malha_municipal()
    ponte = ponte_tse_ibge(locais, malha)
    ponte.to_parquet(PROCESSED / "t23_ponte_tse_ibge.parquet", index=False)
    print(f"ponte: {len(ponte)} municípios TSE; por método: {ponte['metodo'].value_counts().to_dict()}; "
          f"códigos IBGE repetidos: {int(ponte['cd_ibge'].dropna().duplicated().sum())}", flush=True)
    print(ponte[ponte["metodo"] != "nome"].to_string(), flush=True)
    cov = covariaveis_municipais()
    cov.to_parquet(PROCESSED / "t23_covariaveis_municipais.parquet", index=False)
    print(cov.describe().T.round(3).to_string(), flush=True)
    for ano in ANOS_T3:
        painel_municipal(ano, ponte, cov).to_parquet(PROCESSED / f"t23_municipal_{ano}.parquet", index=False)
        print(f"painel municipal {ano} ok", flush=True)
    sec = secoes_2026()
    sec.to_parquet(PROCESSED / "t23_secoes_2026.parquet", index=False)
    print(f"seções 2026: {len(sec)}; sem y: {sec['y'].isna().sum()}; sem 1º turno: {sec['t1_c13'].isna().sum()}; "
          f"sem perfil: {sec['p_fem'].isna().sum()}", flush=True)


if __name__ == "__main__":
    main()
