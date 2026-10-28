"""T3 — modelo misto por município (intercepto aleatório de UF) e resíduos, 2014–2026 (docs/desenho_T2_T3.md).

Uso: python src/04_model_residuals.py
Saídas: data/processed/t3_residuos_{ano}.parquet, output/tables/t3_modelos.csv
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import OUTPUT, PROCESSED

ANOS = [2014, 2018, 2022, 2026]
COVARIAVEIS = ["log_renda", "alfabetizacao_15mais", "urbanizacao", "idosos_60mais_sobre_15mais"]


def ajusta(ano: int) -> tuple[pd.DataFrame, dict]:
    df = pd.read_parquet(PROCESSED / f"t23_municipal_{ano}.parquet")
    t1 = sorted(c for c in df.columns if c.startswith("t1_c"))
    usados = t1 + COVARIAVEIS
    n_total = len(df)
    df = df.dropna(subset=["y", "cd_ibge", *usados])
    # mais de um município TSE no mesmo código IBGE: mantém o de maior votação e registra
    dup = int(df["cd_ibge"].duplicated(keep=False).sum())
    df = df.sort_values("votos_2t", ascending=False).drop_duplicates("cd_ibge")
    z = df.copy()
    for c in usados:
        z[c] = (z[c] - z[c].mean()) / z[c].std()
    formula = "y ~ " + " + ".join(usados)
    fit = smf.mixedlm(formula, z, groups=z["uf"]).fit(reml=True)
    z["ajustado"] = fit.fittedvalues
    z["residuo"] = z["y"] - z["ajustado"]
    info = {
        "ano": ano, "municipios_no_painel": n_total, "municipios_no_modelo": len(z),
        "linhas_com_ibge_duplicado": dup, "preditores_1t": " ".join(c.replace("t1_c", "") for c in t1),
        "r2_condicional": float(np.corrcoef(z["y"], z["ajustado"])[0, 1] ** 2),
        "dp_residuo": float(z["residuo"].std()), "var_uf": float(fit.cov_re.iloc[0, 0]),
        "convergiu": bool(fit.converged),
    }
    coef = fit.params.rename("coef").to_frame().join(fit.bse.rename("ep")).join(fit.pvalues.rename("p"))
    coef["ano"] = ano
    coef.to_csv(OUTPUT / "tables" / f"t3_coeficientes_{ano}.csv")
    return z[["uf", "mun", "cd_ibge", "y", "ajustado", "residuo", "votos_2t"]], info


def main() -> None:
    OUTPUT.joinpath("tables").mkdir(parents=True, exist_ok=True)
    infos = []
    for ano in ANOS:
        res, info = ajusta(ano)
        res.to_parquet(PROCESSED / f"t3_residuos_{ano}.parquet", index=False)
        infos.append(info)
        print(info, flush=True)
    pd.DataFrame(infos).to_csv(OUTPUT / "tables" / "t3_modelos.csv", index=False)


if __name__ == "__main__":
    main()
